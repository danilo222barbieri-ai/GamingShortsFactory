#!/usr/bin/env python3
import contextlib
import io
import json
import tempfile
from pathlib import Path

import gsf_perf

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

with tempfile.TemporaryDirectory() as td:
    root=Path(td)
    (root/"memory.current").write_text("456000000\n",encoding="utf-8")
    (root/"memory.max").write_text("1000000000\n",encoding="utf-8")
    old=gsf_perf.CGROUP_ROOT
    gsf_perf.CGROUP_ROOT=root
    try:
        snap=gsf_perf.snapshot_memory()
    finally:
        gsf_perf.CGROUP_ROOT=old

need(snap["current_bytes"]==456000000,"cgroup current memory parsed")
need(snap["limit_bytes"]==1000000000,"cgroup memory limit parsed")
need(45.0 < snap["percent"] < 46.5,"cgroup memory percent calculated")

buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    gsf_perf.perf_event(
        "unit_test",
        elapsed_seconds=1.25,
        access_token="must-not-leak",
        client_secret="must-not-leak",
        safe_value="ok",
    )
line=buf.getvalue().strip()
need(line.startswith("GSF_PERF "),"structured telemetry prefix")
payload=json.loads(line[len("GSF_PERF "):])
need(payload["event"]=="unit_test","event name serialized")
need(payload["safe_value"]=="ok","safe fields preserved")
need("must-not-leak" not in line,"secret values are redacted")
need(payload["access_token"]=="<redacted>","token field redacted")
need(payload["client_secret"]=="<redacted>","secret field redacted")

print("V105 telemetry contract: PASS")
