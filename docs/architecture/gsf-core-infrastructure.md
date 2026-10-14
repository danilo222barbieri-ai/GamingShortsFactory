# GSF Core Infrastructure V406

## Purpose

This slice moves expensive media handling away from Streamlit state and defines
durable contracts shared by the frontend, AI workers and render workers. It is
designed to integrate with GSF Alive Core rather than duplicate its global
application/project state.

## Rules

1. Project/session state stores `AssetRef` metadata only. Raw video/audio bytes
   do not belong in Streamlit session state.
2. Browser uploads can go directly to S3-compatible object storage using a
   presigned POST. The frontend receives a lightweight asset reference.
3. A direct upload is not trusted until `confirm_upload()` verifies the object
   exists and respects the configured size limit.
4. Heavy work is represented by `JobRecord` and follows:
   `queued -> running -> completed|failed|cancelled`.
5. Retries are explicit and bounded by `max_attempts`.
6. Running jobs heartbeat with progress/phase metadata; a heartbeat cannot be
   written by a different worker.
7. Expensive analysis is keyed by deterministic cache identities so changes to
   unrelated editor settings do not rerun Whisper/Game Vision.
8. Editor proxies have an explicit profile and are cacheable artifacts.
9. Phase timing and cost accounting are first-class data, not log text.

## Modules

- `assets.py`: immutable references to source/proxy/audio/analysis/render assets.
- `storage.py`: streaming local storage plus S3-compatible presigned direct upload.
- `jobs.py`: job lifecycle and an atomic JSON persistence adapter.
- `cache.py`: deterministic artifact cache identities and editor proxy profile.
- `telemetry.py`: phase timings and CPU/GPU/egress cost model.

## Production persistence boundary

`JsonJobStore` is intentionally safe for development or a single durable host,
but it is **not** a distributed scheduler and must not be treated as one on
ephemeral Railway containers.

The production scheduler/store should be an external durable service
(Redis/Postgres/SQS or equivalent). That backend should implement the same
`JobRecord` contract, so the UI and workers do not change when the backend is
introduced.

Object media should live in S3/R2-compatible storage. This avoids routing
multi-GB uploads through the 1 GB Streamlit frontend and makes uploads
retryable at the storage boundary.

## Integration with GSF Alive Core

Alive Core owns application/project state and the Streamlit bridge. It should
store `AssetRef.to_dict()` values and job IDs, not file bytes. The integration
sequence is:

1. create project in Alive Core;
2. request `S3Storage.create_presigned_upload()`;
3. browser uploads directly to object storage;
4. call `confirm_upload()` and attach the confirmed `AssetRef` to the project;
5. create queued jobs by reference;
6. worker resolves assets only while executing the job;
7. cache reusable outputs (proxy, transcript, detections, thumbnails);
8. persist render output as another `AssetRef`.

## Proxy baseline

The default editor proxy is capped at 720p / 30 fps with H.264 + AAC and CRF 24.
It exists only for responsive editing; final rendering continues to use the
original source asset.

## What this slice deliberately does not do

- It does not edit `app.py` while Alive Core owns that file.
- It does not pretend the local JSON store is a production distributed queue.
- It does not change the current final FFmpeg quality baseline.
- It does not add new infrastructure dependencies.

Those integrations can be layered on top after the active Alive Core claim is
merged/released.
