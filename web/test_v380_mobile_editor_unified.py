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
    'compact fixed player':'--v380-player-w:clamp(172px,46vw,188px)' in editor,
    'one-column compact stack':'grid-template-rows:auto 48px 108px!important' in editor,
    'editor heading':'v380EditorTitle' in editor and 'Game Editor' in editor,
    'editor subtitle':'Il tuo gameplay resta nel progetto mentre modifichi.' in editor,
    'FULL control':'#ng27.v326Mobile .topline #zoomEditorBtn' in editor and '.mobileHide{display:inline!important' in editor,
    'timeline fully visible':'#ng27.v326Mobile .cockpit>.timeline' in editor and 'height:108px!important' in editor and 'overflow:visible!important' in editor,
    'paired actions preserved':all(x in editor for x in ['v323CreateShort','v323SaveDraft']),
    'tool docks preserved':all(x in editor for x in ['v326LeftDock','v326RightDock','v326PlaybackDock']),
    'anti flicker stable layers':'V380_IOS_STABLE_COMPOSITE' in editor and '-webkit-backdrop-filter:none!important' in editor and 'transition:none!important' in editor,
    'parent cleanup unified':'V380_HIDE_DUPLICATE_FINAL_CTA' in shell,
    'old parent editor title hidden':'#gsf-editor-overlay-v220 .gsf-editor-head{display:none!important}' in shell,
    'pipeline runs V380':'fix_v380_mobile_editor_unified.py' in pipeline and 'test_v380_mobile_editor_unified.py' in pipeline,
    'pipeline no longer runs V376':'fix_v376_mobile_editor_reference.py' not in pipeline,
    'pipeline no longer runs V378':'fix_v378_mobile_editor_stack.py' not in pipeline,
    'pipeline no longer runs V379':'fix_v379_mobile_editor_final_compose.py' not in pipeline,
}
failed=[name for name,ok in checks.items() if not ok]
if failed:
    raise AssertionError('V380 unified mobile Editor contract failed: '+'; '.join(failed))
print('V380 UNIFIED MOBILE EDITOR CONTRACT: PASS',flush=True)
