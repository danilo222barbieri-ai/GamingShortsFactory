#!/usr/bin/env python3
from pathlib import Path
import re
import sys

DEFAULT_HUB = Path('/app/web/creator_hub_v156_component/index.html')

CSS = r'''
/* V310 CREATOR HUB MOBILE CLEANUP */
@media(max-width:760px){
  #hub .view[data-view="profile"] .profileOnlyScroller{
    overflow-y:auto!important;
    overflow-x:hidden!important;
    overscroll-behavior-y:contain!important;
    -webkit-overflow-scrolling:touch!important;
    padding-bottom:88px!important;
  }
  #hub .view[data-view="profile"] .profileOverviewGrid{
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:8px!important;
    margin:10px 0 0!important;
  }
  #hub .view[data-view="profile"] .profileOverviewCard{
    display:flex!important;
    flex-direction:column!important;
    align-items:flex-start!important;
    justify-content:flex-start!important;
    width:100%!important;
    min-width:0!important;
    min-height:112px!important;
    padding:12px!important;
    border-radius:18px!important;
    text-align:left!important;
    overflow:hidden!important;
  }
  #hub .view[data-view="profile"] .profileOverviewCard small{
    display:block!important;
    width:100%!important;
    margin:0!important;
    font-size:10px!important;
    line-height:1.15!important;
    letter-spacing:.035em!important;
    white-space:normal!important;
  }
  #hub .view[data-view="profile"] .profileOverviewValue{
    display:block!important;
    width:100%!important;
    margin:8px 0 0!important;
    font-size:29px!important;
    line-height:.95!important;
    letter-spacing:-.045em!important;
    white-space:normal!important;
    overflow-wrap:anywhere!important;
  }
  #hub .view[data-view="profile"] .profileOverviewHint{
    display:block!important;
    width:100%!important;
    margin:auto 0 0!important;
    padding-top:10px!important;
    font-size:9.5px!important;
    line-height:1.18!important;
    white-space:normal!important;
    overflow-wrap:anywhere!important;
  }
  #hub .view[data-view="profile"] .profileOverviewActions{
    display:grid!important;
    grid-template-columns:1fr!important;
    gap:7px!important;
    margin-top:8px!important;
  }
  #hub .view[data-view="profile"] .profileOverviewAction{
    min-height:48px!important;
    padding:10px 12px!important;
    border-radius:16px!important;
    font-size:10.5px!important;
  }
  #hub .view[data-view="profile"] .profileEdit{
    grid-template-columns:72px minmax(0,1fr)!important;
    gap:10px!important;
  }
  #hub .view[data-view="profile"] .profileField{min-width:0!important}
  #hub .view[data-view="profile"] .profileField input{min-width:0!important}
  #hub .view[data-view="profile"] .planRow{
    grid-template-columns:minmax(0,1fr) auto!important;
    gap:8px!important;
    align-items:center!important;
  }
  #hub .view[data-view="profile"] .planBtn{
    max-width:150px!important;
    white-space:normal!important;
    line-height:1.15!important;
  }

  #hub .view[data-view="drafts"] .folderScroller{
    padding-bottom:88px!important;
  }
  #hub .view[data-view="drafts"] #projectRows .stats{
    margin-top:0!important;
  }

  #hub .view[data-view="live"] .folderScroller{
    padding-bottom:88px!important;
  }
  #hub .view[data-view="live"] .liveRootFolders{
    margin-bottom:8px!important;
  }
  #hub .view[data-view="live"] .liveFolder,
  #hub .view[data-view="live"] .liveMiniFolder{
    min-height:62px!important;
    padding:10px 6px!important;
  }
  #hub .view[data-view="live"] .livePaneTitle{
    margin:8px 4px 5px!important;
  }
  #hub .view[data-view="live"] .liveMiniContent:empty{
    display:none!important;
  }
}
/* END V310 CREATOR HUB MOBILE CLEANUP */
'''

PROJECT_RENDER_RE = re.compile(
    r'''\s*const p=state\.project\|\|\{\};\s*\n\s*\$\("#projectRows"\)\.innerHTML=p\.id\?.*?;'\s*''',
    re.DOTALL,
)

