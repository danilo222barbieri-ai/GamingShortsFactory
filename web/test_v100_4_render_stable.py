from pathlib import Path
import ast,subprocess,sys,tempfile,time

p=Path(sys.argv[1]); s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

core_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
core=ast.get_source_segment(s,core_node) or ''

need('Gaming Shorts Factory · V100.4 Render Stable' in s,'V100.4 marker')
need('"libx264 HQ"' in core,'software HQ encoder installed')
need('"h264_qsv"' not in core,'QSV final-render fallback removed')
need('"-preset","medium"' in core,'medium preset installed')
need('"-crf","14"' in core,'CRF14 HQ installed')
need('"-threads","2"' in core,'two render threads requested')
need('duration*24.0' in core,'60fps-safe render timeout installed')

for marker in (
    'Gaming Shorts Factory · V100.4 Render Stable',
    'scale=1080:1920:flags=lanczos',
    'GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"',
    'gsf-mobile-preview-gap',
    'gsfUploadCapabilities',
    'GSF_AI_ENGINE_VERSION = "v52-keyframe-turbo"',
    'numero_clip=3',
    '((220,391,424) if vertical else (520,293,332))',
    '_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430',
):
    need(marker in s,f'preserved: {marker}')

# Exercise the exact final software encoder on 1080x1920 60fps.
with tempfile.TemporaryDirectory() as td:
    out=Path(td)/'hq60.mp4'
    cmd=[
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','lavfi','-i','testsrc2=size=1080x1920:rate=60',
        '-t','1.0',
        '-c:v','libx264','-preset','medium','-crf','14','-threads','2',
        '-profile:v','high','-level:v','4.2','-pix_fmt','yuv420p',
        '-an','-movflags','+faststart',str(out)
    ]
    t0=time.perf_counter()
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=90)
    elapsed=time.perf_counter()-t0
    need(r.returncode==0 and out.exists() and out.stat().st_size>0,'real 1080x1920 60fps x264 HQ encode executes')
    print(f'V100.4 60fps encode smoke time: {elapsed:.3f}s')

print('V100.4 render stability regression: PASS')
