import subprocess, tempfile, time
from pathlib import Path

FF='ffmpeg'
def need(ok,msg):
    if not ok: raise AssertionError(msg)
    print('PASS:',msg)

with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'probe.mp4'
    make=[
        FF,'-hide_banner','-loglevel','error',
        '-f','lavfi','-i','testsrc2=size=640x360:rate=30:duration=8',
        '-f','lavfi','-i','sine=frequency=900:sample_rate=48000:duration=8',
        '-c:v','libx264','-preset','ultrafast','-g','30','-keyint_min','30',
        '-pix_fmt','yuv420p','-c:a','aac','-shortest',str(p),'-y'
    ]
    subprocess.run(make,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    need(p.is_file() and p.stat().st_size>0,'synthetic gameplay created')

    cmd=[
        FF,'-hide_banner','-threads','2','-skip_frame','nokey',
        '-i',str(p),'-an','-vf',
        "scale=128:-2,select='gte(scene,0)',metadata=print",
        '-f','null','-'
    ]
    t0=time.perf_counter()
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
    elapsed=time.perf_counter()-t0
    raw=(r.stdout or '')+'\n'+(r.stderr or '')
    need(r.returncode==0,'keyframe-only FFmpeg scan executes')
    need('lavfi.scene_score=' in raw,'keyframe scan emits motion metadata')
    need(elapsed<15,'keyframe scan completes promptly')

    audio=[
        FF,'-hide_banner','-threads','1','-i',str(p),'-vn','-af',
        'aresample=8000,asetnsamples=n=4000:p=0,astats=metadata=1:reset=1,'
        'ametadata=print:key=lavfi.astats.Overall.RMS_level,'
        'ametadata=print:key=lavfi.astats.Overall.Peak_level',
        '-f','null','-'
    ]
    r2=subprocess.run(audio,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
    raw2=(r2.stdout or '')+'\n'+(r2.stderr or '')
    need(r2.returncode==0,'turbo audio scan executes')
    need('lavfi.astats.Overall.RMS_level=' in raw2,'audio scan emits RMS metadata')

print('V99 FFmpeg turbo integration: PASS')
