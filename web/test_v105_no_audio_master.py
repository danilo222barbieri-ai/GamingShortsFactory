#!/usr/bin/env python3
from pathlib import Path
import ast,sys

p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

need("def _gsf_source_has_audio(" in s,"renderer has source-audio probe")
need("anullsrc=channel_layout=stereo:sample_rate=48000" in s,"silent stereo 48 kHz fallback exists")
need("'-map', '0:v:0', '-map', '1:a:0'" in s or '"-map","0:v:0","-map","1:a:0"' in s,
     "silent-audio path explicitly maps source video and generated audio")
need("_gsf_source_has_audio(source_path)" in s,"final render chooses audio path from source")
need("'-af', af" in s or '"-af",af' in s or '"-af", af' in s,
     "normal audio filter path is preserved")
compile(s,str(p),"exec")
print("V105 no-audio master contract: PASS")
