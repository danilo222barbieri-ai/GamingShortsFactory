#!/usr/bin/env python3
from pathlib import Path
import ast
import sys

server=Path("/app/web/direct_upload_server.py").read_text(encoding="utf-8")
patch=Path("/app/web/apply_v105_perf_telemetry.py")
if not patch.is_file():
    raise AssertionError("apply_v105_perf_telemetry.py missing")

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

tree=ast.parse(server)
imports=[]
for node in tree.body:
    if isinstance(node,ast.ImportFrom) and node.module=="gsf_perf":
        imports.extend(a.name for a in node.names)
need("perf_event" in imports,"direct upload server imports perf_event")

for marker in [
    "prescan_queue_start",
    "prescan_queue_end",
    "materialize_start",
    "materialize_end",
    "materialize_error",
]:
    need(marker in server,f"direct upload server emits {marker}")

patch_text=patch.read_text(encoding="utf-8")
need("render_start" in patch_text,"V105 app patch instruments render start")
need("render_end" in patch_text,"V105 app patch instruments render end")
need("local_scan_start" in patch_text,"V105 app patch instruments local scan fallback")
need("local_scan_end" in patch_text,"V105 app patch instruments local scan completion")

print("V105 pipeline telemetry markers: PASS")
