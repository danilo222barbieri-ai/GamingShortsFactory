# V401 Performance & Stability Design

## Goal
Reduce frontend memory pressure and make AI prescan jobs observable and recoverable across worker sleep/redeploy, without changing approved UI, V400 render quality, or the stable Editor component identity.

## Architecture
- Keep the existing browser-to-S3/direct-upload path and V293 materialization guard.
- Remove fallback Streamlit full-buffer duplication by streaming UploadedFile data to disk in bounded chunks while restoring the original cursor.
- Persist worker job state as small JSON objects in the existing S3-compatible bucket; RAM remains the fast live cache.
- Keep the current worker semaphore as the queue/concurrency primitive; no Redis, database, or Railway volume is introduced.
- If a worker restarts while a persisted active state exists and the analysis object is not complete, expose the job as interrupted/retryable instead of pretending it is still running.
- Treat `semantic` as an active state, so duplicate requests cannot start a second prescan while semantic analysis is in progress.
- Attach monotonic phase progress metadata to queued/downloading/scanning/semantic/done states.

## Constraints
- Production baseline remains V400 commit `6792749447b24c590f350036501235891fae91da` until V401 passes branch tests, Production Gate, and Railway health checks.
- Do not change Home, Game Bar, Creator Hub, Game Editor layout, or Streamlit component identity `gsf_editor_2027_v1086`.
- Do not change V400/V399 encoding policy: 1080x1920 master, libx264, preset medium, existing adaptive quality bounds.
- Do not add Redis, a database, or a Railway persistent volume.
- Job-state persistence failure must never make video analysis fail; it is observability/recovery metadata only.
- Runtime patching must be idempotent.

## Acceptance
1. Fallback uploaded-video copies no longer call `video.getvalue()` for the main probe/editor materialization paths.
2. Streaming copy uses bounded chunks and restores the UploadedFile cursor.
3. Worker states are persisted in the bucket under a V401 job-state namespace.
4. Persisted active jobs recover as interrupted/retryable after restart unless the analysis artifact already exists.
5. `semantic` is included in active duplicate suppression.
6. Status responses include stable progress metadata.
7. V400 quality/Hi-DPI and editor regression tests remain green.
