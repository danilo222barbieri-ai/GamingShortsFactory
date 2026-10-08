#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
PATCH=ROOT/'web'/'fix_v325_mobile_editor_viewport_fit.py'
EDITOR=ROOT/'web'/'editor_2027_component'/'index.html'
START=ROOT/'web'/'start_web.sh'

def fail(msg): print('[FAIL]',msg); raise SystemExit(1)
def ok(msg): print('[ OK ]',msg)

# Regression: V295 leaves stageWrap at height:100% + flex centering, which is what
# produced the large blank band above the player and detached timeline on iPhone.
if not PATCH.is_file(): fail('V325 implementation missing')
spec=importlib.util.spec_from_file_location('v325_mobile_editor_viewport_fit',PATCH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
sample='''<!doctype html><html><head>
<style>@media(max-width:760px){#ng27{height:100dvh!important}#ng27 .stageWrap{height:100%!important;display:flex!important;align-items:center!important;justify-content:center!important}#ng27 .topline{display:flex!important}}</style>
<style id="v323MobileEditorPlayerActions"></style>
</head><body><div id="ng27"><div class="shell"><div class="topline"></div><div class="cockpit"><div class="rail"></div><div class="stageWrap"><div class="stage r916" id="stage"></div><div class="timeline"></div></div><div class="rail"></div><div class="v323EditorActions" id="v323EditorActions"></div></div></div></div><script id="v324EditorActionPlacement">/* V324_EDITOR_ACTION_PLACEMENT */</script></body></html>'''
patched=mod.patch_text(sample)
checks={
 'style marker':'id="v325MobileEditorViewportFit"',
 'mobile root uses component height':'#ng27{height:100%!important;min-height:0!important;max-height:100%!important',
 'duplicate inner heading removed':'#ng27 .topline{display:none!important',
 'cockpit constrained to player width':'width:min(100%,340px)!important',
 'stageWrap no longer fills viewport':'height:auto!important',
 'stageWrap no flex centering':'display:block!important',
 'timeline pinned to frame':'left:8px!important;right:8px!important;bottom:8px!important',
 'actions own second row':'#ng27 .cockpit>.v323EditorActions{grid-column:1!important;grid-row:2!important',
 'rails stay inside player':'#ng27 .cockpit>.rail:first-child{left:7px!important',
 'right rail stays inside player':'#ng27 .cockpit>.rail:nth-of-type(2){right:7px!important',
 'short phone fit':'@media(max-width:390px) and (max-height:760px)',
}
for name,marker in checks.items():
 if marker not in patched: fail(name+' missing')
 ok(name)
if mod.patch_text(patched)!=patched: fail('V325 patch is not idempotent')
ok('V325 patch is idempotent')

if EDITOR.is_file() and 'id="v325MobileEditorViewportFit"' in EDITOR.read_text(encoding='utf-8'):
 live=EDITOR.read_text(encoding='utf-8')
 for marker in ('#ng27 .stageWrap{','height:auto!important','display:block!important','#ng27 .cockpit>.v323EditorActions{'):
  if marker not in live: fail('runtime editor missing V325 marker: '+marker)
 ok('runtime editor carries V325 viewport fit')

if START.is_file():
 start=START.read_text(encoding='utf-8')
 v324='python /app/web/test_v324_editor_action_placement.py /app'
 patch='python /app/web/fix_v325_mobile_editor_viewport_fit.py /app/web/editor_2027_component/index.html'
 test='python /app/web/test_v325_mobile_editor_viewport_fit.py /app'
 render='python /app/web/apply_v293_render_memory_guard.py'
 if patch not in start or test not in start: fail('V325 startup registration missing')
 if v324 in start and start.index(patch)<start.index(v324): fail('V325 must run after V324 validation')
 if start.index(test)<start.index(patch): fail('V325 test must run after V325 patch')
 if render in start and start.index(test)>start.index(render): fail('V325 must validate before render-memory generation')
 ok('V325 startup order')

print('\nV325 MOBILE EDITOR VIEWPORT FIT CONTRACT: PASS')
