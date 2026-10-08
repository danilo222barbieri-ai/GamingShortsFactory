#!/usr/bin/env python3
from pathlib import Path
import re
import sys

STYLE_ID='v318HubFillLiveFit'
STYLE=r'''<style id="v318HubFillLiveFit">
/* V318: fill Creator Hub dashboard and keep Live fully inside the mobile viewport. */
@media(max-width:767px){
  #hub .view[data-view="dashboard"] .dashboard{
    grid-template-rows:136px minmax(0,1fr) clamp(150px,23vh,220px)!important;
    gap:10px!important;
  }
  #hub .view[data-view="dashboard"] .hubDashboardAd{
    height:100%!important;min-height:150px!important;align-self:stretch!important;
    border-radius:24px!important;font-size:11px!important;
  }

  #hub .view[data-view="live"]{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .view[data-view="live"] .detail,
  #hub .view[data-view="live"] .detailCard{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .view[data-view="live"] .folderScroller{
    height:100%!important;min-height:0!important;box-sizing:border-box!important;
    padding:2px 2px 94px!important;overflow:hidden!important;
    display:grid!important;grid-template-rows:34px repeat(2,minmax(0,1fr))!important;
    gap:8px!important;align-content:stretch!important;
  }
  #hub .view[data-view="live"] .hubLiveGuide{
    height:34px!important;min-height:34px!important;margin:0!important;padding:5px 10px!important;
    display:flex!important;align-items:center!important;border-radius:14px!important;
    font-size:10.5px!important;line-height:1.1!important;
  }
  #hub .view[data-view="live"] .livePlatformCard{
    height:100%!important;min-height:0!important;margin:0!important;padding:8px 10px!important;
    display:grid!important;grid-template-rows:46px minmax(0,1fr)!important;gap:6px!important;
    overflow:hidden!important;border-radius:22px!important;
  }
  #hub .view[data-view="live"] .livePlatformHead{
    min-height:0!important;margin:0!important;grid-template-columns:40px minmax(0,1fr)!important;
    gap:9px!important;align-items:center!important;
  }
  #hub .view[data-view="live"] .livePlatformIcon{width:40px!important;height:40px!important;border-radius:13px!important;font-size:17px!important}
  #hub .view[data-view="live"] .livePaneTitle{font-size:19px!important;line-height:1!important}
  #hub .view[data-view="live"] .livePlatformSubtitle{margin-top:2px!important;font-size:9.3px!important;line-height:1.08!important}
  #hub .view[data-view="live"] .liveMiniFolders{
    height:100%!important;min-height:0!important;display:grid!important;
    grid-template-rows:repeat(3,minmax(0,1fr))!important;gap:5px!important;align-content:stretch!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder{
    height:100%!important;min-height:0!important;margin:0!important;padding:4px 8px!important;
    grid-template-columns:34px minmax(0,1fr) auto!important;gap:8px!important;border-radius:15px!important;
    align-items:center!important;box-sizing:border-box!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder>span{width:34px!important;height:34px!important;border-radius:11px!important;font-size:14px!important}
  #hub .view[data-view="live"] .liveMiniFolder b{font-size:13.5px!important;line-height:1!important}
  #hub .view[data-view="live"] .liveMiniFolder small{margin-top:2px!important;font-size:9.2px!important;line-height:1.05!important}
  #hub .view[data-view="live"] .liveMiniFolder i{font-size:20px!important}
}
@media(max-width:767px) and (max-height:760px){
  #hub .view[data-view="dashboard"] .dashboard{grid-template-rows:126px minmax(0,1fr) 125px!important;gap:8px!important}
  #hub .view[data-view="dashboard"] .hubDashboardAd{min-height:125px!important;border-radius:19px!important;font-size:9.5px!important}
  #hub .view[data-view="live"] .folderScroller{padding-bottom:86px!important;grid-template-rows:30px repeat(2,minmax(0,1fr))!important;gap:6px!important}
  #hub .view[data-view="live"] .hubLiveGuide{height:30px!important;min-height:30px!important;font-size:9.5px!important;padding:4px 8px!important}
  #hub .view[data-view="live"] .livePlatformCard{grid-template-rows:40px minmax(0,1fr)!important;padding:6px 8px!important;gap:4px!important;border-radius:19px!important}
  #hub .view[data-view="live"] .livePlatformHead{grid-template-columns:34px minmax(0,1fr)!important;gap:7px!important}
  #hub .view[data-view="live"] .livePlatformIcon{width:34px!important;height:34px!important;border-radius:11px!important;font-size:15px!important}
  #hub .view[data-view="live"] .livePaneTitle{font-size:17px!important}
  #hub .view[data-view="live"] .livePlatformSubtitle{font-size:8.5px!important}
  #hub .view[data-view="live"] .liveMiniFolders{gap:4px!important}
  #hub .view[data-view="live"] .liveMiniFolder{grid-template-columns:30px minmax(0,1fr) auto!important;gap:6px!important;padding:3px 7px!important;border-radius:13px!important}
  #hub .view[data-view="live"] .liveMiniFolder>span{width:30px!important;height:30px!important;border-radius:10px!important;font-size:12px!important}
  #hub .view[data-view="live"] .liveMiniFolder b{font-size:12px!important}
  #hub .view[data-view="live"] .liveMiniFolder small{font-size:8px!important}
}
</style>'''

def patch_text(text:str)->str:
    for marker in ('id="hubDashboardAd"','hubLiveGuide','livePlatformTwitch','livePlatformYoutube'):
        if marker not in text: raise RuntimeError('V318 missing Hub anchor: '+marker)
    cleaned=re.sub(r'\s*<style id="'+re.escape(STYLE_ID)+r'">.*?</style>\s*','\n',text,flags=re.DOTALL)
    if '</head>' not in cleaned: raise RuntimeError('V318 Hub </head> anchor missing')
    return cleaned.replace('</head>','\n'+STYLE+'\n</head>',1)

def main()->None:
    hub=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not hub.is_file(): raise SystemExit('V318 Hub missing: '+str(hub))
    before=hub.read_text(encoding='utf-8');after=patch_text(before);hub.write_text(after,encoding='utf-8')
    print('V318 Hub fill + Live viewport fit applied changed=',before!=after,flush=True)

if __name__=='__main__': main()
