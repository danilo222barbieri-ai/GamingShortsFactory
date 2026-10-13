"""V402 deterministic evidence fusion for Auto Highlights.

This module is intentionally pure: no media decode, network, persistence or model
calls. It enriches existing event evidence before the production Game Brain does
final ranking/diversification.
"""
from __future__ import annotations

import math
from typing import Any

ENGINE_VERSION = "highlight-fusion-v402"

_SEMANTIC_PRIOR = {
    "multi_kill": .99,
    "clutch": .98,
    "victory": .97,
    "goal": .95,
    "boss": .91,
    "overtake": .87,
    "save": .84,
    "kill": .80,
    "reaction": .78,
    "impact": .73,
    "crash": .72,
    "assist": .64,
    "shot": .58,
    "death": .40,
    "silence": .08,
    "highlight": .56,
    "peak": .60,
}


def _num(value: Any, default: float = 0.0) -> float:
    try:
        value = float(value)
        return value if math.isfinite(value) else float(default)
    except Exception:
        return float(default)


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    return max(float(low), min(float(high), _num(value, low)))


def _label(value: Any) -> str:
    text = str(value or "highlight").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "multikill": "multi_kill",
        "multi_kill": "multi_kill",
        "win": "victory",
        "winner": "victory",
        "headshot": "kill",
        "explosion": "impact",
        "ko": "death",
    }
    text = aliases.get(text, text)
    return text[:48] or "highlight"


def _rows(value: Any) -> tuple[list[dict[str, Any]], int]:
    if not isinstance(value, (list, tuple)):
        return [], 0 if value in (None, ()) else 1
    out: list[dict[str, Any]] = []
    ignored = 0
    for row in value:
        if not isinstance(row, dict):
            ignored += 1
            continue
        t = _num(row.get("time"), float("nan"))
        if not math.isfinite(t) or t < 0:
            ignored += 1
            continue
        clean = dict(row)
        clean["time"] = t
        out.append(clean)
    return out, ignored


def _nearest_rows(rows: list[dict[str, Any]], event_time: float, window: float) -> dict[str, Any]:
    best = None
    for row in rows:
        dist = abs(_num(row.get("time"), -9999.0) - event_time)
        if dist <= window and (best is None or dist < best[0]):
            best = (dist, row)
    return dict(best[1]) if best else {}


def _nearest_diagnostic(diagnostics: Any, event_time: float, window: float) -> dict[str, Any]:
    if not isinstance(diagnostics, dict):
        return {}
    best = None
    for key, value in diagnostics.items():
        if str(key).startswith("__") or not isinstance(value, dict):
            continue
        try:
            at = float(key)
        except Exception:
            at = _num(value.get("time"), float("nan"))
        if not math.isfinite(at):
            continue
        dist = abs(at - event_time)
        if dist <= window and (best is None or dist < best[0]):
            best = (dist, value)
    return dict(best[1]) if best else {}


def _hud(raw: Any) -> list[str]:
    out: list[str] = []
    if not isinstance(raw, (list, tuple, set)):
        return out
    for value in raw:
        text = str(value or "").strip().lower().replace(" ", "_")[:32]
        if text and text not in out:
            out.append(text)
        if len(out) >= 8:
            break
    return out


def _available_weighted(parts: list[tuple[float, float, bool]]) -> float:
    total = 0.0
    weights = 0.0
    for value, weight, available in parts:
        if not available:
            continue
        total += _clamp(value) * float(weight)
        weights += float(weight)
    return total / weights if weights else 0.0


def _window_hints(label: str, duration: float) -> tuple[float, float]:
    d = max(5.0, min(60.0, _num(duration, 30.0)))
    if label in {"clutch", "multi_kill", "victory", "goal"}:
        lead = min(8.0, max(2.5, d * .30))
        after = min(6.0, max(2.2, d * .24))
    elif label in {"reaction", "crash", "boss"}:
        lead = min(6.0, max(2.0, d * .24))
        after = min(8.0, max(2.8, d * .30))
    else:
        lead = min(8.0, max(2.0, d * .30))
        after = min(5.0, max(1.8, d * .22))
    if lead + after > d:
        scale = d / max(.001, lead + after)
        lead *= scale
        after *= scale
    return round(lead, 3), round(after, 3)


def _reason(label: str, hud: list[str], reaction: float, action: float, visual_quality: float) -> str:
    parts = [label.upper().replace("_", " ")]
    if "killfeed" in hud:
        parts.append("Killfeed")
    elif "minimap" in hud:
        parts.append("Minimap")
    if reaction >= .62:
        parts.append("Reaction")
    if action >= .70:
        parts.append("High Action")
    elif visual_quality >= .82:
        parts.append("Strong Visual")
    return " · ".join(parts[:5])


