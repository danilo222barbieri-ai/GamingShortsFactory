from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_5_STYLE_ONLY.py')
out=Path('/app/GamingShortsFactory_V98_6_PLAYER_SIZES.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.6 target not found: {label}')
    s=s.replace(old,new,1)

# 1) Main preview 16:9 only: 800x450 -> 640x360.
replace_once(
'''            _profile="PLAYER 16:9"; _target_width=800; _max_vw="800px"; _cap=540
''',
'''            _profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430
''',
'main preview 16:9 size')

# 2) Editor LIVE 16:9 only: 480x270 -> 560x315.
# Keep 9:16 exactly 220x391.
replace_once(
'''    frame_w,frame_h,iframe_h=((220,391,424) if vertical else (480,270,309))
''',
'''    frame_w,frame_h,iframe_h=((220,391,424) if vertical else (560,315,354))
''',
'editor live 16:9 size')

# Give the wider 16:9 LIVE player enough real horizontal room.
replace_once(
'''        studio_player, studio_side = st.columns([.22,.78],gap="medium")
''',
'''        studio_player, studio_side = st.columns(
            [.44,.56] if editor_format=="16:9 Originale" else [.22,.78],
            gap="medium"
        )
''',
'main editor 16:9 workspace')

replace_once(
'''                        _pl,_side=st.columns([.22,.78],gap="medium")
''',
'''                        _pl,_side=st.columns(
                            [.44,.56] if st.session_state[_fmt_key]=="16:9 Originale" else [.22,.78],
                            gap="medium"
                        )
''',
'inline editor 16:9 workspace')

# 3) Button copy only: RESET CONTROLLI -> RESET.
reset_count=s.count('↶ RESET CONTROLLI')
if reset_count < 1:
    raise RuntimeError('V98.6 target not found: RESET CONTROLLI')
s=s.replace('↶ RESET CONTROLLI','↶ RESET')

s=s.replace(
    'Gaming Shorts Factory · V98.5 Style Only',
    'Gaming Shorts Factory · V98.6 Player Sizes'
)

out.write_text(s,encoding='utf-8')
print(f'V98.6 patch applied: {out} | reset labels changed: {reset_count}')
