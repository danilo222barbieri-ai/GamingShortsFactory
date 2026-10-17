#!/usr/bin/env python3
"""Keep the GSF Alive 2 runtime inlined verbatim in every user-facing surface.

web/gsf_alive_v418.js is the canonical source. Each surface carries exactly one
block delimited by GSF_ALIVE:BEGIN / GSF_ALIVE:END (same pattern as the Night
Arena theme), so pages are served byte-identical from the repo with no build or
startup rewrite.

    python tools/gsf_alive_inline.py          # check, exit 1 on drift
    python tools/gsf_alive_inline.py --write  # refresh the existing blocks
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "web" / "gsf_alive_v418.js"
SURFACES = [
    "web/home_v154_component/index.html",
    "web/ai_v221_component/index.html",
    "web/share_v156_component/index.html",
    "web/creator_hub_v156_component/index.html",
    # Next: web/game_editor_mobile_component/index.html and web/editor_2027_component/index.html
    # once their claims release (2026-10-17 they belong to other chats).
]
BLOCK = re.compile(r"/\* GSF_ALIVE:BEGIN \*/\n(.*?)\n?/\* GSF_ALIVE:END \*/", re.S)


def runtime() -> str:
    text = RUNTIME.read_text(encoding="utf-8").strip()
    if "</script" in text.lower():
        raise SystemExit("gsf_alive_v418.js must not contain a closing script tag")
    return text


def block() -> str:
    return "/* GSF_ALIVE:BEGIN */\n" + runtime() + "\n/* GSF_ALIVE:END */"


def check() -> list[str]:
    code = runtime()
    problems = []
    for rel in SURFACES:
        found = BLOCK.findall((ROOT / rel).read_text(encoding="utf-8"))
        if len(found) != 1:
            problems.append(f"{rel}: expected exactly one GSF_ALIVE block, found {len(found)}")
        elif found[0].strip() != code:
            problems.append(f"{rel}: GSF_ALIVE block drifted from web/gsf_alive_v418.js")
    return problems


def write() -> None:
    fresh = block()
    for rel in SURFACES:
        path = ROOT / rel
        html = path.read_text(encoding="utf-8")
        if len(BLOCK.findall(html)) != 1:
            raise SystemExit(f"{rel}: add one <script>/* GSF_ALIVE:BEGIN */ ... /* GSF_ALIVE:END */</script> first")
        updated = BLOCK.sub(lambda _m: fresh, html, count=1)
        if updated != html:
            path.write_text(updated, encoding="utf-8")
            print("updated", rel)


def main(argv: list[str]) -> int:
    if "--write" in argv:
        write()
    problems = check()
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
