#!/usr/bin/env python3
from pathlib import Path
import re
import sys

STYLE_ID='v321LiveMobileBalance'
STYLE=r'''<style id="v321LiveMobileBalance">
/* V321: rebalance mobile Live without changing structure or desktop. */
@media(max-width:767px){
  #hub .view[data-view="live"] .folderScroller{
    height:100%!important;
    min-height:0!important;
    overflow:hidden!important;
    padding:0 2px 86px!important;
    display:grid!important;
    grid-template-rows:30px auto auto!important;
    gap:7px!important;
    align-content:start!important;
  }
  #hub .view[data-view="live"] .hubLiveGuide{
    height:30px!important;
    min-height:30px!important;
    margin:0!important;
    padding:4px 10px!important;
    border-radius:13px!important;
    font-size:9.8px!important;
    line-height:1.05!important;
  }
  #hub .view[data-view="live"] .livePlatformCard{
    height:266px!important;
    min-height:266px!important;
    max-height:266px!important;
    margin:0!important;
    padding:7px 9px!important;
    display:grid!important;
    grid-template-rows:42px auto!important;
    gap:5px!important;
    align-self:start!important;
    overflow:hidden!important;
    border-radius:21px!important;
  }
  #hub .view[data-view="live"] .livePlatformHead{
    min-height:42px!important;
    height:42px!important;
    margin:0!important;
    grid-template-columns:36px minmax(0,1fr)!important;
    gap:8px!important;
    align-items:center!important;
  }
  #hub .view[data-view="live"] .livePlatformIcon{
    width:36px!important;
    height:36px!important;
    border-radius:12px!important;
    font-size:15px!important;
  }
  #hub .view[data-view="live"] .livePaneTitle{
    font-size:18px!important;
    line-height:1!important;
  }
  #hub .view[data-view="live"] .livePlatformSubtitle{
    margin-top:2px!important;
    font-size:8.8px!important;
    line-height:1.05!important;
  }
  #hub .view[data-view="live"] .liveMiniFolders{
    height:auto!important;
    min-height:0!important;
    display:grid!important;
    grid-template-rows:repeat(3,65px)!important;
    gap:5px!important;
    align-content:start!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder{
    height:65px!important;
    min-height:65px!important;
    max-height:65px!important;
    margin:0!important;
    padding:6px 9px!important;
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
    font-size:8.4px!important;
    line-height:1.05!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder i{font-size:18px!important}
}
@media(max-width:767px) and (max-height:760px){
  #hub .view[data-view="live"] .folderScroller{
    padding-bottom:78px!important;
    grid-template-rows:27px auto auto!important;
    gap:6px!important;
  }
  #hub .view[data-view="live"] .hubLiveGuide{
    height:27px!important;
    min-height:27px!important;
    padding:3px 8px!important;
    font-size:8.8px!important;
  }
  #hub .view[data-view="live"] .livePlatformCard{
    height:228px!important;
    min-height:228px!important;
    max-height:228px!important;
    padding:6px 8px!important;
    grid-template-rows:38px auto!important;
    gap:4px!important;
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
  #hub .view[data-view="live"] .livePaneTitle{font-size:16.5px!important}
  #hub .view[data-view="live"] .livePlatformSubtitle{font-size:8px!important}
  #hub .view[data-view="live"] .liveMiniFolders{
    grid-template-rows:repeat(3,54px)!important;
    gap:4px!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder{
    height:54px!important;
    min-height:54px!important;
    max-height:54px!important;
    padding:4px 7px!important;
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
  #hub .view[data-view="live"] .liveMiniFolder b{font-size:11.5px!important}
  #hub .view[data-view="live"] .liveMiniFolder small{font-size:7.6px!important}
}
</style>'''

def patch_text(text:str)->str:
    for marker in ('id="v318HubFillLiveFit"','livePlatformTwitch','livePlatformYoutube','hubLiveGuide'):
        if marker not in text:
            raise RuntimeError('V321 missing runtime Live anchor: '+marker)
    marker=f'id="{STYLE_ID}"'
    if text.count(marker)==1 and STYLE in text:
        return text
    out=re.sub(r'<style id="'+re.escape(STYLE_ID)+r'">.*?</style>\n?','',text,count=1,flags=re.DOTALL)
    if '</head>' not in out:
        raise RuntimeError('V321 Hub </head> anchor missing')
    return out.replace('</head>',STYLE+'\n</head>',1)

def main()->None:
    path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not path.is_file():
        raise SystemExit('V321 Hub target missing: '+str(path))
    before=path.read_text(encoding='utf-8')
    after=patch_text(before)
    path.write_text(after,encoding='utf-8')
    print('V321 mobile Live balance applied changed=',before!=after,flush=True)

if __name__=='__main__':
    main()
