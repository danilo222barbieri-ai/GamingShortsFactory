#!/usr/bin/env python3
from pathlib import Path
import re,sys

MARK='V386_MOBILE_EDITOR_REFERENCE_LOCK'

EDITOR_PATCH=r'''
<!-- V386_MOBILE_EDITOR_REFERENCE_LOCK -->
<style id="v386MobileEditorReferenceLock">
@media(max-width:760px){
  html,body{width:100%!important;height:100%!important;margin:0!important;padding:0!important;overflow:hidden!important;background:transparent!important;overscroll-behavior:none!important}
  #ng27,#ng27.v326Mobile{
    --v386-player-w:min(74vw,272px,calc((100dvh - 164px) * 9 / 16));
    width:100%!important;height:100%!important;min-height:0!important;max-height:100%!important;
    margin:0!important;padding:4px 10px 6px!important;box-sizing:border-box!important;
    overflow:hidden!important;background:radial-gradient(circle at 50% 8%,rgba(205,239,252,.88),transparent 35%),linear-gradient(180deg,#fbfdff,#eef8fd)!important;
  }
  #ng27 .shell,#ng27.v326Mobile .shell{
    width:100%!important;height:100%!important;min-height:0!important;max-width:430px!important;
    margin:0 auto!important;padding:0!important;display:block!important;overflow:hidden!important;background:transparent!important;
  }
  #ng27 .topline,#ng27.v326Mobile .topline{display:none!important}
  #ng27 .cockpit,#ng27.expanded .cockpit,#ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{
    width:100%!important;height:100%!important;min-height:0!important;max-width:430px!important;
    margin:0 auto!important;padding:0!important;display:grid!important;grid-template-columns:1fr!important;
    grid-template-rows:minmax(0,1fr) 46px 94px!important;gap:8px!important;
    align-items:center!important;align-content:stretch!important;justify-items:center!important;overflow:hidden!important;
  }
  #ng27 .stageWrap,#ng27.v326Mobile .stageWrap{
    grid-row:1!important;grid-column:1!important;position:relative!important;
    width:var(--v386-player-w)!important;max-width:74vw!important;height:auto!important;min-height:0!important;
    margin:0!important;padding:0!important;align-self:center!important;justify-self:center!important;overflow:visible!important;
  }
  #ng27 .stage.r916,#ng27.expanded .stage.r916,#ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{
    position:relative!important;width:100%!important;height:auto!important;max-width:none!important;max-height:none!important;
    aspect-ratio:9/16!important;margin:0!important;border-radius:22px!important;overflow:hidden!important;
    border:1px solid rgba(79,194,235,.68)!important;background:linear-gradient(180deg,#dff5fd,#f8fcff)!important;
    box-shadow:0 10px 26px rgba(45,104,148,.15),0 0 0 4px rgba(255,255,255,.58)!important;
  }
  #ng27 .stage video,#ng27.v326Mobile .stage video{width:100%!important;height:100%!important;object-fit:cover!important}

  /* V386_TOOLS_INSIDE_PLAYER */
  #ng27 .v326ToolDock,#ng27.v326Mobile .v326ToolDock{position:absolute!important;z-index:115!important;display:flex!important;flex-direction:column!important;gap:7px!important;transform:translateY(-50%)!important;pointer-events:none!important}
  #ng27 .v326LeftDock,#ng27.v326Mobile .v326LeftDock{left:7px!important;top:46%!important}
  #ng27 .v326RightDock,#ng27.v326Mobile .v326RightDock{right:7px!important;top:47%!important}
  #ng27 .v326ToolDock .railBtn,#ng27.v326Mobile .v326ToolDock .railBtn{
    pointer-events:auto!important;width:44px!important;height:52px!important;min-width:44px!important;min-height:52px!important;
    margin:0!important;padding:2px!important;border-radius:15px!important;border:1px solid rgba(255,255,255,.78)!important;
    background:linear-gradient(145deg,rgba(31,57,85,.82),rgba(65,89,115,.74))!important;color:#fff!important;
    box-shadow:0 6px 16px rgba(13,34,53,.18),inset 0 1px 0 rgba(255,255,255,.28)!important;
    -webkit-backdrop-filter:none!important;backdrop-filter:none!important;transition:none!important;animation:none!important;
  }
  #ng27 .v326ToolDock .railBtn .ico,#ng27.v326Mobile .v326ToolDock .railBtn .ico{width:18px!important;height:18px!important}
  #ng27 .v326ToolDock .railBtn span,#ng27.v326Mobile .v326ToolDock .railBtn span{font-size:6px!important;line-height:1!important;font-weight:950!important;color:#fff!important}
  #ng27 .v326Meta,#ng27.v326Mobile .v326Meta{top:8px!important;left:8px!important;right:8px!important}
  #ng27 .v326Time,#ng27 .v326Ratio,#ng27.v326Mobile .v326Time,#ng27.v326Mobile .v326Ratio{height:29px!important;padding:0 9px!important;border-radius:12px!important;font-size:8px!important;background:rgba(31,55,82,.82)!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
  #ng27 .v326Ratio,#ng27.v326Mobile .v326Ratio{margin-left:auto!important;margin-right:37px!important}
  #ng27 #zoomEditorBtn,#ng27.v326Mobile #zoomEditorBtn{display:flex!important;position:absolute!important;top:8px!important;right:8px!important;width:36px!important;min-width:36px!important;height:36px!important;min-height:36px!important;border-radius:12px!important;background:rgba(31,55,82,.82)!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important;transition:none!important;animation:none!important}
  #ng27 .v326PlaybackDock,#ng27.v326Mobile .v326PlaybackDock{position:absolute!important;left:50%!important;bottom:31px!important;transform:translateX(-50%)!important;gap:9px!important;z-index:116!important}
  #ng27 #playBtn,#ng27.v326Mobile #playBtn{width:50px!important;height:50px!important;min-width:50px!important;min-height:50px!important;transition:none!important;animation:none!important}
  #ng27 .v326Skip,#ng27.v326Mobile .v326Skip{width:25px!important;height:30px!important;font-size:19px!important}
  #ng27 .v380PlayerProgress,#ng27.v326Mobile .v380PlayerProgress{left:14px!important;right:14px!important;bottom:8px!important;font-size:6px!important}

  /* V386_ACTIONS_ROW_2 */
  #ng27 .cockpit>.v323EditorActions,#ng27.v326Mobile .cockpit>.v323EditorActions{
    grid-row:2!important;grid-column:1!important;width:min(88vw,352px)!important;max-width:352px!important;height:46px!important;min-height:46px!important;
    margin:0!important;padding:0!important;display:grid!important;grid-template-columns:1.12fr 1fr!important;gap:8px!important;justify-self:center!important;
  }
  #ng27 .v323EditorAction,#ng27.v326Mobile .v323EditorAction{height:46px!important;min-height:46px!important;padding:4px 8px!important;border-radius:16px!important;font-size:8.2px!important;font-weight:950!important;box-shadow:0 6px 15px rgba(64,108,150,.08)!important}
  #ng27 .v323EditorAction.primary,#ng27.v326Mobile .v323EditorAction.primary{background:linear-gradient(135deg,#55c6fb,#287fee)!important}

  /* V386_TIMELINE_ROW_3 */
  #ng27 .cockpit>.timeline,#ng27.v326Mobile .cockpit>.timeline{
    grid-row:3!important;grid-column:1!important;width:min(88vw,352px)!important;max-width:352px!important;height:94px!important;min-height:94px!important;
    margin:0!important;padding:7px 9px 6px!important;border-radius:17px!important;overflow:hidden!important;justify-self:center!important;
    background:rgba(255,255,255,.94)!important;border:1px solid rgba(151,187,216,.25)!important;box-shadow:0 7px 19px rgba(79,118,157,.08)!important;
    -webkit-backdrop-filter:none!important;backdrop-filter:none!important;
  }
  #ng27 .timeline .tlMeta,#ng27.v326Mobile .timeline .tlMeta{margin:0 2px 5px!important;font-size:6.8px!important}
  #ng27 .timeline .tlMeta span:nth-child(2),#ng27.v326Mobile .timeline .tlMeta span:nth-child(2){min-height:22px!important;padding:0 8px!important;border-radius:12px!important}
  #ng27 .timeline .track,#ng27.v326Mobile .timeline .track{height:35px!important;border-radius:10px!important;border:1.5px solid rgba(69,174,228,.70)!important}
  #ng27 .timeline .trimRow,#ng27.v326Mobile .timeline .trimRow{margin-top:3px!important;font-size:6.2px!important}

  /* Stable first paint: no compositing animation or blur around the live video. */
  #ng27,#ng27 .shell,#ng27 .cockpit,#ng27 .stageWrap,#ng27 .stage,#ng27 video,#ng27 #videoBg,#ng27 .timeline,#ng27 .v323EditorActions{transition:none!important;animation:none!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
  #ng27 video,#ng27 #videoBg{-webkit-backface-visibility:hidden!important;backface-visibility:hidden!important;transform:translateZ(0)!important}

  /* FULL is the editing workspace: viewport video + side tools only. */
  #ng27.gsfFullscreen,#ng27.gsfFullscreenFallback,#ng27:fullscreen,#ng27:-webkit-full-screen,
  #ng27.gsfFullscreen .shell,#ng27.gsfFullscreenFallback .shell,#ng27:fullscreen .shell,#ng27:-webkit-full-screen .shell,
  #ng27.gsfFullscreen .cockpit,#ng27.gsfFullscreenFallback .cockpit,#ng27:fullscreen .cockpit,#ng27:-webkit-full-screen .cockpit,
  #ng27.gsfFullscreen .stageWrap,#ng27.gsfFullscreenFallback .stageWrap,#ng27:fullscreen .stageWrap,#ng27:-webkit-full-screen .stageWrap,
  #ng27.gsfFullscreen .stage.r916,#ng27.gsfFullscreenFallback .stage.r916,#ng27:fullscreen .stage.r916,#ng27:-webkit-full-screen .stage.r916{
    position:fixed!important;inset:0!important;width:100vw!important;height:100dvh!important;min-width:100vw!important;min-height:100dvh!important;max-width:none!important;max-height:none!important;
    margin:0!important;padding:0!important;border:0!important;border-radius:0!important;background:#07131d!important;z-index:2147483647!important;overflow:hidden!important;
  }
  #ng27.gsfFullscreen .stage.r916 video,#ng27.gsfFullscreenFallback .stage.r916 video,#ng27:fullscreen .stage.r916 video,#ng27:-webkit-full-screen .stage.r916 video{width:100vw!important;height:100dvh!important;object-fit:cover!important}
  #ng27.gsfFullscreen .timeline,#ng27.gsfFullscreenFallback .timeline,#ng27:fullscreen .timeline,#ng27:-webkit-full-screen .timeline,
  #ng27.gsfFullscreen .v323EditorActions,#ng27.gsfFullscreenFallback .v323EditorActions,#ng27:fullscreen .v323EditorActions,#ng27:-webkit-full-screen .v323EditorActions{display:none!important}
  #ng27.gsfFullscreen .v326ToolDock,#ng27.gsfFullscreenFallback .v326ToolDock,#ng27:fullscreen .v326ToolDock,#ng27:-webkit-full-screen .v326ToolDock{position:fixed!important;top:50%!important;transform:translateY(-50%)!important;display:flex!important;visibility:visible!important;opacity:1!important;z-index:2147483647!important}
  #ng27.gsfFullscreen .v326LeftDock,#ng27.gsfFullscreenFallback .v326LeftDock,#ng27:fullscreen .v326LeftDock,#ng27:-webkit-full-screen .v326LeftDock{left:max(10px,env(safe-area-inset-left))!important}
  #ng27.gsfFullscreen .v326RightDock,#ng27.gsfFullscreenFallback .v326RightDock,#ng27:fullscreen .v326RightDock,#ng27:-webkit-full-screen .v326RightDock{right:max(10px,env(safe-area-inset-right))!important}
  #ng27.gsfFullscreen .v326PlaybackDock,#ng27.gsfFullscreenFallback .v326PlaybackDock,#ng27:fullscreen .v326PlaybackDock,#ng27:-webkit-full-screen .v326PlaybackDock{position:fixed!important;bottom:max(24px,env(safe-area-inset-bottom))!important;z-index:2147483647!important}
  #ng27.gsfFullscreen .v380PlayerProgress,#ng27.gsfFullscreenFallback .v380PlayerProgress,#ng27:fullscreen .v380PlayerProgress,#ng27:-webkit-full-screen .v380PlayerProgress{position:fixed!important;left:74px!important;right:74px!important;bottom:max(8px,env(safe-area-inset-bottom))!important;z-index:2147483647!important}
}
</style>
<script id="v386MobileEditorReferenceRuntime">
(()=>{
  const root=document.getElementById('ng27');if(!root)return;
  /* V386_FULLSCREEN_PARENT_CLEAN */
  const saved=new Map();
  const selectors=['#gsf-global-header','.gsf-global-header','#gsf-game-bar','.gsf-game-bar','.gsf-shell-gamebar','[data-gsf-gamebar]','.gsf-editor-head'];
  const docs=()=>{const a=[];for(const w of [window.parent,window.top]){try{if(w&&w.document&&!a.includes(w.document))a.push(w.document)}catch(_e){}}return a};
  const isFull=()=>root.classList.contains('gsfFullscreen')||root.classList.contains('gsfFullscreenFallback')||document.fullscreenElement===root||document.webkitFullscreenElement===root;
  const cleanParent=()=>{
    const full=isFull();
    for(const d of docs())for(const sel of selectors)d.querySelectorAll(sel).forEach(el=>{
      if(full){if(!saved.has(el))saved.set(el,el.style.display);el.style.setProperty('display','none','important')}
      else if(saved.has(el)){el.style.display=saved.get(el)||'';saved.delete(el)}
    });
    try{const f=window.frameElement;if(f){if(full){f.style.setProperty('position','fixed','important');f.style.setProperty('inset','0','important');f.style.setProperty('width','100vw','important');f.style.setProperty('height','100dvh','important');f.style.setProperty('z-index','2147483647','important')}else{for(const k of ['position','inset','width','height','z-index'])f.style.removeProperty(k)}}}catch(_e){}
  };
  try{new MutationObserver(cleanParent).observe(root,{attributes:true,attributeFilter:['class']})}catch(_e){}
  document.addEventListener('fullscreenchange',cleanParent);document.addEventListener('webkitfullscreenchange',cleanParent);cleanParent();
})();
</script>
'''

