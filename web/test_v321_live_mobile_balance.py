#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
PATCH=ROOT/'web'/'fix_v321_live_mobile_balance.py'
AGG=ROOT/'web'/'fix_v316_creator_hub_dashboard_ad.py'
START=ROOT/'web'/'start_web.sh'

def fail(msg): print('[FAIL]',msg); raise SystemExit(1)
def ok(msg): print('[ OK ]',msg)

if not PATCH.is_file(): fail('V321 Live balance patch missing')
spec=importlib.util.spec_from_file_location('v321_live_mobile_balance',PATCH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

base='''<html><head><style id="v318HubFillLiveFit"></style></head><body><div id="hub"><div class="view" data-view="live"><div class="hubLiveGuide"></div><div class="livePlatformCard livePlatformTwitch"><div class="liveMiniFolders"></div></div><div class="livePlatformCard livePlatformYoutube"><div class="liveMiniFolders"></div></div></div></div></body></html>'''
out=mod.patch_text(base)

checks=(
 ('style marker','id="v321LiveMobileBalance"'),
 ('mobile-only scope','@media(max-width:767px)'),
 ('natural Live flow','grid-template-rows:30px auto auto!important'),
 ('balanced provider height','height:266px!important'),
 ('equal mini rows','grid-template-rows:repeat(3,65px)!important'),
 ('short viewport provider height','height:228px!important'),
 ('short viewport mini rows','grid-template-rows:repeat(3,54px)!important'),
)
for label,needle in checks:
    if needle not in out: fail(label+' missing')
    ok(label)

if mod.patch_text(out)!=out: fail('V321 patch is not idempotent')
ok('V321 patch is idempotent')

if '@media(min-width:' in mod.STYLE.replace(' ',''):
    fail('V321 must not add desktop rules')
ok('desktop is untouched')

if not AGG.is_file(): fail('V316 final runtime aggregate missing')
agg=AGG.read_text(encoding='utf-8')
for marker in ('fix_v321_live_mobile_balance.py','_apply_v321(hub)'):
    if marker not in agg: fail('V321 final runtime delegation missing: '+marker)
if agg.index('_apply_v321(hub)') < agg.index('_apply_v320(hub)'):
    fail('V321 must run after V320')
ok('V321 is the final delegated runtime layout pass')

if not START.is_file(): fail('start_web.sh missing')
start=START.read_text(encoding='utf-8')
v316='python /app/web/fix_v316_creator_hub_dashboard_ad.py /app/web/creator_hub_v156_component/index.html'
if v316 not in start: fail('V316 aggregate startup registration missing')
if start.index(v316) > start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V316/V321 aggregate must run before render-memory generation')
ok('V321 executes before production app generation')

print('\nV321 LIVE MOBILE BALANCE CONTRACT: PASS')
