from pathlib import Path
import ast
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

core=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_render_core")
wrapper=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_v105_run_render")
remote=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_v105_remote_render")

calls=[
    n for n in ast.walk(core)
    if isinstance(n,ast.Call)
    and isinstance(n.func,ast.Name)
    and n.func.id=="_gsf_v105_run_render"
]
need(len(calls)==1,"final renderer uses exactly one V105 render wrapper")
call=calls[0]
need(
    len(call.args)==3
    and isinstance(call.args[0],ast.Name) and call.args[0].id=="cmd"
    and isinstance(call.args[1],ast.Name) and call.args[1].id=="output_path"
    and isinstance(call.args[2],ast.Name) and call.args[2].id=="_diag_timeout",
    "render wrapper receives existing command/output/timeout"
)
direct=[
    n for n in ast.walk(core)
    if isinstance(n,ast.Call)
    and isinstance(n.func,ast.Attribute)
    and isinstance(n.func.value,ast.Name)
    and n.func.value.id=="subprocess"
    and n.func.attr=="run"
    and n.args and isinstance(n.args[0],ast.Name) and n.args[0].id=="cmd"
]
need(not direct,"final core no longer runs heavy FFmpeg directly before wrapper")

wrapper_src=ast.get_source_segment(s,wrapper) or ""
remote_src=ast.get_source_segment(s,remote) or ""
need("subprocess.run" in wrapper_src,"wrapper preserves exact local subprocess fallback")
need("GSF_REMOTE_RENDER_FALLBACK" in wrapper_src,"fallback is diagnosed")
need("worker_url+\"/render\"" in remote_src and "def _gsf_v105_worker_status" in s and "/render/status?" in s,"remote client submits and polls render job")
need("render-stage/" in remote_src and "render-results/" in remote_src,"remote render uses bounded S3 staging/results")
need("bytes(" not in remote_src and ".read_bytes(" not in remote_src,"remote render does not whole-copy media to Python bytes")

# Quality contract remains in the command built by the existing renderer.
pairs=[]
for n in ast.walk(core):
    if not isinstance(n,ast.List):
        continue
    vals=[e.value if isinstance(e,ast.Constant) else None for e in n.elts]
    for i in range(len(vals)-1):
        if isinstance(vals[i],str) and isinstance(vals[i+1],str):
            pairs.append((vals[i],vals[i+1]))
for pair,label in [
    (("-preset","medium"),"preset medium preserved"),
    (("-crf","14"),"CRF14 preserved"),
    (("-threads","1"),"one-thread local fallback preserved"),
    (("-x264-params","rc-lookahead=16:ref=2:bframes=2"),"bounded x264 params preserved"),
    (("-profile:v","high"),"H.264 High preserved"),
    (("-level:v","4.2"),"H.264 level 4.2 preserved"),
    (("-pix_fmt","yuv420p"),"yuv420p preserved"),
    (("-fpsmax","60"),"60fps cap preserved"),
    (("-b:a","192k"),"AAC 192k preserved"),
]:
    need(pair in pairs,label)

need("Gaming Shorts Factory · V105 Hardening" in s,"V105 version marker present")
compile(s,str(p),"exec")
print("V105 render-offload generated app: PASS")
