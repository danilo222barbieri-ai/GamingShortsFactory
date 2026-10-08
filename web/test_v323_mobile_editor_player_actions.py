#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
PATCH=ROOT/'web'/'fix_v323_mobile_editor_player_actions.py'
EDITOR=ROOT/'web'/'editor_2027_component'/'index.html'
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
START=ROOT/'web'/'start_web.sh'

def fail(msg): print('[FAIL]',msg); raise SystemExit(1)
def ok(msg): print('[ OK ]',msg)

# RED first: the implementation file must exist only after the contract is defined.
if not PATCH.is_file(): fail('V323 implementation missing')
spec=importlib.util.spec_from_file_location('v323_mobile_editor_player_actions',PATCH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

editor_sample='''<!doctype html><html><head></head><body><div id="ng27"><div class="shell"><div class="topline"><div class="brand"></div><div class="sys"><button id="zoomEditorBtn"><span>FULL</span></button></div></div><div class="cockpit"><div class="rail"><button class="railBtn" data-panel="frame">FRAME</button><button class="railBtn" data-panel="cover">COVER</button><button class="railBtn" data-panel="look">LOOK</button><button class="railBtn" data-panel="hud">HUD</button><button class="railBtn" data-panel="caption">CAPTION</button><button class="railBtn" data-panel="audio">AUDIO</button></div><div class="stageWrap"><div class="stage r916" id="stage"></div><div class="timeline"><div class="track"></div></div></div><div class="rail"><button class="railBtn" id="playBtn">PLAY</button><button class="railBtn" id="undoBtn">UNDO</button><button class="railBtn" id="redoBtn">REDO</button><button class="railBtn" data-panel="vision">GAME AI</button><button class="railBtn" id="doneBtn">DONE</button></div></div></div></div><script>const root=document.getElementById('ng27');const stage=root.querySelector('#stage');const zoomEditorBtn=root.querySelector('#zoomEditorBtn');function commit(){}function cloneState(){return {inPoint:0,outPoint:15}}function sendStateToPython(value){}function flash(x){}root.querySelector('#doneBtn').onclick=()=>{};</script></body></html>'''
patched=mod.patch_editor_text(editor_sample)
for marker in (
 'id="v323MobileEditorPlayerActions"',
 'id="v323EditorActions"',
 'id="v323CreateShort"',
 'CREA SHORT',
 'id="v323SaveDraft"',
 'SALVA LA TUA BOZZA',
 'data-panel="frame"',
 'data-panel="caption"',
 'data-panel="look"',
 'data-panel="audio"',
 'data-panel="vision"',
 'id="zoomEditorBtn"',
 'editorAction="create_short"',
 'editorAction="save_draft"',
 'v323PlaceFullscreen',
):
 if marker not in patched: fail('V323 editor marker missing: '+marker)
if patched.index('class="timeline"') > patched.index('id="v323EditorActions"'):
 fail('V323 actions must be below the timeline in DOM order')
for marker in (
 '#ng27 .railBtn[data-panel="cover"]',
 '#ng27 .railBtn[data-panel="hud"]',
 '#ng27 #undoBtn',
 '#ng27 #redoBtn',
 '#ng27 #doneBtn',
 'display:none!important',
):
 if marker not in patched: fail('V323 mobile simplification missing: '+marker)
if mod.patch_editor_text(patched)!=patched: fail('V323 editor patch is not idempotent')
ok('V323 editor mobile contract + idempotence')

shell_sample='''const close=()=>{}; window.addEventListener('message',e=>{ if(e.source===frame.contentWindow&&e.data&&e.data.type==='streamlit:setComponentValue'){ const state=e.data.value; if(state&&typeof state==='object'){ editorMeta.initial_state=state; fetch('/editor/state/save',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({state})}).catch(()=>{}); guide('done'); } return; } });'''
shell=mod.patch_shell_text(shell_sample)
for marker in (
 'V323_EDITOR_ACTION_BRIDGE',
 "editorAction||''",
 '/editor/state/save',
 '/creator-hub/project/save-draft',
 '.st-key-gsf-major-create-short button',
 '.st-key-create_final_short_v54 button',
 'target.click()',
):
 if marker not in shell: fail('V323 shell action bridge missing: '+marker)
if mod.patch_shell_text(shell)!=shell: fail('V323 shell patch is not idempotent')
ok('V323 create-short + save-draft bridge contract')

if EDITOR.is_file():
 live=EDITOR.read_text(encoding='utf-8')
 if 'id="v323MobileEditorPlayerActions"' in live:
  for marker in ('id="v323EditorActions"','id="v323CreateShort"','id="v323SaveDraft"'):
   if marker not in live: fail('runtime editor incomplete V323 marker: '+marker)
  ok('runtime editor carries V323')

if APP.is_file() and 'V323_EDITOR_ACTION_BRIDGE' in APP.read_text(encoding='utf-8'):
 ok('runtime shell carries V323 action bridge')

if START.is_file():
 start=START.read_text(encoding='utf-8')
 patch_marker='python /app/web/fix_v323_mobile_editor_player_actions.py /app'
 test_marker='python /app/web/test_v323_mobile_editor_player_actions.py /app'
 v322='python /app/web/test_v322_mobile_hub_live_fill.py /app'
 render='python /app/web/apply_v293_render_memory_guard.py'
 if patch_marker not in start or test_marker not in start: fail('V323 startup registration missing')
 if v322 in start and start.index(patch_marker)<start.index(v322): fail('V323 must run after V322 gate')
 if start.index(test_marker)<start.index(patch_marker): fail('V323 test must run after V323 patch')
 if render in start and start.index(test_marker)>start.index(render): fail('V323 must validate before render-memory generation')
 ok('V323 startup order')

print('\nV323 MOBILE EDITOR PLAYER + ACTIONS CONTRACT: PASS')
