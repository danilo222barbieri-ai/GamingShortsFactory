# V397 Phase 1 Production Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the current V396 production app so a release is accepted only when nginx, Streamlit, companion APIs, current mobile contracts, upload/storage and the release smoke are all healthy, without changing approved UI or product behavior.

**Architecture:** Keep the existing single frontend Railway service and AI worker. Add one composite health contract through the existing companion server and nginx, convert the runtime smoke into a blocking release gate, normalize one expected Editor empty state, remove redundant Creator Hub state reads, and gate `main` with a current production workflow before changing Railway health behavior.

**Tech Stack:** Python 3.12, Streamlit, nginx, GitHub Actions, Docker/Railpack, Railway, boto3/S3-compatible storage, existing GSF static/runtime tests.

**Spec:** `docs/superpowers/specs/2026-10-13-v397-structural-hardening.md`

## Global Constraints

- Baseline is production commit `3668f951e08adc4723afb9931d5a683d454da349` (V396).
- No Home, Creator Hub, AI, Game Editor, Share, header, Game Bar or footer redesign in Phase 1.
- Preserve the current V396 Editor composition and publish surface.
- Preserve 9:16-only final workflow and current render-quality settings.
- Preserve direct upload, S3 multipart, fallback upload, durable drafts/projects/finals and current routes.
- Do not weaken an existing V343 or V389-V396 contract to make V397 pass.
- Work on `v397-structural-hardening`; do not promote until the full release gate passes.

## Review Focus

- Slow Streamlit startup: `/healthz` must return 503 until Streamlit is reachable, then recover without restart.
- Companion failure with nginx still alive: `/healthz` must fail instead of serving a false-positive root health.
- Editor opened before any video exists: media lookup must report an expected not-ready state without a 4xx, while invalid session remains an error.
- Creator Hub with missing/unconfigured social connections: state must remain valid and each provider loader must run at most once per request.
- CI container with no production bucket credentials: smoke must explicitly skip S3-only verification while still requiring local upload/media/range tests.

---

### Task 1: Lock the V397 structural contract before implementation

**Files:**
- Create: `web/test_v397_production_hardening.py`
- Read-only reference: `web/start_web.sh`
- Read-only reference: `web/nginx.conf.template`
- Read-only reference: `web/direct_upload_server.py`
- Read-only reference: `.github/workflows/v397-production-gate.yml` after Task 5

**Interfaces:**
- Consumes: current V396 source tree.
- Produces: one static contract test that later tasks must satisfy without touching visual contracts.

- [ ] **Step 1: Write the failing structural test**

The test must assert all of the following exact release properties:

```python
assert 'location = /healthz' in nginx
assert 'def _composite_health' in companion
assert '"/healthz"' in companion
assert 'runtime_smoke_v107.py &' not in start_web
assert 'GSF_EDITOR_MEDIA_NOT_READY' in companion
assert 'def _creator_social_snapshot' in companion
```

It must also assert that startup still references the V343 shell contract and the V389/V390/V391/V392/V393/V394/V395/V396 continuation chain until Phase 2 canonicalization begins.

- [ ] **Step 2: Run the test and verify RED**

Run: `python web/test_v397_production_hardening.py .`

Expected: FAIL because `/healthz`, the new helper functions and blocking-smoke startup contract do not exist yet.

- [ ] **Step 3: Commit the RED test only**

Commit message: `test: define V397 production hardening contract`

---

### Task 2: Add composite production health

**Files:**
- Modify: `web/direct_upload_server.py`
- Modify: `web/nginx.conf.template`
- Modify: `web/runtime_smoke_v107.py`
- Test: `web/test_v397_production_hardening.py`

**Interfaces:**
- Consumes: companion server on `GSF_DIRECT_UPLOAD_PORT` and Streamlit on `127.0.0.1:8501`.
- Produces: `_composite_health(timeout: float = 1.5) -> dict` and public nginx route `GET /healthz`.

- [ ] **Step 1: Add failing health behavior tests**

Extend `web/test_v397_production_hardening.py` to require:

```python
assert 'streamlit' in companion_health_source
assert 'companion' in companion_health_source
assert '503' in companion_health_source
```

Extend `web/runtime_smoke_v107.py` so the running production image requires `GET /healthz` to return JSON with `ok == true`, `companion == true`, and `streamlit == true`.

- [ ] **Step 2: Verify RED**

Run: `python web/test_v397_production_hardening.py .`

Expected: FAIL on missing composite health implementation.

- [ ] **Step 3: Implement `_composite_health(timeout: float = 1.5) -> dict`**