def _fuse_one(
    event: dict[str, Any],
    *,
    diagnostics: Any,
    visual_rows: list[dict[str, Any]],
    audio_rows: list[dict[str, Any]],
    target_duration: float,
) -> dict[str, Any] | None:
    t = _num(event.get("time"), float("nan"))
    if not math.isfinite(t) or t < 0:
        return None

    row = dict(event)
    row["time"] = t
    label = _label(event.get("semantic") or event.get("kind"))
    kind = str(event.get("kind") or "").upper()
    window = max(2.0, min(12.0, float(target_duration) * .42))
    diag = _nearest_diagnostic(diagnostics, t, window)
    features = dict(diag.get("features") or {}) if isinstance(diag, dict) else {}
    visual = _nearest_rows(visual_rows, t, max(1.5, min(8.0, float(target_duration) * .28)))
    audio = _nearest_rows(audio_rows, t, max(1.5, min(8.0, float(target_duration) * .28)))

    base = _clamp(event.get("score"))
    semantic_conf = _clamp(event.get("semantic_confidence"))
    semantic_excite = _clamp(event.get("semantic_excitement"))
    semantic_raw = _clamp(event.get("semantic_score"))
    semantic_prior = _SEMANTIC_PRIOR.get(label, .56)
    semantic_available = bool(event.get("semantic")) or semantic_raw > 0 or semantic_conf > 0
    semantic_signal = max(
        semantic_raw,
        .70 * semantic_conf + .30 * semantic_excite,
        semantic_prior if semantic_available else 0.0,
    )

    diag_event = _clamp(features.get("event_score"))
    event_signal = max(base, diag_event)

    diag_motion = max(_clamp(features.get("motion_burst")), _clamp(features.get("motion_avg")))
    visual_action = max(
        _clamp(visual.get("action_score")),
        _clamp(visual.get("motion_burst")),
        _clamp(visual.get("motion")),
        diag_motion,
    )
    visual_quality = _clamp(visual.get("visual_quality"))
    subject = _clamp(visual.get("subject_score"))
    sharpness = _clamp(visual.get("sharpness"))
    visual_available = bool(visual) or any(k in features for k in ("motion_burst", "motion_avg"))
    visual_signal = _available_weighted([
        (visual_action, .58, visual_action > 0 or visual_available),
        (subject, .17, "subject_score" in visual),
        (visual_quality, .17, "visual_quality" in visual),
        (sharpness, .08, "sharpness" in visual),
    ])

    event_reaction = _clamp(event.get("semantic_reaction"))
    diag_reaction = max(_clamp(features.get("reaction")), _clamp(features.get("reaction_cue")))
    audio_reaction = max(_clamp(audio.get("reaction")), _clamp(audio.get("reaction_score")))
    audio_peak = _clamp(audio.get("audio_peak"))
    audio_excite = max(_clamp(audio.get("excitement")), _clamp(audio.get("semantic_excitement")))
    reaction_strength = max(event_reaction, diag_reaction, audio_reaction)
    reaction_available = reaction_strength > 0 or bool(audio) or any(k in features for k in ("reaction", "reaction_cue"))
    reaction_signal = _available_weighted([
        (reaction_strength, .62, reaction_strength > 0 or reaction_available),
        (audio_peak, .20, "audio_peak" in audio),
        (audio_excite, .18, bool(audio_excite) or "excitement" in audio),
    ])

    hud = _hud(event.get("hud_elements"))
    if not hud:
        hud = _hud(visual.get("hud_elements"))
    hud_signal = .92 if "killfeed" in hud else (.80 if "minimap" in hud else (.70 if hud else 0.0))

    synergy = _clamp(features.get("synergy"))
    arc = _clamp(features.get("arc"))
    setup = _clamp(features.get("setup_score"))
    aftermath = _clamp(features.get("aftermath_score"))
    context_available = any(k in features for k in ("synergy", "arc", "setup_score", "aftermath_score"))
    context_signal = max(synergy, _available_weighted([
        (arc, .40, "arc" in features),
        (setup, .28, "setup_score" in features),
        (aftermath, .32, "aftermath_score" in features),
    ]))

    score = _available_weighted([
        (event_signal, .28, True),
        (semantic_signal, .26, semantic_available),
        (visual_signal, .20, visual_available),
        (reaction_signal, .17, reaction_available),
        (hud_signal, .05, bool(hud)),
        (context_signal, .04, context_available),
    ])

    strong = [
        event_signal >= .62,
        semantic_available and semantic_signal >= .70,
        visual_available and visual_signal >= .62,
        reaction_available and reaction_signal >= .62,
        bool(hud) and hud_signal >= .70,
        context_available and context_signal >= .65,
    ]
    corroboration = sum(1 for x in strong if x)
    score += min(.085, max(0, corroboration - 1) * .018)

    dead = max(_clamp(features.get("dead_ratio")), _clamp(features.get("dead_streak_ratio")))
    if kind == "SILENCE" or label == "silence":
        score = min(score * .12, .10)
    else:
        score -= .14 * dead
        if label == "death":
            score -= .045
        if visual and "visual_quality" in visual and visual_quality < .22:
            score -= min(.055, (.22 - visual_quality) * .25)
    score = _clamp(score)

    confidence = .40 + min(.34, corroboration * .055) + .16 * semantic_conf + .07 * min(1.0, score)
    if semantic_available and semantic_conf == 0:
        confidence += .025
    confidence = _clamp(confidence)

    signals = ["event"]
    if semantic_available and semantic_signal >= .55:
        signals.append("semantic")
    if visual_available and visual_signal >= .52:
        signals.append("visual")
    if reaction_available and reaction_signal >= .52:
        signals.append("reaction")
    if hud:
        signals.append("hud")
    if context_available and context_signal >= .55:
        signals.append("context")

    lead, after = _window_hints(label, target_duration)
    row.update({
        "fusion_score": round(score, 6),
        "fusion_confidence": round(confidence, 6),
        "fusion_signals": signals,
        "fusion_reason": _reason(label, hud, reaction_signal, visual_action, visual_quality),
        "fusion_version": "v402",
        "peak_time": round(t, 3),
        "lead_seconds": lead,
        "aftermath_seconds": after,
    })
    return row


