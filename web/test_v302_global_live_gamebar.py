#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/app')
home = (root / 'web/home_v154_component/index.html').read_text(encoding='utf-8')
app = (root / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py').read_text(encoding='utf-8')

checks = [
    ('Home has Live nav', 'data-nav="live"' in home and '<span>Live</span>' in home),
    ('Home Live routes to Hub live', 'if(nav==="live")shellNav("hub",{section:"live"});' in home),
    ('Home Social nav removed', 'data-nav="social"' not in home),
    ('Page Game Bar has Live', 'data-section="live" data-active="live"' in app and '<span>Live</span>' in app),
    ('Page Game Bar routes Live through Hub', "activeKey==='live'" in app),
    ('Inclined broadcast icon present', 'transform="rotate(-8 16 16)"' in home and 'transform="rotate(-8 16 16)"' in app),
]
failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(('PASS' if ok else 'FAIL') + ': ' + name)
if failed:
    raise SystemExit('V302 failed: ' + ', '.join(failed))
print('V302 global Live Game Bar: PASS')
