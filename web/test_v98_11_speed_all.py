from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok: raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.11 Speed All' in s,'V98.11 marker')
need('GSF_AI_ENGINE_VERSION = "v51-speed-adaptive"' in s,'new AI cache version')
need('"tier":"medium"' in s and '"video_fps":1.25' in s and '"analysis_width":160' in s,'medium scan optimized')
need('"video_fps":0.75' in s and '"analysis_width":144' in s,'long scan optimized')
need('FFMPEG_PATH,"-hide_banner","-threads","1","-i",str(input_file),"-vn"' in s,'audio scan CPU budget')
need('FFMPEG_PATH,"-hide_banner","-threads","1","-i",str(input_file),"-an"' in s,'video scan CPU budget')
need('"fps=3,scale=160:-2,select=' in s,'long shortlist refine optimized')
need('shortlist_target=8 if profile in ("auto","director","reaction") else 7' in s,'shortlist reduced safely')
need('coarse_target=shortlist_target+(3 if adaptive_scan else 0)' in s,'coarse shortlist reduced')
need('workers=min(2,len(shortlist))' in s,'refine workers match 2-vCPU box')
need('profile=="reaction" and len(enriched)<4' in s,'reaction Whisper checks reduced')
need('"-af","highpass=f=70,lowpass=f=7800"' in s,'voice extraction simplified')
need('beam_size=(1 if GSF_LOW_MEMORY_WEB else 2)' in s,'fast web Whisper beam')
need('best_of=(1 if GSF_LOW_MEMORY_WEB else 2)' in s,'fast web Whisper best-of')

# Upload + UX from pass 1.
need('const CHUNK=32*1024*1024;' in s,'32MB chunks preserved')
need('const CONCURRENCY=2;' in s,'two upload workers preserved')
need('window.parent.location.reload()' not in s,'browser hard refresh remains removed')
need('@st.fragment(run_every="0.35s")' in s,'fast upload watcher preserved')
need('CHIUDI EDITOR' not in s and 'CHIUDI' in s,'compact close label preserved')
need('↶ RESET CONTROLLI' not in s and '↶ RESET' in s,'compact reset preserved')

# Quality/function contracts.
need('numero_clip=3' in s,'three AI clips preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final x264 quality preserved')
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'subtitle VAI preserved')
need('((220,391,424) if vertical else (520,293,332))' in s,'editor dimensions preserved')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main preview preserved')
print('V98.11 speed-all regression: PASS')
