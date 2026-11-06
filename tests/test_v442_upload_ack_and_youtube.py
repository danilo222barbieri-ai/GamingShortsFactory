"""V442: an upload ACK belongs to one upload, and YouTube errors are explicit.

Runs the real companion ``Handler`` in-process (boto3 stubbed, temporary
runtime root, real ffmpeg-generated media) and mocks only Google's API.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import types
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
sys.path.insert(0, str(ROOT))

for name in ("botocore", "botocore.config", "botocore.exceptions", "boto3", "boto3.s3", "boto3.s3.transfer"):
    sys.modules.setdefault(name, types.ModuleType(name))
sys.modules["botocore.config"].Config = getattr(sys.modules["botocore.config"], "Config", MagicMock())
sys.modules["botocore.exceptions"].ClientError = getattr(sys.modules["botocore.exceptions"], "ClientError", Exception)
sys.modules["boto3.s3.transfer"].TransferConfig = getattr(sys.modules["boto3.s3.transfer"], "TransferConfig", MagicMock())

import web.direct_upload_server as dus  # noqa: E402

HOME = (ROOT / "web/home_v154_component/index.html").read_text(encoding="utf-8")


def _make_video(path, seconds=2):
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"testsrc=size=160x284:rate=10:duration={seconds}",
         "-pix_fmt", "yuv420p", str(path)],
        check=True,
    )


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires ffmpeg")
class UploadAckFence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._root_patch = patch.object(dus, "ROOT", self.root)
        self._root_patch.start()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), dus.Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.sid = "sidv442test0001"
        self.media = self.root / "sessions" / self.sid / "media"
        self.media.mkdir(parents=True)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self._root_patch.stop()
        self.tmp.cleanup()

    def _save(self, payload):
        req = urllib.request.Request(
            self.base + "/projects/save-uploaded-source", data=json.dumps(payload).encode(), method="POST",
            headers={"Content-Type": "application/json", "X-GSF-Session-ID": self.sid},
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read() or b"{}")

    def _marker(self, upload_id, path):
        (self.media / ".direct_upload_ready.json").write_text(json.dumps({
            "path": str(path), "name": "clip.mp4", "size": path.stat().st_size,
            "upload_id": upload_id, "completed_at": 1, "storage": "direct_fallback", "duration": 2.0,
        }))

    def test_missing_upload_id_is_rejected(self):
        status, body = self._save({"name": "clip.mp4", "size": 10})
        self.assertEqual(status, 400)
        self.assertFalse(body["ok"])

    def test_previous_videos_marker_is_never_an_ack_for_a_new_upload(self):
        old = self.media / "source_direct_old_aaaaaaaa.mp4"
        _make_video(old)
        self._marker("aaaaaaaa", old)
        status, body = self._save({"name": "new.mp4", "size": old.stat().st_size, "upload_id": "bbbbbbbb"})
        self.assertEqual(status, 409)
        self.assertFalse(body["ok"])

    def test_matching_upload_returns_its_id_size_and_verified_duration(self):
        src = self.media / "source_direct_clip_cccccccc.mp4"
        _make_video(src, seconds=3)
        self._marker("cccccccc", src)
        status, body = self._save({"name": "clip.mp4", "size": src.stat().st_size, "upload_id": "cccccccc"})
        self.assertEqual(status, 200, body)
        self.assertTrue(body["ok"])
        self.assertEqual(body["upload_id"], "cccccccc")
        self.assertEqual(body["size"], src.stat().st_size)
        self.assertGreater(body["duration"], 0)

    def test_size_mismatch_is_rejected(self):
        src = self.media / "source_direct_clip_dddddddd.mp4"
        _make_video(src)
        self._marker("dddddddd", src)
        status, _body = self._save({"name": "clip.mp4", "size": src.stat().st_size + 1, "upload_id": "dddddddd"})
        self.assertEqual(status, 409)


class UploadAckClientContract(unittest.TestCase):
    def test_client_requires_server_echo_of_upload_and_size(self):
        fin = HOME.split("async function executeProjectFinalization(", 1)[1].split("// Tapping circle", 1)[0]
        self.assertIn('String(saveJson.upload_id||"")!==String(uploadId)', fin)
        self.assertIn("Number(saveJson.size||0)!==Number(file.size)", fin)

    def test_recovery_retry_uses_the_server_upload_id(self):
        self.assertIn("activeUploadSession.id=verifiedUploadId", HOME)

    def test_transfer_is_recoverable_only_after_finalization(self):
        bucket = HOME.split("async function bucketUpload(", 1)[1].split("function chunkPut(", 1)[0]
        self.assertIn("if(sr.ok&&st.ready){if(activeUploadSession)activeUploadSession.transferDone=true;return init.upload_id}", bucket)


def _resp(payload, status=200):
    r = MagicMock()
    r.__enter__.return_value = r
    r.read.return_value = json.dumps(payload).encode()
    r.status = status
    return r


def _http_error(code):
    return urllib.error.HTTPError("https://www.googleapis.com", code, "err", {}, None)


class YouTubeContentErrors(unittest.TestCase):
    TOKEN = {"access_token": "old-token"}

    @patch.object(dus, "_youtube_access_token")
    @patch.object(dus.urllib.request, "urlopen")
    def test_genuine_401_refreshes_once_then_succeeds(self, urlopen, refresh):
        refresh.return_value = {"access_token": "new-token"}
        urlopen.side_effect = [_http_error(401), _resp({"items": []})]
        data = dus._youtube_content_request("sid", "https://example/channels", self.TOKEN)
        self.assertEqual(data, {"items": []})
        refresh.assert_called_once_with("sid", force_refresh=True)
        sent = urlopen.call_args_list[1][0][0]
        self.assertEqual(sent.get_header("Authorization"), "Bearer new-token")

    @patch.object(dus, "_youtube_access_token")
    @patch.object(dus.urllib.request, "urlopen")
    def test_failed_refresh_is_an_explicit_reconnect_error(self, urlopen, refresh):
        refresh.return_value = {"error": "invalid_grant"}
        urlopen.side_effect = [_http_error(401)]
        with self.assertRaises(dus._YouTubeContentError) as ctx:
            dus._youtube_content_request("sid", "https://example/channels", self.TOKEN)
        self.assertEqual(ctx.exception.status, 401)
        self.assertIn("ricollega", str(ctx.exception).lower())

    @patch.object(dus.urllib.request, "urlopen")
    def test_quota_rate_limit_and_outage_are_distinguished(self, urlopen):
        for code, status in ((403, 403), (429, 429), (500, 503)):
            with self.subTest(code=code):
                urlopen.side_effect = [_http_error(code)]
                with self.assertRaises(dus._YouTubeContentError) as ctx:
                    dus._youtube_content_request("sid", "https://example/x", self.TOKEN)
                self.assertEqual(ctx.exception.status, status)

    @patch.object(dus, "_youtube_analytics_token", return_value={"access_token": "t"})
    @patch.object(dus.urllib.request, "urlopen")
    def test_live_filter_lists_live_broadcasts_as_not_importable(self, urlopen, _token):
        channel = {"items": [{"id": "UC1", "snippet": {"title": "C"}, "statistics": {},
                              "contentDetails": {"relatedPlaylists": {"uploads": "UU1"}}}]}
        live = {"items": [{"id": {"videoId": "live1"}, "snippet": {"title": "Diretta", "thumbnails": {}}}]}
        urlopen.side_effect = [_resp(channel), _resp(live)]
        res = dus._youtube_content("sid", kind="live")
        self.assertEqual(res["type"], "live")
        self.assertEqual([r["id"] for r in res["data"]], ["live1"])
        self.assertTrue(res["data"][0]["is_live"])
        self.assertFalse(res["data"][0]["can_import"])
        self.assertIn("eventType=live", urlopen.call_args_list[1][0][0].full_url)

    def test_unknown_filter_is_rejected(self):
        with self.assertRaises(ValueError):
            dus._youtube_content("sid", kind="everything")


if __name__ == "__main__":
    unittest.main()
