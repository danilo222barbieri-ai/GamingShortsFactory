"""GSF Core Render Client.

Client helper for dispatching video rendering jobs to an isolated background
worker (e.g. Railway worker service) to keep the web/frontend container lean
and prevent Out-Of-Memory (OOM) crashes during FFmpeg rendering.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True, slots=True)
class RenderJobRequest:
    job_id: str
    session_id: str
    source_key: str
    output_key: str
    cmd: List[str]
    timeout_seconds: float = 600.0
    metadata: Optional[Dict[str, Any]] = None


def get_worker_url() -> str:
    """Return the configured worker base URL or empty string."""
    return str(os.environ.get("GSF_WORKER_URL", "") or "").rstrip("/")


def get_worker_token() -> str:
    """Return the worker authentication secret token or empty string."""
    return str(os.environ.get("GSF_WORKER_TOKEN", "") or "").strip()


def is_worker_configured() -> bool:
    """Return True if an external worker URL is provided."""
    return bool(get_worker_url())


def dispatch_render_to_worker(
    request: RenderJobRequest,
    worker_url: Optional[str] = None,
    worker_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a render job specification to the background worker service."""
    base_url = (worker_url or get_worker_url()).rstrip("/")
    if not base_url:
        raise ValueError("Worker URL is not configured")

    token = worker_token or get_worker_token()
    payload = {
        "job_id": request.job_id,
        "session_id": request.session_id,
        "source_key": request.source_key,
        "output_key": request.output_key,
        "cmd": request.cmd,
        "timeout": request.timeout_seconds,
        "metadata": request.metadata or {},
        "created_at": time.time(),
    }

    data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/render",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Content-Length": str(len(data)),
            **({"X-GSF-Worker-Token": token} if token else {}),
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {"ok": True, "queued": True}
    except urllib.error.HTTPError as exc:
        err_msg = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Worker render request failed with status {exc.code}: {err_msg[:200]}") from exc
    except Exception as exc:
        raise RuntimeError(f"Unable to reach worker at {base_url}: {str(exc)[:200]}") from exc


def get_render_job_status(
    job_id: str,
    worker_url: Optional[str] = None,
    worker_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Poll the current execution state of a render job."""
    base_url = (worker_url or get_worker_url()).rstrip("/")
    if not base_url:
        return {}

    token = worker_token or get_worker_token()
    query = urllib.parse.urlencode({"job_id": job_id})
    req = urllib.request.Request(
        f"{base_url}/status?{query}",
        headers={"X-GSF-Worker-Token": token} if token else {},
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body) if body else {}
            return data.get("job") or data
    except Exception:
        return {}
