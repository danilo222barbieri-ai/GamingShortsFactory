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

surfaces = {
    "ai": WEB / "ai_v221_component" / "index.html",
    "hub": WEB / "creator_hub_v156_component" / "index.html",
    "share": WEB / "share_v156_component" / "index.html",
}
outputs = {name: mod.canonicalize_text(name, path.read_text(encoding="utf-8")) for name, path in surfaces.items()}

checks = []
for name, text in outputs.items():
    checks.extend([
        (f"{name}: no DESKTOP marker", "DESKTOP" not in text and " DESK " not in text),
        (f"{name}: no min-width layout", "@media (min-width" not in text and "@media(min-width" not in text),
        (f"{name}: fluid master", f"gsf-v308-{name}-fluid-master" in text and "clamp(" in text),
    ])

checks.extend([
    ("AI keeps four engines", outputs["ai"].count('data-engine="') >= 4 and all(x in outputs["ai"] for x in ('data-engine="auto"','data-engine="best"','data-engine="action"','data-engine="reaction"'))),
    ("AI keeps duration", "duration" in outputs["ai"].lower()),
    ("Hub keeps folders", all(x in outputs["hub"] for x in ('data-folder="profile"','data-folder="social"','data-folder="live"'))),
    ("Hub keeps projects/drafts", 'data-folder="project"' in outputs["hub"] or 'data-folder="drafts"' in outputs["hub"]),
    ("Share keeps socials", all(x in outputs["share"].lower() for x in ("youtube","tiktok","instagram","facebook"))),
    ("Share keeps download", "download" in outputs["share"].lower()),
])

failed=[]
for name, ok in checks:
    print(("PASS" if ok else "FAIL") + ": " + name)
    if not ok: failed.append(name)
if failed:
    raise SystemExit("V308 responsive surfaces failed: " + ", ".join(failed))
print("V308 responsive surfaces: PASS")
