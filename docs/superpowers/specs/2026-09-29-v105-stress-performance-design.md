# V105 Stress / Performance / Reliability Design

## Purpose

Push Gaming Shorts Factory as far as the current Railway architecture can safely go without regressing the approved UI/player system or lowering final social-video quality.

The production baseline remains V104.7. V105 work happens on an isolated branch first.

## Non-negotiable product constraints

- Do not redesign the approved player system or its 9:16 / 16:9 sizing.
- Do not change the final visual layout merely for performance.
- Preserve direct social flows for TikTok, YouTube and Instagram.
- Preserve final master compatibility: MP4, H.264 High, avc1, yuv420p-compatible, 1080x1920 for 9:16, <=60 fps, AAC stereo 48 kHz.
- Preserve final quality target around the current CRF 14 / 192 kbps AAC master unless measured evidence proves an equal-or-better perceptual result.
- Production V104.7 must remain a rollback point.

## Baseline findings

### Web service

Production service: `gaming-shorts-factory-v79`.

- CPU limit: 2 vCPU.
- Memory limit: ~1.0 GB.
- 24h average memory: ~0.40 GB.
- 24h peak memory observed: ~1.01 GB, effectively at/over the configured ceiling.
- 24h CPU peak observed: ~1.83 / 2 vCPU.
- Normal HTTP/UI endpoints are already fast (generally single-digit milliseconds).
- The bottleneck is media processing, not normal HTTP routing.

### Render

Current final master uses software x264:

- preset: medium
- CRF: 14
- threads: 1
- bounded x264 params: rc-lookahead=16, ref=2, bframes=2
- H.264 High / level 4.2
- max 60 fps
- AAC 192 kbps / 48 kHz stereo

Observed production render timings include roughly:

- ~76 s for a 15 s class final render
- ~157 s for a 30 s class final render

The one-thread limit protects the 1 GB Streamlit container but leaves a second CPU core underused during the most expensive step.

### AI worker

Service: `gsf-ai-worker`.

- 2 replicas.
- ~1 GB memory limit per replica.
- observed peak memory ~0.48 GB.
- observed peak CPU ~0.54 / 2.
- prescan jobs observed from <1 s to ~33.5 s wall time depending on source.

This service has materially more processing headroom than the web process.

### Prescan duplication

`gsf_bucket_bridge.load_prescan_from_marker` historically waits only a short fixed window (default 8 s) for the worker result. Several real worker scans take 25–33 s. When the result is not ready, the web process performs the scan again locally.

This creates avoidable duplicate CPU/memory work exactly where the web service is closest to its RAM ceiling.

Immediate production mitigation applied before V105: `GSF_PRESCAN_WAIT_SECONDS=35`.

V105 must replace blind timeout behavior with worker-status-aware fallback.

### Upload and materialization

Browser multipart upload currently uses 32 MB parts and advertises concurrency 10. On mobile Safari that can imply a large in-flight memory footprint.

After bucket upload, the web service downloads/materializes the complete source locally. One observed ~41 MB file took about 10 s to materialize, while the worker downloaded the same class of source much faster. The web materializer currently allows high multipart concurrency, which may increase RAM without a proportional speed benefit.

### Build / deploy architecture

The current image reconstructs V104.7 by starting from a compressed V77 payload and applying more than 40 sequential patch scripts.

Benefits: every historical fix remains explicit.

Costs:
- fragile text/AST patch ordering;
- large regression surface;
- harder static reasoning;
- unrelated web/social commits rebuild and restart the AI worker;
- multiple failed deployments have been caused by a later patch/test disagreeing with the accumulated generated source.

Most package requirements are lower bounds (`>=`) rather than exact tested versions, so future rebuilds are not fully reproducible.

### Duplicate service

An older `gaming-shorts-factory` V78-era service remains running in SFO with about 0.36 GB steady memory and no observed network traffic over the inspected 24h window. Treat it as a cleanup candidate only after confirming it is not intentionally retained as a backup.

## Approaches considered

### A. Tune the current monolith only

Keep rendering and analysis in Streamlit; adjust timeouts, thread counts and upload concurrency.

Pros: smallest change set.
Cons: the 1 GB web process remains the hard ceiling and prevents meaningful render parallelism.

### B. Balanced V105 architecture — selected

