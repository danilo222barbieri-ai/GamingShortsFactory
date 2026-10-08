#!/usr/bin/env python3
from pathlib import Path
import re
import sys

STYLE_ID='v322MobileHubLiveFill'
STYLE=r'''<style id="v322MobileHubLiveFill">
/* V322: final mobile Hub + Live vertical distribution. No DOM/routing changes. */
@media(max-width:767px){
  /* Dashboard: profile + three folders + ad consume the complete work area. */
  #hub .view[data-view="dashboard"] .dashboard{
    height:100%!important;
    min-height:0!important;
    overflow:hidden!important;
    grid-template-rows:136px minmax(0,1fr) clamp(168px,21vh,198px)!important;
    gap:8px!important;
    align-content:stretch!important;
  }
  #hub .view[data-view="dashboard"] .profileCard{
    height:136px!important;
    min-height:136px!important;
    margin:0!important;
  }
  #hub .view[data-view="dashboard"] .folders{
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    margin:0!important;
    display:grid!important;
    grid-template-columns:1fr!important;
    grid-template-rows:repeat(3,minmax(0,1fr))!important;
    gap:8px!important;
    align-content:stretch!important;
  }
  #hub .view[data-view="dashboard"] .folder{
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    margin:0!important;
    box-sizing:border-box!important;
  }
  #hub .view[data-view="dashboard"] .hubDashboardAd{
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    max-height:none!important;
    margin:0!important;
    align-self:stretch!important;
    border-radius:23px!important;
  }

  /* Live: compact guide, then two equal provider blocks down to Game Bar. */
  #hub .view[data-view="live"],
  #hub .view[data-view="live"] .detail,
  #hub .view[data-view="live"] .detailCard{
    height:100%!important;
    min-height:0!important;
    overflow:hidden!important;
  }
  #hub .view[data-view="live"] .folderScroller{
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    box-sizing:border-box!important;
    overflow:hidden!important;
    padding:0 2px 82px!important;
    display:grid!important;
    grid-template-rows:32px repeat(2,minmax(0,1fr))!important;
    gap:9px!important;
    align-content:stretch!important;
  }
  #hub .view[data-view="live"] .hubLiveGuide{
    width:100%!important;
    height:32px!important;
    min-height:32px!important;
    margin:0!important;
    padding:5px 10px!important;
    display:flex!important;
    align-items:center!important;
    border-radius:14px!important;
    font-size:10px!important;
    line-height:1.08!important;
  }
  #hub .view[data-view="live"] .livePlatformCard{
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    max-height:none!important;
    margin:0!important;
    padding:9px 10px!important;
    align-self:stretch!important;
    display:grid!important;
    grid-template-rows:44px minmax(0,1fr)!important;
    gap:7px!important;
    overflow:hidden!important;
    border-radius:21px!important;
  }
  #hub .view[data-view="live"] .livePlatformHead{
    height:44px!important;
    min-height:44px!important;
    margin:0!important;
    grid-template-columns:38px minmax(0,1fr)!important;
    gap:9px!important;
    align-items:center!important;
  }
  #hub .view[data-view="live"] .livePlatformIcon{
    width:38px!important;
    height:38px!important;
    border-radius:12px!important;
    font-size:16px!important;
  }
  #hub .view[data-view="live"] .livePaneTitle{
    font-size:18px!important;
    line-height:1!important;
  }
  #hub .view[data-view="live"] .livePlatformSubtitle{
    margin-top:2px!important;
    font-size:8.8px!important;
    line-height:1.08!important;
  }
  #hub .view[data-view="live"] .liveMiniFolders{
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    display:grid!important;
    grid-template-rows:repeat(3,minmax(0,1fr))!important;
    gap:7px!important;
    align-content:stretch!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder{
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    max-height:none!important;
    margin:0!important;
    padding:5px 9px!important;
    grid-template-columns:32px minmax(0,1fr) auto!important;
    gap:8px!important;
    align-items:center!important;
    border-radius:14px!important;
    box-sizing:border-box!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder>span{
    width:32px!important;
    height:32px!important;
    border-radius:10px!important;
    font-size:13px!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder b{
    font-size:12.5px!important;
    line-height:1.02!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder small{
    margin-top:2px!important;
    font-size:8.3px!important;
    line-height:1.05!important;
  }
}

@media(max-width:767px) and (max-height:760px){
  #hub .view[data-view="dashboard"] .dashboard{
    grid-template-rows:126px minmax(0,1fr) 126px!important;
    gap:6px!important;
  }
  #hub .view[data-view="dashboard"] .profileCard{
    height:126px!important;
    min-height:126px!important;
  }
  #hub .view[data-view="dashboard"] .folders{gap:6px!important}
  #hub .view[data-view="dashboard"] .hubDashboardAd{border-radius:19px!important}

  #hub .view[data-view="live"] .folderScroller{
    padding:0 2px 74px!important;
    grid-template-rows:28px repeat(2,minmax(0,1fr))!important;
    gap:6px!important;
  }
  #hub .view[data-view="live"] .hubLiveGuide{
    height:28px!important;
    min-height:28px!important;
    padding:3px 8px!important;
    font-size:8.8px!important;
    border-radius:12px!important;
  }
  #hub .view[data-view="live"] .livePlatformCard{
    padding:6px 8px!important;
    grid-template-rows:38px minmax(0,1fr)!important;
    gap:5px!important;
    border-radius:18px!important;
  }
  #hub .view[data-view="live"] .livePlatformHead{
    height:38px!important;
    min-height:38px!important;
    grid-template-columns:32px minmax(0,1fr)!important;
    gap:7px!important;
  }
  #hub .view[data-view="live"] .livePlatformIcon{
    width:32px!important;
    height:32px!important;
    border-radius:10px!important;
    font-size:14px!important;
  }
  #hub .view[data-view="live"] .livePaneTitle{font-size:16px!important}
  #hub .view[data-view="live"] .livePlatformSubtitle{font-size:7.8px!important}
  #hub .view[data-view="live"] .liveMiniFolders{gap:5px!important}
  #hub .view[data-view="live"] .liveMiniFolder{
    padding:3px 7px!important;
    grid-template-columns:28px minmax(0,1fr) auto!important;
    gap:6px!important;
    border-radius:12px!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder>span{
    width:28px!important;
    height:28px!important;
    border-radius:9px!important;
    font-size:12px!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder b{font-size:11.3px!important}
  #hub .view[data-view="live"] .liveMiniFolder small{font-size:7.5px!important}
}
</style>'''

