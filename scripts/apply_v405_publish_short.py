#!/usr/bin/env python3
"""Deterministic V405 patch for the final Crea Short publication screen."""
from pathlib import Path
import re
import sys

MARKER = "# V405_PUBLISH_SHORT_SIMPLE"

HELPER_BLOCK = r'''
# V405_PUBLISH_SHORT_SIMPLE

def _gsf_render_publish_page_v405():
    """Final video-first publication surface. Keeps the current project in session."""
    _pb = (
        st.session_state.get("publication_preview_bytes")
        or st.session_state.get("inline_final_bytes")
        or st.session_state.get("editor_output_bytes")
        or st.session_state.get("preview_bytes")
    )
    _duration = float(
        st.session_state.get("auto_clip_duration")
        or st.session_state.get("publication_duration")
        or 0.0
    )
    _duration_label = f"{_duration:.0f}s" if _duration > 0 else "Short"

    st.markdown("""
    <style>
    .v405-publish-shell{max-width:760px;margin:0 auto;padding:6px 10px 18px;text-align:center}
    .v405-publish-shell h1{margin:0;font-size:clamp(1.85rem,4vw,2.8rem)!important;font-weight:950;letter-spacing:-.045em;color:#0D2A66!important}
    .v405-publish-meta{margin:8px 0 14px;color:#7185A6;font-size:.82rem;font-weight:800;letter-spacing:.01em}
    .v405-published{display:inline-flex;align-items:center;gap:7px;padding:7px 12px;border-radius:999px;background:#DDF8EB;color:#168B65;font-size:.78rem;font-weight:900;margin-bottom:8px}
    [data-testid="stFileUploader"]{display:none!important}
    .gsf-step{display:none!important}
    div[data-testid="stPopover"] button, .v405-publish-shell~div button{border-radius:16px!important}
    @media(max-width:760px){.v405-publish-shell{padding-top:2px}.v405-publish-shell h1{font-size:1.8rem!important}.v405-publish-meta{font-size:.76rem}}
    </style>
    <div class="v405-publish-shell">
      <h1>Il tuo Short è pronto</h1>
      <div class="v405-publish-meta">1080×1920 · 60 fps · __DURATION__</div>
    </div>
    """.replace("__DURATION__", _duration_label), unsafe_allow_html=True)

    if _pb:
        st.video(_pb)
    else:
        st.info("Anteprima pronta non disponibile: il progetto resta salvato e modificabile.")

    _edit_col, _save_col = st.columns(2, gap="small")
    with _edit_col:
        if st.button("✎ Modifica", use_container_width=True, key="v405_edit"):
            st.session_state["publication_return_ready"] = True
            st.session_state["publication_ready"] = False
            st.session_state["project_view"] = "editor"
            st.session_state["current_view"] = "editor"
            if st.session_state.get("publication_source") == "ai_clip":
                st.session_state["editor_source"] = "ai"
                if st.session_state.get("auto_clip_scelta") is not None:
                    st.session_state["editor_ai_start"] = float(st.session_state["auto_clip_scelta"])
                if st.session_state.get("auto_clip_duration") is not None:
                    st.session_state["editor_ai_duration"] = float(st.session_state["auto_clip_duration"])
            st.rerun()
    with _save_col:
        if st.button("♡ Salva", use_container_width=True, key="v405_save"):
            st.session_state["publication_saved"] = True
            st.session_state["project_saved_as_draft"] = True
            st.toast("✓ Salvato nei tuoi Progetti")

    if st.session_state.get("publication_saved"):
        st.caption("✓ Salvato nei tuoi Progetti")

    _publish_col, _download_col = st.columns([1.65, 1], gap="small")
    with _publish_col:
        with st.popover("PUBBLICA", use_container_width=True):
            st.markdown("### Pubblica il tuo Short")
            st.caption("Scegli dove pubblicarlo. I testi sono già pronti e puoi modificarli solo se vuoi.")

            _socials = (
                ("YouTube", "youtube"),
                ("TikTok", "tiktok"),
                ("Instagram", "instagram"),
                ("Facebook", "facebook"),
            )
            _selected = []
            _scols = st.columns(2, gap="small")
            for _idx, (_label, _slug) in enumerate(_socials):
                _connected = bool(st.session_state.get(f"{_slug}_connected") or st.session_state.get(f"social_{_slug}_connected"))
                with _scols[_idx % 2]:
                    _pick = st.checkbox(
                        f"{_label}{' ✓' if _connected else ' · + Collega'}",
                        value=_connected,
                        key=f"v405_social_{_slug}",
                    )
                    if _pick:
                        _selected.append(_slug)
                    if _pick and not _connected:
                        st.session_state["social_connect_target"] = _slug

            _default_title = st.session_state.get("publication_title") or "La giocata che non doveva riuscire"
            _default_desc = st.session_state.get("publication_description") or "Il momento migliore della partita, pronto da condividere."
            _default_tags = st.session_state.get("publication_hashtags") or "#gaming #shorts #gameplay"
            with st.expander("Modifica testi", expanded=False):
                _title = st.text_input("Titolo", value=_default_title, key="v405_title")
                _desc = st.text_area("Descrizione", value=_default_desc, height=82, key="v405_desc")
                _tags = st.text_input("Hashtag", value=_default_tags, key="v405_tags")

            if st.button("PUBBLICA ORA", type="primary", use_container_width=True, key="v405_publish_now"):
                if not _selected:
                    st.warning("Scegli almeno un social")
                else:
                    st.session_state["publication_title"] = _title
                    st.session_state["publication_description"] = _desc
                    st.session_state["publication_hashtags"] = _tags
                    st.session_state["publication_targets"] = list(_selected)
                    st.session_state["publication_submit_requested"] = True
                    st.session_state["publication_status"] = "requested"
                    st.toast("Pubblicazione inviata")
                    st.rerun()

    with _download_col:
        with st.popover("↓ Scarica", use_container_width=True):
            st.markdown("### Scarica Short")
            st.caption("MP4 · 1080×1920 · Alta qualità")
            if _pb:
                st.download_button(
                    "SCARICA",
                    _pb,
                    file_name="gaming_short.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                    key="v405_download_file",
                )
            else:
                st.button("SCARICA", disabled=True, use_container_width=True, key="v405_download_disabled")

    if st.session_state.get("publication_status") == "published":
        _targets = st.session_state.get("publication_targets") or []
        _names = {"youtube":"YouTube", "tiktok":"TikTok", "instagram":"Instagram", "facebook":"Facebook"}
        _status = "   ·   ".join(f"{_names.get(x, x)} ✓" for x in _targets) or "Pubblicazione pronta ✓"
        st.markdown(f'<div style="text-align:center;margin-top:10px"><span class="v405-published">✓ PUBBLICATO</span><div style="color:#7185A6;font-size:.78rem;font-weight:800">{_status}</div></div>', unsafe_allow_html=True)
        _new_col, _shorts_col = st.columns(2, gap="small")
        with _new_col:
            if st.button("Crea un altro Short", use_container_width=True, key="v405_new_short"):
                for _key in ("publication_ready", "publication_source", "publication_preview_bytes", "publication_status", "publication_targets", "publication_submit_requested"):
                    st.session_state.pop(_key, None)
                st.session_state["project_view"] = "home"
                st.rerun()
        with _shorts_col:
            if st.button("Vai ai miei Shorts", use_container_width=True, key="v405_my_shorts"):
                st.session_state["project_view"] = "shorts"
                st.session_state["current_view"] = "creator_hub"
                st.rerun()
'''

