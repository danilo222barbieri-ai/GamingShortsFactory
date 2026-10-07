#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/app")
start = (root / "web/start_web.sh").read_text(encoding="utf-8")
home = (root / "web/home_v154_component/index.html").read_text(encoding="utf-8")
embed = (root / "web/home_v154_embed.py").read_text(encoding="utf-8")

checks = [
    ("V301 runtime Home rebalance is disabled", "python /app/web/fix_v301_home_desk_rebalance.py" not in start),
    ("V306 Home visual lock runs", "python /app/web/fix_v306_home_visual_lock.py" in start),
    ("V306 Home regression gate runs", "python /app/web/test_v306_home_visual_lock.py /app" in start),
    ("approved Home palette marker exists", "V306 APPROVED HOME VISUAL LOCK" in home),
    ("approved pale background restored", "linear-gradient(180deg,#FEFFFF 0%,#FBFDFF 54%,#F7FCFF 100%)" in home),
    ("approved white uploader center restored", "#home154 .circle{background:#FFF!important}" in home),
    ("approved uploader blue restored", "#home154 .circle .icon{color:#6099E2!important}" in home),
    ("approved AI icon colors restored", "background:#D8E9FF!important;color:#1875E6!important" in home),
    ("approved Editor icon colors restored", "background:#CFF4DD!important;color:#078F61!important" in home),
    ("approved Short icon colors restored", "background:#FFE9A8!important;color:#D68000!important" in home),
    ("approved nav material restored", "background:rgba(255,255,255,.93)!important" in home),
    ("V294 desktop geometry remains available", "V294 HOME DESKTOP REALIGN" in home or "fix_v294_home_desktop_realign.py" in start),
    ("Home component cache bumped", "gsf_home_v154_live_306" in embed),
]

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(("PASS" if ok else "FAIL") + ": " + name)
if failed:
    raise SystemExit("V306 Home visual lock failed: " + ", ".join(failed))
print("V306 Home visual lock: PASS")
