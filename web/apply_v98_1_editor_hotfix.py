from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_EDITOR_POLISH.py')
out=Path('/app/GamingShortsFactory_V98_1_EDITOR_HOTFIX.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.1 patch target not found: {label}')
    s=s.replace(old,new,1)

# 1) Remove restored-session bubble and center "Nuovo video" below upload.
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
#    Keep it silent and forward the requested subtitle seek time.
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

# 3) Applying editor changes must not force a rerun to the top/home.
replace_once(
'''            st.session_state["auto_clip_scelta"]=float(editor_start)
            st.session_state["auto_clip_duration"]=float(editor_len)
            st.rerun()

        if _main_recipe_selected:
''',
'''            st.session_state["auto_clip_scelta"]=float(editor_start)
            st.session_state["auto_clip_duration"]=float(editor_len)
            _main_recipe_selected=True

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

                        if _inline_recipe_selected:
''',
'inline editor apply without forced rerun')

# 4) Remove the two V98 informational clouds requested during testing.
replace_once(
'''                        st.caption(
                            f"IN {_istart:.1f}s · OUT {_iend:.1f}s · DURATA {_ilen:.1f}s"
                        )

''',
'',
'remove trim summary cloud')

replace_once(
'''                            st.caption("ANTEPRIMA LIVE · queste regolazioni sono le stesse usate dal render finale.")
''',
'',
'remove preview/render info cloud')

s=s.replace(
    'Gaming Shorts Factory · V98 Editor Polish',
    'Gaming Shorts Factory · V98.1 Editor Hotfix'
)

out.write_text(s,encoding='utf-8')
print(f'V98.1 patch applied: {out}')
