#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path("/app")
WEB = ROOT / "web"
HUB = WEB / "creator_hub_v156_component" / "index.html"
AI = WEB / "ai_v221_component" / "index.html"
EDITOR = WEB / "editor_2027_component" / "index.html"
SHARE = WEB / "share_v156_component" / "index.html"
APP = ROOT / "GamingShortsFactory_V154_STRUCTURAL_HOME.py"
EDITOR_EMBED = WEB / "editor_2027_embed.py"

HUB_CSS = r'''
/* V296 VISIBLE INTERNAL PAGES — HUB */
@media (min-width:761px){
  #hub{
    padding:18px 24px 14px!important;
    gap:14px!important;
  }
  #hub .top{min-height:62px!important}
  #hub h1{font-size:clamp(28px,2.15vw,36px)!important}
  #hub .subtitle{font-size:11px!important}
  #hub .profileCard{
    min-height:112px!important;
    padding:16px 18px!important;
    border-radius:26px!important;
    grid-template-columns:auto minmax(0,1fr) auto!important;
    gap:16px!important;
    box-shadow:0 16px 38px rgba(61,104,145,.09),inset 0 1px 0 rgba(255,255,255,.98)!important;
  }
  #hub .avatar{width:64px!important;height:64px!important;border-radius:20px!important;font-size:22px!important}
  #hub .profileName{font-size:20px!important}
  #hub .profileMeta{font-size:10px!important}
  #hub .socialDot{width:32px!important;height:32px!important;border-radius:11px!important}
  #hub .view[data-view="dashboard"] .dashboard{
    gap:14px!important;
  }
  #hub .view[data-view="dashboard"] .hubMural{
    font-size:clamp(28px,2.2vw,36px)!important;
    padding:10px 12px 8px!important;
  }
  #hub .view[data-view="dashboard"] .folders{
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    grid-template-rows:repeat(3,minmax(0,1fr))!important;
    gap:14px!important;
    align-content:stretch!important;
  }
  #hub .view[data-view="dashboard"] .folder{
    min-height:0!important;
    height:100%!important;
    padding:18px 20px!important;
    border-radius:24px!important;
    border:1px solid rgba(143,181,216,.24)!important;
    box-shadow:0 13px 30px rgba(61,104,145,.08),inset 0 1px 0 rgba(255,255,255,.98)!important;
    column-gap:16px!important;
  }
  #hub .view[data-view="dashboard"] .folderIcon{
    width:56px!important;height:56px!important;border-radius:18px!important;font-size:20px!important;
  }
  #hub .view[data-view="dashboard"] .folder h2{
    font-size:clamp(17px,1.2vw,21px)!important;
    line-height:1.05!important;
  }
  #hub .view[data-view="dashboard"] .folder p{
    font-size:11px!important;
    line-height:1.28!important;
    max-width:44ch!important;
  }
  #hub .view[data-view="dashboard"] .folderArrow{font-size:24px!important}
  #hub .detailCard{padding:16px!important;border-radius:26px!important}
  #hub .profileOverviewGrid{gap:12px!important}
  #hub .profileOverviewCard{min-height:118px!important;padding:16px!important;border-radius:20px!important}
  #hub .profileOverviewValue{font-size:32px!important}
}
/* END V296 VISIBLE INTERNAL PAGES — HUB */
'''

