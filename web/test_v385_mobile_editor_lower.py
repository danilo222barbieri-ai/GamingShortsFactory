#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
e=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
p=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
checks={'marker':'V385_MOBILE_EDITOR_LOWER' in e,'shell bottom aligned':'align-items:flex-end!important' in e,'cockpit bottom aligned':'align-content:end!important' in e,'pipeline':'fix_v385_mobile_editor_lower.py' in p}
failed=[k for k,v in checks.items() if not v]
if failed:raise AssertionError('V385 contract failed: '+'; '.join(failed))
print('V385 MOBILE EDITOR LOWER CONTRACT: PASS',flush=True)
