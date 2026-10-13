from __future__ import annotations

from typing import Any


CANONICAL_TARGET = {
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


def _ratio(value: Any) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return 0.0


def build_render_policy(load_ratio: float = 0.0, ai_operations=None) -> dict:
    """Return a quality-first render policy for AI-directed Shorts.

    Worker pressure is allowed to reduce optional creative re-encodes, never the
    canonical delivery target. This keeps the expensive part adaptive without
    silently turning a 1080x1920/60 Short into a lower-quality export.
    """
    load = _ratio(load_ratio)
    op_count = len([x for x in (ai_operations or []) if isinstance(x, dict)])
    if load >= 0.85:
        max_reencodes = 1
        pressure = "high"
    elif load >= 0.65:
        max_reencodes = 2
        pressure = "medium"
    else:
        max_reencodes = 3
        pressure = "normal"
    if op_count:
        max_reencodes = min(max_reencodes, max(1, op_count))
    return {
        "engine": "v397-ai-render-policy",
        "target": dict(CANONICAL_TARGET),
        "quality_floor": "canonical",
        "crf": 14,
        "preset": "medium",
        "single_pass_preferred": True,
        "max_ai_reencodes": int(max_reencodes),
        "worker_pressure": pressure,
        "load_ratio": round(load, 3),
        "drop_quality_to_save_time": False,
        "optional_effects_may_degrade": True,
    }


def enhance_editor_kwargs(kwargs: dict | None, state: dict | None) -> dict:
    """Blend AI assistance into Editor render kwargs without overriding AI-Off."""
    out = dict(kwargs or {})
    state = dict(state or {})
    mode = str(state.get("aiMode") or "Off").strip().lower()
    auto_gaming = mode in {"auto gaming", "auto", "gaming", "smart"}
    if not auto_gaming:
        out["ai_touch_assist"] = False
        return out

    # Auto Gaming is an assistant, not a destructive preset: it only promotes
    # proven quality helpers and keeps explicit captions/format choices intact.
    out["smart_reframe"] = True
    out["normalize_audio"] = True
    out["polish_audio"] = True
    out["ai_touch_assist"] = True
    out["ai_mode"] = "Auto Gaming"
    return out


def quality_actions(report: dict | None) -> list[dict]:
    """Translate explainable final-QC facts into concrete AI remediation."""
    report = dict(report or {})
    facts = dict(report.get("facts") or {})
    issues = set(report.get("issues") or [])
    warnings = set(report.get("warnings") or [])

    width = int(facts.get("width") or 0)
    height = int(facts.get("height") or 0)
    try:
        fps = float(facts.get("fps") or 0.0)
    except Exception:
        fps = 0.0
    vcodec = str(facts.get("video_codec") or "").lower()
    pix = str(facts.get("pixel_format") or "").lower()
    profile = str(facts.get("profile") or "").lower()

    canonical_video = (
        width == CANONICAL_TARGET["width"]
        and height == CANONICAL_TARGET["height"]
        and fps >= 59.0
        and vcodec == "h264"
        and pix == "yuv420p"
        and profile in {"high", "high 10", "high 4:2:2", "high 4:4:4 predictive"}
    )
    if not canonical_video or "canonical_frame_mismatch" in issues:
        return [{
            "action": "rerender_canonical",
            "reason": "final_video_outside_quality_floor",
            "target": dict(CANONICAL_TARGET),
            "crf": 14,
            "preset": "medium",
        }]

    actions = []
    if warnings.intersection({"audio_rate_noncanonical", "audio_codec_noncanonical", "audio_channels_noncanonical", "audio_near_clipping", "audio_very_low"}):
        actions.append({
            "action": "repair_audio",
            "target": {
                "audio_codec": "aac",
                "audio_rate": 48000,
                "audio_channels": 2,
            },
        })
    if "black_frames_detected" in warnings:
        actions.append({"action": "review_edges", "reason": "black_frames_detected"})
    return actions