SHELL_PATCH=r'''
<style id="v386EditorParentReference">
@media(max-width:760px){
  /* V386_EDITOR_TITLE_CARD */
  #gsf-editor-overlay-v220.is-open{display:flex!important;flex-direction:column!important;overflow:hidden!important}
  #gsf-editor-overlay-v220 .gsf-editor-head{
    display:flex!important;visibility:visible!important;opacity:1!important;position:relative!important;align-items:center!important;
    flex:0 0 60px!important;height:60px!important;min-height:60px!important;margin:6px 12px 6px!important;padding:9px 84px 9px 14px!important;
    border-radius:19px!important;background:rgba(255,255,255,.97)!important;border:1px solid rgba(174,204,225,.30)!important;
    box-shadow:0 7px 20px rgba(65,110,151,.08)!important;color:#103A79!important;z-index:20!important;
    -webkit-backdrop-filter:none!important;backdrop-filter:none!important;transition:none!important;animation:none!important;
  }
  #gsf-editor-overlay-v220 .gsf-editor-head>div{font-size:19px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.02em!important}
  #gsf-editor-overlay-v220 .gsf-editor-head small{display:block!important;margin-top:5px!important;font-size:9.5px!important;line-height:1.1!important;font-weight:700!important;color:#6e81a5!important}
  #gsf-editor-overlay-v220 .v326HeaderFull{display:flex!important;visibility:visible!important;opacity:1!important;align-items:center!important;justify-content:center!important;position:absolute!important;right:10px!important;top:10px!important;width:68px!important;min-width:68px!important;height:40px!important;border-radius:14px!important;padding:0 8px!important;background:#f8fbff!important;color:#294e85!important;border:1px solid rgba(156,190,218,.30)!important;box-shadow:0 5px 14px rgba(64,104,143,.08)!important;font-size:9px!important;font-weight:950!important}
  #gsf-editor-overlay-v220 iframe.gsf-editor-frame,#gsf-editor-overlay-v220 iframe[title="Game Editor"]{display:block!important;flex:1 1 auto!important;width:100%!important;height:auto!important;min-height:0!important;max-height:none!important;border:0!important;background:transparent!important;transform:translateZ(0)!important;transition:none!important;animation:none!important}
}
</style>
<script id="V386_HIDE_DUPLICATE_FINAL_CTA">
(()=>{
  const seen=new WeakSet();
  const docs=()=>{const out=[];for(const w of [window,window.parent,window.top]){try{if(w&&w.document&&!out.includes(w.document))out.push(w.document)}catch(_e){}}return out};
  const cleanDoc=(d)=>{
    d.querySelectorAll('button,a,[role="button"],div').forEach(el=>{
      const t=String(el.textContent||'').replace(/\s+/g,' ').trim().toUpperCase();
      if(t.length<80&&t.includes('HAI FINITO')&&t.includes('CREA IL TUO SHORT')){
        const x=el.closest('button,a,[role="button"]')||el;
        x.style.setProperty('display','none','important');x.setAttribute('data-v386-hidden-final-cta','1');
      }
    });
  };
  const clean=()=>docs().forEach(cleanDoc);clean();
  docs().forEach(d=>{try{if(d.body&&!seen.has(d.body)){seen.add(d.body);new MutationObserver(clean).observe(d.body,{childList:true,subtree:true})}}catch(_e){}});
})();
</script>
'''

