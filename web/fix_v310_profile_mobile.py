#!/usr/bin/env python3
from pathlib import Path
import sys

DEFAULT_HUB = Path('/app/web/creator_hub_v156_component/index.html')
MARK = 'V310 PROFILE MOBILE CLEANUP'

STYLE = r'''
<style id="gsf-v310-profile-mobile">
/* V310 PROFILE MOBILE CLEANUP */
@media(max-width:760px){
  #hub .view[data-view="profile"] .profileMobilePlan{display:none!important}

  #hub .view[data-view="profile"] .detailCard{
    min-height:0!important;
    overflow:hidden!important;
    padding-bottom:0!important;
  }

  #hub .view[data-view="profile"] .profileOnlyScroller{
    display:block!important;
    height:100%!important;
    min-height:0!important;
    overflow-y:auto!important;
    overflow-x:hidden!important;
    overscroll-behavior:contain!important;
    -webkit-overflow-scrolling:touch!important;
    padding:0 0 92px!important;
  }

  #hub .view[data-view="profile"] .profileOverviewGrid{
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;
    margin:10px 0 0!important;
    width:100%!important;
  }

  #hub .view[data-view="profile"] .profileOverviewCard{
    display:flex!important;
    flex-direction:column!important;
    align-items:flex-start!important;
    justify-content:center!important;
    width:100%!important;
    min-width:0!important;
    min-height:92px!important;
    padding:11px 12px!important;
    text-align:left!important;
    overflow:hidden!important;
  }

  #hub .view[data-view="profile"] .profileOverviewCard:nth-child(3),
  #hub .view[data-view="profile"] .profileOverviewCard:nth-child(4){
    grid-column:1/-1!important;
    min-height:82px!important;
  }

  #hub .view[data-view="profile"] .profileOverviewCard small{display:block!important;width:100%!important;line-height:1.12!important;white-space:normal!important}
  #hub .view[data-view="profile"] .profileOverviewValue{display:block!important;width:100%!important;margin:6px 0 0!important;font-size:25px!important;line-height:1!important}
  #hub .view[data-view="profile"] .profileOverviewHint{display:block!important;width:100%!important;margin:7px 0 0!important;line-height:1.18!important;white-space:normal!important}

  #hub .view[data-view="profile"] .profileOverviewActions{display:none!important}

  #hub .view[data-view="profile"] .profileOnlyScroller .logoutProfile{
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    width:100%!important;
    min-height:44px!important;
    margin:10px 0 0!important;
    border-radius:14px!important;
  }
}
/* END V310 PROFILE MOBILE CLEANUP */
</style>
'''


def patch_hub_text(text: str) -> str:
    if MARK in text:
        return text
    pos = text.lower().rfind('</head>')
    if pos < 0:
        raise RuntimeError('V310: </head> anchor missing')
    return text[:pos] + STYLE + '\n' + text[pos:]


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HUB
    if not target.is_file():
        raise SystemExit(f'V310 target missing: {target}')
    before = target.read_text(encoding='utf-8')
    after = patch_hub_text(before)
    target.write_text(after, encoding='utf-8')
    print('V310 mobile Profile cleanup applied:', target, 'changed=', after != before, flush=True)


if __name__ == '__main__':
    main()
