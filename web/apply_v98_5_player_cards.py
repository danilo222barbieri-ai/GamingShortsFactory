from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_4_EDITOR_CLEANUP.py')
out=Path('/app/GamingShortsFactory_V98_5_PLAYER_CARDS.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.5 patch target not found: {label}')
    s=s.replace(old,new,1)

# ------------------------------------------------------------
# 1) ANTEPRIMA VIDEO — only this 16:9 preview is reduced:
#    800x450 -> 640x360. Vertical preview remains unchanged.
# ------------------------------------------------------------
replace_once(
'''            _profile="PLAYER 16:9"; _target_width=800; _max_vw="800px"; _cap=540
''',
'''            _profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430
''',
'main preview 16:9 size')

# ------------------------------------------------------------
# 2) LIVE EDITOR — keep 9:16 at 220x391, enlarge only 16:9:
#    480x270 -> 560x315.
# ------------------------------------------------------------
replace_once(
'''    frame_w,frame_h,iframe_h=((220,391,424) if vertical else (480,270,309))
''',
'''    frame_w,frame_h,iframe_h=((220,391,424) if vertical else (560,315,354))
''',
'legacy editor 16:9 size')

# Give 16:9 enough horizontal workspace; 9:16 keeps its approved proportions.
replace_once(
'''        studio_player, studio_side = st.columns([.22,.78],gap="medium")
''',
'''        studio_player, studio_side = st.columns(
            [.44,.56] if editor_format=="16:9 Originale" else [.22,.78],
            gap="medium"
        )
''',
'main editor responsive columns')

replace_once(
'''                        _pl,_side=st.columns([.22,.78],gap="medium")
''',
'''                        _pl,_side=st.columns(
                            [.44,.56] if st.session_state[_fmt_key]=="16:9 Originale" else [.22,.78],
                            gap="medium"
                        )
''',
'inline editor responsive columns')

# ------------------------------------------------------------
# 3) Wrap the main source preview and both editor player variants
#    in dedicated Streamlit containers so styling never leaks to
#    AI mini previews or final result players.
# ------------------------------------------------------------
def wrap_range(text,start_marker,end_marker,key_expr,label):
    lines=text.splitlines(True)
    start=next((i for i,line in enumerate(lines) if start_marker in line),None)
    if start is None:
        raise RuntimeError(f'V98.5 wrap start not found: {label}')
    base_indent=lines[start][:len(lines[start])-len(lines[start].lstrip())]
    end=next(
        (i for i in range(start+1,len(lines))
         if end_marker in lines[i] and lines[i].startswith(base_indent)),
        None
    )
    if end is None:
        raise RuntimeError(f'V98.5 wrap end not found: {label}')
    lines.insert(start, base_indent+f'with st.container(key={key_expr}):\n')
    end += 1
    for i in range(start+1,end):
        lines[i]='    '+lines[i]
    return ''.join(lines)

s=wrap_range(
    s,
    '_pw,_ph,_rotation,_probe_error=_gsf_probe_display_size(_preview_path)',
    'st.divider()',
    '"v985-main-preview-card"',
    'main preview card'
)

def nest_player_column(text,start_exact,end_exact,key_line,label):
    lines=text.splitlines(True)
    start=next((i for i,line in enumerate(lines) if line.strip()==start_exact),None)
    if start is None:
        raise RuntimeError(f'V98.5 player column start not found: {label}')
    base_indent=lines[start][:len(lines[start])-len(lines[start].lstrip())]
    end=next(
        (i for i in range(start+1,len(lines))
         if lines[i].strip()==end_exact and lines[i].startswith(base_indent)),
        None
    )
    if end is None:
        raise RuntimeError(f'V98.5 player column end not found: {label}')
    child_indent=base_indent+'    '
    lines.insert(start+1, child_indent+key_line+'\n')
    end += 1
    for i in range(start+2,end):
        lines[i]='    '+lines[i]
    return ''.join(lines)

s=nest_player_column(
    s,
    'with studio_player:',
    'with studio_side:',
    'with st.container(key="v985-editor-player-card"):',
    'main editor player card'
)

s=nest_player_column(
    s,
    'with _pl:',
    'with _side:',
    'with st.container(key=f"v985-inline-player-card-{_this_inline_id}"):',
    'inline editor player card'
)

# ------------------------------------------------------------
# 4) Coordinated visual language: same family as AI candidate cards,
#    cleaner frame, soft depth, selected AI card highlighted.
# ------------------------------------------------------------
style=r'''
st.markdown("""
<style id="gsf-v98-5-player-cards">
.st-key-v985-main-preview-card,
.st-key-v985-editor-player-card,
[class*="st-key-v985-inline-player-card-"]{
    box-sizing:border-box !important;
    border:1px solid #D4E4EF !important;
    border-radius:24px !important;
    background:linear-gradient(180deg,#FFFFFF 0%,#F8FCFF 100%) !important;
    box-shadow:0 12px 28px rgba(28,78,112,.09) !important;
    padding:12px !important;
}
.st-key-v985-main-preview-card{
    width:min(680px,100%) !important;
    max-width:680px !important;
    margin:0 auto 14px auto !important;
    padding:14px !important;
}
.st-key-v985-editor-player-card,
[class*="st-key-v985-inline-player-card-"]{
    width:100% !important;
    padding:10px !important;
}
.st-key-v985-main-preview-card iframe,
.st-key-v985-editor-player-card iframe,
[class*="st-key-v985-inline-player-card-"] iframe{
    display:block !important;
    width:100% !important;
    border:0 !important;
    border-radius:18px !important;
    background:#000 !important;
}

/* AI candidate cards: same family, slightly more premium, no size changes. */
[class*="st-key-v71_short_card_"]{
    border:1px solid #D4E4EF !important;
    border-radius:24px !important;
    background:linear-gradient(180deg,#FFFFFF 0%,#F8FCFF 100%) !important;
    box-shadow:0 12px 28px rgba(28,78,112,.09) !important;
    padding:18px !important;
    transition:transform .16s ease, box-shadow .16s ease, border-color .16s ease !important;
}
[class*="st-key-v71_short_card_"] iframe{
    border-radius:18px !important;
    overflow:hidden !important;
    background:#000 !important;
}
[class*="st-key-v71_short_card_"]:has(button[kind="primary"]){
    border-color:#70B7E8 !important;
    box-shadow:0 14px 32px rgba(42,132,192,.16) !important;
    background:linear-gradient(180deg,#FFFFFF 0%,#F0F9FF 100%) !important;
}

@media(max-width:750px){
    .st-key-v985-main-preview-card{
        width:100% !important;
        max-width:100% !important;
        padding:9px !important;
    }
    .st-key-v985-editor-player-card,
    [class*="st-key-v985-inline-player-card-"]{
        padding:8px !important;
    }
}
</style>
""",unsafe_allow_html=True)
'''
s += "\n"+style+"\n"

s=s.replace(
    'Gaming Shorts Factory · V98.4 Editor Cleanup',
    'Gaming Shorts Factory · V98.5 Player Cards'
)

out.write_text(s,encoding='utf-8')
print(f'V98.5 patch applied: {out}')
