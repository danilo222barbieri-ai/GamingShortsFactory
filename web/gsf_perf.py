#!/usr/bin/env python3
import json
import os
import time
from pathlib import Path

CGROUP_ROOT=Path("/sys/fs/cgroup")
_SECRET_MARKERS=("secret","token","password","authorization","credential","private_key","access_key")

def _read_int(path):
    try:
        raw=Path(path).read_text(encoding="utf-8").strip()
        if not raw or raw=="max":
            return None
        return int(raw)
    except Exception:
        return None

def snapshot_memory():
    current=_read_int(CGROUP_ROOT/"memory.current")
    limit=_read_int(CGROUP_ROOT/"memory.max")

    # cgroup v1 fallback
    if current is None:
        current=_read_int(CGROUP_ROOT/"memory"/"memory.usage_in_bytes")
    if limit is None:
        limit=_read_int(CGROUP_ROOT/"memory"/"memory.limit_in_bytes")

    pct=None
    if isinstance(current,int) and isinstance(limit,int) and limit>0:
        pct=round((current/limit)*100.0,3)

    return {
        "current_bytes":current,
        "limit_bytes":limit,
        "percent":pct,
    }

def _safe_fields(fields):
    out={}
    for key,value in fields.items():
        low=str(key).lower()
        if any(marker in low for marker in _SECRET_MARKERS):
            out[key]="<redacted>"
            continue
        if isinstance(value,Path):
            value=str(value)
        if isinstance(value,(str,int,float,bool)) or value is None:
            out[key]=value
        else:
            try:
                json.dumps(value)
                out[key]=value
            except Exception:
                out[key]=str(value)
    return out

def perf_event(name,**fields):
    payload={
        "event":str(name),
        "ts":round(time.time(),3),
        "pid":os.getpid(),
        "memory":snapshot_memory(),
    }
    payload.update(_safe_fields(fields))
    print("GSF_PERF "+json.dumps(payload,separators=(",",":"),ensure_ascii=False),flush=True)
