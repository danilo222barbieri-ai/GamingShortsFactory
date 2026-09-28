from pathlib import Path
import ast,sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
ast.parse(s)

def need(ok,msg):
    if not ok: raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V99 FINAL Architecture' in s,'V99 FINAL architecture marker')
need('gsfUploadCapabilities' in s,'bucket capability discovery')
need("'/direct-upload/bucket/init'" in s,'bucket multipart init')
need('gsfPutPresignedRetry' in s,'presigned multipart retry')
need("'/direct-upload/bucket/complete'" in s,'bucket multipart completion')
need("'/direct-upload/bucket/status?upload_id='" in s,'bucket materialization status')
need('Upload diretto…' in s and 'Preparazione video…' in s,'bucket progress states')
need('load_prescan_from_marker' in s,'worker prescan bridge')
need('scan = _gsf_ai_scan_base(input_file)' in s,'local scan fallback preserved')
need('GSF_AI_ENGINE_VERSION = "v52-keyframe-turbo"' in s,'V99 AI engine preserved')

# Frozen V98/V99 contracts.
need('const CHUNK=16*1024*1024;' in s and 'const CONCURRENCY=6;' in s,'direct fallback frozen')
need('uploadChunkWithRetry' in s,'fallback retry preserved')
need('((220,391,424) if vertical else (520,293,332))' in s,'editor dimensions frozen')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main player frozen')
need('numero_clip=3' in s,'three AI clips preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'render quality preserved')
print('V99 FINAL Architecture regression: PASS')
