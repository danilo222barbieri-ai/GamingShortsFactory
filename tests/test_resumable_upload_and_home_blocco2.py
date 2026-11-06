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

            # V443: an upload is the active project; it becomes a draft only on replacement.
            assert dus._draft_list(sid) == []

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
    assert 'if(loaded){' in home_html  # V444: the check mirrors the active project
    assert 'circleResetTimer=window.setTimeout(restoreEmptyCircleForNewVideo,650);' not in home_html
    assert 'uploadLabel.innerHTML="Video caricato"' in home_html

    # 3. Auto-save to Projects
    assert 'fetch("/direct-upload/projects/save-uploaded-source"' in home_html

    # 4. Restore the original uploader prompt after returning from AI
    assert "function restoreEmptyCircleForNewVideo()" in home_html
    assert 'uploadLabel.innerHTML="CARICA<br>IL TUO GAMEPLAY"' in home_html
    assert "label.innerHTML='CARICA<br>IL TUO GAMEPLAY'" in home_embed

    # 5. Never restore old video preview (.naPreview) when returning to Home
    assert "const showPreview=()=>{hidePreview();};" in home_html


def test_upload_check_persists_while_the_project_is_active():
    home = (ROOT / "web/home_v154_component/index.html").read_text(encoding="utf-8")

    # V444: show success when the server confirms the upload and keep it
    # through rerenders, navigation and refresh while the project is active.
    assert 'const UPLOAD_ACK_KEY="gsf_home_upload_ack_v437"' in home
    assert 'if(fromUploadComplete)setUploadAcknowledgement(true);' in home
    assert 'if(uploadBusy&&!fromUploadComplete){fitViewport();return;}' in home
    assert 'if(target!=="home")setUploadAcknowledgement(false);' in home
    assert 'window.parent.addEventListener("gsf:surfacechange",onHomeSurfaceChange' in home
    assert '}else if(!uploadBusy){\n     // Back on Home the active project is still confirmed by its check.\n     setLoaded(loaded);' in home
    assert 'restoreEmptyCircleForNewVideo();' in home

    # UI reset does not clear the saved source/IA/Editor readiness; it must
    # also retain the safe-replacement confirmation for a second video.
    assert 'circle.setAttribute("data-gsf-has-source",loaded?"true":"false");' in home
    assert 'view.classList.toggle("loadedView",loaded);' in home
    assert 'if(!loaded||uploadBusy||currentUploadState===UPLOAD_ST.RECOVERABLE_ERROR)return;' in home
    assert 'openReplaceToast();' in home


def test_new_video_requires_verified_draft_before_transfer():
    html = (ROOT / "web/home_v154_component/index.html").read_text(encoding="utf-8")
    ai = (ROOT / "web/ai_v221_component/index.html").read_text(encoding="utf-8")
    edge = (ROOT / "web/nginx.conf.template").read_text(encoding="utf-8")
    app = (ROOT / "app.py").read_text(encoding="utf-8")

    # Never bypass draft failure/timeouts: no bytes move before its confirmation.
    start = html.index('pick.addEventListener("change",async()=>')
    save = html.index('const draft=await saveCurrentBeforeReplacement();', start)
    reset = html.index('await prepareCleanSourceAfterDraft(draft,fileFingerprint(file));', save)
    transfer = html.index('uploadBusy=true;', reset)
    assert start < save < reset < transfer
    assert "draft_save_timeout" not in html
    assert 'pick.value="";' in html[reset:transfer]
    assert '"/workflow/prepare-new-upload"' in html
    assert 'location = /workflow/prepare-new-upload' in edge
    assert 'limit_except POST { deny all; }' in edge
    assert 'GSF_V438_FRESH_SOURCE_STATE' in app

    # Old scanning timers, selected moments and previews must be reset. New
    # analysis starts once the iframe is ready, not after a fixed 80ms guess.
    assert 'GSF_NEW_VIDEO_RESET' in html
    assert 'GSF_AI_RESET_SOURCE' in ai
    assert '++pollToken;' in ai
    assert 'sessionStorage.removeItem("gsf_ai_active_scan_v2")' in ai
    assert 'localStorage.removeItem(DRAFT_KEY)' in ai
    assert 'freshSourcePending' in ai
    assert 'sessionStorage.setItem("gsf_ai_source_epoch_v438"' in html
    assert 'sessionStorage.getItem("gsf_ai_source_epoch_v438")' in ai
    assert 'sessionStorage.removeItem("gsf_ai_source_epoch_v438")' in ai
    assert 'frameReady=true;' in app
    assert "startWhenReady();" in app
    assert 'value({event: "upload_complete", duration: actualSec, engine: engine || "auto"});' in html


def test_ai_results_do_not_mix_two_uploaded_sources(tmp_path, monkeypatch):
    import os
    import time
    import web.direct_upload_server as dus

    monkeypatch.setattr(dus, "ROOT", tmp_path)
    sid = "source_epoch_test"
    media = tmp_path / "sessions" / sid / "media"
    media.mkdir(parents=True)
    prior = media / "mini_1_2.mp4"
    prior.write_bytes(b"old moment")
    old_time = time.time() - 100
    os.utime(prior, (old_time, old_time))
    dus._write_json_atomic(media / ".direct_upload_ready.json", {
        "path": str(media / "source_old.mp4"),
        "upload_id": "old123",
        "completed_at": old_time,
    })
    dus._write_json_atomic(media / "ai_results_meta.json", {
        "status": "success", "updated_at": old_time,
        "request_id": "old-ai", "items": [{"index": 0, "start_time": 2.0}],
    })
    dus._write_json_atomic(media / dus._AI_SOURCE_EPOCH_NAME, {
        "reset_at": time.time() - 1,
        "previous_upload_id": "old123", "next_upload_id": "new-client-fingerprint",
    })

    pending = dus._ai_results_payload(sid)
    assert pending["previews"] == []
    assert pending["status"] == "idle"

    # The bucket allocates a different upload ID: the epoch must accept it.
    fresh = media / "mini_1_5.mp4"
    fresh.write_bytes(b"new moment")
    dus._write_json_atomic(media / ".direct_upload_ready.json", {
        "path": str(media / "source_new.mp4"),
        "upload_id": "bucket-new-id",
        "completed_at": time.time(),
    })
    dus._write_json_atomic(media / "ai_results_meta.json", {
        "status": "success", "updated_at": time.time(),
        "request_id": "new-ai", "items": [{"index": 0, "start_time": 5.0}],
    })
    result = dus._ai_results_payload(sid)
    assert result["request_id"] == "new-ai"
    assert result["count"] == 1
    assert "mini_1_5.mp4" in result["previews"][0]["video"]
    assert all("mini_1_2.mp4" not in x.get("video", "") for x in result["previews"])


def test_new_video_reset_refuses_unverified_drafts(tmp_path, monkeypatch):
    import pytest
    import web.direct_upload_server as dus

    monkeypatch.setattr(dus, "ROOT", tmp_path)
    sid = "new_source_unverified"
    with pytest.raises(RuntimeError, match="bozza"):
        dus._ai_begin_new_source(sid, "not-saved", "new-video")
    assert not (tmp_path / "sessions" / sid / "media" / dus._AI_SOURCE_EPOCH_NAME).exists()
