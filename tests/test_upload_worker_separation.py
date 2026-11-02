import unittest
from unittest.mock import patch, MagicMock
from gsf_core.ai_scan import (
    gsf_norm_series,
    gsf_ai_scan_profile_for_duration,
    gsf_interpolate_motion_points,
)
from gsf_core.render_client import (
    RenderJobRequest,
    is_worker_configured,
    get_worker_url,
    get_worker_token,
    dispatch_render_to_worker,
    get_render_job_status,
)


class TestUploadWorkerSeparation(unittest.TestCase):
    def test_norm_series(self):
        self.assertEqual(gsf_norm_series([]), [])
        norm = gsf_norm_series([10.0, 20.0, 30.0, 40.0, 50.0])
        self.assertEqual(len(norm), 5)
        self.assertGreaterEqual(min(norm), 0.0)
        self.assertLessEqual(max(norm), 1.0)

    def test_scan_profile(self):
        short_p = gsf_ai_scan_profile_for_duration(60.0)
        self.assertEqual(short_p["tier"], "standard")
        self.assertEqual(short_p["video_fps"], 2.0)

        long_p = gsf_ai_scan_profile_for_duration(3600.0)
        self.assertEqual(long_p["tier"], "long_turbo")
        self.assertTrue(long_p["adaptive"])

    def test_interpolate_points(self):
        points = {0: 0.0, 10: 1.0}
        interpolated = gsf_interpolate_motion_points(points, 11)
        self.assertEqual(len(interpolated), 11)
        self.assertEqual(interpolated[0], 0.0)
        self.assertEqual(interpolated[10], 1.0)
        self.assertAlmostEqual(interpolated[5], 0.5, places=2)

    def test_render_client_configuration(self):
        with patch.dict("os.environ", {"GSF_WORKER_URL": "https://worker.example.com", "GSF_WORKER_TOKEN": "secret"}):
            self.assertTrue(is_worker_configured())
            self.assertEqual(get_worker_url(), "https://worker.example.com")
            self.assertEqual(get_worker_token(), "secret")

    def test_render_dispatch_and_status(self):
        req = RenderJobRequest(
            job_id="test_job_1",
            session_id="test_sid",
            source_key="uploads/test.mp4",
            output_key="renders/test.mp4",
            cmd=["ffmpeg", "-i", "in.mp4", "out.mp4"],
        )

        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"ok": true, "queued": true, "job_id": "test_job_1"}'
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp):
            res = dispatch_render_to_worker(req, worker_url="https://worker.example.com")
            self.assertTrue(res.get("ok"))
            self.assertEqual(res.get("job_id"), "test_job_1")

        mock_status_resp = MagicMock()
        mock_status_resp.read.return_value = b'{"ok": true, "job": {"state": "completed", "job_id": "test_job_1"}}'
        mock_status_resp.__enter__.return_value = mock_status_resp

        with patch("urllib.request.urlopen", return_value=mock_status_resp):
            status = get_render_job_status("test_job_1", worker_url="https://worker.example.com")
            self.assertEqual(status.get("state"), "completed")


if __name__ == "__main__":
    unittest.main()
