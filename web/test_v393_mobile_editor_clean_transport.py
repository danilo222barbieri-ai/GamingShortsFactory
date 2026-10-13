#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
editor=root/'web'/'editor_2027_component'/'index.html'
shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
chain=root/'web'/'fix_v373_creator_hub_spacing.py'
patch_file=root/'web'/'fix_v393_mobile_editor_clean_transport.py'
for p in (editor,shell,chain,patch_file):
    if not p.is_file():raise SystemExit('V393 contract target missing: '+str(p))
e=editor.read_text(encoding='utf-8');s=shell.read_text(encoding='utf-8');c=chain.read_text(encoding='utf-8');patch=patch_file.read_text(encoding='utf-8')

def must(text,token,label):
    if token not in text:raise AssertionError(label+': '+token)

def forbid(text,token,label):
    if token in text:raise AssertionError(label+': '+token)

for token,label in [
 ('V393_MOBILE_EDITOR_CLEAN_TRANSPORT','V393 marker'),
 ('--v389-player-w:min(78vw,304px,calc((100dvh - 225px) * 9 / 16))','larger height-safe player'),
 ('#ng27 .timeline{display:none!important}','single transport owner'),
 ('v393TransportGlass','clean transport glass'),
 ('v389PlaybackDock','play/pause retained'),
 ('v389PlayerProgress','progress retained'),
 ('v393PosterFrame','paused poster'),
 ("video.addEventListener('pause',capturePoster",'poster on pause'),
 ("video.addEventListener('seeked'",'poster on seek'),
 ("video.addEventListener('play',hidePoster",'poster clears on play'),
 ('CAMBIA SHORT','change short action'),
 ("target:'ai'",'change short AI route'),
 ("#v391SaveDraft",'change short saves current work'),
 ('v389TopBar','top essential controls retained'),
 ('v389ToolDock','side essential controls retained'),
]: must(e,token,label)

for token,label in [
 ('v393EditorShellCleanup','parent shell cleanup'),
 ('#gsf-editor-overlay-v220.is-open','Editor-only shell scope'),
 ('v393EditorChromeGone','mobile X cleanup'),
 ('#gsf-global-header,#gsf-global-gamebar,#gsf-global-footer','global chrome exclusion'),
]: must(s,token,label)

for token,label in [
 ('v393EditorBottomMask','bottom mask must not exist'),
 ('D.body.appendChild(mask)','mask insertion must not exist'),
 ('mask.style.top','mask positioning must not exist'),
 ('mask.style.display','mask visibility must not exist'),
]:
    forbid(patch,token,label)
    forbid(s,token,'runtime '+label)

for token,label in [
 ('fix_v393_mobile_editor_clean_transport.py','V393 runtime wiring'),
 ('test_v393_mobile_editor_clean_transport.py','V393 test wiring'),
]: must(c,token,label)

if "window.addEventListener('resize'" in patch or 'window.addEventListener("resize"' in patch:
    raise AssertionError('V393 must not reintroduce mobile resize loops')
if '#gsf-global-gamebar{' in patch or '#gsf-global-footer{' in patch:
    raise AssertionError('V393 must not rewrite global Game Bar/Footer geometry')
if 'gsf-creator-hub-live-v160' in patch or 'home_v154_component' in patch:
    raise AssertionError('V393 must stay bounded to the Editor')

print('V393 MOBILE EDITOR CLEAN TRANSPORT + FOOTER SAFETY CONTRACT: PASS')
