from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.9 Direct Upload' in s,'V98.9 marker')
need("def _gsf_v989_direct_ready():" in s,'direct-upload marker reader exists')
need("def _gsf_v989_direct_upload_html(loaded=False):" in s,'direct uploader UI exists')
need("'/direct-upload/chunk'" in s,'browser posts to direct upload endpoint')
need("const CHUNK=4*1024*1024" in s,'browser uses 4MB chunks')
need("X-GSF-Chunk-Start" in s and "X-GSF-Chunk-Count" in s,'chunk protocol metadata present')
need('@st.fragment(run_every="1s")' in s,'automatic upload completion watcher exists')
need('_GSFRecoveredUpload(_gsf_direct_source' in s,'completed direct upload reuses disk-backed source')
need('if GSF_WEB_MODE:' in s and 'else:\n        video=st.file_uploader(' in s,'native uploader retained only as local fallback')
need('(not GSF_WEB_MODE and st.session_state.get("upload_v73") is not None)' in s,'active-video guard no longer requires web native uploader')

# Previously approved UI and functions stay untouched.
need('((220,391,424) if vertical else (520,293,332))' in s,'editor 16:9 remains 520x293')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main preview remains 640x360')
need('↶ RESET CONTROLLI' not in s and '↶ RESET' in s,'short reset label preserved')
need('"＋ NUOVO VIDEO"' in s and 'on_click=_gsf_start_new_video' in s,'new-video reset preserved')
need('_gsf_v93_release_analysis_memory()' in s,'new-video memory release preserved')
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'subtitle VAI preserved')
need('_main_recipe_selected=True' in s and '_inline_recipe_selected=True' in s,'apply changes preserved')
need('numero_clip=3' in s,'three AI clips preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final render quality preserved')
print('V98.9 direct upload regression: PASS')
