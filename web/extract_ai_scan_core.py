#!/usr/bin/env python3
import ast
import sys
from pathlib import Path

src=Path(sys.argv[1])
out=Path(sys.argv[2])
source=src.read_text(encoding="utf-8")
tree=ast.parse(source)
order=[
    "_gsf_ai_scan_profile_for_duration",
    "_gsf_interpolate_motion_points",
    "_gsf_norm_series",
    "_gsf_ai_scan_base",
]
found={
    node.name:node
    for node in tree.body
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in order
}
missing=[name for name in order if name not in found]
if missing:
    raise RuntimeError("missing scan functions: "+", ".join(missing))

header='''# Generated at image build time from the tested V99 scan checkpoint.
import math
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

FFMPEG_PATH="/usr/local/bin/ffmpeg"

def durata_video(path):
    cmd=[
        "ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(path)
    ]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60)
    return float((r.stdout or "0").strip() or 0.0)

'''
body="\n\n".join(ast.unparse(found[name]) for name in order)+"\n"
out.write_text(header+body,encoding="utf-8")
compile(out.read_text(encoding="utf-8"),str(out),"exec")
print(f"generated AI scan core: {out}")
