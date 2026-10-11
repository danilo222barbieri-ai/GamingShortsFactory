#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V376_MOBILE_EDITOR_REFERENCE'
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
editor=root/'web'/'editor_2027_component'/'index.html'
shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'

if not editor.is_file() or not shell.is_file():
    raise SystemExit('V376 runtime files missing')

e=editor.read_text(encoding='utf-8')
s=shell.read_text(encoding='utf-8')

checks={
    'reference marker': MARK in e,
    'large mobile player': '--v376-player-w:min(82vw,430px)' in e,
    'editor title card': 'v376EditorTitleCard' in s,
    'editor subtitle': 'Il tuo gameplay resta nel progetto mentre modifichi.' in s,
    'FULL header button preserved': 'v326HeaderFull' in s,
    'toolset preserved': all(x in e for x in ['data-panel="frame"','data-panel="caption"','data-panel="look"','data-panel="audio"','data-panel="vision"']),
    'create short preserved': 'v323CreateShort' in e,
    'save draft preserved': 'v323SaveDraft' in e,
    'timeline outside player': 'grid-row:3!important' in e,
    'caption auto pill': 'CC  Caption AUTO ✓' in e,
    'mobile only': '@media(max-width:760px)' in e,
}
failed=[name for name,ok in checks.items() if not ok]
if failed:
    raise AssertionError('V376 mobile editor reference contract failed: '+'; '.join(failed))
print('V376 MOBILE EDITOR REFERENCE CONTRACT: PASS',flush=True)
