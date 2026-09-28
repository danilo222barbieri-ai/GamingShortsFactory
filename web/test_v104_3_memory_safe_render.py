from pathlib import Path
import ast
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_render_core")
core=ast.get_source_segment(s,node) or ""

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

# Memory safety regression: one x264 worker thread only.
need('"-threads","1"' in core,"final x264 render uses one thread")
need('"-threads","2"' not in core,"two-thread x264 render is removed")
need('"rc-lookahead=16:ref=2:bframes=2"' in core,"bounded x264 memory params preserved")

# Quality contract must not move.
for token,label in [
    ('"-preset","medium"',"preset medium preserved"),
    ('"-crf","14"',"CRF 14 preserved"),
    ('"-profile:v","high"',"H.264 High preserved"),
    ('"-level:v","4.2"',"H.264 level 4.2 preserved"),
    ('"-pix_fmt","yuv420p"',"yuv420p preserved"),
    ('"-fpsmax","60"',"60 fps cap preserved"),
    ('"-b:a","192k"',"AAC 192k preserved"),
]:
    need(token in core,label)

# Diagnostics must be present on the actual final render path.
for marker in [
    "GSF_FINAL_RENDER_START",
    "GSF_FINAL_RENDER_EXIT",
    "GSF_FINAL_RENDER_TIMEOUT",
    "GSF_FINAL_RENDER_EXCEPTION",
]:
    need(marker in core,f"{marker} diagnostic present")

# Later legal/footer work must survive this render-only patch.
need('href="/privacy"' in s,"Privacy footer preserved")
need('href="/terms"' in s,"Terms footer preserved")

compile(s,str(p),"exec")
print("V104.3 memory-safe render: PASS")
