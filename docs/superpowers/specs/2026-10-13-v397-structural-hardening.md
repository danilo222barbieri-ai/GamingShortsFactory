# Gaming Shorts Factory — V397 Structural Hardening

Date: 2026-10-13
Status: approved strategy; implementation staged
Baseline: production commit `3668f951e08adc4723afb9931d5a683d454da349` (V396)

## Goal

Make the current V396 product substantially harder to break without redesigning it. The visible and functional baseline remains the approved mobile application; V397 is an architectural consolidation and reliability release, not a UI redesign.

## Non-negotiable baseline

The following behavior must remain unchanged unless a later, separately approved product change explicitly says otherwise:

- mobile-first GSF experience and current visual language;
- Home layout and upload interaction;
- one global parent-owned header, Game Bar and footer;
- current Creator Hub information architecture and routes;
- current AI surface and candidate flow;
- current Game Editor composition, controls, fullscreen behavior and V396 publish entry;
- 9:16-only final workflow;
- direct upload with S3 multipart when configured and local fallback when needed;
- durable drafts, projects and final Short recovery;
- render output contract: 1080x1920, H.264/libx264, AAC, current quality settings;
- current Share/download flow and social connection surfaces.

No phase may trade away a working user path merely to simplify the code.

## Findings this spec addresses

### 1. Runtime patch-chain fragility

The production image is assembled from a historical generated app and a long build-time migration chain. Startup then applies a second migration chain, including component rewrites. Many recent regressions were caused by old and new owners modifying the same source or by string anchors disappearing.

### 2. Health checks do not cover all required processes

Streamlit is the foreground process while direct-upload, contact and nginx are sibling processes. A healthy root page does not prove that upload/state APIs are healthy. The current runtime smoke is useful but runs asynchronously and cannot reliably reject a bad release.

### 3. CI is fragmented across historical branches

Important contracts exist, but several workflows only run on historical feature branches or manual dispatch. Production deploys from `main` without a single current release gate covering the modern app.

### 4. Expected states pollute operational error signals

`/editor-media/current` may return a 404 before a source is loaded. This is an expected state, not a missing route, and should not appear operationally identical to a real 404.

### 5. Creator Hub state work is repeated

The state endpoint loads social connection state multiple times in the same request. The endpoint should reuse request-scope values and avoid redundant storage/network reads.

### 6. Cloud semantic AI is not dependable enough to be on the critical path

The AI worker already has a local fallback, but Gemini 429/503 responses occur repeatedly. Cloud semantic calls need a failure circuit so repeated provider failures do not add latency or cost to every video.

### 7. Worker scan logic is extracted from generated app source at runtime

The worker currently parses the generated app AST to recover scan functions. This couples worker correctness to generated app structure and should be replaced by a shared importable module.

### 8. Companion backend has too many responsibilities in one file

`web/direct_upload_server.py` owns upload, storage, Editor state, drafts, Creator Hub, account, social, Share, notifications, Guardian and analytics. The service can remain one process, but responsibilities need module boundaries.

## Strategy

Use progressive canonicalization rather than a rewrite.

### Phase 1 — Production hardening

Ship independently, with no intended visual change.

1. Add a composite internal health endpoint that proves nginx can reach Streamlit and the companion server and that the companion server reports its critical dependencies.
2. Change Railway frontend healthcheck from `/` to the composite endpoint.
3. Make production release smoke blocking in CI instead of a detached runtime background process.
4. Add one current production workflow on `main` covering modern static contracts, image build and HTTP smoke.
5. Normalize expected empty Editor-media state to a non-error response.
6. Remove redundant Creator Hub state reads within a request.
7. Preserve every V396 visual and routing contract.

### Phase 2 — Canonical runtime baseline

Create a canonical source snapshot of the generated V396 runtime and component artifacts, then make fresh containers start from that baseline instead of replaying the historical startup migration chain. Keep legacy migration scripts in repository history for traceability, but do not execute them in normal startup once the canonical baseline is verified.

The first target is the startup chain. Build-time historical migration removal happens only after a byte/contract-equivalent canonical artifact can be reproduced in CI.

### Phase 3 — AI resilience

1. Add a provider circuit breaker for Gemini 429/503 responses with cooldown and local-first fallback.
2. Export gameplay scan functions to `web/gsf_core/game_scan.py` and import them from both generated/runtime app adapters and the AI worker.
3. Add structured per-job diagnostics for local scan, cloud semantic attempt, fallback reason and elapsed time.

### Phase 4 — Backend modularization and scale readiness

Split the companion implementation into focused modules while keeping one Railway process and stable URLs. Candidate boundaries:

- `web/gsf_backend/storage.py`
- `web/gsf_backend/session.py`
- `web/gsf_backend/upload.py`
- `web/gsf_backend/editor.py`
- `web/gsf_backend/projects.py`
- `web/gsf_backend/share.py`
- `web/gsf_backend/social.py`
- `web/gsf_backend/health.py`

Do not add Redis or multiple frontend replicas until transient `/tmp` state has either been removed from request correctness or given a shared durable owner.

## Phase 1 success criteria

A release is accepted only when all are true:

- production image builds from a clean checkout;
- Python compile and current V343/V389-V396 contracts pass;
- mobile root serves the app and desktop gate behavior is unchanged;
- direct upload fallback roundtrip and byte-range test pass;
- S3 multipart init/abort passes when bucket credentials are configured;
- composite health fails if Streamlit or companion health fails;
- `/editor-media/current` empty state is non-4xx and explicitly reports not ready;
- Creator Hub state performs each social-state load at most once per request;
- Home, Hub, AI, Editor and Share routes remain present and unchanged in ownership;
- current V396 Editor and publish contracts remain green;
- Railway deployment reaches `SUCCESS` with the new health endpoint;
- no new 5xx appears in post-deploy smoke.

## Rollout rule

No speculative production patch chain. Work on `v397-structural-hardening`; each task is test-first. Promote only after the full Phase 1 release gate passes. If a task cannot preserve the V396 contract, stop and repair the task rather than weakening the contract.

## Explicit non-goals for Phase 1

- no redesign;
- no new AI engine;
- no social-provider feature expansion;
- no render-quality change;
- no multi-replica frontend;
- no database migration;
- no removal of historical source files merely for repository cleanliness.
