#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V378_MOBILE_EDITOR_STACK'
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
editor=root/'web'/'editor_2027_component'/'index.html'

if not editor.is_file():
    raise SystemExit('V378 Editor target missing')

e=editor.read_text(encoding='utf-8')
checks={
    'stack marker': MARK in e,
    'cockpit no longer stretches to viewport': 'height:auto!important;min-height:0!important' in e,
    'rows follow content': 'grid-template-rows:auto 48px 92px!important' in e,
    'stack starts at top': 'align-content:start!important' in e,
    'player stays first': 'grid-row:1!important' in e,
    'actions stay second': 'grid-row:2!important' in e and 'v323EditorActions' in e,
    'timeline stays third': 'grid-row:3!important' in e and 'class="timeline"' in e,
    'create short preserved': 'v323CreateShort' in e,
    'save draft preserved': 'v323SaveDraft' in e,
    'V377 flicker guard preserved': 'V377_IOS_FLICKER_GUARD' in e,
}
failed=[name for name,ok in checks.items() if not ok]
if failed:
    raise AssertionError('V378 mobile Editor stack contract failed: '+'; '.join(failed))
print('V378 MOBILE EDITOR STACK CONTRACT: PASS',flush=True)
