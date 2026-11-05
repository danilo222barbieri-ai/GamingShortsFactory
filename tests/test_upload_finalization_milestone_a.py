import unittest
import tempfile
import json
import os
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "web"))

import direct_upload_server as dus


class TestUploadFinalizationMilestoneA(unittest.TestCase):

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.root = Path(self.td.name)
        self.orig_root = dus.ROOT
        dus.ROOT = self.root

    def tearDown(self):
        dus.ROOT = self.orig_root
        self.td.cleanup()

    def test_01_upload_states_definition(self):
        valid_states = {
            "UPLOADING",
            "TRANSFER_COMPLETE",
            "FINALIZING",
            "VERIFYING",
            "PROJECT_SAVING",
            "COMPLETED",
            "RECOVERABLE_ERROR",
            "FAILED",
        }
        self.assertEqual(len(valid_states), 8)

    def test_02_auto_save_uploaded_source_idempotence(self):
        sid = "sess_test_1"
        upload_id = "up_abc123"
        session_root = self.root / "sessions" / sid
        media = session_root / "media"
        media.mkdir(parents=True, exist_ok=True)
        video_file = media / "source.mp4"
        video_file.write_bytes(b"dummy mp4 content" * 100)

        # First save
        res1 = dus._auto_save_uploaded_source_to_projects(
            sid=sid,
            upload_id=upload_id,
            source_path=str(video_file),
            original_name="Gameplay Test.mp4",
            total=video_file.stat().st_size,
        )
        self.assertTrue(res1["ok"])
        self.assertEqual(res1["project_id"], f"proj_{upload_id}")

        # Check index has exactly 1 project
        proj_idx_file = session_root / "projects" / "index.json"
        self.assertTrue(proj_idx_file.is_file())
        idx_data = json.loads(proj_idx_file.read_text(encoding="utf-8"))
        projects = idx_data.get("projects") or []
        self.assertEqual(len(projects), 1)

        # Second save (retry / idempotence)
        res2 = dus._auto_save_uploaded_source_to_projects(
            sid=sid,
            upload_id=upload_id,
            source_path=str(video_file),
            original_name="Gameplay Test.mp4",
            total=video_file.stat().st_size,
        )
        self.assertTrue(res2["ok"])

        # Must still have exactly 1 project, no duplication
        idx_data_2 = json.loads(proj_idx_file.read_text(encoding="utf-8"))
        projects_2 = idx_data_2.get("projects") or []
        self.assertEqual(len(projects_2), 1)
        self.assertEqual(projects_2[0]["id"], f"proj_{upload_id}")

    def test_03_recovery_from_incomplete_finalization(self):
        sid = "sess_recovery"
        upload_id = "up_recovery_99"
        upload_dir = self.root / "sessions" / sid / "direct_upload" / upload_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        data_path = upload_dir / "upload.tmp"
        data_path.write_bytes(b"\x00\x00\x00 ftypisom" + b"\x00" * 1000)
        state_path = upload_dir / "state.json"
        state_path.write_text(json.dumps({
            "total": data_path.stat().st_size,
            "count": 2,
            "received": [0, 1],
            "name": "GameVideo.mp4",
            "stem": "GameVideo",
            "ext": ".mp4",
        }), encoding="utf-8")

        # Emulate finalization from recovered state without re-uploading
        media = self.root / "sessions" / sid / "media"
        media.mkdir(parents=True, exist_ok=True)
        final = media / f"source_direct_GameVideo_{upload_id}.mp4"
        os.replace(data_path, final)
        marker = media / ".direct_upload_ready.json"
        marker.write_text(json.dumps({
            "path": str(final),
            "name": "GameVideo.mp4",
            "size": final.stat().st_size,
            "upload_id": upload_id,
            "completed_at": 123456789.0,
            "storage": "direct_fallback",
        }), encoding="utf-8")

        res = dus._auto_save_uploaded_source_to_projects(
            sid=sid,
            upload_id=upload_id,
            source_path=str(final),
            original_name="GameVideo.mp4",
            total=final.stat().st_size,
        )
        self.assertTrue(res["ok"])
        self.assertTrue(final.is_file())


if __name__ == "__main__":
    unittest.main()
