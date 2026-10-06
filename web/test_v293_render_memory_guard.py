#!/usr/bin/env python3
import ast
import py_compile
import sys
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

need(upload_server.is_file(), "direct upload server exists")
upload_src = upload_server.read_text(encoding="utf-8")
need('GSF_MATERIALIZE_CONCURRENCY","1"' in upload_src, "materialization defaults to one transfer worker")
need("return max(1,min(2,value))" in upload_src.replace(" ", ""), "materialization concurrency is hard-capped at two")

need(app.is_file(), "V293 guarded production app exists")n