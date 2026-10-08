#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
PATCH=ROOT/'web'/'fix_v322_mobile_hub_live_fill.py'
V316=ROOT/'web'/'fix_v316_creator_hub_dashboard_ad.py'
HUB=ROOT/'web'/'creator_hub_v156_component'/'index.html'
START=ROOT/'web'/'start_web.sh'

def fail(msg): print('[FAIL]',msg); raise SystemExit(1)
def ok(msg): print('[ OK ]',msg)

if not PATCH.is_file(): fail('V322 Hub/Live fill patch missing')
spec=importlib.util.spec_from_file_location('v322_mobile_hub_live_fill',PATCH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

sample='''<!doctype html><html><head>
<style id="v318HubFillLiveFit"></style><style id="v321LiveMobileBalance"></style>
</head><body><div id="hub">
<section class="view" data-view="dashboard"><div class="dashboard"><div class="profileCard"></div><div class="folders"><button class="folder" data-folder="profile"></button><button class="folder" data-folder="projects"></button><button class="folder" data-folder="live"></button></div><div id="hubDashboardAd" class="hubDashboardAd"><span>Pubblicità</span></div></div></section>
<section class="view" data-view="live"><div class="detail"><div class="detailCard"><div class="folderScroller"><div class="hubContextGuide hubLiveGuide"></div><div class="livePlatformCard livePlatformTwitch"><div class="livePlatformHead"></div><div class="liveMiniFolders"><button class="liveMiniFolder"></button><button class="liveMiniFolder"></button><button class="liveMiniFolder"></button></div></div><div class="livePlatformCard livePlatformYoutube"><div class="livePlatformHead"></div><div class="liveMiniFolders"><button class="liveMiniFolder"></button><button class="liveMiniFolder"></button><button class="liveMiniFolder"></button></div></div></div></div></div></section>
</div></body></html>'''

patched=mod.patch_text(sample)
checks={
 'style marker':'id="v322MobileHubLiveFill"',
 'dashboard fills':'grid-template-rows:136px minmax(0,1fr) clamp(168px,21vh,198px)!important',
 'three dashboard folders fill':'grid-template-rows:repeat(3,minmax(0,1fr))!important',
 'dashboard ad stretches':'align-self:stretch!important',
 'live viewport grid':'grid-template-rows:32px repeat(2,minmax(0,1fr))!important',
 'live providers stretch':'height:100%!important',
 'live mini rows balanced':'grid-template-rows:repeat(3,minmax(0,1fr))!important',
 'gamebar clearance':'padding:0 2px 82px!important',
 'short phone contract':'grid-template-rows:28px repeat(2,minmax(0,1fr))!important',
}
for name,marker in checks.items():
 if marker not in patched: fail(name+' missing')
 ok(name)
for marker in ('data-folder="profile"','data-folder="projects"','data-folder="live"','hubDashboardAd','livePlatformTwitch','livePlatformYoutube'):
 if marker not in patched: fail('V322 removed structure: '+marker)
ok('V322 preserves Hub/Live structure')
if mod.patch_text(patched)!=patched: fail('V322 patch is not idempotent')
ok('V322 patch idempotent')

# Restart regression: V316 removes/reinserts its own style, so its CSS can move
# after V322. The final V322 pass must move itself back to the end of <head>.
late_v316=patched.replace('</head>','<style id="v316RestartRewrite">.x{height:1px}</style>\n</head>',1)
reasserted=mod.patch_text(late_v316)
pos322=reasserted.rfind('id="v322MobileHubLiveFill"')
poslate=reasserted.rfind('id="v316RestartRewrite"')
if pos322<0 or poslate<0 or pos322<poslate:
 fail('V322 does not reassert final CSS order after restart')
ok('V322 remains final CSS authority after restart')

if not V316.is_file(): fail('V316 aggregate missing')
source=V316.read_text(encoding='utf-8')
for marker in ('fix_v322_mobile_hub_live_fill.py','_apply_v322(hub)'):
 if marker not in source: fail('V322 final delegation missing: '+marker)
if source.index('_apply_v322(hub)') < source.index('_apply_v321(hub)'):
 fail('V322 must run after V321')
ok('V322 delegated after V321')

if HUB.is_file() and 'id="v322MobileHubLiveFill"' in HUB.read_text(encoding='utf-8'):
 ok('runtime Hub already carries V322 marker')

if START.is_file():
 start=START.read_text(encoding='utf-8')
 marker='python /app/web/test_v322_mobile_hub_live_fill.py /app'
 v320='python /app/web/test_v320_ai_mobile_stability.py /app'
 if marker not in start: fail('V322 startup gate missing')
 if v320 in start and start.index(marker)<start.index(v320): fail('V322 gate must run after V320')
 ok('V322 startup gate order')

print('\nV322 MOBILE HUB + LIVE FULL-HEIGHT CONTRACT: PASS')
