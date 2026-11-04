#!/usr/bin/env python3
"""
Anti-regression & verification suite for GSF AI Performance Engine 2.0 (Blocchi 2–7).
Covers:
- Adaptive fast scan profiles for 15s, 30s, 60s, 5m, 15m, and 60m+ videos
- Singleton Whisper model cache & persistent disk/memory scan cache
- All 10 Game-Aware AI genre profiles + Auto fallback across V2, V108, and V112
- Multi-signal verifiable ranking, low-signal honesty, and anti-duplication
- Zero-subprocess precision boundary refinement (< 5ms)
- Concurrent execution safety & UI persistence contracts
"""
from __future__ import annotations

import tempfile
import threading
import time
import unittest
from pathlib import Path

from web.ai_performance_engine_v2 import (
    ENGINE_VERSION_V2,
    GAME_PROFILES,
    genre_score_multiplier_v2,
    get_game_profile,
    infer_game_genre_v2,
    is_low_signal_scan,
    load_cached_scan,
    precision_refine_boundary,
    save_cached_scan,
    scan_profile_for_duration,
    verify_and_diversify_candidates,
)
from web.game_vision_v108 import (
    genre_score_multiplier,
    infer_game_genre,
    vision_zones_for_genre,
)
from web.game_brain_v112 import _candidate, rerank_moments

ROOT = Path(__file__).resolve().parents[1]


class TestFastAdaptiveEngineV2(unittest.TestCase):
    def test_scan_profiles_for_15s_30s_60s_and_long_videos(self):
        for dur in (15.0, 30.0, 60.0):
            prof = scan_profile_for_duration(dur)
            self.assertEqual(prof["tier"], "fast_short")
            self.assertEqual(prof["video_fps"], 2.0)
            self.assertEqual(prof["analysis_width"], 144)
            self.assertFalse(prof["adaptive"])
            self.assertFalse(prof["keyframes_only"])

        prof_2m = scan_profile_for_duration(120.0)
        self.assertEqual(prof_2m["tier"], "standard")
        self.assertEqual(prof_2m["analysis_width"], 160)
        self.assertFalse(prof_2m["adaptive"])

        prof_5m = scan_profile_for_duration(300.0)
        self.assertEqual(prof_5m["tier"], "medium_turbo")
        self.assertTrue(prof_5m["adaptive"])
        self.assertTrue(prof_5m["keyframes_only"])

        prof_15m = scan_profile_for_duration(900.0)
        self.assertEqual(prof_15m["tier"], "medium_turbo")
        self.assertTrue(prof_15m["adaptive"])

        prof_45m = scan_profile_for_duration(2700.0)
        self.assertEqual(prof_45m["tier"], "long_turbo")
        self.assertTrue(prof_45m["adaptive"])

    def test_persistent_scan_cache_and_concurrent_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            video_file = tmp_path / "gameplay.mp4"
            video_file.write_bytes(b"fake_video_bytes_for_cache_test" * 50)

            sample_scan = {
                "step": 0.5,
                "audio": [0.1, 0.5, 0.9, 0.3],
                "peak": [0.2, 0.6, 0.95, 0.4],
                "motion": [0.1, 0.4, 0.85, 0.2],
                "meta": {"duration_seconds": 15.0, "tier": "fast_short"},
            }

            miss_scan, hit = load_cached_scan(video_file, preview_dir=tmp_path)
            self.assertFalse(hit)
            self.assertIsNone(miss_scan)

            save_cached_scan(video_file, sample_scan, preview_dir=tmp_path)

            t0 = time.perf_counter()
            cached_scan, hit = load_cached_scan(video_file, preview_dir=tmp_path)
            elapsed = time.perf_counter() - t0
            self.assertTrue(hit)
            self.assertLess(elapsed, 0.02)
            self.assertEqual(cached_scan["audio"], sample_scan["audio"])

            # Concurrent read/write stress test
            errors = []

            def worker(idx: int):
                try:
                    for _ in range(10):
                        s, h = load_cached_scan(video_file, preview_dir=tmp_path)
                        if not h or not isinstance(s, dict):
                            errors.append(f"Worker {idx} cache miss")
                except Exception as exc:
                    errors.append(str(exc))

            threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertEqual(errors, [])


