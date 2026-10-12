#!/usr/bin/env python3
from pathlib import Path
import re,sys
MARK='V387_MOBILE_EDITOR_DEMO_LOCK'
EDITOR_PATCH=r'''
<!-- V387_MOBILE_EDITOR_DEMO_LOCK -->
<style id="v387MobileEditorDemoLock">
@media(max-width:760px){
 html,body{width:100%!important;height:100%!important;margin:0!important;padding:0!important;overflow:hidden!important;background:transparent!important}
 #ng27,#ng27.v326Mobile{--v387-player-h:clamp(350px,52dvh,470px);--v387-player-w:calc(var(--v387-player-h) * .5625);width:100%!important;height:100%!important;min-height:0!important;margin:0!important;padding:6px 10px 8px!important;overflow:hidden!important;background:linear-gradient(180deg,#f9fdff,#eef8fd)!important}
 #ng27 .shell,#ng27.v326Mobile .shell{width:100%!important;height:100%!important;max-width:430px!important;margin:0 auto!important;padding:0!important;display:flex!important;align-items:center!important;justify-content:center!important;overflow:hidden!important;background:transparent!important}
 #ng27 .topline,#ng27.v326Mobile .topline{display:none!important}
 #ng27 .cockpit,#ng27.expanded .cockpit,#ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{width:100%!important;height:auto!important;max-width:430px!important;margin:0 auto!important;padding:0!important;display:grid!important;grid-template-columns:1fr!important;grid-template-rows:auto 48px 108px!important;gap:8px!important;align-items:start!important;justify-items:center!important;overflow:visible!important}
 #ng27 .stageWrap,#ng27.v326Mobile .stageWrap{grid-row:1!important;grid-column:1!important;position:relative!important;width:var(--v387-player-w)!important;height:var(--v387-player-h)!important;max-width:none!important;margin:0!important;padding:0!important;justify-self:center!important;overflow:visible!important}
 #ng27 .stage.r916,#ng27.expanded .stage.r916,#ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{position:relative!important;width:100%!important;height:100%!important;aspect-ratio:9/16!important;margin:0!important;border-radius:24px!important;overflow:hidden!important;border:1px solid rgba(82,198,237,.62)!important;background:linear-gradient(180deg,#dff5fd,#f8fcff)!important;box-shadow:0 12px 28px rgba(59,114,154,.14),0 0 0 4px rgba(255,255,255,.64)!important}
 #ng27 .stage video,#ng27.v326Mobile .stage video{width:100%!important;height:100%!important;object-fit:cover!important;background:#dff4fb!important}
 /* V387_TOOLS_OVER_VIDEO */
 #ng27 .v326ToolDock,#ng27.v326Mobile .v326ToolDock{position:absolute!important;z-index:120!important;display:flex!important;flex-direction:column!important;gap:7px!important;top:50%!important;transform:translateY(-50%)!important;pointer-events:none!important}
 #ng27 .v326LeftDock,#ng27.v326Mobile .v326LeftDock{left:8px!important}
 #ng27 .v326RightDock,#ng27.v326Mobile .v326RightDock{right:8px!important}
 #ng27 .v326ToolDock .railBtn,#ng27.v326Mobile .v326ToolDock .railBtn{pointer-events:auto!important;width:48px!important;height:58px!important;min-width:48px!important;min-height:58px!important;margin:0!important;padding:3px!important;border-radius:16px!important;border:1px solid rgba(255,255,255,.82)!important;background:linear-gradient(145deg,rgba(40,66,92,.88),rgba(76,99,123,.78))!important;color:#fff!important;box-shadow:0 7px 18px rgba(20,44,64,.18)!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
 #ng27 .v326ToolDock .railBtn .ico,#ng27.v326Mobile .v326ToolDock .railBtn .ico{width:20px!important;height:20px!important}
 #ng27 .v326ToolDock .railBtn span,#ng27.v326Mobile .v326ToolDock .railBtn span{font-size:6.3px!important;line-height:1!important;font-weight:950!important;color:#fff!important}
 #ng27 button[data-panel="cover"],#ng27 button[data-panel="hud"],#ng27 #undoBtn,#ng27 #redoBtn,#ng27 #doneBtn{display:none!important}
 #ng27 .v326Meta,#ng27.v326Mobile .v326Meta{top:10px!important;left:10px!important;right:10px!important}
 #ng27 .v326Time,#ng27 .v326Ratio,#ng27.v326Mobile .v326Time,#ng27.v326Mobile .v326Ratio{height:30px!important;padding:0 9px!important;border-radius:12px!important;font-size:8px!important;background:rgba(36,61,87,.86)!important;color:#fff!important}
 #ng27 .v326Ratio,#ng27.v326Mobile .v326Ratio{margin-left:auto!important;margin-right:38px!important}
 #ng27 #zoomEditorBtn,#ng27.v326Mobile #zoomEditorBtn{display:flex!important;position:absolute!important;top:9px!important;right:9px!important;width:36px!important;height:36px!important;min-width:36px!important;border-radius:12px!important;background:rgba(36,61,87,.86)!important;color:#fff!important}
 #ng27 .v326PlaybackDock,#ng27.v326Mobile .v326PlaybackDock{position:absolute!important;left:50%!important;bottom:37px!important;transform:translateX(-50%)!important;gap:10px!important;z-index:121!important}
 #ng27 #playBtn,#ng27.v326Mobile #playBtn{width:56px!important;height:56px!important;min-width:56px!important;min-height:56px!important;border-radius:50%!important;background:linear-gradient(145deg,#56c8fb,#2b83ef)!important;color:#fff!important;box-shadow:0 8px 22px rgba(34,126,229,.28)!important}
 #ng27 .v326Skip,#ng27.v326Mobile .v326Skip{width:28px!important;height:32px!important;font-size:20px!important;color:#fff!important}
 #ng27 .v380PlayerProgress,#ng27.v326Mobile .v380PlayerProgress{left:16px!important;right:16px!important;bottom:10px!important;font-size:6.5px!important}
 /* V387_ACTIONS_COMPACT */
 #ng27 .cockpit>.v323EditorActions,#ng27.v326Mobile .cockpit>.v323EditorActions{grid-row:2!important;grid-column:1!important;width:min(90vw,370px)!important;height:48px!important;min-height:48px!important;margin:0!important;padding:0!important;display:grid!important;grid-template-columns:1.08fr 1fr!important;gap:8px!important;justify-self:center!important}
 #ng27 .v323EditorAction,#ng27.v326Mobile .v323EditorAction{height:48px!important;min-height:48px!important;padding:4px 9px!important;border-radius:17px!important;font-size:8.3px!important;font-weight:950!important;box-shadow:0 7px 17px rgba(64,108,150,.08)!important}
 #ng27 .v323EditorAction.primary,#ng27.v326Mobile .v323EditorAction.primary{background:linear-gradient(135deg,#58c8fb,#2a82ef)!important}
 /* V387_TIMELINE_REFERENCE */
 #ng27 .cockpit>.timeline,#ng27.v326Mobile .cockpit>.timeline{grid-row:3!important;grid-column:1!important;position:relative!important;left:auto!important;bottom:auto!important;transform:none!important;width:min(90vw,370px)!important;height:108px!important;min-height:108px!important;margin:0!important;padding:8px 10px 7px!important;border-radius:18px!important;overflow:hidden!important;justify-self:center!important;background:rgba(255,255,255,.96)!important;border:1px solid rgba(151,187,216,.24)!important;box-shadow:0 8px 20px rgba(79,118,157,.08)!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
 #ng27 .timeline .tlMeta,#ng27.v326Mobile .timeline .tlMeta{margin:0 2px 6px!important;font-size:7px!important;color:#60789b!important}
 #ng27 .timeline .tlMeta span:nth-child(2),#ng27.v326Mobile .timeline .tlMeta span:nth-child(2){display:inline-flex!important;min-height:23px!important;padding:0 9px!important;align-items:center!important;border-radius:12px!important;background:#dff9f2!important;color:#2c866e!important}
 #ng27 .timeline .track,#ng27.v326Mobile .timeline .track{height:39px!important;border-radius:11px!important;border:1.5px solid rgba(69,174,228,.72)!important;background:repeating-linear-gradient(90deg,rgba(119,193,229,.22) 0 3px,transparent 3px 9px),linear-gradient(180deg,#e9f8ff,#dff2fb)!important}
 #ng27 .timeline .trimRow,#ng27.v326Mobile .timeline .trimRow{margin-top:4px!important;font-size:6.4px!important;color:#667b99!important}
 /* no flicker */
 #ng27,#ng27 *,#ng27 video{transition:none!important;animation:none!important}
 #ng27 video,#ng27 #videoBg{-webkit-backface-visibility:hidden!important;backface-visibility:hidden!important;transform:translateZ(0)!important}
 /* V387_FULLSCREEN_WORKSPACE */
 #ng27.gsfFullscreen,#ng27.gsfFullscreenFallback,#ng27:fullscreen,#ng27:-webkit-full-screen,#ng27.gsfFullscreen .shell,#ng27.gsfFullscreenFallback .shell,#ng27:fullscreen .shell,#ng27:-webkit-full-screen .shell,#ng27.gsfFullscreen .cockpit,#ng27.gsfFullscreenFallback .cockpit,#ng27:fullscreen .cockpit,#ng27:-webkit-full-screen .cockpit,#ng27.gsfFullscreen .stageWrap,#ng27.gsfFullscreenFallback .stageWrap,#ng27:fullscreen .stageWrap,#ng27:-webkit-full-screen .stageWrap,#ng27.gsfFullscreen .stage.r916,#ng27.gsfFullscreenFallback .stage.r916,#ng27:fullscreen .stage.r916,#ng27:-webkit-full-screen .stage.r916{position:fixed!important;inset:0!important;width:100vw!important;height:100dvh!important;min-width:100vw!important;min-height:100dvh!important;max-width:none!important;max-height:none!important;margin:0!important;padding:0!important;border:0!important;border-radius:0!important;background:#07131d!important;z-index:2147483647!important;overflow:hidden!important}
 #ng27.gsfFullscreen .stage.r916 video,#ng27.gsfFullscreenFallback .stage.r916 video,#ng27:fullscreen .stage.r916 video,#ng27:-webkit-full-screen .stage.r916 video{width:100vw!important;height:100dvh!important;object-fit:cover!important}
 #ng27.gsfFullscreen .timeline,#ng27.gsfFullscreenFallback .timeline,#ng27:fullscreen .timeline,#ng27:-webkit-full-screen .timeline,#ng27.gsfFullscreen .v323EditorActions,#ng27.gsfFullscreenFallback .v323EditorActions,#ng27:fullscreen .v323EditorActions,#ng27:-webkit-full-screen .v323EditorActions{display:none!important}
 #ng27.gsfFullscreen .v326ToolDock,#ng27.gsfFullscreenFallback .v326ToolDock,#ng27:fullscreen .v326ToolDock,#ng27:-webkit-full-screen .v326ToolDock{position:fixed!important;top:50%!important;transform:translateY(-50%)!important;display:flex!important;visibility:visible!important;opacity:1!important;z-index:2147483647!important}
 #ng27.gsfFullscreen .v326LeftDock,#ng27.gsfFullscreenFallback .v326LeftDock,#ng27:fullscreen .v326LeftDock,#ng27:-webkit-full-screen .v326LeftDock{left:max(10px,env(safe-area-inset-left))!important}
 #ng27.gsfFullscreen .v326RightDock,#ng27.gsfFullscreenFallback .v326RightDock,#ng27:fullscreen .v326RightDock,#ng27:-webkit-full-screen .v326RightDock{right:max(10px,env(safe-area-inset-right))!important}
 #ng27.gsfFullscreen .v326PlaybackDock,#ng27.gsfFullscreenFallback .v326PlaybackDock,#ng27:fullscreen .v326PlaybackDock,#ng27:-webkit-full-screen .v326PlaybackDock{position:fixed!important;bottom:max(25px,env(safe-area-inset-bottom))!important;z-index:2147483647!important}
 #ng27.gsfFullscreen .v380PlayerProgress,#ng27.gsfFullscreenFallback .v380PlayerProgress,#ng27:fullscreen .v380PlayerProgress,#ng27:-webkit-full-screen .v380PlayerProgress{position:fixed!important;left:76px!important;right:76px!important;bottom:max(8px,env(safe-area-inset-bottom))!important;z-index:2147483647!important}
}
</style>
<script id="v387MobileEditorDemoRuntime">
(()=>{
 const root=document.getElementById('ng27');if(!root)return;
 const ai=root.querySelector('[data-panel="vision"] span');if(ai)ai.textContent='AI';
 /* V387_FULLSCREEN_PARENT_CLEAN */
 const saved=new Map();
 const sels=['#gsf-global-header','.gsf-global-header','#gsf-game-bar','.gsf-game-bar','.gsf-shell-gamebar','[data-gsf-gamebar]','.gsf-editor-head'];
 const docs=()=>{const out=[];for(const w of [window.parent,window.top]){try{if(w&&w.document&&!out.includes(w.document))out.push(w.document)}catch(_e){}}return out};
 const full=()=>root.classList.contains('gsfFullscreen')||root.classList.contains('gsfFullscreenFallback')||document.fullscreenElement===root||document.webkitFullscreenElement===root;
 const clean=()=>{for(const d of docs())for(const sel of sels)d.querySelectorAll(sel).forEach(el=>{if(full()){if(!saved.has(el))saved.set(el,el.style.display);el.style.setProperty('display','none','important')}else if(saved.has(el)){el.style.display=saved.get(el)||'';saved.delete(el)}})};
 try{new MutationObserver(clean).observe(root,{attributes:true,attributeFilter:['class']})}catch(_e){}
 document.addEventListener('fullscreenchange',clean);document.addEventListener('webkitfullscreenchange',clean);clean();
})();
</script>
'''
SHELL_PATCH=r'''
<style id="v387EditorParentReference">
@media(max-width:760px){
 /* V387_EDITOR_TITLE_CARD */
 #gsf-editor-overlay-v220.is-open{display:flex!important;flex-direction:column!important;overflow:hidden!important}
 #gsf-editor-overlay-v220 .gsf-editor-head{display:flex!important;visibility:visible!important;opacity:1!important;position:relative!important;align-items:center!important;flex:0 0 66px!important;height:66px!important;min-height:66px!important;margin:6px 14px 7px!important;padding:10px 88px 10px 16px!important;border-radius:20px!important;background:rgba(255,255,255,.97)!important;border:1px solid rgba(174,204,225,.28)!important;box-shadow:0 8px 22px rgba(65,110,151,.08)!important;color:#103A79!important;z-index:20!important;transition:none!important;animation:none!important}
 #gsf-editor-overlay-v220 .gsf-editor-head>div{font-size:20px!important;line-height:1!important;font-weight:950!important;letter-spacing:-.02em!important}
 #gsf-editor-overlay-v220 .gsf-editor-head small{display:block!important;margin-top:5px!important;font-size:10px!important;line-height:1.1!important;font-weight:700!important;color:#6e81a5!important;white-space:nowrap!important}
 #gsf-editor-overlay-v220 .v326HeaderFull{display:flex!important;align-items:center!important;justify-content:center!important;position:absolute!important;right:10px!important;top:11px!important;width:72px!important;height:44px!important;border-radius:15px!important;background:#f8fbff!important;color:#294e85!important;border:1px solid rgba(156,190,218,.28)!important;box-shadow:0 5px 14px rgba(64,104,143,.08)!important;font-size:9px!important;font-weight:950!important}
 #gsf-editor-overlay-v220 iframe.gsf-editor-frame,#gsf-editor-overlay-v220 iframe[title="Game Editor"]{display:block!important;flex:1 1 auto!important;width:100%!important;height:calc(100% - 79px)!important;min-height:0!important;border:0!important;background:transparent!important;transition:none!important;animation:none!important}
}
</style>
<script id="V387_HIDE_OUTER_SHORT_CTA">
(()=>{
 const hide=()=>{
  for(const d of [document]){
   d.querySelectorAll('button,a,div').forEach(el=>{
    const t=String(el.textContent||'').replace(/\s+/g,' ').trim().toUpperCase();
    if(!t.includes('HAI FINITO')||!t.includes('CREA IL TUO SHORT'))return;
    const r=el.getBoundingClientRect?.();if(r&&r.height>0&&r.height<180&&r.width>180){el.style.setProperty('display','none','important');}
   });
  }
 };
 hide();try{new MutationObserver(hide).observe(document.body,{subtree:true,childList:true,characterData:true})}catch(_e){}
})();
</script>
'''
def strip_block(text,marker):
 return re.sub(r'\s*<!-- '+re.escape(marker)+r' -->.*?</script>\s*','\n',text,flags=re.S)