Keep the approved Streamlit UI, but make it a coordinator rather than the place where every heavy task runs.

- Worker result is authoritative when healthy; no duplicate local prescan.
- Upload settings become device-aware.
- Web materialization becomes memory-bounded and measured.
- Rendering is benchmarked outside Streamlit before any two-thread production change.
- Build inputs become reproducible and worker deployments become independent from social/UI-only changes.
- Add timing/memory telemetry around the heavy stages.

This gives the largest practical improvement without rewriting the product.

### C. Full application rewrite

Split the monolithic generated app into a new frontend/backend job system immediately.

Pros: cleanest long-term architecture.
Cons: highest regression risk to the UI/editor/player behavior already approved.

Not selected for V105.

## V105 architecture

### 1. Performance telemetry

Introduce structured timing markers for:

- upload complete
- source materialized
- worker prescan queued / ready / error
- local fallback scan
- candidate selection/refinement
- subtitle transcription
- final render start/end
- social publish start/end

Add lightweight process/cgroup memory snapshots around scan and render boundaries.

No user-facing diagnostics are added to the UI.

### 2. Worker-aware prescan bridge

The web bridge polls both:

- the S3 analysis object; and
- worker `/status?analysis_key=...`.

Rules:

- if worker reports `done`, allow a short S3 consistency grace period;
- if worker reports `error`, fall back locally immediately;
- if worker is healthy and still `queued/downloading/scanning`, continue waiting up to the configured hard cap;
- if worker is unavailable, retain local fallback;
- never run worker scan and local scan concurrently merely because a blind 8 s timer expired.

### 3. Adaptive upload

Desktop and mobile use different concurrency caps.

Target policy:

- desktop: up to 8 concurrent 32 MB parts;
- iPhone/iPad/Android: up to 3 concurrent parts;
- fall back to existing chunk endpoint if bucket upload is unavailable.

The objective is to avoid mobile browser memory pressure without unnecessarily slowing desktop uploads.

### 4. Memory-bounded web materialization

Make S3 materialization concurrency configurable and benchmark values 4, 6 and current 12.

Selection criterion: choose the lowest-memory value that does not materially worsen wall time.

Do not load entire source videos into Python bytes.

### 5. Render benchmark gate

Do not blindly switch production back to two x264 threads.

Build a benchmark matrix for 15 s and 30 s 1080x1920 output using:

- current: medium / CRF14 / 1 thread;
- candidate: medium / CRF14 / 2 threads;
- candidate: fast / CRF14 / 2 threads.

Measure:

- render wall time;
- peak cgroup memory;
- output size;
- ffprobe compatibility;
- frame count/fps;
- SSIM when practical against the same processed frames.

A faster profile can ship only if it stays comfortably below the memory ceiling and preserves the master-quality contract.

### 6. Build reproducibility

- Capture the effective V104.7 dependency versions and pin them in a lock/constraints file.
- Stop treating `>=` as the production dependency contract.
- Introduce a dedicated worker Dockerfile so UI/social-only patches do not rebuild/restart `gsf-ai-worker`.
- Longer term, create a canonical generated baseline checkpoint so future versions do not need the full V77→V104 patch chain every build.

The canonical checkpoint must be generated from the tested patch chain, not manually reconstructed.

### 7. Stress matrix

V105 verification must cover:

- 15 s and 30 s final shorts;
- 1080p30, 1080p60, 1440p60;
- portrait/rotated iPhone sources;
- variable-frame-rate input;
- 44.1 kHz / 48 kHz audio;
- mono and stereo;
- source without audio;
- large upload;
- long gameplay where worker scan exceeds 8 s;
- worker unavailable / worker error;
- two browser sessions to verify state isolation;
- TikTok, YouTube and Instagram connection state surviving tab/OAuth flow;
- repeated new-video/reset cycles.

## Success criteria

V105 is considered better only if all of the following hold:

1. No regression in the approved UI/player layout.
2. Final master compatibility tests remain green.
3. Worker prescan is not redundantly repeated on the web when the worker is healthy.
4. Web memory stays materially below the 1 GB ceiling in the tested heavy path.
5. Final render is faster than the current baseline or, if unchanged, the web memory/stability improvement is significant.
6. Mobile upload remains stable under the adaptive concurrency policy.
7. Existing V104 social and render regression tests remain green.
8. Production rollout remains reversible to V104.7.