def strip_old_editor(t:str)->str:
    patterns=[
      r'\s*<!-- V381_MOBILE_EDITOR_COMPACT_FULL -->.*?</style>\s*',
      r'\s*<!-- V382_MOBILE_EDITOR_TRUE_FULL -->.*?<script id="v382MobileEditorTrueFullRuntime">.*?</script>\s*',
      r'\s*<!-- V383_MOBILE_EDITOR_POSITION -->.*?</style>\s*',
      r'\s*<!-- V384_MOBILE_EDITOR_NO_SCROLL -->.*?<script id="v384MobileEditorNoScrollRuntime">.*?</script>\s*',
      r'\s*<!-- V385_MOBILE_EDITOR_LOWER -->.*?</style>\s*',
      r'\s*<!-- V386_MOBILE_EDITOR_REFERENCE_LOCK -->.*?<script id="v386MobileEditorReferenceRuntime">.*?</script>\s*',
    ]
    for p in patterns:t=re.sub(p,'\n',t,flags=re.S)
    # V326 used three first-paint geometry passes; one deterministic pass is enough and removes iOS flashing.
    t=t.replace('layout();requestAnimationFrame(layout);setTimeout(layout,80);','layout();')
    return t

def strip_old_shell(t:str)->str:
    patterns=[
      r'\s*<style id="v380EditorParentUnified">.*?<script id="V380_HIDE_DUPLICATE_FINAL_CTA">.*?</script>\s*',
      r'\s*<style id="v386EditorParentReference">.*?<script id="V386_HIDE_DUPLICATE_FINAL_CTA">.*?</script>\s*',
    ]
    for p in patterns:t=re.sub(p,'\n',t,flags=re.S)
    return t

def main():
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html';shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
    if not editor.is_file() or not shell.is_file():raise SystemExit('V386 runtime files missing')
    e=strip_old_editor(editor.read_text(encoding='utf-8'))
    if 'V380_MOBILE_EDITOR_UNIFIED' not in e:raise RuntimeError('V386 requires V380 base')
    e=e.replace('</body>',EDITOR_PATCH+'\n</body>',1);editor.write_text(e,encoding='utf-8')
    s=strip_old_shell(shell.read_text(encoding='utf-8'))
    marker='<style id="gsf-v220-editor-shell">'
    if marker not in s:raise RuntimeError('V386 parent Editor shell anchor missing')
    s=s.replace(marker,SHELL_PATCH+'\n'+marker,1)
    compile(s,str(shell),'exec');shell.write_text(s,encoding='utf-8')
    print('V386 mobile Editor reference lock applied',flush=True)
if __name__=='__main__':main()