AI_CSS = r'''
/* V296 VISIBLE INTERNAL PAGES — AI */
@media (min-width:761px){
  #ai221{
    padding:18px 24px 18px!important;
  }
  #ai221 .top{margin-bottom:14px!important}
  #ai221 h1{font-size:clamp(30px,2.25vw,38px)!important}
  #ai221 .subtitle{font-size:12px!important}
  #ai221 .titleIcon{width:54px!important;height:54px!important;border-radius:18px!important}
  #ai221 .panel{
    padding:16px!important;
    border-radius:28px!important;
    box-shadow:0 17px 42px rgba(61,104,145,.09),inset 0 1px 0 rgba(255,255,255,.98)!important;
  }
  #ai221 .panel+.panel{margin-top:14px!important}
  #ai221 .panelTitle{font-size:16px!important}
  #ai221 .engines{gap:14px!important}
  #ai221 .engine{
    min-height:204px!important;
    padding:15px!important;
    border-radius:23px!important;
    border:1px solid rgba(125,177,216,.28)!important;
    box-shadow:0 11px 27px rgba(65,105,145,.075),inset 0 1px 0 #fff!important;
  }
  #ai221 .engineIcon{width:50px!important;height:50px!important;font-size:22px!important}
  #ai221 .engine h3{font-size:16px!important;margin:12px 0 6px!important}
  #ai221 .engine p{font-size:10.5px!important;line-height:1.42!important}
  #ai221 .tag{font-size:8px!important;padding:5px 7px!important}
  #ai221 .selectBtn{min-height:40px!important;font-size:9.5px!important;border-radius:13px!important}
  #ai221 .create{min-height:50px!important;padding:13px 22px!important;font-size:12px!important;border-radius:16px!important}
  #ai221 .moments{gap:13px!important}
  #ai221 .moment{min-height:124px!important;padding:9px!important;border-radius:20px!important}
  #ai221 .thumb{height:86px!important;border-radius:15px!important}
  #ai221 .moment b{font-size:10px!important;margin-top:8px!important}
}
/* END V296 VISIBLE INTERNAL PAGES — AI */
'''

EDITOR_CSS = r'''
/* V296 VISIBLE INTERNAL PAGES — EDITOR */
@media (min-width:761px){
  #ng27 .shell{
    max-width:1540px!important;
    padding:10px 18px!important;
    border-radius:26px!important;
  }
  #ng27 .cockpit{
    grid-template-columns:96px minmax(0,1fr) 96px!important;
    gap:18px!important;
  }
  #ng27 .rail{gap:10px!important}
  #ng27 .railBtn{
    width:82px!important;height:82px!important;
    border-radius:24px!important;
    box-shadow:0 10px 24px rgba(91,126,170,.14)!important;
  }
  #ng27 .railBtn .ico{width:29px!important;height:29px!important}
  #ng27 .railBtn span{font-size:9px!important;letter-spacing:.06em!important}
  #ng27 .stage.r916{
    width:min(100%,390px)!important;
    border-radius:26px!important;
  }
  #ng27 .timeline{width:min(96%,900px)!important}
  #ng27 .zoomEditorBtn{height:34px!important;padding:0 11px!important;font-size:8px!important}
  #ng27 .createShortJourney{width:min(100%,620px)!important;margin:10px auto 4px!important}
  #ng27 .createShortJourneyBtn{
    min-height:56px!important;
    border-radius:18px!important;
    font-size:12px!important;
  }
}
@media (min-width:761px) and (max-height:820px){
  #ng27 .stage.r916{width:min(100%,330px)!important}
  #ng27 .railBtn{width:70px!important;height:70px!important}
  #ng27 .cockpit{grid-template-columns:82px minmax(0,1fr) 82px!important;gap:12px!important}
}
/* END V296 VISIBLE INTERNAL PAGES — EDITOR */
'''

