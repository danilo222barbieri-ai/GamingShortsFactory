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
source = (WEB / "home_v154_component" / "index.html").read_text(encoding="utf-8")
out = mod.canonicalize_text("home", source)
embed = (WEB / "home_v154_embed.py").read_text(encoding="utf-8")
forbidden = ("V267", "V268", "V294", "V296", "V297", "V298", "V301", "V305")
checks = {
    "legacy desktop markers removed": not any(marker in out for marker in forbidden),
    "no desktop min-width composition": "@media (min-width" not in out and "@media(min-width" not in out,
    "uploader preserved": "rings" in out and "circle" in out,
    "murals preserved": "scribble" in out,
    "three CTAs preserved": all(label in out for label in ("Crea con IA", "Game Editor", "Crea Short")),
    "fluid master present": "gsf-v308-home-fluid-master" in out and "clamp(" in out,
    "viewport-neutral parent": "@media (max-width:760px)" not in embed and "gsf-v308-viewport-shell" in embed,
}
failed=[]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)
    if not ok: failed.append(name)
if failed:
    raise SystemExit("V308 Home mobile-master failed: " + ", ".join(failed))
print("V308 Home mobile-master: PASS")
