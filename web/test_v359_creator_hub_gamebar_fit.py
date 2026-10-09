#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FIX = HERE / 'fix_v359_creator_hub_gamebar_fit.py'
START = HERE / 'start_web.sh'

FIXTURE = '''<!doctype html><html><head></head><body>
<div id="hub">
 <section class="view" data-view="dashboard"><div class="dashboard"></div></section>
 <section class="view" data-view="projects"><div class="detail"><div class="detailHead"><div class="detailHeadText"><h2 id="projectsViewTitle">Progetti</h2></div></div><div class="detailCard"><div class="folderScroller"><div class="hubProjectsGuide">Guida</div><div id="projectHubCards"></div><div class="projectSection" data-project-pane="drafts"><div class="projectSectionHead">BOZZE</div><div id="projectRows"></div><div id="draftRows"></div></div><div class="projectSection" data-project-pane="shorts"><div class="projectSectionHead">I MIEI SHORTS</div><div id="shortRows"></div></div></div></div></div></section>
 <section class="view" data-view="live"><div class="v357LiveRoot"></div><div class="v357LiveDetail"></div></section>
 <section class="view" data-view="profile"><div class="profileReferenceScroll"><div class="profileReferenceEdit"></div><div class="profilePlanRef"></div><div class="profileSocialRef"><div class="profileSocialRows"></div></div></div></section>
</div>
<!-- V357_CREATOR_HUB_HIERARCHY -->
</body></html>'''

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    hub = root / 'index.html'
    hub.write_text(FIXTURE, encoding='utf-8')
    subprocess.run([sys.executable, str(FIX), str(hub)], check=True)
    out = hub.read_text(encoding='utf-8')

    required = [
        'V359_CREATOR_HUB_GAMEBAR_FIT',
        'v359CreatorHubGamebarFit',
        '--v359-gamebar-gap:6px',
        '.v359ProjectDirect .detailHead{display:none!important}',
        '.v359ProjectActivePane .projectSectionHead{display:none!important}',
        'grid-template-rows:auto minmax(0,1fr)!important',
        'padding:0 4px var(--v359-gamebar-gap)!important',
        '#hub .view[data-view="dashboard"] .dashboard{padding-bottom:var(--v359-gamebar-gap)!important}',
        'grid-template-rows:repeat(2,minmax(180px,42%))!important',
        'align-content:space-between!important',
        '.v359ProjectHeroDuplicate{display:none!important}',
        'v359ProjectDirect',
        'v359ProjectActivePane',
        'v359ProjectHeroDuplicate',
        "\\d+\\s+(?:bozze|shorts)\\s+salvat",
        "padding:8px 4px var(--v359-gamebar-gap)!important",
        'grid-template-rows:minmax(0,1fr)!important',
    ]
    for token in required:
        assert token in out, f'missing V359 contract token: {token}'

    assert 'padding-bottom:96px!important' not in out[out.index('v359CreatorHubGamebarFit'):], 'V359 must not re-add the obsolete internal Game Bar reserve'
    assert 'padding-bottom:104px!important' not in out[out.index('v359CreatorHubGamebarFit'):], 'V359 must not re-add the obsolete internal Game Bar reserve'
    assert '@media(max-width:767px)' in out, 'V359 must stay mobile-only'

    once = out
    subprocess.run([sys.executable, str(FIX), str(hub)], check=True)
    assert hub.read_text(encoding='utf-8') == once, 'V359 patch must be restart-safe'

start = START.read_text(encoding='utf-8')
assert 'fix_v359_creator_hub_gamebar_fit.py' in start, 'startup must apply V359'
assert 'test_v359_creator_hub_gamebar_fit.py' in start, 'startup must verify V359'
assert start.index('fix_v357_creator_hub_hierarchy.py') < start.index('fix_v359_creator_hub_gamebar_fit.py'), 'V359 must run after V357'

print('V359 CREATOR HUB GAMEBAR FIT: PASS', flush=True)
