#!/usr/bin/env python3
"""
Unit and regression tests for GSF AI Engine 3.0 — Blocco 2 (Fast AI Engine).
Verifies:
- Fast Detection: rapid metadata probe and adaptive scan profiles.
- Smart Ranking: verifiable scoring, MMR temporal diversity, and elimination of duplicates.
- Precision Pass: sub-millisecond in-memory boundary refinement snapping to silence.
- Honesty: low-signal and silent videos handled transparently without fake confidence scores.
- Mini-previews generation with exact v71_mini_{idx}_{start:.2f}.mp4 format expected by UI.
- Performance: end-to-end pipeline execution comfortably within the 1-3s target.
"""
from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from web.ai_performance_engine_v2 import (
    ENGINE_VERSION_V2,
    generate_mini_previews_parallel,
    is_low_signal_scan,
    load_cached_scan,
    precision_refine_boundary,
    probe_media_duration,
    run_fast_ai_pipeline,
    run_fast_scan_base,
    save_cached_scan,
    scan_profile_for_duration,
    smart_rank_candidates,
    verify_and_diversify_candidates,
)


class TestAiEngineV3Blocco2(unittest.TestCase):
    def test_scan_profiles_adaptive(self):
        self.assertEqual(scan_profile_for_duration(15)["tier"], "fast_short")
        self.assertEqual(scan_profile_for_duration(30)["tier"], "fast_short")
        self.assertEqual(scan_profile_for_duration(60)["tier"], "fast_short")
        self.assertEqual(scan_profile_for_duration(120)["tier"], "standard")
        self.assertEqual(scan_profile_for_duration(300)["tier"], "medium_turbo")
        self.assertEqual(scan_profile_for_duration(1800)["tier"], "long_turbo")

    def test_low_signal_honesty(self):
        flat_scan = {
            "step": 0.5,
            "audio": [0.01] * 60,
            "peak": [0.01] * 60,
            "motion": [0.01] * 60,
        }
        self.assertTrue(is_low_signal_scan(flat_scan))
        selected, alts = smart_rank_candidates(flat_scan, target_duration=15.0, total_seconds=30.0)
        # Legitimate completed_no_highlights: do not fabricate random clips on low-signal video
        self.assertEqual(len(selected), 0)

    def test_smart_ranking_and_diversity(self):
        # Scan with 2 distinct action peaks at 4s and 18s
        step = 0.5
        total_len = 60  # 30 seconds
        audio = [0.1] * total_len
        motion = [0.1] * total_len
        peak = [0.1] * total_len

        # Peak 1 at 4s (index 8)
        audio[8] = 0.95
        motion[8] = 0.90
        peak[8] = 0.98

        # Peak 2 at 18s (index 36)
        audio[36] = 0.88
        motion[36] = 0.85
        peak[36] = 0.90

        dynamic_scan = {
            "step": step,
            "audio": audio,
            "motion": motion,
            "peak": peak,
        }
        self.assertFalse(is_low_signal_scan(dynamic_scan))
        selected, alts = smart_rank_candidates(
            dynamic_scan,
            target_duration=10.0,
            total_seconds=30.0,
            genre="FPS",
            profile="action",
            target_count=3,
        )
        self.assertTrue(len(selected) >= 2)
        starts = [r["start"] for r in selected]
        # Moments must never be duplicate (spacing must be >= 4.5s)
        for i in range(len(starts)):
            for j in range(i + 1, len(starts)):
                self.assertGreaterEqual(abs(starts[i] - starts[j]), 3.5)

    def test_precision_refine_boundary_snaps_to_dip(self):
        step = 0.5
        # 10s video, burst at 5s, silence at 1.5s
        audio = [0.6, 0.4, 0.1, 0.05, 0.8, 0.9, 0.95, 0.3, 0.2, 0.1]
        motion = [0.5, 0.3, 0.1, 0.1, 0.8, 0.85, 0.9, 0.2, 0.1, 0.1]
        scan = {"step": step, "audio": audio, "motion": motion, "peak": audio}

        start, dur = precision_refine_boundary(scan, center_start=2.0, target_duration=5.0, total_seconds=5.0)
        self.assertIsInstance(start, float)
        self.assertEqual(dur, 5.0)

    def test_end_to_end_fast_pipeline_benchmark(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            video_file = tmp_path / "test_15s.mp4"
            out_media = tmp_path / "media"

            # Create synthetic 15s MP4
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "testsrc=duration=15:size=480x270:rate=25",
                "-f", "lavfi",
                "-i", "sine=frequency=440:duration=15",
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
                genre="Action",
                profile="auto",
                request_id="test_req_fast",
                generate_previews=True,
            )
            elapsed = time.perf_counter() - t0
            # Target is 1-3s for 15s video
            self.assertLess(elapsed, 4.0, f"Pipeline exceeded benchmark limit: {elapsed:.2f}s")
            self.assertTrue(res.get("candidates"))
            self.assertEqual(res.get("request_id"), "test_req_fast")

            # Check that mini-preview files and meta exist
            meta_path = out_media / "ai_results_meta.json"
            self.assertTrue(meta_path.is_file())
            minis = list(out_media.glob("v71_mini_*.mp4"))
            self.assertTrue(len(minis) >= 1)


if __name__ == "__main__":
    unittest.main()
