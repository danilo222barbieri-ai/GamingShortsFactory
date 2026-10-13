#!/usr/bin/env python3
from __future__ import annotations

import math

from highlight_fusion_v402 import fuse_highlight_evidence
from auto_highlights.engine_v129 import analysis_to_candidates
import auto_highlights.engine_v129 as engine_v129


def need(ok, msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:", msg)


def event(time, semantic, score=.72, *, kind="IMPACT", semantic_score=.74,
          semantic_confidence=.80, reaction=0.0, hud=None, source="local"):
    return {
        "time": float(time),
        "kind": kind,
        "semantic": semantic,
        "score": score,
        "semantic_score": semantic_score,
        "semantic_confidence": semantic_confidence,
        "semantic_reaction": reaction,
        "hud_elements": list(hud or []),
        "source": source,
    }


events = [
    event(20, "kill", hud=["killfeed"]),
    event(60, "kill"),
    event(100, "clutch", score=.70, semantic_score=.94, semantic_confidence=.96,
          reaction=.72, hud=["killfeed", "minimap"]),
    event(101.2, "clutch", score=.60, semantic_score=.78, semantic_confidence=.80),
    event(140, "reaction", score=.76, semantic_score=.82, semantic_confidence=.88,
          reaction=.97),
    event(180, "silence", score=.99, kind="SILENCE", semantic_score=.99,
          semantic_confidence=.99),
]

diagnostics = {
    "20.0": {"features": {"event_score": .76, "motion_burst": .94, "reaction": .86,
                            "synergy": .82, "dead_ratio": .01}},
    "60.0": {"features": {"event_score": .76, "motion_burst": .30, "reaction": .08,
                            "synergy": .20, "dead_ratio": .02}},
    "100.0": {"features": {"event_score": .95, "motion_burst": .83, "reaction": .72,
                             "arc": .90, "setup_score": .76, "aftermath_score": .88}},
    "140.0": {"features": {"event_score": .80, "motion_burst": .46, "reaction": .98,
                             "synergy": .75}},
}

visual = [
    {"time": 20.0, "action_score": .95, "subject_score": .84, "visual_quality": .91,
     "sharpness": .86},
    {"time": 60.0, "action_score": .24, "subject_score": .50, "visual_quality": .82,
     "sharpness": .70},
    {"time": 100.0, "action_score": .86, "subject_score": .83, "visual_quality": .92,
     "sharpness": .87},
    {"time": 140.0, "action_score": .44, "subject_score": .65, "visual_quality": .88,
     "sharpness": .76},
]

audio = [
    {"time": 20.0, "reaction": .90, "audio_peak": .92, "excitement": .88},
    {"time": 60.0, "reaction": .06, "audio_peak": .22, "excitement": .18},
    {"time": 100.0, "reaction": .74, "audio_peak": .80, "excitement": .84},
    {"time": 140.0, "reaction": .98, "audio_peak": .90, "excitement": .94},
]

fused, fusion_meta = fuse_highlight_evidence(
    events,
    diagnostics=diagnostics,
    visual_observations=visual,
    audio_observations=audio,
    target_duration=30,
    genre="FPS",
)
need(fusion_meta.get("engine") == "highlight-fusion-v402",
     "V402 exposes its fusion engine identity")
need(fusion_meta.get("fallback") is False,
     "direct V402 fusion reports normal non-fallback execution")
need(all(row.get("fusion_version") == "v402" for row in fused),
     "every fused event carries the V402 version marker")
need(all(math.isfinite(float(row.get("fusion_score", -1))) and 0.0 <= float(row["fusion_score"]) <= 1.0 for row in fused),
     "fusion scores are finite and bounded")
need(all(math.isfinite(float(row.get("fusion_confidence", -1))) and 0.0 <= float(row["fusion_confidence"]) <= 1.0 for row in fused),
     "fusion confidence is finite and bounded")

by_time = {round(float(row["time"]), 1): row for row in fused}
need(20.0 in by_time and 60.0 in by_time,
     "both separated kill events survive fusion")
need(float(by_time[20.0]["fusion_score"]) > float(by_time[60.0]["fusion_score"]),
     "multi-signal kill outranks an equivalent plain kill")
need("visual" in by_time[20.0].get("fusion_signals", []) and
     "reaction" in by_time[20.0].get("fusion_signals", []) and
     "hud" in by_time[20.0].get("fusion_signals", []),
     "strong kill records corroborating visual/reaction/HUD families")
need("Killfeed" in by_time[20.0].get("fusion_reason", "") and
     "Reaction" in by_time[20.0].get("fusion_reason", ""),
     "fusion reason explains real corroborating evidence")

clutches = [row for row in fused if str(row.get("semantic") or "").lower() == "clutch"]
need(len(clutches) == 1 and abs(float(clutches[0]["time"]) - 100.0) < .01,
     "near-duplicate clutch evidence collapses to the stronger peak")
need(fusion_meta.get("deduped_count", 0) >= 1,
     "fusion metadata reports duplicate collapse")
need(float(clutches[0]["fusion_score"]) > float(by_time[60.0]["fusion_score"]),
     "high-value clutch priority survives signal fusion")
need(float(clutches[0].get("lead_seconds", 99)) + float(clutches[0].get("aftermath_seconds", 99)) <= 30.0,
     "peak window hints never exceed requested clip duration")

silence = [row for row in fused if str(row.get("kind") or "").upper() == "SILENCE"]
need(not silence or float(silence[0]["fusion_score"]) < float(by_time[60.0]["fusion_score"]),
     "silence/dead-air cannot outrank a valid gameplay event")

# Missing optional evidence is neutral; malformed optional rows are ignored.
base_only, _ = fuse_highlight_evidence([event(30, "kill")], target_duration=15, genre="FPS")
malformed, _ = fuse_highlight_evidence(
    [event(30, "kill")],
    visual_observations=[None, "bad", {"time": "nan", "action_score": object()}],
    audio_observations=[42, {"time": "oops", "reaction": "nan"}],
    target_duration=15,
    genre="FPS",
)
need(base_only == malformed,
     "malformed optional observations are ignored exactly like missing observations")
need(float(base_only[0]["fusion_score"]) > 0.0,
     "missing visual/audio evidence never suppresses a valid event")

# Non-finite/extreme input must never escape the fusion boundary.
weird, _ = fuse_highlight_evidence([
    {"time": 8.0, "kind": "IMPACT", "semantic": "kill", "score": float("inf"),
     "semantic_score": float("nan"), "semantic_confidence": -999,
     "semantic_reaction": 999},
], target_duration=15)
need(len(weird) == 1 and math.isfinite(float(weird[0]["fusion_score"])) and
     math.isfinite(float(weird[0]["fusion_confidence"])),
     "non-finite/extreme evidence is normalized safely")

# Same input must produce exactly the same order, scores and reasons.
fused_again, meta_again = fuse_highlight_evidence(
    events, diagnostics=diagnostics, visual_observations=visual,
    audio_observations=audio, target_duration=30, genre="FPS",
)
need(fused_again == fused and meta_again == fusion_meta,
     "V402 fusion is deterministic for identical inputs")

analysis = {
    "engine_version": "v52-keyframe-turbo",
    "scan": {
        "event_map_v108": events,
        "diagnostics": diagnostics,
        "visual_observations": visual,
        "audio_observations": audio,
        "meta": {"duration": 220.0},
    },
}

for seconds in (15, 30):
    candidates, meta = analysis_to_candidates(
        analysis, target_highlights=3, target_duration=seconds, genre="FPS"
    )
    need(candidates and all(abs(x.duration - seconds) < 1e-9 for x in candidates),
         f"Auto Highlights keeps exact {seconds}s candidate duration")
    need(meta.get("fusion", {}).get("engine") == "highlight-fusion-v402" and
         meta.get("fusion", {}).get("fallback") is False,
         f"Auto Highlights exposes live V402 fusion metadata at {seconds}s")
    selected = list(meta.get("game_brain", {}).get("selected") or [])
    need(selected and all(
        "fusion_reason" in row and "fusion_signals" in row and
        "fusion_score" in row and "fusion_confidence" in row
        for row in selected
    ), f"selected Game Brain rows retain V402 explainability at {seconds}s")
    starts = [float(x.start_seconds) for x in candidates]
    need(len(starts) == len(set(round(x, 3) for x in starts)),
         f"deduped evidence does not produce duplicate {seconds}s candidates")

many, many_meta = analysis_to_candidates(
    {"scan": {"event_map_v108": [event(20, "kill"), event(80, "reaction", reaction=.9)]}},
    target_highlights=8,
    target_duration=15,
    genre="FPS",
)
need(len(many) <= 2 and many_meta.get("selected_count") == len(many),
     "requesting excess highlights does not fabricate filler candidates")

# Fusion integration must fail soft back to the original V129 event path.
original_fuse = engine_v129.fuse_highlight_evidence
try:
    def explode(*args, **kwargs):
        raise RuntimeError("synthetic fusion failure for fallback contract")
    engine_v129.fuse_highlight_evidence = explode
    fallback_candidates, fallback_meta = engine_v129.analysis_to_candidates(
        analysis, target_highlights=3, target_duration=30, genre="FPS"
    )
finally:
    engine_v129.fuse_highlight_evidence = original_fuse
need(bool(fallback_candidates),
     "fusion exception falls back to original V129 candidates")
need(fallback_meta.get("fusion", {}).get("fallback") is True,
     "fusion exception is visible in metadata")
need(len(str(fallback_meta.get("fusion", {}).get("reason") or "")) <= 180,
     "fusion fallback diagnostic is bounded")

print("V402 Game Brain / Auto Highlights 2.0 contract: PASS")
