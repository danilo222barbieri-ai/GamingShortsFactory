# V401 Performance & Stability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce frontend upload memory duplication and make worker prescan jobs persistent, recoverable, and progress-aware.

**Architecture:** Add a small V401 job-state module backed by the existing S3-compatible bucket, wire it into the existing AI worker without replacing the semaphore queue, and add an idempotent runtime source patch that converts the two Streamlit fallback `video.getvalue()` disk writes into bounded streaming copies. Keep V400 render/editor behavior untouched.

**Tech Stack:** Python 3, Streamlit fallback upload object, boto3-compatible S3 client already present in worker, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-13-v401-performance-stability.md`

## Global Constraints
- V400 production baseline stays untouched until all V401 gates pass.
- Keep `gsf_editor_2027_v1086` unchanged.
- Keep V400/V399 render policy unchanged.
- No Redis/database/new Railway volume.
- Bucket job-state persistence is best-effort and must not fail prescan.
- Runtime patch must be idempotent.

## Review Focus
- Worker restart during `semantic`: status must become interrupted/retryable and a resubmit must not be blocked by stale persistence.
- Analysis artifact completed immediately before a restart: artifact existence must win over a stale persisted active state.
- Bucket metadata outage: live job must continue using RAM state.
- Streamlit fallback cursor is non-zero before copy: copy must still write full content and restore cursor.
- Repeated startup patch application: generated runtime source must remain unchanged after first successful patch.

---

### Task 1: V401 contract tests

**Files:**
- Create: `web/test_v401_performance_stability.py`
- Create: `.github/workflows/v401-performance-stability-tdd.yml`

**Interfaces:**
- Consumes: current V400 sources.
- Produces: executable contract for job persistence/recovery, streaming fallback, worker integration, and V400 regression.

- [ ] Write tests for job-state persistence/recovery, semantic active-state handling, progress metadata, streaming copy/cursor restore, patch idempotence, worker wiring, and startup hook wiring.
- [ ] Run branch CI and verify RED because V401 production modules do not exist yet.
- [ ] Commit.

### Task 2: Persistent worker job state

**Files:**
- Create: `web/job_state_v401.py`
- Modify: `web/ai_worker_server.py`

**Interfaces:**
- Produces: `ACTIVE_JOB_STATES`, `enrich_job_state(payload, now=None)`, `persist_job_state(client, bucket, job_id, payload)`, `load_job_state(client, bucket, job_id)`, `recover_persisted_state(payload)`.
- Worker produces `_set_job_state(job_id, payload)` and `_get_job_state(job_id, analysis_key="")`.

- [ ] Implement minimal state module.
- [ ] Replace direct `JOBS[...]` mutations with best-effort persisted `_set_job_state`.
- [ ] Make `/status` load/recover persisted state and let completed analysis artifacts override stale active persistence.
- [ ] Use `ACTIVE_JOB_STATES` for duplicate suppression including `semantic`.
- [ ] Run V401 test and verify worker-state portion GREEN.
- [ ] Commit.

### Task 3: Streamed fallback upload materialization

**Files:**
- Create: `web/fix_v401_frontend_memory.py`
- Modify: `web/apply_v343_v293_compat.py`

**Interfaces:**
- Produces: `stream_uploaded_file(uploaded, target, chunk_size=4*1024*1024)`, `patch_runtime_source(text)`, `patch_runtime_file(path)`.

- [ ] Implement bounded stream copy with cursor restore.
- [ ] Replace the two fallback `video.getvalue()` disk writes through the idempotent runtime patch.
- [ ] Invoke V401 runtime patch after V293/V343 compatibility materialization on every startup.
- [ ] Run V401 test and verify GREEN.
- [ ] Commit.

### Task 4: Regression and release gate

**Files:**
- No product behavior changes unless a failing regression requires a V401-scoped fix.

**Interfaces:**
- Consumes: Tasks 1-3.
- Produces: merge-ready V401 branch.

- [ ] Run V401, V400, V399, editor contract, and Production Gate checks.
- [ ] Review branch diff for UI/render regressions.
- [ ] Merge only when all checks pass.
- [ ] Verify GitHub main SHA, Railway deployment SHA/status, frontend health, and issue counters before calling V401 live.
