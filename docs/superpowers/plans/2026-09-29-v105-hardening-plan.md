# Gaming Shorts Factory V105 Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans task-by-task. Steps use checkbox syntax.

**Goal:** Ship a V105 candidate that materially lowers web-process memory pressure and render wall time while preserving approved UI/player behavior and V104.7 social/master quality.

**Architecture:** Keep Streamlit as UI/orchestration. Use S3 as durable media state, move heavy rendering to the existing worker fleet, stream social uploads from files/S3 instead of giant Python byte arrays, and separate worker/web build concerns. Develop on `v105-hardening`; verify on Railway staging before production.

**Tech Stack:** Python 3.12, Streamlit, FFmpeg/libx264, Nginx, boto3/S3, Railway, TikTok/YouTube/Instagram APIs.

**Spec:** `docs/superpowers/specs/2026-09-29-v105-hardening-design.md`

## Global Constraints

- Do not modify approved player dimensions/layout.
- Preserve 1080x1920 / 1920x1080 H.264 social master, CRF 14 quality contract, <=60 fps, AAC 192k / 48 kHz stereo.
- V104.7 production remains rollback until staging stress gates pass.
- No OAuth tokens, signed URLs, secrets or user video contents in logs.
- Every behavior change gets a regression test first.
- Staging storage/session namespace must be isolated from production.

## Review Focus

- Large 60 fps iPhone source: upload + rotation + final render must not exhaust 1 GB web memory.
- Interrupted/retried multipart upload: no corrupt ready marker and no stale false-success state.
- Worker replica switch/restart mid-job: job status must remain observable from shared storage.
- OAuth cancel/return while video is prepared: prepared session/video must survive.
- Social publish of a large master: no whole-master Python bytes copy in the normal web path.

---

### Task 1: Upload + S3 hardening

**Files:**
- Modify: `web/direct_upload_server.py`
- Create: `web/test_v105_upload_hardening.py`

**Interfaces:**
- Produces: `_allowed_cors_origins()`, `_client_upload_concurrency(user_agent)`, bounded materialization config, structured upload/materialize logs.
- Keeps existing `/bucket/init`, `/bucket/complete`, `/bucket/status` response compatibility.

- [ ] Write static/unit tests asserting multi-origin CORS, adaptive browser concurrency, bounded S3 materialization, no forced fsync on S3-derived ephemeral copy, and unchanged fallback fsync.
- [ ] Verify RED against V104.7 code.
- [ ] Implement helpers and instrumentation.
- [ ] Verify GREEN and py_compile.

### Task 2: Minimal persistent AI worker core

**Files:**
- Create: `web/extract_ai_scan_core.py`
- Create: `web/test_v105_worker_core.py`
- Modify: `web/ai_worker_server.py`
- Create: `requirements-worker.txt`
- Create: `Dockerfile.worker`

**Interfaces:**
- Produces: generated `/app/web/generated_ai_scan_core.py` at worker build time.
- Worker status persists to S3 under `worker-jobs/prescan/<job>.json`.
- Existing `POST /prescan` and `GET /status` remain compatible.

- [ ] Write tests for no runtime AST extraction, persisted cross-replica status, worker-specific minimal build, and only-through-V99 generation.
- [ ] Verify RED.
- [ ] Implement extractor, worker persistence and worker Dockerfile.
- [ ] Verify GREEN and py_compile.

### Task 3: Remote final render offload

**Files:**
- Create: `web/render_bridge.py`
- Create: `web/test_v105_render_bridge.py`
- Modify: `web/ai_worker_server.py`
- Create: `web/apply_v105_render_offload.py`
- Create: `web/test_v105_render_offload.py`

**Interfaces:**
- Worker: `POST /render`, `GET /render/status?job_id=...`.
- Web wrapper: `_gsf_v105_run_render(cmd, output_path, timeout)` returns a subprocess-compatible CompletedProcess.
- Remote worker overrides only final x264 `-threads` to 2; filter threads remain 1; CRF/preset/profile/audio contract unchanged.
- Any remote error falls back to the current local renderer.

- [ ] Write tests for placeholder staging, command validation, thread override, shared job state and fallback behavior.
- [ ] Verify RED.
- [ ] Implement render worker + web patch.
- [ ] Verify GREEN, existing render-contract tests, py_compile.

### Task 4: Social streaming / zero whole-master copies

**Files:**
- Create: `web/apply_v105_social_streaming.py`
- Create: `web/test_v105_social_streaming.py`

**Interfaces:**
- TikTok file upload reads bounded chunks from a file path.
- YouTube uses resumable MediaFileUpload/path when a path is available.
- Instagram uses signed S3 URL when master already exists in S3; temporary staging copies only as fallback.
- Legacy bytes path remains compatibility fallback, not default web path.

- [ ] Write tests that fail if normal web social path converts the whole master with `bytes(video)` or `read_bytes()`.
- [ ] Verify RED.
- [ ] Implement path/S3-first publishing.
- [ ] Verify GREEN plus V104 social tests.

### Task 5: Build reproducibility + deployment separation

**Files:**
- Modify: `requirements-web.txt`
- Create: `constraints-v105.txt`
- Modify: `Dockerfile`
- Create: `web/apply_v105_hardening.py` only if a final aggregation patch is needed.
- Modify: `web/start_web.sh`
- Create: `web/test_v105_build_contract.py`

**Interfaces:**
- Web image builds V105 candidate and runs all V104 + V105 tests.
- Worker image uses `Dockerfile.worker`.
- Staging and production support `GSF_STORAGE_PREFIX` and explicit allowed origins.
- Healthcheck `/_stcore/health`.

- [ ] Write build-contract test.
- [ ] Verify RED.
- [ ] Freeze known-good dependency versions from the built candidate and add constraints.
- [ ] Add V105 patch chain/tests and staging-safe namespace.
- [ ] Verify GREEN with Railway staging build.

### Task 6: Stress/benchmark/release gate

**Files:**
- Create: `web/v105_stress_checks.py`
- Create: `docs/v105-stress-report.md`

**Interfaces:**
- Report records build result, static tests, worker tests, HTTP health, memory/CPU metrics, render benchmark and regression gates.

- [ ] Run production-equivalent staging build.
- [ ] Run upload/API concurrency stress using synthetic files (no user content copied).
- [ ] Run synthetic 1080x1920/60 render comparison for local 1-thread vs worker 2-thread.
- [ ] Verify ffprobe master contract.
- [ ] Inspect staging Railway metrics/logs for 5xx, restarts and memory.
- [ ] Record measured results and remaining risks.
- [ ] Only after all gates: prepare production promotion; do not delete V104.7 rollback during this task.
