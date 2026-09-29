#!/usr/bin/env python3
import subprocess
import tempfile
from pathlib import Path
import v105_render_benchmark as bench

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

with tempfile.TemporaryDirectory() as td:
    root=Path(td)
    silent=root/"silent.mp4"
    r=subprocess.run([
        bench.FFMPEG,"-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i","testsrc2=size=320x180:rate=30",
        "-t","0.5","-c:v","libx264","-preset","ultrafast",
        "-pix_fmt","yuv420p",str(silent)
    ],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    need(r.returncode==0,"no-audio fixture generated")

    cmd=bench.render_command(silent,root/"out.mp4","medium_crf14_t1")
    joined=" ".join(map(str,cmd))
    need("anullsrc=channel_layout=stereo:sample_rate=48000" in joined,
         "benchmark injects silent stereo audio for no-audio source")
    need("-map 0:v:0 -map 1:a:0" in joined,
         "benchmark explicitly maps generated silent audio")

print("V105 benchmark no-audio contract: PASS")
