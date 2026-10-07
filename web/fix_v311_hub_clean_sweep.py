#!/usr/bin/env python3
from pathlib import Path
import sys

DEFAULT_HUB = Path('/app/web/creator_hub_v156_component/index.html')

CSS = r'''
/* V311 HUB CLEAN SWEEP */
@media(max-width:760px){
  /* Dashboard: only the three real destinations. Social stays inside Profile. */
  #hub .view[data-view="dashboard"] .folder[data-folder="social"]{display:none!important}
  #hub .view[data-view="dashboard"] .folder[data-folder="subscription"]{display:none!important}
  #hub .view[data-view="dashboard"] .folders{
    grid-template-columns:1fr!important;
    grid-template-rows:repeat(3,minmax(0,1fr))!important;
    gap:8px!important;
    min-height:0!important;
  }
  #hub .view[data-view="dashboard"] .folder{
    min-height:0!important;
    padding:12px 14px!important;
  }

  /* Every internal Hub page scrolls only inside its own content area. */
  #hub .view[data-view="profile"] .profileOnlyScroller,
  #hub .view[data-view="projects"] .folderScroller,
  #hub .view[data-view="live"] .folderScroller,
  #hub .view[data-view="social"] .folderScroller,
  #hub .view[data-view="subscription"] .folderScroller{
    overflow-y:auto!important;
    overflow-x:hidden!important;
    overscroll-behavior-y:contain!important;
    -webkit-overflow-scrolling:touch!important;
    padding-bottom:96px!important;
  }

  /* Profile: the plan already exists in the ABBONAMENTO block above. */
  #hub .view[data-view="profile"] .profileOverviewGrid{
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;
    margin:10px 0 0!important;
  }
  #hub .view[data-view="profile"] .profileOverviewCard{
    min-width:0!important;
    min-height:94px!important;
    padding:12px!important;
    border-radius:17px!important;
    overflow:hidden!important;
    display:flex!important;
    flex-direction:column!important;
    align-items:flex-start!important;
    text-align:left!important;
  }
  #hub .view[data-view="profile"] .profileOverviewCard small{
    width:100%!important;
    font-size:10px!important;
    line-height:1.15!important;
    white-space:normal!important;
  }
  #hub .view[data-view="profile"] .profileOverviewValue{
    width:100%!important;
    margin:7px 0 0!important;
    font-size:27px!important;
    line-height:1!important;
    white-space:normal!important;
    overflow-wrap:anywhere!important;
  }
  #hub .view[data-view="profile"] .profileOverviewHint{
    width:100%!important;
    margin:auto 0 0!important;
    padding-top:8px!important;
    font-size:9.5px!important;
    line-height:1.18!important;
    white-space:normal!important;
  }
  #hub .view[data-view="profile"] .profileOverviewCard[data-profile-overview="subscription"]{display:none!important}
  #hub .view[data-view="profile"] .profileOverviewCard[data-profile-overview="social"]{grid-column:1/-1!important;min-height:82px!important}
  #hub .view[data-view="profile"] .profileOverviewActions{display:none!important}
  #hub .view[data-view="profile"] .profileOnlyMural{display:none!important}
  #hub .view[data-view="profile"] .logoutProfile{margin-top:10px!important}

  /* Drafts: no current-project duplicate, no repeated stats. Only saved drafts. */
  #hub .view[data-view="drafts"] #projectRows{display:none!important}
  #hub .view[data-view="drafts"] .projectSection:first-of-type{display:none!important}
  #hub .view[data-view="drafts"] .projectSection{margin-top:0!important}

  /* Live landing is a clean three-item gateway. Subfolders appear only after tap. */
  #hub .view[data-view="live"] .liveRootFolders{display:grid!important;gap:0!important;margin:0!important}
  #hub .view[data-view="live"].live-subview .liveRootFolders{display:none!important}
  #hub .view[data-view="live"] .livePane{display:none!important}
  #hub .view[data-view="live"].live-subview .livePane.active{display:block!important}
  #hub .view[data-view="live"] .liveFolder,
  #hub .view[data-view="live"] .liveMiniFolder{
    min-height:68px!important;
    padding:11px 7px!important;
  }
  #hub .view[data-view="live"] .liveFolder.active{background:transparent!important}
  #hub .view[data-view="live"] .livePaneTitle{margin:8px 4px 7px!important}
  #hub .view[data-view="live"] .liveMiniContent{display:none!important}
  #hub .view[data-view="live"] .liveBack{
    border:0!important;
    background:#EDF6FF!important;
    color:#477FA9!important;
    border-radius:12px!important;
    min-height:38px!important;
    padding:8px 11px!important;
    margin:0 0 7px!important;
    font-size:10px!important;
    font-weight:900!important;
  }
  #hub .view[data-view="live"] .livePlainNote{
    margin:8px 5px 0!important;
    color:#8798AD!important;
    font-size:10px!important;
    line-height:1.3!important;
  }

  /* Projects / Social: compact rows, no oversized dead space. */
  #hub .view[data-view="projects"] .row,
  #hub .view[data-view="social"] .socialCard{min-height:56px!important}
  #hub .view[data-view="social"] .socialGrid{gap:7px!important}
}
/* END V311 HUB CLEAN SWEEP */
'''

