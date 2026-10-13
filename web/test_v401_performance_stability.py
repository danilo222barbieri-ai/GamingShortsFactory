#!/usr/bin/env python3
import io
import tempfile
from pathlib import Path

from job_state_v401 import (
    ACTIVE_JOB_STATES,
    enrich_job_state,
    job_state_key,
    load_job_state,
    persist_job_state,
    recover_persisted_state,
)
from fix_v401_frontend_memory import patch_runtime_source, stream_uploaded_file
from fix_v401_worker_state import patch_worker_source


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:", msg)


class FakeS3:
    def __init__(self):
        self.objects = {}

    def put_object(self, Bucket, Key, Body, **kwargs):
        self.objects[(Bucket, Key)] = bytes(Body)
        return {"ETag": "fake"}

    def get_object(self, Bucket, Key):
        raw = self.objects[(Bucket, Key)]
        return {"Body": io.BytesIO(raw)}


need("semantic" in ACTIVE_JOB_STATES,
     "semantic analysis is treated as an active worker state")
need(job_state_key("abc123").startswith("worker-jobs/v401/"),
     "V401 worker state uses its own persistent bucket namespace")

semantic = enrich_job_state({"state": "semantic", "analysis_key": "analysis/demo.json"}, now=100.0)
need(0.70 <= float(semantic["progress"]) < 1.0,
     "semantic phase exposes stable progress metadata")
need(float(semantic["updated_at"]) == 100.0,
     "job-state enrichment stamps deterministic update time")

fake = FakeS3()
persist_job_state(fake, "bucket", "job-1", semantic)
loaded = load_job_state(fake, "bucket", "job-1")
need(loaded["state"] == "semantic" and loaded["analysis_key"] == "analysis/demo.json",
     "job state round-trips through persistent object storage")

recovered = recover_persisted_state(loaded)
need(recovered["state"] == "interrupted" and recovered["previous_state"] == "semantic",
     "persisted active jobs recover as interrupted after worker restart")
need(recovered["retryable"] is True,
     "interrupted jobs are explicitly retryable")

done = recover_persisted_state(enrich_job_state({"state": "done", "analysis_key": "analysis/done.json"}, now=200.0))
need(done["state"] == "done" and float(done["progress"]) == 1.0,
     "terminal completed jobs remain completed after restart")

payload = b"0123456789" * 1024
uploaded = io.BytesIO(payload)
uploaded.seek(17)
with tempfile.TemporaryDirectory(prefix="gsf_v401_test_") as tmp:
    target = Path(tmp) / "video.mp4"
    written = stream_uploaded_file(uploaded, target, chunk_size=257)
    need(written == len(payload) and target.read_bytes() == payload,
         "fallback upload is streamed completely to disk in bounded chunks")
    need(uploaded.tell() == 17,
         "streaming fallback restores the original UploadedFile cursor")

source = Path("app.py").read_text(encoding="utf-8")
patched = patch_runtime_source(source)
need("video.getvalue()" not in patched,
     "V401 removes full-buffer video.getvalue copies from fallback disk materialization")
need("GSF_V401_STREAM_UPLOAD_HELPER" in patched,
     "runtime patch installs the V401 bounded streaming helper")
need(patch_runtime_source(patched) == patched,
     "runtime memory patch is idempotent across service restarts")

worker = Path("web/ai_worker_server.py").read_text(encoding="utf-8")
patched_worker = patch_worker_source(worker)
need("from job_state_v401 import" in patched_worker,
     "V401 worker build patch wires the persistent job-state module")
need("existing.get(\"state\") in ACTIVE_JOB_STATES" in patched_worker,
     "duplicate suppression uses the shared active-state contract including semantic")
need("_set_job_state" in patched_worker and "_get_job_state" in patched_worker,
     "worker centralizes job-state writes and recovery-aware reads")
need(patch_worker_source(patched_worker) == patched_worker,
     "worker-state patch is idempotent across image rebuilds")

worker_docker = Path("web/Dockerfile.worker").read_text(encoding="utf-8")
need("fix_v401_worker_state.py" in worker_docker,
     "worker image applies V401 state persistence before syntax verification")

compat = Path("web/apply_v343_v293_compat.py").read_text(encoding="utf-8")
need("fix_v401_frontend_memory" in compat and "patch_runtime_file" in compat,
     "restart-safe runtime bootstrap reapplies the V401 frontend memory patch")

print("V401 Performance & Stability contract: PASS")
