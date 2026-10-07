#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "/app")
HOME = ROOT / "web" / "home_v154_component" / "index.html"
EMBED = ROOT / "web" / "home_v154_embed.py"
START = ROOT / "web" / "start_web.sh"

home = HOME.read_text(encoding="utf-8")
embed = EMBED.read_text(encoding="utf-8")
start = START.read_text(encoding="utf-8")

begin = home.rfind("/* V306 HOME VISUAL LOCK */")
end = home.find("/* END V306 HOME VISUAL LOCK */", begin)
assert begin >= 0 and end > begin, "V306 Home visual lock block missing"
block = home[begin:end]

checks = [
    ("desktop-only lock", "@media (min-width:761px)" in block and "max-width:760px" not in block),
    ("approved pale canvas", "linear-gradient(180deg,#FEFFFF 0%,#FBFDFF 54%,#F7FCFF 100%)" in block),
    ("white uploader center", "#home154 .circle{background:#FFF!important}" in block),
    ("cyan-mint uploader ring", "rgba(109,195,244,.68)" in block and "rgba(113,229,192,.42)" in block),
    ("AI icon blue", "#home154 .feature.fAi .featureIcon{background:#D8E9FF!important;color:#1875E6!important}" in block),
    ("Editor icon mint", "#home154 .feature.fEditor .featureIcon{background:#CFF4DD!important;color:#078F61!important}" in block),
    ("Short icon yellow", "#home154 .feature.fShort .featureIcon{background:#FFE9A8!important;color:#D68000!important}" in block),
    ("milky Game Bar", "background:rgba(255,255,255,.93)!important" in block and "rgba(219,241,255,.70)" in block),
    ("fresh Home component cache", '"gsf_home_v154_live_306"' in embed),
    ("startup applies V306", "fix_v306_home_visual_lock.py" in start and "test_v306_home_visual_lock.py" in start),
    ("V306 runs after Home geometry and project patches", start.index("fix_v301_home_desk_rebalance.py") < start.index("fix_v306_home_visual_lock.py") and start.index("fix_v304_project_draft_details.py") < start.index("fix_v306_home_visual_lock.py")),
    ("V306 runs before final app generation", start.index("fix_v306_home_visual_lock.py") < start.index("apply_v293_render_memory_guard.py")),
]

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(("PASS" if ok else "FAIL") + ": " + name)
if failed:
    raise SystemExit("V306 Home visual lock failed: " + ", ".join(failed))
print("V306 Home visual lock: PASS")
