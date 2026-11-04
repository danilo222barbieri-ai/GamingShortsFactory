#!/usr/bin/env python3
"""
GSF Global Background Job System (Blocco 1, 2, 3, 4).

Provides a centralized, persistent, idempotent background job queue and worker pool
with:
- Unique job IDs and strict user/session (`sid` / `account_id`) isolation
- Canonical states: queued (in attesa), running (in esecuzione),
  completed (completato), failed (fallito), cancelled (annullato)
- Real measurable progress (0..100%) from byte counters, FFmpeg `-progress`, or stage weights
- Persistence across server restarts (atomic local JSON + optional S3 bucket sync)
- Controlled retries, error recovery, and idempotency keys (zero duplicate execution)
- Railway concurrency semaphores per resource class (CPU/FFmpeg, AI/Whisper, I/O)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import signal
import subprocess
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Mapping

JOB_STATUS_LABELS_IT = {
    "queued": "in attesa",
    "running": "in esecuzione",
    "completed": "completato",
    "failed": "fallito",
    "cancelled": "annullato",
}

ACTIVE_STATUSES = frozenset({"queued", "running"})
TERMINAL_STATUSES = frozenset({"completed", "failed", "cancelled"})

VALID_JOB_KINDS = frozenset({
    "upload",
    "ai_analysis",
    "whisper",
    "ffmpeg_render",
    "create_short",
    "export",
    "social_publish",
    "project_save",
})

# Resource classes to protect Railway container RAM & CPU
JOB_RESOURCE_CLASS = {
    "ffmpeg_render": "heavy_cpu",
    "create_short": "heavy_cpu",
    "export": "heavy_cpu",
    "ai_analysis": "ai_engine",
    "whisper": "ai_engine",
    "upload": "network_io",
    "social_publish": "network_io",
    "project_save": "network_io",
}

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


def _safe_id(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    if _SAFE_ID_RE.fullmatch(raw):
        return raw
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "", raw)[:80]
    return cleaned or fallback


def _clamp_progress(val: Any) -> float | None:
    if val is None:
        return None
    try:
        x = float(val)
        if not math.isfinite(x):
            return None
        return round(max(0.0, min(100.0, x)), 1)
    except Exception:
        return None


class JobCancelledError(RuntimeError):
    """Raised when a running job detects a cancellation request."""


class GlobalJobManager:
    """Central persistent job manager for Gaming Shorts Factory."""

    def __init__(
        self,
        runtime_root: str | Path | None = None,
        s3_client_fn: Callable[[], Any] | None = None,
        s3_bucket: str = "",
        notify_fn: Callable[[str, dict[str, Any]], None] | None = None,
        max_cpu_workers: int | None = None,
        max_ai_workers: int | None = None,
        max_io_workers: int | None = None,
    ) -> None:
        self.runtime_root = Path(
            runtime_root or os.environ.get("GSF_RUNTIME_ROOT", "/tmp/gsf-runtime")
        )
        self.s3_client_fn = s3_client_fn
        self.s3_bucket = str(s3_bucket or "")
        self.notify_fn = notify_fn

        cpu_limit = max(1, int(max_cpu_workers or os.environ.get("GSF_MAX_CONCURRENT_RENDERS", "1") or 1))
        ai_limit = max(1, int(max_ai_workers or os.environ.get("GSF_MAX_CONCURRENT_AI", "1") or 1))
        io_limit = max(1, int(max_io_workers or os.environ.get("GSF_MAX_CONCURRENT_IO", "3") or 3))

        self._semaphores = {
            "heavy_cpu": threading.Semaphore(cpu_limit),
            "ai_engine": threading.Semaphore(ai_limit),
            "network_io": threading.Semaphore(io_limit),
        }
        self._limits = {
            "heavy_cpu": cpu_limit,
            "ai_engine": ai_limit,
            "network_io": io_limit,
        }
        self._executor = ThreadPoolExecutor(
            max_workers=max(4, cpu_limit + ai_limit + io_limit + 2),
            thread_name_prefix="gsf-global-job",
        )
        self._lock = threading.RLock()
        self._handlers: dict[str, Callable[[dict[str, Any], "JobContext"], Any]] = {}
        self._jobs_cache: dict[tuple[str, str], dict[str, Any]] = {}
        self._cancel_flags: set[tuple[str, str]] = set()
        self._active_pids: dict[tuple[str, str], int] = {}

    # ------------------------------------------------------------------
    # Storage paths & persistence
    # ------------------------------------------------------------------
    def _jobs_dir(self, sid: str) -> Path:
        clean_sid = _safe_id(sid, "anon")
        d = self.runtime_root / "sessions" / clean_sid / "jobs"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _job_file(self, sid: str, job_id: str) -> Path:
        return self._jobs_dir(sid) / f"{_safe_id(job_id, 'job')}.json"

    def _s3_key(self, sid: str, job_id: str) -> str:
        return f"jobs/{_safe_id(sid, 'anon')}/{_safe_id(job_id, 'job')}.json"

    def _write_job_atomic(self, sid: str, job: dict[str, Any], sync_s3: bool = False) -> dict[str, Any]:
        clean_sid = _safe_id(sid, "anon")
        jid = _safe_id(job.get("id"), "job")
        job["status_it"] = JOB_STATUS_LABELS_IT.get(str(job.get("status") or ""), "in attesa")
        job["stage_label"] = str(job.get("stage") or "")
        job["updated_at"] = time.time()
        snapshot = json.loads(json.dumps(job, default=str))

        with self._lock:
            self._jobs_cache[(clean_sid, jid)] = snapshot
            path = self._job_file(clean_sid, jid)
            tmp = path.with_suffix(f".{os.getpid()}.{threading.get_ident()}.tmp")
            try:
                tmp.write_text(json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
                os.replace(tmp, path)
            except Exception:
                try:
                    tmp.unlink(missing_ok=True)
                except Exception:
                    pass

        if sync_s3 and self.s3_bucket and self.s3_client_fn is not None:
            def _push_s3(payload_bytes: bytes, key: str) -> None:
                try:
                    client = self.s3_client_fn()
                    if client is not None:
                        client.put_object(
                            Bucket=self.s3_bucket,
                            Key=key,
                            Body=payload_bytes,
                            ContentType="application/json",
                            CacheControl="no-store",
                        )
                except Exception:
                    pass

            raw_bytes = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            threading.Thread(
                target=_push_s3,
                args=(raw_bytes, self._s3_key(clean_sid, jid)),
                daemon=True,
            ).start()

        return snapshot

    # ------------------------------------------------------------------
    # Handler Registration
    # ------------------------------------------------------------------
    def register_handler(
        self,
        kind: str,
        fn: Callable[[dict[str, Any], "JobContext"], Any],
    ) -> None:
        self._handlers[str(kind)] = fn

    # ------------------------------------------------------------------
    # Querying & Recovery
    # ------------------------------------------------------------------
    def get_job(self, sid: str, job_id: str) -> dict[str, Any] | None:
        clean_sid = _safe_id(sid)
        jid = _safe_id(job_id)
        if not clean_sid or not jid:
            return None
        with self._lock:
            cached = self._jobs_cache.get((clean_sid, jid))
            if cached is not None:
                return json.loads(json.dumps(cached))
        path = self._job_file(clean_sid, jid)
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    with self._lock:
                        self._jobs_cache[(clean_sid, jid)] = data
                    return json.loads(json.dumps(data))
            except Exception:
                pass
        # Fallback to S3 if missing on local disk after container redeploy
        if self.s3_bucket and self.s3_client_fn is not None:
            try:
                client = self.s3_client_fn()
                if client is not None:
                    obj = client.get_object(Bucket=self.s3_bucket, Key=self._s3_key(clean_sid, jid))
                    data = json.loads(obj["Body"].read().decode("utf-8"))
                    if isinstance(data, dict):
                        self._write_job_atomic(clean_sid, data, sync_s3=False)
                        return data
            except Exception:
                pass
        return None

    def list_jobs(self, sid: str, limit: int = 25, include_terminal: bool = True) -> list[dict[str, Any]]:
        clean_sid = _safe_id(sid)
        if not clean_sid:
            return []
        jobs_dir = self._jobs_dir(clean_sid)
        rows: dict[str, dict[str, Any]] = {}
        for f in jobs_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data.get("id"):
                    jid = str(data["id"])
                    rows[jid] = data
                    with self._lock:
                        self._jobs_cache[(clean_sid, jid)] = data
            except Exception:
                continue
        with self._lock:
            for (csid, jid), cached in self._jobs_cache.items():
                if csid == clean_sid:
                    rows[jid] = json.loads(json.dumps(cached))

        filtered = [
            r for r in rows.values()
            if include_terminal or str(r.get("status") or "") in ACTIVE_STATUSES
        ]
        filtered.sort(key=lambda r: float(r.get("created_at") or 0.0), reverse=True)
        return filtered[: max(1, int(limit))]

    def recover_after_restart(self, sid: str | None = None, auto_resume: bool = True) -> list[dict[str, Any]]:
        """Inspect persisted jobs on disk and recover any left in `queued`/`running` when the process restarted."""
        sessions_dir = self.runtime_root / "sessions"
        if not sessions_dir.is_dir():
            return []
        target_sids = [_safe_id(sid)] if sid else [d.name for d in sessions_dir.iterdir() if d.is_dir()]
        recovered: list[dict[str, Any]] = []

        for s in target_sids:
            if not s:
                continue
            jdir = sessions_dir / s / "jobs"
            if not jdir.is_dir():
                continue
            for f in jdir.glob("*.json"):
                try:
                    job = json.loads(f.read_text(encoding="utf-8"))
                except Exception:
                    continue
                if not isinstance(job, dict):
                    continue
                status = str(job.get("status") or "")
                if status not in ACTIVE_STATUSES:
                    continue
                jid = _safe_id(job.get("id"))
                kind = str(job.get("kind") or "")
                can_auto = (
                    auto_resume
                    and bool(job.get("auto_retry_on_boot", True))
                    and kind in self._handlers
                    and int(job.get("attempt", 1) or 1) < int(job.get("max_retries", 3) or 3)
                )
                if can_auto:
                    job["status"] = "queued"
                    job["stage"] = "Ripresa automatica dopo riavvio server"
                    job["recovered_after_restart"] = True
                    job["attempt"] = int(job.get("attempt", 1) or 1) + 1
                    snap = self._write_job_atomic(s, job, sync_s3=True)
                    recovered.append(snap)
                    self._schedule_execution(s, jid)
                else:
                    job["previous_status"] = status
                    job["status"] = "failed"
                    job["interrupted_by_restart"] = True
                    job["retryable"] = True
                    job["error"] = "Lavoro interrotto dal riavvio del server. Puoi riprenderlo con Riprova."
                    snap = self._write_job_atomic(s, job, sync_s3=True)
                    recovered.append(snap)
        return recovered

    # ------------------------------------------------------------------
    # Enqueue, Update, Cancel, Retry
    # ------------------------------------------------------------------
    def enqueue_job(
        self,
        sid: str,
        kind: str,
        title: str = "",
        payload: Mapping[str, Any] | None = None,
        idempotency_key: str = "",
        account_id: str = "",
        max_retries: int = 3,
        auto_retry_on_boot: bool = True,
        initial_status: str = "queued",
        initial_progress: float | None = 0.0,
        auto_start: bool = True,
    ) -> dict[str, Any]:
        clean_sid = _safe_id(sid)
        if not clean_sid:
            raise ValueError("invalid session id")
        clean_kind = str(kind or "").strip().lower()
        if clean_kind not in VALID_JOB_KINDS:
            raise ValueError(f"unsupported job kind: {clean_kind}")

        idem = str(idempotency_key or "").strip()[:120]
        if idem:
            existing = self._find_by_idempotency(clean_sid, clean_kind, idem)
            if existing is not None:
                return existing

        now = time.time()
        job_id = f"job_{clean_kind}_{uuid.uuid4().hex[:14]}"
        resource_class = JOB_RESOURCE_CLASS.get(clean_kind, "network_io")
        status = initial_status if initial_status in ("queued", "running") else "queued"
        job: dict[str, Any] = {
            "id": job_id,
            "sid": clean_sid,
            "account_id": _safe_id(account_id),
            "kind": clean_kind,
            "resource_class": resource_class,
            "title": str(title or clean_kind)[:160],
            "status": status,
            "status_it": JOB_STATUS_LABELS_IT.get(status, "in attesa"),
            "progress": _clamp_progress(initial_progress),
            "stage": "In coda" if status == "queued" else "Avviato",
            "idempotency_key": idem,
            "attempt": 1,
            "max_retries": max(1, int(max_retries or 3)),
            "auto_retry_on_boot": bool(auto_retry_on_boot),
            "retryable": True,
            "payload": dict(payload or {}),
            "result": {},
            "error": "",
            "pid": 0,
            "created_at": now,
            "started_at": now if status == "running" else 0.0,
            "completed_at": 0.0,
            "updated_at": now,
        }
        snapshot = self._write_job_atomic(clean_sid, job, sync_s3=True)
        if auto_start and clean_kind in self._handlers and status == "queued":
            self._schedule_execution(clean_sid, job_id)
        return snapshot

    def enqueue(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self.enqueue_job(*args, **kwargs)

    def _find_by_idempotency(self, sid: str, kind: str, idempotency_key: str) -> dict[str, Any] | None:
        for job in self.list_jobs(sid, limit=40, include_terminal=True):
            if str(job.get("kind") or "") != kind:
                continue
            if str(job.get("idempotency_key") or "") != idempotency_key:
                continue
            st = str(job.get("status") or "")
            if st in ACTIVE_STATUSES:
                return job
            if st == "completed" and (time.time() - float(job.get("completed_at") or 0.0)) < 3600.0:
                return job
        return None

    def update_job(
        self,
        sid: str,
        job_id: str,
        *,
        status: str | None = None,
        state: str | None = None,
        progress: float | None = None,
        stage: str | None = None,
        stage_label: str | None = None,
        result: Mapping[str, Any] | None = None,
        error: str | None = None,
        pid: int | None = None,
        extra: Mapping[str, Any] | None = None,
        sync_s3: bool = False,
    ) -> dict[str, Any] | None:
        if status is None and state is not None:
            status = state
        if stage is None and stage_label is not None:
            stage = stage_label
        clean_sid = _safe_id(sid)
        jid = _safe_id(job_id)
        with self._lock:
            job = self.get_job(clean_sid, jid)
            if not isinstance(job, dict):
                return None
            prev_status = str(job.get("status") or "")
            if status is not None and status in JOB_STATUS_LABELS_IT:
                job["status"] = status
                if status == "running" and not float(job.get("started_at") or 0.0):
                    job["started_at"] = time.time()
                elif status in TERMINAL_STATUSES:
                    job["completed_at"] = time.time()
                    if status == "completed":
                        job["progress"] = 100.0
                    self._active_pids.pop((clean_sid, jid), None)
            if progress is not None:
                clamped = _clamp_progress(progress)
                if clamped is not None:
                    job["progress"] = clamped
            if stage is not None:
                job["stage"] = str(stage)[:220]
            if result is not None:
                cur_res = dict(job.get("result") or {})
                cur_res.update(dict(result))
                job["result"] = cur_res
            if error is not None:
                job["error"] = str(error)[:400]
            if pid is not None:
                job["pid"] = int(pid or 0)
                if int(pid or 0) > 1:
                    self._active_pids[(clean_sid, jid)] = int(pid)
                else:
                    self._active_pids.pop((clean_sid, jid), None)
            if extra:
                for k, v in extra.items():
                    if k not in ("id", "sid"):
                        job[k] = v

            is_terminal_transition = (
                status in TERMINAL_STATUSES and prev_status != status
            )
            snapshot = self._write_job_atomic(
                clean_sid, job, sync_s3=bool(sync_s3 or is_terminal_transition)
            )

        if is_terminal_transition and self.notify_fn is not None:
            try:
                self.notify_fn(clean_sid, snapshot)
            except Exception:
                pass
        return snapshot

    def cancel_job(self, sid: str, job_id: str, reason: str = "Annullato dall'utente") -> dict[str, Any] | None:
        clean_sid = _safe_id(sid)
        jid = _safe_id(job_id)
        with self._lock:
            job = self.get_job(clean_sid, jid)
            if not isinstance(job, dict):
                return None
            if str(job.get("status") or "") in TERMINAL_STATUSES:
                return job
            self._cancel_flags.add((clean_sid, jid))
            pid = self._active_pids.pop((clean_sid, jid), 0) or int(job.get("pid") or 0)
            if pid > 1:
                try:
                    os.kill(pid, signal.SIGTERM)
                except Exception:
                    pass
            return self.update_job(
                clean_sid,
                jid,
                status="cancelled",
                stage=reason,
                error="",
                pid=0,
                sync_s3=True,
            )

    def retry_job(self, sid: str, job_id: str) -> dict[str, Any] | None:
        clean_sid = _safe_id(sid)
        jid = _safe_id(job_id)
        with self._lock:
            job = self.get_job(clean_sid, jid)
            if not isinstance(job, dict):
                return None
            if str(job.get("status") or "") in ACTIVE_STATUSES:
                return job
            attempt = int(job.get("attempt", 1) or 1) + 1
            max_retries = int(job.get("max_retries", 3) or 3)
            if attempt > max_retries + 1:
                raise ValueError("Numero massimo di tentativi raggiunto per questo lavoro.")
            self._cancel_flags.discard((clean_sid, jid))
            job["attempt"] = attempt
            job["status"] = "queued"
            job["progress"] = 0.0
            job["stage"] = f"In coda (tentativo {attempt})"
            job["error"] = ""
            job["interrupted_by_restart"] = False
            job["completed_at"] = 0.0
            snap = self._write_job_atomic(clean_sid, job, sync_s3=True)

        kind = str(snap.get("kind") or "")
        if kind in self._handlers:
            self._schedule_execution(clean_sid, jid)
        return snap

    def is_cancelled(self, sid: str, job_id: str) -> bool:
        clean_sid = _safe_id(sid)
        jid = _safe_id(job_id)
        if (clean_sid, jid) in self._cancel_flags:
            return True
        job = self.get_job(clean_sid, jid)
        return bool(isinstance(job, dict) and str(job.get("status") or "") == "cancelled")

    # ------------------------------------------------------------------
    # Worker Execution & Concurrency Control
    # ------------------------------------------------------------------
    def _schedule_execution(self, sid: str, job_id: str) -> None:
        self._executor.submit(self._run_job_worker, sid, job_id)

    def _run_job_worker(self, sid: str, job_id: str) -> None:
        job = self.get_job(sid, job_id)
        if not isinstance(job, dict):
            return
        if self.is_cancelled(sid, job_id):
            return
        kind = str(job.get("kind") or "")
        handler = self._handlers.get(kind)
        if handler is None:
            return

        res_class = JOB_RESOURCE_CLASS.get(kind, "network_io")
        sem = self._semaphores.get(res_class, self._semaphores["network_io"])

        # Wait for Railway resource slot while remaining in 'queued' state
        sem.acquire()
        try:
            if self.is_cancelled(sid, job_id):
                return
            current = self.update_job(
                sid,
                job_id,
                status="running",
                stage="In esecuzione",
                progress=max(1.0, float(job.get("progress") or 0.0)),
                sync_s3=True,
            )
            if not isinstance(current, dict):
                return
            ctx = JobContext(self, sid, job_id)
            result = handler(current, ctx)
            if self.is_cancelled(sid, job_id):
                return
            res_dict = result if isinstance(result, Mapping) else {"value": result}
            self.update_job(
                sid,
                job_id,
                status="completed",
                progress=100.0,
                stage="Completato",
                result=res_dict,
                error="",
                pid=0,
                sync_s3=True,
            )
        except JobCancelledError:
            self.update_job(
                sid,
                job_id,
                status="cancelled",
                stage="Annullato",
                pid=0,
                sync_s3=True,
            )
        except Exception as exc:
            if self.is_cancelled(sid, job_id):
                return
            msg = str(exc)[:300] or "Errore durante l'elaborazione"
            cur = self.get_job(sid, job_id) or job
            attempt = int(cur.get("attempt", 1) or 1)
            max_retries = int(cur.get("max_retries", 1) or 1)
            auto_retry = bool((cur.get("payload") or {}).get("auto_retry", False))
            if auto_retry and attempt < max_retries:
                self.update_job(
                    sid,
                    job_id,
                    status="queued",
                    stage=f"Nuovo tentativo automatico ({attempt + 1}/{max_retries})…",
                    error=msg,
                    pid=0,
                    extra={"attempt": attempt + 1},
                    sync_s3=True,
                )
                time.sleep(min(2.0, 0.4 * attempt))
                self._schedule_execution(sid, job_id)
            else:
                self.update_job(
                    sid,
                    job_id,
                    status="failed",
                    stage="Fallito",
                    error=msg,
                    pid=0,
                    sync_s3=True,
                )
        finally:
            sem.release()


class JobContext:
    """Helper passed to background job handlers to report real progress and check cancellation."""

    def __init__(self, manager: GlobalJobManager, sid: str, job_id: str) -> None:
        self.manager = manager
        self.sid = sid
        self.job_id = job_id

    def check_cancelled(self) -> None:
        if self.manager.is_cancelled(self.sid, self.job_id):
            raise JobCancelledError("Job cancelled")

    def set_progress(
        self,
        progress: float | None,
        stage: str | None = None,
        result: Mapping[str, Any] | None = None,
        pid: int | None = None,
    ) -> None:
        self.check_cancelled()
        self.manager.update_job(
            self.sid,
            self.job_id,
            progress=progress,
            stage=stage,
            result=result,
            pid=pid,
        )

    def run_ffmpeg_with_progress(
        self,
        cmd: list[str],
        total_duration_seconds: float,
        stage_prefix: str = "Rendering video",
        timeout_seconds: float = 600.0,
    ) -> subprocess.CompletedProcess[str]:
        """Run an FFmpeg command while streaming real progress percentage (`out_time_us`) into the job."""
        self.check_cancelled()
        dur = max(0.1, float(total_duration_seconds or 15.0))
        # Inject -progress pipe:1 -nostats right after ffmpeg executable
        full_cmd = [cmd[0], "-progress", "pipe:1", "-nostats", *cmd[1:]]
        proc = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.set_progress(2.0, stage=f"{stage_prefix} (avvio)…", pid=proc.pid)
        start_ts = time.monotonic()
        last_update = 0.0
        stdout_lines: list[str] = []

        try:
            assert proc.stdout is not None
            for raw_line in proc.stdout:
                stdout_lines.append(raw_line)
                if self.manager.is_cancelled(self.sid, self.job_id):
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except Exception:
                        proc.kill()
                    raise JobCancelledError("FFmpeg render cancelled")
                if time.monotonic() - start_ts > timeout_seconds:
                    proc.kill()
                    raise TimeoutError("Timeout durante il rendering FFmpeg")

                line = raw_line.strip()
                if line.startswith("out_time_us=") or line.startswith("out_time_ms="):
                    try:
                        val_us = float(line.split("=", 1)[1].strip())
                        sec = val_us / 1_000_000.0
                        pct = min(98.0, max(2.0, (sec / dur) * 100.0))
                        now = time.monotonic()
                        if now - last_update >= 0.25:
                            last_update = now
                            self.set_progress(
                                pct,
                                stage=f"{stage_prefix} · {int(round(pct))}%",
                                pid=proc.pid,
                            )
                    except Exception:
                        pass
            stderr_text = proc.stderr.read() if proc.stderr else ""
            rc = proc.wait(timeout=15)
            return subprocess.CompletedProcess(
                full_cmd,
                rc,
                "".join(stdout_lines),
                stderr_text,
            )
        finally:
            self.manager.update_job(self.sid, self.job_id, pid=0)