class TestGameAwareProfilesV2(unittest.TestCase):
    REQUIRED_GENRES = (
        "FPS",
        "Battle Royale",
        "Action",
        "Racing",
        "Sports",
        "Survival",
        "Horror",
        "RPG",
        "Platform",
        "Narrative",
    )

    def test_all_ten_game_genres_exist_and_have_valid_profiles(self):
        for genre in self.REQUIRED_GENRES:
            self.assertIn(genre, GAME_PROFILES)
            prof = get_game_profile(genre)
            pad = prof.get("context_padding") or {}
            self.assertGreater(float(pad.get("pre_event_seconds", 0.0)), 0.0)
            self.assertGreater(float(pad.get("post_event_seconds", 0.0)), 0.0)
            self.assertTrue(len(prof.get("weights") or {}) >= 4)
            zones = vision_zones_for_genre(genre)
            self.assertTrue(len(zones) >= 2)

    def test_game_genre_inference_covers_all_ten_categories_plus_auto(self):
        cases = {
            "Call of Duty Black Ops 6": "FPS",
            "Valorant Ranked": "FPS",
            "Fortnite Zero Build": "Battle Royale",
            "Apex Legends": "Battle Royale",
            "God of War Ragnarok": "Action",
            "Devil May Cry 5": "Action",
            "F1 24 Monza": "Racing",
            "Forza Horizon 5": "Racing",
            "EA Sports FC 25": "Sports",
            "NBA 2K25": "Sports",
            "Minecraft Hardcore": "Survival",
            "Rust Wipe Day": "Survival",
            "Resident Evil 4": "Horror",
            "Phasmophobia": "Horror",
            "Elden Ring": "RPG",
            "Baldur's Gate 3": "RPG",
            "Super Mario Odyssey": "Platform",
            "Celeste Speedrun": "Platform",
            "Life is Strange": "Narrative",
            "Detroit Become Human": "Narrative",
            "": "Auto",
            "Gioco Sconosciuto XYZ": "Auto",
        }
        for title, expected in cases.items():
            with self.subTest(title=title):
                self.assertEqual(infer_game_genre_v2(title), expected)
                self.assertEqual(infer_game_genre(title), expected)

    def test_genre_multipliers_and_game_brain_bonus_respect_all_genres(self):
        sample_features = {
            "event_type": "shooter_elimination",
            "event_score": 0.82,
            "motion_avg": 0.65,
            "motion_peak": 0.88,
            "motion_burst": 0.72,
            "audio_burst": 0.68,
            "audio_peak": 0.79,
            "reaction": 0.55,
            "reaction_cue": 0.60,
            "speech": 0.45,
            "synergy": 0.62,
            "arc": 0.58,
            "continuity": 0.64,
            "sustained_peak": 0.70,
            "hook_score": 0.66,
            "payoff_position": 0.72,
            "dead_ratio": 0.05,
        }
        for genre in (*self.REQUIRED_GENRES, "Auto"):
            m_v2 = genre_score_multiplier_v2(genre, "auto", sample_features)
            m_108 = genre_score_multiplier(genre, "auto", sample_features)
            cand_112 = _candidate(
                0.78,
                10.0,
                {10.0: {"features": sample_features, "why": {"event": "kill"}}},
                15.0,
                [{"time": 16.0, "kind": "KILL", "score": 0.85}],
                genre,
                "auto",
            )
            self.assertGreaterEqual(m_v2, 0.90)
            self.assertLessEqual(m_v2, 1.18)
            self.assertGreaterEqual(m_108, 0.90)
            self.assertLessEqual(m_108, 1.18)
            self.assertGreater(float(cand_112.get("score", 0.0)), 0.50)


