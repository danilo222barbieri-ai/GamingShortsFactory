#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PATCH = ROOT / 'web' / 'fix_v308_mobile_master.py'

spec = importlib.util.spec_from_file_location('gsf_v308_mobile_master', PATCH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

sample = '''<!doctype html><html><head><style>
/* V287 PROFILE OVERVIEW
   Real account summary cards inside Profile, optimized for mobile and desktop. */
#hub .profileOverviewCard small{display:block!important}
#hub .profileOverviewValue{display:block!important}
#hub .profileOverviewHint{display:block!important}
@media(max-width:760px){#hub .profileOverviewGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important}}
/* END V287 PROFILE OVERVIEW */
</style></head><body><main id="hub"></main></body></html>'''

out = module.canonicalize_text('hub', sample)
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
