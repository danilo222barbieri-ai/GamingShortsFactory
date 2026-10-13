#!/usr/bin/env python3
import hashlib
import json
import re
import time

ACTIVE_JOB_STATES = frozenset({"queued", "downloading", "scanning", "semantic"})
TERMINAL_JOB_STATES = frozenset({"done", "error", "interrupted"})
STATE_PROGRESS = {
    "queued": 0.05,
    "downloading": 0.20,
    "scanning": 0.50,
    "semantic": 0.80,
    "done": 1.0,
    "error": 1.0,
    "interrupted": 0.0,
}


def _safe_job_id(job_id):
    value = str(job_id or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{1,80}", value):
        return value
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:40]


def job_state_key(job_id):
    return f"worker-jobs/v401/{_safe_job_id(job_id)}.json"


def enrich_job_state(payload, now=None):
    state = dict(payload or {})
    phase = str(state.get("state") or "").strip().lower()
    ts = float(time.time() if now is None else now)
    state["updated_at"] = ts
    state.setdefault("progress", float(STATE_PROGRESS.get(phase, 0.0)))
    if phase == "queued":
        state.setdefault("queued_at", ts)
    return state


def persist_job_state(client, bucket, job_id, payload):
    state = dict(payload or {})
    body = json.dumps(state, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    client.put_object(
        Bucket=str(bucket),
        Key=job_state_key(job_id),
        Body=body,
        ContentType="application/json",
        CacheControl="no-store",
    )
    return state


def load_job_state(client, bucket, job_id):
    obj = client.get_object(Bucket=str(bucket), Key=job_state_key(job_id))
    raw = obj["Body"].read()
    state = json.loads(raw.decode("utf-8"))
    if not isinstance(state, dict):
        raise ValueError("invalid V401 job-state payload")
    return state


def recover_persisted_state(payload):
    state = dict(payload or {})
    phase = str(state.get("state") or "").strip().lower()
    state["persisted"] = True
    if phase in ACTIVE_JOB_STATES:
        previous_progress = float(state.get("progress", STATE_PROGRESS.get(phase, 0.0)) or 0.0)
        state["previous_state"] = phase
        state["state"] = "interrupted"
        state["progress"] = previous_progress
        state["retryable"] = True
    return state
