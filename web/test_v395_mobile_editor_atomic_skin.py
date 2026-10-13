#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
FIX=ROOT/'web'/'fix_v395_mobile_editor_atomic_skin.py'
EDITOR=ROOT/'web'/'editor_2027_component'/'index.html'
CHAIN=ROOT/'web'/'fix_v373_creator_hub_spacing.py'

if not FIX.is_file(): raise SystemExit('V395 implementation missing')
spec=importlib.util.spec_from_file_location('v395_mobile_editor_atomic_skin',FIX)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

sample='''<!doctype html><html><body>
<div id="ng27">
<div class="stageWrap"><div class="stage r916" id="stage">
<div class="v389TopBar"><div class="v389UndoRedo"><button id="undoBtn"></button><button id="redoBtn"></button></div><div class="v389TrimDock"><button class="v389TrimBtn"></button></div><div class="v389TopMode"><span class="v389RatioBtn">9:16</span><button id="zoomEditorBtn"></button></div></div>
<div class="v389ToolDock v389LeftDock"><button class="railBtn" data-panel="frame"><span>FRAME</span></button><button class="railBtn" data-panel="caption"><span>CAPTION</span></button><button class="railBtn" data-panel="look"><span>LOOK</span></button></div>
<div class="v389ToolDock v389RightDock"><button class="railBtn" data-panel="audio"><span>AUDIO</span></button><button class="railBtn" data-panel="vision"><span>AI</span></button></div>
<div class="v393TransportGlass"></div><div class="v389PlaybackDock"><button id="playBtn"></button></div><div class="v389PlayerProgress"><div class="v389ProgressTrack"></div></div>
</div></div>
<div id="v391EditorActions" class="v391EditorActions"></div><button id="v393ChangeShort" class="v393ChangeShort">CAMBIA SHORT</button>
</div>
<!-- V394_MOBILE_EDITOR_FOOTER_RESTORE -->
</body></html>'''
out=mod.patch_editor(sample)
for token in (
 'V395_MOBILE_EDITOR_ATOMIC_SKIN','v395MobileEditorAtomicSkin','--v395-ink:#24557b',
 'box-shadow:0 12px 30px rgba(31,99,145,.16)','#ng27 .stage.r916:before',
 '#ng27 .v389ToolDock .railBtn:before','#ng27 .v389RightDock .railBtn[data-panel="vision"]',
 '#ng27 .v393TransportGlass','margin:-3px auto 14px!important','border:0!important'):
 if token not in out: raise AssertionError('V395 token missing: '+token)
if 'box-shadow:0 0 0 4px' in mod.EDITOR_PATCH: raise AssertionError('V395 must not restore old double-ring player shell')
if mod.patch_editor(out)!=out: raise AssertionError('V395 patch must be idempotent')

if EDITOR.is_file():
 live=EDITOR.read_text(encoding='utf-8')
 if 'V394_MOBILE_EDITOR_FOOTER_RESTORE' in live:
  for token in ('V395_MOBILE_EDITOR_ATOMIC_SKIN','v395MobileEditorAtomicSkin','margin:-3px auto 14px!important'):
   if token not in live: raise AssertionError('runtime V395 token missing: '+token)

if CHAIN.is_file():
 c=CHAIN.read_text(encoding='utf-8')
 for token in ('fix_v395_mobile_editor_atomic_skin.py','test_v395_mobile_editor_atomic_skin.py'):
  if token not in c: raise AssertionError('V395 chain wiring missing: '+token)

print('V395 MOBILE EDITOR ATOMIC SKIN CONTRACT: PASS')
