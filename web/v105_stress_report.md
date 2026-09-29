# V105 Stress / Performance / Reliability Report

Date: 2026-09-29

## Result

**GO for web V105 rollout**, with one deferred infrastructure item: the dedicated worker image is implemented and statically verified, but a separate worker staging service could not be provisioned because the Railway account/project hit its resource provision limit.

The approved UI/player system was not redesigned.

## Production-safe changes

- Structured cgroup memory/timing telemetry around heavy stages.
- Worker-status-aware prescan bridge.
- Production prescan soft wait increased from the historical 8 seconds to 35 seconds.
- Desktop multipart upload concurrency capped at 8.
- Mobile (iPhone/iPad/Android) multipart concurrency capped at 3.
- S3 source materialization concurrency made configurable, default 6 and bounded 1..8.
- Python dependencies pinned to the exact tested environment.
- Silent AAC 48 kHz stereo fallback for sources with no audio stream.
- Existing TikTok, YouTube and Instagram Social Connect regression tests preserved.

## Render decision

Three candidates were measured with the same CRF14 master contract.

### 15 second fixture

| Profile | Time | Peak memory | SSIM vs baseline |
|---|---:|---:|---:|
| medium CRF14 / 1 thread | ~20.7–21.9 s | ~515–526 MB | 1.0 |
| medium CRF14 / 2 threads | ~21.2–21.9 s | ~591–595 MB | ~0.999465 |
| fast CRF14 / 2 threads | ~21.8–23.0 s | ~604–607 MB | ~0.999313 |

### 30 second fixture

| Profile | Time | Peak memory | SSIM vs baseline |
|---|---:|---:|---:|
| medium CRF14 / 1 thread | 43.387 s | 682,430,464 B | 1.0 |
| medium CRF14 / 2 threads | 44.350 s | 767,799,296 B | 0.999522 |
| fast CRF14 / 2 threads | 45.887 s | 798,539,776 B | 0.999313 |

**Winner: medium / CRF14 / 1 thread.**

Two threads were not faster on the Railway workload and materially increased memory pressure, so V105 deliberately retains the one-thread production render.

## Runtime stress matrix

Final post-fix staging matrix:

| Source case | Result | Render time | Peak memory |
|---|---|---:|---:|
| 1080p30 / 48 kHz stereo | PASS | 2.746 s | 440,410,112 B |
| 1080p60 / 44.1 kHz mono | PASS | 5.002 s | 451,686,400 B |
| 1440p60 / no audio | PASS | 5.093 s | 572,018,688 B |
| portrait 1080x1920 / 60 fps | PASS | 6.369 s | 492,724,224 B |
| rotated iPhone-style 1080p60 | PASS | 5.011 s | 499,703,808 B |
| VFR 1080p | PASS | 4.415 s | 505,176,064 B |

Final runtime signal:

`GSF_STRESS_SUMMARY {"ok":true,"failed":[],"count":6}`

All six produced the required social master:
- H.264 High
- avc1
- 1080x1920
- yuv420p
- <=60 fps
- AAC LC
- 48 kHz
- stereo

## Bug found by stress testing

A source with no audio stream previously produced a final MP4 with no AAC track, causing the strict social-master validator to reject it.

V105 adds a source-audio probe. Only when the source has no audio, FFmpeg injects:
`anullsrc=channel_layout=stereo:sample_rate=48000`

Normal sources keep the existing audio path unchanged.

A second test-harness-only bug was also found: generated silent audio is infinite. The benchmark now adds `-shortest` for the no-audio fixture so runtime tests terminate at source duration.

## Prescan deduplication

The old bridge used a short blind wait. Real worker logs showed jobs taking roughly 25–33 seconds on heavier sources, so the web process could begin the same scan locally while the worker was still healthy.

V105:
- polls worker state;
- waits while worker is queued/downloading/scanning;
- consumes the worker result when ready;
- falls back immediately on worker error/unavailability;
- returns cached S3 analysis immediately.

This removes the known healthy-worker duplicate scan path.

## Upload / memory

V105 upload policy:
- 32 MB parts retained.
- Desktop concurrency: 8.
- Mobile concurrency: 3.
- Materialization: default 6, bounded 1..8.

The stress service's Railway aggregate metrics briefly exceeded 1 GB while several staging deployments were overlapping; individual measured render peaks remained below 0.7 GB in the selected profile. After the stress run, service memory returned to roughly 0.10 GB idle.

## Regression suite

GREEN:
- V104.3 render safety
- V104.4 TikTok Social Connect
- V104.5 YouTube Social Connect
- V104.6 stable three-social flow
- V104.7 Instagram Login
- V105 telemetry
- V105 prescan bridge
- V105 upload policy
- V105 worker image contract
- V105 render contract
- V105 benchmark diagnostics
- V105 no-audio application contract
- V105 no-audio benchmark contract
- V105 dependency lock
- V105 stress matrix contract
- legal pages
- TikTok site verification

## Deferred item

A dedicated minimal worker Docker image exists at `web/Dockerfile.worker` with pinned worker dependencies. A second worker staging service could not be created because Railway returned a resource provisioning limit error. The current production worker remains unchanged.

This does not block the web V105 improvements; it only defers independent worker-image rollout.

## Rollback

Production V104.7 deployment/commit remains the rollback reference:
`04935f5ac474486d49d5542a27a6d2430b8980c7`
