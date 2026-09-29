# V105 Stress / Performance / Reliability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce duplicate processing and web-memory pressure, improve upload/render throughput, and make Gaming Shorts Factory builds reproducible without changing the approved UI/player or final master-quality contract.

**Architecture:** V105 keeps Streamlit as the UI/coordinator and the existing AI worker for heavy analysis. Changes are introduced behind tests and measured in an isolated branch/staging deployment before production rollout. Rendering is optimized only after a benchmark proves both memory safety and output compatibility.

**Tech Stack:** Python 3.12, Streamlit, FFmpeg/libx264, Nginx, boto3/S3-compatible Railway Bucket, Railway services, faster-whisper.

**Spec:** `docs/superpowers/specs/2026-09-29-v105-stress-performance-design.md`

## Global Constraints

- Preserve the approved 9:16 / 16:9 player system and UI sizing.
- Preserve TikTok, YouTube and Instagram connection behavior.
- Preserve 9:16 master: 1080x1920, H.264 High/avc1, 4:2:0 8-bit compatible, <=60 fps, AAC stereo 48 kHz.
- Do not lower the current CRF14 / AAC192k quality contract without measured equal-or-better perceptual evidence.
- Production V104.7 stays rollback-capable until V105 stress verification passes.
- Avoid loading entire source videos into Python bytes.

## Review Focus

- Long video whose worker prescan takes 25–35 s must not start a duplicate local scan while the worker is healthy.
- Worker outage must still fall back locally rather than leaving the user stuck.
- iPhone/iPad multipart upload must use a bounded concurrency that does not regress desktop throughput.
- Final render optimization must not cross the 1 GB memory ceiling or alter social master compatibility.
- OAuth/session state must remain isolated across two browser sessions after performance changes.

---

### Task 1: Structured performance telemetry

**Files:**
- Create: `web/gsf_perf.py`
- Create: `web/test_v105_perf_telemetry.py`
- Modify: `web/direct_upload_server.py`
- Modify: V105 app patch script created in this task

**Interfaces:**
- Produces: `snapshot_memory() -> dict`, `perf_event(name: str, **fields) -> None`
- Consumes: Linux cgroup files when present; falls back safely elsewhere.

- [ ] **Step 1: Write the failing telemetry contract test**

Assert that memory snapshots return numeric current/limit values when cgroup fixtures are present and that events serialize without secrets.

- [ ] **Step 2: Run it and verify RED**

Run: `python web/test_v105_perf_telemetry.py`
Expected: FAIL because `web/gsf_perf.py` does not exist.

- [ ] **Step 3: Implement telemetry helper and add markers**

Instrument upload completion/materialization, worker prescan bridge, local fallback, and final render start/end. Do not add UI text.

- [ ] **Step 4: Run GREEN plus existing V104 tests**

Run: `python web/test_v105_perf_telemetry.py` and the complete existing V104 test chain.
Expected: all PASS.

- [ ] **Step 5: Commit**

Commit message: `perf: add V105 processing telemetry`

---

### Task 2: Worker-status-aware prescan deduplication

**Files:**
- Modify: `web/gsf_bucket_bridge.py`
- Create: `web/test_v105_prescan_bridge.py`

**Interfaces:**
- Consumes: `GSF_WORKER_URL`, analysis key, S3 analysis object.
- Produces: `load_prescan_from_marker(...)` with status-aware waiting and immediate error fallback.

- [ ] **Step 1: Write RED tests**

Cover:
- worker `scanning` at 8 s then result appears at 25 s → return worker scan and never request local fallback;
- worker `error` → return `None` immediately;
- worker unreachable → return `None` after bounded fallback policy;
- already-cached S3 result → immediate return.

- [ ] **Step 2: Run RED**

Run: `python web/test_v105_prescan_bridge.py`
Expected: at least the long-running healthy-worker case fails under the current blind timeout behavior.

- [ ] **Step 3: Implement status-aware polling**

Poll the S3 object and worker `/status?analysis_key=...`; healthy running states continue to configured hard cap, error returns immediately, unreachable worker preserves local fallback.

- [ ] **Step 4: Run GREEN and regression suite**

Expected: new tests PASS and V104 tests remain PASS.

- [ ] **Step 5: Commit**

Commit message: `perf: prevent duplicate worker and web prescan`

---

### Task 3: Adaptive upload and memory-bounded materialization

**Files:**
- Modify: `web/direct_upload_server.py`
- Create: `web/test_v105_upload_policy.py`
- Create/modify: V105 app patch for browser uploader policy

