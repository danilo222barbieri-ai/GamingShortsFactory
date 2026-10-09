#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
FIX = ROOT / 'fix_v362_project_pages_cleanup.py'

assert FIX.is_file(), 'V362 cleanup patch is missing'

spec = importlib.util.spec_from_file_location('v362', FIX)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

fixture = '''<!doctype html><html><body>
<div id="hub"><section class="view" data-view="projects"><div class="detail">
<div class="detailHead"><div class="detailHeadText"><h2 id="projectsViewTitle">I miei Shorts</h2><p id="projectsViewSubtitle">Tutti gli Shorts completati e salvati nel Creator Hub.</p></div></div>
<div class="detailCard"><div class="folderScroller">
<div class="hubContextGuide hubProjectsGuide">Qui trovi i tuoi progetti</div>
<div class="legacyBrand">GAMING SHORTS FACTORY | Creator Hub</div>
<div class="projectSection" data-project-pane="shorts"><div class="projectHero"><h2>I miei Shorts</h2><p>I tuoi Shorts salvati</p></div><div class="rows" id="shortRows"><div class="empty">Nessuno Short archiviato.</div></div></div>
<div class="projectSection" data-project-pane="drafts"><div class="projectHero"><h2>Bozze</h2></div><div class="rows" id="draftRows"><div class="empty">Nessun progetto in lavorazione salvato.</div></div></div>
</div></div></div></section></div>
<!-- V359_CREATOR_HUB_GAMEBAR_FIT -->
</body></html>'''

patched = mod.patch_text(fixture)
for token in (
    'V362_PROJECT_PAGES_CLEANUP',
    'v362ProjectClean',
    'v362RedundantProjectBlock',
    'v362EmptyCollection',
    'hubProjectsGuide',
    '#shortRows',
    '#draftRows',
    "view.classList.toggle('v362CollectionEmpty',removableEmpty)",
    "el.classList.toggle('v362EmptyCollection',removableEmpty)",
    "rows.classList.toggle('v362EmptyCollection',removableEmpty)",
):
    assert token in patched, f'missing V362.1 contract token: {token}'

# Cleanup must not churn its own MutationObserver by removing and immediately
# re-adding classes on every callback.
direct_block = patched[patched.index('function clean(){'):patched.index('const scroller=q', patched.index('function clean(){'))]
assert "qa('.v362RedundantProjectBlock').forEach((n)=>n.classList.remove('v362RedundantProjectBlock'));" not in direct_block
assert "qa('.v362EmptyCollection').forEach((n)=>n.classList.remove('v362EmptyCollection'));" not in direct_block

# The existing top page title remains; V362 removes only redundant content inside the scroller.
assert 'id="projectsViewTitle"' in patched
assert 'detailHead' in patched

print('V362.1 PROJECT PAGES CLEANUP CONTRACT: PASS')
