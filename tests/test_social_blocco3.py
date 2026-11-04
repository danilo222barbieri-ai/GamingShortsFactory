import io
import json
import os
import sys
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
sys.path.insert(0, str(ROOT))

from cryptography.fernet import Fernet
if not os.environ.get("GSF_DATA_ENCRYPTION_KEY"):
    os.environ["GSF_DATA_ENCRYPTION_KEY"] = Fernet.generate_key().decode()

if "botocore" not in sys.modules:
    botocore = types.ModuleType("botocore")
    botocore_config = types.ModuleType("botocore.config")
    botocore_config.Config = MagicMock()
    botocore_exceptions = types.ModuleType("botocore.exceptions")
    botocore_exceptions.ClientError = Exception
    sys.modules["botocore"] = botocore
    sys.modules["botocore.config"] = botocore_config
    sys.modules["botocore.exceptions"] = botocore_exceptions

if "boto3" not in sys.modules:
    boto3 = types.ModuleType("boto3")
    boto3_s3 = types.ModuleType("boto3.s3")
    boto3_s3_transfer = types.ModuleType("boto3.s3.transfer")
    boto3_s3_transfer.TransferConfig = MagicMock()
    sys.modules["boto3"] = boto3
    sys.modules["boto3.s3"] = boto3_s3
    sys.modules["boto3.s3.transfer"] = boto3_s3_transfer

import direct_upload_server as server
import publish_multi_v413 as pm

class MockBucket:
    def __init__(self):
        self.store = {}
    def put_object(self, **kw):
        self.store[kw["Key"]] = kw["Body"]
    def get_object(self, **kw):
        k = kw["Key"]
        if k not in self.store:
            raise FileNotFoundError(k)
        return {"Body": io.BytesIO(self.store[k])}
    def delete_object(self, **kw):
        self.store.pop(kw["Key"], None)

class TestBlocco3MultiPublish(unittest.TestCase):
    def setUp(self):
        self.sid = "test_user_blocco3"
        self.session_dir = ROOT / "sessions" / self.sid / "social"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.bucket = MockBucket()
        server._bucket_enabled = lambda: True
        server._s3 = lambda: self.bucket

    def tearDown(self):
        for f in self.session_dir.glob("*"):
            try: f.unlink()
            except Exception: pass

    def test_preflight_checks_platforms_independently(self):
        """Preflight accurately reports statuses for each platform."""
        # 1. YouTube connected & valid
        server._youtube_user_save(self.sid, {
            "token": "yt_valid",
            "access_token": "yt_valid",
            "refresh_token": "yt_ref",
            "expires_at": time.time() + 3600,
            "channel_title": "Pro Gamer Channel",
            "needs_reauth": False,
        })
        # 2. Instagram expired
        server._instagram_user_save(self.sid, {
            "access_token": "ig_token",
            "ig_user_id": "123",
            "needs_reauth": True,
        })
        # 3. Facebook has no page selected
        server._social_connection_save(self.sid, "facebook", {
            "access_token": "fb_token",
            "facebook_user_id": "456",
            "pages": [],
            "selected_page_id": "",
            "selected_page_token": "",
        })

        pf = server._publish_preflight(self.sid, ["youtube", "instagram", "facebook"])
        checks = pf["checks"]

        self.assertTrue(checks["youtube"]["ready"])
        self.assertEqual(checks["youtube"]["status"], "ready")

        self.assertFalse(checks["instagram"]["ready"])
        self.assertEqual(checks["instagram"]["status"], "needs_reauth")

        self.assertFalse(checks["facebook"]["ready"])
        self.assertEqual(checks["facebook"]["status"], "no_page")

    def test_multi_platform_isolation_failure_does_not_abort_success(self):
        """When publishing simultaneously, failure on Facebook must not prevent YouTube from succeeding."""
        # Setup YouTube valid
        server._youtube_user_save(self.sid, {
            "token": "yt_valid",
            "access_token": "yt_valid",
            "refresh_token": "yt_ref",
            "expires_at": time.time() + 3600,
            "channel_title": "Pro Gamer Channel",
            "needs_reauth": False,
        })
        # Setup Facebook valid
        server._social_connection_save(self.sid, "facebook", {
            "access_token": "fb_token",
            "facebook_user_id": "456",
            "pages": [{"id": "p1", "name": "P1", "access_token": "t1"}],
            "selected_page_id": "p1",
            "selected_page_token": "t1",
            "needs_reauth": False,
        })

        job = {
            "id": "job_multi_test",
            "state": "running",
            "created_at": time.time(),
            "updated_at": time.time(),
            "privacy": "public",
            "results": {
                "youtube": {"status": "queued", "url": "", "error": ""},
                "facebook": {"status": "queued", "url": "", "error": ""},
            }
        }
        request = {
            "platforms": ["youtube", "facebook"],
            "privacy": "public",
            "plans": {
                "youtube": {"title": "YT Title", "caption": "YT Desc"},
                "facebook": {"title": "FB Title", "caption": "FB Desc"},
            }
        }

        def mock_yt_upload(*args, **kwargs):
            return {"id": "yt_video_001", "url": "https://youtu.be/yt_video_001", "privacy": "public"}

        def mock_fb_post(*args, **kwargs):
            raise pm.PublishError("Facebook: permessi insufficienti per pubblicare sulla Pagina.", code="permission_denied")

        with patch("publish_multi_v413.youtube_upload", side_effect=mock_yt_upload), \
             patch("direct_upload_server._facebook_direct_post", side_effect=mock_fb_post):
            server._publish_run(self.sid, job, request, "/fake/video.mp4")

        self.assertEqual(job["results"]["youtube"]["status"], "done")
        self.assertEqual(job["results"]["youtube"]["content_id"], "yt_video_001")
        self.assertEqual(job["results"]["youtube"]["url"], "https://youtu.be/yt_video_001")

        self.assertEqual(job["results"]["facebook"]["status"], "error")
        self.assertEqual(job["results"]["facebook"]["error_code"], "permission_denied")
        self.assertIn("permessi insufficienti", job["results"]["facebook"]["error"])

    def test_idempotent_attempt_ids(self):
        """Each publishing job assigns a distinct idempotent attempt ID per platform."""
        fake_video = ROOT / "sessions" / self.sid / "final.mp4"
        fake_video.parent.mkdir(parents=True, exist_ok=True)
        fake_video.write_bytes(b"dummy mp4")

        server._publish_final_path = lambda s: fake_video

        # Setup valid connection for YouTube
        server._youtube_user_save(self.sid, {
            "token": "yt_valid",
            "access_token": "yt_valid",
            "expires_at": time.time() + 3600,
        })

        payload = {
            "platforms": ["youtube"],
            "privacy": "public",
            "shared": {
                "title": "Idempotency Test",
                "description": "Test",
            },
        }
        with patch("threading.Thread") as mock_thread:
            job = server._publish_start(self.sid, payload)
            attempt_id = job["results"]["youtube"]["attempt_id"]
            self.assertTrue(attempt_id.startswith(f"{job['id']}_youtube_"))

    def test_tiktok_remains_untouched(self):
        """Pipeline verification: TikTok routines are defined and isolated."""
        self.assertTrue(callable(server._tiktok_user_load))
        self.assertTrue(callable(server._tiktok_analytics_token))
        self.assertTrue(callable(pm.tiktok_direct_post))

if __name__ == "__main__":
    unittest.main()
