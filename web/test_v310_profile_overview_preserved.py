#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
V308 = ROOT / 'web' / 'fix_v308_mobile_master.py'
V287 = ROOT / 'web' / 'fix_v287_profile_overview.py'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

master = load('gsf_v308_mobile_master', V308)
profile = load('gsf_v287_profile_overview', V287)

sample = '<!doctype html><html><head><style>' + profile.CSS + '</style></head><body><main id="hub"></main></body></html>'
out = master.canonicalize_text('hub', sample)

required = (
    '#hub .profileOverviewCard small{display:block!important}',
    '#hub .profileOverviewValue{display:block!important}',
    '#hub .profileOverviewHint{display:block!important}',
    'grid-template-columns:repeat(2,minmax(0,1fr))!important',
)
missing = [marker for marker in required if marker not in out]
if missing:
    print('V310 RED: V308 canonicalization stripped required Profile overview CSS:')
    for marker in missing:
        print(' -', marker)
    raise SystemExit(1)

print('V310 profile overview preservation contract: PASS')
