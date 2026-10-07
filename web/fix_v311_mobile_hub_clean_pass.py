#!/usr/bin/env python3
from pathlib import Path
import re
import sys

DEFAULT_HUB = Path('/app/web/creator_hub_v156_component/index.html')
DEFAULT_APP = Path('/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')
CACHE_KEY = '3112'

# This route is mobile-gated by nginx. The final Hub contract must therefore be
# independent from iframe CSS width and from historical data-vXXX layout attrs.
# Put one final stylesheet at the end of <head> so old V2xx/V3xx rules cannot
# win the cascade, then enforce the structural removals once the DOM is live.
STYLE = r'''
<style id="v311HubForce">
/* V311 MOBILE HUB CLEAN PASS */
html,body{overflow:hidden!important}
#hub{height:100dvh!important;min-height:0!important;overflow:hidden!important;padding:7px 6px 6px!important}
#hub .stage{height:100%!important;min-height:0!important;overflow:hidden!important}

/* PROFILE: editor + the four real overview cards only. */
#hub .view[data-view="profile"] .profileMobilePlan,
#hub .view[data-view="profile"] .profilePlanGroup,
#hub .view[data-view="profile"] .profileOverviewActions{display:none!important}
#hub .view[data-view="profile"] .profileOnlyMural{display:none!important}
#hub .view[data-view="profile"] .profileOnlyScroller{overflow-y:auto!important;overflow-x:hidden!important;padding-bottom:86px!important}
#hub .view[data-view="profile"] .profileOverviewGrid{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px!important;margin:10px 0 0!important}
#hub .view[data-view="profile"] .profileOverviewCard{min-height:104px!important;padding:10px!important;border-radius:16px!important}

/* BOZZE: no four-stat strip. Keep title/count and the saved drafts/empty state. */
#hub .view[data-view="projects"] #projectRows .stats,
#hub .view[data-view="drafts"] #projectRows .stats{display:none!important}

/* LIVE: remove the three launcher tiles. Twitch and YouTube each own a section. */
#hub .view[data-view="live"] .liveRootFolders{display:none!important}
#hub .view[data-view="live"] .livePane[data-live-pane="twitch"],
#hub .view[data-view="live"] .livePane[data-live-pane="youtube"]{display:block!important}
#hub .view[data-view="live"] .livePane[data-live-pane="highlights"]{display:none!important}
#hub .view[data-view="live"] .livePane[data-live-pane="youtube"]{margin-top:14px!important;padding-top:12px!important;border-top:1px solid rgba(143,181,216,.22)!important}
#hub .view[data-view="live"] .livePaneTitle{font-size:17px!important;margin:3px 4px 7px!important}
#hub .view[data-view="live"] .liveMiniFolders{display:grid!important;grid-template-columns:1fr!important;gap:7px!important}
#hub .view[data-view="live"] .liveMiniFolder{min-height:62px!important;padding:9px 10px!important;border-radius:15px!important}

/* HUB HOME: four destinations, all visible above the fixed Game Bar. */
#hub .view[data-view="dashboard"]{overflow:hidden!important}
#hub .view[data-view="dashboard"] .dashboard{height:100%!important;min-height:0!important;display:grid!important;grid-template-rows:auto minmax(0,1fr)!important;gap:6px!important}
#hub .view[data-view="dashboard"] .hubMural{display:none!important}
#hub .view[data-view="dashboard"] .folder[data-folder="subscription"]{display:none!important}
#hub .view[data-view="dashboard"] .profileCard{min-height:80px!important;height:auto!important;padding:7px 8px!important;border-radius:18px!important;grid-template-columns:auto minmax(0,1fr)!important;gap:8px!important}
#hub .view[data-view="dashboard"] .profileCard .avatar{width:43px!important;height:43px!important;border-radius:14px!important;font-size:16px!important}
#hub .view[data-view="dashboard"] .profileName{font-size:16px!important}
#hub .view[data-view="dashboard"] .profileMeta{font-size:9px!important;margin-top:2px!important;line-height:1.15!important}
#hub .view[data-view="dashboard"] .badges{margin-top:3px!important;gap:4px!important}
#hub .view[data-view="dashboard"] .badge{font-size:7.2px!important;padding:3px 5px!important}
#hub .view[data-view="dashboard"] .profileSocials{margin-top:3px!important;gap:4px!important}
#hub .view[data-view="dashboard"] .profileSocials .socialDot{width:22px!important;height:22px!important;border-radius:8px!important}
#hub .view[data-view="dashboard"] .profileAction{display:none!important}
#hub .view[data-view="dashboard"] .folders{width:100%!important;height:100%!important;min-height:0!important;display:grid!important;grid-template-columns:1fr!important;grid-template-rows:repeat(4,minmax(0,1fr))!important;gap:5px!important;align-content:stretch!important;overflow:hidden!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important}
#hub .view[data-view="dashboard"] .folder,
#hub .view[data-view="dashboard"] .folder[data-folder]{position:relative!important;width:100%!important;height:auto!important;min-height:0!important;margin:0!important;padding:7px 10px!important;border:1px solid rgba(143,181,216,.20)!important;border-radius:17px!important;background:rgba(255,255,255,.90)!important;box-shadow:0 8px 20px rgba(61,104,145,.055),inset 0 1px 0 rgba(255,255,255,.98)!important;display:grid!important;grid-template-columns:auto minmax(0,1fr) auto!important;grid-template-rows:auto auto!important;column-gap:9px!important;row-gap:1px!important;align-items:center!important}
#hub .view[data-view="dashboard"] .folder::after{display:none!important}
#hub .view[data-view="dashboard"] .folder>div:first-child,
#hub .view[data-view="dashboard"] .folderTop{display:contents!important}
#hub .view[data-view="dashboard"] .folderIcon{grid-column:1!important;grid-row:1/3!important;width:38px!important;height:38px!important;border-radius:12px!important;font-size:14px!important;align-self:center!important}
#hub .view[data-view="dashboard"] .folderArrow{grid-column:3!important;grid-row:1/3!important;font-size:20px!important;align-self:center!important}
#hub .view[data-view="dashboard"] .folder h2{grid-column:2!important;grid-row:1!important;margin:0!important;font-size:15px!important;line-height:1!important;align-self:end!important}
#hub .view[data-view="dashboard"] .folder p{grid-column:2!important;grid-row:2!important;margin:0!important;font-size:8.8px!important;line-height:1.15!important;align-self:start!important}
#hub .view[data-view="dashboard"] .folderFoot{display:none!important}
/* END V311 MOBILE HUB CLEAN PASS */
</style>
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

RUNTIME = r'''
<script id="v311HubRuntime">
(()=>{
  const apply=()=>{
    document.documentElement.dataset.gsfHubVersion='3112';
    const hide=(selector)=>document.querySelectorAll(selector).forEach((el)=>el.style.setProperty('display','none','important'));
    hide('#hub .view[data-view="profile"] .profileMobilePlan,#hub .view[data-view="profile"] .profilePlanGroup,#hub .view[data-view="profile"] .profileOverviewActions');
    hide('#hub .view[data-view="projects"] #projectRows .stats,#hub .view[data-view="drafts"] #projectRows .stats');
    hide('#hub .view[data-view="live"] .liveRootFolders,#hub .view[data-view="live"] .livePane[data-live-pane="highlights"]');
    hide('#hub .view[data-view="dashboard"] .hubMural,#hub .view[data-view="dashboard"] .folder[data-folder="subscription"]');
    document.querySelectorAll('#hub .view[data-view="live"] .livePane[data-live-pane="twitch"],#hub .view[data-view="live"] .livePane[data-live-pane="youtube"]').forEach((el)=>el.style.setProperty('display','block','important'));
  };
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',apply,{once:true}); else apply();
  const observer=new MutationObserver(()=>requestAnimationFrame(apply));
  const startObserver=()=>observer.observe(document.body||document.documentElement,{childList:true,subtree:true});
  if(document.body) startObserver(); else document.addEventListener('DOMContentLoaded',startObserver,{once:true});
})();
</script>
'''


def patch_hub_text(text: str) -> str:
    if 'id="v311HubForce"' in text and 'id="v311HubRuntime"' in text:
        return text
    if YOUTUBE_OLD in text:
        text = text.replace(YOUTUBE_OLD, YOUTUBE_NEW, 1)
    elif 'youtubeLiveFolders' not in text:
        raise RuntimeError('V311: YouTube Live pane anchor missing')
    if '</head>' not in text:
        raise RuntimeError('V311: head anchor missing')
    if '</body>' not in text:
        raise RuntimeError('V311: body anchor missing')
    text = text.replace('</head>', STYLE + '\n</head>', 1)
    text = text.replace('</body>', RUNTIME + '\n</body>', 1)
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

    print('V311 mobile Hub clean pass applied:', hub, 'changed=', before != after, 'force=3112', flush=True)
    print('V311 Creator Hub cache key:', 'v='+CACHE_KEY, 'changed=', shell_before != shell_after, flush=True)


if __name__ == '__main__':
    main()
