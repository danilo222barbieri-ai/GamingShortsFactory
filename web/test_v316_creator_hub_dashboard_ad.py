#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
PATCH=ROOT/'web'/'fix_v316_creator_hub_dashboard_ad.py'
V317=ROOT/'web'/'fix_v317_compact_ai_selected_short.py'
AI=ROOT/'web'/'ai_v221_component'/'index.html'
START=ROOT/'web'/'start_web.sh'

def fail(msg):print('[FAIL]',msg);raise SystemExit(1)
def ok(msg):print('[ OK ]',msg)

if not PATCH.is_file():fail('V316 dashboard ad patch missing')
spec=importlib.util.spec_from_file_location('v316_creator_hub_dashboard_ad',PATCH);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
sample='''<!doctype html><html><head></head><body><div id="hub"><div class="stage"><section class="view active" data-view="dashboard"><div class="dashboard"><div class="profileCard"></div><div class="folders"><button class="folder" data-folder="profile"><div><div></div></div></button><button class="folder" data-folder="projects"><div><div></div></div></button><button class="folder" data-folder="live"><div><div></div></div></button></div></div></section></div></div><!-- V311 APPROVED CREATOR REFERENCE --></body></html>'''
patched=mod.patch_text(sample)
checks={'ad element':'id="hubDashboardAd"','ad slot marker':'data-ad-slot="hub-dashboard-mobile"','style marker':'id="v316HubDashboardAd"','mobile ad row':'grid-template-rows:136px minmax(0,1fr) 66px!important','short-screen ad row':'grid-template-rows:126px minmax(0,1fr) 50px!important','no-scroll clipping':'overflow:hidden!important'}
for name,marker in checks.items():
 if marker not in patched:fail(name+' missing')
 ok(name)
for marker in ('data-folder="profile"','data-folder="projects"','data-folder="live"'):
 if marker not in patched:fail('dashboard destination removed: '+marker)
ok('dashboard destinations preserved')
if patched.index('id="hubDashboardAd"')<=patched.index('data-folder="live"'):fail('ad is not after Live/folders')
ok('ad is after Live')
if mod.patch_text(patched)!=patched:fail('V316 patch is not idempotent')
ok('V316 patch is idempotent')

if not V317.is_file():fail('V317 compact AI patch missing')
if not AI.is_file():fail('V317 AI target missing')
ai=AI.read_text(encoding='utf-8')
for marker in ('id="v317AiCompactSelectedShort"','id="v317EmptyResults"','id="selectedShortPage"','id="selectedShortVideo"','Modifica in Editor','Vai alla pubblicazione','Scegli un altro momento','openSelectedShort(index);','send("open_editor"','send("create_short"','v317SyncResults();','Scegli come l’IA deve leggere il tuo gameplay.'):
 if marker not in ai:fail('V317 marker missing: '+marker)
ok('V317 compact AI and selected-short flow present')
if 'openMomentPreview(index);' in ai:fail('old mobile fullscreen preview handler still active')
ok('V317 replaces old mobile fullscreen preview')
vspec=importlib.util.spec_from_file_location('v317_compact_ai_selected_short',V317);vmod=importlib.util.module_from_spec(vspec);vspec.loader.exec_module(vmod)
if vmod.patch_text(ai)!=ai:fail('V317 patch is not idempotent')
ok('V317 patch is idempotent')

if START.is_file():
 start=START.read_text(encoding='utf-8');patch_marker='python /app/web/fix_v316_creator_hub_dashboard_ad.py /app/web/creator_hub_v156_component/index.html';test_marker='python /app/web/test_v316_creator_hub_dashboard_ad.py /app';v314='python /app/web/test_v314_hub_context_fill.py /app'
 if patch_marker not in start or test_marker not in start:fail('V316 startup registration missing')
 if start.index(patch_marker)<start.index(v314):fail('V316 must run after V314')
 if start.index(test_marker)<start.index(patch_marker):fail('V316 test must run after patch')
 ok('V316/V317 startup order')
print('\nV316 DASHBOARD AD + V317 COMPACT AI CONTRACT: PASS')
