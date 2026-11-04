from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

from web.global_jobs_v2 import GlobalJobManager


ROOT = Path(__file__).resolve().parents[1]


def test_default_global_job_handlers_execute_ai_and_project_save_in_background():
    import web.direct_upload_server as dus

    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        old_root = dus.ROOT
        old_mgr = dus._GLOBAL_JOB_MANAGER
        dus.ROOT = tmp_root
        notified = []
        mgr = GlobalJobManager(
            runtime_root=tmp_root,
            notify_fn=lambda sid, job: notified.append((sid, job["kind"], job["status"])),
        )
        dus._register_default_job_handlers(mgr)
        dus._GLOBAL_JOB_MANAGER = mgr
        try:
            sid = "session_blocco3_bg"
            media_dir = tmp_root / "sessions" / sid / "media"
            media_dir.mkdir(parents=True, exist_ok=True)
            src_video = media_dir / "source_gameplay.mp4"
            src_video.write_bytes(b"\x00\x00\x00\x18ftypmp42" + b"V" * 4096)
            (tmp_root / "sessions" / sid / "editor2027_current.txt").write_text(
                str(src_video), encoding="utf-8"
            )

            # 1. Enqueue background AI analysis job (simulating user starting AI and changing page / closing app)
            ai_job = mgr.enqueue_job(
                sid=sid,
                kind="ai_analysis",
                title="Analisi IA · Call of Duty",
                payload={"source_path": str(src_video), "duration": 15, "engine": "action", "request_id": "req_b3_1"},
            )
            deadline = time.time() + 5.0
            while time.time() < deadline:
                cur = mgr.get_job(sid, ai_job["id"])
                if cur and cur["status"] in ("completed", "failed"):
                    break
                time.sleep(0.05)

            final_ai = mgr.get_job(sid, ai_job["id"])
            assert final_ai is not None
            assert final_ai["status"] == "completed"
            assert final_ai["status_it"] == "completato"
            assert final_ai["progress"] == 100.0
            assert (media_dir / "ai_results_meta.json").is_file()

            # 2. Enqueue background project_save job
            save_job = mgr.enqueue_job(
                sid=sid,
                kind="project_save",
                title="Salvataggio Progetto",
                payload={"upload_id": "up_b3", "name": "CallOfDuty.mp4", "title": "Progetto CoD"},
            )
            deadline = time.time() + 5.0
            while time.time() < deadline:
                cur = mgr.get_job(sid, save_job["id"])
                if cur and cur["status"] in ("completed", "failed"):
                    break
                time.sleep(0.05)

            final_save = mgr.get_job(sid, save_job["id"])
            assert final_save is not None
            assert final_save["status"] == "completed"
            assert final_save["progress"] == 100.0
            assert any(k == "ai_analysis" and st == "completed" for _s, k, st in notified)
            assert any(k == "project_save" and st == "completed" for _s, k, st in notified)
        finally:
            dus._GLOBAL_JOB_MANAGER = old_mgr
            dus.ROOT = old_root


def test_ai_write_results_meta_syncs_with_global_job_manager():
    from web.ai_engines_v412 import write_results_meta

    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        sid = "session_ai_sync_01"
        media_dir = tmp_root / "sessions" / sid / "media"
        media_dir.mkdir(parents=True, exist_ok=True)

        write_results_meta(
            media_dir,
            {"request_id": "req_sync_99", "status": "analyzing", "engine": "AUTO", "items": []},
        )
        mgr = GlobalJobManager(runtime_root=tmp_root)
        jobs = mgr.list_jobs(sid)
        assert len(jobs) == 1
        assert jobs[0]["kind"] == "ai_analysis"
        assert jobs[0]["status"] == "running"
        assert jobs[0]["progress"] == 35.0

        write_results_meta(
            media_dir,
            {
                "request_id": "req_sync_99",
                "status": "success",
                "engine": "AUTO",
                "items": [{"index": 0, "start_time": 4.0, "end_time": 19.0}],
            },
        )
        mgr2 = GlobalJobManager(runtime_root=tmp_root)
        jobs2 = mgr2.list_jobs(sid)
        assert len(jobs2) == 1
        assert jobs2[0]["status"] == "completed"
        assert jobs2[0]["progress"] == 100.0


def test_global_activity_center_present_in_push_client():
    import web.direct_upload_server as dus

    js = dus._push_client_bytes().decode("utf-8")
    assert "GSFActivityCenter" in js
    assert "Centro Attività Globale" in js
    assert "/jobs/list" in js
    assert "/jobs/cancel" in js
    assert "/jobs/retry" in js
    assert "/jobs/enqueue" in js
    assert 'font-family:"Avenir' not in js
