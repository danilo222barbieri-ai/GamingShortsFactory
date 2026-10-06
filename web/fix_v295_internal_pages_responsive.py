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
/* V295 INTERNAL PAGE SYSTEM — HUB */
#hub{
  --gsf-page-pad:clamp(10px,1.2vw,18px);
  --gsf-card-radius:22px;
}
#hub .closeTop{display:none!important}
#hub .profileOverviewCard,
#hub .profileOverviewAction,
#hub .folder,
#hub .socialCard,
#hub .liveFolder,
#hub .liveMiniFolder,
#hub .row,
#hub .planRow{
  -webkit-tap-highlight-color:transparent;
  touch-action:manipulation;
}
#hub .profileOverviewCard:active,
#hub .profileOverviewAction:active,
#hub .folder:active,
#hub .socialCard:active,
#hub .liveFolder:active,
#hub .liveMiniFolder:active{transform:scale(.99)!important}

@media (min-width:761px){
  #hub{padding:clamp(12px,1.45vh,16px) clamp(16px,1.55vw,24px) clamp(10px,1.25vh,14px)!important}
  #hub .top{min-height:52px!important}
  #hub .stage{min-height:0!important}
  #hub .detail{height:100%!important;min-height:0!important}
  #hub .detailCard{height:100%!important;min-height:0!important;border-radius:24px!important}
  #hub .profileOverviewGrid{grid-template-columns:repeat(4,minmax(0,1fr))!important}
  #hub .socialGrid,#hub .profileSocialGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  #hub .view[data-view="dashboard"] .folders{grid-template-rows:repeat(5,minmax(0,1fr))!important}
}

