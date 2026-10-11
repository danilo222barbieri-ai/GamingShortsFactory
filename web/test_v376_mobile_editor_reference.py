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
    'approved compact player': '--v376-player-w:clamp(196px,56vw,224px)' in e,
    'no editor page scrolling': 'overflow:hidden!important;overscroll-behavior:none!important' in e,
    'single-screen cockpit rows': 'grid-template-rows:minmax(0,1fr) 48px 92px!important' in e,
    'actions immediately after player': 'grid-row:2!important' in e and 'height:48px!important' in e,
    'timeline immediately after actions': 'grid-row:3!important' in e and 'height:92px!important' in e,
    'editor title card visible': 'v376EditorTitleCard' in s and 'visibility:visible!important' in s,
    'compact editor title card': 'min-height:62px!important;height:62px!important' in s,
    'FULL header button preserved': 'v326HeaderFull' in s,
    'toolset preserved': all(x in e for x in ['data-panel="frame"','data-panel="caption"','data-panel="look"','data-panel="audio"','data-panel="vision"']),
    'create short preserved': 'v323CreateShort' in e,
    'save draft preserved': 'v323SaveDraft' in e,
    'caption auto pill': 'CC  Caption AUTO ✓' in e,
    'mobile only': '@media(max-width:760px)' in e,
    'old oversized player removed': '--v376-player-w:min(82vw,430px)' not in e,
    'old internal scrolling removed': 'padding:14px 12px 118px!important;overflow-y:auto!important' not in e,
}
failed=[name for name,ok in checks.items() if not ok]
if failed:
    raise AssertionError('V376 mobile editor reference contract failed: '+'; '.join(failed))
print('V376 MOBILE EDITOR REFERENCE CONTRACT: PASS',flush=True)
