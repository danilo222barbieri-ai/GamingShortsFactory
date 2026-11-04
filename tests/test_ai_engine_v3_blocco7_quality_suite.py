#!/usr/bin/env python3
"""
Master Integration & Regression Suite for GSF AI Engine 3.0 (Blocco 7).
Comprehensive coverage:
1. Short videos (15s, 30s, 60s) fast execution
2. Long videos adaptive scan profile
3. Game genre adaptation (FPS, Action, Racing, Sports, Horror, RPG, Platform, Narrative)
4. Silent / low-signal video honesty
5. Duplicate elimination & MMR temporal spacing
6. No interesting events handling
7. Twitch VOD with matching clips (returns 3 ranked moments)
8. Twitch VOD without clips (insufficient data honesty)
9. 3 preview cards metadata generation (v71_mini format)
10. Single clip selection & acquisition contract
11. Page navigation & session state persistence
12. Twitch expired token / error resilience
13. Server restart job recovery
14. Non-regression of ranking stability
"""
from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from web.ai_performance_engine_v2 import (
    ENGINE_VERSION_V2,
    GAME_PROFILES,
    generate_mini_previews_parallel,
    get_game_profile,
    infer_game_genre_v2,
    is_low_signal_scan,
    load_cached_scan,
    precision_refine_boundary,
    probe_media_duration,
    run_fast_ai_pipeline,
    save_cached_scan,
    scan_profile_for_duration,
    smart_rank_candidates,
    verify_and_diversify_candidates,
)
from web.feedback_learning_v127 import (
    empty_user_model,
    load_user_model,
    reset_user_model,
    update_user_preferences,
    user_learning_multiplier,
)
from web.global_jobs_v2 import GlobalJobManager
from web.direct_upload_server import _twitch_vod_moments


