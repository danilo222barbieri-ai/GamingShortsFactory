#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
FIX = ROOT / 'fix_v403_creator_hub_simplified.py'
COMPONENT = ROOT / 'creator_hub_v156_component' / 'index.html'

assert FIX.is_file(), 'V403 Creator Hub simplification patch is missing'
assert COMPONENT.is_file(), 'Creator Hub component is missing'

spec = importlib.util.spec_from_file_location('v403_creator_hub', FIX)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

fixture = '''<!doctype html><html><body>
<!-- V374_CREATOR_HUB_SPACING_LIVE_ISOLATION -->
<main id="hub">
<section class="view active" data-view="dashboard"><div class="dashboard"><div class="folders">
<button class="folder" data-folder="profile"><div><div class="folderTop"><span class="folderIcon">⌂</span></div><h2>Profilo</h2><p>Foto e nome del creator.</p></div></button>
<button class="folder" data-folder="projects"><div><h2>I miei progetti</h2><p>Bozze e Shorts completati nello stesso posto.</p></div></button>
<button class="folder" data-folder="live"><div><h2>Le mie live</h2></div></button>
<button class="folder" data-folder="social"><div><h2>Social</h2></div></button>
<button class="folder" data-folder="subscription"><div><h2>Abbonamento</h2></div></button>
</div></div></section>
<section class="view" data-view="profile"><div class="detailCard"><div class="profileOnlyScroller"><button class="logoutProfile">Disconnetti</button></div></div></section>
<section class="view" data-view="subscription"><div id="profilePlanName">FREE</div></section>
<section class="view" data-view="projects"><div class="detailCard"><div class="projectSection" data-project-pane="drafts"><div id="draftRows"><div class="row"><b>Bozza 1</b><span class="status">Adesso</span><button class="action" data-resume="draft_1">Continua</button></div></div></div><div class="projectSection" data-project-pane="shorts"><div id="shortRows"><div class="row shortRow"><b>Short 1</b><span class="status">Salvato</span><button class="action" data-short-download="short_1">Scarica</button><button class="action danger" data-short-delete="short_1">Elimina</button></div></div></div></div></section>
</main>
</body></html>'''

patched = mod.patch_text(fixture)
for token in (
    'V403_CREATOR_HUB_SIMPLIFIED',
    'data-folder="subscription"',
    'display:none!important',
    'grid-template-rows:repeat(4,minmax(0,1fr))',
    'Profilo e piano',
    'Bozze e Shorts',
    'v403PlanShortcut',
    'v403ProjectMenu',
    'v403ProjectMenuPanel',
    'RIPRENDI',
    'SCARICA',
    '✓ Salvata',
    '/drafts/delete?id=',
    'MutationObserver',
):
    assert token in patched, f'missing V403 simplified Creator Hub contract token: {token}'

assert mod.patch_text(patched) == patched, 'V403 patch must be idempotent'

# The runtime component is transformed by earlier Creator Hub patches before V403.
# Those patches may add classes/data attributes to <main>, so V403 must detect the
# Hub semantically instead of requiring the exact literal <main id="hub">.
transformed_fixture = fixture.replace(
    '<main id="hub">',
    '<main class="v357-hierarchy" data-v373-ready="1" id="hub" aria-live="polite">',
    1,
)
transformed_patched = mod.patch_text(transformed_fixture)
assert 'V403_CREATOR_HUB_SIMPLIFIED' in transformed_patched, 'V403 must accept transformed Hub <main> attributes/order'

real_patched = mod.patch_text(COMPONENT.read_text(encoding='utf-8'))
assert 'V403_CREATOR_HUB_SIMPLIFIED' in real_patched
assert 'v403CreatorHubSimplifiedRuntime' in real_patched
print('V403 CREATOR HUB SIMPLIFIED CONTRACT: PASS')
