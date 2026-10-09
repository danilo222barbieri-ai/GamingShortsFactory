#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FIX = HERE / 'fix_v359_creator_hub_gamebar_fit.py'
START = HERE / 'start_web.sh'

FIXTURE = '''<!doctype html><html><head></head><body>
<div id="hub"><header class="top">Creator Hub</header><div class="stage">
 <section class="view" data-view="dashboard"><div class="dashboard"></div></section>
 <section class="view" data-view="projects"><div class="detail"><div class="detailHead"><div class="detailHeadText"><h2 id="projectsViewTitle">Progetti</h2><p></p></div></div><div class="detailCard"><div class="folderScroller"><div class="hubProjectsGuide">Guida</div><div id="projectHubCards"></div><div class="projectSection" data-project-pane="drafts"><div class="projectSectionHead">BOZZE</div><div id="projectRows"></div><div id="draftRows"><div class="empty"></div></div></div><div class="projectSection" data-project-pane="shorts"><div class="projectSectionHead">I MIEI SHORTS</div><div id="shortRows"><div class="empty"></div></div></div></div></div></div></section>
 <section class="view" data-view="live"><div class="detail"><div class="detailCard"><div class="folderScroller"><div class="v357LiveRoot"></div><div class="v357LiveDetail"><div class="v357LiveDetailBody"></div></div></div></div></div></section>
 <section class="view" data-view="profile"><div class="profileReferenceScroll"><div class="profileReferenceBrand"></div><div class="profileReferenceCard profileReferenceEdit"></div><div class="profileReferenceCard profilePlanRef"></div><div class="profileReferenceCard profileSocialRef"><div class="profileSocialRows"></div></div></div></section>
 <section class="view" data-view="social"><div class="detail"><div class="detailCard"><div class="folderScroller"></div></div></div></section>
 <section class="view" data-view="subscription"><div class="detail"><div class="detailCard"><div class="folderScroller"></div></div></div></section>
</div></div>
<!-- V357_CREATOR_HUB_HIERARCHY -->
</body></html>'''

with tempfile.TemporaryDirectory() as td:
    hub = Path(td) / 'index.html'
    hub.write_text(FIXTURE, encoding='utf-8')
    subprocess.run([sys.executable, str(FIX), str(hub)], check=True)
    out = hub.read_text(encoding='utf-8')

    required = [
        'V359_CREATOR_HUB_GAMEBAR_FIT',
        'GSF_V361_HUB_REPAIR',
        'v359CreatorHubGamebarFit',
        '#hub>.top{display:none!important}',
        '.profileReferenceBrand{display:none!important}',
        'padding:10px 3px 104px!important',
        'overflow-y:auto!important',
        '.v359ProjectDirect .detailHead{display:flex!important}',
        '.v359ProjectActivePane #draftRows>.empty',
        'min-height:220px!important',
        'grid-template-rows:repeat(2,148px)!important',
        'height:148px!important',
        'padding:0 2px 104px!important',
        'v359ProjectDirect',
        'v359ProjectActivePane',
        'v359ProjectHeroDuplicate',
        "\\d+\\s+(?:bozze|shorts)\\s+salvat",
    ]
    for token in required:
        assert token in out, f'missing repaired V359/V361 contract token: {token}'

    tail = out[out.index('v359CreatorHubGamebarFit'):]
    assert '--v359-gamebar-gap:6px' not in tail, 'the 6px-only reserve caused content to sit under the global shell'
    assert 'grid-template-rows:repeat(2,minmax(0,1fr))!important' not in tail, 'Live providers must not stretch to half the viewport'
    assert 'grid-template-rows:42px minmax(146px,1.25fr)' not in tail, 'Profile cards must not stretch to fill the viewport'
    assert '@media(max-width:767px)' in out

    once = out
    subprocess.run([sys.executable, str(FIX), str(hub)], check=True)
    assert hub.read_text(encoding='utf-8') == once, 'V359 repaired patch must be restart-safe'

start = START.read_text(encoding='utf-8')
assert 'fix_v359_creator_hub_gamebar_fit.py' in start
assert 'test_v359_creator_hub_gamebar_fit.py' in start
assert start.index('fix_v357_creator_hub_hierarchy.py') < start.index('fix_v359_creator_hub_gamebar_fit.py')

print('V361 CREATOR HUB MOBILE REGRESSION REPAIR: PASS', flush=True)
