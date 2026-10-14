#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'scripts' / 'apply_v405_publish_short.py'
COMPONENT = ROOT / 'web' / 'publish_short_v405_component' / 'index.html'

assert PATCH.is_file(), 'V405 publish patch is missing'
assert COMPONENT.is_file(), 'V405 publish component contract is missing'

spec = importlib.util.spec_from_file_location('v405_publish_short', PATCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

fixture = '''import streamlit as st

def render_gsf_player(source_path, key, *, scene=False, start_seconds=None):
    return None

st.set_page_config(page_title="Gaming Shorts Factory")

def legacy_area():
    if st.session_state.get("publication_ready") and st.session_state.get("publication_source")=="ai_clip":
        st.markdown("#### 🎬 Esporta")
        _pb=st.session_state.get("publication_preview_bytes")
        if _pb:
            st.download_button("⬇️ SCARICA CLIP",_pb,"gaming_short_ai.mp4","video/mp4",use_container_width=True,key="export_ai_selected")
        st.markdown("#### 🚀 Pubblicazione")
        st.success("Clip scelta e pronta per la pubblicazione.")
        st.caption("Qui collegheremo titolo, descrizione, piattaforma e pubblicazione diretta.")

if video:

    # Player pulito: solo il lettore nativo, senza etichette o controlli aggiuntivi.
    print("player")

print("unrelated survives")
'''

patched = mod.patch_text(fixture)
for token in (
    'V405_PUBLISH_SHORT_SIMPLE',
    'def _gsf_render_publish_page_v405',
    'Il tuo Short è pronto',
    'PUBBLICA',
    'Scarica',
    'Modifica',
    'Salva',
    'YouTube',
    'TikTok',
    'Instagram',
    'Facebook',
    'Modifica testi',
    'PUBBLICA ORA',
    '1080×1920',
    '60 fps',
    'Salvato nei tuoi Progetti',
    'st.stop()',
):
    assert token in patched, f'missing V405 publication contract token: {token}'

assert 'Qui collegheremo titolo, descrizione, piattaforma e pubblicazione diretta.' not in patched
assert 'print("unrelated survives")' in patched
assert 'if video:\n\n    if st.session_state.get("publication_ready"):\n        _gsf_render_publish_page_v405()\n        st.stop()' in patched, 'publication hook must run at the start of the video flow'
assert '[data-testid="stFileUploader"]{display:none!important}' in patched
assert 'st.session_state["publication_status"] = "requested"' in patched
assert 'Scegli almeno un social' in patched
assert mod.patch_text(patched) == patched, 'V405 patch must be idempotent'

html = COMPONENT.read_text(encoding='utf-8')
for token in (
    'V405_PUBLISH_SHORT_SIMPLE',
    'Il tuo Short è pronto',
    'data-action="publish"',
    'data-action="download"',
    'data-action="edit"',
    'data-action="save"',
    'publishSheet',
    'downloadSheet',
    'YouTube', 'TikTok', 'Instagram', 'Facebook',
):
    assert token in html, f'missing V405 component token: {token}'

print('V405 PUBLISH SHORT SIMPLE CONTRACT: PASS')
