#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path

import gsf_bucket_bridge as bridge

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

def marker_dir():
    td=tempfile.TemporaryDirectory()
    root=Path(td.name)
    (root/".direct_upload_ready.json").write_text(
        json.dumps({"analysis_key":"analysis/sid/upload/v52-keyframe-turbo.json"}),
        encoding="utf-8",
    )
    return td,root

def fake_clock(step=1.0):
    state={"t":0.0}
    def mono():
        state["t"]+=step
        return state["t"]
    return mono,state

# Healthy worker still scanning beyond the old 8 s window; result appears later.
td,root=marker_dir()
try:
    bridge._cfg=lambda: {"bucket":"b","access":"a","secret":"s","endpoint":"e","region":"auto","style":"virtual"}
    bridge._client=lambda c: object()
    scan={"meta":{"expected":"worker"}}
    calls={"analysis":0,"status":0}
    def load_obj(client,c,key,engine):
        calls["analysis"]+=1
        if calls["analysis"]>=5:
            return scan
        return None
    def worker_status(key):
        calls["status"]+=1
        return {"reachable":True,"state":"scanning" if calls["status"]<4 else "done"}
    bridge._load_analysis_object=load_obj
    bridge._worker_status=worker_status
    mono,state=fake_clock(3.0)
    bridge.time.monotonic=mono
    bridge.time.sleep=lambda _: None
    result=bridge.load_prescan_from_marker(root,"v52-keyframe-turbo",wait_seconds=20)
    need(result is scan,"healthy slow worker result is awaited instead of duplicated locally")
    need(calls["status"]>=3,"worker status is polled while analysis is running")
finally:
    td.cleanup()

# Worker error must trigger immediate local fallback.
td,root=marker_dir()
try:
    bridge._client=lambda c: object()
    calls={"analysis":0,"status":0}
    bridge._load_analysis_object=lambda *args: calls.__setitem__("analysis",calls["analysis"]+1) or None
    def worker_error(key):
        calls["status"]+=1
        return {"reachable":True,"state":"error","error":"boom"}
    bridge._worker_status=worker_error
    mono,state=fake_clock(1.0)
    bridge.time.monotonic=mono
    bridge.time.sleep=lambda _: None
    result=bridge.load_prescan_from_marker(root,"v52-keyframe-turbo",wait_seconds=30)
    need(result is None,"worker error returns local-fallback signal")
    need(calls["status"]==1,"worker error does not burn the full wait window")
finally:
    td.cleanup()

# Worker unavailable must stay bounded and return fallback signal.
td,root=marker_dir()
try:
    bridge._client=lambda c: object()
    bridge._load_analysis_object=lambda *args: None
    bridge._worker_status=lambda key: {"reachable":False,"state":"unavailable"}
    mono,state=fake_clock(2.0)
    bridge.time.monotonic=mono
    bridge.time.sleep=lambda _: None
    result=bridge.load_prescan_from_marker(root,"v52-keyframe-turbo",wait_seconds=6)
    need(result is None,"unreachable worker falls back locally")
    need(state["t"]<=12.0,"unreachable worker fallback remains bounded")
finally:
    td.cleanup()

# Cached S3 result wins immediately, without worker dependency.
td,root=marker_dir()
try:
    cached={"meta":{"cached":True}}
    bridge._client=lambda c: object()
    bridge._load_analysis_object=lambda *args: cached
    bridge._worker_status=lambda key: (_ for _ in ()).throw(AssertionError("worker should not be polled"))
    mono,state=fake_clock(1.0)
    bridge.time.monotonic=mono
    bridge.time.sleep=lambda _: None
    result=bridge.load_prescan_from_marker(root,"v52-keyframe-turbo",wait_seconds=30)
    need(result is cached,"cached analysis returns immediately")
finally:
    td.cleanup()

print("V105 prescan bridge: PASS")
