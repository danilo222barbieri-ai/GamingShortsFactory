#!/usr/bin/env python3
from pathlib import Path
import importlib.util

HERE=Path(__file__).resolve().parent
FIX=HERE/'fix_v364_editor_stable_reference.py'
assert FIX.exists(), 'V364 fixer missing'

spec=importlib.util.spec_from_file_location('v364fix', FIX)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FIXTURE='''<!doctype html><html><head></head><body>
<div id="ng27" class="v326Mobile">
<style id="v326MobileEditorExact">/* existing V326 */</style>
<div class="shell"><div class="cockpit">
<div class="stageWrap"><div class="stage r916" id="stage">
<video id="video"></video><video id="videoBg"></video>
<button id="zoomEditorBtn"><span>FULL</span></button>
<div class="v325PlayerMeta"><span class="v325RatioChip">9:16</span></div>
<div class="v326Meta"><span class="v326Time">00:00 / 00:15</span><span class="v326Ratio">9:16</span></div>
<div class="v325PlaybackDock"></div><div class="v326PlaybackDock"><button id="playBtn">PLAY</button></div>
<div class="v326ToolDock v326LeftDock"><button data-panel="frame">FRAME</button><button data-panel="caption">CAPTION</button><button data-panel="look">LOOK</button></div>
<div class="v326ToolDock v326RightDock"><button data-panel="audio">AUDIO</button><button data-panel="vision">AI</button></div>
</div></div>
<div id="v323EditorActions" class="v323EditorActions"><button id="v323CreateShort">CREA SHORT</button><button id="v323SaveDraft">SALVA LA TUA BOZZA</button></div>
<div class="timeline"><div class="track"></div></div>
</div></div></div>
<script>
const SET_FRAME_HEIGHT='streamlit:setFrameHeight';
function sendMessage(type,data){}
function setFrameHeight(height){
  const h=Math.max(320,Number(height)||720);
  sendMessage(SET_FRAME_HEIGHT,{height:h});
}
function fitEditorViewport(){
  try{
    const pw=Math.max(320,Number(window.parent.innerWidth||window.innerWidth||1920));
    if(pw<=820){setFrameHeight(Math.max(720,Math.ceil(document.documentElement.scrollHeight||720)));return}
    const ph=Math.max(600,Number(window.parent.innerHeight||window.innerHeight||900));
    setFrameHeight(Math.max(600,Math.min(1080,Math.floor(ph))));
  }catch(e){setFrameHeight(900)}
}
window.addEventListener("resize",()=>{clearTimeout(fitEditorViewport.t);fitEditorViewport.t=setTimeout(fitEditorViewport,80)});
let hostVideoUrl='';
window.setTimeout(()=>{
  if(!hostVideoUrl){
    hostVideoUrl='/editor-media/current?ts='+Date.now();
  }
},80);
</script>
</body></html>'''

out=mod.patch_text(FIXTURE)
assert 'V364_EDITOR_STABLE_REFERENCE' in out
assert 'v364EditorStableReference' in out
assert 'clamp(220px,66vw,286px)' in out
assert '.v325PlayerMeta{display:none!important}' in out
assert '.v325PlaybackDock{display:none!important}' in out
assert '#zoomEditorBtn' in out and '.v326PlaybackDock' in out
assert 'data-panel="frame"' in out and 'data-panel="caption"' in out and 'data-panel="look"' in out
assert 'data-panel="audio"' in out and 'data-panel="vision"' in out
assert out.count('id="v323CreateShort"') == 1
assert out.count('id="v323SaveDraft"') == 1
assert 'ResizeObserver' not in out[out.index('V364_EDITOR_STABLE_REFERENCE'):]
assert 'MutationObserver' not in out[out.index('V364_EDITOR_STABLE_REFERENCE'):]
assert 'document.documentElement.scrollHeight' not in out
assert "?ts='+Date.now()" not in out
assert 'window.setTimeout(()=>{' in out and '},900);' in out
assert 'lastSentFrameHeight' in out
assert 'Math.abs(h-lastSentFrameHeight)<3' in out
assert 'screen.height' in out
assert 'transition:none!important' in out
for panel in ('frame','caption','look','audio','vision'):
    assert out.count(f'data-panel="{panel}"') == 1
assert mod.patch_text(out) == out
print('V364 EDITOR STABLE REFERENCE: PASS')
