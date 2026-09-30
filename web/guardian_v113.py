from __future__ import annotations

import json
import os
import time
from pathlib import Path


def _read_json(path):
    try:
        data=json.loads(Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data,dict) else {}
    except Exception:
        return {}


def _write_json_atomic(path,payload):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=Path(str(path)+".guardian.tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    os.replace(tmp,path)


def source_restore_plan(session_root):
    """Return the deterministic bucket restore plan for a missing local source."""
    root=Path(session_root)
    marker=root/"media"/".direct_upload_ready.json"
    meta=_read_json(marker)
    if not meta:
        return {}
    local_path=Path(str(meta.get("path") or "")) if meta.get("path") else None
    if local_path is not None and local_path.is_file():
        return {}
    key=str(meta.get("bucket_key") or "").strip()
    if not key:
        return {}
    return {
        "path":str(meta.get("path") or ""),
        "name":str(meta.get("name") or ""),
        "size":int(meta.get("size") or 0),
        "upload_id":str(meta.get("upload_id") or ""),
        "bucket_key":key,
        "analysis_key":str(meta.get("analysis_key") or ""),
    }


def inspect_and_repair_local(session_root,now=None,stale_after=900):
    """Safe local self-healing for one browser session. No network, no code edits."""
    root=Path(session_root)
    now=float(time.time() if now is None else now)
    stale_after=max(60.0,float(stale_after or 900))
    job_path=root/"render_job.json"
    stable=root/"media"/"gaming_short_finale_share.mp4"
    source_marker=root/"media"/".direct_upload_ready.json"

    job=_read_json(job_path)
    status=str(job.get("status") or "")
    repairs=[]
    stable_ready=False
    stable_bytes=0
    stable_mtime=0.0
    try:
        if stable.is_file():
            stable_bytes=int(stable.stat().st_size)
            stable_mtime=float(stable.stat().st_mtime)
            stable_ready=stable_bytes>1024
    except Exception:
        stable_ready=False

    if stable_ready and status not in ("ready","cancelled"):
        started=float(job.get("started_at") or 0.0)
        job.update({
            "status":"ready",
            "completed_at":float(job.get("completed_at") or stable_mtime or now),
            "final_path":str(stable),
            "final_bytes":stable_bytes,
            "pid":0,
            "guardian_repaired_at":now,
        })
        if started:
            job["started_at"]=started
        _write_json_atomic(job_path,job)
        status="ready"
        repairs.append("job_from_final")

    started=float(job.get("started_at") or 0.0)
    if status=="running" and started>0 and now-started>stale_after:
        job.update({
            "status":"stale",
            "pid":0,
            "guardian_repaired_at":now,
            "guardian_reason":"render_timeout",
        })
        _write_json_atomic(job_path,job)
        status="stale"
        repairs.append("render_stale")

    needs_final_restore=bool(status=="ready" and not stable_ready)
    source=_read_json(source_marker)
    source_path=Path(str(source.get("path") or "")) if source.get("path") else None
    source_missing=bool(source and (source_path is None or not source_path.is_file()))
    needs_source_restore=bool(source_missing and source.get("bucket_key"))

    return {
        "ok":True,
        "status":status,
        "repairs":repairs,
        "stable_ready":bool(stable_ready),
        "stable_bytes":int(stable_bytes),
        "needs_final_restore":needs_final_restore,
        "needs_source_restore":needs_source_restore,
        "source_known":bool(source),
        "checked_at":now,
    }
