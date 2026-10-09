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
      <video id="video"></video>
      <button id="zoomEditorBtn"><svg></svg><span>FULL</span></button>
      <div class="v326ToolDock v326LeftDock">
        <button class="railBtn" data-panel="frame"><span>FRAME</span></button>
        <button class="railBtn" data-panel="caption"><span>CAPTION</span></button>
        <button class="railBtn" data-panel="look"><span>LOOK</span></button>
      </div>
      <div class="v326ToolDock v326RightDock">
        <button class="railBtn" data-panel="audio"><span>AUDIO</span></button>
        <button class="railBtn" data-panel="vision"><span>AI</span></button>
      </div>
      <div class="v326Meta"><span class="v326Time">00:07 / 00:15</span><span class="v326Ratio">9:16</span></div>
      <div class="v326PlaybackDock"><button class="v326Skip">‹</button><button id="playBtn">PLAY</button><button class="v326Skip">›</button></div>
    </div></div>
    <div class="v323EditorActions" id="v323EditorActions"><button id="v323CreateShort">CREA SHORT</button><button id="v323SaveDraft">SALVA LA TUA BOZZA</button></div>
    <div class="timeline"><div class="tlMeta"><span>IN 00:00.0</span><span>Caption AUTO</span><span>OUT 00:15.0</span></div><div class="track"></div><div class="trimRow">00:00 00:05 00:10 00:15</div></div>
  </div>
  <div class="drawer">ZOOM LUMINOSITA CONTRASTO VOLUME VELOCITA RESET CHIUDI SAFE ZONE HOOK SUBTITLES GAME VISION</div>
</div>
</div>
</body></html>'''

with tempfile.TemporaryDirectory() as td:
    target = Path(td) / 'index.html'
    target.write_text(FIXTURE, encoding='utf-8')
    if FIX.exists():
        subprocess.run([sys.executable, str(FIX), str(target)], check=True)
    out = target.read_text(encoding='utf-8')

required = [
    'V360_MOBILE_EDITOR_REFERENCE',
    'v360MobileEditorReference',
    'v360EditorHeader',
    'Game Editor',
    'Il tuo gameplay resta nel progetto mentre modifichi.',
    'v360FullProxy',
    'fullBtn.click()',
    '--v360-player-w:',
    'grid-template-rows:auto minmax(0,1fr)!important',
    'grid-template-rows:minmax(0,1fr) auto auto!important',
    'PLAYER -> ACTIONS -> TIMELINE',
    'v360FitLayout',
    'Math.max(4,',
    'requestAnimationFrame',
    'FRAME', 'CAPTION', 'LOOK', 'AUDIO', 'AI',
    'CREA SHORT', 'SALVA LA TUA BOZZA',
    'IN 00:00.0', 'OUT 00:15.0',
    'ZOOM', 'LUMINOSITA', 'CONTRASTO', 'VOLUME', 'VELOCITA',
    'RESET', 'CHIUDI', 'SAFE ZONE', 'HOOK', 'SUBTITLES', 'GAME VISION',
]
for token in required:
    assert token in out, f'missing V360 contract token: {token}'

# V360 must reuse the existing functional controls, not clone/replace them.
for panel in ('frame','caption','look','audio','vision'):
    assert out.count(f'data-panel="{panel}"') == 1, f'V360 duplicated {panel} control'
assert out.count('id="v323CreateShort"') == 1, 'V360 duplicated create-short action'
assert out.count('id="v323SaveDraft"') == 1, 'V360 duplicated save-draft action'
assert 'cloneNode(' not in out[out.index('V360_MOBILE_EDITOR_REFERENCE'):], 'V360 must not clone real editor controls'
assert 'display:none!important' not in out[out.index('V360_MOBILE_EDITOR_REFERENCE'):][out[out.index('V360_MOBILE_EDITOR_REFERENCE'):].find('[data-panel="frame"]'):out[out.index('V360_MOBILE_EDITOR_REFERENCE'):].find('[data-panel="frame"]')+90], 'FRAME must stay available'

once = out
if FIX.exists():
    subprocess.run([sys.executable, str(FIX), str(target)], check=True)
    assert target.read_text(encoding='utf-8') == once, 'V360 patch must be restart-safe'

start = START.read_text(encoding='utf-8')
assert 'fix_v360_mobile_editor_reference.py' in start, 'startup must apply V360'
assert 'test_v360_mobile_editor_reference.py' in start, 'startup must verify V360'
assert start.index('fix_v326_mobile_editor_home_speed.py') < start.index('fix_v360_mobile_editor_reference.py'), 'V360 must run after V326'

print('V360 MOBILE EDITOR REFERENCE: PASS', flush=True)