def strip_v386_editor(text):
 return re.sub(r'\s*<!-- V386_MOBILE_EDITOR_REFERENCE_LOCK -->.*?</script>\s*','\n',text,flags=re.S)
def strip_v386_shell(text):
 text=re.sub(r'\s*<style id="v386EditorParentReference">.*?</style>\s*','\n',text,flags=re.S)
 text=re.sub(r'\s*<script id="V386_HIDE_DUPLICATE_FINAL_CTA">.*?</script>\s*','\n',text,flags=re.S)
 return text
def main():
 root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
 editor=root/'web'/'editor_2027_component'/'index.html';shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
 e=strip_v386_editor(editor.read_text(encoding='utf-8'))
 e=re.sub(r'\s*<!-- V387_MOBILE_EDITOR_DEMO_LOCK -->.*?</script>\s*','\n',e,flags=re.S)
 if '</body>' not in e: raise RuntimeError('V387 editor body anchor missing')
 editor.write_text(e.replace('</body>',EDITOR_PATCH+'\n</body>',1),encoding='utf-8')
 s=strip_v386_shell(shell.read_text(encoding='utf-8'))
 s=re.sub(r'\s*<style id="v387EditorParentReference">.*?</style>\s*','\n',s,flags=re.S)
 s=re.sub(r'\s*<script id="V387_HIDE_OUTER_SHORT_CTA">.*?</script>\s*','\n',s,flags=re.S)
 marker='<style id="gsf-v220-editor-shell">'
 if marker not in s: raise RuntimeError('V387 parent editor shell anchor missing')
 s=s.replace(marker,SHELL_PATCH+'\n'+marker,1)
 compile(s,str(shell),'exec');shell.write_text(s,encoding='utf-8')
 print('V387 mobile Editor demo-reference lock applied',flush=True)
if __name__=='__main__': main()
