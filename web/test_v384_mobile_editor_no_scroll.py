#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
e=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
p=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
checks={
 'marker':'V384_MOBILE_EDITOR_NO_SCROLL' in e,
 'viewport locked':'height:calc(100dvh - 154px)!important' in e,
 'no page scroll':'overflow:hidden!important' in e,
 'small player':'--v384-player-h:min(48dvh,390px)' in e,
 'compact timeline':'height:82px!important' in e,
 'compact actions':'height:42px!important' in e,
 'full hides parent gamebar':'V384_HIDE_PARENT_GAMEBAR_FULL' in e,
 'full keeps editor tools':'.gsfFullscreenFallback .v326ToolDock' in e,
 'pipeline':'fix_v384_mobile_editor_no_scroll.py' in p,
}
failed=[k for k,v in checks.items() if not v]
if failed:raise AssertionError('V384 contract failed: '+'; '.join(failed))
print('V384 MOBILE EDITOR NO SCROLL CONTRACT: PASS',flush=True)
