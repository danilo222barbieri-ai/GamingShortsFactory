from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _stub_optional_server_dependencies() -> None:
    if "boto3" not in sys.modules:
        boto3 = types.ModuleType("boto3")
        boto3.client = lambda *args, **kwargs: None
        boto3_s3 = types.ModuleType("boto3.s3")
        boto3_transfer = types.ModuleType("boto3.s3.transfer")
        boto3_transfer.TransferConfig = lambda *args, **kwargs: object()
        boto3.s3 = boto3_s3
        sys.modules.update(
            {
                "boto3": boto3,
                "boto3.s3": boto3_s3,
                "boto3.s3.transfer": boto3_transfer,
            }
        )
    if "botocore.config" not in sys.modules:
        botocore = types.ModuleType("botocore")
        botocore_config = types.ModuleType("botocore.config")
        botocore_config.Config = lambda *args, **kwargs: object()
        botocore.config = botocore_config
        sys.modules.update({"botocore": botocore, "botocore.config": botocore_config})
    if "cryptography.fernet" not in sys.modules:
        cryptography = types.ModuleType("cryptography")
        fernet = types.ModuleType("cryptography.fernet")

        class _Fernet:
            def __init__(self, *_args, **_kwargs):
                pass

        class _InvalidToken(Exception):
            pass

        fernet.Fernet = _Fernet
        fernet.InvalidToken = _InvalidToken
        cryptography.fernet = fernet
        sys.modules.update({"cryptography": cryptography, "cryptography.fernet": fernet})


def _load_server_module():
    _stub_optional_server_dependencies()
    web = str(ROOT / "web")
    spec = importlib.util.spec_from_file_location(
        "gsf_direct_upload_server_mobile_editor_test",
        ROOT / "web" / "direct_upload_server.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.path.insert(0, web)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(web)
    return module


SERVER = _load_server_module()


def test_quality_mode_round_trips_through_session_bound_overlay(tmp_path) -> None:
    SERVER.ROOT = tmp_path

    saved = SERVER._editor_overlay_state_save(
        "session-safe_1",
        {"qualityMode": "Max Quality", "zoom": 1.2, "notAllowed": "drop-me"},
    )

    assert saved == {"qualityMode": "Max Quality", "zoom": 1.2}
    assert SERVER._editor_overlay_state_load("session-safe_1") == saved
    assert not (tmp_path / "sessions" / "drop-me").exists()


def test_mobile_context_normalizes_real_events_and_bounded_ai_suggestions() -> None:
    session_state = {
        "gsf_v108_event_map": [
            {"time": 2.4, "type": "kill", "score": 0.95, "label": "Eliminazione"},
            {"time": 99, "type": "hook", "score": 1},
            {"time": "bad", "type": "aim"},
        ],
        "gsf_v112_brain_context": {
            "engine": "game-brain-v112",
            "genre": "FPS",
            "selected": [{"start": 0, "motion": 0.9}],
        },
    }
    editor_state = {
        "sourceDuration": 20,
        "inPoint": 0,
        "outPoint": 15,
        "zoom": 1,
        "panX": 4,
        "panY": -2,
        "captionOn": True,
        "captionY": 90,
        "volume": 70,
    }

    context = SERVER._editor_mobile_context(session_state, editor_state)

    assert [marker["type"] for marker in context["event_map"]] == ["KILL"]
    assert context["event_map"][0]["position_pct"] == 16.0
    assert context["brain_context"]["engine"] == "game-brain-v112"
    assert len(context["event_map"]) <= 18
    assert 1 <= len(context["ai_suggestions"]) <= 6
    assert {"action_reframe", "caption_safe_zone", "lift_game_audio"} <= {
        item["id"] for item in context["ai_suggestions"]
    }
    allowed_patch_keys = {
        "inPoint",
        "outPoint",
        "zoom",
        "panX",
        "panY",
        "volume",
        "speed",
        "brightness",
        "contrast",
        "captionOn",
        "captionY",
        "hudMode",
    }
    for suggestion in context["ai_suggestions"]:
        assert set(suggestion) == {"id", "category", "label", "reason", "impact", "patch"}
        assert suggestion["id"] and suggestion["label"] and suggestion["reason"] and suggestion["impact"]
        assert suggestion["patch"]
        assert set(suggestion["patch"]) <= allowed_patch_keys
    json.dumps(context, allow_nan=False)


def test_malformed_intelligence_degrades_to_manual_empty_context() -> None:
    context = SERVER._editor_mobile_context(
        {"gsf_v108_event_map": "not-a-list", "gsf_v112_brain_context": ["bad"]},
        {"sourceDuration": "bad", "inPoint": None, "outPoint": {}},
    )

    assert context == {"event_map": [], "brain_context": {}, "ai_suggestions": []}


def test_editor_state_payload_includes_session_intelligence(tmp_path) -> None:
    SERVER.ROOT = tmp_path
    sid = "session_payload_1"
    session_root = tmp_path / "sessions" / sid
    session_root.mkdir(parents=True)
    media = session_root / "source.mp4"
    media.write_bytes(b"video-bytes")
    (session_root / "session_state.json").write_text(
        json.dumps(
            {
                "gsf_v108_event_map": [{"time": 1, "type": "action_peak", "score": 1}],
                "gsf_v112_brain_context": {"engine": "game-brain-v112"},
            }
        ),
        encoding="utf-8",
    )
    SERVER._editor_overlay_state_save(
        sid,
        {"sourceDuration": 12, "inPoint": 0, "outPoint": 10, "qualityMode": "Adaptive AI"},
    )

    payload = SERVER._editor_state_payload(sid, media)

    assert payload["ok"] and payload["ready"]
    assert payload["initial_state"]["qualityMode"] == "Adaptive AI"
    assert payload["event_map"][0]["type"] == "ACTION_PEAK"
    assert payload["brain_context"]["engine"] == "game-brain-v112"
    assert isinstance(payload["ai_suggestions"], list)


def test_editor_state_security_contract_remains_session_bound() -> None:
    server = (ROOT / "web" / "direct_upload_server.py").read_text(encoding="utf-8")
    nginx = (ROOT / "web" / "nginx.conf.template").read_text(encoding="utf-8")

    get_block = server[server.index('if clean=="/editor/state":') :]
    get_block = get_block[: get_block.index('if clean=="/editor-media/current":')]
    assert "_editor_prepare_current(_social_sid(self))" in get_block
    post_block = server[server.index('if path=="/editor/state/save":') :]
    post_block = post_block[: post_block.index('if path=="/ai/feedback":')]
    assert "_editor_overlay_state_save(sid,raw_state)" in post_block
    assert 'sid=_safe_id(self.headers.get("X-GSF-Session-ID"))' in server

    for route in ('location = /editor/state {', 'location = /editor/state/save {'):
        block = nginx[nginx.index(route) :]
        block = block[: block.index("\n    }")]
        assert "proxy_set_header X-GSF-Session-ID $gsf_session_cookie;" in block
