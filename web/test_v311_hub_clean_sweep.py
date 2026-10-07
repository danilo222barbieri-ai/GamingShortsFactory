#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'
PATCH = WEB / 'fix_v311_hub_clean_sweep.py'
HUB = WEB / 'creator_hub_v156_component' / 'index.html'
START = WEB / 'start_web.sh'


def fail(message):
    print('[FAIL]', message)
    raise SystemExit(1)


def ok(message):
    print('[ OK ]', message)


if not PATCH.exists():
    fail('V311 patch file missing')
if not HUB.exists():
    fail('Creator Hub HTML missing')
if not START.exists():
    fail('start_web.sh missing')

spec = importlib.util.spec_from_file_location('gsf_v311_hub_clean_sweep', PATCH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
if not hasattr(module, 'patch_hub_text'):
    fail('patch_hub_text() missing')
ok('pure patch_hub_text helper present')

source = HUB.read_text(encoding='utf-8')
patched = module.patch_hub_text(source)

required = (
    'V311 HUB CLEAN SWEEP',
    '.folder[data-folder="social"]{display:none!important}',
    'grid-template-rows:repeat(3,minmax(0,1fr))!important',
    '.profileOverviewCard[data-profile-overview="subscription"]{display:none!important}',
    '.profileOverviewActions{display:none!important}',
    '.profileOverviewCard[data-profile-overview="social"]{grid-column:1/-1!important}',
    '#projectRows{display:none!important}',
    'class="liveBack"',
    'function closeLiveFolder',
    'live-subview',
)
for marker in required:
    if marker not in patched:
        fail('missing V311 marker: ' + marker)
    ok('found: ' + marker)

for forbidden in (
    'Le tue live Twitch compariranno qui come mini-cartelle, una per ogni diretta.',
    '<div class="livePane active" data-live-pane="twitch">',
):
    if forbidden in patched:
        fail('stale Live content remains: ' + forbidden)
ok('Live landing page is clean and non-duplicated')

# The old current-project renderer must no longer be visible on mobile.
if '#hub .view[data-view="drafts"] #projectRows{display:none!important}' not in patched:
    fail('Drafts current project/stats container is still exposed on mobile')
ok('Drafts only exposes saved draft list on mobile')

# Idempotency matters because startup patches may be retried locally.
patched_twice = module.patch_hub_text(patched)
if patched_twice != patched:
    fail('V311 patch is not idempotent')
ok('patch is idempotent')

start = START.read_text(encoding='utf-8')
needle = 'python /app/web/fix_v311_hub_clean_sweep.py /app/web/creator_hub_v156_component/index.html'
if needle not in start:
    fail('V311 startup patch is not registered')
if start.index(needle) < start.index('python /app/web/fix_v307_mobile_visual_source.py /app'):
    fail('V311 must run after the canonical V307 visual pass')
if start.index(needle) > start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V311 must run before production app generation')
ok('startup order is correct')

print('\nV311 HUB CLEAN SWEEP: PASS')
