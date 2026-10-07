#!/usr/bin/env python3
from pathlib import Path
import sys

DEFAULT_HUB = Path('/app/web/creator_hub_v156_component/index.html')

CSS = r'''
/* V311 MOBILE HUB CLEANUP */
@media(max-width:760px){
  /* PROFILE: the four overview cards are the only account summary. */
  #hub .view[data-view="profile"] .profilePlanGroup,
  #hub .view[data-view="profile"] .profileOverviewActions,
  #hub .view[data-view="profile"] .profileMobilePlan{display:none!important}
  #hub .view[data-view="profile"] .profileOverviewGrid{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;margin-top:9px!important
  }
  #hub .view[data-view="profile"] .profileOverviewCard,
  #hub .view[data-view="profile"] .profileOverviewCard:nth-child(3),
  #hub .view[data-view="profile"] .profileOverviewCard:nth-child(4){
    grid-column:auto!important;min-height:118px!important;
    display:flex!important;flex-direction:column!important;align-items:flex-start!important;
    justify-content:space-between!important;padding:12px!important
  }
  #hub .view[data-view="profile"] .profileOverviewHint{text-align:left!important;max-width:none!important}

  /* BOZZE: remove the generic account/project counters. */
  #hub .view[data-view="projects"][data-project-mode="drafts"] .stats{display:none!important}

  /* LIVE: no redundant root chooser; Twitch + YouTube are the page. */
  #hub .view[data-view="live"] .liveRootFolders{display:none!important}
  #hub .view[data-view="live"] .livePane{display:block!important;margin:0 0 14px!important}
  #hub .view[data-view="live"] .livePane[data-live-pane="highlights"]{display:none!important}
  #hub .view[data-view="live"] .livePaneTitle{font-size:17px!important;margin:4px 4px 7px!important}
  #hub .view[data-view="live"] .liveMiniFolder{min-height:66px!important}

  /* HUB HOME: make every destination visible above the fixed Game Bar. */
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .dashboard{
    grid-template-rows:auto minmax(0,1fr)!important;gap:6px!important
  }
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .profileCard{
    min-height:82px!important;padding:7px 9px!important;border-radius:19px!important
  }
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .profileCard .avatar{
    width:45px!important;height:45px!important;border-radius:14px!important
  }
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folders{
    grid-template-columns:1fr!important;grid-template-rows:repeat(5,minmax(0,1fr))!important;
    gap:5px!important;min-height:0!important;overflow:hidden!important;padding-bottom:2px!important
  }
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder,
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder[data-folder]{
    min-height:0!important;height:auto!important;padding:6px 9px!important;border-radius:17px!important
  }
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folderIcon{
    width:36px!important;height:36px!important;border-radius:11px!important
  }
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder h2{font-size:13.5px!important}
  #hub[data-v300-layout="hub"] .view[data-view="dashboard"] .folder p{font-size:8.4px!important;line-height:1.12!important}
}
/* END V311 MOBILE HUB CLEANUP */
'''

YOUTUBE_OLD = '''<div class="livePane" data-live-pane="youtube"><div class="livePaneTitle">YouTube Live</div><div class="empty">Quando collegheremo YouTube Live, dirette e replay compariranno qui con la stessa struttura a cartelle.</div></div>'''
YOUTUBE_NEW = '''<div class="livePane" data-live-pane="youtube">
       <div class="livePaneTitle">YouTube</div>
       <div class="liveMiniFolders youtubeMiniFolders">
        <button class="liveMiniFolder" type="button"><span>▣</span><div><b>Le tue live</b><small>Dirette YouTube salvate nel Creator Hub</small></div><i>›</i></button>
        <button class="liveMiniFolder" type="button"><span>▶</span><div><b>VOD</b><small>Replay completi delle dirette</small></div><i>›</i></button>
        <button class="liveMiniFolder" type="button"><span>✦</span><div><b>Highlights</b><small>Short e momenti estratti da YouTube</small></div><i>›</i></button>
       </div>
       <div class="liveMiniContent"><div class="empty">Le tue live YouTube compariranno qui quando saranno disponibili.</div></div>
      </div>'''

JS_ANCHOR = '''if(view==="projects"){
     $$("[data-project-pane]").forEach(p=>{p.style.display=(!projectMode||p.dataset.projectPane===projectMode)?"":"none"});'''
JS_REPL = '''if(view==="projects"){
     const projectsView=$("[data-view=projects]");if(projectsView)projectsView.dataset.projectMode=projectMode||"all";
     $$("[data-project-pane]").forEach(p=>{p.style.display=(!projectMode||p.dataset.projectPane===projectMode)?"":"none"});'''


def patch_hub_text(text: str) -> str:
    if 'V311 MOBILE HUB CLEANUP' in text:
        return text
    if '</style>' not in text:
        raise RuntimeError('V311 style anchor missing')
    text = text.replace('</style>', CSS + '\n</style>', 1)
    if YOUTUBE_OLD not in text:
        raise RuntimeError('V311 YouTube live anchor missing')
    text = text.replace(YOUTUBE_OLD, YOUTUBE_NEW, 1)
    if JS_ANCHOR not in text:
        raise RuntimeError('V311 project-mode anchor missing')
    text = text.replace(JS_ANCHOR, JS_REPL, 1)
    return text


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HUB
    before = target.read_text(encoding='utf-8')
    after = patch_hub_text(before)
    target.write_text(after, encoding='utf-8')
    print('V311 mobile Hub cleanup applied:', target, 'changed=', before != after, flush=True)


if __name__ == '__main__':
    main()
