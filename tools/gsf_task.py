from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from tools.gsf_claims import Claim, find_conflicts, normalize_paths, validate_claim_dict

INDEX_PATH = Path(".gsf/claims/index.json")
CLAIM_DIR = Path(".gsf/claims")
MAX_COORDINATION_RETRIES = 5


class ClaimConflictError(RuntimeError):
    pass


class TaskStateError(RuntimeError):
    pass


def _run(*args: str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, args, output=result.stdout, stderr=result.stderr
        )
    return result


def _repo_root() -> Path:
    result = _run("git", "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip()).resolve()


def _slugify(scope: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", scope.lower()).strip("-")
    return slug[:48] or "task"


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _empty_index() -> dict[str, Any]:
    return {"version": 1, "claims": []}


def _load_index_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _empty_index()
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("claims"), list):
        raise TaskStateError("invalid .gsf/claims/index.json")
    for item in data["claims"]:
        validate_claim_dict(item)
    return data


def _write_index_file(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _configure_git_identity(repo: Path) -> None:
    _run("git", "config", "user.name", "GSF Coordinator", cwd=repo)
    _run("git", "config", "user.email", "gsf-coordinator@users.noreply.github.com", cwd=repo)


def _mutate_main(
    repo: Path,
    message: str,
    mutate: Callable[[dict[str, Any], Path], None],
) -> None:
    """Optimistically mutate coordination metadata on origin/main.

    A rejected non-fast-forward push is treated as a race: fetch the latest main,
    re-run the mutation (including conflict checks), and retry.
    """
    last_error: Exception | None = None
    for _attempt in range(MAX_COORDINATION_RETRIES):
        _run("git", "fetch", "origin", "main", cwd=repo)
        with tempfile.TemporaryDirectory(prefix="gsf-coord-") as td:
            worktree = Path(td) / "coord"
            _run("git", "worktree", "add", "--detach", str(worktree), "origin/main", cwd=repo)
            try:
                index = _load_index_file(worktree / INDEX_PATH)
                mutate(index, worktree)
                _write_index_file(worktree / INDEX_PATH, index)
                _configure_git_identity(worktree)
                _run("git", "add", ".gsf", cwd=worktree)
                diff = _run("git", "diff", "--cached", "--quiet", cwd=worktree, check=False)
                if diff.returncode == 0:
                    return
                _run("git", "commit", "-m", f"{message} [skip ci]", cwd=worktree)
                pushed = _run("git", "push", "origin", "HEAD:main", cwd=worktree, check=False)
                if pushed.returncode == 0:
                    return
                combined = f"{pushed.stdout}\n{pushed.stderr}".lower()
                if "non-fast-forward" not in combined and "fetch first" not in combined and "rejected" not in combined:
                    raise subprocess.CalledProcessError(
                        pushed.returncode,
                        ("git", "push", "origin", "HEAD:main"),
                        output=pushed.stdout,
                        stderr=pushed.stderr,
                    )
                last_error = RuntimeError("coordination push raced with another update")
            finally:
                _run("git", "worktree", "remove", "--force", str(worktree), cwd=repo, check=False)
    raise TaskStateError("could not update coordination registry after retries") from last_error


def _claim_path(claim_id: str) -> Path:
    return CLAIM_DIR / f"{claim_id}.json"


def _write_claim_detail(worktree: Path, claim: Claim) -> None:
    path = worktree / _claim_path(claim.id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(claim.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _active_claims(index: dict[str, Any]) -> list[Claim]:
    return [validate_claim_dict(item) for item in index["claims"]]


def _default_worktree_root(repo: Path) -> Path:
    configured = os.getenv("GSF_WORKTREE_ROOT")
    if configured:
        return Path(configured).resolve()
    return repo.parent / ".gsf-worktrees" / repo.name


def _create_product_worktree(repo: Path, claim: Claim) -> Path:
    _run("git", "fetch", "origin", "main", cwd=repo)
    root = _default_worktree_root(repo)
    root.mkdir(parents=True, exist_ok=True)
    path = root / claim.id
    if path.exists():
        raise TaskStateError(f"worktree path already exists: {path}")
    result = _run(
        "git", "worktree", "add", "-b", claim.branch, str(path), "origin/main", cwd=repo, check=False
    )
    if result.returncode != 0:
        raise TaskStateError(result.stderr.strip() or "could not create task worktree")
    push = _run("git", "push", "-u", "origin", claim.branch, cwd=path, check=False)
    if push.returncode != 0:
        _run("git", "worktree", "remove", "--force", str(path), cwd=repo, check=False)
        raise TaskStateError(push.stderr.strip() or "could not publish task branch")
    return path


def task_status_payload(claim: Claim) -> dict[str, Any]:
    evidence = dict(claim.evidence or {})
    tests = evidence.get("tests")
    if not isinstance(tests, dict):
        tests = {}
    return {
        "claim_id": claim.id,
        "branch": claim.branch,
        "scope": claim.scope,
        "state": claim.state,
        "paths": list(claim.paths),
        "commit": evidence.get("commit"),
        "pr": evidence.get("pr"),
        "tests": tests,
        "gate": evidence.get("gate"),
        "railway": evidence.get("railway"),
        "terminal_status": evidence.get("terminal_status"),
        "updated_at": evidence.get("updated_at") or claim.created_at,
    }


def start_task(scope: str, paths: list[str], owner: str | None = None) -> Claim:
    repo = _repo_root()
    requested_paths = normalize_paths(paths)
    if not requested_paths:
        raise ValueError("at least one path is required")

    slug = _slugify(scope)
    claim_id = f"{slug}-{secrets.token_hex(3)}"
    branch = f"chat/{claim_id}"
    claim = Claim(
        id=claim_id,
        branch=branch,
        scope=scope.strip() or slug,
        paths=requested_paths,
        owner=owner or branch,
        created_at=_now_iso(),
        state="active",
    )

    def acquire(index: dict[str, Any], worktree: Path) -> None:
        conflicts = find_conflicts(requested_paths, _active_claims(index))
        if conflicts:
            names = ", ".join(f"{item.id}:{item.branch}" for item in conflicts)
            raise ClaimConflictError(f"ownership conflict with {names}")
        index["claims"].append(claim.to_dict())
        _write_claim_detail(worktree, claim)

    _mutate_main(repo, f"coord: claim {claim_id}", acquire)

    try:
        worktree_path = _create_product_worktree(repo, claim)
    except Exception:
        try:
            finish_task(claim.id, "abandoned", {"reason": "worktree-or-branch-creation-failed"})
        except Exception:
            pass
        raise

    claim.evidence["worktree"] = str(worktree_path)
    return claim


def finish_task(claim_id: str, state: str, evidence: dict[str, Any]) -> None:
    if state not in {"active", "handoff", "completed", "abandoned"}:
        raise ValueError(f"invalid claim state: {state}")
    repo = _repo_root()

    def finish(index: dict[str, Any], worktree: Path) -> None:
        found = False
        for idx, item in enumerate(index["claims"]):
            claim = validate_claim_dict(item)
            if claim.id != claim_id:
                continue
            claim.state = state
            claim.evidence.update(dict(evidence or {}))
            index["claims"][idx] = claim.to_dict()
            _write_claim_detail(worktree, claim)
            found = True
            break
        if not found:
            raise TaskStateError(f"claim not found: {claim_id}")

    _mutate_main(repo, f"coord: {state} {claim_id}", finish)


def get_task(claim_id: str) -> Claim:
    repo = _repo_root()
    _run("git", "fetch", "origin", "main", cwd=repo)
    shown = _run("git", "show", f"origin/main:{INDEX_PATH.as_posix()}", cwd=repo, check=False)
    if shown.returncode != 0:
        raise TaskStateError("claim registry not found on origin/main")
    index = json.loads(shown.stdout)
    for item in index.get("claims", []):
        claim = validate_claim_dict(item)
        if claim.id == claim_id:
            return claim
    raise TaskStateError(f"claim not found: {claim_id}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GSF parallel task coordinator")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    start.add_argument("--scope", required=True)
    start.add_argument("--paths", nargs="+", required=True)
    start.add_argument("--owner")

    finish = sub.add_parser("finish")
    finish.add_argument("--claim", required=True)
    finish.add_argument("--state", choices=["active", "handoff", "completed", "abandoned"], default="completed")
    finish.add_argument("--evidence-json", default="{}")

    status = sub.add_parser("status")
    status.add_argument("--claim", required=True)
    status.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    try:
        if args.command == "start":
            claim = start_task(args.scope, args.paths, args.owner)
            print(json.dumps(task_status_payload(claim), indent=2, sort_keys=True))
        elif args.command == "finish":
            finish_task(args.claim, args.state, json.loads(args.evidence_json))
            print(args.state)
        else:
            claim = get_task(args.claim)
            if args.json:
                print(json.dumps(task_status_payload(claim), indent=2, sort_keys=True))
            else:
                print(f"{claim.id} {claim.state} {claim.branch}")
        return 0
    except ClaimConflictError as exc:
        print(f"BLOCKED: {exc}", file=os.sys.stderr)
        return 3
    except (TaskStateError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=os.sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
