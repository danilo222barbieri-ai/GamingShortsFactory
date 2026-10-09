#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FIX = HERE / 'fix_v361_mobile_regression_repair.py'
START = HERE / 'start_web.sh'

HUB_FIXTURE = '''<!doctype html><html><head></head><body>
<main id="hub" class="v357NoLegacyTop"><header class="top">Creator Hub</header><div class="stage">
<section class="view active" data-view="profile"><div class="profileReferenceScroll"><div class="profileReferenceBrand">BRAND</div><div class="profileReferenceCard profileReferenceEdit"></div><div class="profileReferenceCard profilePlanRef"></div><div class="profileReferenceCard profileSocialRef"></div></div></section>
<section class="view" data-view="projects"><div class="detail"><div class="detailHead"></div><div class="detailCard"><div class="folderScroller"><div class="hubProjectsGuide"></div><div id="projectHubCards"></div><div class="projectSection" data-project-pane="drafts"><div id="draftRows"><div class="empty"></div></div></div><div class="projectSection" data-project-pane="shorts"><div id="shortRows"><div class="empty"></div></div></div></div></div></div></section>
<section class="view" data-view="live"><div class="detail"><div class="detailCard"><div class="folderScroller"><div class="v357LiveRoot"><button class="v357LiveFolder"></button><button class="v357LiveFolder"></button></div><div class="v357LiveDetail"></div></div></div></div></section>
</div></main><!-- V359_CREATOR_HUB_GAMEBAR_FIT --></body></html>'''

EDITOR_FIXTURE = '''<!doctype html><html><head></head><body>
<div id="ng27" class="v326Mobile v360Reference"><div class="shell"><div class="v360EditorHeader"><div class="v360EditorTitle"></div><button class="v360FullProxy">FULL</button></div><div class="cockpit"><div class="stageWrap"><div class="stage r916" id="stage"><div class="v325PlayerMeta"><span class="v325TimeChip"></span><span class="v325RatioChip">9:16</span></div><div class="v326Meta"><span class="v326Time"></span><span class="v326Ratio">9:16</span></div><button id="zoomEditorBtn"><span>FULL</span></button><div class="v325PlaybackDock"></div><div class="v326PlaybackDock"></div></div></div><div class="v323EditorActions" id="v323EditorActions"></div><div class="timeline"></div></div></div></div><!-- V360_MOBILE_EDITOR_REFERENCE --></body></html>'''

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    hub = root / 'hub.html'
    editor = root / 'editor.html'
    hub.write_text(HUB_FIXTURE, encoding='utf-8')
    editor.write_text(EDITOR_FIXTURE, encoding='utf-8')
    subprocess.run([sys.executable, str(FIX), str(hub), str(editor)], check=True)
    hub_out = hub.read_text(encoding='utf-8')
    editor_out = editor.read_text(encoding='utf-8')

    for token in (
        'V361_MOBILE_REGRESSION_REPAIR',
        'v361MobileHubRepair',
        '#hub>.top{display:none!important}',
        'padding:10px 3px 104px!important',
        'overflow-y:auto!important',
        '.v359ProjectActivePane',
        'min-height:220px!important',
        '.v357LiveRoot',
        'grid-template-rows:repeat(2,148px)!important',
        '.profileReferenceBrand{display:none!important}',
    ):
        assert token in hub_out, f'missing V361 Hub repair token: {token}'

    for token in (
        'V361_MOBILE_REGRESSION_REPAIR',
        'v361MobileEditorRepair',
        '.v325PlayerMeta{display:none!important}',
        '.v325PlaybackDock{display:none!important}',
        '.v360FullProxy{display:none!important}',
        'padding-bottom:96px!important',
        '#zoomEditorBtn{',
        'display:flex!important',
        '.v326Ratio{margin-right:44px!important}',
    ):
        assert token in editor_out, f'missing V361 Editor repair token: {token}'

    assert hub_out.count('V361_MOBILE_REGRESSION_REPAIR') == 1
    assert editor_out.count('V361_MOBILE_REGRESSION_REPAIR') == 1
    once_hub, once_editor = hub_out, editor_out
    subprocess.run([sys.executable, str(FIX), str(hub), str(editor)], check=True)
    assert hub.read_text(encoding='utf-8') == once_hub, 'V361 Hub patch must be restart-safe'
    assert editor.read_text(encoding='utf-8') == once_editor, 'V361 Editor patch must be restart-safe'

start = START.read_text(encoding='utf-8')
assert 'fix_v361_mobile_regression_repair.py' in start
assert 'test_v361_mobile_regression_repair.py' in start
assert start.index('fix_v359_creator_hub_gamebar_fit.py') < start.index('fix_v361_mobile_regression_repair.py')
assert start.index('fix_v360_mobile_editor_reference.py') < start.index('fix_v361_mobile_regression_repair.py')

print('V361 MOBILE HUB + EDITOR REGRESSION REPAIR: PASS', flush=True)