# The exact current assignment is kept as a fallback because older Python regex
# engines can be awkward around the HTML/JS ternary quotes in this generated file.
PROJECT_RENDER_OLD = '''   const p=state.project||{};
   $("#projectRows").innerHTML=p.id?'<div class="projectBox"><div class="projectInfo"><b>Progetto corrente</b><span>'+(p.has_source?"Gameplay collegato · ":"In preparazione · ")+ago(p.updated_at)+'</span></div><div class="quick"><button data-quick="ai">IA</button><button data-quick="editor">Editor</button><button data-quick="social">Social</button></div></div><div class="stats"><div class="stat"><b>'+String(st.shorts_created||0)+'</b><small>Short</small></div><div class="stat"><b>'+String(st.shorts_published||0)+'</b><small>Pubblicati</small></div><div class="stat"><b>'+String(st.drafts||0)+'</b><small>Bozze</small></div><div class="stat"><b>'+String(st.social||0)+'</b><small>Social</small></div></div>':'<div class="empty">Nessun progetto attivo recuperato.</div>';
'''

PROJECT_RENDER_NEW = '''   $("#projectRows").innerHTML='<div class="stats"><div class="stat"><b>'+String(st.shorts_created||0)+'</b><small>Short</small></div><div class="stat"><b>'+String(st.shorts_published||0)+'</b><small>Pubblicati</small></div><div class="stat"><b>'+String(st.drafts||0)+'</b><small>Bozze</small></div><div class="stat"><b>'+String(st.social||0)+'</b><small>Social</small></div></div>';
'''

LIVE_BOOT_OLD = '<div id="liveMiniContent" class="liveMiniContent"><div class="empty">Le tue live Twitch compariranno qui come mini-cartelle, una per ogni diretta.</div></div>'
LIVE_BOOT_NEW = '<div id="liveMiniContent" class="liveMiniContent"></div>'

LIVE_HANDLER_OLD = '''   if(key==="sessions")box.innerHTML='<div class="empty">Le tue live Twitch compariranno qui come mini-cartelle, una per ogni diretta.</div>';
   else if(key==="vod")box.innerHTML='<div class="empty">I VOD Twitch compariranno qui appena attiveremo la sincronizzazione.</div>';
   else box.innerHTML='<div class="empty">Gli Highlights generati dalle live Twitch compariranno qui automaticamente.</div>';'''
LIVE_HANDLER_NEW = '''   box.innerHTML="";'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f'V310 anchor missing: {label}')
    return text.replace(old, new, 1)


def patch_hub_text(text: str) -> str:
    if 'V310 CREATOR HUB MOBILE CLEANUP' in text:
        return text

    text = replace_once(text, '</style>', CSS + '\n</style>', 'style end')

    if PROJECT_RENDER_OLD in text:
        text = text.replace(PROJECT_RENDER_OLD, PROJECT_RENDER_NEW, 1)
    else:
        # If formatting drifted, replace from the known project declaration up to
        # the next resume-binding block while preserving that following block.
        start = text.find('   const p=state.project||{};')
        end = text.find('   $$(["[data-resume]"])', start) if start >= 0 else -1
        if end < 0 and start >= 0:
            end = text.find('   $$("[data-resume]")', start)
        if start < 0 or end < 0:
            raise RuntimeError('V310 anchor missing: project render')
        text = text[:start] + PROJECT_RENDER_NEW + '\n' + text[end:]

    text = replace_once(text, LIVE_BOOT_OLD, LIVE_BOOT_NEW, 'live bottom placeholder')
    text = replace_once(text, LIVE_HANDLER_OLD, LIVE_HANDLER_NEW, 'live mini placeholder handler')
    return text


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HUB
    if not target.is_file():
        raise SystemExit(f'V310 Creator Hub target missing: {target}')
    before = target.read_text(encoding='utf-8')
    after = patch_hub_text(before)
    target.write_text(after, encoding='utf-8')
    print('V310 Creator Hub mobile cleanup applied:', target, 'changed=', after != before, flush=True)


if __name__ == '__main__':
    main()