In `web/direct_upload_server.py`, probe `http://127.0.0.1:8501/_stcore/health` with the standard library, treat only HTTP 200 as Streamlit-ready, and return a dictionary containing at least `ok`, `companion`, `streamlit`, `bucket`, and `worker`. Do not make bucket/worker configuration mandatory for frontend health.

Route `GET /healthz` through the existing Handler. Return HTTP 200 only when `ok` is true; otherwise 503.

- [ ] **Step 4: Expose nginx `/healthz`**

Add `location = /healthz` in `web/nginx.conf.template` that proxies to `http://127.0.0.1:8502/healthz`, disables buffering, and returns `Cache-Control: no-store`.

- [ ] **Step 5: Run static and runtime-targeted tests**

Run:

```bash
python web/test_v397_production_hardening.py .
python -m py_compile web/direct_upload_server.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

Commit message: `feat: add composite frontend health check`

---

### Task 3: Normalize the expected empty Editor-media state

**Files:**
- Modify: `web/direct_upload_server.py`
- Modify: `web/runtime_smoke_v107.py`
- Test: `web/test_v397_production_hardening.py`

**Interfaces:**
- Consumes: `_editor_media_current(handler, sid)` and existing `/editor-media/current` nginx proxy.
- Produces: valid-session empty state `HTTP 204` with marker log `GSF_EDITOR_MEDIA_NOT_READY`; invalid session behavior remains `HTTP 400`.

- [ ] **Step 1: Write the failing source contract**

Require the Editor-media missing branch to contain `GSF_EDITOR_MEDIA_NOT_READY` and to send 204 rather than 404 for a valid session with no current source.

- [ ] **Step 2: Verify RED**

Run: `python web/test_v397_production_hardening.py .`

Expected: FAIL because current missing media returns 404.

- [ ] **Step 3: Implement the minimal semantic change**

In `_editor_media_current`, preserve the existing 302 redirect when media exists and the existing 400 for invalid session. Replace only the final valid-session missing-media 404 branch with a 204 no-content response and `GSF_EDITOR_MEDIA_NOT_READY` log marker.

- [ ] **Step 4: Add runtime smoke coverage**

Before the smoke test uploads its synthetic video, request `/editor-media/current` and require HTTP 204. After upload/materialization, preserve existing media roundtrip/range coverage.

- [ ] **Step 5: Verify**

Run:

```bash
python web/test_v397_production_hardening.py .
python -m py_compile web/direct_upload_server.py web/runtime_smoke_v107.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

Commit message: `fix: treat empty editor media as expected state`

---

### Task 4: Make Creator Hub social state single-read per request

**Files:**
- Modify: `web/direct_upload_server.py`
- Test: `web/test_v397_production_hardening.py`

**Interfaces:**
- Consumes: `_youtube_user_load(sid)`, `_tiktok_user_load(sid)`, `_instagram_user_load(sid)`, Creator profile `providers`.
- Produces: `_creator_social_snapshot(sid: str, providers: dict | None = None) -> dict[str, bool]` returning booleans for `youtube`, `tiktok`, `instagram`, `facebook`, `twitch`.

- [ ] **Step 1: Write failing unit/source coverage**

The test must require one helper definition and require `/creator-hub/state` to obtain its `social` response and `stats.social` count from the same `social_snapshot` variable, rather than calling provider loaders twice.

- [ ] **Step 2: Verify RED**

Run: `python web/test_v397_production_hardening.py .`

Expected: FAIL on missing helper/reuse.

- [ ] **Step 3: Implement `_creator_social_snapshot`**

Load each provider connection once, return booleans only, and accept an already-loaded Creator `providers` mapping for Facebook/Twitch.

- [ ] **Step 4: Use the snapshot in `/creator-hub/state`**

Build the JSON `social` property from the helper and calculate `stats.social` with `sum(1 for connected in social_snapshot.values() if connected)`. Do not change response field names or limits/draft/short behavior.

- [ ] **Step 5: Verify**

Run:

