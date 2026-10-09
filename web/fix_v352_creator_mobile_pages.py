#!/usr/bin/env python3
from pathlib import Path
import re
import sys

STYLE_ID='v352CreatorMobilePages'
STYLE=r'''<style id="v352CreatorMobilePages">
/* V352: mobile Creator Hub internal pages use breathing room + internal scrolling. */
@media(max-width:767px){
  #hub .view[data-view="projects"],
  #hub .view[data-view="live"]{
    height:100%!important;
    min-height:0!important;
    overflow:hidden!important;
  }

  #hub .view[data-view="projects"] .detail,
  #hub .view[data-view="live"] .detail{
    height:100%!important;
    min-height:0!important;
    display:grid!important;
    grid-template-rows:auto minmax(0,1fr)!important;
    gap:10px!important;
    padding-top:8px!important;
    box-sizing:border-box!important;
  }

  #hub .view[data-view="projects"] .detailHead,
  #hub .view[data-view="live"] .detailHead{
    display:flex!important;
    min-height:64px!important;
    padding:7px 12px 5px!important;
    align-items:flex-start!important;
    box-sizing:border-box!important;
  }
  #hub .view[data-view="projects"] .detailHeadText,
  #hub .view[data-view="live"] .detailHeadText{
    min-width:0!important;
    width:100%!important;
  }
  #hub .view[data-view="projects"] .detailHeadText h2,
  #hub .view[data-view="live"] .detailHeadText h2{
    margin:0!important;
    font-size:24px!important;
    line-height:1.04!important;
    letter-spacing:-.03em!important;
    font-weight:950!important;
  }
  #hub .view[data-view="projects"] .detailHeadText p,
  #hub .view[data-view="live"] .detailHeadText p{
    margin:6px 0 0!important;
    max-width:92%!important;
    font-size:12px!important;
    line-height:1.28!important;
    font-weight:720!important;
    color:#7185a6!important;
    white-space:normal!important;
    overflow:visible!important;
    text-overflow:clip!important;
  }

  #hub .view[data-view="projects"] .detailCard,
  #hub .view[data-view="live"] .detailCard{
    height:100%!important;
    min-height:0!important;
    overflow:hidden!important;
  }

  /* Projects: heading stays readable; content scrolls inside the page. */
  #hub .view[data-view="projects"] .folderScroller{
    height:100%!important;
    min-height:0!important;
    overflow-y:auto!important;
    overflow-x:hidden!important;
    -webkit-overflow-scrolling:touch!important;
    overscroll-behavior-y:contain!important;
    padding:2px 2px 96px!important;
    display:block!important;
  }
  #hub .view[data-view="projects"] .hubProjectsGuide{
    margin:0 0 12px!important;
    padding:10px 12px!important;
    border-radius:16px!important;
    font-size:11.5px!important;
    line-height:1.28!important;
  }
  #hub .view[data-view="projects"] #projectHubCards{
    gap:12px!important;
    margin:0 0 14px!important;
  }
  #hub .view[data-view="projects"] .projectHubCard{
    min-height:122px!important;
    padding:16px!important;
    border-radius:24px!important;
  }
  #hub .view[data-view="projects"] .projectHubCard b{font-size:20px!important;line-height:1.08!important}
  #hub .view[data-view="projects"] .projectHubCard small{font-size:11.5px!important;line-height:1.28!important}

  /* Live: stop forcing both providers into one compressed fixed-height grid. */
  #hub .view[data-view="live"] .folderScroller{
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    overflow-y:auto!important;
    overflow-x:hidden!important;
    -webkit-overflow-scrolling:touch!important;
    overscroll-behavior-y:contain!important;
    padding:2px 2px 100px!important;
    display:block!important;
  }
  #hub .view[data-view="live"] .hubLiveGuide{
    width:100%!important;
    height:auto!important;
    min-height:0!important;
    margin:0 0 12px!important;
    padding:10px 12px!important;
    display:flex!important;
    align-items:center!important;
    border-radius:16px!important;
    font-size:11.5px!important;
    line-height:1.28!important;
  }
  #hub .view[data-view="live"] .livePlatformCard{
    width:100%!important;
    height:auto!important;
    min-height:0!important;
    max-height:none!important;
    margin:0 0 14px!important;
    padding:14px!important;
    display:grid!important;
    grid-template-rows:auto auto!important;
    gap:11px!important;
    overflow:visible!important;
    border-radius:25px!important;
  }
  #hub .view[data-view="live"] .livePlatformCard:last-child{margin-bottom:0!important}
  #hub .view[data-view="live"] .livePlatformHead{
    height:auto!important;
    min-height:52px!important;
    margin:0!important;
    grid-template-columns:52px minmax(0,1fr)!important;
    gap:12px!important;
    align-items:center!important;
  }
  #hub .view[data-view="live"] .livePlatformIcon{
    width:52px!important;
    height:52px!important;
    border-radius:17px!important;
    font-size:21px!important;
  }
  #hub .view[data-view="live"] .livePaneTitle{
    margin:0!important;
    font-size:21px!important;
    line-height:1.04!important;
    letter-spacing:-.025em!important;
  }
  #hub .view[data-view="live"] .livePlatformSubtitle{
    margin-top:4px!important;
    font-size:11px!important;
    line-height:1.24!important;
  }
  #hub .view[data-view="live"] .liveMiniFolders{
    width:100%!important;
    height:auto!important;
    min-height:0!important;
    display:grid!important;
    grid-template-rows:none!important;
    grid-auto-rows:auto!important;
    gap:8px!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder{
    width:100%!important;
    height:auto!important;
    min-height:68px!important;
    max-height:none!important;
    margin:0!important;
    padding:10px 11px!important;
    grid-template-columns:44px minmax(0,1fr) auto!important;
    gap:10px!important;
    align-items:center!important;
    border-radius:18px!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder>span{
    width:44px!important;
    height:44px!important;
    border-radius:14px!important;
    font-size:17px!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder b{
    font-size:14.5px!important;
    line-height:1.06!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder small{
    margin-top:3px!important;
    font-size:10.3px!important;
    line-height:1.18!important;
  }
}

@media(max-width:390px){
  #hub .view[data-view="projects"] .detail,
  #hub .view[data-view="live"] .detail{padding-top:6px!important;gap:8px!important}
  #hub .view[data-view="projects"] .detailHead,
  #hub .view[data-view="live"] .detailHead{min-height:60px!important;padding:6px 9px 4px!important}
  #hub .view[data-view="projects"] .detailHeadText h2,
  #hub .view[data-view="live"] .detailHeadText h2{font-size:22px!important}
  #hub .view[data-view="projects"] .detailHeadText p,
  #hub .view[data-view="live"] .detailHeadText p{font-size:11px!important;margin-top:5px!important;max-width:96%!important}
  #hub .view[data-view="live"] .livePlatformCard{padding:12px!important;border-radius:22px!important}
  #hub .view[data-view="live"] .livePlatformHead{grid-template-columns:48px minmax(0,1fr)!important;gap:10px!important}
  #hub .view[data-view="live"] .livePlatformIcon{width:48px!important;height:48px!important;border-radius:16px!important}
  #hub .view[data-view="live"] .livePaneTitle{font-size:20px!important}
  #hub .view[data-view="live"] .liveMiniFolder{min-height:66px!important;padding:9px 10px!important;grid-template-columns:42px minmax(0,1fr) auto!important}
  #hub .view[data-view="live"] .liveMiniFolder>span{width:42px!important;height:42px!important}
}
</style>'''

def patch_text(text:str)->str:
    for marker in ('id="projectHubCards"','hubProjectsGuide','hubLiveGuide','livePlatformTwitch','livePlatformYoutube'):
        if marker not in text:
            raise RuntimeError('V352 missing Creator Hub anchor: '+marker)
    out=re.sub(r'<style id="'+re.escape(STYLE_ID)+r'">.*?</style>\n?','',text,count=1,flags=re.DOTALL)
    if '</head>' not in out:
        raise RuntimeError('V352 Creator Hub </head> anchor missing')
    return out.replace('</head>',STYLE+'\n</head>',1)

def main()->None:
    path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not path.is_file():
        raise SystemExit('V352 Creator Hub target missing: '+str(path))
    before=path.read_text(encoding='utf-8')
    after=patch_text(before)
    path.write_text(after,encoding='utf-8')
    print('V352 Creator Hub mobile pages applied changed=',before!=after,flush=True)

if __name__=='__main__':
    main()
