# Gaming Shorts Factory V105 Hardening — Design

## Intent

V105 is a stability/performance/quality hardening release for the existing Gaming Shorts Factory web beta. It must improve measurable speed and reliability without changing the approved UI/player layout or reducing final social-master quality.

The production V104.7 deployment remains the fallback while V105 is developed and tested on the isolated `v105-hardening` branch.

## Measured baseline

Production observations gathered on 29 September 2026:

- Current web service: `gaming-shorts-factory-v79`, 1 replica, 2 vCPU limit, ~1 GB RAM limit, Europe.
- Web memory reached ~1.01 GB in the last 24 h and an aggregated ~1.36 GB peak in the 7-day metrics. Railway reports no `CRASHED` deployments, so this is treated as severe memory pressure rather than a proven OOM event.
- HTTP logs contain a cluster of 502 `connection reset/refused` responses around 28 September 19:02 UTC, proving at least one period of process unavailability.
- A measured 9:16 final render completed successfully in 157.22 s with `libx264 HQ`.
- Final render currently uses H.264 High, CRF 14, preset medium, 1080×1920, max 60 fps, AAC 192 kbps / 48 kHz / stereo. V105 must not weaken this quality contract without benchmark evidence.
- Upload already goes browser → S3, but the web service then materializes the full source locally while the AI worker downloads another copy. A measured 41,179,249-byte source took roughly 10 s to materialize on web, while the worker completed its prescan in 4.36 s.
- AI worker has 2 replicas and materially more headroom than the web process; recent 24 h peak was ~0.48 GB RAM and ~0.54 CPU against 2 vCPU.
- Social publish still copies large video payloads into Python `bytes`, increasing peak RAM.
- The Docker build reconstructs the app by applying 58 sequential patch scripts from V78 through V104.7 after unpacking the V77 source. This is fragile and increases regression/build-failure surface.
- Runtime dependencies other than Streamlit are specified with `>=`, making future builds non-reproducible.
- A legacy V78 Railway web service is still running. Its last observed HTTP traffic was 27 September 2026 18:54 UTC and it currently consumes ~0.36 GB memory while idle.

## Non-negotiable constraints

- Preserve the approved player system and approved player dimensions.
- Preserve existing V104.7 TikTok/YouTube/Instagram connection behavior while hardening it.
- Do not regress iPhone/iPad upload, preview, download, or session recovery.
- Keep 15 s / 30 s behavior and current AI mode semantics.
- Do not reduce final output below 1080×1920 for 9:16 or 1920×1080 for 16:9.
- Keep H.264/AAC social compatibility and post-render validation.
- Every production behavior change requires a regression test.
- V104.7 stays deployable as rollback until V105 passes stress verification.

## Architecture

### 1. Keep Streamlit as orchestration/UI, not as the heavy media engine

The web process should own UI state, lightweight metadata, routing, and job orchestration. It should stop retaining full final videos in Python `bytes` and stop performing the heaviest long-running encoding work when a worker can do it more safely.

### 2. File/S3 references become the source of truth

Introduce a small media-reference abstraction representing either:
- a local session path (compatibility/fallback), or
- an S3 bucket/key plus metadata.

Consumers should request a path/stream/presigned URL only when needed. Social publishing and worker jobs should stream from file/S3 rather than materialize duplicate full byte arrays.

### 3. Offload final rendering from Streamlit

Extend the worker protocol with a final-render job:
- input: source S3 key, selected segment, editor/render recipe, format, subtitle/reframe data;
- processing: one bounded render per worker replica, with analysis and render sharing a global heavy-job semaphore;
- output: validated MP4 written to S3;
- status: queued/running/progress/done/error persisted in shared storage, not only worker-process RAM, because the worker currently has 2 replicas;
- web: poll and display progress without holding FFmpeg memory.

The worker has two replicas, so this uses existing capacity while isolating the web UI from render pressure.

### 4. Keep visual quality measurable

V105 initially preserves CRF 14 / H.264 High / AAC 192k. Encoder changes are allowed only after A/B benchmarking on representative source material.

Benchmark candidates:
- current: medium / CRF14 / 1 thread;
- isolated worker: medium / CRF14 / 2 threads with bounded lookahead;
- optional speed candidate: fast / CRF14 with the same output validation.

Compare wall time, peak RAM, output size and objective metrics available in FFmpeg (SSIM/PSNR; VMAF only if available). Never select a faster profile merely because it is faster.

### 5. Upload path

Keep direct browser → S3 multipart upload. Reduce duplicate server work:
- prescan starts immediately after multipart completion;
- upload state distinguishes `uploaded_to_s3` from `local_materialized`; the UI must not wait for a full S3→web download just to declare the upload usable;
- source materialization on web becomes lazy/compatibility-only instead of the gate for every AI workflow;
- browser preview should prefer an authenticated app endpoint that issues a short-lived signed S3 GET/redirect, preserving session isolation without proxying the video bytes through Python;
- local materialization remains for editor paths that still require local FFmpeg access until those paths are migrated.

