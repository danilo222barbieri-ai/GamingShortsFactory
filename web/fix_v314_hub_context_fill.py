#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import re
import sys

STYLE_ID = 'v314HubContextFill'
PROJECTS_GUIDE = '<div class="hubContextGuide hubProjectsGuide">Qui trovi i tuoi progetti: Shorts completati e bozze da riprendere quando vuoi.</div>'
LIVE_GUIDE = '<div class="hubContextGuide hubLiveGuide">Qui trovi e gestisci live, VOD e Highlights da Twitch e YouTube.</div>'

STYLE = r'''<style id="v314HubContextFill">
/* V314: contextual Hub guidance + full-height Live layout. */
#hub .hubContextGuide{
  width:100%!important;box-sizing:border-box!important;margin:0 0 10px!important;
  padding:8px 12px!important;border:1px solid rgba(143,181,216,.16)!important;
  border-radius:16px!important;background:linear-gradient(135deg,rgba(239,248,255,.95),rgba(242,251,247,.92))!important;
  color:#7185a6!important;font-size:12px!important;line-height:1.25!important;font-weight:800!important;
  box-shadow:0 6px 16px rgba(61,104,145,.04)!important;
}
#hub .hubProjectsGuide{margin:0 0 10px!important}
#hub .hubLiveGuide{margin:0!important}

@media(max-width:767px){
  #hub .view[data-view="projects"] .folderScroller{box-sizing:border-box!important}
  #hub .view[data-view="projects"] .hubContextGuide{font-size:11px!important;padding:7px 10px!important;border-radius:14px!important}

  #hub .view[data-view="live"] .detail,
  #hub .view[data-view="live"] .detailCard{height:100%!important;min-height:0!important;overflow:hidden!important}
  #hub .view[data-view="live"] .folderScroller{
    height:100%!important;min-height:0!important;box-sizing:border-box!important;overflow:hidden!important;
    padding:2px 2px 88px!important;display:grid!important;
    grid-template-rows:auto repeat(2,minmax(0,1fr))!important;gap:9px!important;align-content:stretch!important;
  }
  #hub .view[data-view="live"] .hubLiveGuide{
    min-height:34px!important;display:flex!important;align-items:center!important;
    font-size:10.8px!important;line-height:1.15!important;padding:6px 10px!important;border-radius:14px!important;
  }
  #hub .view[data-view="live"] .livePlatformCard{
    height:100%!important;min-height:0!important;box-sizing:border-box!important;margin:0!important;
    padding:11px 13px!important;display:grid!important;grid-template-rows:auto minmax(0,1fr)!important;
    gap:8px!important;overflow:hidden!important;
  }
  #hub .view[data-view="live"] .livePlatformHead{
    margin:0!important;grid-template-columns:48px minmax(0,1fr)!important;gap:10px!important;align-items:center!important;
  }
  #hub .view[data-view="live"] .livePlatformIcon{width:48px!important;height:48px!important;border-radius:16px!important;font-size:20px!important}
  #hub .view[data-view="live"] .livePaneTitle{font-size:21px!important}
  #hub .view[data-view="live"] .livePlatformSubtitle{margin-top:3px!important;font-size:10.5px!important;line-height:1.15!important}
  #hub .view[data-view="live"] .liveMiniFolders{
    height:100%!important;min-height:0!important;display:grid!important;
    grid-template-rows:repeat(3,minmax(0,1fr))!important;gap:7px!important;align-content:stretch!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder{
    height:100%!important;min-height:0!important;box-sizing:border-box!important;
    grid-template-columns:42px minmax(0,1fr) auto!important;gap:9px!important;padding:6px 10px!important;border-radius:17px!important;
  }
  #hub .view[data-view="live"] .liveMiniFolder>span{width:42px!important;height:42px!important;border-radius:14px!important;font-size:16px!important}
  #hub .view[data-view="live"] .liveMiniFolder b{font-size:14.5px!important}
  #hub .view[data-view="live"] .liveMiniFolder small{margin-top:2px!important;font-size:10px!important;line-height:1.12!important}
}

@media(max-width:767px) and (max-height:760px){
  #hub .view[data-view="live"] .folderScroller{padding-bottom:82px!important;gap:6px!important}
  #hub .view[data-view="live"] .hubLiveGuide{min-height:30px!important;font-size:10px!important;padding-top:4px!important;padding-bottom:4px!important}
  #hub .view[data-view="live"] .livePlatformCard{padding:8px 10px!important;gap:5px!important}
  #hub .view[data-view="live"] .livePlatformHead{grid-template-columns:42px minmax(0,1fr)!important;gap:8px!important}
  #hub .view[data-view="live"] .livePlatformIcon{width:42px!important;height:42px!important;border-radius:14px!important}
  #hub .view[data-view="live"] .livePaneTitle{font-size:18px!important}
  #hub .view[data-view="live"] .livePlatformSubtitle{font-size:9.5px!important}
  #hub .view[data-view="live"] .liveMiniFolders{gap:5px!important}
  #hub .view[data-view="live"] .liveMiniFolder{grid-template-columns:36px minmax(0,1fr) auto!important;padding:4px 8px!important}
  #hub .view[data-view="live"] .liveMiniFolder>span{width:36px!important;height:36px!important;border-radius:12px!important}
  #hub .view[data-view="live"] .liveMiniFolder b{font-size:13px!important}
  #hub .view[data-view="live"] .liveMiniFolder small{font-size:9px!important}
}
</style>'''


