from pathlib import Path

src=Path('/app/GamingShortsFactory_V80_2_RENDER_HOTFIX.py')
out=Path('/app/GamingShortsFactory_V81_MOBILE_TABLET_POLISH.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V81 patch target not found: {label}')
    s=s.replace(old,new,1)

# ============================================================
# V81 — nuovo video dopo refresh/session recovery
# ============================================================
anchor='''_gsf_restore_persistent_state()
'''
insert='''# V81: reset sicuro della lavorazione corrente per poter caricare un nuovo
# video anche dopo il ripristino automatico della sessione.
def _gsf_start_new_video():
    old_generation=int(st.session_state.get("gsf_upload_generation",0) or 0)

    keep_exact={"gsf_web_session_id"}
    keep_parts=("youtube","tiktok","instagram","social","oauth")

    for _key in list(st.session_state.keys()):
        _ks=str(_key)
        _low=_ks.lower()
        if _ks.startswith("_") or _ks in keep_exact:
            continue
        if any(part in _low for part in keep_parts):
            continue
        try:
            st.session_state.pop(_key,None)
        except Exception:
            pass

    st.session_state["gsf_upload_generation"]=old_generation+1

    try:
        GSF_SESSION_STATE_FILE.unlink(missing_ok=True)
    except Exception:
        pass

    # Pulisce solo i file della lavorazione video. I token social restano.
    for _root in (GSF_PREVIEW_DIR,GSF_SESSION_TMP_DIR,GSF_SESSION_EXPORT_DIR):
        try:
            for _p in sorted(_root.rglob("*"),key=lambda p:len(p.parts),reverse=True):
                try:
                    if _p.is_file() or _p.is_symlink():
                        _p.unlink(missing_ok=True)
                    elif _p.is_dir():
                        _p.rmdir()
                except Exception:
                    pass
            _root.mkdir(parents=True,exist_ok=True)
        except Exception:
            pass

# Questo pulsante viene aggiunto dopo V80.1, quindi lo registriamo
# esplicitamente come widget transitorio da NON persistere.
try:
    if "v81_new_video" not in _GSF_TRANSIENT_WIDGET_EXACT:
        _GSF_TRANSIENT_WIDGET_EXACT.append("v81_new_video")
except Exception:
    pass

_gsf_restore_persistent_state()
'''
replace_once(anchor,insert,'new-video reset anchor')

replace_once(
'''        key="upload_v73"
    )
''',
'''        key=f"upload_v73_{int(st.session_state.get('gsf_upload_generation',0) or 0)}"
    )
''',
'dynamic uploader key')

replace_once(
'''    if _gsf_recovered_source is not None:
        st.caption("Sessione beta ripristinata automaticamente.")
''',
'''    if _gsf_recovered_source is not None:
        st.caption("Sessione beta ripristinata automaticamente.")

    st.button(
        "＋ NUOVO VIDEO",
        use_container_width=False,
        key="v81_new_video",
        on_click=_gsf_start_new_video,
        help="Azzera questa lavorazione e prepara l'upload di un nuovo video."
    )
''',
'new-video button')

# ============================================================
# V81 — upload ring verde (attivo durante upload, pieno a fine upload)
# ============================================================
v81_css=r'''
st.markdown("""
<style id="gsf-v81-mobile-tablet-polish">
/* Upload: il cerchio deve comunicare chiaramente che sta lavorando. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
    position:relative !important;
    overflow:visible !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::after{
    content:"";
    position:absolute;
    inset:-7px;
    border-radius:999px;
    border:5px solid transparent;
    pointer-events:none;
    opacity:0;
    box-sizing:border-box;
    z-index:4;
}
@keyframes gsfV81UploadRing{
    from{transform:rotate(0deg)}
    to{transform:rotate(360deg)}
}
/* Streamlit espone un progressbar durante l'upload: anello verde animato. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([role="progressbar"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="Progress"])
[data-testid="stFileUploaderDropzone"]::after{
    opacity:1;
    border-top-color:#22C55E;
    border-right-color:#22C55E;
    border-bottom-color:rgba(34,197,94,.22);
    border-left-color:rgba(34,197,94,.22);
    animation:gsfV81UploadRing .85s linear infinite;
    filter:drop-shadow(0 0 5px rgba(34,197,94,.28));
}
/* Upload completato: anello verde pieno. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::after{
    opacity:1;
    border-color:#22C55E;
    animation:none;
    filter:drop-shadow(0 0 5px rgba(34,197,94,.25));
}

/* Tablet/mobile: tutti i player custom devono restare centrati. */
@media(max-width:1100px){
    iframe{
        display:block !important;
        margin-left:auto !important;
        margin-right:auto !important;
    }
    .st-key-v81_new_video button{
        min-height:2.55rem !important;
        border-radius:14px !important;
    }
}
</style>
""",unsafe_allow_html=True)
'''

marker='<style id="gsf-v80-ui-fix">'
pos=s.find(marker)
if pos<0:
    raise RuntimeError('V81 patch target not found: V80 style marker')
end=s.find('""", unsafe_allow_html=True)',pos)
if end<0:
    raise RuntimeError('V81 patch target not found: V80 style end')
end+=len('""", unsafe_allow_html=True)')
s=s[:end]+'\n\n'+v81_css+s[end:]

# ============================================================
# V81 — centra il video dentro il player HTML (9:16 e 16:9).
# Sul desktop non cambia la dimensione; su iPhone/iPad il 16:9 non resta a sinistra.
# ============================================================
replace_once(
'''        video{{display:block;width:{_target_width}px;max-width:min({_max_vw},100%);height:auto;
        object-fit:contain;border-radius:18px;background:#000;
''',
'''        video{{display:block;width:{_target_width}px;max-width:min({_max_vw},100%);height:auto;
        margin-left:auto;margin-right:auto;
        object-fit:contain;border-radius:18px;background:#000;
''',
'center unified player')

# Footer.
s=s.replace(
    'Gaming Shorts Factory · V80.2 Render Hotfix',
    'Gaming Shorts Factory · V81 Mobile/Tablet'
)

out.write_text(s,encoding='utf-8')
print(f'V81 patch applied: {out}')