SHARE_CSS = r'''
/* V296 VISIBLE INTERNAL PAGES — SHARE */
@media (min-width:761px){
  #share.gsfFinalSurface{
    padding:20px 28px 22px!important;
  }
  #share.gsfFinalSurface .topline{margin-bottom:17px!important}
  #share.gsfFinalSurface h1{font-size:clamp(30px,2.25vw,38px)!important}
  #share.gsfFinalSurface .subtitle{font-size:12px!important}
  #share.gsfFinalSurface .titleIcon{width:56px!important;height:56px!important;border-radius:19px!important}
  #share.gsfFinalSurface .section{padding:18px!important;border-radius:29px!important}
  #share.gsfFinalSurface .sectionTitle{font-size:16px!important}
  #share.gsfFinalSurface .socials{
    grid-template-columns:repeat(4,minmax(0,1fr))!important;
    gap:14px!important;
  }
  #share.gsfFinalSurface .card{
    min-height:216px!important;
    padding:16px!important;
    border-radius:24px!important;
    border:1px solid rgba(125,177,216,.27)!important;
    box-shadow:0 12px 30px rgba(65,105,145,.08),inset 0 1px 0 #fff!important;
  }
  #share.gsfFinalSurface .logo{width:54px!important;height:54px!important;border-radius:17px!important}
  #share.gsfFinalSurface .logo svg{width:29px!important;height:29px!important}
  #share.gsfFinalSurface .card h3{font-size:17px!important;margin:12px 0 5px!important}
  #share.gsfFinalSurface .card p{font-size:10.5px!important;line-height:1.38!important}
  #share.gsfFinalSurface .open{min-height:44px!important;font-size:10px!important;border-radius:14px!important}
  #share.gsfFinalSurface .downloadTitle h2{font-size:20px!important}
  #share.gsfFinalSurface .downloadTitle p{font-size:10.5px!important}
  #share.gsfFinalSurface .downloadBtn{min-height:54px!important;padding:14px 24px!important;font-size:12px!important}
  #share.gsfFinalSurface .secondary{min-height:46px!important;font-size:10px!important}
}
/* END V296 VISIBLE INTERNAL PAGES — SHARE */
'''


def inject_css(path: Path, marker: str, css: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print("V296 CSS already present:", path, flush=True)
        return
    if "</style>" not in text:
        raise RuntimeError("V296 style anchor missing: " + str(path))
    text = text.replace("</style>", css + "\n</style>", 1)
    path.write_text(text, encoding="utf-8")
    print("V296 visible CSS applied:", path, flush=True)


def patch_shell_cache() -> None:
    if not APP.is_file():
        raise RuntimeError("V296 structural shell missing: " + str(APP))
    text = APP.read_text(encoding="utf-8")
    before = text
    for route in ("creator-hub-v156", "share-v156", "ai-v221"):
        text = re.sub(rf"/{re.escape(route)}/\?v=\d+", f"/{route}/?v=296", text)
    required = (
        "/creator-hub-v156/?v=296",
        "/share-v156/?v=296",
        "/ai-v221/?v=296",
    )
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError("V296 shell cache markers missing: " + ", ".join(missing))
    APP.write_text(text, encoding="utf-8")
    print("V296 shell cache bumped: changed=", text != before, flush=True)


def patch_editor_asset_key() -> None:
    if not EDITOR_EMBED.is_file():
        raise RuntimeError("V296 editor embed missing: " + str(EDITOR_EMBED))
    text = EDITOR_EMBED.read_text(encoding="utf-8")
    before = text
    text, count = re.subn(r'"gsf_editor_2027_v\d+"', '"gsf_editor_2027_v296"', text, count=1)
    if count != 1 and '"gsf_editor_2027_v296"' not in text:
        raise RuntimeError("V296 editor component key anchor missing")
    EDITOR_EMBED.write_text(text, encoding="utf-8")
    print("V296 editor asset key bumped: changed=", text != before, flush=True)


if __name__ == "__main__":
    for path in (HUB, AI, EDITOR, SHARE):
        if not path.is_file():
            raise RuntimeError("V296 required component missing: " + str(path))
    inject_css(HUB, "/* V296 VISIBLE INTERNAL PAGES — HUB */", HUB_CSS)
    inject_css(AI, "/* V296 VISIBLE INTERNAL PAGES — AI */", AI_CSS)
    inject_css(EDITOR, "/* V296 VISIBLE INTERNAL PAGES — EDITOR */", EDITOR_CSS)
    inject_css(SHARE, "/* V296 VISIBLE INTERNAL PAGES — SHARE */", SHARE_CSS)
    patch_shell_cache()
    patch_editor_asset_key()
