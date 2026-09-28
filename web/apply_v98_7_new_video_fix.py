from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_6_PLAYER_SIZES.py')
out=Path('/app/GamingShortsFactory_V98_7_NEW_VIDEO_FIX.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.7 target not found: {label}')
    s=s.replace(old,new,1)

# 1) Editor 16:9 a little smaller: 560x315 -> 520x293.
replace_once(
'''    frame_w,frame_h,iframe_h=((220,391,424) if vertical else (560,315,354))
''',
'''    frame_w,frame_h,iframe_h=((220,391,424) if vertical else (520,293,332))
''',
'editor live 16:9 size')

replace_once(
'''            [.44,.56] if editor_format=="16:9 Originale" else [.22,.78],
''',
'''            [.40,.60] if editor_format=="16:9 Originale" else [.22,.78],
''',
'main editor 16:9 workspace')

replace_once(
'''                            [.44,.56] if st.session_state[_fmt_key]=="16:9 Originale" else [.22,.78],
''',
'''                            [.40,.60] if st.session_state[_fmt_key]=="16:9 Originale" else [.22,.78],
''',
'inline editor 16:9 workspace')

# 2) New-video button: show for every active-video state, not only recovered sessions.
replace_once(
'''    if _gsf_recovered_source is not None:
        _nv_left,_nv_center,_nv_right=st.columns([1,1,1])
''',
'''    _gsf_has_active_video=(
        _gsf_recovered_source is not None
        or bool(st.session_state.get("gsf_source_path"))
        or st.session_state.get("upload_v73") is not None
    )
    if _gsf_has_active_video:
        _nv_left,_nv_center,_nv_right=st.columns([1,1,1])
''',
'robust new-video visibility')

s=s.replace(
    'Gaming Shorts Factory · V98.6 Player Sizes',
    'Gaming Shorts Factory · V98.7 New Video Fix'
)

out.write_text(s,encoding='utf-8')
print(f'V98.7 patch applied: {out}')
