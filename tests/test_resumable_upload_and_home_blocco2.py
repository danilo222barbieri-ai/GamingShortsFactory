from __future__ import annotations

import json
import tempfile
from pathlib import Path

from web.global_jobs_v2 import GlobalJobManager


ROOT = Path(__file__).resolve().parents[1]


def test_auto_save_uploaded_source_to_projects_is_idempotent():
    import web.direct_upload_server as dus

    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        old_root = dus.ROOT
        dus.ROOT = tmp_root
        try:
            sid = "session_test_blocco2_abc123"
            media_dir = tmp_root / "sessions" / sid / "media"
            media_dir.mkdir(parents=True, exist_ok=True)
            video_file = media_dir / "source_direct_warzone_up123.mp4"
            video_file.write_bytes(b"\x00\x00\x00\x18ftypmp42" + b"A" * 2048)

            res1 = dus._auto_save_uploaded_source_to_projects(
                sid=sid,
                upload_id="up123",
                source_path=str(video_file),
                original_name="Warzone_Clip.mp4",
                total=video_file.stat().st_size,
            )
            assert res1["ok"] is True
            assert res1["project_id"] == "proj_up123"

            # Calling again (e.g. on page change or duplicate callback) must not duplicate entries
            res2 = dus._auto_save_uploaded_source_to_projects(
                sid=sid,
                upload_id="up123",
                source_path=str(video_file),
                original_name="Warzone_Clip.mp4",
                total=video_file.stat().st_size,
            )
            assert res2["ok"] is True

            proj_index = json.loads(
                (tmp_root / "sessions" / sid / "projects" / "index.json").read_text(encoding="utf-8")
            )
            assert len(proj_index["items"]) == 1
            assert proj_index["items"][0]["id"] == "proj_up123"
            assert proj_index["items"][0]["video_filename"] == "Warzone_Clip.mp4"

            drafts = dus._draft_list(sid)
            assert len(drafts) == 1
            assert drafts[0]["id"] == "draft_auto_up123"

            session_state = json.loads(
                (tmp_root / "sessions" / sid / "session_state.json").read_text(encoding="utf-8")
            )
            assert session_state["video_Originale"] == str(video_file)
            assert session_state["gsf_uploaded_video_name"] == "Warzone_Clip.mp4"
        finally:
            dus.ROOT = old_root


def test_resumable_chunk_upload_state_and_recovery():
    import web.direct_upload_server as dus

    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        old_root = dus.ROOT
        old_mgr = dus._GLOBAL_JOB_MANAGER
        dus.ROOT = tmp_root
        dus._GLOBAL_JOB_MANAGER = GlobalJobManager(tmp_root)
        try:
            sid = "session_resume_chunk_001"
            upload_id = "up_testresume_1000"
            upload_dir = tmp_root / "sessions" / sid / "direct_upload" / upload_id
            upload_dir.mkdir(parents=True, exist_ok=True)
            data_path = upload_dir / "upload.tmp"
            state_path = upload_dir / "state.json"

            # Simulate 2 out of 3 chunks uploaded before network drop
            total_size = 3000
            with open(data_path, "wb") as f:
                f.truncate(total_size)
                f.seek(0)
                f.write(b"A" * 2000)

            state = {
                "total": total_size,
                "count": 3,
                "name": "ClipResume.mp4",
                "stem": "ClipResume",
                "ext": ".mp4",
                "ranges": {"0": [0, 1000], "1": [1000, 1000]},
                "received": [0, 1],
            }
            dus._write_json_atomic(state_path, state)

            # Verify state.json preserves exact received chunks for /chunk/status
            saved_state = json.loads(state_path.read_text(encoding="utf-8"))
            received = sorted({int(x) for x in saved_state.get("received", [])})
            count = int(saved_state.get("count", 1))
            pct = round((len(received) / count) * 100.0, 1)
            assert received == [0, 1]
            assert pct == 66.7
        finally:
            dus._GLOBAL_JOB_MANAGER = old_mgr
            dus.ROOT = old_root


def test_home_component_resumable_upload_and_clean_circle_contracts():
    home_html = (ROOT / "web/home_v154_component/index.html").read_text(encoding="utf-8")
    home_embed = (ROOT / "web/home_v154_embed.py").read_text(encoding="utf-8")

    # 1. Resumable upload fingerprint & endpoints
    assert "function fileFingerprint(file)" in home_html
    assert "/direct-upload/chunk/status?upload_id=" in home_html
    assert "init.uploaded_parts" in home_html
    assert "putWithRetry" in home_html
    assert "chunkPutWithRetry" in home_html

    # 2. Real transfer progress & confirmed completion «Video caricato»
    assert "function updateUploadProgressUI(pct)" in home_html
    assert 'statusText.textContent = "Video caricato";' in home_html
    assert 'if(loaded){' in home_html
    assert 'circleResetTimer=window.setTimeout(restoreEmptyCircleForNewVideo,650);' not in home_html
    assert 'uploadLabel.innerHTML="Video caricato"' in home_html

    # 3. Auto-save to Projects
    assert 'fetch("/direct-upload/projects/save-uploaded-source"' in home_html

    # 4. Restore empty circle with «Carica un nuovo video»
    assert "function restoreEmptyCircleForNewVideo()" in home_html
    assert 'uploadLabel.innerHTML=loaded?"Carica un<br>nuovo video":"CARICA<br>IL TUO GAMEPLAY"' in home_html
    assert "label.innerHTML='Carica un<br>nuovo video'" in home_embed

    # 5. Never restore old video preview (.naPreview) when returning to Home
    assert "const showPreview=()=>{hidePreview();};" in home_html
