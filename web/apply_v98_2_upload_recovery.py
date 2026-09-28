from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_1_EDITOR_HOTFIX.py')
out=Path('/app/GamingShortsFactory_V98_2_UPLOAD_RECOVERY.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.2 patch target not found: {label}')
    s=s.replace(old,new,1)

# Restore the proven upload flow shape: the "Nuovo video" control belongs
# only to a recovered/loaded session, and must never sit unconditionally
# next to the live file_uploader during a new upload.
replace_once(
'''    st.markdown("""
<style id="gsf-v98-1-new-video-center">
.st-key-v81_new_video{
    display:flex !important;
    justify-content:center !important;
}
.st-key-v81_new_video button{
    width:auto !important;
    min-width:170px !important;
}
</style>
""",unsafe_allow_html=True)

    st.button(
        "＋ NUOVO VIDEO",
        use_container_width=False,
        key="v81_new_video",
        on_click=_gsf_start_new_video,
        help="Azzera questa lavorazione e prepara l'upload di un nuovo video."
    )
''',
'''    if _gsf_recovered_source is not None:
        _nv_left,_nv_center,_nv_right=st.columns([1,1,1])
        with _nv_center:
            st.button(
                "＋ NUOVO VIDEO",
                use_container_width=True,
                key="v81_new_video",
                on_click=_gsf_start_new_video,
                help="Azzera questa lavorazione e prepara l'upload di un nuovo video."
            )
''',
'restore safe conditional new-video flow')

s=s.replace(
    'Gaming Shorts Factory · V98.1 Editor Hotfix',
    'Gaming Shorts Factory · V98.2 Upload Recovery'
)

out.write_text(s,encoding='utf-8')
print(f'V98.2 patch applied: {out}')
