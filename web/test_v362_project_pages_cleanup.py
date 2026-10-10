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
    'V371_OBSERVER_STABILITY',
    'function v362SetClass',
    'v362ProjectClean',
    'v362RedundantProjectBlock',
    'v362EmptyCollection',
    'hubProjectsGuide',
    '#shortRows',
    '#draftRows',
    "v362SetClass(view,'v362CollectionEmpty',removableEmpty)",
    "v362SetClass(el,'v362EmptyCollection',removableEmpty)",
    "v362SetClass(rows,'v362EmptyCollection',removableEmpty)",
):
    assert token in patched, f'missing V362/V371 contract token: {token}'

# The callback observes class/style, so every class mutation it performs must
# be conditional. Re-applying the patch must also be a true no-op.
assert mod.patch_text(patched) == patched
for forbidden in (
    "view.classList.remove('v362ProjectClean','v362CollectionEmpty')",
    "view.classList.toggle('v362ProjectClean',direct)",
    "view.classList.remove('v362CollectionEmpty')",
    "rows.classList.toggle('v362EmptyCollection',removableEmpty)",
    "view.classList.toggle('v362CollectionEmpty',removableEmpty)",
):
    assert forbidden not in patched, f'unstable observer mutation remains: {forbidden}'

# Upgrade an already-installed legacy V362 block instead of treating its marker
# as proof that the runtime is safe.
legacy = patched.replace("  const V371_OBSERVER_STABILITY=true;\n", "").replace(
    "    v362SetClass(view,'v362ProjectClean',direct);",
    "    view.classList.toggle('v362ProjectClean',direct);",
)
legacy = legacy.replace('V371_OBSERVER_STABILITY', 'V362_LEGACY_OBSERVER')
upgraded = mod.patch_text(legacy)
assert 'V371_OBSERVER_STABILITY' in upgraded
assert "view.classList.toggle('v362ProjectClean',direct)" not in upgraded

# The existing top page title remains; V362 removes only redundant content inside the scroller.
assert 'id="projectsViewTitle"' in patched
assert 'detailHead' in patched

print('V362.2/V371 PROJECT PAGES CLEANUP CONTRACT: PASS')
