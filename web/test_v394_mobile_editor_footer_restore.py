#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
editor=root/'web'/'editor_2027_component'/'index.html'
chain=root/'web'/'fix_v373_creator_hub_spacing.py'
fix=root/'web'/'fix_v394_mobile_editor_footer_restore.py'
for p in (shell,editor,chain,fix):
    if not p.is_file(): raise SystemExit('V394 contract target missing: '+str(p))

s=shell.read_text(encoding='utf-8')
e=editor.read_text(encoding='utf-8')
c=chain.read_text(encoding='utf-8')
f=fix.read_text(encoding='utf-8')

def must(text,token,label):
    if token not in text: raise AssertionError(label+': '+token)

for token,label in [
    ('V394_MOBILE_EDITOR_FOOTER_RESTORE','V394 marker'),
    ('v394EditorFooterRestore','parent footer restore style'),
    ('#gsf-global-footer','global footer target'),
    ('#v393EditorBottomMask','old V393 mask target'),
    ('.remove()','old mask removal'),
    ('gsf-editor-overlay-v220','Editor-only active detection'),
]: must(s,token,label)

for token,label in [
    ('v394MobileEditorFooterGap','Editor spacing style'),
    ('#ng27 .v393ChangeShort','Change Short target'),
    ('margin:5px auto 9px!important','Change Short bottom breathing room'),
]: must(e,token,label)

for token,label in [
    ('fix_v394_mobile_editor_footer_restore.py','V394 runtime wiring'),
    ('test_v394_mobile_editor_footer_restore.py','V394 test wiring'),
]: must(c,token,label)

if '#gsf-global-gamebar{' in f or '#gsf-global-footer{' in f:
    raise AssertionError('V394 must not rewrite global Game Bar/Footer geometry')
if 'home_v154_component' in f or 'creator_hub_v156_component' in f:
    raise AssertionError('V394 must stay bounded to Editor cleanup')
if 'position:fixed' in f and 'gsf-global-footer' in f:
    raise AssertionError('V394 must leave footer position ownership to V351/V343')

print('V394 MOBILE EDITOR FOOTER RESTORE CONTRACT: PASS')
