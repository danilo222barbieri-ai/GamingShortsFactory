#!/usr/bin/env python3
import ast
import importlib.util
import os
import py_compile
import sys
import threading
import time
from pathlib import Path


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:", msg)


app = Path(sys.argv[1] if len(sys.argv) > 1 else "/app/GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py")
upload_server = Path(sys.argv[2] if len(sys.argv) > 2 else "/app/web/direct_upload_server.py")
gate = Path(sys.argv[3] if len(sys.argv) > 3 else "/app/web/render_gate_v293.py")

need(gate.is_file(), "V293 render gate module exists")
gate_src = gate.read_text(encoding="utf-8")
need("BoundedSemaphore" in gate_src, "render gate uses a process-wide bounded semaphore")
need("GSF_FINAL_RENDER_SLOTS" in gate_src, "render gate is explicitly configurable")
need("GSF_FINAL_RENDER_WAIT" in gate_src, "render gate logs queue wait")
need("GSF_FINAL_RENDER_ACQUIRED" in gate_src, "render gate logs acquisition")
need("GSF_FINAL_RENDER_RELEASED" in gate_src, "render gate logs release")

# Runtime behavior: two callers must never enter the guarded section together
# with the production-safe default of one slot.
os.environ["GSF_FINAL_RENDER_SLOTS"] = "1"
spec = importlib.util.spec_from_file_location("render_gate_v293_test", gate)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
state = {"active": 0, "max_active": 0}
lock = threading.Lock()


def guarded_probe():
    with mod.render_slot("test"):
        with lock:
            state["active"] += 1
            state["max_active"] = max(state["max_active"], state["active"])
        time.sleep(0.08)
        with lock:
            state["active"] -= 1


threads = [threading.Thread(target=guarded_probe) for _ in range(2)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join(timeout=3)
need(state["max_active"] == 1, "render gate serializes concurrent final renders")

need(upload_server.is_file(), "direct upload server exists")
upload_src = upload_server.read_text(encoding="utf-8")
compact_upload = upload_src.replace(" ", "")
need('GSF_MATERIALIZE_CONCURRENCY","1"' in compact_upload, "materialization defaults to one transfer worker")
need("returnmax(1,min(2,value))" in compact_upload, "materialization concurrency is hard-capped at two")

need(app.is_file(), "V293 guarded production app exists")
app_src = app.read_text(encoding="utf-8")
tree = ast.parse(app_src)
core = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_gsf_render_core"), None)
need(core is not None, "final render core still exists")
segment = ast.get_source_segment(app_src, core) or ""
need("_gsf_render_slot_v293" in segment, "final render core acquires V293 render slot")

with_nodes = [n for n in ast.walk(core) if isinstance(n, ast.With)]
protected = False
for node in with_nodes:
    for item in node.items:
        expr = item.context_expr
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id == "_gsf_render_slot_v293":
            protected = True
need(protected, "FFmpeg final render is wrapped by the global render gate")


def list_has_pair(flag, value):
    for node in ast.walk(core):
        if not isinstance(node, ast.List):
            continue
        vals = [x.value if isinstance(x, ast.Constant) else None for x in node.elts]
        for i in range(len(vals) - 1):
            if vals[i] == flag and vals[i + 1] == value:
                return True
    return False


need(list_has_pair("-preset", "medium"), "render keeps x264 medium preset")
need(list_has_pair("-crf", "14"), "render keeps CRF 14")
need(list_has_pair("-threads", "1"), "render keeps one x264 thread")
need(list_has_pair("-profile:v", "high"), "render keeps H.264 High profile")
need(list_has_pair("-level:v", "4.2"), "render keeps H.264 level 4.2")
need("GSF_FINAL_RENDER_SLOTS" in app_src, "production app exposes the render slot setting")

py_compile.compile(str(gate), doraise=True)
py_compile.compile(str(upload_server), doraise=True)
py_compile.compile(str(app), doraise=True)
print("V293 render memory guard: PASS")