OLD_BLOCK = r'''    if st.session_state.get("publication_ready") and st.session_state.get("publication_source")=="ai_clip":
        st.markdown("#### 🎬 Esporta")
        _pb=st.session_state.get("publication_preview_bytes")
        if _pb:
            st.download_button("⬇️ SCARICA CLIP",_pb,"gaming_short_ai.mp4","video/mp4",use_container_width=True,key="export_ai_selected")
        st.markdown("#### 🚀 Pubblicazione")
        st.success("Clip scelta e pronta per la pubblicazione.")
        st.caption("Qui collegheremo titolo, descrizione, piattaforma e pubblicazione diretta.")
'''

EARLY_ANCHOR = r'''if video:

    # Player pulito: solo il lettore nativo, senza etichette o controlli aggiuntivi.
'''

EARLY_HOOK = r'''if video:

    if st.session_state.get("publication_ready"):
        _gsf_render_publish_page_v405()
        st.stop()

    # Player pulito: solo il lettore nativo, senza etichette o controlli aggiuntivi.
'''

LEGACY_REMOVED = "    # V405: publication surface is rendered at the start of the video flow.\n"


def patch_text(text: str) -> str:
    if MARKER in text:
        return text
    anchor = 'st.set_page_config('
    if anchor not in text:
        raise ValueError('V405 helper anchor not found')
    legacy = re.compile(
        r'(?ms)^    if st\.session_state\.get\("publication_ready"\) and st\.session_state\.get\("publication_source"\)=="ai_clip":\n'
        r'.*?^        st\.caption\("Qui collegheremo titolo, descrizione, piattaforma e pubblicazione diretta\."\)\n'
    )
    if not legacy.search(text):
        raise ValueError('V405 legacy publication block not found')
    if EARLY_ANCHOR not in text:
        raise ValueError('V405 early video-flow anchor not found')
    text = text.replace(anchor, HELPER_BLOCK + '\n\n' + anchor, 1)
    text = text.replace(EARLY_ANCHOR, EARLY_HOOK, 1)
    text = legacy.sub(LEGACY_REMOVED, text, count=1)
    return text


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    target = Path(argv[0] if argv else 'app.py')
    original = target.read_text(encoding='utf-8')
    patched = patch_text(original)
    if patched != original:
        target.write_text(patched, encoding='utf-8')
        print(f'V405 publish patch applied: {target}')
    else:
        print(f'V405 publish patch already present: {target}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
