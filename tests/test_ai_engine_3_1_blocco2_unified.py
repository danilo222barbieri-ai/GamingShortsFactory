import unittest
import tempfile
import time
import subprocess
from pathlib import Path
from web.ai_performance_engine_v2 import (
    run_fast_ai_pipeline,
    load_cached_scan,
    save_cached_scan,
    smart_rank_candidates,
    is_low_signal_scan,
)
import web.ai_engines_v412 as v412


class TestAiEngine31Blocco2Unified(unittest.TestCase):
    """Test suite for Blocco 2: Fast AI Engine 3.1 Unified Pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.base_path = Path(cls.temp_dir.name)
        cls.action_video = cls.base_path / "action_test.mp4"
        cls.silent_video = cls.base_path / "silent_test.mp4"

        # Generate action test video (30s)
        cmd_action = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=duration=30:size=640x360:rate=25",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=30",
            "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "aac", "-b:a", "64k",
            str(cls.action_video)
        ]
        subprocess.run(cmd_action, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Generate silent flat video (20s)
        cmd_silent = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=640x360:d=20",
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "20",
            "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "aac", "-b:a", "64k",
            str(cls.silent_video)
        ]
        subprocess.run(cmd_silent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_01_action_video_fast_analysis_cold_and_warm(self):
        out_dir = self.base_path / "media_action"
        out_dir.mkdir(parents=True, exist_ok=True)

        # Cold run
        t0 = time.perf_counter()
        res_cold = run_fast_ai_pipeline(
            source_path=self.action_video,
            output_dir=out_dir,
            duration=15.0,
            genre="FPS",
            profile="auto",
            request_id="req_cold",
            sid="session_cold",
            generate_previews=True,
        )
        t_cold = time.perf_counter() - t0
        self.assertLess(t_cold, 3.5, f"Cold run exceeded 3.5s: took {t_cold:.3f}s")
        self.assertEqual(res_cold.get("result_state"), "completed_with_results")
        self.assertEqual(len(res_cold.get("selected", [])), 3)  # Top 3 ranked moments selected

        # Warm run (cached scan)
        t0 = time.perf_counter()
        res_warm = run_fast_ai_pipeline(
            source_path=self.action_video,
            output_dir=out_dir,
            duration=15.0,
            genre="FPS",
            profile="auto",
            request_id="req_warm",
            sid="session_cold",
            generate_previews=False,
        )
        t_warm = time.perf_counter() - t0
        self.assertLess(t_warm, 0.25, f"Warm run exceeded 0.25s: took {t_warm:.3f}s")
        self.assertEqual(res_warm.get("result_state"), "completed_with_results")

    def test_02_silent_video_completed_no_highlights(self):
        out_dir = self.base_path / "media_silent"
        out_dir.mkdir(parents=True, exist_ok=True)

        res_silent = run_fast_ai_pipeline(
            source_path=self.silent_video,
            output_dir=out_dir,
            duration=15.0,
            genre="Auto",
            profile="auto",
            request_id="req_silent",
            sid="session_silent",
            generate_previews=True,
        )
        self.assertEqual(res_silent.get("result_state"), "completed_no_highlights")
        self.assertEqual(len(res_silent.get("selected", [])), 0)

        meta = v412.read_results_meta(out_dir)
        self.assertIsNotNone(meta)
        merged = v412.merge_results(meta, v412.mini_files(out_dir), lambda x: f"/media/{x}")
        self.assertEqual(merged.get("status"), "completed_no_highlights")
        self.assertEqual(merged.get("count"), 0)

    def test_03_invalid_video_failed_state(self):
        out_dir = self.base_path / "media_invalid"
        out_dir.mkdir(parents=True, exist_ok=True)
        bad_video = self.base_path / "does_not_exist.mp4"

        try:
            res_bad = run_fast_ai_pipeline(
                source_path=bad_video,
                output_dir=out_dir,
                duration=15.0,
                genre="Auto",
                profile="auto",
                request_id="req_bad",
                sid="session_bad",
            )
            state = res_bad.get("result_state")
        except Exception:
            state = "failed"
        self.assertEqual(state, "failed")


if __name__ == "__main__":
    unittest.main()
