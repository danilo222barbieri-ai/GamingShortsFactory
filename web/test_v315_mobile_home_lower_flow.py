#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PATCH = ROOT / 'web' / 'fix_v315_mobile_home_lower_flow.py'
START = ROOT / 'web' / 'start_web.sh'


def fail(msg: str) -> None:
    print('[FAIL]', msg)
    raise SystemExit(1)


def ok(msg: str) -> None:
    print('[ OK ]', msg)


if not PATCH.is_file():
    fail('V315 mobile Home lower-flow patch missing')

spec = importlib.util.spec_from_file_location('v315_mobile_home_lower_flow', PATCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

sample = '''<html><head><style>@media(max-width:760px){#home154 .bottomNav{margin-bottom:34px!important}}</style></head><body><div id="home154"><div class="stage"><div class="muralAmbient muralGuide">x</div><div class="rings"></div></div><div class="features"></div><nav class="bottomNav"></nav><footer class="siteFooter"></footer></div></body></html>'''
patched = mod.patch_text(sample)

checks = {
    'style marker': 'id="v315MobileHomeLowerFlow"',
    'mobile only': '@media(max-width:760px)',
    'shared lower shift': '--gsf-home-lower-shift:clamp(14px,2.5vh,22px)!important',
    'uploader lowered': '#home154 .rings',
    'central mural lowered': 'bottom:calc(1px - var(--gsf-home-lower-shift))!important',
    'CTA cards follow': '#home154 .features',
    'Game Bar follows': '#home154 .bottomNav',
    'old footer gap reduced': 'margin-bottom:12px!important',
    'short viewport guard': '--gsf-home-lower-shift:12px!important',
}
for name, marker in checks.items():
    if marker not in patched:
        fail(name + ' missing')
    ok(name)

if mod.patch_text(patched) != patched:
    fail('V315 patch is not idempotent')
ok('V315 patch is idempotent')

if START.is_file():
    start = START.read_text(encoding='utf-8')
    patch_marker = 'python /app/web/fix_v315_mobile_home_lower_flow.py /app/web/home_v154_component/index.html'
    test_marker = 'python /app/web/test_v315_mobile_home_lower_flow.py /app'
    if patch_marker not in start or test_marker not in start:
        fail('V315 startup registration missing')
    if start.index(patch_marker) < start.index('python /app/web/fix_v314_hub_context_fill.py'):
        fail('V315 must run after V314')
    if start.index(test_marker) < start.index(patch_marker):
        fail('V315 test must run after patch')
    ok('V315 startup order')

print('\nV315 MOBILE HOME LOWER FLOW CONTRACT: PASS')
