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

class TestBlocco2Facebook(unittest.TestCase):
    def setUp(self):
        self.sid = "test_user_blocco2"
        self.session_dir = ROOT / "sessions" / self.sid / "social"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.bucket = MockBucket()
        server._bucket_enabled = lambda: True
        server._s3 = lambda: self.bucket

    def tearDown(self):
        for f in self.session_dir.glob("*"):
            try: f.unlink()
            except Exception: pass

    def test_facebook_scopes_contain_required_permissions(self):
        """Facebook OAuth scopes must contain pages_show_list, pages_read_engagement, and pages_manage_posts."""
        scopes = server.FACEBOOK_SCOPES.split(",")
        self.assertIn("pages_show_list", scopes)
        self.assertIn("pages_read_engagement", scopes)
        self.assertIn("pages_manage_posts", scopes)

    def test_facebook_direct_post_blocks_personal_profile(self):
        """When an account has no Page, Facebook publish must fail with an informative no_page error, never falling back to personal profile."""
        sc = {
            "access_token": "EAA_user_token_only",
            "facebook_user_id": "999888777",
            "pages": [],
            "selected_page_id": "",
            "selected_page_token": "",
        }
        server._social_connection_save(self.sid, "facebook", sc)

        plan = {"title": "Short", "caption": "Caption"}
        with self.assertRaises(pm.PublishError) as ctx:
            server._facebook_direct_post(self.sid, "/dev/null", plan, "public")
        self.assertEqual(ctx.exception.code, "no_page")
        self.assertIn("Pagine Facebook", str(ctx.exception))

    def test_facebook_direct_post_uses_page_token_and_page_id(self):
        """Direct post must target /{page_id}/videos with Page Access Token, not User Token."""
        sc = {
            "access_token": "EAA_user_token",
            "facebook_user_id": "999888777",
            "pages": [
                {
                    "id": "page_12345",
                    "name": "GSF Gaming Page",
                    "access_token": "EAA_PAGE_TOKEN_SECRET",
                    "tasks": ["CREATE_CONTENT", "MANAGE"],
                }
            ],
            "selected_page_id": "page_12345",
            "selected_page_name": "GSF Gaming Page",
            "selected_page_token": "EAA_PAGE_TOKEN_SECRET",
        }
        server._social_connection_save(self.sid, "facebook", sc)

        called_url = []
        called_data = []

        def mock_urlopen(req, *args, **kwargs):
            called_url.append(req.full_url)
            called_data.append(req.data.decode("utf-8"))
            resp = MagicMock()
            resp.read.return_value = json.dumps({"id": "fb_video_987"}).encode("utf-8")
            resp.__enter__.return_value = resp
            return resp

        with patch("urllib.request.urlopen", side_effect=mock_urlopen):
            plan = {"title": "My Short", "caption": "Awesome clip"}
            res = server._facebook_direct_post(self.sid, "/dev/null", plan, "public")
            self.assertEqual(res["id"], "fb_video_987")
            # Verify URL uses page_12345, not 999888777 or me
            self.assertIn("/page_12345/videos", called_url[0])
            self.assertNotIn("/me/videos", called_url[0])
            self.assertNotIn("/999888777/videos", called_url[0])
            # Verify payload contains Page Token, not User Token
            self.assertIn("access_token=EAA_PAGE_TOKEN_SECRET", called_data[0])

    def test_facebook_select_page_endpoint(self):
        """Switching selected page updates selected_page_id, name, and token."""
        sc = {
            "access_token": "EAA_user_token",
            "facebook_user_id": "999888777",
            "pages": [
                {"id": "page_A", "name": "Page Alpha", "access_token": "token_A"},
                {"id": "page_B", "name": "Page Beta", "access_token": "token_B"},
            ],
            "selected_page_id": "page_A",
            "selected_page_name": "Page Alpha",
            "selected_page_token": "token_A",
        }
        server._social_connection_save(self.sid, "facebook", sc)

        # Select Page B
        conn = server._social_connection_load(self.sid, "facebook")
        for p in conn.get("pages", []):
            if p["id"] == "page_B":
                conn["selected_page_id"] = p["id"]
                conn["selected_page_name"] = p["name"]
                conn["selected_page_token"] = p["access_token"]
                break
        server._social_connection_save(self.sid, "facebook", conn)

        updated = server._social_connection_load(self.sid, "facebook")
        self.assertEqual(updated["selected_page_id"], "page_B")
        self.assertEqual(updated["selected_page_name"], "Page Beta")
        self.assertEqual(updated["selected_page_token"], "token_B")

if __name__ == "__main__":
    unittest.main()
