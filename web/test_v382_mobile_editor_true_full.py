#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
e=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
p=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
checks={
 'marker':'V382_MOBILE_EDITOR_TRUE_FULL' in e,
 'compact timeline proportional':'width:min(84vw,344px)' in e,
 'compact actions proportional':'width:min(84vw,344px)' in e,
 'true full viewport':'width:100vw!important;height:100dvh!important' in e,
 'full stage covers viewport':'object-fit:cover!important' in e,
 'full chrome hidden':'V382_FULL_HIDE_PARENT_CHROME' in e,
 'fallback z max':"2147483647" in e,
 'pipeline':'fix_v382_mobile_editor_true_full.py' in p,
}
failed=[k for k,v in checks.items() if not v]
if failed:raise AssertionError('V382 contract failed: '+'; '.join(failed))
print('V382 MOBILE EDITOR TRUE FULL CONTRACT: PASS',flush=True)
