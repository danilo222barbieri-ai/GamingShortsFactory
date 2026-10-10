#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import re
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
PATCH=ROOT/'web'/'fix_v325_mobile_editor_viewport_fit.py'
EDITOR=ROOT/'web'/'editor_2027_component'/'index.html'
START=ROOT/'web'/'start_web.sh'

def fail(msg): print('[FAIL]',msg); raise SystemExit(1)
def ok(msg): print('[ OK ]',msg)

if not PATCH.is_file(): fail('V325 implementation missing')
spec=importlib.util.spec_from_file_location('v325_mobile_editor_viewport_fit',PATCH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

sample='''<!doctype html><html><head>
<style id="v323MobileEditorPlayerActions"></style>
</head><body><div id="ng27"><div class="shell"><div class="topline"></div><div class="cockpit">
<div class="rail"><button data-panel="frame"></button><button data-panel="caption"></button><button data-panel="look"></button><button data-panel="audio"></button></div>
<div class="stageWrap"><div class="stage r916" id="stage"><div class="captionPreview" id="captionPreview">CAPTION AUTO</div><video id="video"></video></div><div class="timeline"><div class="tlMeta"><span>IN</span><span>TAGLIO</span><span>OUT</span></div><div class="track"></div></div></div>
<div class="v323EditorActions" id="v323EditorActions"></div>
<div class="rail"><button id="playBtn"></button><button data-panel="vision"></button></div>
</div></div></div>
<script>function setFrameHeight(x){} function fitEditorViewport(){const pw=400;if(pw<=820){setFrameHeight(Math.max(720,Math.ceil(document.documentElement.scrollHeight||720)));return}}</script>
<script id="v324EditorActionPlacement">/* V324_EDITOR_ACTION_PLACEMENT */</script></body></html>'''

patched=mod.patch_text(sample)
checks={
 'style marker':'id="v325MobileEditorViewportFit"',
 'runtime layout marker':'id="v325MobileEditorReferenceLayout"',
 'legacy mobile iframe minimum removed':'Math.max(500,Math.min(710,Math.floor(ph-145)))',
 'compact player sizing':'width:min(calc(100% - 18px),292px,calc((100dvh - 150px)*.5625))!important',
 'timeline no longer absolute':'position:relative!important',
 'left controls moved into player':'stage.appendChild(leftRail)',
 'right controls moved into player':'stage.appendChild(rightRail)',
 'audio moved to right':'rightRail.insertBefore(audioBtn',
 'play dock inside player':'dock.appendChild(playBtn)',
 'timeline moved below actions':"actions.insertAdjacentElement('afterend',timeline)",
 'time chip':'id="v325TimeChip"',
 'ratio chip':'9:16',
 'default caption placeholder suppressed':'v325DefaultCaption',
 'short phone fit':'@media(max-width:390px) and (max-height:700px)',
}
for name,marker in checks.items():
 if marker not in patched: fail(name+' missing')
 ok(name)

layout_checks={
 'player is first row':r'#ng27\s+\.stageWrap\s*\{[\s\S]*?grid-column\s*:\s*1\s*!important\s*;\s*grid-row\s*:\s*1\s*!important',
 'actions directly below player':r'#ng27\s+\.cockpit>\.v323EditorActions\s*\{[\s\S]*?grid-column\s*:\s*1\s*!important\s*;\s*grid-row\s*:\s*2\s*!important',
 'timeline is dedicated third row':r'#ng27\s+\.cockpit>\.timeline\.v325DetachedTimeline\s*\{[\s\S]*?grid-column\s*:\s*1\s*!important\s*;\s*grid-row\s*:\s*3\s*!important',
}
for name,pattern in layout_checks.items():
 if not re.search(pattern,patched): fail(name+' missing')
 ok(name)

if 'Math.max(720,Math.ceil(document.documentElement.scrollHeight||720))' in patched:
 fail('legacy 720px mobile iframe inflation still present')
if mod.patch_text(patched)!=patched: fail('V325 patch is not idempotent')
ok('V325 patch is idempotent')

if EDITOR.is_file() and 'id="v325MobileEditorViewportFit"' in EDITOR.read_text(encoding='utf-8'):
 live=EDITOR.read_text(encoding='utf-8')
 for marker in ('v325MobileEditorReferenceLayout','v325DetachedTimeline','v325PlaybackDock'):
  if marker not in live: fail('runtime editor missing approved-reference marker: '+marker)
 ok('runtime editor carries approved-reference layout')

if START.is_file():
 start=START.read_text(encoding='utf-8')
 v324='python /app/web/test_v324_editor_action_placement.py /app'
 patch='python /app/web/fix_v325_mobile_editor_viewport_fit.py /app/web/editor_2027_component/index.html'
 test='python /app/web/test_v325_mobile_editor_viewport_fit.py /app'
 render='python /app/web/apply_v293_render_memory_guard.py'
 guard="if grep -q 'V360_MOBILE_EDITOR_REFERENCE' /app/web/editor_2027_component/index.html 2>/dev/null; then"
 skip='V325 restart-safe: newer V360 Editor reference already active'
 if patch not in start or test not in start: fail('V325 startup registration missing')
 if guard not in start or skip not in start: fail('V325 restart-safe V360 guard missing')
 if v324 in start and start.index(guard)<start.index(v324): fail('V325 restart-safe guard must run after V324 validation')
 if start.index(test)<start.index(patch): fail('V325 test must run after V325 patch')
 if render in start and start.index(test)>start.index(render): fail('V325 must validate before render-memory generation')
 ok('V325 startup order + V360 restart guard')

print('\nV325 MOBILE EDITOR APPROVED REFERENCE CONTRACT: PASS')
