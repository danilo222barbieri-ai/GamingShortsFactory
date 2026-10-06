#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "/app")
WEB = ROOT / "web"

HUB = WEB / "creator_hub_v156_component" / "index.html"
AI = WEB / "ai_v221_component" / "index.html"
EDITOR = WEB / "editor_2027_component" / "index.html"
SHARE = WEB / "share_v156_component" / "index.html"
APP = ROOT / "GamingShortsFactory_V154_STRUCTURAL_HOME.py"
EDITOR_EMBED = WEB / "editor_2027_embed.py"
START = WEB / "start_web.sh"


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:", msg)


for path in (HUB, AI, EDITOR, SHARE, APP, EDITOR_EMBED, START):
    need(path.is_file(), f"{path.name} exists")

hub = HUB.read_text(encoding="utf-8")
ai = AI.read_text(encoding="utf-8")
editor = EDITOR.read_text(encoding="utf-8")
share = SHARE.read_text(encoding="utf-8")
app = APP.read_text(encoding="utf-8")
embed = EDITOR_EMBED.read_text(encoding="utf-8")
start = START.read_text(encoding="utf-8")
hub_c = hub.replace(" ", "")
ai_c = ai.replace(" ", "")
editor_c = editor.replace(" ", "")
share_c = share.replace(" ", "")

# Creator Hub: real desktop shell, not another size-only CSS layer.
need("V297 DESK REBUILD — HUB" in hub, "Hub has V297 rebuild marker")
need('data-v297-layout="hub"' in hub, "Hub exposes V297 desktop layout")
need("v297HubSidebar" in hub and "v297HubMain" in hub, "Hub has sidebar + workspace DOM")
need("grid-template-columns:190pxminmax(0,1fr)" in hub_c, "Hub desktop uses fixed sidebar plus wide workspace")
need("data-v297-target=\"profile\"" in hub, "Hub sidebar routes into the real profile view")
need("data-v297-target=\"drafts\"" in hub, "Hub sidebar routes into the real drafts view")
need("data-v297-target=\"shorts\"" in hub, "Hub sidebar routes into the real shorts view")

# AI: 2x2 engines plus three real moments in one desk workspace.
need("V297 DESK REBUILD — AI" in ai, "AI has V297 rebuild marker")
need('data-v297-layout="ai"' in ai, "AI exposes V297 desktop layout")
need("v297AiSidebar" in ai and "v297AiMain" in ai, "AI has sidebar + main workspace DOM")
need("grid-template-columns:repeat(2,minmax(0,1fr))" in ai_c, "AI engines are a real 2x2 desktop grid")
need("v297AiMoments" in ai, "AI has a dedicated three-moment desk strip")
need("querySelectorAll('.engine')" in ai or 'querySelectorAll(".engine")' in ai, "AI keeps the real engine controls")

# Editor: three-column desktop cockpit and right-side moment rail.
need("V297 DESK REBUILD — EDITOR" in editor, "Editor has V297 rebuild marker")
need('data-v297-layout="editor"' in editor, "Editor exposes V297 desktop layout")
need("v297EditorGrid" in editor, "Editor has V297 three-column grid")
need("v297EditorMoments" in editor, "Editor has a right-side moment panel")
need("grid-template-columns:110pxminmax(360px,520px)minmax(300px,1fr)" in editor_c, "Editor matches desk reference proportions")
need("v297EditorTimeline" in editor, "Editor timeline has a dedicated desk row")
need("createShortJourneyBtn" in editor, "Editor keeps the real Create Short action")

# Share: actual preview + social publication area + download row.
need("V297 DESK REBUILD — SHARE" in share, "Share has V297 rebuild marker")
need('data-v297-layout="share"' in share, "Share exposes V297 desktop layout")
need("v297ShareGrid" in share and "v297SharePreview" in share and "v297ShareMain" in share, "Share has preview + publication workspace DOM")
need("<video" in share and "v297PreviewVideo" in share, "Share includes a real video preview element")
need("state.video_url" in share, "Share preview is wired to the real final video URL")
need("grid-template-columns:minmax(250px,330px)minmax(0,1fr)" in share_c, "Share uses reference-like preview + content desktop split")
need("downloadBtn" in share, "Share keeps the real download action")

# Fresh caches so the browser cannot keep V296 assets.
for route in ("creator-hub-v156", "share-v156", "ai-v221"):
    need(f"/{route}/?v=297" in app, f"{route} cache key is V297")
need('"gsf_editor_2027_v297"' in embed, "Editor component cache key is V297")

# Startup must apply and verify V297 after V296.
need("fix_v297_desk_rebuild.py" in start, "startup applies V297")
need("test_v297_desk_rebuild.py" in start, "startup verifies V297")
need(start.index("fix_v296_visible_internal_pages.py") < start.index("fix_v297_desk_rebuild.py"), "V297 runs after V296")

print("V297 desk rebuild: PASS")