LIVE_TWITCH_OLD = '<div class="livePane active" data-live-pane="twitch">'
LIVE_TWITCH_NEW = '<div class="livePane" data-live-pane="twitch"><button class="liveBack" type="button" data-live-back>← Live</button>'
LIVE_YOUTUBE_OLD = '<div class="livePane" data-live-pane="youtube"><div class="livePaneTitle">YouTube Live</div><div class="empty">Quando collegheremo YouTube Live, dirette e replay compariranno qui con la stessa struttura a cartelle.</div></div>'
LIVE_YOUTUBE_NEW = '<div class="livePane" data-live-pane="youtube"><button class="liveBack" type="button" data-live-back>← Live</button><div class="livePaneTitle">YouTube Live</div><div class="livePlainNote">Dirette e replay compariranno qui quando la sorgente sarà collegata.</div></div>'
LIVE_HIGHLIGHTS_OLD = '<div class="livePane" data-live-pane="highlights"><div class="livePaneTitle">Auto Highlights</div><div class="empty">Qui finiranno automaticamente i momenti trovati nelle live Twitch e YouTube.</div></div>'
LIVE_HIGHLIGHTS_NEW = '<div class="livePane" data-live-pane="highlights"><button class="liveBack" type="button" data-live-back>← Live</button><div class="livePaneTitle">Auto Highlights</div><div class="livePlainNote">I momenti trovati automaticamente nelle live compariranno qui.</div></div>'

LIVE_BOOT_OLD = '<div id="liveMiniContent" class="liveMiniContent"><div class="empty">Le tue live Twitch compariranno qui come mini-cartelle, una per ogni diretta.</div></div>'
LIVE_BOOT_NEW = '<div id="liveMiniContent" class="liveMiniContent"></div>'

OPEN_LIVE_OLD = ''' function openLiveFolder(key){
   $$("[data-live-folder]").forEach(b=>b.classList.toggle("active",b.dataset.liveFolder===key));
   $$("[data-live-pane]").forEach(p=>p.classList.toggle("active",p.dataset.livePane===key));
 }'''
OPEN_LIVE_NEW = ''' function openLiveFolder(key){
   const liveView=document.querySelector('.view[data-view="live"]');
   if(liveView)liveView.classList.add("live-subview");
   $$("[data-live-folder]").forEach(b=>b.classList.toggle("active",b.dataset.liveFolder===key));
   $$("[data-live-pane]").forEach(p=>p.classList.toggle("active",p.dataset.livePane===key));
 }
 function closeLiveFolder(){
   const liveView=document.querySelector('.view[data-view="live"]');
   if(liveView)liveView.classList.remove("live-subview");
   $$("[data-live-folder]").forEach(b=>b.classList.remove("active"));
   $$("[data-live-pane]").forEach(p=>p.classList.remove("active"));
 }'''

LIVE_MINI_OLD = '''   if(key==="sessions")box.innerHTML='<div class="empty">Le tue live Twitch compariranno qui come mini-cartelle, una per ogni diretta.</div>';
   else if(key==="vod")box.innerHTML='<div class="empty">I VOD Twitch compariranno qui appena attiveremo la sincronizzazione.</div>';
   else box.innerHTML='<div class="empty">Gli Highlights generati dalle live Twitch compariranno qui automaticamente.</div>';'''
LIVE_MINI_NEW = '''   box.innerHTML="";'''

LIVE_BIND_OLD = '$$("[data-live-folder]").forEach(b=>b.onclick=()=>openLiveFolder(b.dataset.liveFolder));\n $$("[data-live-mini]").forEach(b=>b.onclick=()=>openLiveMini(b.dataset.liveMini));'
LIVE_BIND_NEW = '$$("[data-live-folder]").forEach(b=>b.onclick=()=>openLiveFolder(b.dataset.liveFolder));\n $$("[data-live-back]").forEach(b=>b.onclick=()=>closeLiveFolder());\n $$("[data-live-mini]").forEach(b=>b.onclick=()=>openLiveMini(b.dataset.liveMini));'

OPEN_VIEW_OLD = ' function openView(view="dashboard"){\n   const requested=String(view||"dashboard");'
OPEN_VIEW_NEW = ' function openView(view="dashboard"){\n   if(view==="live"&&typeof closeLiveFolder==="function")closeLiveFolder();\n   const requested=String(view||"dashboard");'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError('V311 anchor missing: ' + label)
    return text.replace(old, new, 1)


def patch_hub_text(text: str) -> str:
    if 'V311 HUB CLEAN SWEEP' in text:
        return text

    text = replace_once(text, '</style>', CSS + '\n</style>', 'style end')

    # Live starts at the clean root level: three choices only, no pre-opened Twitch pane.
    text = text.replace('class="liveFolder active" data-live-folder="twitch"', 'class="liveFolder" data-live-folder="twitch"', 1)
    text = replace_once(text, LIVE_TWITCH_OLD, LIVE_TWITCH_NEW, 'Twitch pane')
    text = replace_once(text, LIVE_YOUTUBE_OLD, LIVE_YOUTUBE_NEW, 'YouTube pane')
    text = replace_once(text, LIVE_HIGHLIGHTS_OLD, LIVE_HIGHLIGHTS_NEW, 'Highlights pane')
    text = replace_once(text, LIVE_BOOT_OLD, LIVE_BOOT_NEW, 'Live bottom bubble')
    text = replace_once(text, OPEN_LIVE_OLD, OPEN_LIVE_NEW, 'Live folder routing')
    text = replace_once(text, LIVE_MINI_OLD, LIVE_MINI_NEW, 'Live mini bubbles')
    text = replace_once(text, LIVE_BIND_OLD, LIVE_BIND_NEW, 'Live back binding')
    text = replace_once(text, OPEN_VIEW_OLD, OPEN_VIEW_NEW, 'Live root reset')

    return text


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HUB
    if not target.is_file():
        raise SystemExit('V311 Creator Hub target missing: ' + str(target))
    before = target.read_text(encoding='utf-8')
    after = patch_hub_text(before)
    target.write_text(after, encoding='utf-8')
    print('V311 Creator Hub clean sweep applied:', target, 'changed=', after != before, flush=True)


if __name__ == '__main__':
    main()