@media (max-width:760px){
  #hub{
    width:100%!important;
    height:100dvh!important;
    min-height:0!important;
    overflow:hidden!important;
    padding:max(7px,env(safe-area-inset-top)) 7px max(7px,env(safe-area-inset-bottom))!important;
    gap:6px!important;
  }
  #hub .top{min-height:48px!important;padding:0 2px!important}
  #hub .titleIcon{width:42px!important;height:42px!important;border-radius:14px!important}
  #hub h1{font-size:21px!important}
  #hub .subtitle{font-size:10px!important;max-width:72vw!important}
  #hub .stage{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .view{min-height:0!important}
  #hub .view.active{height:100%!important}
  #hub .dashboard{height:100%!important;min-height:0!important}
  #hub .profileCard{
    min-height:82px!important;
    padding:7px 6px!important;
    border-radius:18px!important;
  }
  #hub .avatar{width:46px!important;height:46px!important;border-radius:15px!important}
  #hub .profileSocials{gap:4px!important}
  #hub .socialDot{width:27px!important;height:27px!important;min-width:27px!important;min-height:27px!important}
  #hub .view[data-view="dashboard"] .dashboard{
    grid-template-rows:auto auto minmax(0,1fr)!important;
    gap:7px!important;
  }
  #hub .view[data-view="dashboard"] .hubMural{
    margin:0!important;
    padding:3px 4px 5px!important;
    font-size:clamp(20px,5.5vw,24px)!important;
  }
  #hub .view[data-view="dashboard"] .folders{
    height:100%!important;
    min-height:0!important;
    grid-template-columns:1fr!important;
    grid-template-rows:repeat(5,minmax(0,1fr))!important;
    border-radius:21px!important;
  }
  #hub .view[data-view="dashboard"] .folder,
  #hub .view[data-view="dashboard"] .folder[data-folder="profile"],
  #hub .view[data-view="dashboard"] .folder[data-folder="projects"],
  #hub .view[data-view="dashboard"] .folder[data-folder="live"],
  #hub .view[data-view="dashboard"] .folder[data-folder="social"],
  #hub .view[data-view="dashboard"] .folder[data-folder="subscription"]{
    min-height:0!important;
    padding:8px 11px!important;
    column-gap:11px!important;
  }
  #hub .view[data-view="dashboard"] .folderIcon{
    width:42px!important;height:42px!important;border-radius:14px!important;font-size:16px!important;
  }
  #hub .view[data-view="dashboard"] .folder h2{
    font-size:clamp(16px,4.6vw,19px)!important;line-height:1.02!important;
  }
  #hub .view[data-view="dashboard"] .folder p{
    font-size:clamp(9.5px,2.65vw,11px)!important;line-height:1.17!important;
  }
  #hub .view[data-view="dashboard"] .folderArrow{font-size:22px!important}

  #hub .detail{
    height:100%!important;
    min-height:0!important;
    grid-template-rows:auto minmax(0,1fr)!important;
    gap:6px!important;
  }
  #hub .detailHead{min-height:38px!important;padding:0 4px!important}
  #hub .detailCard{
    height:100%!important;
    min-height:0!important;
    padding:8px!important;
    border-radius:19px!important;
    overflow:hidden!important;
  }
  #hub .folderScroller,
  #hub .profileOnlyScroller,
  #hub .socialFolderScroller,
  #hub .subscriptionScroller{
    height:100%!important;
    min-height:0!important;
    overflow:auto!important;
    overscroll-behavior:contain!important;
    -webkit-overflow-scrolling:touch!important;
  }
  #hub .profileOnlyMural,
  #hub .socialFolderMural,
  #hub .subscriptionMural{
    margin:8px 0 6px!important;
    font-size:clamp(18px,5.1vw,22px)!important;
  }
  #hub .profileOverviewGrid{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;
    margin-top:7px!important;
  }
  #hub .profileOverviewCard{
    min-height:92px!important;
    padding:12px!important;
    border-radius:17px!important;
  }
  #hub .profileOverviewValue{font-size:26px!important}
  #hub .profileOverviewActions{
    grid-template-columns:1fr!important;
    gap:7px!important;
    margin-top:8px!important;
  }
  #hub .profileOverviewAction{min-height:48px!important;border-radius:15px!important}
  #hub .socialGrid,#hub .profileSocialGrid{grid-template-columns:1fr!important;gap:7px!important}
  #hub .socialCard{min-height:58px!important;border-radius:15px!important}
  #hub .projectBox{border-radius:15px!important}
  #hub .row{min-height:48px!important;border-radius:14px!important}
  #hub .liveFolder,#hub .liveMiniFolder{min-height:52px!important}
}
/* END V295 INTERNAL PAGE SYSTEM — HUB */
'''

AI_CSS = r'''
/* V295 INTERNAL PAGE SYSTEM — AI */
#ai221{
  --gsf-page-blue:#53A9F3;
  --gsf-page-line:rgba(143,181,216,.23);
}
#ai221 .engine,
#ai221 .moment,
#ai221 .duration button,
#ai221 .create,
#ai221 .momentAction{
  -webkit-tap-highlight-color:transparent;
  touch-action:manipulation;
}

@media (min-width:761px){
  #ai221{
    height:100dvh!important;
    overflow:auto!important;
    padding:clamp(12px,1.5vh,16px) clamp(16px,1.6vw,22px) clamp(14px,1.6vh,18px)!important;
  }
  #ai221 .engines{grid-template-columns:repeat(4,minmax(0,1fr))!important}
  #ai221 .moments{grid-template-columns:repeat(3,minmax(0,1fr))!important}
  #ai221 .momentActionGrid{grid-template-columns:1fr 1fr!important}
}

