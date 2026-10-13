from __future__ import annotations

import math
from typing import Any, Dict, Mapping

from quality_supreme_v399 import quality_profile


_QUALITY_MODES = ("Fast HQ", "Max Quality", "Adaptive AI")


def quality_modes() -> tuple[str, str, str]:
    """Public V400 quality-mode contract used by UI/editor/render code."""
    return _QUALITY_MODES


def _finite(value: Any, fallback: float) -> float:
    try:
        value = float(value)
    except Exception:
        return float(fallback)
    if not math.isfinite(value):
        return float(fallback)
    return value


def hidpi_profile(
    device_pixel_ratio: Any = 1.0,
    *,
    viewport_width: Any = 0,
    coarse_pointer: bool = False,
) -> Dict[str, Any]:
    """Return a bounded display-density policy for the Game Editor.

    Browser DPR is intentionally capped: the UI stays vector-first and we do
    not multiply video decode/render workload merely because a phone reports a
    very high density.  The profile is metadata for the editor; CSS pixels and
    the 1080x1920 export master remain unchanged.
    """
    dpr = max(1.0, min(3.0, _finite(device_pixel_ratio, 1.0)))
    width = max(0, int(_finite(viewport_width, 0.0)))
    touch = bool(coarse_pointer)
    return {
        "pixel_ratio": round(dpr, 2),
        "retina": dpr >= 1.5,
        "density": "retina" if dpr >= 1.5 else "standard",
        "vector_ui": True,
        "viewport_width": width,
        "coarse_pointer": touch,
        "touch_target_px": 48 if touch else 40,
        "raster_scale": 1.0,
    }


def adaptive_quality_profile(metadata: Any = None) -> Dict[str, Any]:
    """Resolve V400's approved Fast HQ / Max Quality / Adaptive AI modes.

    V400 extends, rather than replaces, V399 Quality Supreme.  All modes keep
    libx264 medium, H.264 High, yuv420p and the 1080x1920 master.  The AI mode
    can spend CRF/AQ only inside the V399 compatibility envelope, while source
    awareness prevents fake detail on low-resolution uploads.
    """
    data: Mapping[str, Any] = metadata if isinstance(metadata, Mapping) else {}
    requested = str(data.get("quality_mode") or "Adaptive AI")
    mode = requested if requested in _QUALITY_MODES else "Adaptive AI"

    # Start from the already-proven V399 scene-aware policy.
    profile = quality_profile(data)
    low_source = bool(profile.get("source_low_resolution"))

    if mode == "Fast HQ":
        profile["crf"] = 14
        profile["aq_strength"] = 1.0
        profile["sharpen"] = False
        ai_directed = False
    elif mode == "Max Quality":
        # Keep preset=medium so fidelity rises without changing the proven
        # throughput class.  Low-resolution sources still avoid fake detail.
        profile["crf"] = 13 if low_source else 12
        profile["aq_strength"] = 1.10 if low_source else 1.18
        profile["sharpen"] = bool(profile.get("sharpen")) and not low_source
        ai_directed = False
    else:
        ai_directed = True

    profile["quality_mode"] = mode
    profile["ai_directed"] = ai_directed
    profile["detail_restore"] = (
        "edge-safe"
        if bool(profile.get("sharpen")) and not low_source
        else "off"
    )
    profile["hidpi_ui"] = True
    profile["vector_ui"] = True
    return profile
