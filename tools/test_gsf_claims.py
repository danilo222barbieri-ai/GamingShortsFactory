from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.gsf_claims import Claim, find_conflicts, normalize_paths, patterns_overlap, validate_claim_dict
from tools.gsf_task import ClaimConflictError, finish_task, start_task


def run(*args: str, cwd: Path) -> str:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True)
    return result.stdout.strip()


@contextmanager
def chdir(path: Path):
    old = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def make_remote(root: Path) -> tuple[Path, Path, Path]:
    remote = root / "remote.git"
    seed = root / "seed"
    clone_a = root / "clone-a"
    clone_b = root / "clone-b"
    run("git", "init", "--bare", str(remote), cwd=root)
    seed.mkdir()
    run("git", "init", "-b", "main", cwd=seed)
    run("git", "config", "user.name", "GSF Test", cwd=seed)
    run("git", "config", "user.email", "gsf@example.invalid", cwd=seed)
    (seed / ".gsf/claims").mkdir(parents=True)
    (seed / ".gsf/claims/index.json").write_text('{"version":1,"claims":[]}\n', encoding="utf-8")
    (seed / "README.md").write_text("seed\n", encoding="utf-8")
    run("git", "add", ".", cwd=seed)
    run("git", "commit", "-m", "seed", cwd=seed)
    run("git", "remote", "add", "origin", str(remote), cwd=seed)
    run("git", "push", "-u", "origin", "main", cwd=seed)
    run("git", "clone", "-b", "main", str(remote), str(clone_a), cwd=root)
    run("git", "clone", "-b", "main", str(remote), str(clone_b), cwd=root)
    for clone in (clone_a, clone_b):
        run("git", "config", "user.name", "GSF Test", cwd=clone)
        run("git", "config", "user.email", "gsf@example.invalid", cwd=clone)
    return remote, clone_a, clone_b


class ClaimModelTests(unittest.TestCase):
    def test_normalize_paths_deduplicates_and_sorts(self):
        self.assertEqual(normalize_paths(["web/b.py", "web/a.py", "web/b.py"]), ["web/a.py", "web/b.py"])

    def test_exact_overlap(self):
        self.assertTrue(patterns_overlap("web/editor.py", "web/editor.py"))

    def test_glob_exact_overlap(self):
        self.assertTrue(patterns_overlap("web/fix_v*_mobile_editor_*.py", "web/fix_v403_mobile_editor_x.py"))
        self.assertTrue(patterns_overlap("web/fix_v403_mobile_editor_x.py", "web/fix_v*_mobile_editor_*.py"))

    def test_glob_glob_overlap(self):
        self.assertTrue(patterns_overlap("web/editor_*.py", "web/*_2027.py"))

    def test_non_overlap(self):
        self.assertFalse(patterns_overlap("web/editor_*.py", "web/ai_worker_server.py"))

    def test_validate_rejects_unknown_state(self):
        with self.assertRaises(ValueError):
            validate_claim_dict({
                "id": "x",
                "branch": "chat/x-abcd",
                "scope": "x",
                "paths": ["web/x.py"],
                "owner": "chat/x-abcd",
                "created_at": "2026-10-13T23:50:00+02:00",
                "state": "mystery",
            })

    def test_only_active_and_handoff_block(self):
        requested = ["web/editor.py"]
        active = Claim("a", "chat/a", "editor", ["web/editor.py"], "chat/a", "2026-10-13T23:50:00+02:00", "active")
        handoff = Claim("b", "chat/b", "editor", ["web/editor.py"], "chat/b", "2026-10-13T23:50:00+02:00", "handoff")
        completed = Claim("c", "chat/c", "editor", ["web/editor.py"], "chat/c", "2026-10-13T23:50:00+02:00", "completed")
        conflicts = find_conflicts(requested, [active, handoff, completed])
        self.assertEqual([c.id for c in conflicts], ["a", "b"])


class TaskBootstrapTests(unittest.TestCase):
    def test_non_overlapping_tasks_get_unique_branches_and_both_claims_survive(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, clone_a, clone_b = make_remote(root)
            os.environ["GSF_WORKTREE_ROOT"] = str(root / "worktrees")
            try:
                with chdir(clone_a):
                    first = start_task("Editor mobile", ["web/editor.py"], owner="chat-a")
                with chdir(clone_b):
                    second = start_task("Home desktop", ["web/home.py"], owner="chat-b")
                self.assertNotEqual(first.branch, second.branch)
                run("git", "fetch", "origin", "main", cwd=clone_b)
                raw = run("git", "show", "origin/main:.gsf/claims/index.json", cwd=clone_b)
                ids = {item["id"] for item in json.loads(raw)["claims"]}
                self.assertEqual(ids, {first.id, second.id})
            finally:
                os.environ.pop("GSF_WORKTREE_ROOT", None)

    def test_overlapping_second_task_is_blocked_after_refresh(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, clone_a, clone_b = make_remote(root)
            os.environ["GSF_WORKTREE_ROOT"] = str(root / "worktrees")
            try:
                with chdir(clone_a):
                    start_task("Editor A", ["web/editor.py"], owner="chat-a")
                with chdir(clone_b):
                    with self.assertRaises(ClaimConflictError):
                        start_task("Editor B", ["web/editor.py"], owner="chat-b")
            finally:
                os.environ.pop("GSF_WORKTREE_ROOT", None)

    def test_finish_preserves_other_claim_and_marks_target_completed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, clone_a, clone_b = make_remote(root)
            os.environ["GSF_WORKTREE_ROOT"] = str(root / "worktrees")
            try:
                with chdir(clone_a):
                    first = start_task("Editor", ["web/editor.py"], owner="chat-a")
                with chdir(clone_b):
                    second = start_task("Home", ["web/home.py"], owner="chat-b")
                    finish_task(second.id, "completed", {"tests": "PASS"})
                    run("git", "fetch", "origin", "main", cwd=clone_b)
                    raw = run("git", "show", "origin/main:.gsf/claims/index.json", cwd=clone_b)
                claims = {item["id"]: item for item in json.loads(raw)["claims"]}
                self.assertEqual(claims[first.id]["state"], "active")
                self.assertEqual(claims[second.id]["state"], "completed")
                self.assertEqual(claims[second.id]["evidence"]["tests"], "PASS")
            finally:
                os.environ.pop("GSF_WORKTREE_ROOT", None)


if __name__ == "__main__":
    unittest.main()
