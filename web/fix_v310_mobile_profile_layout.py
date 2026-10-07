#!/usr/bin/env python3
from pathlib import Path
import sys

DEFAULT_HUB = Path('/app/web/creator_hub_v156_component/index.html')

CSS = r'''
/* V310 MOBILE PROFILE LAYOUT */
@media(max-width:760px){
  #hub .view[data-view="profile"] .detailCard{
    min-height:0!important;
    overflow:hidden!important;
  }
  #hub .view[data-view="profile"] .profileOnlyScroller{
    height:100%!important;
    min-height:0!important;
    overflow-y:auto!important;
    overflow-x:hidden!important;
    overscroll-behavior-y:contain!important;
    -webkit-overflow-scrolling:touch!important;
    scrollbar-width:none!important;
    padding:0 1px 96px!important;
  }
  #hub .view[data-view="profile"] .profileOnlyScroller::-webkit-scrollbar{display:none!important}

  /* The separate mobile subscription strip duplicated the real plan overview. */
  #hub .view[data-view="profile"] .profileMobilePlan{display:none!important}
  #hub .view[data-view="profile"] .profileOnlyMural{display:none!important}

  #hub .view[data-view="profile"] .profileDetail{
    grid-template-columns:72px minmax(0,1fr)!important;
    gap:10px!important;
    align-items:start!important;
  }
  #hub .view[data-view="profile"] .profileDetail .avatar{
    width:62px!important;
    height:62px!important;
    border-radius:18px!important;
  }
  #hub .view[data-view="profile"] .profileLines{gap:7px!important}
  #hub .view[data-view="profile"] .profileLine{
    min-height:58px!important;
    padding:9px 11px!important;
    border-radius:15px!important;
  }

  #hub .view[data-view="profile"] .profileOverviewGrid{
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    grid-auto-rows:auto!important;
    gap:8px!important;
    margin:10px 0 0!important;
    width:100%!important;
  }
  #hub .view[data-view="profile"] .profileOverviewCard{
    display:grid!important;
    grid-template-columns:minmax(0,1fr)!important;
    grid-template-rows:auto auto auto!important;
    align-content:center!important;
    justify-items:start!important;
    gap:5px!important;
    min-width:0!important;
    min-height:104px!important;
    width:100%!important;
    padding:12px 13px!important;
    border-radius:17px!important;
    overflow:hidden!important;
    text-align:left!important;
  }
  #hub .view[data-view="profile"] .profileOverviewCard:nth-child(3),
  #hub .view[data-view="profile"] .profileOverviewCard:nth-child(4){
    grid-column:1/-1!important;
    min-height:86px!important;
    grid-template-columns:minmax(0,1fr) auto!important;
    grid-template-rows:auto auto!important;
    column-gap:12px!important;
    row-gap:4px!important;
    align-items:center!important;
  }
  #hub .view[data-view="profile"] .profileOverviewCard small{
    display:block!important;
    width:100%!important;
    margin:0!important;
    color:#6E86A4!important;
    font-size:9.5px!important;
    line-height:1.15!important;
    font-weight:900!important;
    letter-spacing:.035em!important;
    white-space:normal!important;
  }
  #hub .view[data-view="profile"] .profileOverviewValue{
    display:block!important;
    width:100%!important;
    margin:0!important;
    color:#1195F2!important;
    font-size:27px!important;
    line-height:1!important;
    font-weight:950!important;
    letter-spacing:-.035em!important;
    white-space:nowrap!important;
  }
  #hub .view[data-view="profile"] .profileOverviewHint{
    display:block!important;
    width:100%!important;
    margin:0!important;
    color:#6F8CAA!important;
    font-size:9.5px!important;
    line-height:1.2!important;
    font-weight:750!important;
    white-space:normal!important;
  }
  #hub .view[data-view="profile"] .profileOverviewCard:nth-child(3) small,
  #hub .view[data-view="profile"] .profileOverviewCard:nth-child(4) small{
    grid-column:1!important;
    grid-row:1!important;
  }
  #hub .view[data-view="profile"] .profileOverviewCard:nth-child(3) .profileOverviewValue,
  #hub .view[data-view="profile"] .profileOverviewCard:nth-child(4) .profileOverviewValue{
    grid-column:1!important;
    grid-row:2!important;
    font-size:25px!important;
  }
  #hub .view[data-view="profile"] .profileOverviewCard:nth-child(3) .profileOverviewHint,
  #hub .view[data-view="profile"] .profileOverviewCard:nth-child(4) .profileOverviewHint{
    grid-column:2!important;
    grid-row:1/3!important;
    width:auto!important;
    max-width:124px!important;
    text-align:right!important;
    font-size:9.5px!important;
  }

  /* These duplicate the two full-width cards above on mobile. */
  #hub .view[data-view="profile"] .profileOverviewActions{display:none!important}

  #hub .view[data-view="profile"] .logoutProfile{
    width:100%!important;
    min-height:44px!important;
    margin:10px 0 0!important;
  }
}
/* END V310 MOBILE PROFILE LAYOUT */
'''


def patch_hub_text(text: str) -> str:
    if 'V310 MOBILE PROFILE LAYOUT' in text:
        return text
    anchor = '</style>'
    if anchor not in text:
        raise RuntimeError('V310: style anchor missing')
    return text.replace(anchor, CSS + '\n</style>', 1)


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HUB
    if not target.is_file():
        raise SystemExit(f'V310 target missing: {target}')
    before = target.read_text(encoding='utf-8')
    after = patch_hub_text(before)
    target.write_text(after, encoding='utf-8')
    print('V310 mobile profile layout applied:', target, 'changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
