"""V443: real companion Handler over HTTP; only S3 and provider APIs are faked."""
import io
import json
import os
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


class NoSuchKey(Exception):
    response = {"Error": {"Code": "NoSuchKey"}}


class FakeS3:
    def __init__(self):
        self.objects = {}
        self.down = False

    def _check(self):
        if self.down:
            raise ConnectionError("endpoint unreachable")

    def put_object(self, Bucket, Key, Body, **_):
        self._check()
        self.objects[Key] = bytes(Body)

    def get_object(self, Bucket, Key):
        self._check()
        if Key not in self.objects:
            raise NoSuchKey(Key)
        return {"Body": io.BytesIO(self.objects[Key])}

    def head_object(self, Bucket, Key):
        self._check()
        if Key not in self.objects:
            raise NoSuchKey(Key)
        return {"ContentLength": len(self.objects[Key])}

    def delete_object(self, Bucket, Key):
        self._check()
        self.objects.pop(Key, None)


class Base(unittest.TestCase):
    sid = "sidv443test0001"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.patches = [patch.object(dus, "ROOT", self.root), patch.dict(os.environ, {"GSF_CSRF_SECRET": "v443-test-secret"})]
        self.s3 = self.bucket_client()
        if self.s3:
            self.patches += [patch.object(dus, "_bucket_enabled", lambda: True), patch.object(dus, "_s3", lambda: self.s3),
                             patch.object(dus, "_security_encrypt_json", lambda p: json.dumps(p).encode()),
                             patch.object(dus, "_security_decrypt_json", lambda r: json.loads(r.decode())),
                             patch.object(dus, "S3_BUCKET", "test")]
        for item in self.patches:
            item.start()
        dus._ACTIVE_RESTORE_CHECKED.clear()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), dus.Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.media = self.root / "sessions" / self.sid / "media"
        self.media.mkdir(parents=True)

    def bucket_client(self):
        return None

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        for item in reversed(self.patches):
            item.stop()
        self.tmp.cleanup()

    def http(self, path, body=None, csrf=None):
        headers = {"X-GSF-Session-ID": self.sid, "Content-Type": "application/json"}
        if csrf:
            headers["X-GSF-CSRF"] = csrf
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(self.base + path, data=data, headers=headers, method="POST" if data is not None else "GET")
        try:
            with urllib.request.urlopen(req, timeout=15) as res:
                return res.status, json.loads(res.read() or b"{}")
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read() or b"{}")

    def csrf(self):
        return self.http("/creator-hub/state?scope=header")[1]["csrf_token"]

    def upload(self, upload_id, name, bucket_key=""):
        final = self.media / f"source_direct_x_{upload_id}.mp4"
        final.write_bytes(b"video-" + upload_id.encode())
        meta = {"path": str(final), "name": name, "size": final.stat().st_size, "upload_id": upload_id,
                "completed_at": 1.0, "storage": "railway_bucket" if bucket_key else "direct_fallback", "bucket_key": bucket_key}
        (self.media / ".direct_upload_ready.json").write_text(json.dumps(meta), encoding="utf-8")
        return dus._auto_save_uploaded_source_to_projects(self.sid, upload_id, str(final), name, final.stat().st_size, bucket_key, "")

    def replace_with(self, upload_id, name, bucket_key=""):
        token = self.csrf()
        status, saved = self.http("/drafts/save-current", {"for_replacement": True}, token)
        self.assertEqual(status, 200, saved)
        self.assertTrue(saved["verified"])
        if not saved.get("no_source"):
            status, prepared = self.http("/workflow/prepare-new-upload", {"draft_id": saved["id"], "upload_id": upload_id}, token)
            self.assertEqual(status, 200, prepared)
        self.upload(upload_id, name, bucket_key)
        return saved

    def active_project(self):
        return dus._current_project_record(self.sid)[2]

    def draft_sources(self):
        return sorted(row.get("source_name") for row in dus._draft_list(self.sid))