@media (max-width:760px){
  #ai221{
    width:100%!important;
    height:100dvh!important;
    min-height:0!important;
    overflow:auto!important;
    overscroll-behavior:contain!important;
    -webkit-overflow-scrolling:touch!important;
    padding:max(8px,env(safe-area-inset-top)) 7px max(82px,calc(env(safe-area-inset-bottom) + 70px))!important;
    background:
      radial-gradient(circle at 9% 6%,rgba(126,214,255,.16),transparent 24%),
      radial-gradient(circle at 91% 8%,rgba(127,236,197,.14),transparent 25%),
      linear-gradient(180deg,#FEFFFF 0%,#FBFDFF 54%,#F7FCFF 100%)!important;
  }
  #ai221 .top{
    align-items:center!important;
    gap:8px!important;
    margin:0 1px 7px!important;
  }
  #ai221 .title{gap:9px!important;min-width:0!important}
  #ai221 .titleIcon{width:42px!important;height:42px!important;border-radius:14px!important;flex:0 0 auto!important}
  #ai221 h1{font-size:21px!important}
  #ai221 .subtitle{font-size:10px!important;line-height:1.2!important;max-width:220px!important}
  #ai221 .duration{padding:4px!important;border-radius:14px!important;flex:0 0 auto!important}
  #ai221 .duration button{min-height:36px!important;padding:7px 9px!important;font-size:9.5px!important}
  #ai221 .journeySteps{
    grid-template-columns:repeat(5,minmax(0,1fr))!important;
    gap:3px!important;
    margin:0 1px 7px!important;
    padding:4px!important;
    border-radius:14px!important;
  }
  #ai221 .journeyStep{padding:6px 2px!important;font-size:7.2px!important;overflow:hidden!important;text-overflow:ellipsis!important}
  #ai221 .panel{padding:9px!important;border-radius:20px!important}
  #ai221 .panel+.panel{margin-top:8px!important}
  #ai221 .panelHead{margin-bottom:7px!important}
  #ai221 .panelTitle{font-size:13px!important}
  #ai221 .panelHint{display:none!important}
  #ai221 .engines{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:7px!important;
  }
  #ai221 .engine{
    min-height:150px!important;
    padding:10px!important;
    border-radius:17px!important;
  }
  #ai221 .engineIcon{width:38px!important;height:38px!important;border-radius:50%!important;font-size:17px!important}
  #ai221 .check{width:23px!important;height:23px!important}
  #ai221 .engine h3{font-size:12px!important;margin:8px 0 4px!important}
  #ai221 .engine p{
    display:-webkit-box!important;
    -webkit-line-clamp:2!important;
    -webkit-box-orient:vertical!important;
    overflow:hidden!important;
    font-size:9px!important;
    line-height:1.28!important;
  }
  #ai221 .tags{display:none!important}
  #ai221 .selectBtn{min-height:36px!important;padding:7px!important;font-size:9px!important;border-radius:11px!important}
  #ai221 .actionRow{
    display:grid!important;
    grid-template-columns:1fr!important;
    gap:7px!important;
    margin-top:8px!important;
  }
  #ai221 .status{font-size:9.5px!important;line-height:1.25!important}
  #ai221 .create{
    width:100%!important;
    min-height:46px!important;
    padding:11px 14px!important;
    border-radius:15px!important;
    font-size:10.5px!important;
  }
  #ai221 .moments{
    grid-template-columns:repeat(3,minmax(0,1fr))!important;
    gap:6px!important;
  }
  #ai221 .moment{
    min-height:94px!important;
    padding:5px!important;
    border-radius:15px!important;
  }
  #ai221 .thumb{height:62px!important;border-radius:12px!important}
  #ai221 .moment b{font-size:8.6px!important;margin:5px 1px 0!important}
  #ai221 .momentNextActions{padding:9px!important;border-radius:17px!important}
  #ai221 .momentChoiceTitle{font-size:10.5px!important}
  #ai221 .momentActionGrid{grid-template-columns:1fr!important;gap:7px!important}
  #ai221 .momentAction{min-height:46px!important;font-size:10px!important}
}
/* END V295 INTERNAL PAGE SYSTEM — AI */
'''

EDITOR_CSS = r'''
/* V295 INTERNAL PAGE SYSTEM — EDITOR */
#ng27 .railBtn,
#ng27 .pill,
#ng27 .zoomEditorBtn,
#ng27 .createShortJourneyBtn{
  -webkit-tap-highlight-color:transparent;
  touch-action:manipulation;
}

