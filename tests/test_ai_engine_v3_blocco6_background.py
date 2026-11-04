#!/usr/bin/env python3
"""
Unit and regression tests for GSF AI Engine 3.0 — Blocco 6 (Background e Velocità).
Verifies:
- Execution of AI analysis jobs in background via GlobalJobManager.
- Progress updates and stages reported correctly.
- Cache reuse on repeat analysis (instantaneous response).
- Resilient recovery of completed jobs after process restart.
- Terminal notification 'Momenti IA pronti' dispatched on job completion.
"""
from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from web.global_jobs_v2 import GlobalJobManager
from web.ai_performance_engine_v2 import load_cached_scan, save_cached_scan, ENGINE_VERSION_V2


class TestAiBackgroundSpeedBlocco6(unittest.TestCase):
    def test_background_cache_instant_reuse(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            video_file = tmp_path / "gameplay_sample.mp4"
            video_file.write_bytes(b"dummy_bytes_for_fast_cache_test" * 100)

            mock_scan = {
                "step": 0.5,
                "audio": [0.2, 0.8, 0.4],
                "peak": [0.3, 0.9, 0.5],
                "motion": [0.1, 0.7, 0.3],
                "meta": {"duration_seconds": 1.5},
            }

            # First check: cache miss
            loaded, hit = load_cached_scan(video_file, tmp_path, ENGINE_VERSION_V2)
            self.assertFalse(hit)

            # Save to persistent cache
            save_cached_scan(video_file, mock_scan, tmp_path, ENGINE_VERSION_V2)

            # Second check: cache hit
            loaded2, hit2 = load_cached_scan(video_file, tmp_path, ENGINE_VERSION_V2)
            self.assertTrue(hit2)
            self.assertEqual(loaded2["audio"], mock_scan["audio"])

    def test_global_job_manager_ai_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            sid = "test_user_bg_ai"
            notified = []

            def mock_notify(s, job):
                notified.append((s, job.get("status"), job.get("kind")))

            mgr = GlobalJobManager(runtime_root=root, notify_fn=mock_notify)

            # Handler for ai_analysis
            def handle_ai(job, ctx):
                ctx.set_progress(25.0, stage="Scansione rapida...")
                ctx.set_progress(75.0, stage="Smart Ranking...")
                return {"candidates": [0.0, 15.0], "count": 2}

            mgr.register_handler("ai_analysis", handle_ai)

            job = mgr.enqueue(
                sid=sid,
                kind="ai_analysis",
                title="Trova i momenti IA",
                payload={"duration": 15.0, "genre": "FPS"},
            )
            self.assertIn(job["status"], ("queued", "running", "completed"))

            # Wait for background completion
            t0 = time.time()
            done_job = None
            while time.time() - t0 < 5.0:
                snap = mgr.get_job(sid, job["id"])
                if snap and snap["status"] in ("completed", "failed"):
                    done_job = snap
                    break
                time.sleep(0.05)

            self.assertIsNotNone(done_job)
            self.assertEqual(done_job["status"], "completed")
            self.assertEqual(done_job["progress"], 100.0)
            self.assertEqual(len(notified), 1)
            self.assertEqual(notified[0], (sid, "completed", "ai_analysis"))

            # Verify persistence across restart
            mgr_restarted = GlobalJobManager(runtime_root=root)
            restored = mgr_restarted.get_job(sid, job["id"])
            self.assertIsNotNone(restored)
            self.assertEqual(restored["status"], "completed")


if __name__ == "__main__":
    unittest.main()