```bash
python web/test_v397_production_hardening.py .
python -m py_compile web/direct_upload_server.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

Commit message: `perf: reuse creator social state per request`

---

### Task 5: Replace detached runtime smoke with one blocking production gate

**Files:**
- Modify: `web/start_web.sh`
- Create: `.github/workflows/v397-production-gate.yml`
- Modify: `web/runtime_smoke_v107.py`
- Test: `web/test_v397_production_hardening.py`

**Interfaces:**
- Consumes: production Dockerfile, V343 shell tests, V389-V396 component tests, V397 static contract, runtime smoke.
- Produces: one GitHub Actions required-style gate for pushes/PRs to `main` and `v397-structural-hardening`.

- [ ] **Step 1: Extend RED contract for release gate**

Require workflow text to contain triggers for `main` and `v397-structural-hardening`, build `Dockerfile`, start one container, wait on `/healthz`, execute `runtime_smoke_v107.py` synchronously, and dump container logs on failure.

- [ ] **Step 2: Remove detached smoke from startup**

Delete only `python /app/web/runtime_smoke_v107.py &` from `web/start_web.sh`. Do not alter nginx, companion/contact startup order or Streamlit foreground ownership in this phase.

- [ ] **Step 3: Create `.github/workflows/v397-production-gate.yml`**

The workflow must:

1. checkout source;
2. run `python web/test_v397_production_hardening.py .`;
3. build the production Docker image;
4. run current V343 and V389-V396 contracts against the built/current source where their existing invocation requires it;
5. start the image at host port 18080;
6. wait until mobile `GET /healthz` returns 200;
7. execute `/app/web/runtime_smoke_v107.py` inside the running container synchronously;
8. fail the job on any non-zero smoke exit;
9. print container logs on failure.

Do not require production S3 secrets in CI; the existing smoke must keep its explicit bucket-configured conditional.

- [ ] **Step 4: Verify locally/static**

Run:

```bash
python web/test_v397_production_hardening.py .
python -m py_compile web/runtime_smoke_v107.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `ci: add blocking V397 production release gate`

---

### Task 6: Run the complete branch verification before any Railway configuration change

**Files:**
- No new source files unless a failing test reveals a defect.

**Interfaces:**
- Consumes: Tasks 1-5.
- Produces: a green branch suitable for one production deployment.

- [ ] **Step 1: Run static contracts**

Run the V397 contract plus current V343 and V389-V396 tests exactly as wired by the repository's current production path.

Expected: all PASS; no test is deleted or weakened.

- [ ] **Step 2: Build the production image from a clean checkout**

Run: `docker build --progress=plain -t gsf-v397-phase1 .`

Expected: exit 0.

- [ ] **Step 3: Start the image and wait on `/healthz`**

Run the image with `PORT=8080`, poll `/healthz` with the mobile user agent until HTTP 200.

Expected JSON: `ok=true`, `companion=true`, `streamlit=true`.

- [ ] **Step 4: Execute blocking runtime smoke**

Run inside the container: `python /app/web/runtime_smoke_v107.py`

Expected final line: `V107 runtime smoke: PASS`.

- [ ] **Step 5: Verify current user surfaces remain present**

HTTP-check mobile `/`, `/editor-live/`, `/ai-v221/`, `/creator-hub-v156/`, `/share-v156/` and desktop gate behavior. No visual source files may differ except changes explicitly required by this plan.

- [ ] **Step 6: Commit any verification-only adjustment separately**

Only if necessary. Commit message must describe the concrete defect repaired; do not add a generic V397 patch layer.

---

### Task 7: Promote once and verify Railway with the new health contract

**Files:**
- No repository source change expected.
- Railway frontend service configuration: healthcheck path only after branch CI is green.

**Interfaces:**
- Consumes: fully green `v397-structural-hardening` branch and production gate.
- Produces: one production deployment whose health is based on `/healthz`.

- [ ] **Step 1: Merge/promote the complete Phase 1 change as one reviewed unit**

Do not drip individual RED/GREEN commits into production. `main` should receive the coherent tested Phase 1 state.

- [ ] **Step 2: Change Railway frontend healthcheck path from `/` to `/healthz`**

Keep healthcheck timeout at 180 seconds unless startup evidence shows it needs adjustment.

- [ ] **Step 3: Wait for Railway deployment `SUCCESS`**

Do not declare completion while status is building/deploying.

- [ ] **Step 4: Inspect post-deploy logs**

Require startup success, no V397/V396 contract failure, no repeated 5xx, and no detached smoke process failure.

- [ ] **Step 5: Run live HTTP verification**

Confirm `/healthz` is 200, mobile root works, expected Editor no-media state is non-4xx, Creator Hub state is 200, and current internal surfaces are reachable with mobile user agent.

- [ ] **Step 6: Record the production commit and deployment ID in the final report**

The report must distinguish automated verification from any UI geometry that still needs a physical iPhone screenshot check.

---

## Self-review result

- Spec coverage: Phase 1 health, CI, smoke, Editor empty state and Hub duplicate-read findings are all owned by tasks above. Patch-chain canonicalization, AI circuit breaker/shared scan module and backend modularization are deliberately deferred to their own Phase 2-4 plans.
- Type consistency: `_composite_health(timeout: float = 1.5) -> dict` and `_creator_social_snapshot(sid: str, providers: dict | None = None) -> dict[str, bool]` are defined once and consumed consistently.
- Existing behavior: no task changes V396 UI, routing, rendering, upload policy, persistent storage model or social provider capabilities.
- Rollback safety: Railway health path is changed only after the branch has proven `/healthz` inside a clean production image.
