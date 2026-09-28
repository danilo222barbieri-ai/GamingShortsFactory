from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.7 New Video Fix' in s,'V98.7 marker')

# Editor sizing.
need('((220,391,424) if vertical else (520,293,332))' in s,'editor live 16:9 reduced to 520x293')
need('((220,391,424) if vertical else (560,315,354))' not in s,'old 560x315 editor size removed')
need('[.40,.60] if editor_format=="16:9 Originale" else [.22,.78]' in s,'main editor 16:9 workspace reduced')
need('[.40,.60] if st.session_state[_fmt_key]=="16:9 Originale" else [.22,.78]' in s,'inline editor 16:9 workspace reduced')

# Main preview stays 640x360.
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main preview stays 640x360')
need('_profile="PLAYER 9:16"; _target_width=300; _max_vw="300px"; _cap=680' in s,'main preview 9:16 unchanged')

# New video visibility.
need('_gsf_has_active_video=(' in s,'active-video guard installed')
need('_gsf_recovered_source is not None' in s,'recovered video state included')
need('bool(st.session_state.get("gsf_source_path"))' in s,'materialized source state included')
need('st.session_state.get("upload_v73") is not None' in s,'live uploader state included')
need('if _gsf_has_active_video:' in s,'new-video button uses robust guard')
need('"＋ NUOVO VIDEO"' in s,'new-video button preserved')
need('on_click=_gsf_start_new_video' in s,'new-video reset action preserved')

# Reset copy + style preserved.
need('↶ RESET CONTROLLI' not in s and '↶ RESET' in s,'short reset label preserved')
need('width:fit-content;max-width:100%;margin:0 auto;' in s,'main preview card styling preserved')
need('0 0 0 9px #F8FCFF,0 0 0 10px #D4E4EF' in s,'editor card styling preserved')

# Upload/function guardrails.
need('key="upload_v73"' in s,'native stable uploader key unchanged')
need('gsf-v91-upload-status' in s,'upload status preserved')
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'subtitle VAI fix preserved')
need('_main_recipe_selected=True' in s and '_inline_recipe_selected=True' in s,'apply changes fix preserved')
need('gsf-v98-3-home-compact' in s,'compact home preserved')
need('numero_clip=3' in s,'three AI clips preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final render quality preserved')
print('V98.7 new-video regression: PASS')
