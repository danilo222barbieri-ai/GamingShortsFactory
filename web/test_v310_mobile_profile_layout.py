#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'
PATCH = WEB / 'fix_v310_mobile_profile_layout.py'
HUB = WEB / 'creator_hub_v156_component' / 'index.html'
START = WEB / 'start_web.sh'


def fail(msg):
    print('[FAIL]', msg)
    raise SystemExit(1)


def ok(msg):
    print('[ OK ]', msg)


if not PATCH.is_file():
    fail('V310 patch missing')
if not HUB.is_file():
    fail('Creator Hub component missing')
if not START.is_file():
    fail('start_web.sh missing')

spec = importlib.util.spec_from_file_location('v310', PATCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if not hasattr(mod, 'patch_hub_text'):
    fail('patch_hub_text helper missing')
ok('pure patch helper present')

source = HUB.read_text(encoding='utf-8')
patched = mod.patch_hub_text(source)

required = (
    'V310 MOBILE PROFILE LAYOUT',
    '@media(max-width:760px)',
    '.profileMobilePlan{display:none!important}',
    'grid-template-columns:repeat(2,minmax(0,1fr))!important',
    '.profileOverviewCard:nth-child(3)',
    '.profileOverviewCard:nth-child(4)',
    'grid-column:1/-1!important',
    'display:grid!important',
    'grid-template-rows:auto auto auto!important',
    '.profileOverviewCard small',
    '.profileOverviewValue',
    '.profileOverviewHint',
    '.profileOverviewActions{display:none!important}',
    'overflow-y:auto!important',
    'padding-bottom:96px!important',
)
for marker in required:
    if marker not in patched:
        fail('missing layout marker: ' + marker)
    ok('found ' + marker)

if patched.count('V310 MOBILE PROFILE LAYOUT') != 2:
    fail('unexpected V310 marker count')
if mod.patch_hub_text(patched) != patched:
    fail('patch is not idempotent')
ok('patch is idempotent')

# V310 must not introduce desktop overrides.
block = patched.split('/* V310 MOBILE PROFILE LAYOUT */', 1)[1].split('/* END V310 MOBILE PROFILE LAYOUT */', 1)[0]
if '@media(min-width' in block:
    fail('desktop media query introduced')
ok('mobile-only scope retained')

start = START.read_text(encoding='utf-8')
needle = 'python /app/web/fix_v310_mobile_profile_layout.py /app/web/creator_hub_v156_component/index.html'
if needle not in start:
    fail('V310 startup patch not registered')
if start.index(needle) < start.index('python /app/web/test_v308_startup_contract.py /app'):
    fail('V310 must run after V308 canonical checks')
if start.index(needle) > start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V310 must run before production app generation')
ok('startup order correct')

print('\nV310 MOBILE PROFILE LAYOUT CONTRACT: PASS')
