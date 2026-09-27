from pathlib import Path
import re

src = Path('/app/GamingShortsFactory_V79_SESSION_SOCIAL_BETA.py')
out = Path('/app/GamingShortsFactory_V80_UI_AUTOSUB_BETA.py')
s = src.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise RuntimeError(f'V80 patch target not found: {label}')
    s = s.replace(old, new, 1)

# ------------------------------------------------------------------
# V80 UI FIX — Streamlit chrome / iPhone light controls / compact editor
# ------------------------------------------------------------------
_ui_fix = r'''
st.markdown("""
<style id="gsf-v80-ui-fix">
/* Elimina la fascia vuota di Streamlit sopra l'app (desktop + mobile). */
[data-testid="stHeader"],
header[data-testid="stHeader"]{
    height:0 !important;
    min-height:0 !important;
    max-height:0 !important;
    visibility:hidden !important;
    overflow:hidden !important;
    background:transparent !important;
}
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu{
    display:none !important;
}
[data-testid="stAppViewContainer"]{
    padding-top:0 !important;
}
[data-testid="stAppViewContainer"] > .main{
    padding-top:0 !important;
}
.block-container{
    padding-top:.30rem !important;
}

/* Safari/iOS non deve trasformare i controlli dell'Editor in pulsanti scuri. */
:root, html, body, .stApp, [data-testid="stAppViewContainer"]{
    color-scheme:light !important;
}

@media(max-width:750px){
    html, body, .stApp, [data-testid="stAppViewContainer"]{
        background:#F7FBFE !important;
    }
    .block-container{
        padding-top:.20rem !important;
        padding-left:.72rem !important;
        padding-right:.72rem !important;
    }

    /* Segmenti Formato / Sottotitoli: contrasto leggibile su iPhone. */
    .st-key-editor_format button,
    .st-key-editor_sub_mode_v18 button{
        background:#FFFFFF !important;
        color:#17324A !important;
        border-color:#BFD7E8 !important;
        min-height:2.65rem !important;
        font-weight:700 !important;
        box-shadow:none !important;
    }
    .st-key-editor_format button[aria-pressed="true"],
    .st-key-editor_sub_mode_v18 button[aria-pressed="true"]{
        background:#EAF5FD !important;
        color:#0E2D46 !important;
        border-color:#56AEDD !important;
    }
    .st-key-editor_format button p,
    .st-key-editor_sub_mode_v18 button p{
        color:inherit !important;
    }

    /* Popover INQUADRATURA / REGOLAZIONI / POSIZIONE. */
    [data-testid="stPopover"] > button,
    [data-testid="stPopover"] > button p{
        background:#FFFFFF !important;
        color:#17324A !important;
    }
    [data-testid="stPopover"] > button{
        border:1px solid #BFD7E8 !important;
        min-height:2.70rem !important;
        height:auto !important;
        padding:.35rem .70rem !important;
        border-radius:14px !important;
        box-shadow:none !important;
    }

    /* Bottoni Editor: compatti ma ancora comodi da toccare. */
    .st-key-reset_main_all_v29 button,
    .st-key-editor_transcribe_scene_v18 button,
    .st-key-editor_use_changes_v54 button,
    .st-key-retry_auto_sub_v80 button{
        min-height:2.75rem !important;
        height:auto !important;
        padding:.38rem .75rem !important;
        border-radius:14px !important;
    }

    /* Rimuove le frecce decorative che su mobile sembravano pulsanti "avanti". */
    .st-key-reset_main_all_v29 button::before,
    .st-key-editor_transcribe_scene_v18 button::before,
    .st-key-editor_use_changes_v54 button::before,
    .st-key-retry_auto_sub_v80 button::before,
    [data-testid="stPopover"] > button::before{
        display:none !important;
        content:none !important;
        width:0 !important;
        height:0 !important;
        margin:0 !important;
    }

    /* Mantieni leggibile anche il testo dei pulsanti custom. */
    .st-key-reset_main_all_v29 button,
    .st-key-editor_transcribe_scene_v18 button,
    .st-key-retry_auto_sub_v80 button{
        background:#FFFFFF !important;
        color:#17324A !important;
        border:1px solid #9FCDEA !important;
    }
    .st-key-reset_main_all_v29 button p,
    .st-key-editor_transcribe_scene_v18 button p,
    .st-key-retry_auto_sub_v80 button p{
        color:#17324A !important;
    }

    .st-key-editor_use_changes_v54 button{
        color:#102C45 !important;
    }
    .st-key-editor_use_changes_v54 button p{
        color:inherit !important;
    }
}
</style>
""", unsafe_allow_html=True)
'''

_m = re.search(
    r'try:\n    import numpy as np\nexcept Exception:\n    np = None\n',
    s
)
if not _m:
    raise RuntimeError('V80 patch target not found: numpy import anchor')
