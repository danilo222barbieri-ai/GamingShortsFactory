#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/app")
editor = root / "web" / "editor_2027_component" / "index.html"
text = editor.read_text(encoding="utf-8")

checks = {
    "V298 editor marker": "V298 EDITOR REFERENCE LAYOUT" in text,
    "desktop-only contract": "@media (min-width:761px)" in text and "v298EditorWorkspace" in text,
    "left ad": "v298EditorAdLeft" in text,
    "right ad": "v298EditorAdRight" in text,
    "central player": "v298EditorPlayer" in text,
    "mural instead of robot": "v298EditorMural" in text and "robot" not in text.lower(),
    "three best moments": all(f'data-v298-moment="{i}"' in text for i in (1,2,3)),
    "timeline below player": "v298EditorTimeline" in text,
    "horizontal toolbar": "v298EditorToolbar" in text,
    "legacy V297 sidebar neutralized": ".v297EditorSidebar{display:none!important}" in text,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)
if failed:
    raise AssertionError("V298 editor layout missing: " + ", ".join(failed))
print("V298 editor reference layout: PASS")
