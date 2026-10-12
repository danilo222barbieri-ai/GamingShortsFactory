#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
e=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
s=(root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py').read_text(encoding='utf-8')
p=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
checks={
 'marker':'V387_MOBILE_EDITOR_DEMO_LOCK' in e,
 'old V386 removed':'V386_MOBILE_EDITOR_REFERENCE_LOCK' not in e,
 'stable player height':'--v387-player-h:clamp(350px,52dvh,470px)' in e,
 'player actions timeline order':'grid-template-rows:auto 48px 108px!important' in e,
 'compact actions':'V387_ACTIONS_COMPACT' in e,
 'reference timeline':'V387_TIMELINE_REFERENCE' in e,
 'tools over player':'V387_TOOLS_OVER_VIDEO' in e,
 'fullscreen workspace':'V387_FULLSCREEN_WORKSPACE' in e,
 'no motion flicker':'transition:none!important' in e and 'animation:none!important' in e,
 'parent title card':'V387_EDITOR_TITLE_CARD' in s,
 'duplicate outer cta removed':'V387_HIDE_OUTER_SHORT_CTA' in s,
 'fullscreen hides parent chrome':'V387_FULLSCREEN_PARENT_CLEAN' in e,
 'pipeline':'fix_v387_mobile_editor_demo_lock.py' in p,
}
failed=[k for k,v in checks.items() if not v]
if failed: raise AssertionError('V387 demo-reference contract failed: '+'; '.join(failed))
print('V387 MOBILE EDITOR DEMO-REFERENCE CONTRACT: PASS',flush=True)
