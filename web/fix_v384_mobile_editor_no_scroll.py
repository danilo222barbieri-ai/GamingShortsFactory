#!/usr/bin/env python3
from pathlib import Path
import re,sys
MARK='V384_MOBILE_EDITOR_NO_SCROLL'
PATCH=r'''
<!-- V384_MOBILE_EDITOR_NO_SCROLL -->
<style id="v384MobileEditorNoScroll">
@media(max-width:760px){
/* Normal mode must fit between the global header and Game Bar: zero Editor-page scrolling. */
html,body{height:100%!important;overflow:hidden!important}
#ng27.v326Mobile{--v384-player-h:min(48dvh,390px);height:calc(100dvh - 154px)!important;min-height:0!important;max-height:calc(100dvh - 154px)!important;overflow:hidden!important;padding:4px 10px 6px!important;box-sizing:border-box!important}
#ng27.v326Mobile .shell{height:100%!important;min-height:0!important;overflow:hidden!important;display:flex!important;align-items:flex-start!important;justify-content:center!important}
#ng27.v326Mobile .cockpit,#ng27.v326Mobile.expanded .cockpit{display:grid!important;grid-template-columns:1fr!important;grid-template-rows:var(--v384-player-h) 82px 42px!important;gap:7px!important;width:100%!important;max-width:430px!important;height:auto!important;min-height:0!important;margin:0 auto!important;padding:0!important;align-content:start!important}
#ng27.v326Mobile .stageWrap{grid-row:1!important;width:calc(var(--v384-player-h) * 9 / 16)!important;max-width:74vw!important;height:var(--v384-player-h)!important;justify-self:center!important;margin:0!important}
#ng27.v326Mobile .stage.r916,#ng27.v326Mobile.expanded .stage.r916{width:100%!important;height:100%!important;aspect-ratio:9/16!important;max-height:none!important;border-radius:18px!important;margin:0!important}
/* Controls stay around the compact player; full mode is where editing gets room. */
#ng27.v326Mobile .v326ToolDock{gap:4px!important}
#ng27.v326Mobile .v326ToolDock .railBtn{width:34px!important;height:39px!important;min-width:34px!important;min-height:39px!important;border-radius:11px!important;padding:2px!important}
#ng27.v326Mobile .v326ToolDock .railBtn .ico{width:14px!important;height:14px!important}
#ng27.v326Mobile .v326ToolDock .railBtn span{font-size:4.8px!important}
#ng27.v326Mobile .v326LeftDock{left:5px!important;top:24%!important}
#ng27.v326Mobile .v326RightDock{right:5px!important;top:34%!important}
#ng27.v326Mobile .cockpit>.timeline{grid-row:2!important;width:min(88vw,370px)!important;max-width:370px!important;height:82px!important;min-height:82px!important;padding:5px 7px!important;justify-self:center!important;margin:0!important;border-radius:13px!important}
#ng27.v326Mobile .timeline .track{height:27px!important}
#ng27.v326Mobile .timeline .tlMeta{margin-bottom:3px!important;font-size:5.7px!important}
#ng27.v326Mobile .timeline .trimRow{margin-top:2px!important;font-size:5.3px!important}
#ng27.v326Mobile .cockpit>.v323EditorActions{grid-row:3!important;width:min(88vw,370px)!important;max-width:370px!important;height:42px!important;min-height:42px!important;justify-self:center!important;margin:0!important;gap:7px!important}
#ng27.v326Mobile .v323EditorAction{height:42px!important;min-height:42px!important;font-size:7.4px!important;padding:3px 6px!important;border-radius:14px!important}
/* Full editor: tools remain available; timeline/actions disappear and the parent Game Bar must not cover the canvas. */
#ng27.v326Mobile.gsfFullscreenFallback .v326ToolDock,#ng27.v326Mobile.gsfFullscreen .v326ToolDock,#ng27.v326Mobile:fullscreen .v326ToolDock,#ng27.v326Mobile:-webkit-full-screen .v326ToolDock{display:flex!important;visibility:visible!important;opacity:1!important}
}
</style>
<script id="v384MobileEditorNoScrollRuntime">
(()=>{
 const root=document.getElementById('ng27');if(!root)return;
 /* V384_HIDE_PARENT_GAMEBAR_FULL */
 const selectors=['#gsf-game-bar','.gsf-game-bar','.gsf-shell-gamebar','[data-gsf-gamebar]'];let saved=[];
 const isFull=()=>root.classList.contains('gsfFullscreen')||root.classList.contains('gsfFullscreenFallback')||document.fullscreenElement===root||document.webkitFullscreenElement===root;
 function sync(){
  try{const d=window.parent.document;if(isFull()){if(saved.length)return;selectors.forEach(sel=>d.querySelectorAll(sel).forEach(el=>{if(saved.some(x=>x.el===el))return;saved.push({el,display:el.style.display});el.style.setProperty('display','none','important')}));}else{saved.forEach(x=>x.el.style.display=x.display||'');saved=[];}}catch(_e){}
 }
 new MutationObserver(sync).observe(root,{attributes:true,attributeFilter:['class']});document.addEventListener('fullscreenchange',sync);document.addEventListener('webkitfullscreenchange',sync);sync();
})();
</script>
'''
def strip(t):return re.sub(r'\s*<!-- V384_MOBILE_EDITOR_NO_SCROLL -->.*?</script>\s*','\n',t,flags=re.S)
def main():
 root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app');p=root/'web'/'editor_2027_component'/'index.html';t=strip(p.read_text(encoding='utf-8'))
 if 'V383_MOBILE_EDITOR_POSITION' not in t:raise RuntimeError('V384 requires V383')
 p.write_text(t.replace('</body>',PATCH+'\n</body>',1),encoding='utf-8');print('V384 no-scroll mobile Editor applied',flush=True)
if __name__=='__main__':main()
