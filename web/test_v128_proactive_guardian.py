from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,"/app/web")

from guardian_watchdog_v128 import ProactiveGuardian, recent_sessions

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    sessions=root/"sessions"
    sessions.mkdir(parents=True)

    a=sessions/"alpha"
    b=sessions/"beta"
    old=sessions/"old"
    for p in (a,b,old):
        (p/"media").mkdir(parents=True)

    now=10000.0
    (a/".active").write_text("a")
    (b/"render_job.json").write_text('{"status":"ready"}')
    (old/".active").write_text("old")

    import os
    os.utime(a/".active",(now-10,now-10))
    os.utime(b/"render_job.json",(now-20,now-20))
    os.utime(old/".active",(now-9999,now-9999))

    rows=recent_sessions(root,now=now,active_window=3600,max_sessions=10)
    ids=[x["sid"] for x in rows]
    if ids!=["alpha","beta"]:
        raise SystemExit("V128 recent session selection failed: "+repr(ids))

    calls=[]
    def tick(sid,force):
        calls.append((sid,force))
        return {
            "ok":True,
            "stable_ready":sid=="alpha",
            "repairs":["source_from_bucket"] if sid=="beta" else [],
        }

    quality=[]
    def q(sid):
        quality.append(sid)
        return {"status":"pass"}

    watchdog=ProactiveGuardian(
        root,tick,quality_fn=q,
        interval=15,active_window=3600,max_sessions=10,
    )
    result=watchdog.run_once(now=now)
    if result["checked"]!=2 or result["repaired_sessions"]!=1:
        raise SystemExit("V128 watchdog summary failed: "+repr(result))
    if quality!=["alpha"]:
        raise SystemExit("V128 quality scheduling failed: "+repr(quality))
    if not calls or any(force is not False for _,force in calls):
        raise SystemExit("V128 watchdog must use throttled safe Guardian tick")

    # Circuit breaker: repeated failed sessions are blocked instead of looping.
    def bad_tick(sid,force):
        raise RuntimeError("synthetic")
    breaker=ProactiveGuardian(
        root,bad_tick,interval=15,active_window=3600,max_sessions=10,
        failure_limit=2,breaker_seconds=300,
    )
    r1=breaker.run_once(now=now)
    r2=breaker.run_once(now=now+1)
    r3=breaker.run_once(now=now+2)
    if r1["errors"]!=2 or r2["errors"]!=2 or r3["blocked_sessions"]!=2:
        raise SystemExit("V128 Guardian circuit breaker failed")

server=Path("/app/web/direct_upload_server.py").read_text(encoding="utf-8")
for marker in (
    "from guardian_watchdog_v128 import ProactiveGuardian as _ProactiveGuardian",
    "def _start_proactive_guardian()",
    "GSF_V128_GUARDIAN started",
    'clean=="/guardian/watchdog"',
    '"proactive_guardian"',
    "_start_proactive_guardian()",
):
    if marker not in server:
        raise SystemExit("V128 server watchdog marker missing: "+marker)

compile(server,"<v128-server>","exec")
print("V128 proactive Guardian contracts: PASS")
