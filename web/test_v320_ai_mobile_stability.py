#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
PATCH=ROOT/'web'/'fix_v320_ai_mobile_stability.py'
V316=ROOT/'web'/'fix_v316_creator_hub_dashboard_ad.py'
START=ROOT/'web'/'start_web.sh'

def fail(msg): print('[FAIL]',msg); raise SystemExit(1)
def ok(msg): print('[ OK ]',msg)

if not PATCH.is_file(): fail('V320 mobile AI stability patch missing')
if not V316.is_file(): fail('V316 final runtime pass missing')
spec=importlib.util.spec_from_file_location('v320_ai_mobile_stability',PATCH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

sample='''<html><head>
<style id="v317AiCompactSelectedShort"></style>
<style id="v319AiResultsBridgeStyle"></style>
</head><body>
<div id="ai221"><div class="top"></div><div class="panel"></div><div class="panel"><div class="moments"></div></div></div>
<section class="selectedShortPage" id="selectedShortPage"></section>
<script>
let state={loaded:false,previews:[],selectedMoment:-1};
function send(){}
function v319Fail(){}
function v319StartAnalysis(){
   if(!state.loaded)return;
}
function openSelectedShort(index){const i=index,page=document.getElementById("selectedShortPage"),video=document.createElement("video");page.classList.add("open");page.setAttribute("aria-hidden","false");const play=video.play();if(play&&play.catch)play.catch(()=>{})}
function closeSelectedShort(){const page=document.getElementById("selectedShortPage"),video=null;if(video)try{video.pause()}catch(_e){};if(page){page.classList.remove("open");page.setAttribute("aria-hidden","true")}}
function sync(){create.disabled=!state.loaded;}
function v319SetBusy(on){create.disabled=!!on||!state.loaded;}
function v319Fail2(){create.disabled=!state.loaded;}
create.addEventListener("click",v319StartAnalysis);
</script></body></html>'''

patched=mod.patch_text(sample)
checks={
 'style marker':'id="v320AiMobileStability"',
 'mobile nav reserve':'padding-bottom:96px!important',
 'results panel fills viewport':'flex:1 1 0!important',
 'state retry':'function v320RequestState()',
 'click recovery':'async function v320StartAnalysis()',
 'recovered click handler':'create.addEventListener("click",v320StartAnalysis);',
 'cta stays actionable':'create.disabled=false;',
 'busy still disables':'create.disabled=!!on;',
 'selected page persistence':'GSF_AI_SELECTED_SHORT_V320',
 'ios inline video':'webkit-playsinline',
}
for name,marker in checks.items():
 if marker not in patched: fail(name+' missing')
 ok(name)
if 'const play=video.play()' in patched: fail('selected short still autoplays and can trigger iOS fullscreen churn')
if 'data-ad-slot' in patched: fail('V320 must not add an ad to the AI page')
if mod.patch_text(patched)!=patched: fail('V320 patch is not idempotent')
ok('V320 patch is idempotent')

v316_source=V316.read_text(encoding='utf-8')
for marker in ('fix_v320_ai_mobile_stability.py','_apply_v320(hub)','ai_v221_component'):
 if marker not in v316_source: fail('V320 final runtime delegation missing: '+marker)
ok('V320 is delegated from V316 final runtime pass')

if START.is_file():
 start=START.read_text(encoding='utf-8')
 v316_patch='python /app/web/fix_v316_creator_hub_dashboard_ad.py /app/web/creator_hub_v156_component/index.html'
 v319_test='python /app/web/test_v319_ai_results_bridge.py /app'
 test_marker='python /app/web/test_v320_ai_mobile_stability.py /app'
 if v316_patch not in start: fail('V316 final runtime pass registration missing')
 if test_marker not in start: fail('V320 startup test registration missing')
 if start.index(test_marker)<start.index(v316_patch): fail('V320 test must run after delegated patch')
 if v319_test in start and start.index(test_marker)<start.index(v319_test): fail('V320 final test must run after V319 result bridge test')
 ok('V320 startup order')

print('\nV320 MOBILE AI STABILITY CONTRACT: PASS')
