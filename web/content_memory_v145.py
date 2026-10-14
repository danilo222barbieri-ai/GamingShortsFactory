from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


def _d(v):
    return dict(v) if isinstance(v,dict) else {}


def candidate_fingerprint(source_fingerprint,short_pkg):
    """Fingerprint one edited moment, not only the source video."""
    s=_d(short_pkg)
    mount=_d(s.get("mount"))
    trim=_d(mount.get("trim"))
    payload={
        "source":str(source_fingerprint or ""),
        "start":round(float(s.get("start") or 0.0),2),
        "event":str(s.get("event") or ""),
        "rank":int(s.get("rank") or 0),
        "trim_start":round(float(trim.get("start") or 0.0),2),
        "trim_end":round(float(trim.get("end") or 0.0),2),
        "hook":str(mount.get("hook") or "")[:120],
    }
    raw=json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def series_key(source_fingerprint,game="",event=""):
    raw="|".join((str(source_fingerprint or ""),str(game or "").lower(),str(event or "").lower()))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def memory_record(source_fingerprint,short_pkg,metadata=None):
    s=_d(short_pkg); meta=_d(metadata)
    return {
        "fingerprint":candidate_fingerprint(source_fingerprint,s),
        "source_fingerprint":str(source_fingerprint or ""),
        "series_key":series_key(source_fingerprint,meta.get("game"),s.get("event")),
        "created_at":float(meta.get("created_at") or time.time()),
        "event":str(s.get("event") or "highlight"),
        "start":round(float(s.get("start") or 0.0),3),
        "rank":int(s.get("rank") or 0),
        "game":str(meta.get("game") or ""),
        "platform":str(meta.get("platform") or ""),
        "status":str(meta.get("status") or "prepared"),
        "performance_score":float(meta.get("performance_score") or 0.0),
    }


def inspect_memory(records,record):
    rows=[_d(x) for x in (records or []) if isinstance(x,dict)]
    fp=str(_d(record).get("fingerprint") or "")
    src=str(_d(record).get("source_fingerprint") or "")
    series=str(_d(record).get("series_key") or "")
    exact=[x for x in rows if fp and str(x.get("fingerprint") or "")==fp]
    same_source=[x for x in rows if src and str(x.get("source_fingerprint") or "")==src]
    same_series=[x for x in rows if series and str(x.get("series_key") or "")==series]
    best=max(same_source,key=lambda x:float(x.get("performance_score") or 0.0),default={})
    return {
        "duplicate":bool(exact),
        "duplicate_count":len(exact),
        "source_count":len(same_source),
        "series_count":len(same_series),
        "series_key":series,
        "best_from_source":best,
        "recommendation":"use_alternative_moment" if exact else ("continue_series" if same_source else "new_content"),
    }
