#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'
PATCH = WEB / 'fix_v309_mobile_ai_flow.py'
AI = WEB / 'ai_v221_component' / 'index.html'
START = WEB / 'start_web.sh'


def fail(message):
    print(f'[FAIL] {message}')
    raise SystemExit(1)


def ok(message):
    print(f'[ OK ] {message}')


if not PATCH.exists():
    fail('V309 patch file missing')
if not AI.exists():
    fail('AI component missing')
if not START.exists():
    fail('start_web.sh missing')

spec = importlib.util.spec_from_file_location('gsf_v309_mobile_ai_flow', PATCH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
if not hasattr(module, 'patch_ai_text'):
    fail('patch_ai_text() missing')
ok('pure patch_ai_text helper present')

# V309 runs after V308 canonicalization in production, so verify against the
# same canonicalized AI HTML rather than only the raw source file.
master_path = WEB / 'fix_v308_mobile_master.py'
master_spec = importlib.util.spec_from_file_location('gsf_v308_mobile_master', master_path)
master = importlib.util.module_from_spec(master_spec)
master_spec.loader.exec_module(master)
source = master.canonicalize_text('ai', AI.read_text(encoding='utf-8'))
patched = module.patch_ai_text(source)

required = (
    'V309 MOBILE AI FLOW',
    '@media(max-width:760px)',
    '.journeySteps{display:none!important}',
    'overflow-y:auto!important',
    'id="momentFullscreen"',
    'id="momentFullscreenVideo"',
    'id="closeMomentFullscreen"',
    'function openMomentPreview',
    'function closeMomentPreview',
    'window.matchMedia("(max-width:760px)")',
    'momentNextActions',
    'scrollIntoView',
    'requestFullscreen',
    'webkitEnterFullscreen',
)
for marker in required:
    if marker not in patched:
        fail(f'missing V309 behavior marker: {marker}')
    ok(f'found marker: {marker}')

if 'grid-template-columns:1fr!important' not in patched:
    fail('mobile moments are not promoted to a readable single-column layout')
ok('mobile moments use readable single-column layout')

# Desktop must keep the V308 canonical layout. The V309 behavior itself must
# remain gated inside a max-width rule / runtime matchMedia check.
if '@media(min-width' in patched:
    fail('V309 reintroduced a desktop-only media query')
ok('no desktop-only layout introduced')

if patched.count('V309 MOBILE AI FLOW') != 2:
    fail('V309 marker count is unexpected')
patched_twice = module.patch_ai_text(patched)
if patched_twice != patched:
    fail('patch_ai_text is not idempotent')
ok('patch is idempotent')

start = START.read_text(encoding='utf-8')
needle = 'python /app/web/fix_v309_mobile_ai_flow.py /app/web/ai_v221_component/index.html'
if needle not in start:
    fail('V309 startup patch is not registered')
if start.index(needle) < start.index('python /app/web/test_v308_startup_contract.py /app'):
    fail('V309 must run only after the canonical V308 checks')
if start.index(needle) > start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V309 must run before production app generation')
ok('startup order is correct')

print('\nV309 MOBILE AI FLOW CONTRACT: PASS')
