#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
PATCH=ROOT/'web'/'fix_v324_editor_action_placement.py'
EDITOR=ROOT/'web'/'editor_2027_component'/'index.html'
START=ROOT/'web'/'start_web.sh'

def fail(msg): print('[FAIL]',msg); raise SystemExit(1)
def ok(msg): print('[ OK ]',msg)

if not PATCH.is_file(): fail('V324 implementation missing')
spec=importlib.util.spec_from_file_location('v324_editor_action_placement',PATCH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
sample='''<!doctype html><html><body><div id="ng27"><div class="cockpit"><div class="rail"></div><div class="stageWrap"><div id="stage"></div><div class="timeline"></div><div class="v323EditorActions" id="v323EditorActions"></div></div><div class="rail"></div></div></div><script></script></body></html>'''
patched=mod.patch_text(sample)
for marker in ('V324_EDITOR_ACTION_PLACEMENT','stageWrap.insertAdjacentElement(\'afterend\',actions)','id="v323EditorActions"'):
 if marker not in patched: fail('V324 marker missing: '+marker)
if mod.patch_text(patched)!=patched: fail('V324 patch is not idempotent')
ok('V324 runtime action placement script + idempotence')

if EDITOR.is_file() and 'id="v323MobileEditorPlayerActions"' in EDITOR.read_text(encoding='utf-8'):
 live=EDITOR.read_text(encoding='utf-8')
 if 'V324_EDITOR_ACTION_PLACEMENT' in live: ok('runtime editor carries V324 placement')

if START.is_file():
 start=START.read_text(encoding='utf-8')
 v323='python /app/web/test_v323_mobile_editor_player_actions.py /app'
 patch='python /app/web/fix_v324_editor_action_placement.py /app/web/editor_2027_component/index.html'
 test='python /app/web/test_v324_editor_action_placement.py /app'
 render='python /app/web/apply_v293_render_memory_guard.py'
 if patch not in start or test not in start: fail('V324 startup registration missing')
 if v323 in start and start.index(patch)<start.index(v323): fail('V324 must run after V323 validation')
 if start.index(test)<start.index(patch): fail('V324 test must run after patch')
 if render in start and start.index(test)>start.index(render): fail('V324 must validate before render-memory generation')
 ok('V324 startup order')

print('\nV324 EDITOR ACTION PLACEMENT CONTRACT: PASS')
