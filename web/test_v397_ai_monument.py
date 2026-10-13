from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


ai_path = ROOT / "ai_monument_v397.py"
assert ai_path.is_file(), "missing V397 AI monument policy module"
ai = load(ai_path, "gsf_v397_ai_monument")

policy = ai.build_render_policy(
    load_ratio=0.92,
    ai_operations=[
        {"op": "pattern_interrupt"},
        {"op": "cold_open"},
        {"op": "smart_ending"},
    ],
)
assert policy["target"] == {
    "width": 1080,
    "height": 1920,
    "fps": 60,
    "video_codec": "h264",
    "profile": "high",
    "pixel_format": "yuv420p",
    "audio_codec": "aac",
    "audio_rate": 48000,
    "audio_channels": 2,
}
assert policy["quality_floor"] == "canonical"
assert policy["single_pass_preferred"] is True
assert policy["max_ai_reencodes"] == 1, policy
assert policy["drop_quality_to_save_time"] is False

normal = ai.build_render_policy(load_ratio=0.25, ai_operations=[{"op": "cold_open"}])
assert normal["max_ai_reencodes"] >= 2
assert normal["crf"] == 14

kwargs = ai.enhance_editor_kwargs(
    {
        "smart_reframe": False,
        "normalize_audio": False,
        "polish_audio": False,
        "subtitles_enabled": True,
        "fmt": "9:16 Short",
    },
    {"aiMode": "Auto Gaming", "captionMode": "Auto", "hudMode": "Off"},
)
assert kwargs["smart_reframe"] is True
assert kwargs["normalize_audio"] is True
assert kwargs["polish_audio"] is True
assert kwargs["ai_touch_assist"] is True

manual = ai.enhance_editor_kwargs(
    {"smart_reframe": False, "normalize_audio": False, "polish_audio": True, "subtitles_enabled": False},
    {"aiMode": "Off", "captionMode": "Off", "hudMode": "Off"},
)
assert manual["smart_reframe"] is False
assert manual["normalize_audio"] is False
assert manual["subtitles_enabled"] is False

bad_report = {
    "status": "warn",
    "facts": {
        "width": 720,
        "height": 1280,
        "fps": 30,
        "video_codec": "h264",
        "pixel_format": "yuv420p",
        "profile": "high",
        "audio_codec": "aac",
        "audio_rate": 48000,
        "audio_channels": 2,
    },
    "issues": [],
    "warnings": [],
}
actions = ai.quality_actions(bad_report)
assert actions and actions[0]["action"] == "rerender_canonical", actions
assert actions[0]["target"]["width"] == 1080
assert actions[0]["target"]["height"] == 1920

qc = load(ROOT / "quality_control_v124.py", "gsf_v124_quality")
assert hasattr(qc, "evaluate_media_facts"), "quality control needs a pure canonical evaluator"
canonical = qc.evaluate_media_facts(
    {
        "width": 1080,
        "height": 1920,
        "fps": 59.94,
        "video_codec": "h264",
        "pixel_format": "yuv420p",
        "profile": "High",
        "audio_codec": "aac",
        "audio_rate": 48000,
        "audio_channels": 2,
        "has_audio": True,
    }
)
assert "canonical_frame_mismatch" not in canonical["issues"]
assert "gaming_fps_below_target" not in canonical["warnings"]
noncanonical = qc.evaluate_media_facts(
    {
        "width": 720,
        "height": 1280,
        "fps": 30,
        "video_codec": "h264",
        "pixel_format": "yuv420p",
        "profile": "High",
        "audio_codec": "aac",
        "audio_rate": 44100,
        "audio_channels": 2,
        "has_audio": True,
    }
)
assert "canonical_frame_mismatch" in noncanonical["issues"]
assert "gaming_fps_below_target" in noncanonical["warnings"]
assert "audio_rate_noncanonical" in noncanonical["warnings"]

editor_src = (ROOT / "editor_2027_embed.py").read_text(encoding="utf-8")
pipeline_src = (ROOT / "director_pipeline_v142.py").read_text(encoding="utf-8")
exec_src = (ROOT / "director_render_exec_v143.py").read_text(encoding="utf-8")
start_src = (ROOT / "start_web.sh").read_text(encoding="utf-8")
fix_path = ROOT / "fix_v397_ai_monument.py"

assert "enhance_editor_kwargs" in editor_src
assert "build_render_policy" in pipeline_src and "ai_render_policy" in pipeline_src
assert "max_ai_reencodes" in exec_src
assert fix_path.is_file(), "missing restart-safe Editor AI monument migration"
fix_src = fix_path.read_text(encoding="utf-8")
for token in (
    "__GSF_AI_MONUMENT_V397",
    "touchstart",
    "touchmove",
    "touchend",
    "aiMonumentV397",
    "pinch",
    "double",
):
    assert token in fix_src, token
assert "fix_v397_ai_monument.py" in start_src
assert "test_v397_ai_monument.py" in start_src

print("V397 AI Monument + Quality: PASS")
