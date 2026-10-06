#!/usr/bin/env python3
from pathlib import Path
import sys


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:", msg)


home = Path(sys.argv[1] if len(sys.argv) > 1 else "/app/web/home_v154_component/index.html")
need(home.is_file(), "Home component exists")
s = home.read_text(encoding="utf-8")
marker = "/* V294 DESKTOP HOME ALIGNMENT */"
need(marker in s, "V294 desktop alignment marker exists")
block = s.split(marker, 1)[1].split("/* END V294 DESKTOP HOME ALIGNMENT */", 1)[0]

# This patch is deliberately desktop-only. Mobile was already approved and must
# not be changed while restoring the laptop/desktop composition.
need("@media (min-width:761px)" in block, "V294 is scoped to desktop")
need("@media (max-width:760px)" not in block, "V294 does not alter mobile geometry")

# Regression: V274 compressed the whole desktop CTA group to 390-440px and the
# Game Bar inherited that width. A 1366-class laptop must keep a real desktop
# composition instead of looking like the phone UI shrunk into the center.
need("--gsf-desk-content:clamp(560px,48vw,680px)" in block.replace(" ", ""), "desktop CTA group is restored to readable width")
need("--gsf-desk-card-h:clamp(158px,20vh,180px)" in block.replace(" ", ""), "desktop CTA cards regain useful height")
need("width:clamp(560px,55vw,700px)!important" in block.replace(" ", ""), "Game Bar width no longer follows the compressed V274 CTA width")
need("--gsf-desk-ring:clamp(290px,min(25vw,39vh),350px)" in block.replace(" ", ""), "desktop uploader regains visual priority")

# Short laptop viewport is the exact failure shown in the user screenshot.
need("@media (min-width:1000px) and (max-height:720px)" in block, "short-laptop correction exists")
need("--gsf-desk-content:clamp(540px,47vw,640px)" in block.replace(" ", ""), "short laptop keeps desktop CTA width")
need("--gsf-desk-ring:clamp(270px,min(25vw,42vh),310px)" in block.replace(" ", ""), "short laptop keeps a substantial uploader")
need("--gsf-desk-nav-h:52px" in block.replace(" ", ""), "short laptop Game Bar remains readable")

# Keep the approved no-scroll architecture and side advertising while correcting
# their proportions rather than hiding them.
need("overflow:hidden!important" in block.replace(" ", ""), "desktop Home remains no-scroll")
need(".sideAd" in block and "height:clamp(270px,43vh,330px)!important" in block.replace(" ", ""), "short-laptop ad rails are proportionate")
print("V294 desktop Home alignment: PASS")