@media (min-width:761px){
  #ng27{
    height:100dvh!important;
    min-height:600px!important;
    overflow:hidden!important;
  }
  #ng27 .shell{height:100%!important;max-width:1440px!important}
  #ng27 .cockpit{min-height:0!important}
  #ng27 .createShortJourney{width:min(100%,520px)!important;margin:7px auto 3px!important}
}

@media (max-width:760px){
  #ng27{
    width:100%!important;
    height:100dvh!important;
    min-height:0!important;
    max-height:none!important;
    overflow:hidden!important;
    padding:max(5px,env(safe-area-inset-top)) max(5px,env(safe-area-inset-right)) max(5px,env(safe-area-inset-bottom)) max(5px,env(safe-area-inset-left))!important;
    border-radius:0!important;
    background:
      radial-gradient(circle at 50% 10%,rgba(205,235,249,.86),transparent 42%),
      linear-gradient(180deg,#F9FDFF 0%,#EEF7FC 100%)!important;
  }
  #ng27 .shell{
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    max-width:none!important;
    margin:0 auto!important;
    padding:0!important;
    display:flex!important;
    flex-direction:column!important;
    justify-content:flex-start!important;
    overflow:hidden!important;
  }
  #ng27 .topline{
    position:relative!important;
    top:auto!important;right:auto!important;
    flex:0 0 38px!important;
    min-height:38px!important;
    padding:0 3px 4px!important;
    display:flex!important;
    align-items:center!important;
    justify-content:flex-end!important;
  }
  #ng27 .topline:before{
    content:"GAME EDITOR"!important;
    margin-right:auto!important;
    font-size:10px!important;
    letter-spacing:.18em!important;
    color:#667E9D!important;
  }
  #ng27 .zoomEditorBtn{height:36px!important;min-width:48px!important;border-radius:11px!important}
  #ng27 .cockpit,
  #ng27.expanded .cockpit{
    position:relative!important;
    flex:1 1 auto!important;
    width:100%!important;
    height:auto!important;
    min-height:0!important;
    display:block!important;
    overflow:hidden!important;
  }
  #ng27 .stageWrap{
    position:relative!important;
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    margin:0 auto!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
  }
  #ng27 .stage.r916,
  #ng27.expanded .stage.r916{
    width:min(calc(100vw - 12px),calc((100dvh - 164px) * .5625),350px)!important;
    max-width:350px!important;
    aspect-ratio:9/16!important;
    border-radius:20px!important;
    box-shadow:0 12px 30px rgba(42,77,104,.16)!important;
  }
  #ng27 .cockpit>.rail{
    display:flex!important;
    visibility:visible!important;
    opacity:1!important;
    pointer-events:auto!important;
    position:absolute!important;
    top:50%!important;
    z-index:64!important;
    flex-direction:column!important;
    justify-content:center!important;
    gap:6px!important;
    transform:translateY(-50%)!important;
  }
  #ng27 .cockpit>.rail:first-child{left:max(5px,env(safe-area-inset-left))!important}
  #ng27 .cockpit>.rail:last-child{right:max(5px,env(safe-area-inset-right))!important}
  #ng27 .railBtn,
  #ng27.expanded .railBtn{
    display:flex!important;
    visibility:visible!important;
    opacity:1!important;
    width:48px!important;
    height:48px!important;
    min-width:48px!important;
    min-height:48px!important;
    padding:0!important;
    border-radius:14px!important;
    border:1px solid rgba(185,211,229,.92)!important;
    background:rgba(250,253,255,.88)!important;
    box-shadow:0 6px 17px rgba(48,82,106,.14)!important;
    -webkit-backdrop-filter:blur(14px)!important;
    backdrop-filter:blur(14px)!important;
  }
  #ng27 .railBtn .ico,#ng27.expanded .railBtn .ico{width:19px!important;height:19px!important}
  #ng27 .railBtn span,#ng27.expanded .railBtn span{font-size:8px!important;line-height:1!important;letter-spacing:.025em!important}
  #ng27 .timeline,
  #ng27.expanded .timeline{
    position:absolute!important;
    left:50%!important;
    bottom:7px!important;
    z-index:60!important;
    width:min(calc(100% - 14px),350px)!important;
    margin:0!important;
    padding:6px 7px 7px!important;
    transform:translateX(-50%)!important;
    border-radius:13px!important;
  }
  #ng27 .tlMeta{font-size:7.8px!important;margin-bottom:3px!important}
  #ng27 .track{height:21px!important}
  #ng27 .trimRow{font-size:8px!important;gap:3px!important}
  #ng27 .drawer{
    left:57px!important;right:57px!important;bottom:82px!important;
    z-index:72!important;max-height:46dvh!important;
    overflow:auto!important;border-radius:15px!important;padding:9px!important;
  }
  #ng27 .captionPreview{width:62%!important;font-size:clamp(18px,5.2vw,22px)!important}
  #ng27 .createShortJourney{
    flex:0 0 auto!important;
    width:min(100%,360px)!important;
    margin:5px auto 0!important;
    padding:0 3px!important;
  }
  #ng27 .createShortJourneyBtn{
    width:100%!important;
    min-height:48px!important;
    border-radius:15px!important;
    font-size:10px!important;
  }
  #ng27 .toast{bottom:86px!important}
  #ng27 .footNote{display:none!important}
}
/* END V295 INTERNAL PAGE SYSTEM — EDITOR */
'''

SHARE_CSS = r'''
/* V295 INTERNAL PAGE SYSTEM — SHARE */
#share.gsfFinalSurface .card,
#share.gsfFinalSurface .open,
#share.gsfFinalSurface .downloadBtn,
#share.gsfFinalSurface .secondary{
  -webkit-tap-highlight-color:transparent;
  touch-action:manipulation;
}