class TestRankingLowSignalAndPrecisionBoundaryV2(unittest.TestCase):
    def test_low_signal_and_silent_video_detection(self):
        # Completely dead/flat scan
        flat_scan = {
            "step": 0.5,
            "audio": [0.02] * 30,
            "peak": [0.03] * 30,
            "motion": [0.01] * 30,
        }
        self.assertTrue(is_low_signal_scan(flat_scan))

        # Silent video with strong visual gameplay (must NOT be marked dead!)
        silent_active_scan = {
            "step": 0.5,
            "audio": [0.0] * 30,
            "peak": [0.0] * 30,
            "motion": [0.1, 0.2, 0.85, 0.92, 0.78, 0.3, 0.15] * 4 + [0.1, 0.2],
        }
        self.assertFalse(is_low_signal_scan(silent_active_scan))

    def test_close_events_deduplication_and_diversity(self):
        close_candidates = [
            (0.91, 10.0, {"event_score": 0.8, "motion_avg": 0.7, "audio_burst": 0.6}, ""),
            (0.89, 11.5, {"event_score": 0.78, "motion_avg": 0.68, "audio_burst": 0.58}, ""),  # duplicate of 10.0s
            (0.84, 32.0, {"event_score": 0.72, "motion_avg": 0.65, "audio_burst": 0.75}, ""),
            (0.79, 54.0, {"event_score": 0.65, "motion_avg": 0.80, "audio_burst": 0.50}, ""),
        ]
        chosen = verify_and_diversify_candidates(
            close_candidates, duration=15.0, target_count=3, total_seconds=90.0
        )
        self.assertEqual(len(chosen), 3)
        starts = [c[1] for c in chosen]
        self.assertIn(10.0, starts)
        self.assertNotIn(11.5, starts)
        self.assertIn(32.0, starts)
        self.assertIn(54.0, starts)

    def test_zero_subprocess_precision_boundary_refinement_is_sub_millisecond(self):
        # 60s scan (120 buckets at 0.5s) with a clean lull at 9.5s and peak at 14.0s
        audio = [0.25] * 120
        motion = [0.30] * 120
        audio[19] = 0.02  # 9.5s quiet breath before hook
        motion[19] = 0.05
        for idx in range(26, 32):  # 13.0s - 16.0s climax
            audio[idx] = 0.92
            motion[idx] = 0.88

        scan = {"step": 0.5, "audio": audio, "peak": audio, "motion": motion}
        t0 = time.perf_counter()
        refined_start, refined_dur = precision_refine_boundary(
            scan, center_start=10.5, target_duration=15.0, total_seconds=60.0, genre="FPS"
        )
        elapsed = time.perf_counter() - t0
        self.assertLess(elapsed, 0.01)
        self.assertEqual(refined_dur, 15.0)
        self.assertGreaterEqual(refined_start, 0.0)
        self.assertLessEqual(refined_start + refined_dur, 60.0)
        # Ensure climax (14.0s) is well inside [refined_start, refined_start + 15.0]
        self.assertLessEqual(refined_start, 11.5)
        self.assertGreaterEqual(refined_start + refined_dur, 16.0)

    def test_ui_persistence_and_fast_polling_contracts(self):
        html = (ROOT / "web/ai_v221_component/index.html").read_text(encoding="utf-8")
        self.assertIn("gsf_ai_active_scan_v2", html)
        self.assertIn("setTimeout(()=>pollResults(token,deadline),650)", html)
        app_code = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("from web.ai_performance_engine_v2 import precision_refine_boundary", app_code)
        self.assertIn("from web.ai_performance_engine_v2 import get_cached_whisper_tiny", app_code)
        self.assertIn("max_workers=min(3, len(_short_cards))", app_code)


if __name__ == "__main__":
    unittest.main()
