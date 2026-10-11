#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
editor=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
shell=(root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py').read_text(encoding='utf-8')
pipeline=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')
checks={
 'single V380 editor layer':'V380_MOBILE_EDITOR_UNIFIED' in editor,
 'compact approved composition':'V380_COMPACT_REFERENCE' in editor,
 'no editor title':'#ng27.v326Mobile .topline{display:none!important}' in editor,
 'compact player':'--v380-player-w:min(58vw,238px)' in editor,
 'tools inside player':'V380_TOOLS_INSIDE_PLAYER' in editor,
 'audio preserved':'audioBtn' in editor,
 'timeline compact':'V380_COMPACT_TIMELINE' in editor and 'height:118px!important' in editor,
 'timeline before actions':'grid-template-rows:auto 118px 54px!important' in editor,
 'no extra edit controls':'v380EditControls' not in editor and all(x not in editor for x in ['>Zoom<','>Luce<','>Contrasto<','>Velocità<','>Volume<']),
 'paired actions preserved':all(x in editor for x in ['v323CreateShort','v323SaveDraft']),
 'anti flicker':'V380_IOS_STABLE_COMPOSITE' in editor,
 'duplicate final CTA cleanup':'V380_HIDE_DUPLICATE_FINAL_CTA' in shell,
 'pipeline runs V380':'fix_v380_mobile_editor_unified.py' in pipeline,
}
failed=[n for n,v in checks.items() if not v]
if failed: raise AssertionError('V380 compact Editor contract failed: '+'; '.join(failed))
print('V380 COMPACT MOBILE EDITOR CONTRACT: PASS',flush=True)