@media (min-width:761px){
  #share.gsfFinalSurface{
    height:100dvh!important;
    overflow:auto!important;
    padding:clamp(14px,1.8vh,20px) clamp(18px,2vw,28px) clamp(16px,2vh,22px)!important;
  }
  #share.gsfFinalSurface .socials{grid-template-columns:repeat(4,minmax(0,1fr))!important}
  #share.gsfFinalSurface .downloadRow{grid-template-columns:minmax(260px,1fr) minmax(420px,auto)!important}
}

@media (max-width:760px){
  #share.gsfFinalSurface{
    width:100%!important;
    height:100dvh!important;
    min-height:0!important;
    overflow:auto!important;
    overscroll-behavior:contain!important;
    -webkit-overflow-scrolling:touch!important;
    gap:8px!important;
    padding:max(9px,env(safe-area-inset-top)) 8px max(82px,calc(env(safe-area-inset-bottom) + 70px))!important;
  }
  #share.gsfFinalSurface .topline{margin:0 1px 2px!important}
  #share.gsfFinalSurface .titleIcon{width:43px!important;height:43px!important;border-radius:14px!important}
  #share.gsfFinalSurface h1{font-size:24px!important}
  #share.gsfFinalSurface .subtitle{font-size:10.5px!important;line-height:1.2!important}
  #share.gsfFinalSurface .readyPill{display:none!important}
  #share.gsfFinalSurface .section{padding:10px!important;border-radius:20px!important}
  #share.gsfFinalSurface .sectionHead{margin-bottom:8px!important}
  #share.gsfFinalSurface .socials{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:7px!important;
  }
  #share.gsfFinalSurface .card{
    min-height:154px!important;
    padding:10px!important;
    border-radius:17px!important;
  }
  #share.gsfFinalSurface .logo{width:38px!important;height:38px!important;border-radius:50%!important}
  #share.gsfFinalSurface .card h3{font-size:13px!important;margin:8px 0 3px!important}
  #share.gsfFinalSurface .card p{
    min-height:30px!important;
    font-size:9.4px!important;
    line-height:1.25!important;
    display:-webkit-box!important;
    -webkit-line-clamp:2!important;
    -webkit-box-orient:vertical!important;
    overflow:hidden!important;
  }
  #share.gsfFinalSurface .cardHint{display:none!important}
  #share.gsfFinalSurface .open{min-height:38px!important;font-size:9.5px!important}
  #share.gsfFinalSurface .downloadRow{grid-template-columns:1fr!important;gap:9px!important}
  #share.gsfFinalSurface .downloadTitle h2{font-size:17px!important}
  #share.gsfFinalSurface .downloadTitle p{font-size:10px!important}
  #share.gsfFinalSurface .actions{
    width:100%!important;
    display:grid!important;
    grid-template-columns:1fr 1fr!important;
    gap:7px!important;
  }
  #share.gsfFinalSurface .downloadBtn{
    grid-column:1/-1!important;
    width:100%!important;
    min-height:49px!important;
    font-size:12px!important;
    border-radius:15px!important;
  }
  #share.gsfFinalSurface .secondary{width:100%!important;min-height:40px!important}
  #share.gsfFinalSurface #muralSocial{
    position:relative!important;left:auto!important;top:auto!important;width:100%!important;
    margin:0 0 6px!important;font-size:12px!important;transform:rotate(-2deg)!important;
  }
  #share.gsfFinalSurface #muralAction{display:none!important}
}
@media (max-width:390px){
  #share.gsfFinalSurface .socials{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  #share.gsfFinalSurface .card{min-height:148px!important;padding:9px!important}
  #share.gsfFinalSurface .card p{font-size:9px!important}
}
/* END V295 INTERNAL PAGE SYSTEM — SHARE */
'''


def inject_css(path: Path, marker: str, css: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print("V295 CSS already present:", path, flush=True)
        return
    if "</style>" not in text:
        raise RuntimeError("V295 style anchor missing: " + str(path))
    text = text.replace("</style>", css + "\n</style>", 1)
    path.write_text(text, encoding="utf-8")
    print("V295 CSS applied:", path, flush=True)


def patch_shell_cache() -> None:
    if not APP.is_file():
        raise RuntimeError("V295 structural shell missing: " + str(APP))
    text = APP.read_text(encoding="utf-8")
    before = text
    routes = ("creator-hub-v156", "share-v156", "ai-v221")
    for route in routes:
        text = re.sub(rf"/{re.escape(route)}/\?v=\d+", f"/{route}/?v=295", text)
    required = (
        'data-target="hub" data-section="dashboard"',
        'data-target="hub" data-section="shorts"',
        'data-target="hub" data-section="drafts"',
        "/creator-hub-v156/?v=295",
        "/share-v156/?v=295",
    )
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError("V295 shell/cache markers missing: " + ", ".join(missing))
    APP.write_text(text, encoding="utf-8")
    print("V295 shell cache/routes verified: changed=", text != before, flush=True)


def patch_editor_asset_key() -> None:
    if not EDITOR_EMBED.is_file():
        raise RuntimeError("V295 editor embed missing: " + str(EDITOR_EMBED))
    text = EDITOR_EMBED.read_text(encoding="utf-8")
    before = text
    text, count = re.subn(r'"gsf_editor_2027_v\d+"', '"gsf_editor_2027_v295"', text, count=1)
    if count != 1 and '"gsf_editor_2027_v295"' not in text:
        raise RuntimeError("V295 editor component key anchor missing")
    EDITOR_EMBED.write_text(text, encoding="utf-8")
    print("V295 editor asset key bumped: changed=", text != before, flush=True)


if __name__ == "__main__":
    for path in (HUB, AI, EDITOR, SHARE):
        if not path.is_file():
            raise RuntimeError("V295 required component missing: " + str(path))
    inject_css(HUB, "/* V295 INTERNAL PAGE SYSTEM — HUB */", HUB_CSS)
    inject_css(AI, "/* V295 INTERNAL PAGE SYSTEM — AI */", AI_CSS)
    inject_css(EDITOR, "/* V295 INTERNAL PAGE SYSTEM — EDITOR */", EDITOR_CSS)
    inject_css(SHARE, "/* V295 INTERNAL PAGE SYSTEM — SHARE */", SHARE_CSS)
    patch_shell_cache()
    patch_editor_asset_key()
