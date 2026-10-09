#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
PATCH = ROOT / 'web' / 'fix_v308_mobile_ai_flow.py'
AI = ROOT / 'web' / 'ai_v221_component' / 'index.html'
START = ROOT / 'web' / 'start_web.sh'


def fail(message):
    print(f'[FAIL] {message}')
    raise SystemExit(1)


def ok(message):
    print(f'[ OK ] {message}')


if not PATCH.exists():
    fail('V308 patch file missing')
if not AI.exists():
    fail('AI component missing')
if not START.exists():
    fail('start_web.sh missing')

spec = importlib.util.spec_from_file_location('gsf_v308_mobile_ai_flow', PATCH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
if not hasattr(module, 'patch_ai_text'):
    fail('patch_ai_text() missing')
ok('pure patch_ai_text helper present')

source = AI.read_text(encoding='utf-8')
patched = module.patch_ai_text(source)

required = (
    'V308 MOBILE AI FLOW',
    '@media(max-width:760px)',
    '.journeySteps{display:none!important}',
    'id="momentFullscreen"',
    'id="momentFullscreenVideo"',
    'id="closeMomentFullscreen"',
    'function openMomentPreview',
    'function closeMomentPreview',
    'window.matchMedia("(max-width:760px)")',
    'momentNextActions',
    'scrollIntoView',
)
for marker in required:
    if marker not in patched:
        fail(f'missing V308 behavior marker: {marker}')
    ok(f'found marker: {marker}')

if 'grid-template-columns:1fr!important' not in patched:
    fail('mobile moments are not promoted to a readable single-column layout')
ok('mobile moments use readable single-column layout')

if patched.count('V308 MOBILE AI FLOW') != 2:
    fail('V308 patch is not idempotent or marker count is unexpected')
patched_twice = module.patch_ai_text(patched)
if patched_twice != patched:
    fail('patch_ai_text is not idempotent')
ok('patch is idempotent')

start = START.read_text(encoding='utf-8')
needle = 'python /app/web/fix_v308_mobile_ai_flow.py /app/web/ai_v221_component/index.html'
if needle not in start:
    fail('V308 startup patch is not registered')

# The old runtime generated V293 directly. V343 now owns the final V293-safe
# generation step, so accept either anchor and require V308 to run before it.
generation_anchors = (
    'python /app/web/apply_v343_v293_compat.py',
    'python /app/web/apply_v293_render_memory_guard.py',
)
generation_anchor = next((item for item in generation_anchors if item in start), None)
if generation_anchor is None:
    fail('production app generation anchor is missing from startup')
if start.index(needle) > start.index(generation_anchor):
    fail('V308 patch must run before production app generation')
ok('startup order is correct')

print('\nV308 MOBILE AI FLOW CONTRACT: PASS')