**Interfaces:**
- Produces: device-aware upload concurrency policy.
- Produces: configurable materialization concurrency via `GSF_MATERIALIZE_CONCURRENCY`.

- [ ] **Step 1: Write RED policy tests**

Assert:
- desktop cap = 8;
- iPhone/iPad/Android cap = 3;
- part size remains 32 MB unless capability negotiation says otherwise;
- web materialization concurrency is configurable and bounded 1–8.

- [ ] **Step 2: Run RED**

Expected: current fixed concurrency 10 / materialization 12 fails the contract.

- [ ] **Step 3: Implement adaptive policy**

Keep bucket-first upload and direct-upload fallback. Do not alter the upload-circle UI.

- [ ] **Step 4: Run GREEN and existing upload/session tests**

Expected: all PASS.

- [ ] **Step 5: Commit**

Commit message: `perf: bound mobile upload and materialization concurrency`

---

### Task 4: Reproducible and isolated AI-worker image

**Files:**
- Create: `Dockerfile.worker`
- Create: `requirements-worker.txt`
- Create: `web/test_v105_worker_image.py`
- Modify Railway worker service configuration after image tests pass.

**Interfaces:**
- Worker continues to expose `/health`, `/status`, `/prescan`.
- Worker `AI_APP_PATH` continues to point at the V99 scan implementation.

- [ ] **Step 1: Write RED image-contract test**

Assert dedicated worker image:
- installs only worker-required packages;
- contains FFmpeg and boto3;
- generates the V99 scan source;
- starts `web/ai_worker_server.py`;
- does not run Streamlit/Nginx/social patch tests.

- [ ] **Step 2: Run RED**

Expected: FAIL because `Dockerfile.worker` does not exist.

- [ ] **Step 3: Implement worker image and pin worker dependencies**

Use exact tested versions after resolving them in the staging build.

- [ ] **Step 4: Deploy branch to isolated staging worker and verify**

Verify `/health`, a real prescan, worker wall time, memory, and S3 result.

- [ ] **Step 5: Commit**

Commit message: `build: isolate V105 AI worker image`

---

### Task 5: Render benchmark gate

**Files:**
- Create: `web/v105_render_benchmark.py`
- Create: `web/test_v105_render_contract.py`
- No production render behavior change until benchmark decision.

**Interfaces:**
- Benchmark accepts source/fixture, duration and profile.
- Produces JSON containing wall time, peak memory, output bytes and ffprobe compatibility.

- [ ] **Step 1: Write RED benchmark-contract test**

Assert three profiles exist:
- `medium_crf14_t1`
- `medium_crf14_t2`
- `fast_crf14_t2`

and all enforce H.264 High, avc1, 1080x1920, <=60 fps, AAC 48 kHz stereo.

- [ ] **Step 2: Run RED**

Expected: FAIL because benchmark module does not exist.

- [ ] **Step 3: Implement benchmark harness**

Use a deterministic FFmpeg-generated gaming-like motion fixture plus an optional real uploaded test source in staging.

- [ ] **Step 4: Run benchmark in staging**

Record 15 s and 30 s results. Reject any profile with unsafe peak memory or master-contract failure.

- [ ] **Step 5: Apply only the measured winner**

If no candidate clearly wins, leave current render unchanged.

- [ ] **Step 6: Run GREEN/regression suite and commit**

Commit message: `perf: adopt measured V105 render profile`

---

### Task 6: Stress verification and rollout

**Files:**
- Create: `web/v105_stress_report.md`
- Modify only files required by findings that reproduce under tests.

**Interfaces:**
- Consumes the V105 staging deployment.
- Produces a measured go/no-go report and rollback reference.

- [ ] **Step 1: Run upload/source matrix**

Exercise 1080p30/60, 1440p60, portrait/rotation, VFR, mono/stereo/no-audio, long gameplay, and a large upload.

- [ ] **Step 2: Run failure matrix**

Exercise worker unavailable/error, upload interruption/retry, new-video reset, two concurrent browser sessions, and OAuth return paths.

- [ ] **Step 3: Compare metrics to V104.7 baseline**

Required:
- no duplicate prescan while worker healthy;
- lower heavy-path web memory;
- no master-quality regression;
- render improvement only if measured;
- no UI/player regression.

- [ ] **Step 4: Final branch review**

Review all branch changes against the spec and record any deferred minor findings.

- [ ] **Step 5: Production rollout**

Merge only after the full suite and staging stress report are green. Keep V104.7 rollback deployment identifiable.

- [ ] **Step 6: Verify production after rollout**

Check startup, upload, worker prescan, one final render and social-connect routes from production logs/metrics.