def patch_text(text:str)->str:
    for marker in (
        'id="v318HubFillLiveFit"',
        'id="v321LiveMobileBalance"',
        'id="hubDashboardAd"',
        'data-folder="profile"',
        'data-folder="projects"',
        'data-folder="live"',
        'livePlatformTwitch',
        'livePlatformYoutube',
        'hubLiveGuide',
    ):
        if marker not in text:
            raise RuntimeError('V322 missing runtime Hub/Live anchor: '+marker)
    # Always remove/reinsert the final style. V316 rewrites its own CSS on every
    # process start, so this guarantees V322 remains the last mobile authority
    # after Railway restarts as well as on the first boot.
    out=re.sub(r'<style id="'+re.escape(STYLE_ID)+r'">.*?</style>\n?','',text,count=1,flags=re.DOTALL)
    if '</head>' not in out:
        raise RuntimeError('V322 Hub </head> anchor missing')
    return out.replace('</head>',STYLE+'\n</head>',1)

def main()->None:
    path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not path.is_file():
        raise SystemExit('V322 Hub target missing: '+str(path))
    before=path.read_text(encoding='utf-8')
    after=patch_text(before)
    path.write_text(after,encoding='utf-8')
    print('V322 mobile Hub + Live full-height layout applied changed=',before!=after,flush=True)

if __name__=='__main__':
    main()