s = s[:_m.end()] + "\n" + _ui_fix + "\n" + s[_m.end():]

# ------------------------------------------------------------------
# V80 AUTOMATIC SUBTITLES — trascrive davvero quando Automatici è attivo
# ------------------------------------------------------------------
replace_once(
'''            st.session_state["editor_sub_mode"]=editor_sub_mode
            st.session_state["project_subtitles_enabled"]=(editor_sub_mode!="Nessuno")
            st.session_state["project_subtitles_mode"]=editor_sub_mode

            if editor_sub_mode=="Manuali":
''',
'''            st.session_state["editor_sub_mode"]=editor_sub_mode
            st.session_state["project_subtitles_enabled"]=(editor_sub_mode!="Nessuno")
            st.session_state["project_subtitles_mode"]=editor_sub_mode

            # V80: "Automatici" significa davvero automatici.
            # La scena viene trascritta una volta per sorgente + IN/OUT e le parole
            # reali vengono mostrate subito nel player. Zoom/colori/strumenti non
            # rilanciano Whisper perché il token della scena resta invariato.
            if editor_sub_mode=="Automatici":
                _auto_sub_token=hashlib.sha256(
                    (
                        f"{editor_input}|{float(editor_start):.3f}|"
                        f"{float(editor_len):.3f}|v80-auto"
                    ).encode("utf-8")
                ).hexdigest()[:24]

                if st.session_state.get("editor_auto_sub_scene_token") != _auto_sub_token:
                    with st.spinner("Trascrizione automatica della scena..."):
                        _auto_words,_auto_err=_gsf_transcribe_editor_scene(
                            editor_input,editor_start,editor_len
                        )

                    st.session_state["editor_auto_sub_scene_token"]=_auto_sub_token
                    st.session_state["editor_auto_sub_error"]=str(_auto_err or "")

                    if _auto_err:
                        st.session_state["editor_sub_words"]=[]
                        st.session_state["editor_sub_live_words"]=[]
                        st.session_state["editor_sub_text"]=""
                    else:
                        _auto_words=list(_auto_words or [])
                        _auto_text=" ".join(
                            str(w.get("text","")).strip()
                            for w in _auto_words
                            if str(w.get("text","")).strip()
                        )
                        st.session_state["editor_sub_words"]=_auto_words
                        st.session_state["editor_sub_live_words"]=_auto_words
                        st.session_state["editor_sub_text"]=_auto_text
                        st.session_state["editor_sub_applied_text"]=_auto_text
                        st.session_state["editor_sub_seek"]=float(editor_start)
                        st.session_state["editor_sub_seek_feedback"]=float(editor_start)
                        try:
                            _gsf_save_persistent_state()
                        except Exception:
                            pass
                        st.rerun()

                _auto_sub_error=st.session_state.get("editor_auto_sub_error","")
                if _auto_sub_error:
                    st.warning(
                        "Trascrizione automatica non riuscita: "
                        + str(_auto_sub_error)
                    )
                    if st.button(
                        "RIPROVA TRASCRIZIONE",
                        use_container_width=True,
                        key="retry_auto_sub_v80"
                    ):
                        st.session_state.pop("editor_auto_sub_scene_token",None)
                        st.session_state.pop("editor_auto_sub_error",None)
                        st.rerun()
                elif st.session_state.get("editor_sub_live_words"):
                    st.caption(
                        "Trascrizione automatica pronta · "
                        f"{len(st.session_state.get('editor_sub_live_words',[]))} parole"
                    )

            if editor_sub_mode=="Manuali":
''',
'main automatic subtitle trigger')

replace_once(
'''        _main_sub_words=(
            st.session_state.get(
                "editor_sub_live_words",
                st.session_state.get("editor_sub_words",[])
            )
            if _main_sub_mode=="Manuali" else []
        )
''',
'''        _main_sub_words=(
            st.session_state.get(
                "editor_sub_live_words",
                st.session_state.get("editor_sub_words",[])
            )
            if _main_sub_mode in ("Manuali","Automatici") else []
        )
''',
'main automatic subtitle words')

replace_once(
'''                "subtitle_mode":_main_sub_mode,
''',
'''                # Automatici V80 ha già parole temporizzate: al renderer passa
                # come trascrizione pronta, evitando un secondo download/modello.
                "subtitle_mode":(
                    "Manuali"
                    if _main_sub_mode=="Automatici" and _main_sub_words
                    else _main_sub_mode
                ),
''',
'main automatic subtitle render mode')

# Footer/versione corretti.
s = s.replace(
    "Gaming Shorts Factory · V77 Web Ready",
    "Gaming Shorts Factory · V80 UI + Auto Sub"
)
s = s.replace(
    "Versione di prova · Anteprime video leggere",
    "Beta web/mobile · Sessione persistente"
)

out.write_text(s, encoding='utf-8')
print(f'V80 patch applied: {out}')