class RuntimeImport(unittest.TestCase):
    def test_lazy_imports_resolve_as_the_servers_launch(self):
        result = subprocess.run([sys.executable, str(ROOT / "web/check_runtime_imports_v443.py")], cwd=ROOT,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": ""},
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inner_package_still_serves_its_shim(self):
        program = "import sys;sys.path.insert(0,'.');import web.render_gate_v293 as m,web.mobile_editor_recipe as r;print(m.__file__);print(r.__file__)"
        out = subprocess.run([sys.executable, "-c", program], cwd=ROOT / "web", capture_output=True, text=True, timeout=60,
                             env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": ""})
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("web/web/render_gate_v293.py", out.stdout)
        self.assertIn("web/mobile_editor_recipe.py", out.stdout)


class ActiveProjectAndDrafts(Base):
    def test_first_video_stays_active_without_a_draft(self):
        self.assertEqual(self.replace_with("aaaaaaaaaa", "uno.mp4").get("no_source"), True)
        self.assertEqual(self.active_project(), "proj_aaaaaaaaaa")
        self.assertEqual(dus._draft_list(self.sid), [])

    def test_second_and_third_video_save_only_the_previous_one(self):
        self.upload("aaaaaaaaaa", "uno.mp4")
        self.replace_with("bbbbbbbbbb", "due.mp4")
        self.assertEqual(self.active_project(), "proj_bbbbbbbbbb")
        self.assertEqual(self.draft_sources(), ["uno.mp4"])
        self.replace_with("cccccccccc", "tre.mp4")
        self.assertEqual(self.active_project(), "proj_cccccccccc")
        self.assertEqual(self.draft_sources(), ["due.mp4", "uno.mp4"])

    def test_failed_draft_preserves_project_and_hides_python_errors(self):
        self.upload("aaaaaaaaaa", "uno.mp4")
        marker = (self.media / ".direct_upload_ready.json").read_bytes()
        with patch.object(dus, "_draft_save", side_effect=ModuleNotFoundError("No module named 'web.x'")):
            status, body = self.http("/drafts/save-current", {"for_replacement": True}, self.csrf())
        self.assertEqual(status, 503)
        self.assertFalse(body["verified"])
        self.assertNotIn("module", body["error"].lower())
        self.assertEqual((self.media / ".direct_upload_ready.json").read_bytes(), marker)
        self.assertEqual(self.active_project(), "proj_aaaaaaaaaa")
        self.assertEqual(dus._draft_list(self.sid), [])

    def test_editor_state_travels_with_the_replaced_project(self):
        self.upload("aaaaaaaaaa", "uno.mp4")
        session = self.root / "sessions" / self.sid
        (session / "editor_overlay_state.json").write_text(json.dumps({"source_key": "aaaaaaaaaa", "state": {"trim": [1, 5]}}), encoding="utf-8")
        saved = self.replace_with("bbbbbbbbbb", "due.mp4")
        draft = dus._draft_load(self.sid, saved["id"])
        self.assertEqual(draft["state"]["gsf_mobile_editor_snapshot"]["state"], {"trim": [1, 5]})

    def test_plain_save_without_a_source_still_reports_it(self):
        status, body = self.http("/drafts/save-current", {}, self.csrf())
        self.assertEqual(status, 409)
        self.assertFalse(body["ok"])


class RedeploySurvival(Base):
    def bucket_client(self):
        return FakeS3()

    def test_active_project_survives_loss_of_the_runtime_disk(self):
        self.upload("aaaaaaaaaa", "uno.mp4", "uploads/sidv443test0001/aaaaaaaaaa/uno.mp4")
        self.assertEqual(dus._draft_list(self.sid), [])
        import shutil
        shutil.rmtree(self.root / "sessions" / self.sid)
        dus._ACTIVE_RESTORE_CHECKED.clear()
        self.assertTrue(dus._active_project_restore(self.sid))
        marker = json.loads((self.media / ".direct_upload_ready.json").read_text(encoding="utf-8"))
        self.assertEqual(marker["upload_id"], "aaaaaaaaaa")
        self.assertEqual(self.active_project(), "proj_aaaaaaaaaa")

    def test_no_mirror_means_nothing_restored(self):
        self.assertFalse(dus._active_project_restore(self.sid))


class SocialStatus(Base):
    def bucket_client(self):
        return FakeS3()

    def connect_youtube(self):
        dus._youtube_user_write_local(self.sid, {"access_token": "t", "owner_id": dus._storage_owner_id(self.sid)})

    def test_hub_and_share_report_the_same_state(self):
        self.connect_youtube()
        hub = self.http("/creator-hub/state")[1]
        share = self.http("/share/state")[1]
        self.assertEqual(hub["social"], share["social"])
        self.assertEqual(hub["social_status"], share["social_status"])
        self.assertTrue(share["social"]["youtube"])
        self.assertEqual(share["social_status"]["tiktok"], "not_connected")

    def test_share_state_does_not_crash_on_the_final_lookup(self):
        status, body = self.http("/share/state")
        self.assertEqual(status, 200, body)
        self.assertIn("preflight", body)

    def test_storage_outage_is_not_a_disconnect(self):
        self.s3.down = True
        status, body = self.http("/share/state")
        self.assertEqual(status, 200, body)
        self.assertEqual(set(body["social_status"].values()), {"unavailable"})
        self.assertEqual(body["preflight"]["checks"]["youtube"]["status"], "unavailable")
        self.assertFalse(body["preflight"]["checks"]["youtube"]["ready"])

    def test_expired_is_distinct_and_blocks_publishing(self):
        dus._youtube_user_write_local(self.sid, {"access_token": "t", "needs_reauth": True, "owner_id": dus._storage_owner_id(self.sid)})
        body = self.http("/share/state")[1]
        self.assertEqual(body["social_status"]["youtube"], "expired")
        self.assertEqual(body["preflight"]["checks"]["youtube"]["status"], "needs_reauth")

    def test_twitch_with_refresh_token_stays_connected_after_access_expiry(self):
        dus._social_connection_save(self.sid, "twitch", {"access_token": "a", "refresh_token": "r", "expires_at": 1, "user_id": "9"})
        self.assertEqual(dus._social_status_of(self.sid, "twitch"), "connected")

    def test_facebook_without_page_is_connected_but_not_publishable(self):
        dus._social_connection_save(self.sid, "facebook", {"access_token": "a", "pages": [{"id": "1"}]})
        body = self.http("/share/state")[1]
        self.assertTrue(body["social"]["facebook"])
        self.assertEqual(body["preflight"]["checks"]["facebook"]["status"], "no_page_selected")


class TwitchContent(Base):
    def bucket_client(self):
        return FakeS3()

    def fake_api(self, failures):
        rows = {"streams": [{"id": "s1", "user_id": "9", "user_login": "me", "title": "live"}],
                "videos": [{"id": "v1", "user_id": "9", "title": "vod"}],
                "clips": [{"id": "c1", "broadcaster_id": "9", "title": "clip"}]}

        def api(sid, path, params=None):
            if path in failures:
                raise dus._social421.TwitchError("Twitch temporaneamente non disponibile.", failures[path])
            return {"data": rows.get(path, [])}
        return api

    def listing(self, kind, failures=None):
        with patch.object(dus, "_twitch_access", lambda sid, **_: {"user_id": "9", "access_token": "a"}), \
                patch.object(dus, "_twitch_api", self.fake_api(failures or {})):
            return self.http(f"/social-connect/twitch/content?type={kind}")

    def test_each_section_returns_its_content(self):
        for kind, expected in (("live", "s1"), ("videos", "v1"), ("clips", "c1")):
            status, body = self.listing(kind)
            self.assertEqual(status, 200, body)
            self.assertEqual([row["id"] for row in body["data"]], [expected])

    def test_all_merges_sections(self):
        body = self.listing("all")[1]
        self.assertEqual(sorted(row["id"] for row in body["data"]), ["c1", "s1", "v1"])
        self.assertFalse(body["partial"])

    def test_no_live_stream_is_empty_not_an_error(self):
        with patch.object(dus, "_twitch_access", lambda sid, **_: {"user_id": "9", "access_token": "a"}), \
                patch.object(dus, "_twitch_api", lambda *a, **k: {"data": []}):
            status, body = self.http("/social-connect/twitch/content?type=live")
        self.assertEqual((status, body["data"]), (200, []))

    def test_failed_section_keeps_the_working_ones(self):
        for code in (403, 429, 503):
            status, body = self.listing("all", {"videos": code})
            self.assertEqual(status, 200, body)
            self.assertEqual(sorted(row["id"] for row in body["data"]), ["c1", "s1"])
            self.assertEqual(body["unavailable_sections"], ["videos"])

    def test_api_failure_never_looks_like_an_empty_list(self):
        for code in (401, 403, 429, 503):
            status, body = self.listing("videos", {"videos": code})
            self.assertEqual(status, code)
            self.assertFalse(body["ok"])
            self.assertNotIn("data", body)
        status, body = self.listing("all", {"streams": 429, "videos": 429, "clips": 429})
        self.assertEqual(status, 429)

    def test_expired_credentials_fail_the_whole_listing(self):
        self.assertEqual(self.listing("all", {"clips": 401})[0], 401)

    def test_catalog_outage_does_not_hide_twitch_content(self):
        with patch.object(dus, "_source_load", side_effect=ConnectionError("down")):
            status, body = self.listing("clips")
        self.assertEqual(status, 200, body)
        self.assertEqual(body["data"][0]["id"], "c1")


class ProfileRename(Base):
    def bucket_client(self):
        return FakeS3()

    def login(self):
        self.s3.objects[dus._creator_session_key(self.sid)] = json.dumps({"account_id": "acct1"}).encode()
        self.s3.objects[dus._creator_profile_key("acct1")] = json.dumps({"account_id": "acct1", "display_name": "Old"}).encode()

    def test_rename_keeps_identity_and_project(self):
        self.login()
        self.upload("aaaaaaaaaa", "uno.mp4")
        owner = dus._storage_owner_id(self.sid)
        status, body = self.http("/creator-hub/profile", {"display_name": "Nuovo"}, self.csrf())
        self.assertEqual(status, 200, body)
        self.assertEqual(dus._storage_owner_id(self.sid), owner)
        self.assertEqual(json.loads(self.s3.objects[dus._creator_session_key(self.sid)])["account_id"], "acct1")
        self.assertEqual(self.http("/creator-hub/state?scope=header")[1]["account"]["display_name"], "Nuovo")
        self.assertEqual(self.active_project(), "proj_aaaaaaaaaa")

    def test_unreadable_profile_never_detaches_the_account(self):
        self.login()
        token = self.csrf()
        before = dict(self.s3.objects)
        with patch.object(dus, "_creator_account_load", return_value={}):
            status, body = self.http("/creator-hub/profile", {"display_name": "Nuovo"}, token)
        self.assertEqual(status, 503)
        self.assertNotIn("account", body["error"])
        self.assertEqual(self.s3.objects[dus._creator_session_key(self.sid)], before[dus._creator_session_key(self.sid)])

    def test_guest_rename_still_works(self):
        status, body = self.http("/creator-hub/profile", {"display_name": "Ospite"}, self.csrf())
        self.assertEqual((status, body["display_name"]), (200, "Ospite"))


if __name__ == "__main__":
    unittest.main()
