from pathlib import Path
import ast,sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.1 Editor Hotfix' in s,'V98.1 marker')

# UI cleanup requested from screenshots.
need('Sessione beta ripristinata automaticamente.' not in s,'restored-session bubble removed')
need('gsf-v98-1-new-video-center' in s,'new-video centering CSS installed')
need('justify-content:center' in s and 'st-key-v81_new_video' in s,'new-video button centered')
need('Per il player LIVE persistente serve una versione recente di Streamlit con Components V2.' not in s,'Components V2 warning removed')
need('IN {_istart:.1f}s · OUT {_iend:.1f}s · DURATA {_ilen:.1f}s' not in s,'trim info cloud removed')
need('ANTEPRIMA LIVE · queste regolazioni sono le stesse usate dal render finale.' not in s,'preview info cloud removed')
need('Modifiche applicate. Puoi continuare nell\\'Editor o creare lo Short finale.' not in s,'no extra apply notification cloud')

# VAI must work on the actual production fallback.
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'legacy player receives selected seek target')
need('source_path,key,_legacy_seek,fmt,zoom,x_pos,y_pos,volume,brightness,contrast,speed' in s,'legacy player opens at requested subtitle time')
need('inline_seek_nonce_' in s and 'inline_time_go_v22_' in s,'subtitle VAI event path preserved')
need('st.session_state[f"inline_seek_{_this_inline_id}"]=float(_chosen_t)' in s,'selected subtitle time is stored')

# Apply changes must persist without an extra forced rerun.
main_anchor='st.session_state["auto_clip_duration"]=float(editor_len)'
main_i=s.index(main_anchor)
main_block=s[main_i:main_i+450]
need('st.rerun()' not in main_block,'main apply no longer forces home/top rerun')
need('_main_recipe_selected=True' in main_block,'main recipe remains selected after apply')

inline_anchor=']=float(_ilen)'
inline_i=s.index(inline_anchor)
inline_block=s[inline_i:inline_i+500]
need('st.rerun()' not in inline_block,'inline apply no longer forces home/top rerun')
need('_inline_recipe_selected=True' in inline_block,'inline recipe remains selected after apply')

# Guardrails.
need('def render_gsf_editor_live_player' in s,'live player system preserved')
need('inline_live_v32_' in s,'inline live player identity preserved')
need('numero_clip=3' in s,'three AI clips preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final render quality preserved')
need('gsf-v89-upload-visual' in s,'approved upload circle preserved')
print('V98.1 editor hotfix regression: PASS')
