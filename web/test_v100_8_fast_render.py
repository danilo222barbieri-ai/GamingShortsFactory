from pathlib import Path
import ast,subprocess,sys,tempfile

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

core_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
core=ast.get_source_segment(s,core_node) or ''

need('Gaming Shorts Factory · V100.8 Fast Render' in s,'V100.8 marker')
need('"-threads","2"' in core,'two x264 threads enabled')
need('rc-lookahead=16:ref=2:bframes=2' in core,'V100.7 memory bounds preserved')
need('"-crf","14"' in core,'CRF14 quality preserved')
need('"-preset","medium"' in core,'medium preset preserved')
need('"-fpsmax","60"' in core,'60fps guard preserved')
need('"-profile:v","high"' in core,'H.264 High profile preserved')
need('"scale=1080:1920:flags=lanczos"' in s or 'scale=1080:1920:flags=lanczos' in s,'1080x1920 Lanczos output preserved')
need('GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"' in s,'Smart Reframe preserved')
need('numero_clip=3' in s,'AI 3 clips preserved')
need('Math.min(10,requestedConcurrency)' in s,'MAX Upload desktop preserved')
need('Math.min(6,requestedConcurrency)' in s,'MAX Upload mobile preserved')
need('"h264_qsv"' not in core,'QSV remains absent')

with tempfile.TemporaryDirectory() as td:
    out=Path(td)/'fast_render_60.mp4'
    cmd=[
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','lavfi','-i','testsrc2=size=1080x1920:rate=60',
        '-t','1',
        '-c:v','libx264','-preset','medium','-crf','14','-threads','2',
        '-x264-params','rc-lookahead=16:ref=2:bframes=2',
        '-profile:v','high','-level:v','4.2','-pix_fmt','yuv420p',
        '-fpsmax','60','-an','-movflags','+faststart',str(out)
    ]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=90)
    need(r.returncode==0 and out.exists() and out.stat().st_size>0,'real 1080x1920 60fps two-thread encode executes')

print('V100.8 Fast Render regression: PASS')
