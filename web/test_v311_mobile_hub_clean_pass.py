#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'
PATCH = WEB / 'fix_v311_mobile_hub_clean_pass.py'
HUB = WEB / 'creator_hub_v156_component' / 'index.html'
START = WEB / 'start_web.sh'


def fail(msg):
    print('[FAIL]', msg)
    raise SystemExit(1)


def ok(msg):
    print('[ OK ]', msg)

for path, label in ((PATCH,'patch'),(HUB,'hub'),(START,'start_web')):
    if not path.is_file(): fail(label + ' missing')

spec = importlib.util.spec_from_file_location('v311', PATCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
source = HUB.read_text(encoding='utf-8')
patched = mod.patch_hub_text(source)

required = (
    'V311 MOBILE HUB CLEAN PASS',
    '@media(max-width:760px)',
    '.profilePlanGroup{display:none!important}',
    '.profileOverviewActions{display:none!important}',
    '#projectRows .stats',
    '.liveRootFolders{display:none!important}',
    'data-live-pane="youtube"',
    'youtubeLiveFolders',
    '<b>Le tue live</b><small>Dirette YouTube salvate nel Creator Hub</small>',
    '<b>VOD</b><small>Replay completi delle live YouTube</small>',
    '<b>Highlights</b><small>Short e momenti estratti da YouTube</small>',
    'grid-template-rows:repeat(5,minmax(58px,1fr))!important',
    '.hubMural{display:none!important}',
)
for marker in required:
    if marker not in patched: fail('missing marker: ' + marker)
    ok('found ' + marker)

if mod.patch_hub_text(patched) != patched:
    fail('V311 patch is not idempotent')
ok('patch is idempotent')

block = patched.split('/* V311 MOBILE HUB CLEAN PASS */',1)[1].split('/* END V311 MOBILE HUB CLEAN PASS */',1)[0]
if '@media(min-width' in block:
    fail('desktop rule introduced')
ok('mobile-only scope retained')

start = START.read_text(encoding='utf-8')
needle = 'python /app/web/fix_v311_mobile_hub_clean_pass.py /app/web/creator_hub_v156_component/index.html'
if needle not in start: fail('V311 startup patch not registered')
if start.index(needle) < start.index('python /app/web/test_v310_creator_hub_mobile_cleanup.py /app'):
    fail('V311 must run after V310')
if start.index(needle) > start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V311 must run before production app generation')
ok('startup order correct')

print('\nV311 MOBILE HUB CLEAN PASS: PASS')
