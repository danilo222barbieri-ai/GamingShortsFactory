import time

import pytest

from gsf_core.assets import AssetKind, AssetRef
from gsf_core.cache import ArtifactCacheKey, JsonArtifactCache, ProxyProfile
from gsf_core.jobs import (
    InvalidJobTransition,
    JobRecord,
    JobStatus,
    JsonJobStore,
)
from gsf_core.storage import LocalStorage, S3Storage
from gsf_core.telemetry import CostModel, JobMetrics, phase_timer


def make_asset(**overrides):
    data = dict(
        asset_id="asset-1",
        backend="s3",
        key="projects/p1/source.mp4",
        kind=AssetKind.SOURCE,
        content_type="video/mp4",
        size_bytes=1234,
        checksum_sha256="a" * 64,
    )
    data.update(overrides)
    return AssetRef(**data)


def test_asset_ref_round_trip_never_serializes_raw_bytes():
    asset = make_asset(metadata={"fps": 60, "width": 3840})
    payload = asset.to_dict()

    assert "bytes" not in payload
    assert "data" not in payload
    assert payload["key"] == "projects/p1/source.mp4"
    assert AssetRef.from_dict(payload) == asset

    with pytest.raises((TypeError, ValueError)):
        AssetRef(
            asset_id="bad",
            backend="memory",
            key=b"raw-video",
            kind=AssetKind.SOURCE,
            content_type="video/mp4",
        )


def test_job_store_persists_and_enforces_lifecycle(tmp_path):
    store = JsonJobStore(tmp_path / "jobs")
    job = JobRecord.new(
        project_id="p1",
        kind="analyze",
        inputs=[make_asset()],
        max_attempts=2,
    )
    store.create(job)

    reopened = JsonJobStore(tmp_path / "jobs")
    loaded = reopened.get(job.job_id)
    assert loaded.status is JobStatus.QUEUED

    running = reopened.transition(
        job.job_id,
        JobStatus.RUNNING,
        worker_id="worker-a",
        progress=0.1,
    )
    assert running.status is JobStatus.RUNNING
    assert running.attempts == 1
    assert running.worker_id == "worker-a"
    assert running.heartbeat_at is not None

    heartbeat = reopened.heartbeat(
        job.job_id,
        worker_id="worker-a",
        progress=0.55,
        metadata={"phase": "whisper"},
    )
    assert heartbeat.progress == pytest.approx(0.55)
    assert heartbeat.metadata["phase"] == "whisper"

    with pytest.raises(InvalidJobTransition):
        reopened.heartbeat(job.job_id, worker_id="wrong-worker", progress=0.6)

    completed = reopened.transition(
        job.job_id,
        JobStatus.COMPLETED,
        progress=1.0,
        outputs=[make_asset(asset_id="asset-out", kind=AssetKind.RENDER)],
    )
    assert completed.status is JobStatus.COMPLETED
    assert completed.finished_at is not None
    assert completed.outputs[0].asset_id == "asset-out"

    with pytest.raises(InvalidJobTransition):
        reopened.transition(job.job_id, JobStatus.RUNNING)


def test_failed_job_can_retry_until_max_attempts(tmp_path):
    store = JsonJobStore(tmp_path / "jobs")
    job = JobRecord.new(project_id="p1", kind="render", max_attempts=2)
    store.create(job)

    store.transition(job.job_id, JobStatus.RUNNING, worker_id="w1")
    failed = store.transition(job.job_id, JobStatus.FAILED, error="ffmpeg exit 1")
    assert failed.can_retry is True

    queued = store.retry(job.job_id)
    assert queued.status is JobStatus.QUEUED

    store.transition(job.job_id, JobStatus.RUNNING, worker_id="w2")
    failed_again = store.transition(job.job_id, JobStatus.FAILED, error="ffmpeg exit 1")
    assert failed_again.attempts == 2
    assert failed_again.can_retry is False

    with pytest.raises(InvalidJobTransition):
        store.retry(job.job_id)


def test_local_storage_streams_file_and_returns_asset_ref(tmp_path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"x" * 1024 * 1024)

    storage = LocalStorage(tmp_path / "assets")
    ref = storage.put_file(
        source,
        key="projects/p1/source.bin",
        kind=AssetKind.SOURCE,
        content_type="application/octet-stream",
    )

    assert ref.size_bytes == 1024 * 1024
    assert ref.checksum_sha256
    assert storage.path_for(ref).read_bytes() == source.read_bytes()


