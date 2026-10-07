#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/app')
home = (root / 'web/home_v154_component/index.html').read_text(encoding='utf-8')
embed = (root / 'web/home_v154_embed.py').read_text(encoding='utf-8')

checks = [
    ('V301 desktop marker exists', 'V301 HOME DESK REBALANCE' in home),
    ('desktop-only breakpoint exists', '@media (min-width:761px)' in home),
    ('desktop uploader enlarged', '--gsf-desk-ring:clamp(270px,min(23vw,36vh),360px)' in home),
    ('desktop content widened', '--gsf-desk-content:clamp(740px,68vw,940px)' in home),
    ('ambient mural hidden on desktop', '#home154 .muralAmbient{display:none!important}' in home),
    ('left mural moved outward', 'left:clamp(34px,4.6vw,86px)!important' in home),
    ('right mural moved outward', 'right:clamp(34px,4.6vw,86px)!important' in home),
    ('Home cache bumped to V301', 'gsf_home_v154_live_301' in embed),
]

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(('PASS' if ok else 'FAIL') + ': ' + name)
if failed:
    raise SystemExit('V301 Home desk rebalance failed: ' + ', '.join(failed))
print('V301 Home desk rebalance: PASS')
