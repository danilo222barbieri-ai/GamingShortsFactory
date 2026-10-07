#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
FIX = WEB / "fix_v308_mobile_master.py"
if not FIX.is_file():
    raise SystemExit("V308 FAIL: mobile-master canonicalizer missing")
spec = importlib.util.spec_from_file_location("v308_mobile_master", FIX)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
source = (WEB / "editor_2027_component" / "index.html").read_text(encoding="utf-8")
out = mod.canonicalize_text("editor", source)
embed = (WEB / "editor_2027_embed.py").read_text(encoding="utf-8")
checks = {
    "single editor root": out.count('id="ng27"') == 1,
    "single cockpit markup": out.count('class="cockpit"') == 1,
    "controls preserved": all(label in out.upper() for label in ("FRAME","CAPTION","LOOK","AUDIO","AI")),
    "9:16 stage preserved": "r916" in out,
    "timeline preserved": "timeline" in out,
    "legacy runtimes removed": all(x not in out for x in ("v297EditorRuntime","v298EditorGraphicOnly","v298EditorWorkspace","V305 EDITOR DESKTOP SINGLE SURFACE")),
    "legacy layout attrs removed": "data-v297-layout" not in out and "data-v298-layout" not in out,
    "no desktop min-width layout": "@media (min-width" not in out and "@media(min-width" not in out,
    "fluid editor master": "gsf-v308-editor-fluid-master" in out and "clamp(" in out,
    "render kwargs preserved": "def editor_2027_render_kwargs" in embed and '"fmt"' in embed and '"smart_reframe"' in embed,
}
failed=[]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)
    if not ok: failed.append(name)
if failed:
    raise SystemExit("V308 Editor mobile-master failed: " + ", ".join(failed))
print("V308 Editor mobile-master: PASS")
