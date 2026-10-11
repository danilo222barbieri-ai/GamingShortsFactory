#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
editor=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
shell=(root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py').read_text(encoding='utf-8')
pipeline=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')

checks={
 'single V380 editor layer':'V380_MOBILE_EDITOR_UNIFIED' in editor,
 'approved visual reference':'V380_APPROVED_VISUAL_REFERENCE' in editor,
 'no editor title card':'v380EditorTitle' not in editor and 'Il tuo gameplay resta nel progetto mentre modifichi.' not in editor,
 'player dominates mobile':'--v380-player-w:min(68vw,286px)' in editor,
 'tools outside player':'V380_TOOLS_OUTSIDE_PLAYER' in editor,
 'timeline before actions':'V380_TIMELINE_BEFORE_ACTIONS' in editor,
 'editing controls row':'V380_EDIT_CONTROLS' in editor and all(x in editor for x in ['Zoom','Luce','Contrasto','Velocità','Volume']),
 'paired actions preserved':all(x in editor for x in ['v323CreateShort','v323SaveDraft']),
 'timeline readable':'height:170px!important' in editor,
 'anti flicker stable layers':'V380_IOS_STABLE_COMPOSITE' in editor,
 'duplicate final CTA cleanup':'V380_HIDE_DUPLICATE_FINAL_CTA' in shell,
 'parent editor head hidden':'#gsf-editor-overlay-v220 .gsf-editor-head' in shell,
 'pipeline runs V380':'fix_v380_mobile_editor_unified.py' in pipeline,
}
failed=[name for name,ok in checks.items() if not ok]
if failed: raise AssertionError('V380 approved visual contract failed: '+'; '.join(failed))
print('V380 APPROVED VISUAL EDITOR CONTRACT: PASS',flush=True)
