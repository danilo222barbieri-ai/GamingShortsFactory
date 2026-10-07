#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PATCH = ROOT / 'web' / 'fix_v310_profile_mobile.py'
START = ROOT / 'web' / 'start_web.sh'


def fail(message):
    print('[FAIL]', message)
    raise SystemExit(1)

if not PATCH.exists():
    fail('V310 profile mobile patch missing')
if not START.exists():
    fail('start_web.sh missing')

spec = importlib.util.spec_from_file_location('gsf_v310_profile_mobile', PATCH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
if not hasattr(module, 'patch_hub_text'):
    fail('patch_hub_text() missing')

sample = '''<!doctype html><html><head></head><body><main id="hub">
<section class="view" data-view="profile"><div class="detailCard"><div class="folderScroller profileOnlyScroller">
<div class="profileGroup profilePlanGroup profileMobilePlan">ABBONAMENTO</div>
<div class="profileOverviewGrid">
<button class="profileOverviewCard"><small>SHORTS CREATI</small><b class="profileOverviewValue">0</b><span class="profileOverviewHint">Apri I miei Shorts</span></button>
<button class="profileOverviewCard"><small>BOZZE</small><b class="profileOverviewValue">1</b><span class="profileOverviewHint">Riprendi i progetti</span></button>
<button class="profileOverviewCard"><small>IL TUO PIANO</small><b class="profileOverviewValue">FREE</b><span class="profileOverviewHint">Vedi abbonamento</span></button>
<button class="profileOverviewCard"><small>SOCIAL COLLEGATI</small><b class="profileOverviewValue">1/5</b><span class="profileOverviewHint">Gestisci account</span></button>
</div><div class="profileOverviewActions"></div><button class="logoutProfile">Disconnetti</button>
</div></div></section></main></body></html>'''

out = module.patch_hub_text(sample)
required = (
    'V310 PROFILE MOBILE CLEANUP',
    '@media(max-width:760px)',
    '.profileMobilePlan{display:none!important}',
    '.profileOnlyScroller{',
    'overflow-y:auto!important',
    '.profileOverviewCard{',
    'display:flex!important',
    'flex-direction:column!important',
    '.profileOverviewCard:nth-child(3)',
    'grid-column:1/-1!important',
    '.profileOverviewCard small{display:block!important',
    '.profileOverviewValue{display:block!important',
    '.profileOverviewHint{display:block!important',
    '.profileOverviewActions{display:none!important}',
    '.logoutProfile{',
    'margin:10px 0 0!important',
)
for marker in required:
    if marker not in out:
        fail('missing layout marker: ' + marker)

if module.patch_hub_text(out) != out:
    fail('patch_hub_text is not idempotent')

start = START.read_text(encoding='utf-8')
needle = 'python /app/web/fix_v310_profile_mobile.py /app/web/creator_hub_v156_component/index.html'
if needle not in start:
    fail('V310 startup patch not registered')
if start.index(needle) < start.index('python /app/web/test_v308_startup_contract.py /app'):
    fail('V310 must run after V308 canonical visual checks')
if start.index(needle) > start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V310 must run before production app generation')

print('V310 mobile Profile layout contract: PASS')
