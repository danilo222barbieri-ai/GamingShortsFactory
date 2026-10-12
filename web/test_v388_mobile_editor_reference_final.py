#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
e=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
s=(root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py').read_text(encoding='utf-8')
p=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
checks={
 'marker':'V388_MOBILE_EDITOR_REFERENCE_FINAL' in e,
 'old editor geometry removed':'V386_MOBILE_EDITOR_REFERENCE_LOCK' not in e and 'V387_MOBILE_EDITOR_PLAYER_VISIBILITY' not in e,
 'stable mobile player':'--v388-player-h:clamp(340px,48dvh,455px)' in e,
 'title card':'v388EditorTitleCard' in e,
 'actions':'V388_ACTIONS_REFERENCE' in e,
 'timeline':'V388_TIMELINE_REFERENCE' in e,
 'thumbs':'V388_REAL_TIMELINE_THUMBS' in e,
 'tools':'V388_TOOLS_OVER_VIDEO' in e,
 'fullscreen':'V388_FULLSCREEN_WORKSPACE' in e,
 'iframe fill':'V388_PARENT_IFRAME_FILL' in s,
 'pipeline':'fix_v388_mobile_editor_reference_final.py' in p,
}
failed=[k for k,v in checks.items() if not v]
if failed: raise AssertionError('V388 contract failed: '+'; '.join(failed))
print('V388 MOBILE EDITOR REFERENCE FINAL CONTRACT: PASS',flush=True)