def _dedupe(rows: list[dict[str, Any]], target_duration: float) -> tuple[list[dict[str, Any]], int]:
    gap = max(1.5, min(3.5, float(target_duration) * .08))
    kept: list[dict[str, Any]] = []
    dropped = 0
    for row in sorted(rows, key=lambda x: (_num(x.get("time")), _label(x.get("semantic") or x.get("kind")))):
        label = _label(row.get("semantic") or row.get("kind"))
        match_index = None
        for index, old in enumerate(kept):
            if _label(old.get("semantic") or old.get("kind")) != label:
                continue
            if abs(_num(old.get("peak_time"), old.get("time")) - _num(row.get("peak_time"), row.get("time"))) <= gap:
                match_index = index
                break
        if match_index is None:
            kept.append(row)
            continue
        old = kept[match_index]
        new_key = (_num(row.get("fusion_score")), _num(row.get("fusion_confidence")), -_num(row.get("time")))
        old_key = (_num(old.get("fusion_score")), _num(old.get("fusion_confidence")), -_num(old.get("time")))
        if new_key > old_key:
            kept[match_index] = row
        dropped += 1
    kept.sort(key=lambda x: _num(x.get("time")))
    return kept, dropped


def fuse_highlight_evidence(
    events: Any,
    diagnostics: Any = None,
    visual_observations: Any = None,
    audio_observations: Any = None,
    target_duration: float = 30,
    genre: str = "Auto",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Fuse local/semantic/visual/reaction evidence without changing ranking authority."""
    duration = max(5.0, min(60.0, _num(target_duration, 30.0)))
    raw_events = list(events) if isinstance(events, (list, tuple)) else []
    visual_rows, ignored_visual = _rows(visual_observations)
    audio_rows, ignored_audio = _rows(audio_observations)

    enriched: list[dict[str, Any]] = []
    invalid_events = 0
    for raw in raw_events:
        if not isinstance(raw, dict):
            invalid_events += 1
            continue
        fused = _fuse_one(
            raw,
            diagnostics=diagnostics,
            visual_rows=visual_rows,
            audio_rows=audio_rows,
            target_duration=duration,
        )
        if fused is None:
            invalid_events += 1
            continue
        enriched.append(fused)

    fused_rows, deduped = _dedupe(enriched, duration)
    family_counts = {key: 0 for key in ("event", "semantic", "visual", "reaction", "hud", "context")}
    for row in fused_rows:
        for key in row.get("fusion_signals") or []:
            if key in family_counts:
                family_counts[key] += 1

    meta = {
        "engine": ENGINE_VERSION,
        "version": "v402",
        "fallback": False,
        "genre": str(genre or "Auto"),
        "raw_event_count": len(raw_events),
        "fused_count": len(fused_rows),
        "deduped_count": deduped,
        "invalid_event_count": invalid_events,
        "ignored_visual_count": ignored_visual,
        "ignored_audio_count": ignored_audio,
        "signal_family_counts": family_counts,
    }
    return fused_rows, meta
