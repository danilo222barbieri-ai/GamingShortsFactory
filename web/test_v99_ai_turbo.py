from pathlib import Path
import ast,sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
ast.parse(s)

def need(ok,msg):
    if not ok: raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V99 AI Turbo' in s,'V99 marker')
need('GSF_AI_ENGINE_VERSION = "v52-keyframe-turbo"' in s,'V99 scan cache version')
need('"tier":"medium_turbo"' in s and '"keyframes_only":True' in s,'medium keyframe scan')
need('"tier":"long_turbo"' in s and '"analysis_width":112' in s,'long turbo scan')
need('"aresample=8000,asetnsamples=n=4000:p=0,"' in s,'lighter audio scan')
need('"-skip_frame","nokey"' in s,'decoder skips non-keyframes')
need('FFMPEG_PATH,"-hide_banner","-threads","2"' in s,'coarse video uses available CPU')
need('"keyframes_only":keyframes_only' in s,'scan diagnostics expose turbo mode')
need('"fps=2,scale=144:-2,select=' in s,'focused dense refinement')
need('candidate_stride=2 if adaptive_scan else 1' in s,'adaptive ranking stride')
need('shortlist_target=6' in s and 'coarse_target=7 if adaptive_scan' in s,'small refinement shortlist')

# V98 frozen invariants.
need('const CHUNK=16*1024*1024;' in s and 'const CONCURRENCY=6;' in s,'V98 upload frozen')
need('uploadChunkWithRetry' in s,'upload retry frozen')
need('((220,391,424) if vertical else (520,293,332))' in s,'editor dimensions frozen')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main player frozen')
need('numero_clip=3' in s,'three AI clips')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'render quality preserved')
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'subtitle VAI preserved')
print('V99 AI Turbo regression: PASS')
