#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('.').resolve()
WEB = ROOT / 'web'
PATCH = WEB / 'fix_v310_creator_hub_mobile_cleanup.py'
HUB = WEB / 'creator_hub_v156_component' / 'index.html'
START = WEB / 'start_web.sh'


def fail(msg):
    print('[FAIL]', msg)
    raise SystemExit(1)


def ok(msg):
    print('[ OK ]', msg)

if not PATCH.exists():
    fail('V310 patch file missing')
if not HUB.exists():
    fail('Creator Hub component missing')
if not START.exists():
    fail('start_web.sh missing')

spec = importlib.util.spec_from_file_location('v310_cleanup', PATCH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
if not hasattr(module, 'patch_hub_text'):
    fail('patch_hub_text() missing')
ok('pure patch_hub_text helper present')

source = HUB.read_text(encoding='utf-8')
patched = module.patch_hub_text(source)

required = (
    'V310 CREATOR HUB MOBILE CLEANUP',
    'profileOverviewGrid',
    'grid-template-columns:repeat(2,minmax(0,1fr))',
    'profileOverviewCard',
    'profileOverviewValue',
    'liveMiniContent',
)
for marker in required:
    if marker not in patched:
        fail('missing expected marker: ' + marker)
    ok('found marker: ' + marker)

if '<b>Progetto corrente</b>' in patched:
    fail('Bozze still renders Progetto corrente')
ok('Bozze no longer renders Progetto corrente')

if 'Le tue live Twitch compariranno qui come mini-cartelle, una per ogni diretta.' in patched:
    fail('Live bottom placeholder bubble still present')
ok('Live bottom placeholder bubble removed')

if 'id="liveMiniContent" class="liveMiniContent"><div class="empty">' in patched:
    fail('Live mini content still boots with an empty bubble')
ok('Live mini content boots clean')

patched_twice = module.patch_hub_text(patched)
if patched_twice != patched:
    fail('V310 patch is not idempotent')
ok('V310 patch is idempotent')

start = START.read_text(encoding='utf-8')
needle = 'python /app/web/fix_v310_creator_hub_mobile_cleanup.py /app/web/creator_hub_v156_component/index.html'
if needle not in start:
    fail('V310 startup patch is not registered')
if start.index(needle) < start.index('python /app/web/test_v308_mobile_ai_flow.py /app'):
    fail('V310 must run after V308 final mobile surface patch')
if start.index(needle) > start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V310 must run before production app generation')
ok('startup order is correct')

print('\nV310 CREATOR HUB MOBILE CLEANUP: PASS')
