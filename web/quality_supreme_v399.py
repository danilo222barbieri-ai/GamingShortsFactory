from __future__ import annotations

import math
from typing import Any, Dict, Mapping


_BASE = {
    "codec": "libx264",
    "preset": "medium",
    "crf": 14,
    "profile": "high",
    "level": "4.2",
    "pix_fmt": "yuv420p",
    "fpsmax": 60,
    "width": 1080,
    "height": 1920,
    "threads": 2,
    "aq_mode": 3,
    "aq_strength": 1.0,
    "sharpen": False,
}


def _score(value: Any, default: float = 0.0) -> float:
    try:
        value = float(value)
    except Exception:
        return float(default)
    if not math.isfinite(value):
        return float(default)
    return max(0.0, min(1.0, value))


def _positive_int(value: Any, default: int = 0) -> int:
    try:
        value = int(value)
    except Exception:
        return int(default)
    return max(0, value)


def quality_profile(metadata: Any = None) -> Dict[str, Any]:
    """Return the bounded V399 social-master encoding policy.

    V399 deliberately keeps the proven x264 medium / H.264 High / yuv420p
    baseline.  Scene intelligence may spend a little more bitrate on genuine
    high-motion/high-detail gameplay, but it may never switch to a slower
    preset or reduce compatibility.  Missing or malformed AI metadata simply
    falls back to the V398 master profile.
    """
    data: Mapping[str, Any] = metadata if isinstance(metadata, Mapping) else {}
    motion = _score(data.get("motion"))
    detail = _score(data.get("detail"))
    action = _score(data.get("action_peak"))
    source_w = _positive_int(data.get("source_width"))
    source_h = _positive_int(data.get("source_height"))

    profile = dict(_BASE)

    # A source whose long edge is below Full HD should not receive artificial
    # bitrate/sharpening just because an AI score is noisy.
    source_known = source_w > 0 and source_h > 0
    low_source = source_known and max(source_w, source_h) < 1920

    complexity = 0.46 * motion + 0.34 * detail + 0.20 * action
    if not low_source and complexity >= 0.78 and max(motion, action) >= 0.82:
        profile["crf"] = 13
        profile["aq_strength"] = 1.15
    elif not low_source and complexity >= 0.62:
        profile["crf"] = 14
        profile["aq_strength"] = 1.08

    # Sharpening is intentionally conservative. It is only a policy hint for
    # future filter stages; V399 detail protection primarily uses bitrate/AQ,
    # avoiding halos around HUD text and subtitles.
    profile["sharpen"] = bool(
        not low_source
        and source_known
        and min(source_w, source_h) >= 1080
        and detail >= 0.88
        and motion <= 0.72
    )
    profile["complexity"] = round(complexity, 4)
    profile["source_low_resolution"] = bool(low_source)
    return profile


def encoder_args(
    metadata_or_profile: Any = None,
    *,
    has_audio: bool = True,
    audio_mode: str = "encode",
) -> list[str]:
    """Build the single V399 FFmpeg tail shared by post-master re-encoders."""
    if isinstance(metadata_or_profile, Mapping) and metadata_or_profile.get("codec"):
        p = dict(metadata_or_profile)
    else:
        p = quality_profile(metadata_or_profile)

    crf = max(12, min(14, _positive_int(p.get("crf"), 14)))
    aq_strength = max(0.8, min(1.3, float(p.get("aq_strength", 1.0) or 1.0)))
    threads = max(1, min(2, _positive_int(p.get("threads"), 2)))

    out = [
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", str(crf),
        "-pix_fmt", "yuv420p",
        "-profile:v", "high",
        "-level:v", "4.2",
        "-threads", str(threads),
        "-x264-params",
        f"aq-mode=3:aq-strength={aq_strength:.2f}:rc-lookahead=16:ref=2:bframes=2",
    ]
    if has_audio:
        if str(audio_mode).lower() == "copy":
            out += ["-c:a", "copy"]
        else:
            out += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
    else:
        out += ["-an"]
    out += ["-movflags", "+faststart"]
    return out
