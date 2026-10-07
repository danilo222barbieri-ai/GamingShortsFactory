#!/usr/bin/env python3
from pathlib import Path
import re
import sys

DEFAULT_HUB = Path('/app/web/creator_hub_v156_component/index.html')
DEFAULT_APP = Path('/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')
CACHE_KEY = '3111'

# /creator-hub-v156/ is already mobile-gated by nginx. Do not wrap the final
# overrides in a CSS-width media query: Streamlit can give the iframe a layout
# viewport wider than the physical iPhone viewport, which made the previous
# V311 rules silently inactive on the real phone.
CSS = r'''
/* V311 MOBILE HUB CLEAN PASS */
/* PROFILE: keep only the editor + four summary cards. */
#hub[data-v300-layout="hub"] .view[data-view="profile"] .profileMobilePlan,
#hub[data-v300-layout="hub"] .view[data-view="profile"] .profilePlanGroup{display:none!important}
#hub[data-v300-layout="hub"] .view[data-view="profile"] .profileOverviewActions{display:none!important}
#hub[data-v300-layout="hub"] .view[data-view="profile"] .profileOverviewGrid{margin-top:10px!important}

/* BOZZE: remove the four statistic boxes, keep counter + drafts list/empty state. */
#hub[data-v300-layout="hub"] .view[data-view="projects"] #projectRows .stats{display:none!important}

/* LIVE: no launcher strip above Twitch; Twitch + YouTube sections stay visible. */
#hub[data-v300-layout="hub"] .view[data-view="live"] .liveRootFolders{display:none!important}
#hub[data-v300-layout="hub"] .view[data-view="live"] .livePane[data-live-pane="twitch"],
#hub[data-v300-layout="hub"] .view[data-view="live"] .livePane[data-live-pane="youtube"]{display:block!important}
#hub[data-v300-layout="hub"] .view[data-view="live"] .livePane[data-live-pane="highlights"]{display:none!important}
#hub[data-v300-layout="hub"] .view[data-view="live"] .livePane[data-live-pane="youtube"]{margin-top:16px!important;padding-top:12px!important;border-top:1px solid rgba(143,181,216,.22)!important}
#hub[data-v300-layout="hub"] .view[data-view="live"] .livePaneTitle{font-size:17px!important;margin:3px 4px 7px!important}
#hub[data-v300-layout="hub"] .view[data-view="live"] .liveMiniFolder{min-height:62px!important;padding:9px 8px!important}

/* HUB HOME: only the four mobile destinations; all visible above the Game Bar. */
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .dashboard{grid-template-rows:auto minmax(0,1fr)!important;gap:5px!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .profileCard{min-height:82px!important;padding:7px 8px!important;border-radius:19px!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .profileCard .avatar{width:44px!important;height:44px!important;border-radius:14px!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .profileName{font-size:16px!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .profileMeta{font-size:9px!important;margin-top:2px!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .badges{margin-top:4px!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .profileSocials{margin-top:3px!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .profileSocials .socialDot{width:22px!important;height:22px!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .hubMural{display:none!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder[data-folder="subscription"]{display:none!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folders{
  grid-template-columns:1fr!important;
  grid-template-rows:repeat(4,minmax(58px,1fr))!important;
  gap:4px!important;
  min-height:0!important;
  overflow:hidden!important;
}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder,
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder[data-folder]{
  min-height:58px!important;
  height:auto!important;
  padding:7px 10px!important;
  border-radius:16px!important;
  column-gap:9px!important;
}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folderIcon{width:38px!important;height:38px!important;border-radius:12px!important;font-size:14px!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder h2{font-size:15px!important;line-height:1!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder p{font-size:8.8px!important;line-height:1.15!important}
#hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folderArrow{font-size:20px!important}
/* END V311 MOBILE HUB CLEAN PASS */
'''

YOUTUBE_OLD = '<div class="livePane" data-live-pane="youtube"><div class="livePaneTitle">YouTube Live</div><div class="empty">Quando collegheremo YouTube Live, dirette e replay compariranno qui con la stessa struttura a cartelle.</div></div>'
YOUTUBE_NEW = '''<div class="livePane" data-live-pane="youtube">
       <div class="livePaneTitle">YouTube</div>
       <div class="liveMiniFolders youtubeLiveFolders">
        <div class="liveMiniFolder"><span>▶</span><div><b>Le tue live</b><small>Dirette YouTube salvate nel Creator Hub</small></div><i>›</i></div>
        <div class="liveMiniFolder"><span>▣</span><div><b>VOD</b><small>Replay completi delle live YouTube</small></div><i>›</i></div>
        <div class="liveMiniFolder"><span>✦</span><div><b>Highlights</b><small>Short e momenti estratti da YouTube</small></div><i>›</i></div>
       </div>
      </div>'''


def patch_hub_text(text: str) -> str:
    if 'V311 MOBILE HUB CLEAN PASS' in text:
        return text
    if '</style>' not in text:
        raise RuntimeError('V311: style anchor missing')
    text = text.replace('</style>', CSS + '\n</style>', 1)
    if YOUTUBE_OLD in text:
        text = text.replace(YOUTUBE_OLD, YOUTUBE_NEW, 1)
    elif 'youtubeLiveFolders' not in text:
        raise RuntimeError('V311: YouTube Live pane anchor missing')
    return text


def patch_shell_text(text: str) -> str:
    target = f'/creator-hub-v156/?v={CACHE_KEY}'
    if target in text:
        return text
    text, count = re.subn(
        r'/creator-hub-v156/\?v=[^"\'&\s]+',
        target,
        text,
    )
    if count < 1:
        raise RuntimeError('V311: Creator Hub shell cache anchor missing')
    return text


def main():
    hub = Path(sys.argv[1]) if len(sys.argv)>1 else DEFAULT_HUB
    app = Path(sys.argv[2]) if len(sys.argv)>2 else DEFAULT_APP
    if not hub.is_file():
        raise SystemExit(f'V311 target missing: {hub}')
    if not app.is_file():
        raise SystemExit(f'V311 shell missing: {app}')

    before = hub.read_text(encoding='utf-8')
    after = patch_hub_text(before)
    hub.write_text(after, encoding='utf-8')

    shell_before = app.read_text(encoding='utf-8')
    shell_after = patch_shell_text(shell_before)
    compile(shell_after, str(app), 'exec')
    app.write_text(shell_after, encoding='utf-8')

    print('V311 mobile Hub clean pass applied:', hub, 'changed=', before != after, flush=True)
    print('V311 Creator Hub cache key:', 'v='+CACHE_KEY, 'changed=', shell_before != shell_after, flush=True)


if __name__ == '__main__':
    main()
