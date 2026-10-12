#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
e=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
p=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
checks={
 'marker':'V383_MOBILE_EDITOR_POSITION' in e,
 'no legacy 46vw player':'--v383-player-w:min(84vw,344px)' in e,
 'single compact grid':'grid-template-rows:auto auto auto!important' in e,
 'timeline immediately after player':'grid-row:2!important' in e,
 'actions immediately after timeline':'grid-row:3!important' in e,
 'no giant editor floor':'min-height:0!important' in e,
 'fallback full covered':'.gsfFullscreenFallback' in e,
 'pipeline':'fix_v383_mobile_editor_position.py' in p,
}
failed=[k for k,v in checks.items() if not v]
if failed:raise AssertionError('V383 contract failed: '+'; '.join(failed))
print('V383 MOBILE EDITOR POSITION CONTRACT: PASS',flush=True)