class FakeS3:
    def __init__(self):
        self.calls = []
        self.head = {
            "ContentLength": 123456,
            "ContentType": "video/mp4",
            "ETag": '"abc123"',
            "Metadata": {"sha256": "b" * 64},
        }

    def generate_presigned_post(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "url": "https://storage.example/upload",
            "fields": {"key": kwargs["Key"], "policy": "signed"},
        }

    def head_object(self, **kwargs):
        self.calls.append({"head_object": kwargs})
        return self.head


def test_s3_presigned_upload_targets_storage_not_frontend():
    fake = FakeS3()
    storage = S3Storage(
        bucket="gsf-media",
        prefix="prod",
        client=fake,
    )

    target = storage.create_presigned_upload(
        project_id="p1",
        filename="Gameplay 01.MP4",
        kind=AssetKind.SOURCE,
        content_type="video/mp4",
        max_bytes=4 * 1024**3,
        expires_in=900,
    )

    assert target.method == "POST"
    assert target.url == "https://storage.example/upload"
    assert target.asset.backend == "s3"
    assert target.asset.key.startswith("prod/projects/p1/source/")
    assert target.asset.key.endswith(".mp4")
    assert target.max_bytes == 4 * 1024**3
    assert fake.calls[0]["Bucket"] == "gsf-media"
    conditions = fake.calls[0]["Conditions"]
    assert ["content-length-range", 1, 4 * 1024**3] in conditions

    confirmed = storage.confirm_upload(target.asset, max_bytes=4 * 1024**3)
    assert confirmed.size_bytes == 123456
    assert confirmed.checksum_sha256 == "b" * 64
    assert confirmed.metadata["upload_state"] == "confirmed"

    fake.head["ContentLength"] = 5 * 1024**3
    with pytest.raises(ValueError):
        storage.confirm_upload(target.asset, max_bytes=4 * 1024**3)


def test_cache_key_is_deterministic_and_parameter_sensitive(tmp_path):
    a = ArtifactCacheKey.build(
        source_checksum="f" * 64,
        operation="whisper",
        version="large-v3",
        params={"language": "it", "vad": True},
    )
    b = ArtifactCacheKey.build(
        source_checksum="f" * 64,
        operation="whisper",
        version="large-v3",
        params={"vad": True, "language": "it"},
    )
    c = ArtifactCacheKey.build(
        source_checksum="f" * 64,
        operation="whisper",
        version="large-v3",
        params={"vad": False, "language": "it"},
    )
    assert a.digest == b.digest
    assert a.digest != c.digest

    cache = JsonArtifactCache(tmp_path / "cache.json")
    ref = make_asset(asset_id="transcript", kind=AssetKind.ANALYSIS)
    cache.put(a, ref)
    assert JsonArtifactCache(tmp_path / "cache.json").get(b) == ref


def test_proxy_profile_is_explicit_and_cacheable():
    profile = ProxyProfile.editor_default()
    assert profile.max_height <= 720
    assert profile.video_codec
    assert profile.audio_codec
    assert profile.cache_params()["purpose"] == "editor_proxy"


def test_metrics_phase_timing_and_cost_model():
    metrics = JobMetrics()
    with phase_timer(metrics, "whisper"):
        time.sleep(0.01)

    assert metrics.phase_seconds["whisper"] >= 0.005

    metrics.cpu_seconds = 120
    metrics.gpu_seconds = 30
    metrics.egress_bytes = 2 * 1024**3

    costs = CostModel(
        cpu_eur_per_hour=0.12,
        gpu_eur_per_hour=0.90,
        egress_eur_per_gb=0.02,
    ).estimate(metrics)

    assert costs["cpu"] == pytest.approx(0.004, rel=1e-6)
    assert costs["gpu"] == pytest.approx(0.0075, rel=1e-6)
    assert costs["egress"] == pytest.approx(0.04, rel=1e-6)
    assert costs["total"] == pytest.approx(sum(v for k, v in costs.items() if k != "total"), rel=1e-6)