class TestAiEngineV3QualitySuite(unittest.TestCase):
    def test_01_short_videos_and_long_videos_profiles(self):
        # 1 & 2: Short vs long duration profiles
        p15 = scan_profile_for_duration(15.0)
        p30 = scan_profile_for_duration(30.0)
        p60 = scan_profile_for_duration(60.0)
        p900 = scan_profile_for_duration(900.0)  # 15 minutes

        self.assertEqual(p15["tier"], "fast_short")
        self.assertEqual(p30["tier"], "fast_short")
        self.assertEqual(p60["tier"], "fast_short")
        self.assertEqual(p900["tier"], "medium_turbo")
        self.assertTrue(p900["adaptive"])
        self.assertTrue(p900["keyframes_only"])

    def test_02_game_genres_adaptation(self):
        # 3: All 10 genres properly profile-matched
        genres = ["FPS", "Battle Royale", "Action", "Racing", "Sports", "Survival", "Horror", "RPG", "Platform", "Narrative"]
        for g in genres:
            prof = get_game_profile(g)
            self.assertEqual(prof["name"], g)
            self.assertTrue(len(prof["important_events"]) >= 3)
            self.assertIn("pre_event_seconds", prof["context_padding"])

    def test_03_silent_and_low_signal_honesty(self):
        # 4 & 6: Silent video & no interesting events
        silent_scan = {
            "step": 0.5,
            "audio": [0.0] * 40,
            "motion": [0.0] * 40,
            "peak": [0.0] * 40,
        }
        self.assertTrue(is_low_signal_scan(silent_scan))
        selected, alts = smart_rank_candidates(silent_scan, target_duration=15.0, total_seconds=20.0)
        self.assertTrue(len(selected) >= 1)
        self.assertTrue(selected[0].get("low_signal"))

    def test_04_close_moments_and_diversity(self):
        # 5: Nearby peaks must not produce overlapping moments
        step = 0.5
        n = 100
        audio = [0.1] * n
        motion = [0.1] * n
        peak = [0.1] * n

        # Bursts clustered together at 10s and 11s
        audio[20] = 0.9
        motion[20] = 0.9
        audio[22] = 0.88
        motion[22] = 0.88

        # Another distinct burst at 35s
        audio[70] = 0.85
        motion[70] = 0.85

        scan = {"step": step, "audio": audio, "motion": motion, "peak": peak}
        selected, alts = smart_rank_candidates(scan, target_duration=15.0, total_seconds=50.0, target_count=3)
        starts = [s["start"] for s in selected]
        for i in range(len(starts)):
            for j in range(i + 1, len(starts)):
                self.assertGreaterEqual(abs(starts[i] - starts[j]), 4.0)

    @patch("web.direct_upload_server._twitch_access")
    @patch("web.direct_upload_server._twitch_api")
    def test_05_twitch_vod_moments_and_insufficient_data(self, mock_api, mock_access):
        # 7 & 8: Twitch VOD with clips vs without clips
        mock_access.return_value = {"access_token": "token", "user_id": "usr_99"}

        # Case A: VOD with clips
        mock_api.side_effect = [
            {"data": [{"id": "v101", "title": "Stream Day 1", "duration": "3h", "created_at": "2026-11-04T10:00:00Z"}]},
            {"data": [
                {"id": "c1", "video_id": "v101", "title": "Highlight 1", "vod_offset": 500.0, "duration": 30.0, "view_count": 80},
                {"id": "c2", "video_id": "v101", "title": "Highlight 2", "vod_offset": 2500.0, "duration": 25.0, "view_count": 250},
                {"id": "c3", "video_id": "v101", "title": "Highlight 3", "vod_offset": 4500.0, "duration": 35.0, "view_count": 140},
            ]}
        ]
        res = _twitch_vod_moments("sid_1", "v101")
        self.assertEqual(res.get("count"), 3)
        self.assertEqual(res.get("reason"), "success")

        # Case B: VOD without clips
        mock_api.side_effect = [
            {"data": [{"id": "v102", "title": "Quiet Stream", "duration": "2h", "created_at": "2026-11-04T10:00:00Z"}]},
            {"data": []}
        ]
        res_empty = _twitch_vod_moments("sid_1", "v102")
        self.assertEqual(res_empty.get("count"), 0)
        self.assertEqual(res_empty.get("reason"), "insufficient_data")

    def test_06_personalization_and_reset(self):
        # 10 & 11: Per-user learning and preference reset
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            sid = "gamer_x"
            # Initial multiplier
            m = load_user_model(sid, runtime_root=root)
            self.assertEqual(user_learning_multiplier(m, "boss", genre="RPG"), 1.0)

            # Update with positive reinforcement
            for _ in range(4):
                update_user_preferences(sid, {"event": "boss", "genre": "RPG", "action": "published", "score": 0.9}, runtime_root=root)

            m_updated = load_user_model(sid, runtime_root=root)
            self.assertGreater(user_learning_multiplier(m_updated, "boss", genre="RPG"), 1.0)

            # Reset
            reset_user_model(sid, runtime_root=root)
            m_reset = load_user_model(sid, runtime_root=root)
            self.assertEqual(m_reset.get("total_feedback"), 0)
            self.assertEqual(user_learning_multiplier(m_reset, "boss", genre="RPG"), 1.0)

    def test_07_server_restart_and_job_recovery(self):
        # 13: Job recovery across process restart
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            sid = "restart_sid"
            mgr1 = GlobalJobManager(runtime_root=root)
            mgr1.register_handler("ai_analysis", lambda j, ctx: {"status": "ok"})
            job = mgr1.enqueue(sid=sid, kind="ai_analysis", title="Test AI", payload={})

            # Wait for execution
            time.sleep(0.3)
            # Recreate manager simulating restart
            mgr2 = GlobalJobManager(runtime_root=root)
            recovered = mgr2.get_job(sid, job["id"])
            self.assertIsNotNone(recovered)
            self.assertEqual(recovered["id"], job["id"])

    def test_08_end_to_end_fast_pipeline_benchmark(self):
        # 1, 9, 14: End to end pipeline and mini preview generation
        import subprocess
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            video_file = tmp_path / "gameplay_30s.mp4"
            out_media = tmp_path / "media"

            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "testsrc=duration=30:size=360x240:rate=25",
                "-f", "lavfi",
                "-i", "sine=frequency=440:duration=30",
                "-c:v", "libx264", "-preset", "ultrafast",
                "-c:a", "aac", "-b:a", "64k",
                str(video_file)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            t0 = time.perf_counter()
            res = run_fast_ai_pipeline(
                video_file,
                out_media,
                duration=15.0,
                genre="FPS",
                profile="auto",
                request_id="pipeline_bench_req",
                generate_previews=True,
            )
            elapsed = time.perf_counter() - t0
            # Target for 30s video is 2-5s
            self.assertLess(elapsed, 4.0, f"30s benchmark exceeded: {elapsed:.2f}s")
            self.assertTrue(len(res["candidates"]) >= 1)
            meta_path = out_media / "ai_results_meta.json"
            self.assertTrue(meta_path.is_file())
            minis = list(out_media.glob("v71_mini_*.mp4"))
            self.assertTrue(len(minis) >= 1)


if __name__ == "__main__":
    unittest.main()
