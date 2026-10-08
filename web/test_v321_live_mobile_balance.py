#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
PATCH=ROOT/'web'/'fix_v321_live_mobile_balance.py'
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

if not START.is_file(): fail('start_web.sh missing')
start=START.read_text(encoding='utf-8')
patch_cmd='python /app/web/fix_v321_live_mobile_balance.py /app/web/creator_hub_v156_component/index.html'
test_cmd='python /app/web/test_v321_live_mobile_balance.py /app'
if patch_cmd not in start or test_cmd not in start: fail('V321 startup registration missing')
if start.index(patch_cmd) < start.index('python /app/web/fix_v316_creator_hub_dashboard_ad.py'):
    fail('V321 must run after V316-V320 aggregate')
if start.index(test_cmd) > start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V321 contract must run before render-memory generation')
ok('V321 startup order')

print('\nV321 LIVE MOBILE BALANCE CONTRACT: PASS')
