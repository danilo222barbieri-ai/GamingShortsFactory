from pathlib import Path

src=Path('/app/GamingShortsFactory_V88_PERSISTENT_LOADED_CIRCLE.py')
out=Path('/app/GamingShortsFactory_V89_DECOUPLED_UPLOAD_VISUAL.py')
s=src.read_text(encoding='utf-8')

# V89 root fix: the visible circle must never be the Streamlit uploader DOM.
# Streamlit remains only as an invisible click/upload layer. The visible circle
# is our own HTML and is rendered on every rerun, so it cannot disappear when
# Streamlit replaces its internal post-upload markup.
v89_fn=r'''
def _gsf_v89_upload_visual_html(loaded=False):
    _loaded_class = " is-loaded" if loaded else ""
    _icon = "✓" if loaded else "⇧"
    _label = "Video caricato" if loaded else "Carica il tuo video"
    return f"""
<style id="gsf-v89-decoupled-upload-visual">
.st-key-v73-upload-shell{{
    width:100% !important;
    min-height:244px !important;
    padding:10px 0 8px !important;
    position:relative !important;
    box-sizing:border-box !important;
    text-align:center !important;
}}

/* Streamlit is only the invisible functional upload layer. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]{{
    position:absolute !important;
    left:50% !important;
    top:10px !important;
    transform:translateX(-50%) !important;
    width:218px !important;
    min-width:218px !important;
    max-width:218px !important;
    height:218px !important;
    min-height:218px !important;
    max-height:218px !important;
    margin:0 !important;
    padding:0 !important;
    border:0 !important;
    background:transparent !important;
    box-shadow:none !important;
    opacity:0 !important;
    z-index:20 !important;
    overflow:hidden !important;
}}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"],
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] > div,
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button{{
    position:absolute !important;
    inset:0 !important;
    width:100% !important;
    height:100% !important;
    min-width:100% !important;
    min-height:100% !important;
    max-width:100% !important;
    max-height:100% !important;
    margin:0 !important;
    padding:0 !important;
    border-radius:50% !important;
}}

/* After upload only + NUOVO VIDEO should change the source. */
.st-key-v73-upload-shell:has(.gsf-v89-upload-visual.is-loaded)
[data-testid="stFileUploader"]{{
    pointer-events:none !important;
}}

/* This is the ONLY visible circle. It is independent of Streamlit's DOM. */
.gsf-v89-upload-visual{{
    box-sizing:border-box;
    width:218px;
    height:218px;
    min-width:218px;
    min-height:218px;
    max-width:218px;
    max-height:218px;
    margin:0 auto;
    padding:26px 22px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    border-radius:50%;
    background:#DCEBFC;
    border:2px solid #8DB4E2;
    box-shadow:0 10px 26px rgba(31,78,121,.10);
    color:#214F82;
    position:relative;
    z-index:2;
    pointer-events:none;
}}
.gsf-v89-upload-visual.is-loaded{{
    background:#DDF5E8;
    border-color:#69BE8E;
    color:#236B43;
}}
.gsf-v89-upload-icon{{
    display:block;
    margin:0 0 13px 0;
    color:#24558B;
    font-size:58px;
    font-weight:500;
    line-height:.82;
}}
.gsf-v89-upload-visual.is-loaded .gsf-v89-upload-icon{{
    color:#238A50;
    font-size:54px;
    font-weight:700;
}}
.gsf-v89-upload-label{{
    display:block;
    width:150px;
    max-width:150px;
    margin:0;
    color:inherit;
    font-size:17px;
    font-weight:800;
    line-height:1.2;
    white-space:normal;
    text-align:center;
}}

/* Real upload progress, but shown outside the invisible uploader as a tiny bar. */
.st-key-v73-upload-shell:has([role="progressbar"])::after,
.st-key-v73-upload-shell:has(progress)::after,
.st-key-v73-upload-shell:has([data-testid*="Progress"])::after{{
    content:"";
    display:block;
    width:154px;
    height:6px;
    margin:12px auto 0;
    border-radius:999px;
    background:#22C55E;
    box-shadow:0 0 0 1px rgba(34,197,94,.14);
}}

@media(max-width:600px){{
    .st-key-v73-upload-shell{{min-height:234px !important;}}
    .st-key-v73-upload-shell [data-testid="stFileUploader"]{{
        width:208px !important;
        min-width:208px !important;
        max-width:208px !important;
        height:208px !important;
        min-height:208px !important;
        max-height:208px !important;
    }}
    .gsf-v89-upload-visual{{
        width:208px;
        height:208px;
        min-width:208px;
        min-height:208px;
        max-width:208px;
        max-height:208px;
    }}
    .gsf-v89-upload-icon{{font-size:54px;margin-bottom:12px;}}
    .gsf-v89-upload-visual.is-loaded .gsf-v89-upload-icon{{font-size:52px;}}
    .gsf-v89-upload-label{{width:144px;max-width:144px;font-size:16px;}}
}}
</style>
<div class="gsf-v89-upload-visual{{_loaded_class}}" role="status" aria-label="{{_label}}">
  <span class="gsf-v89-upload-icon">{{_icon}}</span>
  <span class="gsf-v89-upload-label">{{_label}}</span>
</div>
"""

'''

anchor='with st.container(key="v73-upload-shell"):\n'
if anchor not in s:
    raise RuntimeError('V89 uploader anchor not found')
s=s.replace(anchor,v89_fn+anchor,1)

old='''with st.container(key="v73-upload-shell"):
    video = st.file_uploader(
        "Carica il tuo video",
        type=["mp4", "mov", "mkv"],
        label_visibility="collapsed",
        key="upload_v73"
    )

_gsf_recovered_source = None
if video is None and GSF_WEB_MODE:
    _gsf_recovered_source = _gsf_find_recovered_source()
    if _gsf_recovered_source is not None:
        video = _GSFRecoveredUpload(
            _gsf_recovered_source,
            st.session_state.get("gsf_source_name", _gsf_recovered_source.name)
        )
        st.session_state["gsf_source_path"] = str(_gsf_recovered_source)

st.markdown(_gsf_v86_upload_css(video is not None), unsafe_allow_html=True)
if video is not None:
    st.markdown(_gsf_v88_loaded_circle_html(), unsafe_allow_html=True)
'''
new='''with st.container(key="v73-upload-shell"):
    video = st.file_uploader(
        "Carica il tuo video",
        type=["mp4", "mov", "mkv"],
        label_visibility="collapsed",
        key="upload_v73"
    )

    _gsf_recovered_source = None
    if video is None and GSF_WEB_MODE:
        _gsf_recovered_source = _gsf_find_recovered_source()
        if _gsf_recovered_source is not None:
            video = _GSFRecoveredUpload(
                _gsf_recovered_source,
                st.session_state.get("gsf_source_name", _gsf_recovered_source.name)
            )
            st.session_state["gsf_source_path"] = str(_gsf_recovered_source)

    st.markdown(_gsf_v89_upload_visual_html(video is not None), unsafe_allow_html=True)
'''
if old not in s:
    raise RuntimeError('V89 expected V88 uploader flow not found')
s=s.replace(old,new,1)

s=s.replace(
    'Gaming Shorts Factory · V88 Persistent Loaded Circle',
    'Gaming Shorts Factory · V89 Decoupled Upload Visual'
)

out.write_text(s,encoding='utf-8')
print(f'V89 patch applied: {out}')
