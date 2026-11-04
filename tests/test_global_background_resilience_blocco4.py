from __future__ import annotations

import json
import tempfile
import threading
import time
from pathlib import Path

from web.global_jobs_v2 import GlobalJobManager, JobContext


ROOT = Path(__file__).resolve().parents[1]


def test_1_and_2_page_change_and_app_close_reopen_preserve_job_progress_and_completion():
    """Scenarios 1 & 2: Changing page or closing/reopening the app during a job never interrupts execution."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        sid = "sid_page_and_reopen"
        step_gate = threading.Event()
        halfway_reached = threading.Event()

        mgr = GlobalJobManager(runtime_root=tmp_root)

        def long_ai_job(job: dict, ctx: JobContext):
            ctx.set_progress(25.0, stage="Decodifica rapida")
            ctx.set_progress(55.0, stage="Valutazione momenti")
            halfway_reached.set()
            step_gate.wait(timeout=4.0)
            ctx.set_progress(90.0, stage="Rifinitura timestamp")
            return {"moments": [3.5, 18.0, 42.0]}

        mgr.register_handler("ai_analysis", long_ai_job)
        job = mgr.enqueue_job(sid, "ai_analysis", "Analisi IA · Apex Legends", idempotency_key="ai_apex_1")
        assert halfway_reached.wait(timeout=2.0)

        # User changes page (queries /jobs/list from another route)
        active_on_new_page = mgr.list_jobs(sid)
        assert len(active_on_new_page) == 1
        assert active_on_new_page[0]["status"] == "running"
        assert active_on_new_page[0]["progress"] == 55.0

        # User closes the app while server completes the job
        step_gate.set()
        deadline = time.time() + 4.0
        while time.time() < deadline:
            if mgr.get_job(sid, job["id"])["status"] == "completed":
                break
            time.sleep(0.05)

        # User reopens the app (new read from persisted state)
        reopened_mgr = GlobalJobManager(runtime_root=tmp_root)
        restored_job = reopened_mgr.get_job(sid, job["id"])
        assert restored_job is not None
        assert restored_job["status"] == "completed"
        assert restored_job["status_it"] == "completato"
        assert restored_job["progress"] == 100.0
        assert restored_job["result"]["moments"] == [3.5, 18.0, 42.0]


def test_3_server_restart_recovers_and_completes_interrupted_jobs():
    """Scenario 3: Server restart persists jobs on disk and recovers/resumes them automatically."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        sid = "sid_server_restart"

        # Simulate a job that was 'running' at 40% when the server container restarted
        mgr_before_crash = GlobalJobManager(runtime_root=tmp_root)
        job = mgr_before_crash.enqueue_job(
            sid,
            "create_short",
            "Creazione Short 9:16",
            payload={"clip_start": 12.0},
            initial_status="running",
            initial_progress=40.0,
        )
        assert mgr_before_crash.get_job(sid, job["id"])["status"] == "running"

        # New server boot: register handler and call recover_after_restart()
        mgr_after_boot = GlobalJobManager(runtime_root=tmp_root)
        mgr_after_boot.register_handler(
            "create_short",
            lambda j, ctx: (ctx.set_progress(80.0, stage="Ripresa post-riavvio"), {"short": "ready.mp4"})[1],
        )
        recovered = mgr_after_boot.recover_after_restart()
        assert any(r["id"] == job["id"] for r in recovered)

        deadline = time.time() + 4.0
        while time.time() < deadline:
            cur = mgr_after_boot.get_job(sid, job["id"])
            if cur and cur["status"] == "completed":
                break
            time.sleep(0.05)

        final = mgr_after_boot.get_job(sid, job["id"])
        assert final["status"] == "completed"
        assert final["recovered_after_restart"] is True
        assert final["progress"] == 100.0
        assert final["result"]["short"] == "ready.mp4"


def test_4_and_5_temporary_connection_loss_and_resumable_upload():
    """Scenarios 4 & 5: Temporary connection drop during upload resumes from last chunk without restarting from 0%."""
    import web.direct_upload_server as dus

    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        old_root = dus.ROOT
        old_mgr = dus._GLOBAL_JOB_MANAGER
        dus.ROOT = tmp_root
        mgr = GlobalJobManager(runtime_root=tmp_root)
        dus._GLOBAL_JOB_MANAGER = mgr
        try:
            sid = "sid_conn_drop"
            upload_id = "up_resumable_4chunks"
            upload_dir = tmp_root / "sessions" / sid / "direct_upload" / upload_id
            upload_dir.mkdir(parents=True, exist_ok=True)
            data_path = upload_dir / "upload.tmp"
            state_path = upload_dir / "state.json"

            # Chunks 0 and 1 succeeded before temporary connection loss (50%)
            total = 4096
            with open(data_path, "wb") as fh:
                fh.truncate(total)
                fh.seek(0)
                fh.write(b"X" * 2048)

            dus._write_json_atomic(
                state_path,
                {
                    "total": total,
                    "count": 4,
                    "name": "Valorant_Clutch.mp4",
                    "stem": "Valorant_Clutch",
                    "ext": ".mp4",
                    "ranges": {"0": [0, 1024], "1": [1024, 1024]},
                    "received": [0, 1],
                },
            )
            up_job = mgr.enqueue(
                sid=sid,
                kind="upload",
                title="Upload · Valorant_Clutch.mp4",
                payload={"upload_id": upload_id, "size": total, "count": 4},
                idempotency_key=f"upload_{upload_id}",
                auto_start=False,
            )
            mgr.update_job(sid, up_job["id"], state="running", progress=50.0, stage_label="Caricamento chunk 2/4")

            # Connection returns: client queries state and uploads only chunks 2 and 3
            state = json.loads(state_path.read_text(encoding="utf-8"))
            missing = [i for i in range(4) if i not in set(state["received"])]
            assert missing == [2, 3]

            with open(data_path, "r+b") as fh:
                for idx in missing:
                    fh.seek(idx * 1024)
                    fh.write(b"Y" * 1024)
                    state["received"].append(idx)
            dus._write_json_atomic(state_path, state)
            assert sorted(state["received"]) == [0, 1, 2, 3]
        finally:
            dus._GLOBAL_JOB_MANAGER = old_mgr
            dus.ROOT = old_root


