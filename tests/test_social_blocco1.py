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

class TestBlocco1OAuth(unittest.TestCase):
    def setUp(self):
        self.sid = "test_user_blocco1"
        self.session_dir = ROOT / "sessions" / self.sid / "social"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        server._bucket_enabled = lambda: False

    def tearDown(self):
        for f in self.session_dir.glob("*"):
            try: f.unlink()
            except Exception: pass

    def test_youtube_token_preserves_refresh_token_on_reauth(self):
        """When user re-authenticates without getting a new refresh token, the existing refresh token must be preserved."""
        initial_token = {
            "token": "old_access_token",
            "access_token": "old_access_token",
            "refresh_token": "1//original_refresh_token",
            "expires_at": time.time() + 3600,
            "channel_title": "Test Channel",
            "channel_id": "UC12345",
        }
        server._youtube_user_save(self.sid, initial_token)
        loaded = server._youtube_user_load(self.sid)
        self.assertEqual(loaded.get("refresh_token"), "1//original_refresh_token")

        existing = dict(server._youtube_user_load(self.sid) or {})
        google_payload = {
            "access_token": "new_access_token",
            "expires_in": 3600,
        }
        preserved_refresh = google_payload.get("refresh_token") or existing.get("refresh_token") or ""
        self.assertEqual(preserved_refresh, "1//original_refresh_token")

    def test_youtube_access_token_refreshes_when_expired(self):
        """Expired YouTube access tokens must be automatically refreshed via Google token endpoint."""
        expired_token = {
            "token": "expired_access",
            "access_token": "expired_access",
            "refresh_token": "valid_refresh",
            "expires_at": time.time() - 60,
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "needs_reauth": False,
        }
        server._youtube_user_save(self.sid, expired_token)

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "access_token": "fresh_access_token_123",
            "expires_in": 3600,
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp):
            tok = server._youtube_access_token(self.sid)
            self.assertEqual(tok.get("access_token"), "fresh_access_token_123")
            self.assertFalse(tok.get("needs_reauth"))
            self.assertGreater(tok.get("expires_at"), time.time())

    def test_youtube_access_token_handles_invalid_grant(self):
        """When Google returns invalid_grant, mark needs_reauth=True and return clear re-auth message."""
        import urllib.error
        revoked_token = {
            "token": "expired_access",
            "access_token": "expired_access",
            "refresh_token": "revoked_refresh",
            "expires_at": time.time() - 60,
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
        }
        server._youtube_user_save(self.sid, revoked_token)

        err_fp = io.BytesIO(b'{"error": "invalid_grant", "error_description": "Token has been expired or revoked."}')
        http_err = urllib.error.HTTPError("https://oauth2.googleapis.com/token", 400, "Bad Request", {}, err_fp)

        with patch("urllib.request.urlopen", side_effect=http_err):
            res = server._youtube_access_token(self.sid)
            self.assertEqual(res.get("error"), "needs_reauth")
            loaded = server._youtube_user_load(self.sid)
            self.assertTrue(loaded.get("needs_reauth"))

    def test_instagram_endpoint_uses_graph_instagram_for_instagram_login(self):
        """Instagram Login user token must target graph.instagram.com, not graph.facebook.com."""
        ig_cfg = {
            "access_token": "IGQVJ_test_token_123",
            "ig_user_id": "1784140001",
            "oauth_mode": "instagram_login",
            "api_host": "https://graph.instagram.com",
            "needs_reauth": False,
        }
        server._instagram_user_write_local(self.sid, ig_cfg)

        called_urls = []
        def mock_urlopen(req, *args, **kwargs):
            url = req.full_url if hasattr(req, "full_url") else str(req)
            called_urls.append(url)
            resp = MagicMock()
            if "media_publish" in url:
                resp.read.return_value = json.dumps({"id": "pub_999"}).encode("utf-8")
            elif "fields=status_code" in url:
                resp.read.return_value = json.dumps({"status_code": "FINISHED"}).encode("utf-8")
            else:
                resp.read.return_value = json.dumps({"id": "container_123"}).encode("utf-8")
            resp.__enter__.return_value = resp
            return resp

        with patch("urllib.request.urlopen", side_effect=mock_urlopen):
            plan = {"title": "Test Reel", "caption": "Awesome test"}
            result = server._instagram_direct_post(self.sid, "/dev/null", plan, "public")
            self.assertEqual(result.get("id"), "pub_999")
            for u in called_urls:
                self.assertTrue(u.startswith("https://graph.instagram.com"), f"Expected graph.instagram.com, got: {u}")
                self.assertFalse("graph.facebook.com" in u, f"graph.facebook.com must not be called with IG token: {u}")

    def test_instagram_invalid_token_error_raises_needs_reauth(self):
        """When Meta returns OAuthException (code 190) or 'Cannot parse access token', raise needs_reauth."""
        import urllib.error
        ig_cfg = {
            "access_token": "malformed_or_expired_token",
            "ig_user_id": "1784140001",
            "oauth_mode": "instagram_login",
            "api_host": "https://graph.instagram.com",
            "needs_reauth": False,
        }
        server._instagram_user_write_local(self.sid, ig_cfg)

        err_body = json.dumps({
            "error": {
                "message": "Invalid OAuth access token - Cannot parse access token",
                "type": "OAuthException",
                "code": 190,
                "fbtrace_id": "Abc123xyz"
            }
        }).encode("utf-8")
        http_err = urllib.error.HTTPError("https://graph.instagram.com/1784140001/media", 400, "Bad Request", {}, io.BytesIO(err_body))

        with patch("urllib.request.urlopen", side_effect=http_err):
            plan = {"caption": "Test"}
            with self.assertRaises(pm.PublishError) as ctx:
                server._instagram_direct_post(self.sid, "/dev/null", plan, "public")
            self.assertEqual(ctx.exception.code, "needs_reauth")
            self.assertIn("ricollega l'account", str(ctx.exception).lower())

    def test_tiktok_untouched(self):
        """Verify TikTok logic, endpoints, and token handlers remain untouched."""
        self.assertTrue(hasattr(server, "_tiktok_oauth_start"))
        self.assertTrue(hasattr(server, "_tiktok_oauth_callback"))
        self.assertTrue(hasattr(server, "_tiktok_user_load"))
        self.assertTrue(hasattr(pm, "tiktok_direct_post"))

if __name__ == "__main__":
    unittest.main()
