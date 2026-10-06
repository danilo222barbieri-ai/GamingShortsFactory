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
}


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:", msg)


for name, path in FILES.items():
    need(path.is_file(), f"{name} component exists")

hub = FILES["hub"].read_text(encoding="utf-8")
ai = FILES["ai"].read_text(encoding="utf-8")
editor = FILES["editor"].read_text(encoding="utf-8")
share = FILES["share"].read_text(encoding="utf-8")

hub_compact = hub.replace(" ", "")
ai_compact = ai.replace(" ", "")
editor_compact = editor.replace(" ", "")
share_compact = share.replace(" ", "")

need("V296 VISIBLE INTERNAL PAGES — HUB" in hub, "Hub has V296 visible layer")
need("grid-template-columns:repeat(2,minmax(0,1fr))!important" in hub_compact, "Hub desktop dashboard is visibly two-column")
need("width:56px!important;height:56px!important" in hub_compact, "Hub desktop folder icons are visibly larger")
need("font-size:clamp(17px,1.2vw,21px)!important" in hub_compact, "Hub desktop folder titles are visibly larger")
need("min-height:112px!important" in hub_compact, "Hub account header is visibly larger")

need("V296 VISIBLE INTERNAL PAGES — AI" in ai, "AI has V296 visible layer")
need("min-height:204px!important" in ai_compact, "AI engine cards are visibly larger on desktop")
need("width:50px!important;height:50px!important" in ai_compact, "AI engine icons are visibly larger")
need("font-size:16px!important" in ai_compact, "AI engine titles are visibly larger")
need("min-height:50px!important" in ai_compact, "AI primary action is visibly stronger")

need("V296 VISIBLE INTERNAL PAGES — EDITOR" in editor, "Editor has V296 visible layer")
need("max-width:1540px!important" in editor_compact, "Editor cockpit uses wider desktop canvas")
need("width:min(100%,390px)!important" in editor_compact, "Editor vertical player is visibly larger")
need("width:82px!important;height:82px!important" in editor_compact, "Editor rail controls are visibly larger")
need("min-height:56px!important" in editor_compact, "Editor Create Short CTA is visibly larger")

need("V296 VISIBLE INTERNAL PAGES — SHARE" in share, "Share has V296 visible layer")
need("grid-template-columns:repeat(4,minmax(0,1fr))!important" in share_compact, "Share desktop social cards use a clear four-column row")
need("min-height:216px!important" in share_compact, "Share social cards are visibly larger")
need("width:54px!important;height:54px!important" in share_compact, "Share social icons are visibly larger")
need("min-height:54px!important" in share_compact, "Share primary CTA is visibly larger")

start = (WEB / "start_web.sh").read_text(encoding="utf-8")
app = (ROOT / "GamingShortsFactory_V154_STRUCTURAL_HOME.py").read_text(encoding="utf-8")
editor_embed = (WEB / "editor_2027_embed.py").read_text(encoding="utf-8")
need("fix_v296_visible_internal_pages.py" in start, "startup applies V296 after V295")
need("test_v296_visible_internal_pages.py" in start, "startup verifies V296")
need("/creator-hub-v156/?v=296" in app, "Creator Hub cache key is V296")
need("/ai-v221/?v=296" in app, "AI cache key is V296")
need("/share-v156/?v=296" in app, "Share cache key is V296")
need('"gsf_editor_2027_v296"' in editor_embed, "Editor component cache key is V296")
print("V296 visible internal pages: PASS")
