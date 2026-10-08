#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
PATCH=ROOT/'web'/'fix_v316_creator_hub_dashboard_ad.py'
V317=ROOT/'web'/'fix_v317_compact_ai_selected_short.py'
V318=ROOT/'web'/'fix_v318_hub_fill_live_fit.py'
V320=ROOT/'web'/'fix_v320_ai_mobile_stability.py'
AI=ROOT/'web'/'ai_v221_component'/'index.html'
HUB=ROOT/'web'/'creator_hub_v156_component'/'index.html'
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
# Once later runtime passes are present V317 itself must no longer rewrite the page.
if 'id="v320AiMobileStability"' not in ai and vmod.patch_text(ai)!=ai:fail('V317 patch is not idempotent before later passes')
ok('V317 base contract remains present')

if not V318.is_file():fail('V318 Hub fill/Live fit patch missing')
xspec=importlib.util.spec_from_file_location('v318_hub_fill_live_fit',V318);xmod=importlib.util.module_from_spec(xspec);xspec.loader.exec_module(xmod)
live_sample='''<!doctype html><html><head></head><body><div id="hub"><section class="view" data-view="dashboard"><div class="dashboard"><div id="hubDashboardAd" class="hubDashboardAd"><span>Pubblicità</span></div></div></section><section class="view" data-view="live"><div class="detail"><div class="detailCard"><div class="folderScroller"><div class="hubContextGuide hubLiveGuide">Guida</div><div class="livePane active livePlatformCard livePlatformTwitch"><div class="livePlatformHead"><div class="livePlatformIcon"></div><div><h2 class="livePaneTitle">Twitch</h2><p class="livePlatformSubtitle">x</p></div></div><div class="liveMiniFolders"><button class="liveMiniFolder"><span></span><div><b>Le tue live</b><small>x</small></div><i>›</i></button></div></div><div class="livePane livePlatformCard livePlatformYoutube"><div class="livePlatformHead"><div class="livePlatformIcon"></div><div><h2 class="livePaneTitle">YouTube</h2><p class="livePlatformSubtitle">x</p></div></div><div class="liveMiniFolders"><button class="liveMiniFolder"><span></span><div><b>VOD</b><small>x</small></div><i>›</i></button></div></div></div></div></div></section></div></body></html>'''
xpatched=xmod.patch_text(live_sample)
xchecks={
 'V318 style':'id="v318HubFillLiveFit"',
 'larger dashboard ad row':'grid-template-rows:136px minmax(0,1fr) clamp(150px,23vh,220px)!important',
 'dashboard ad fills row':'min-height:150px!important',
 'Live owns viewport':'#hub .view[data-view="live"]{height:100%!important;min-height:0!important;overflow:hidden!important}',
 'Live two-platform grid':'grid-template-rows:34px repeat(2,minmax(0,1fr))!important',
 'Live keeps Game Bar clearance':'padding:2px 2px 94px!important',
 'Live compact mini rows':'grid-template-rows:repeat(3,minmax(0,1fr))!important',
 'short-screen fit':'grid-template-rows:30px repeat(2,minmax(0,1fr))!important',
}
for name,marker in xchecks.items():
 if marker not in xpatched:fail(name+' missing')
 ok(name)
if xmod.patch_text(xpatched)!=xpatched:fail('V318 patch is not idempotent')
ok('V318 patch is idempotent')
if HUB.is_file():
 hub=HUB.read_text(encoding='utf-8')
 for marker in ('id="hubDashboardAd"','id="v318HubFillLiveFit"','livePlatformTwitch','livePlatformYoutube'):
  if marker not in hub:fail('runtime Hub missing V318 marker: '+marker)
 ok('runtime Hub has expanded ad + fitted Live layout')

if not V320.is_file():fail('V320 mobile AI stability patch missing')
ai=AI.read_text(encoding='utf-8')
for marker in (
 'id="v320AiMobileStability"',
 'padding-bottom:96px!important',
 'flex:1 1 0!important',
 'function v320RequestState()',
 'async function v320StartAnalysis()',
 'create.addEventListener("click",v320StartAnalysis);',
 'GSF_AI_SELECTED_SHORT_V320',
 'webkit-playsinline',
):
 if marker not in ai:fail('runtime AI missing V320 marker: '+marker)
# V308's retired fullscreen helper can still contain an autoplay token, but
# V317 removes that click route. The iOS stability contract concerns the active
# selected-Short page only, so scope the check to openSelectedShort().
open_start=ai.find('function openSelectedShort(')
open_end=ai.find('function closeSelectedShort(',open_start)
if open_start<0 or open_end<0:fail('selected Short open/close function bounds missing')
selected_open=ai[open_start:open_end]
if 'video.play()' in selected_open:fail('active selected Short still autoplays on iOS')
if 'webkit-playsinline' not in selected_open:fail('active selected Short missing iOS inline playback')
ok('runtime AI has expanded results + state recovery + stable selected Short')

zspec=importlib.util.spec_from_file_location('v320_ai_mobile_stability',V320);zmod=importlib.util.module_from_spec(zspec);zspec.loader.exec_module(zmod)
if zmod.patch_text(ai)!=ai:fail('V320 patch is not idempotent')
ok('V320 patch is idempotent')

source=PATCH.read_text(encoding='utf-8')
for marker in ('fix_v318_hub_fill_live_fit.py','_apply_v318(hub)','fix_v320_ai_mobile_stability.py','_apply_v320(hub)'):
 if marker not in source:fail('final runtime delegation missing: '+marker)
ok('V318 and V320 are delegated from V316 final runtime pass')

if START.is_file():
 start=START.read_text(encoding='utf-8');patch_marker='python /app/web/fix_v316_creator_hub_dashboard_ad.py /app/web/creator_hub_v156_component/index.html';test_marker='python /app/web/test_v316_creator_hub_dashboard_ad.py /app';v314='python /app/web/test_v314_hub_context_fill.py /app';v320='python /app/web/test_v320_ai_mobile_stability.py /app'
 if patch_marker not in start or test_marker not in start:fail('V316 startup registration missing')
 if start.index(patch_marker)<start.index(v314):fail('V316 must run after V314')
 if start.index(test_marker)<start.index(patch_marker):fail('V316 test must run after patch')
 if v320 not in start or start.index(v320)<start.index(test_marker):fail('V320 final startup gate missing or out of order')
 ok('V316/V317/V318/V319/V320 startup order')
print('\nV316 DASHBOARD AD + V317 COMPACT AI + V318 HUB/LIVE FIT + V320 AI STABILITY CONTRACT: PASS')
