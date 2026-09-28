import importlib.util
import os
import subprocess
import tempfile
from pathlib import Path

spec=importlib.util.spec_from_file_location("worker","/app/web/ai_worker_server.py")
worker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)

def need(ok,msg):
    if not ok: raise AssertionError(msg)
    print('PASS:',msg)

fn=worker._load_scan_fn()
need(callable(fn),'worker extracted exact V99 scan function')

with tempfile.TemporaryDirectory() as td:
    p=Path(td)/"worker_probe.mp4"
    cmd=[
        "ffmpeg","-hide_banner","-loglevel","error",
        "-f","lavfi","-i","testsrc2=size=320x180:rate=15:duration=4",
        "-f","lavfi","-i","sine=frequency=700:sample_rate=16000:duration=4",
        "-c:v","libx264","-preset","ultrafast","-g","15","-pix_fmt","yuv420p",
        "-c:a","aac","-shortest",str(p),"-y"
    ]
    subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    scan=fn(str(p))
    need(isinstance(scan,dict),'worker scan returns dict')
    need(scan.get("step")==0.5,'worker scan grid matches app')
    need(len(scan.get("audio",[]))>0,'worker scan has audio')
    need(len(scan.get("motion",[]))>0,'worker scan has motion')
    need((scan.get("meta") or {}).get("duration_seconds",0)>0,'worker scan metadata valid')

print('V99 worker engine integration: PASS')
