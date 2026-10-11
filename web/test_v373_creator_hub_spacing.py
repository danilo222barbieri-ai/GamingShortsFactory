#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
FIX = ROOT / 'fix_v373_creator_hub_spacing.py'
assert FIX.is_file(), 'V373 Creator Hub spacing patch is missing'

spec = importlib.util.spec_from_file_location('v373', FIX)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

fixture = '''<!doctype html><html><body>
<div id="hub"><div class="stage">
<section class="view" data-view="projects"><div class="detail"><div class="detailHead"><h2 id="projectsViewTitle">Bozze</h2></div><div id="draftRows"><div class="empty">Nessuna bozza salvata</div></div><div id="shortRows"><div class="empty">Nessuno Short salvato</div></div></div></section>
<section class="view" data-view="live"></section>
<section class="view" data-view="profile"></section>
</div></div>
</body></html>'''

patched = mod.patch_text(fixture)
for token in (
    'V373_CREATOR_HUB_HEADER_BREATH',
    '#hub>.stage>.view',
    'top:16px!important',
    'height:auto!important',
    'v373DraftsOnly',
    '#shortRows{display:none!important}',
    "title==='bozze'",
):
    assert token in patched, f'missing V373 contract token: {token}'

assert mod.patch_text(patched) == patched, 'V373 patch must be idempotent'
assert 'Nessuna bozza salvata' in patched, 'draft empty state must remain available'
assert 'Nessuno Short salvato' in patched, 'patch hides Short block via route CSS; it must not rewrite data content'
print('V373 CREATOR HUB HEADER BREATH + DRAFTS CLEANUP CONTRACT: PASS')
