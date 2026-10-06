#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "/app")
WEB = ROOT / "web"

FILES = {
    "hub": WEB / "creator_hub_v156_component" / "index.html",
    "ai": WEB / "ai_v221_component" / "index.html",
    "editor": WEB / "editor_2027_component" / "index.html",
    "share": WEB / "share_v156_component" / "index.html",
    "app": ROOT / "GamingShortsFactory_V154_STRUCTURAL_HOME.py",
    "editor_embed": WEB / "editor_2027_embed.py",
}

MARKERS = {
    "hub": ("/* V295 INTERNAL PAGE SYSTEM — HUB */", "/* END V295 INTERNAL PAGE SYSTEM — HUB */"),
    "ai": ("/* V295 INTERNAL PAGE SYSTEM — AI */", "/* END V295 INTERNAL PAGE SYSTEM — AI */"),
    "editor": ("/* V295 INTERNAL PAGE SYSTEM — EDITOR */", "/* END V295 INTERNAL PAGE SYSTEM — EDITOR */"),
    "share": ("/* V295 INTERNAL PAGE SYSTEM — SHARE */", "/* END V295 INTERNAL PAGE SYSTEM — SHARE */"),
}


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:", msg)


def block(src, start, end):
    i = src.find(start)
    need(i >= 0, start + " exists")
    j = src.find(end, i)
    need(j > i, end + " closes")
    return src[i:j]


for key in ("hub", "ai", "editor", "share"):
    need(FILES[key].is_file(), f"{key} component exists")

src = {key: path.read_text(encoding="utf-8") for key, path in FILES.items() if path.is_file()}
blocks = {key: block(src[key], *MARKERS[key]) for key in MARKERS}

for key, css in blocks.items():
    need("@media (min-width:761px)" in css, f"{key} has paired desktop rules")
    need("@media (max-width:760px)" in css, f"{key} has paired mobile rules")

hub = blocks["hub"]
need("#hub .closeTop" in hub and "display:none!important" in hub, "Creator Hub return is owned by global Game Bar")
need(".profileOverviewGrid" in hub and "repeat(2,minmax(0,1fr))" in hub, "Profile overview becomes a real two-column phone dashboard")
need('data-view="dashboard"' in hub and "repeat(5,minmax(0,1fr))" in hub, "Creator Hub keeps all five modules visible on mobile")
need(".folderScroller" in hub and "overflow:auto!important" in hub, "Hub detail folders remain scroll-safe on small phones")

ai = blocks["ai"]
need(".engines" in ai and "repeat(2,minmax(0,1fr))" in ai, "AI engines use a 2x2 mobile grid")
need(".create" in ai and "width:100%!important" in ai, "AI primary action is thumb-friendly full width")
need(".moments" in ai and "repeat(3,minmax(0,1fr))" in ai, "AI keeps all three candidate moments visible together")
need(".momentActionGrid" in ai and "grid-template-columns:1fr!important" in ai, "AI next actions stack cleanly on phone")

editor = blocks["editor"]
need(".cockpit>.rail" in editor and "visibility:visible!important" in editor and "opacity:1!important" in editor, "Editor rails are explicitly visible on iOS/mobile")
need("min-width:48px!important" in editor and "min-height:48px!important" in editor, "Editor mobile controls meet 48px touch target")
need(".stage.r916" in editor and "100dvh" in editor, "Editor player is sized against the phone viewport")
need(".createShortJourneyBtn" in editor and "min-height:48px!important" in editor, "Editor-to-Short CTA stays visible and touchable")

share = blocks["share"]
need(".socials" in share and "repeat(2,minmax(0,1fr))" in share, "Share keeps social destinations in a 2x2 phone grid")
need(".downloadBtn" in share and "width:100%!important" in share, "Download CTA is full width on phone")
need(".actions" in share and "grid-template-columns:1fr 1fr!important" in share, "Secondary Share actions remain paired on mobile")

need(FILES["app"].is_file(), "structural shell exists")
app = src["app"]
need('data-target="hub" data-section="dashboard"' in app, "global Game Bar keeps Hub route")
need('data-target="hub" data-section="shorts"' in app, "global Game Bar keeps My Shorts route")
need('data-target="hub" data-section="drafts"' in app, "global Game Bar keeps Drafts route")
need("/creator-hub-v156/?v=295" in app, "Creator Hub iframe cache is bumped to V295")
need("/share-v156/?v=295" in app, "Share iframe cache is bumped to V295")

need(FILES["editor_embed"].is_file(), "Editor embed exists")
need('"gsf_editor_2027_v295"' in src["editor_embed"], "Editor component asset key is bumped to V295")

print("V295 internal responsive page system: PASS")
