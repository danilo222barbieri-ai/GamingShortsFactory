import io
import json
import os
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
sys.path.insert(0, str(ROOT))

from cryptography.fernet import Fernet
if not os.environ.get("GSF_DATA_ENCRYPTION_KEY"):
    os.environ["GSF_DATA_ENCRYPTION_KEY"] = Fernet.generate_key().decode()

import types
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

class TestInstagramDisconnectAndOAuth(unittest.TestCase):
    def setUp(self):
        self.sid = "test_user_ig_disconnect"
        self.session_dir = server.ROOT / "sessions" / self.sid / "social"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        server._bucket_enabled = lambda: False

    def tearDown(self):
        for f in self.session_dir.glob("*"):
            try: f.unlink()
            except Exception: pass

    def test_disconnect_succeeds_even_with_expired_or_invalid_instagram_token(self):
        """Disconnecting Instagram must succeed cleanly without 400 even if token is expired or revoked."""
        server._instagram_user_write_local(self.sid, {
            "access_token": "expired_token_123",
            "ig_user_id": "17841400",
            "oauth_mode": "instagram_login",
        })
        self.assertTrue((self.session_dir / "instagram_config.json").exists())

        # Should never raise HTTPError 400 or exception
        server._meta_disconnect(self.sid, "instagram")

        # Local files must be removed
        self.assertFalse((self.session_dir / "instagram_config.json").exists())
        self.assertFalse((self.session_dir / "instagram_token.json").exists())
        self.assertEqual(server._instagram_user_load(self.sid), {})

    def test_disconnect_instagram_preserves_other_social_connections(self):
        """Disconnecting Instagram must only remove Instagram, leaving Facebook/YouTube intact."""
        server._instagram_user_write_local(self.sid, {
            "access_token": "ig_token",
            "ig_user_id": "17841400",
        })
        server._security_write_json(self.session_dir / "facebook_config.json", {
            "access_token": "fb_token_keep",
            "facebook_user_id": "999888",
        })

        server._meta_disconnect(self.sid, "instagram")

        self.assertFalse((self.session_dir / "instagram_config.json").exists())
        self.assertTrue((self.session_dir / "facebook_config.json").exists())

    def test_instagram_scopes_conform_to_business_login(self):
        """INSTAGRAM_SCOPES must contain only valid Business Login scopes without non-existent ones."""
        scopes = server.INSTAGRAM_SCOPES.split(",")
        self.assertIn("instagram_business_basic", scopes)
        self.assertIn("instagram_business_content_publish", scopes)
        self.assertNotIn("instagram_business_manage_insights", scopes)

if __name__ == "__main__":
    unittest.main()
