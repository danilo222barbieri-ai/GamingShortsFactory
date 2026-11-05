import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "web") not in sys.path:
    sys.path.insert(0, str(ROOT / "web"))

import ai_performance_engine_v2 as ape


class TestFastAIEngineMilestoneB(unittest.TestCase):
    def test_strict_three_states_and_fast_detection(self):
        # 1. Active gameplay scan -> completed_with_results with 3 candidates
        active_scan = {
            "step": 0.5,
            "audio": [0.2, 0.4, 0.8, 0.9, 0.6, 0.3, 0.2] * 20,
            "motion": [0.1, 0.3, 0.85, 0.7, 0.5, 0.2, 0.1] * 20,
            "peak": [0.3, 0.5, 0.95, 0.9, 0.7, 0.4, 0.2] * 20,
            "meta": {"tier": "short", "adaptive": False, "duration_seconds": 70.0},
        }
        selected, alternates = ape.smart_rank_candidates(
            active_scan,
            target_duration=15.0,
            total_seconds=70.0,
            genre="FPS",
            profile="action",
            target_count=3,
        )
        self.assertGreaterEqual(len(selected), 1)
        self.assertLessEqual(len(selected), 3)
        # Check boundary adherence
        for row in selected:
            self.assertGreaterEqual(row["start"], 0.0)
            self.assertLessEqual(row["start"] + row["duration"], 70.0 + 1e-3)
            self.assertIn("score", row)

        # 2. Silent/blank scan -> completed_no_highlights (0 candidates)
        silent_scan = {
            "step": 0.5,
            "audio": [0.0] * 40,
            "motion": [0.0] * 40,
            "peak": [0.0] * 40,
            "meta": {"tier": "short", "adaptive": False, "duration_seconds": 20.0},
        }
        self.assertTrue(ape.is_low_signal_scan(silent_scan))
        sel_silent, _ = ape.smart_rank_candidates(
            silent_scan,
            target_duration=15.0,
            total_seconds=20.0,
            genre="Auto",
            profile="auto",
        )
        self.assertEqual(len(sel_silent), 0)

    def test_app_routing_calls_run_fast_ai_pipeline_for_normal_gameplay(self):
        # Verify app.py syntax and routing logic for normal video (> requested duration)
        app_text = (ROOT / "app.py").read_text(encoding="utf-8")
        # Ensure the legacy 5-minute branch is restricted to _gsf_whole_source
        self.assertIn(
            "if _gsf_whole_source and (callable(globals().get(\"_gsf_ai_scan_cached\")) or callable(locals().get(\"_gsf_ai_scan_cached\"))):",
            app_text,
        )
        # Ensure run_fast_ai_pipeline is imported and called in the else block
        self.assertIn("from web.ai_performance_engine_v2 import run_fast_ai_pipeline", app_text)
        self.assertIn("_fast_res = run_fast_ai_pipeline(", app_text)

    def test_pipeline_execution_diagnostics(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir)
            dummy_video = out_dir / "gameplay.mp4"
            dummy_video.write_bytes(b"\x00" * 2048)

            mock_scan = {
                "step": 0.5,
                "audio": [0.2, 0.5, 0.9, 0.4] * 20,
                "motion": [0.1, 0.6, 0.8, 0.3] * 20,
                "peak": [0.3, 0.7, 0.95, 0.5] * 20,
                "meta": {"tier": "short", "adaptive": False, "duration_seconds": 40.0},
            }

            with patch("ai_performance_engine_v2.probe_media_duration", return_value=40.0), \
                 patch("ai_performance_engine_v2.load_cached_scan", return_value=(mock_scan, True)), \
                 patch("ai_performance_engine_v2.generate_mini_previews_parallel", return_value=["mini_1.mp4", "mini_2.mp4", "mini_3.mp4"]):

                res = ape.run_fast_ai_pipeline(
                    source_path=dummy_video,
                    output_dir=out_dir,
                    duration=15.0,
                    genre="Auto",
                    profile="auto",
                    request_id="req_test_1",
                    generate_previews=True,
                )

                self.assertEqual(res["result_state"], "completed_with_results")
                self.assertGreaterEqual(len(res["candidates"]), 1)
                self.assertIn("genre", res)
                self.assertIn("total_time", res)


if __name__ == "__main__":
    unittest.main()
