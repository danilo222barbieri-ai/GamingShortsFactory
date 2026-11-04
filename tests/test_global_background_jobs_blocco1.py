#!/usr/bin/env python3
"""
Verification suite for GSF Global Background Architecture — BLOCCO 1 (Central Job System).
"""
from __future__ import annotations

import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path

from web.global_jobs_v2 import GlobalJobManager, JobContext


class TestGlobalJobManagerBlocco1(unittest.TestCase):
    def test_job_lifecycle_states_progress_and_user_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            notified = []
            mgr = GlobalJobManager(
                runtime_root=tmp,
                notify_fn=lambda sid, job: notified.append((sid, job["id"], job["status"])),
            )

            def sample_handler(job: dict, ctx: JobContext):
                ctx.set_progress(35.0, stage="Decodifica stream")
                ctx.set_progress(75.0, stage="Codifica clip")
                return {"output": "short_ready.mp4"}

            mgr.register_handler("create_short", sample_handler)

            j1 = mgr.enqueue_job(
                sid="user_alpha",
                kind="create_short",
                title="Short Fortnite #1",
                idempotency_key="short_fn_1",
                account_id="acc_101",
            )
            self.assertTrue(j1["id"].startswith("job_create_short_"))
            self.assertEqual(j1["sid"], "user_alpha")
            self.assertEqual(j1["account_id"], "acc_101")

            # Wait for completion
            deadline = time.time() + 5.0
            final = None
            while time.time() < deadline:
                cur = mgr.get_job("user_alpha", j1["id"])
                if cur and cur["status"] == "completed":
                    final = cur
                    break
                time.sleep(0.05)

            self.assertIsNotNone(final)
            self.assertEqual(final["status"], "completed")
            self.assertEqual(final["status_it"], "completato")
            self.assertEqual(final["progress"], 100.0)
            self.assertEqual(final["result"].get("output"), "short_ready.mp4")
            self.assertEqual(len(notified), 1)
            self.assertEqual(notified[0][0], "user_alpha")

            # User isolation: user_beta cannot see user_alpha's job
            self.assertIsNone(mgr.get_job("user_beta", j1["id"]))
            self.assertEqual(mgr.list_jobs("user_beta"), [])

            # Idempotency: re-submitting with the same idempotency_key returns the same job
            j_dup = mgr.enqueue_job(
                sid="user_alpha",
                kind="create_short",
                title="Short Fortnite #1",
                idempotency_key="short_fn_1",
            )
            self.assertEqual(j_dup["id"], j1["id"])

    def test_concurrency_semaphore_queues_second_heavy_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = GlobalJobManager(runtime_root=tmp, max_cpu_workers=1)
            gate = threading.Event()
            first_started = threading.Event()

            def slow_render(job: dict, ctx: JobContext):
                if job["payload"].get("order") == 1:
                    first_started.set()
                    gate.wait(timeout=4.0)
                ctx.set_progress(50.0, stage="Rendering")
                return {"order": job["payload"].get("order")}

            mgr.register_handler("ffmpeg_render", slow_render)

            job1 = mgr.enqueue_job("sid_conc", "ffmpeg_render", "Render 1", payload={"order": 1})
            self.assertTrue(first_started.wait(timeout=2.0))

            job2 = mgr.enqueue_job("sid_conc", "ffmpeg_render", "Render 2", payload={"order": 2})
            time.sleep(0.1)

            # While job1 holds the single CPU semaphore slot, job2 must remain 'queued' ("in attesa")
            j1_live = mgr.get_job("sid_conc", job1["id"])
            j2_live = mgr.get_job("sid_conc", job2["id"])
            self.assertEqual(j1_live["status"], "running")
            self.assertEqual(j1_live["status_it"], "in esecuzione")
            self.assertEqual(j2_live["status"], "queued")
            self.assertEqual(j2_live["status_it"], "in attesa")

            # Release job1 and verify both complete
            gate.set()
            deadline = time.time() + 5.0
            while time.time() < deadline:
                s1 = mgr.get_job("sid_conc", job1["id"])["status"]
                s2 = mgr.get_job("sid_conc", job2["id"])["status"]
                if s1 == "completed" and s2 == "completed":
                    break
                time.sleep(0.05)

            self.assertEqual(mgr.get_job("sid_conc", job1["id"])["status"], "completed")
            self.assertEqual(mgr.get_job("sid_conc", job2["id"])["status"], "completed")

    def test_failure_retry_and_persistence_across_server_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr1 = GlobalJobManager(runtime_root=tmp)
            calls = {"count": 0}

            def flaky_handler(job: dict, ctx: JobContext):
                calls["count"] += 1
                if calls["count"] == 1:
                    raise RuntimeError("Errore temporaneo di rete")
                return {"recovered": True}

            mgr1.register_handler("social_publish", flaky_handler)
            j = mgr1.enqueue_job("sid_retry", "social_publish", "Pubblica Short", max_retries=3)

            deadline = time.time() + 3.0
            while time.time() < deadline:
                cur = mgr1.get_job("sid_retry", j["id"])
                if cur["status"] == "failed":
                    break
                time.sleep(0.05)

            failed_job = mgr1.get_job("sid_retry", j["id"])
            self.assertEqual(failed_job["status"], "failed")
            self.assertEqual(failed_job["status_it"], "fallito")
            self.assertIn("Errore temporaneo", failed_job["error"])

            # Retry the failed job
            mgr1.retry_job("sid_retry", j["id"])
            deadline = time.time() + 3.0
            while time.time() < deadline:
                cur = mgr1.get_job("sid_retry", j["id"])
                if cur["status"] == "completed":
                    break
                time.sleep(0.05)

            retried_job = mgr1.get_job("sid_retry", j["id"])
            self.assertEqual(retried_job["status"], "completed")
            self.assertEqual(retried_job["attempt"], 2)

            # Simulate an active job interrupted by a server restart
            interrupted = mgr1.enqueue_job(
                "sid_restart",
                "ai_analysis",
                "Analisi IA gameplay",
                initial_status="running",
                initial_progress=42.0,
            )
            self.assertEqual(interrupted["status"], "running")

            # Boot a brand-new GlobalJobManager pointing to the same runtime_root
            mgr2 = GlobalJobManager(runtime_root=tmp)
            mgr2.register_handler("ai_analysis", lambda job, ctx: {"moments": 3})
            recovered = mgr2.recover_after_restart(auto_resume=True)
            self.assertEqual(len(recovered), 1)
            self.assertEqual(recovered[0]["id"], interrupted["id"])

            deadline = time.time() + 4.0
            while time.time() < deadline:
                cur = mgr2.get_job("sid_restart", interrupted["id"])
                if cur["status"] == "completed":
                    break
                time.sleep(0.05)

            final_after_boot = mgr2.get_job("sid_restart", interrupted["id"])
            self.assertEqual(final_after_boot["status"], "completed")
            self.assertEqual(final_after_boot["result"].get("moments"), 3)


if __name__ == "__main__":
    unittest.main()
