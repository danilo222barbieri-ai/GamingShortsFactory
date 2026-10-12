#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
e=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
p=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
checks={
 'V381 marker':'V381_MOBILE_EDITOR_COMPACT_FULL' in e,
 'small player':'--v381-player-w:min(46vw,188px)' in e,
 'frame integrated':'V381_FRAME_IN_VIDEO' in e,
 'all tools integrated':'V381_TOOLS_IN_VIDEO' in e,
 'tiny actions':'V381_TINY_ACTIONS' in e and 'height:34px!important' in e,
 'real fullscreen preserved':'requestFullscreen' in e and 'webkitRequestFullscreen' in e,
 'fullscreen side controls':'V381_FULLSCREEN_SIDE_CONTROLS' in e,
 'fullscreen hides actions timeline':'V381_FULLSCREEN_CLEAN' in e,
 'pipeline runs V381':'fix_v381_mobile_editor_compact_full.py' in p,
}
failed=[k for k,v in checks.items() if not v]
if failed:raise AssertionError('V381 compact/full Editor contract failed: '+'; '.join(failed))
print('V381 MOBILE EDITOR COMPACT/FULL CONTRACT: PASS',flush=True)
