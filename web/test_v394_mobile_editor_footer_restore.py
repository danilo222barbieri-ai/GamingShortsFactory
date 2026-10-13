#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
editor=root/'web'/'editor_2027_component'/'index.html'
chain=root/'web'/'fix_v373_creator_hub_spacing.py'
fix394=root/'web'/'fix_v394_mobile_editor_footer_restore.py'
fix393=root/'web'/'fix_v393_mobile_editor_clean_transport.py'
fix351=root/'web'/'fix_v351_footer_brand_glass.py'
for p in (shell,editor,chain,fix394,fix393,fix351):
    if not p.is_file(): raise SystemExit('V394 contract target missing: '+str(p))

s=shell.read_text(encoding='utf-8')
e=editor.read_text(encoding='utf-8')
c=chain.read_text(encoding='utf-8')
f394=fix394.read_text(encoding='utf-8')
f393=fix393.read_text(encoding='utf-8')
f351=fix351.read_text(encoding='utf-8')

def must(text,token,label):
    if token not in text: raise AssertionError(label+': '+token)

def forbid(text,token,label):
    if token in text: raise AssertionError(label+': '+token)

# The canonical footer must still be real, fixed and owned by V351/V343.
for token,label in [
    ('#gsf-global-footer','canonical footer selector'),
    ('position:fixed!important','fixed footer geometry'),
    ('bottom:0!important','bottom-locked footer'),
    ('gsf-v351-socials','footer social cluster'),
    ('gsf-v351-legal','footer legal cluster'),
]: must(f351,token,label)

# Root-cause regression: V393 must never create a layer below the Game Bar.
# Removing that layer later is racy because Streamlit components mount asynchronously.
for token,label in [
    ('v393EditorBottomMask','V393 bottom mask retired'),
    ('D.body.appendChild(mask)','V393 mask insertion retired'),
    ('mask.style.top','V393 mask positioning retired'),
    ('mask.style.display','V393 mask visibility retired'),
]:
    forbid(f393,token,label)
    forbid(s,token,'runtime '+label)

# V394 may force visibility while Editor is open, but it must not depend on deleting V393 later.
for token,label in [
    ('V394_MOBILE_EDITOR_FOOTER_RESTORE','V394 marker'),
    ('v394EditorFooterRestore','parent footer visibility style'),
    ('#gsf-global-footer','global footer target'),
    ('gsf-editor-overlay-v220','Editor-only active detection'),
]: must(s,token,label)
for token,label in [
    ('retireMask','late mask cleanup retired'),
    ('v393EditorBottomMask','V394 mask dependency retired'),
]: forbid(f394,token,label)

for token,label in [
    ('V394_MOBILE_EDITOR_FOOTER_RESTORE','V394 Editor marker'),
    ('v394MobileEditorFooterGap','Editor spacing style'),
    ('#ng27 .v393ChangeShort','Change Short target'),
    ('margin:5px auto 14px!important','visible Change Short breathing room'),
]: must(e,token,label)

for token,label in [
    ('fix_v394_mobile_editor_footer_restore.py','V394 runtime wiring'),
    ('test_v394_mobile_editor_footer_restore.py','V394 test wiring'),
]: must(c,token,label)

if '#gsf-global-gamebar{' in f394:
    raise AssertionError('V394 must not rewrite global Game Bar geometry')
if 'home_v154_component' in f394 or 'creator_hub_v156_component' in f394:
    raise AssertionError('V394 must stay bounded to Editor/footer visibility')
if 'position:fixed' in f394 and 'gsf-global-footer' in f394:
    raise AssertionError('V394 must leave footer geometry ownership to V351/V343')

print('V394 MOBILE EDITOR FOOTER ROOT-CAUSE CONTRACT: PASS')
