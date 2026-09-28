from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_EDITOR_POLISH.py')
out=Path('/app/GamingShortsFactory_V98_1_EDITOR_HOTFIX.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.1 patch target not found: {label}')
    s=s.replace(old,new,1)

# 1) Remove restored-session bubble and keep "Nuovo video" directly under upload.
replace_once(
'''    if _gsf_recovered_source is not None:
        st.caption("Sessione beta ripristinata automaticamente.")

    st.button(
''',
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
''',
'center new-video button and remove restored-session caption')

# 2) Production uses the legacy fallback on the pinned Streamlit version.
#    Do not show the internal compatibility warning to the user and make VAI
#    seek to the selected subtitle even in the legacy iframe.
replace_once(
'''    if _GSF_LIVE_V2 is None:
        st.warning("Per il player LIVE persistente serve una versione recente di Streamlit con Components V2.")
        return _render_gsf_editor_live_player_legacy(
            source_path,key,start_seconds,fmt,zoom,x_pos,y_pos,volume,brightness,contrast,speed,
''',
'''    if _GSF_LIVE_V2 is None:
        _legacy_seek=float(seek_target if seek_target is not None else start_seconds)
        return _render_gsf_editor_live_player_legacy(
            source_path,key,_legacy_seek,fmt,zoom,x_pos,y_pos,volume,brightness,contrast,speed,
''',
'legacy seek and warning removal')

# 3) "USA QUESTE MODIFICHE" already runs inside a Streamlit interaction.
#    A second explicit rerun jumps the user back to the top and can make the
#    editor look as if it lost the applied recipe. Persist state in the same run.
replace_once(
'''            st.session_state["auto_clip_scelta"]=float(editor_start)
            st.session_state["auto_clip_duration"]=float(editor_len)
            st.rerun()

        if _main_recipe_selected:
''',
'''            st.session_state["auto_clip_scelta"]=float(editor_start)
            st.session_state["auto_clip_duration"]=float(editor_len)
            _main_recipe_selected=True
            st.success("Modifiche applicate. Puoi continuare nell'Editor o creare lo Short finale.")

        if _main_recipe_selected:
''',
'main editor apply without forced rerun')

replace_once(
'''                            st.session_state[
                                "auto_clip_duration"
                            ]=float(_ilen)
                            st.rerun()

                        if _inline_recipe_selected:
''',
'''                            st.session_state[
                                "auto_clip_duration"
                            ]=float(_ilen)
                            _inline_recipe_selected=True
                            st.success("Modifiche applicate. Puoi continuare nell'Editor o creare lo Short finale.")

                        if _inline_recipe_selected:
''',
'inline editor apply without forced rerun')

s=s.replace(
    'Gaming Shorts Factory · V98 Editor Polish',
    'Gaming Shorts Factory · V98.1 Editor Hotfix'
)

out.write_text(s,encoding='utf-8')
print(f'V98.1 patch applied: {out}')
