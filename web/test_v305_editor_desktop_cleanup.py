#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "/app")
WEB = ROOT / "web"
EDITOR = WEB / "editor_2027_component" / "index.html"
EMBED = WEB / "editor_2027_embed.py"
START = WEB / "start_web.sh"


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:", msg)


for path in (EDITOR, EMBED, START):
    need(path.is_file(), f"{path.name} exists")

editor = EDITOR.read_text(encoding="utf-8")
embed = EMBED.read_text(encoding="utf-8")
start = START.read_text(encoding="utf-8")

need("/* V305 DESKTOP EDITOR CLEANUP */" in editor, "Editor has V305 desktop cleanup marker")
need("/* END V305 DESKTOP EDITOR CLEANUP */" in editor, "Editor closes V305 desktop cleanup block")
block = editor.split("/* V305 DESKTOP EDITOR CLEANUP */", 1)[1].split("/* END V305 DESKTOP EDITOR CLEANUP */", 1)[0]

need("@media (min-width:821px)" in block, "V305 cleanup is desktop-scoped")
need("grid-template-columns:96px minmax(300px,420px) 96px" in block, "desktop cockpit uses balanced rail/player/rail columns")
need("background:linear-gradient(180deg,#111D28 0%,#08111A 100%)" in block, "9:16 stage stays visibly defined even before video paint")
need(".gsfGuide{display:none!important}" in block, "broken desktop Editor mural is removed")
need("@media(max-width:820px)" not in block, "V305 does not override the mobile Editor")
need('data-editor-build="2027.6-v305"' in editor, "Editor build marker is V305")
need('"gsf_editor_2027_v305"' in embed, "Editor component cache key is V305")

need("fix_v305_editor_desktop_cleanup.py" in start, "startup applies V305 desktop cleanup")
need("test_v305_editor_desktop_cleanup.py" in start, "startup verifies V305 desktop cleanup")
need(start.index("fix_v299_editor_clean_restore.py") < start.index("fix_v305_editor_desktop_cleanup.py"), "V305 runs after the V299 clean Editor restore")
need(start.index("fix_v305_editor_desktop_cleanup.py") < start.index("apply_v293_render_memory_guard.py"), "V305 runs before final app generation")

print("V305 Editor desktop cleanup: PASS")
