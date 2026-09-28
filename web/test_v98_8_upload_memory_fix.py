from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.8 Upload Memory Fix' in s,'V98.8 marker')
need('def _gsf_v93_release_analysis_memory():' in s,'existing low-memory helper preserved')
need('_gsf_v93_release_analysis_memory()' in s[s.index('def _gsf_start_new_video'):s.index('_gsf_restore_persistent_state()')],'new-video callback releases AI memory')
need('globals().get("_gsf_ai_whisper_tiny")' in s,'AI Whisper cache release preserved')
need('globals().get("_gsf_subtitle_whisper_model")' in s,'subtitle Whisper cache release preserved')
need('ctypes.CDLL("libc.so.6").malloc_trim(0)' in s,'allocator memory trim preserved')

# Upload mechanics remain unchanged.
need('key="upload_v73"' in s,'stable uploader unchanged')
need('chunk=video_obj.read(8*1024*1024)' in s,'upload materialization remains chunked')
need('f.write(chunk)' in s,'upload still streams to disk in chunks')
need('_gsf_has_active_video=(' in s,'new-video visibility fix preserved')
need('"＋ NUOVO VIDEO"' in s,'new-video button preserved')

# UI/player guardrails.
need('((220,391,424) if vertical else (520,293,332))' in s,'editor 16:9 stays 520x293')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main preview stays 640x360')
need('↶ RESET CONTROLLI' not in s and '↶ RESET' in s,'short reset label preserved')
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'subtitle VAI preserved')
need('_main_recipe_selected=True' in s and '_inline_recipe_selected=True' in s,'apply changes preserved')
need('numero_clip=3' in s,'three AI clips preserved')
need('"-crf","21"' in s,'final render quality preserved')
print('V98.8 upload memory regression: PASS')
