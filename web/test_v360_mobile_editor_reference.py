#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FIX = HERE / 'fix_v360_mobile_editor_reference.py'
START = HERE / 'start_web.sh'

FIXTURE = '''<!doctype html><html><head></head><body>
<div id="ng27" class="v326Mobile">
<style id="v326MobileEditorExact">/* V326 */</style>
<div class="shell">
  <div class="cockpit">
    <div class="stageWrap"><div class="stage r916" id="stage">
      <video id="video"></video><video id="videoBg"></video>
      <button id="zoomEditorBtn"><svg class="ico"></svg><span>FULL</span></button>
      <div class="v326ToolDock v326LeftDock">
        <button class="railBtn" data-panel="frame"><span>FRAME</span></button>
        <button class="railBtn" data-panel="caption"><span>CAPTION</span></button>
        <button class="railBtn" data-panel="look"><span>LOOK</span></button>
      </div>
      <div class="v326ToolDock v326RightDock">
        <button class="railBtn" data-panel="audio"><span>AUDIO</span></button>
        <button class="railBtn" data-panel="vision"><span>AI</span></button>
      </div>
      <div class="v325PlayerMeta"><span class="v325RatioChip">9:16</span></div>
      <div class="v326Meta"><span class="v326Time">00:07 / 00:15</span><span class="v326Ratio">9:16</span></div>
      <div class="v325PlaybackDock"></div>
      <div class="v326PlaybackDock"><button class="v326Skip">‹</button><button id="playBtn">PLAY</button><button class="v326Skip">›</button></div>
    </div></div>
    <div class="v323EditorActions" id="v323EditorActions"><button class="v323EditorAction primary" id="v323CreateShort">CREA SHORT</button><button class="v323EditorAction secondary" id="v323SaveDraft">SALVA LA TUA BOZZA</button></div>
    <div class="timeline"><div class="tlMeta"><span>IN 00:00.0</span><span>Caption AUTO</span><span>OUT 00:15.0</span></div><div class="track"></div><div class="trimRow">00:00 00:05 00:10 00:15</div></div>
  </div>
  <div class="drawer">ZOOM LUMINOSITA CONTRASTO VOLUME VELOCITA RESET CHIUDI SAFE ZONE HOOK SUBTITLES GAME VISION</div>
</div>
</div>
<script>
const SET_FRAME_HEIGHT="streamlit:setFrameHeight";
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
let hostVideoUrl="";
const video=document.getElementById('video');
window.setTimeout(()=>{
  if(!hostVideoUrl){
    hostVideoUrl='/editor-media/current?ts='+Date.now();
    video.src=hostVideoUrl;
    video.preload='auto';
    video.load();
  }
},80);
</script>
</body></html>'''

with tempfile.TemporaryDirectory() as td:
    target = Path(td) / 'index.html'
    target.write_text(FIXTURE, encoding='utf-8')
    subprocess.run([sys.executable, str(FIX), str(target)], check=True)
    out = target.read_text(encoding='utf-8')

    required = [
        'V360_MOBILE_EDITOR_REFERENCE',
        'GSF_V361_EDITOR_REPAIR',
        'GSF_V364_EDITOR_STABLE_NOSCROLL',
        'v360MobileEditorReference',
        'overflow:hidden!important',
        'overscroll-behavior:none!important',
        'width:clamp(188px,52vw,200px)!important',
        'grid-template-rows:minmax(0,1fr) auto auto!important',
        '.v325PlayerMeta{display:none!important}',
        '.v325PlaybackDock{display:none!important}',
        '#zoomEditorBtn{',
        'display:flex!important;position:absolute!important',
        'opacity:1!important;pointer-events:auto!important',
        '.v326Ratio{margin-left:auto!important;margin-right:40px!important}',
        'width:40px!important;height:48px!important',
        'height:40px!important;min-height:40px!important',
        '.track{height:28px!important}',
        'lastSentFrameHeight',
        'Math.abs(h-lastSentFrameHeight)<3',
        'screen.height',
        '},900);',
        "hostVideoUrl='/editor-media/current';",
        'transition:none!important',
        'FRAME', 'CAPTION', 'LOOK', 'AUDIO', 'AI',
        'CREA SHORT', 'SALVA LA TUA BOZZA',
        'IN 00:00.0', 'OUT 00:15.0',
        'ZOOM', 'LUMINOSITA', 'CONTRASTO', 'VOLUME', 'VELOCITA',
        'RESET', 'CHIUDI', 'SAFE ZONE', 'HOOK', 'SUBTITLES', 'GAME VISION',
    ]
    for token in required:
        assert token in out, f'missing V364 Editor contract token: {token}'

    # Flicker regression: V360 must not create resize/mutation feedback loops.
    patch = out[out.index('V360_MOBILE_EDITOR_REFERENCE'):]
    assert 'ResizeObserver' not in patch
    assert 'MutationObserver' not in patch
    assert 'v360FitLayout' not in patch
    assert 'requestAnimationFrame' not in patch
    assert 'document.documentElement.scrollHeight' not in out
    assert "?ts='+Date.now()" not in out

    # Existing functional controls are reused exactly once.
    for panel in ('frame','caption','look','audio','vision'):
        assert out.count(f'data-panel="{panel}"') == 1, f'Editor duplicated {panel} control'
    assert out.count('id="v323CreateShort"') == 1
    assert out.count('id="v323SaveDraft"') == 1
    assert 'cloneNode(' not in patch
    assert out.count('class="v326Ratio"') == 1
    assert out.count('class="v325RatioChip"') == 1

    once = out
    subprocess.run([sys.executable, str(FIX), str(target)], check=True)
    assert target.read_text(encoding='utf-8') == once, 'V360/V364 patch must be restart-safe'

start = START.read_text(encoding='utf-8')
assert 'fix_v360_mobile_editor_reference.py' in start
assert 'test_v360_mobile_editor_reference.py' in start
assert start.index('fix_v326_mobile_editor_home_speed.py') < start.index('fix_v360_mobile_editor_reference.py')

print('V364 EDITOR COMPACT NO-SCROLL STABILITY: PASS', flush=True)
