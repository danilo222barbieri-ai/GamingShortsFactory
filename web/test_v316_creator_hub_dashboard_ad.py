#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PATCH = ROOT / 'web' / 'fix_v316_creator_hub_dashboard_ad.py'
START = ROOT / 'web' / 'start_web.sh'


def fail(msg: str) -> None:
    print('[FAIL]', msg)
    raise SystemExit(1)


def ok(msg: str) -> None:
    print('[ OK ]', msg)


if not PATCH.is_file():
    fail('V316 dashboard ad patch missing')

spec = importlib.util.spec_from_file_location('v316_creator_hub_dashboard_ad', PATCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

sample = '''<!doctype html><html><head></head><body>
<div id="hub"><div class="stage">
<section class="view active" data-view="dashboard">
 <div class="dashboard">
  <div class="profileCard"></div>
  <div class="folders">
   <button class="folder" data-folder="profile"><div><div></div></div></button>
   <button class="folder" data-folder="projects"><div><div></div></div></button>
   <button class="folder" data-folder="live"><div><div></div></div></button>
  </div>
 </div>
</section>
</div></div>
<!-- V311 APPROVED CREATOR REFERENCE -->
</body></html>'''

patched = mod.patch_text(sample)

checks = {
    'ad element': 'id="hubDashboardAd"',
    'ad slot marker': 'data-ad-slot="hub-dashboard-mobile"',
    'style marker': 'id="v316HubDashboardAd"',
    'mobile ad row': 'grid-template-rows:136px minmax(0,1fr) 66px!important',
    'short-screen ad row': 'grid-template-rows:126px minmax(0,1fr) 50px!important',
    'no-scroll clipping': 'overflow:hidden!important',
}
for name, marker in checks.items():
    if marker not in patched:
        fail(name + ' missing')
    ok(name)

for marker in ('data-folder="profile"', 'data-folder="projects"', 'data-folder="live"'):
    if marker not in patched:
        fail('dashboard destination removed: ' + marker)
ok('dashboard destinations preserved')

if patched.index('id="hubDashboardAd"') <= patched.index('data-folder="live"'):
    fail('ad is not after Live/folders')
ok('ad is after Live')

if mod.patch_text(patched) != patched:
    fail('V316 patch is not idempotent')
ok('V316 patch is idempotent')

if START.is_file():
    start = START.read_text(encoding='utf-8')
    patch_marker = 'python /app/web/fix_v316_creator_hub_dashboard_ad.py /app/web/creator_hub_v156_component/index.html'
    test_marker = 'python /app/web/test_v316_creator_hub_dashboard_ad.py /app'
    v314_marker = 'python /app/web/test_v314_hub_context_fill.py /app'
    if patch_marker not in start or test_marker not in start:
        fail('V316 startup registration missing')
    if start.index(patch_marker) < start.index(v314_marker):
        fail('V316 must run after V314')
    if start.index(test_marker) < start.index(patch_marker):
        fail('V316 test must run after patch')
    ok('V316 startup order')

print('\nV316 CREATOR HUB DASHBOARD AD CONTRACT: PASS')
