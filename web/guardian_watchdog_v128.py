from __future__ import annotations

import threading
import time
from pathlib import Path


ENGINE_VERSION="v128-proactive-guardian"


def _mtime(path):
    try:
        return float(Path(path).stat().st_mtime)
    except Exception:
        return 0.0


def recent_sessions(runtime_root,now=None,active_window=21600,max_sessions=24):
    root=Path(runtime_root)/"sessions"
    now=float(time.time() if now is None else now)
    active_window=max(300.0,float(active_window or 21600))
    rows=[]
    if not root.is_dir():
        return rows
    try:
        entries=list(root.iterdir())
    except Exception:
        return rows
    for session in entries:
        if not session.is_dir():
            continue
        sid=session.name
        if not sid or len(sid)>80:
            continue
        candidates=[
            session/".active",
            session/"render_job.json",
            session/"media"/".direct_upload_ready.json",
            session/"media"/"gaming_short_finale_share.mp4",
        ]
        marker_times=[_mtime(x) for x in candidates]
        marker_latest=max(marker_times or [0.0])
        latest=marker_latest if marker_latest>0 else _mtime(session)
        if latest<=0 or now-latest>active_window:
            continue
        rows.append({"sid":sid,"last_seen":latest,"age":max(0.0,now-latest)})
    rows.sort(key=lambda x:x["last_seen"],reverse=True)
    return rows[:max(1,int(max_sessions or 24))]


class ProactiveGuardian:
    """Bounded watchdog. It calls only pre-approved safe repair callbacks."""

    def __init__(
        self,
        runtime_root,
        tick_fn,
        quality_fn=None,
        interval=60.0,
        active_window=21600.0,
        max_sessions=24,
        failure_limit=3,
        breaker_seconds=300.0,
    ):
        self.runtime_root=Path(runtime_root)
        self.tick_fn=tick_fn
        self.quality_fn=quality_fn
        self.interval=max(15.0,float(interval or 60.0))
        self.active_window=max(300.0,float(active_window or 21600.0))
        self.max_sessions=max(1,min(100,int(max_sessions or 24)))
        self.failure_limit=max(1,int(failure_limit or 3))
        self.breaker_seconds=max(60.0,float(breaker_seconds or 300.0))
        self.failures={}
        self.last_run=0.0
        self.last_summary={}
        self._stop=threading.Event()
        self._thread=None

    def _blocked(self,sid,now):
        row=dict(self.failures.get(sid) or {})
        return float(row.get("blocked_until") or 0.0)>now

    def _success(self,sid):
        self.failures.pop(sid,None)

    def _failure(self,sid,now):
        row=dict(self.failures.get(sid) or {})
        count=int(row.get("count") or 0)+1
        row={"count":count,"last_failure":now,"blocked_until":0.0}
        if count>=self.failure_limit:
            row["blocked_until"]=now+self.breaker_seconds
            row["count"]=0
        self.failures[sid]=row

    def run_once(self,now=None):
        now=float(time.time() if now is None else now)
        sessions=recent_sessions(
            self.runtime_root,
            now=now,
            active_window=self.active_window,
            max_sessions=self.max_sessions,
        )
        checked=0
        repaired=0
        quality_scheduled=0
        blocked=0
        errors=0
        details=[]

        for item in sessions:
            sid=item["sid"]
            if self._blocked(sid,now):
                blocked+=1
                continue
            try:
                result=self.tick_fn(sid,False)
                checked+=1
                if not isinstance(result,dict) or not result.get("ok",False):
                    errors+=1
                    self._failure(sid,now)
                    continue
                self._success(sid)
                repairs=list(result.get("repairs") or [])
                if repairs:
                    repaired+=1
                stable_ready=bool(result.get("stable_ready"))
                if stable_ready and self.quality_fn is not None:
                    try:
                        q=self.quality_fn(sid)
                        if isinstance(q,dict) and q:
                            quality_scheduled+=1
                    except Exception:
                        pass
                if repairs:
                    details.append({"sid":sid,"repairs":repairs[:6]})
            except Exception:
                errors+=1
                self._failure(sid,now)

        summary={
            "engine":ENGINE_VERSION,
            "checked":checked,
            "repaired_sessions":repaired,
            "quality_sessions":quality_scheduled,
            "blocked_sessions":blocked,
            "errors":errors,
            "recent_sessions":len(sessions),
            "details":details[:12],
            "checked_at":now,
        }
        self.last_run=now
        self.last_summary=summary
        return summary

    def loop(self):
        # First pass shortly after process start, then bounded periodic checks.
        while not self._stop.wait(self.interval):
            try:
                self.run_once()
            except Exception:
                pass

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return self._thread
        self._stop.clear()
        self._thread=threading.Thread(
            target=self.loop,
            name="gsf-proactive-guardian",
            daemon=True,
        )
        self._thread.start()
        return self._thread

    def stop(self):
        self._stop.set()
