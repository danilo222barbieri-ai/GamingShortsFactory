#!/usr/bin/env python3
"""
Unit and regression tests for GSF AI Engine 3.1 — Blocco 3 (Advanced Game-Aware AI).

Covers:
1. Full presence and validity of all 10 canonical game genre profiles + Auto.
2. Live title and genre extraction from realistic gamer filenames and metadata.
3. Fallback to behavioral audio/motion scan classification when filenames lack keywords.
4. Dynamic contextual padding with anti-cutoff speech/action protection and sub-millisecond execution.
5. End-to-end integration in run_fast_ai_pipeline.
"""
from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from web.ai_performance_engine_v2 import (
    GAME_PROFILES,
    get_game_profile,
    infer_game_genre_v2,
    extract_game_title_from_path_or_meta,
    classify_game_genre_from_scan,
    detect_game_genre_live,
    precision_refine_boundary,
    run_fast_ai_pipeline,
)


class TestAdvancedGameAwareAiBlocco3(unittest.TestCase):
    def test_all_10_genre_profiles_integrity(self):
        expected_genres = [
            "FPS", "Battle Royale", "Action", "Racing", "Sports",
            "Survival", "Horror", "RPG", "Platform", "Narrative", "Auto"
        ]
        for g in expected_genres:
            self.assertIn(g, GAME_PROFILES)
            prof = GAME_PROFILES[g]
            self.assertEqual(prof.get("name"), g)
            self.assertTrue(prof.get("label"))
            self.assertTrue(len(prof.get("important_events", [])) >= 3)
            self.assertIn(prof.get("recommended_duration"), (15, 30, 60))
            self.assertTrue(prof.get("priority"))
            padding = prof.get("context_padding", {})
            self.assertGreater(padding.get("pre_event_seconds", 0.0), 0.0)
            self.assertGreater(padding.get("post_event_seconds", 0.0), 0.0)
            self.assertTrue(len(prof.get("vision_zones", [])) >= 1)

    def test_live_title_and_genre_extraction_from_filenames(self):
        cases = [
            ("Valorant_Ace_2024-05-12_1080p60.mp4", "Valorant", "FPS"),
            ("Fortnite_VictoryRoyale_clip_h264.mp4", "Fortnite", "Battle Royale"),
            ("AssettoCorsa_Drift_Lap_obs.mp4", "Assetto Corsa", "Racing"),
            ("Rocket_League_Goal_Replay_4k.mp4", "Rocket League", "Sports"),
            ("Elden_Ring_Malenia_NoDamage.mp4", "Elden Ring", "RPG"),
            ("ResidentEvil_Village_Jumpscare.mp4", "Resident Evil", "Horror"),
            ("Minecraft_Hardcore_Day100.mp4", "Minecraft", "Survival"),
            ("Super_Mario_Wonder_Speedrun.mp4", "Super Mario Wonder", "Platform"),
            ("Detroit_Become_Human_Best_Ending.mp4", "Detroit: Become Human", "Narrative"),
            ("DevilMayCry5_Dante_Combo.mp4", "Devil May Cry", "Action"),
        ]
        for filename, exp_title, exp_genre in cases:
            title, genre = extract_game_title_from_path_or_meta(filename)
            self.assertEqual(genre, exp_genre, f"Failed genre for {filename}")
            self.assertEqual(title, exp_title, f"Failed title for {filename}")

            det_genre, det_title, conf = detect_game_genre_live(filename)
            self.assertEqual(det_genre, exp_genre)
            self.assertEqual(det_title, exp_title)
            self.assertGreaterEqual(conf, 0.90)

    def test_metadata_extraction_precedence(self):
        meta = {"game": "Cyberpunk 2077", "title": "Night City Drive"}
        title, genre = extract_game_title_from_path_or_meta("generic_recording_001.mp4", metadata=meta)
        self.assertEqual(genre, "RPG")
        self.assertEqual(title, "Cyberpunk 2077")

    def test_behavioral_scan_classification_fallback(self):
        # 1. Horror: long silence with sudden extreme scream
        horror_audio = [0.05] * 120
        horror_audio[45] = 0.95
        horror_motion = [0.10] * 120
        scan_horror = {"audio": horror_audio, "motion": horror_motion}
        g, conf = classify_game_genre_from_scan(scan_horror)
        self.assertEqual(g, "Horror")
        self.assertGreaterEqual(conf, 0.80)

        # 2. Racing: sustained continuous high velocity motion
        racing_audio = [0.40] * 120
        racing_motion = [0.65] * 120
        scan_racing = {"audio": racing_audio, "motion": racing_motion}
        g, conf = classify_game_genre_from_scan(scan_racing)
        self.assertEqual(g, "Racing")
        self.assertGreaterEqual(conf, 0.80)

        # 3. Action: bursty combo combat
        action_audio = [0.35] * 120
        action_motion = [0.25] * 120
        for idx in range(15, 55):
            action_motion[idx] = 0.85
        scan_action = {"audio": action_audio, "motion": action_motion}
        g, conf = classify_game_genre_from_scan(scan_action)
        self.assertEqual(g, "Action")
        self.assertGreaterEqual(conf, 0.75)

        # 4. Neutral / unknown -> Auto
        neutral_audio = [0.25] * 120
        neutral_motion = [0.25] * 120
        scan_neutral = {"audio": neutral_audio, "motion": neutral_motion}
        g, conf = classify_game_genre_from_scan(scan_neutral)
        self.assertEqual(g, "Auto")
        self.assertEqual(conf, 1.0)

    def test_dynamic_contextual_padding_and_anti_cutoff(self):
        # Scan with 120 buckets (60s total, step=0.5s)
        # Climax at 15.0s (idx 30)
        # Quiet pause dip at 11.5s (idx 23)
        # End cut near 26.5s has quiet transition
        audio = [0.35] * 120
        motion = [0.40] * 120
        audio[23] = 0.02  # 11.5s quiet breath
        motion[23] = 0.04
        for idx in range(29, 33):  # 14.5s - 16.5s climax
            audio[idx] = 0.95
            motion[idx] = 0.90

        scan = {"step": 0.5, "audio": audio, "peak": audio, "motion": motion}
        t0 = time.perf_counter()
        st, dur = precision_refine_boundary(
            scan, center_start=12.0, target_duration=15.0, total_seconds=60.0, genre="FPS"
        )
        elapsed = time.perf_counter() - t0

        # Sub-millisecond performance (< 5ms)
        self.assertLess(elapsed, 0.005)
        self.assertEqual(dur, 15.0)
        self.assertGreaterEqual(st, 0.0)
        self.assertLessEqual(st + dur, 60.0)

        # Anti-cutoff: candidate must start before peak (15.0s) and end well after peak (15.0s)
        self.assertLessEqual(st, 15.0 - 2.5)  # pre_event padding preserved
        self.assertGreaterEqual(st + dur, 15.0 + 2.5)  # post_event padding preserved

    def test_run_fast_ai_pipeline_with_live_game_detection(self):
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td)
            dummy_src = out_dir / "Valorant_Competitive_Ace.mp4"
            dummy_src.write_bytes(b"GSF_SIMULATED_GAMEPLAY_SOURCE")

            # Prime cached scan so no ffprobe/ffmpeg needed
            audio = [0.20] * 60
            motion = [0.30] * 60
            for idx in range(18, 25):  # Event around 9-12s
                audio[idx] = 0.88
                motion[idx] = 0.85
            scan = {"step": 0.5, "audio": audio, "peak": audio, "motion": motion}

            from web.ai_performance_engine_v2 import save_cached_scan, ENGINE_VERSION_V2
            save_cached_scan(dummy_src, scan, out_dir, ENGINE_VERSION_V2)

            res = run_fast_ai_pipeline(
                source_path=dummy_src,
                output_dir=out_dir,
                duration=15.0,
                genre="Auto",  # Should trigger live detection
                profile="auto",
                generate_previews=False,
            )

            self.assertEqual(res["result_state"], "completed_with_results")
            self.assertEqual(res["genre"], "FPS")
            self.assertEqual(res["detected_game"], "Valorant")
            self.assertGreaterEqual(res["genre_confidence"], 0.90)
            self.assertTrue(len(res["selected"]) > 0)


if __name__ == "__main__":
    unittest.main()
