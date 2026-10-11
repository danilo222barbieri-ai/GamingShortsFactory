#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
editor=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
shell=(root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py').read_text(encoding='utf-8')
pipeline=(root/'web'/'fix_v373_creator_hub_spacing.py').read_text(encoding='utf-8')

checks={
    'single V380 editor layer':'V380_MOBILE_EDITOR_UNIFIED' in editor,
    'legacy V376 layer removed':'V376_MOBILE_EDITOR_REFERENCE' not in editor,
    'legacy V378 layer removed':'V378_MOBILE_EDITOR_STACK' not in editor,
    'legacy V379 layer removed':'V379_MOBILE_EDITOR_FINAL_COMPOSE' not in editor,
    'player is primary but fits viewport':'--v380-player-w:clamp(205px,56vw,230px)' in editor,
    'single clean stack':'grid-template-rows:auto 50px 122px!important' in editor,
    'one editor heading only':'V380_HIDE_LEGACY_TOPLINE_CHILDREN' in editor and 'Game Editor' in editor,
    'editor subtitle':'Il tuo gameplay resta nel progetto mentre modifichi.' in editor,
    'FULL control kept':'#zoomEditorBtn' in editor and 'FULL' in editor,
    'timeline readable':'height:122px!important' in editor and 'overflow:hidden!important' in editor,
    'paired actions preserved':all(x in editor for x in ['v323CreateShort','v323SaveDraft']),
    'tool docks preserved':all(x in editor for x in ['v326LeftDock','v326RightDock','v326PlaybackDock']),
    'anti flicker stable layers':'V380_IOS_STABLE_COMPOSITE' in editor and 'transition:none!important' in editor,
    'duplicate final CTA cleanup scans document':'V380_HIDE_DUPLICATE_FINAL_CTA' in shell and 'document.querySelectorAll' in shell,
    'old parent editor title hidden':'#gsf-editor-overlay-v220 .gsf-editor-head' in shell,
    'pipeline runs only V380 final editor pass':'fix_v380_mobile_editor_unified.py' in pipeline and all(x not in pipeline for x in ['fix_v376_mobile_editor_reference.py','fix_v378_mobile_editor_stack.py','fix_v379_mobile_editor_final_compose.py']),
}
failed=[name for name,ok in checks.items() if not ok]
if failed: raise AssertionError('V380 clean mobile Editor contract failed: '+'; '.join(failed))
print('V380 CLEAN MOBILE EDITOR CONTRACT: PASS',flush=True)