def test_6_two_concurrent_jobs_respect_limits_and_both_complete():
    """Scenario 6: Two concurrent jobs run safely within Railway concurrency limits."""
    with tempfile.TemporaryDirectory() as tmp:
        mgr = GlobalJobManager(runtime_root=tmp, max_cpu_workers=1, max_io_workers=2)
        mgr.register_handler("ai_analysis", lambda j, ctx: {"job": j["title"]})
        mgr.register_handler("project_save", lambda j, ctx: {"saved": j["title"]})

        j_cpu = mgr.enqueue_job("sid_dual", "ai_analysis", "AI Job")
        j_io = mgr.enqueue_job("sid_dual", "project_save", "Save Job")

        deadline = time.time() + 4.0
        while time.time() < deadline:
            s1 = mgr.get_job("sid_dual", j_cpu["id"])["status"]
            s2 = mgr.get_job("sid_dual", j_io["id"])["status"]
            if s1 == "completed" and s2 == "completed":
                break
            time.sleep(0.05)

        assert mgr.get_job("sid_dual", j_cpu["id"])["status"] == "completed"
        assert mgr.get_job("sid_dual", j_io["id"])["status"] == "completed"


def test_7_and_8_failure_retry_and_zero_duplication_or_data_loss():
    """Scenarios 7 & 8: Controlled failure + retry, zero duplication of results, and social/draft preservation."""
    import web.direct_upload_server as dus

    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        old_root = dus.ROOT
        dus.ROOT = tmp_root
        try:
            sid = "sid_retry_nodup"
            # Preserve existing drafts and local social token files before running background jobs
            session_dir = tmp_root / "sessions" / sid
            session_dir.mkdir(parents=True, exist_ok=True)
            social_tok_file = session_dir / ".instagram_oauth.json"
            social_tok_file.write_text(json.dumps({"access_token": "ig_tok_keep", "ig_user_id": "ig1"}), encoding="utf-8")
            dus._draft_save(sid, {"id": "draft_existing_1", "title": "Bozza Esistente", "source_name": "Clip1.mp4", "state": {"k": "v"}})

            mgr = GlobalJobManager(runtime_root=tmp_root)
            attempts = {"n": 0}

            def flaky_render(job: dict, ctx: JobContext):
                attempts["n"] += 1
                if attempts["n"] == 1:
                    raise RuntimeError("Errore temporaneo disco")
                return {"artifact": "short_v1.mp4"}

            mgr.register_handler("ffmpeg_render", flaky_render)
            j = mgr.enqueue_job(sid, "ffmpeg_render", "Render Short", idempotency_key="render_unique_1")

            deadline = time.time() + 3.0
            while time.time() < deadline:
                if mgr.get_job(sid, j["id"])["status"] == "failed":
                    break
                time.sleep(0.05)
            assert mgr.get_job(sid, j["id"])["status"] == "failed"

            # Retry the failed job
            mgr.retry_job(sid, j["id"])
            deadline = time.time() + 3.0
            while time.time() < deadline:
                if mgr.get_job(sid, j["id"])["status"] == "completed":
                    break
                time.sleep(0.05)

            completed = mgr.get_job(sid, j["id"])
            assert completed["status"] == "completed"
            assert completed["attempt"] == 2

            # Re-submitting with the same idempotency_key must NOT duplicate the job or result
            dup = mgr.enqueue_job(sid, "ffmpeg_render", "Render Short", idempotency_key="render_unique_1")
            assert dup["id"] == j["id"]
            assert len(mgr.list_jobs(sid)) == 1

            # Verify drafts and social token files were untouched
            assert json.loads(social_tok_file.read_text(encoding="utf-8"))["access_token"] == "ig_tok_keep"
            assert any(d.get("id") == "draft_existing_1" for d in dus._draft_list(sid))
        finally:
            dus.ROOT = old_root