Review both browser and server concurrency instead of assuming more lanes are faster:
- current browser multipart configuration can request 10 concurrent 32 MB parts, which is aggressive for iPhone/Safari and weaker uplinks;
- current web materialization uses 12 concurrent transfer workers on a 1 GB service.

V105 should benchmark adaptive bounded concurrency (mobile vs desktop/network conditions) and cap in-flight work to avoid memory/network contention.

### 6. Social publishing

All three platforms should publish from a path/stream/S3 reference:
- TikTok chunk upload reads bounded chunks from file instead of slicing a giant Python bytes object.
- YouTube uploader receives a file path / resumable file object.
- Instagram uses a short-lived signed S3 GET URL directly, avoiding re-uploading the same master from Python memory when Meta can fetch it itself.

OAuth tokens remain persisted per anonymous browser session using the existing persistent bucket bridge.

### 7. Session and temporary-file lifecycle

Keep the current anonymous browser session recovery, but add explicit lifecycle checks:
- stale local sessions are removed after TTL;
- abandoned multipart uploads are aborted/cleaned where feasible;
- temporary render/staging files are deleted after success or failure;
- recovered-upload compatibility paths must not call whole-file `getvalue()`/`read_bytes()` on large sources during normal web workflows;
- active session files are never removed while a job is running;
- new-video reset clears transient media state without breaking social connections.

### 8. Build reproducibility and source consolidation

Two steps, not one risky rewrite:
1. Freeze the exact dependency versions proven by the V105 test suite.
2. Generate a canonical V105 application source as a build artifact/checkpoint so production no longer depends indefinitely on replaying 40+ historical text patches.

Historical patch scripts remain in git for traceability, but the production Docker build should eventually start from the canonical checkpoint plus only current-version patches.

### 9. Deployment and process health

V105 must stop using production `main` as the first place where a risky change is exercised. Use an isolated branch and a staging deployment/service for smoke and stress testing before merging production changes. The existing legacy V78 service may be repurposed as a staging shell only after its domain/config dependencies are verified; otherwise disable it and create a dedicated staging target.

Split worker build concerns from the full web image. The current worker service rebuilds/restarts on many commits that only affect later UI/social patches because both services share the same Dockerfile/repo trigger.

V105 should:
- add a worker-specific build path/image that contains only worker dependencies and the AI code it actually consumes;
- add Railway watch patterns so unrelated documentation/UI/social changes do not redeploy the worker;
- add an explicit web healthcheck that only turns a deployment healthy once the Streamlit route is reachable;
- use a clear restart policy for unexpected process exits;
- keep one web replica until session/media state is sufficiently S3-native for safe horizontal scaling.

### 10. Observability

Add structured one-line diagnostics for:
- upload init/complete/materialize;
- worker prescan;
- render queued/start/finish/fail;
- source/output bytes;
- duration/fps/resolution;
- wall time;
- process RSS before/after heavy operations when available;
- social publish start/finish/error.

Never log secrets, OAuth tokens, signed URLs, or raw user content.

## Stress verification

A V105 candidate is not releasable until it passes:

1. Upload: small, 500 MB-class synthetic/representative, interrupted/retried multipart, iPhone Safari path.
2. AI: 15 s, 30 s, several-minute gameplay, long gameplay; all four AI modes.
3. Render: 9:16 and 16:9; 30/60 fps; rotated iPhone input; subtitle/no-subtitle; editor transformations.
4. Memory: repeated upload → AI → render → new-video cycles with no monotonic RSS growth.
5. Session: refresh/reconnect, OAuth new tab, return to prepared video, new video reset.
6. Social: connected/unconnected, token refresh, provider cancel/error, publish success without resetting Streamlit state.
7. Compatibility: ffprobe gate confirms H.264/avc1/yuv420p-compatible, expected dimensions, <=60 fps, AAC 48 kHz stereo.
8. Deployment: a UI/social-only commit must not unnecessarily rebuild/restart the AI worker.
9. Regression: all existing V104.3–V104.7 tests remain green.

## Release gates

V105 can replace V104.7 only when:
- the candidate has passed a production-equivalent staging deployment;
- no Critical/Important regression remains;
- production-equivalent build passes;
- stress suite passes;
- render benchmark shows no quality regression;
- web memory headroom improves materially under the same workload;
- social flow still preserves the prepared video/session.

The old V78 Railway service may be disabled only after confirming no DNS/OAuth/provider callback depends on its domain. Its current domain is different from the V104.7 production domain, but this must be checked before removal.