def _clean(text: str) -> str:
    text = re.sub(r'<style id="' + re.escape(STYLE_ID) + r'">.*?</style>\n?', '', text, count=1, flags=re.DOTALL)
    text = re.sub(r'<div class="hubContextGuide hubProjectsGuide">.*?</div>\n\s*', '', text, count=1, flags=re.DOTALL)
    text = re.sub(r'<div class="hubContextGuide hubLiveGuide">.*?</div>\n\s*', '', text, count=1, flags=re.DOTALL)
    return text


def patch_text(text: str) -> str:
    if 'V311 APPROVED CREATOR REFERENCE' not in text:
        raise RuntimeError('V314 requires the normalized V311 Creator Hub')
    for marker in ('id="projectHubCards"', 'livePlatformTwitch', 'livePlatformYoutube'):
        if marker not in text:
            raise RuntimeError(f'V314 missing Creator Hub anchor: {marker}')

    out = _clean(text)
    if '</head>' not in out:
        raise RuntimeError('V314 Creator Hub </head> anchor missing')
    out = out.replace('</head>', STYLE + '\n</head>', 1)

    project_anchor = '<div id="projectHubCards"'
    p = out.find(project_anchor)
    if p < 0:
        raise RuntimeError('V314 Projects landing anchor missing')
    out = out[:p] + PROJECTS_GUIDE + '\n      ' + out[p:]

    live_anchor = '<div class="livePane active livePlatformCard livePlatformTwitch"'
    p = out.find(live_anchor)
    if p < 0:
        raise RuntimeError('V314 Live Twitch anchor missing')
    out = out[:p] + LIVE_GUIDE + '\n      ' + out[p:]
    return out


def _apply_v315_mobile_home_lower_flow() -> bool:
    patch_path = Path(__file__).resolve().with_name('fix_v315_mobile_home_lower_flow.py')
    if not patch_path.is_file():
        raise RuntimeError('V315 mobile Home lower-flow patch missing')
    spec = importlib.util.spec_from_file_location('v315_mobile_home_lower_flow', patch_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    home = Path('/app/web/home_v154_component/index.html')
    if not home.is_file():
        raise RuntimeError(f'V315 Home missing: {home}')
    before = home.read_text(encoding='utf-8')
    after = mod.patch_text(before)
    home.write_text(after, encoding='utf-8')
    return before != after


def main() -> None:
    hub = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app/web/creator_hub_v156_component/index.html')
    if not hub.is_file():
        raise SystemExit(f'V314 Hub missing: {hub}')
    before = hub.read_text(encoding='utf-8')
    after = patch_text(before)
    hub.write_text(after, encoding='utf-8')
    home_changed = _apply_v315_mobile_home_lower_flow()
    print('V314 Hub context + Live full-height applied changed=', before != after, 'V315 mobile Home changed=', home_changed, flush=True)


if __name__ == '__main__':
    main()
