from pathlib import Path
import ast,subprocess,sys,tempfile,json

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

need('Gaming Shorts Factory · V100.6 FPS Guard' in s,'V100.6 marker')
need('"-fpsmax","60"' in core,'60fps maximum guard installed')
need('"libx264 HQ"' in core,'software HQ encoder preserved')
need('"-preset","medium"' in core,'medium preset preserved')
need('"-crf","14"' in core,'CRF14 preserved')
need('"-threads","2"' in core,'two render threads preserved')
need('"h264_qsv"' not in core,'QSV remains removed')
need('Math.min(10,requestedConcurrency)' in s,'V100.5 desktop upload preserved')
need('Math.min(6,requestedConcurrency)' in s,'V100.5 mobile upload preserved')
need('GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"' in s,'Smart Reframe preserved')
need('numero_clip=3' in s,'AI 3 clips preserved')

# Real FFmpeg smoke test: deliberately feed a 600fps source and verify fpsmax clamps output.
with tempfile.TemporaryDirectory() as td:
    out=Path(td)/'fps_guard.mp4'
    cmd=[
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','lavfi','-i','testsrc2=size=320x180:rate=600',
        '-t','0.5',
        '-c:v','libx264','-preset','ultrafast','-crf','23','-threads','2',
        '-pix_fmt','yuv420p','-fpsmax','60','-an',str(out)
    ]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
    need(r.returncode==0 and out.exists() and out.stat().st_size>0,'real 600fps source encodes with fpsmax guard')
    pr=subprocess.run([
        'ffprobe','-v','error','-select_streams','v:0',
        '-show_entries','stream=avg_frame_rate,r_frame_rate',
        '-of','json',str(out)
    ],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=10)
    data=json.loads(pr.stdout or '{}')
    st=(data.get('streams') or [{}])[0]
    def ratio(v):
        a,b=(v or '0/1').split('/')
        return float(a)/float(b) if float(b) else 0.0
    need(ratio(st.get('avg_frame_rate'))<=60.01,'output average fps capped at 60')
    need(ratio(st.get('r_frame_rate'))<=60.01,'output nominal fps capped at 60')

print('V100.6 FPS Guard regression: PASS')
