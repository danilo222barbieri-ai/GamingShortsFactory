#!/usr/bin/env python3
from pathlib import Path

from ai_hidpi_v400 import adaptive_quality_profile, hidpi_profile, quality_modes


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:", msg)


need(quality_modes() == ("Fast HQ", "Max Quality", "Adaptive AI"),
     "V400 exposes the three approved quality modes")

retina = hidpi_profile(2.0, viewport_width=390, coarse_pointer=True)
need(retina["pixel_ratio"] == 2.0 and retina["retina"],
     "2x mobile displays are detected as Retina/Hi-DPI")
need(retina["touch_target_px"] >= 44,
     "coarse-pointer controls preserve a finger-safe target")

extreme = hidpi_profile(9.0, viewport_width=1920, coarse_pointer=False)
need(extreme["pixel_ratio"] <= 3.0,
     "pathological DPR values are bounded")
need(extreme["vector_ui"],
     "Hi-DPI keeps the UI vector-first rather than raster-scaling icons")

adaptive = adaptive_quality_profile({
    "quality_mode": "Adaptive AI",
    "motion": 0.94,
    "detail": 0.91,
    "action_peak": 0.96,
    "source_width": 2560,
    "source_height": 1440,
})
need(adaptive["preset"] == "medium" and adaptive["codec"] == "libx264",
     "Adaptive AI keeps the proven V399 encoder baseline")
need(12 <= int(adaptive["crf"]) <= 14,
     "Adaptive AI spends quality without leaving the bounded CRF contract")
need(adaptive["width"] == 1080 and adaptive["height"] == 1920,
     "V400 keeps the single 1080x1920 vertical master")
need(adaptive["ai_directed"],
     "Adaptive AI marks scene-driven quality decisions explicitly")

low = adaptive_quality_profile({
    "quality_mode": "Adaptive AI",
    "motion": 0.20,
    "detail": 0.30,
    "source_width": 720,
    "source_height": 1280,
})
need(low["source_low_resolution"],
     "source-aware AI detects low-resolution inputs")
need(low["detail_restore"] in {"off", "edge-safe"},
     "low-resolution sources avoid fake-detail enhancement")

maxq = adaptive_quality_profile({"quality_mode": "Max Quality", "source_width": 1920, "source_height": 1080})
need(int(maxq["crf"]) <= 13 and maxq["preset"] == "medium",
     "Max Quality increases fidelity without switching to a slower preset")

fast = adaptive_quality_profile({"quality_mode": "Fast HQ", "motion": 1.0, "detail": 1.0})
need(int(fast["crf"]) == 14 and fast["preset"] == "medium",
     "Fast HQ is deterministic and stays on the proven medium baseline")

component = Path("web/editor_2027_component/index.html").read_text(encoding="utf-8")
need("window.devicePixelRatio" in component,
     "Game Editor measures browser devicePixelRatio")
need("data-v400-hidpi" in component,
     "Game Editor exposes a V400 Hi-DPI runtime marker")
need("shape-rendering:geometricPrecision" in component,
     "SVG controls request geometric precision on Hi-DPI displays")

embed = Path("web/editor_2027_embed.py").read_text(encoding="utf-8")
need("ai_hidpi_v400" in embed and "v400_profile" in embed,
     "Editor bridge carries the V400 AI/Hi-DPI profile without replacing the approved UI")

print("V400 AI + Hi-DPI contract: PASS")
