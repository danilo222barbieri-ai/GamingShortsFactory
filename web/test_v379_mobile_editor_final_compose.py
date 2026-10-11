#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
editor=(root/'web'/'editor_2027_component'/'index.html').read_text(encoding='utf-8')
shell=(root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py').read_text(encoding='utf-8')

checks={
    'V379 editor marker':'V379_MOBILE_EDITOR_FINAL_COMPOSE' in editor,
    'smaller player':'--v376-player-w:clamp(180px,50vw,200px)' in editor,
    'internal Editor title':'v379EditorTitle' in editor and 'Game Editor' in editor,
    'Editor subtitle':'Il tuo gameplay resta nel progetto mentre modifichi.' in editor,
    'mobile title card visible':'#ng27.v326Mobile .topline' in editor and 'display:flex!important' in editor,
    'FULL button restored':'#ng27.v326Mobile .topline #zoomEditorBtn' in editor and '.mobileHide{display:inline!important}' in editor,
    'timeline controls unclipped':'#ng27.v326Mobile .cockpit>.timeline' in editor and 'overflow:visible!important' in editor,
    'actions preserved':all(x in editor for x in ['v323CreateShort','v323SaveDraft']),
    'V377 flicker guard preserved':'V377_IOS_FLICKER_GUARD' in editor,
    'V378 stack preserved':'V378_MOBILE_EDITOR_STACK' in editor,
    'parent cleanup marker':'V379_HIDE_DUPLICATE_FINAL_CTA' in shell,
    'old parent title hidden':'#gsf-editor-overlay-v220 .gsf-editor-head{display:none!important}' in shell,
    'duplicate CTA targeting':'HAI FINITO' in shell and 'CREA IL TUO SHORT' in shell,
    'only clickable duplicate targets':"querySelectorAll('button,a,[role=\"button\"]')" in shell,
}
failed=[name for name,ok in checks.items() if not ok]
if failed:
    raise AssertionError('V379 mobile Editor final compose contract failed: '+'; '.join(failed))
print('V379 MOBILE EDITOR FINAL COMPOSE CONTRACT: PASS',flush=True)
