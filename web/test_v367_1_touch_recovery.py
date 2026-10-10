#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
startup = root / 'web' / 'fix_v362_project_pages_cleanup.py'
text = startup.read_text(encoding='utf-8')

checks = {
    'V367 arbiter is not invoked from startup': "fix_v367_single_active_surface.py" not in text,
    'V367 arbiter regression test is not invoked from startup': "test_v367_single_active_surface.py" not in text,
    'startup summary no longer claims V367 active': "V367 single active surface applied" not in text,
    'V365 bootstrap remains active': "fix_v365_creator_hub_bootstrap.py" in text,
    'V366 state stability remains active': "fix_v366_creator_hub_state_stability.py" in text,
    'V366 state contract remains active': "test_v366_creator_hub_state_stability.py" in text,
}

failed = False
for label, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + label)
    failed |= not ok

if failed:
    raise SystemExit(1)
print('V367.1 TOUCH RECOVERY CONTRACT: PASS')
