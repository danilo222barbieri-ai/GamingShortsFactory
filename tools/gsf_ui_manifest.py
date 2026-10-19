#!/usr/bin/env python3
"""GSF canonical UI manifest — one definition of "the files that are served".

The repository is the single source of truth for the runtime UI: every file
listed here is copied byte-for-byte into the image and must never be rewritten
by a build step, startup script or legacy patch. This tool computes the same
deterministic manifest from either side so they can be compared:

  repo side   python tools/gsf_ui_manifest.py digest --repo .
  image side  python /app/gsf_ui_manifest.py write          (Docker build)
              python /app/gsf_ui_manifest.py verify         (startup / CI)
  compare     python tools/gsf_ui_manifest.py compare --repo . --image-json f.json

Paths in the manifest are always *image* paths (relative to /app), so a repo
manifest and an image manifest are directly comparable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

IMAGE_ROOT = Path("/app")
MANIFEST_NAME = ".gsf-ui-manifest.json"
SCHEMA = "gsf-ui-manifest/1"

# repo-relative source -> image-relative destination (directories map recursively)
CANONICAL_MAP = (
    ("app.py", "app.py"),
    ("web", "web"),
    ("web/gsf_perf.py", "gsf_perf.py"),
    ("gsf_alive.py", "gsf_alive.py"),
    ("gsf_alive_notifications.py", "gsf_alive_notifications.py"),
    ("gsf_editor_v403.py", "gsf_editor_v403.py"),
    ("gsf_project_state.py", "gsf_project_state.py"),
    ("gsf_core", "gsf_core"),
    (".streamlit", ".streamlit"),
)

# Files the Docker build legitimately *adds* (never modifies) under canonical dirs.
# web/app_icons/app-icon.png is tracked and must remain byte-identical.
BUILD_GENERATED = frozenset({
    "web/app_icons/app-icon-192.png",
    "web/app_icons/app-icon-512.png",
    "web/app_icons/apple-touch-icon.png",
    "web/app_icons/official_logo_180.valid.b64",
})

SKIP_DIRS = frozenset({"__pycache__", ".pytest_cache", ".mypy_cache"})
SKIP_SUFFIXES = (".pyc", ".pyo")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _walk(path: Path):
    if path.is_file():
        yield path
        return
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name.endswith(SKIP_SUFFIXES):
                continue
            yield Path(dirpath) / name


def files_from_repo(repo: Path) -> dict[str, str]:
    """image-relative path -> sha256, computed from a repository checkout."""
    out: dict[str, str] = {}
    for src, dst in CANONICAL_MAP:
        base = repo / src
        if not base.exists():
            raise SystemExit(f"GSF UI manifest: canonical source missing: {src}")
        for f in _walk(base):
            rel = Path(dst) / f.relative_to(base) if base.is_dir() else Path(dst)
            out[rel.as_posix()] = _sha256(f)
    return out


def files_from_image(root: Path, expected: set[str] | None = None) -> dict[str, str]:
    """image-relative path -> sha256 for every file under the canonical image dirs."""
    out: dict[str, str] = {}
    for _src, dst in CANONICAL_MAP:
        base = root / dst
        if not base.exists():
            continue
        for f in _walk(base):
            rel = f.relative_to(root).as_posix()
            if rel in BUILD_GENERATED:
                continue
            out[rel] = _sha256(f)
    return out


def digest(files: dict[str, str]) -> str:
    h = hashlib.sha256()
    for rel in sorted(files):
        h.update(rel.encode("utf-8") + b"\0" + files[rel].encode("ascii") + b"\n")
    return h.hexdigest()


def manifest(files: dict[str, str]) -> dict:
    return {"schema": SCHEMA, "digest": digest(files), "count": len(files), "files": files}


def diff(expected: dict[str, str], actual: dict[str, str]) -> dict[str, list[str]]:
    return {
        "modified": sorted(k for k in expected if k in actual and actual[k] != expected[k]),
        "missing": sorted(k for k in expected if k not in actual),
        "unexpected": sorted(k for k in actual if k not in expected),
    }


def _report(problems: dict[str, list[str]], github: bool) -> int:
    bad = sum(len(v) for v in problems.values())
    for kind, items in problems.items():
        for item in items[:200]:
            line = f"GSF UI manifest {kind}: {item}"
            print(f"::error title=Canonical UI drift::{line}" if github else line, flush=True)
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("digest", help="print the repo manifest digest (or full JSON)")
    d.add_argument("--repo", default=".")
    d.add_argument("--json", action="store_true")
    w = sub.add_parser("write", help="build time: record the image manifest")
    w.add_argument("--root", default=str(IMAGE_ROOT))
    v = sub.add_parser("verify", help="image files still match the recorded manifest")
    v.add_argument("--root", default=str(IMAGE_ROOT))
    c = sub.add_parser("compare", help="repo checkout vs an image manifest JSON")
    c.add_argument("--repo", default=".")
    c.add_argument("--image-json", required=True)
    args = ap.parse_args(argv)
    github = bool(os.environ.get("GITHUB_ACTIONS"))

    if args.cmd == "digest":
        m = manifest(files_from_repo(Path(args.repo).resolve()))
        print(json.dumps(m, indent=1, sort_keys=True) if args.json else m["digest"])
        return 0

    if args.cmd == "write":
        root = Path(args.root)
        m = manifest(files_from_image(root))
        (root / MANIFEST_NAME).write_text(json.dumps(m, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"GSF UI manifest written: digest={m['digest']} files={m['count']}", flush=True)
        return 0

    if args.cmd == "verify":
        root = Path(args.root)
        path = root / MANIFEST_NAME
        if not path.is_file():
            print("GSF UI manifest missing: image was not built by the canonical pipeline", flush=True)
            return 2
        recorded = json.loads(path.read_text(encoding="utf-8"))
        actual = files_from_image(root)
        bad = _report(diff(recorded["files"], actual), github)
        if bad:
            print(f"GSF UI manifest verify FAILED: {bad} file(s) differ from the build manifest", flush=True)
            return 1
        print(f"GSF UI manifest verify PASS: digest={recorded['digest']} files={recorded['count']}", flush=True)
        return 0

    if args.cmd == "compare":
        expected = files_from_repo(Path(args.repo).resolve())
        image = json.loads(Path(args.image_json).read_text(encoding="utf-8"))
        bad = _report(diff(expected, image["files"]), github)
        if bad:
            print(f"GSF UI manifest compare FAILED: image differs from repository in {bad} file(s)", flush=True)
            return 1
        print(f"GSF UI manifest compare PASS: repo == image digest={digest(expected)}", flush=True)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
