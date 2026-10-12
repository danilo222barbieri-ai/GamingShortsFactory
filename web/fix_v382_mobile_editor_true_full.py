#!/usr/bin/env python3
from pathlib import Path
import re,sys
MARK='V382_MOBILE_EDITOR_TRUE_FULL'
PATCH=r'''
<!-- V382_MOBILE_EDITOR_TRUE_FULL -->
<style id="v382MobileEditorTrueFull">
@media(max-width:760px){
/* Normal editor: every block follows the compact player instead of staying phone-wide. */
#ng27.v326Mobile .cockpit>.timeline{width:min(84vw,344px)!important;max-width:344px!important;justify-self:center!important}
#ng27.v326Mobile .cockpit>.v323EditorActions{width:min(84vw,344px)!important;max-width:344px!important;justify-self:center!important}
#ng27.v326Mobile .v323EditorAction{font-size:6.2px!important;padding:2px 4px!important}
/* Full means full: no letterbox, no shell geometry, video owns the viewport. */
#ng27.v326Mobile.gsfFullscreen,#ng27.v326Mobile:fullscreen,#ng27.v326Mobile:-webkit-full-screen,
#ng27.v326Mobile.gsfFullscreen .shell,#ng27.v326Mobile:fullscreen .shell,#ng27.v326Mobile:-webkit-full-screen .shell,
#ng27.v326Mobile.gsfFullscreen .cockpit,#ng27.v326Mobile:fullscreen .cockpit,#ng27.v326Mobile:-webkit-full-screen .cockpit,
#ng27.v326Mobile.gsfFullscreen .stageWrap,#ng27.v326Mobile:fullscreen .stageWrap,#ng27.v326Mobile:-webkit-full-screen .stageWrap,
#ng27.v326Mobile.gsfFullscreen .stage.r916,#ng27.v326Mobile:fullscreen .stage.r916,#ng27.v326Mobile:-webkit-full-screen .stage.r916{position:fixed!important;inset:0!important;width:100vw!important;height:100dvh!important;min-width:100vw!important;min-height:100dvh!important;max-width:none!important;max-height:none!important;margin:0!important;padding:0!important;border:0!important;border-radius:0!important;background:#08131c!important}
#ng27.v326Mobile.gsfFullscreen .stage.r916 video,#ng27.v326Mobile:fullscreen .stage.r916 video,#ng27.v326Mobile:-webkit-full-screen .stage.r916 video{width:100vw!important;height:100dvh!important;object-fit:cover!important}
#ng27.v326Mobile.gsfFullscreen .v326Time,#ng27.v326Mobile:fullscreen .v326Time,#ng27.v326Mobile:-webkit-full-screen .v326Time{position:fixed!important;top:max(12px,env(safe-area-inset-top))!important;left:max(12px,env(safe-area-inset-left))!important}
#ng27.v326Mobile.gsfFullscreen .v326Ratio,#ng27.v326Mobile:fullscreen .v326Ratio,#ng27.v326Mobile:-webkit-full-screen .v326Ratio{position:fixed!important;top:max(12px,env(safe-area-inset-top))!important;right:52px!important}
#ng27.v326Mobile.gsfFullscreen #zoomEditorBtn,#ng27.v326Mobile:fullscreen #zoomEditorBtn,#ng27.v326Mobile:-webkit-full-screen #zoomEditorBtn{position:fixed!important;top:max(10px,env(safe-area-inset-top))!important;right:max(10px,env(safe-area-inset-right))!important}
}
</style>
<script id="v382MobileEditorTrueFullRuntime">
(()=>{
 const root=document.getElementById('ng27'); if(!root)return;
 /* V382_FULL_HIDE_PARENT_CHROME */
 const chromeSelectors=['#gsf-global-header','.gsf-global-header','#gsf-game-bar','.gsf-game-bar','.gsf-shell-gamebar','header'];
 let hidden=[];
 function parentChrome(hide){
   try{
     const d=window.parent.document;
     if(hide){hidden=[];chromeSelectors.forEach(sel=>d.querySelectorAll(sel).forEach(el=>{if(hidden.some(x=>x.el===el))return;hidden.push({el,display:el.style.display});el.style.setProperty('display','none','important')}));}
     else{hidden.forEach(x=>{x.el.style.display=x.display||''});hidden=[];}
   }catch(_e){}
 }
 function sync(){const full=root.classList.contains('gsfFullscreen')||root.classList.contains('gsfFullscreenFallback')||document.fullscreenElement===root||document.webkitFullscreenElement===root;parentChrome(full);try{const f=window.frameElement;if(full&&f){f.style.setProperty('z-index','2147483647','important');f.style.setProperty('inset','0','important');f.style.setProperty('width','100vw','important');f.style.setProperty('height','100dvh','important')}}catch(_e){}}
 new MutationObserver(sync).observe(root,{attributes:true,attributeFilter:['class']});document.addEventListener('fullscreenchange',sync);document.addEventListener('webkitfullscreenchange',sync);sync();
})();
</script>
'''
def strip(t):return re.sub(r'\s*<!-- V382_MOBILE_EDITOR_TRUE_FULL -->.*?</script>\s*','\n',t,flags=re.S)
def main():
 root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app');p=root/'web'/'editor_2027_component'/'index.html';t=strip(p.read_text(encoding='utf-8'))
 if 'V381_MOBILE_EDITOR_COMPACT_FULL' not in t:raise RuntimeError('V382 requires V381')
 p.write_text(t.replace('</body>',PATCH+'\n</body>',1),encoding='utf-8');print('V382 true full + proportional compact Editor applied',flush=True)
if __name__=='__main__':main()
