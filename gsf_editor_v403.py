"""Pure support engine for Gaming Shorts Factory Game Editor V403.

The module intentionally has no Streamlit dependency.  It models edit decisions,
history, Smart Timeline markers and deterministic Game Director suggestions so the
UI can rerun without losing the project state and the behavior stays unit-testable.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping


TOOLS = ("FRAME", "CAPTION", "LOOK", "AUDIO", "AI")
FORMATS = ("9:16 Short", "16:9 Originale")
COMPARE_MODES = ("EDITED", "ORIGINAL")
MARKER_TYPES = {
    "ACTION_PEAK",
    "KILL",
    "AIM",
    "SPEECH",
    "HOOK",
    "CUT",
    "FACE_CAM",
    "MINIMAP",
    "KILLFEED",
    "PLAYER",
}

_MARKER_LABELS = {
    "ACTION_PEAK": "Action peak",
    "KILL": "Kill",
    "AIM": "Aim",
    "SPEECH": "Voce",
    "HOOK": "Hook",
    "CUT": "Cut",
    "FACE_CAM": "Face cam",
    "MINIMAP": "Minimap",
    "KILLFEED": "Killfeed",
    "PLAYER": "Player",
}


def _number(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(fallback)


def _clamp(value: Any, low: float, high: float, fallback: float | None = None) -> float:
    parsed = _number(value, low if fallback is None else fallback)
    return max(float(low), min(float(high), parsed))


def _clean_bool(value: Any, fallback: bool) -> bool:
    if isinstance(value, bool):
        return value
    return bool(fallback)


def default_editor_state(source_duration: float, preferred_duration: float = 15.0) -> dict[str, Any]:
    """Return the canonical, non-destructive edit-decision document."""
    duration = max(0.5, _number(source_duration, 0.5))
    scene = max(0.5, min(duration, _number(preferred_duration, 15.0)))
    return {
        "version": 403,
        "source_duration": duration,
        "start": 0.0,
        "end": scene,
        "format": "9:16 Short",
        "zoom": 1.0,
        "x": 0,
        "y": 0,
        "volume": 100,
        "speed": 1.0,
        "brightness": 0.0,
        "contrast": 1.0,
        "subtitles_enabled": True,
        "subtitle_y": 78,
        "safe_zones": True,
        "focus_mode": False,
        "compare_mode": "EDITED",
        "active_tool": "FRAME",
    }


def normalize_editor_state(
    state: Mapping[str, Any] | None,
    source_duration: float,
    preferred_duration: float = 15.0,
) -> dict[str, Any]:
    """Normalize a user/session document while leaving the input untouched."""
    duration = max(0.5, _number(source_duration, 0.5))
    base = default_editor_state(duration, preferred_duration)
    incoming = dict(state or {})
    merged = {**base, **deepcopy(incoming)}

    start = _clamp(merged.get("start"), 0.0, max(0.0, duration - 0.5), 0.0)
    end = _clamp(merged.get("end"), 0.5, duration, min(duration, preferred_duration))
    if end - start < 0.5:
        if start + 0.5 <= duration:
            end = start + 0.5
        else:
            end = duration
            start = max(0.0, duration - 0.5)

    fmt = str(merged.get("format", base["format"]))
    tool = str(merged.get("active_tool", base["active_tool"])).upper()
    compare = str(merged.get("compare_mode", base["compare_mode"])).upper()

    normalized = {
        **merged,
        "version": 403,
        "source_duration": duration,
        "start": round(start, 3),
        "end": round(end, 3),
        "format": fmt if fmt in FORMATS else base["format"],
        "zoom": round(_clamp(merged.get("zoom"), 1.0, 2.0, 1.0), 3),
        "x": int(round(_clamp(merged.get("x"), -100, 100, 0))),
        "y": int(round(_clamp(merged.get("y"), -100, 100, 0))),
        "volume": int(round(_clamp(merged.get("volume"), 0, 200, 100))),
        "speed": round(_clamp(merged.get("speed"), 0.5, 2.0, 1.0), 2),
        "brightness": round(_clamp(merged.get("brightness"), -0.3, 0.3, 0.0), 2),
        "contrast": round(_clamp(merged.get("contrast"), 0.7, 1.5, 1.0), 2),
        "subtitles_enabled": _clean_bool(merged.get("subtitles_enabled"), True),
        "subtitle_y": int(round(_clamp(merged.get("subtitle_y"), 5, 95, 78))),
        "safe_zones": _clean_bool(merged.get("safe_zones"), True),
        "focus_mode": _clean_bool(merged.get("focus_mode"), False),
        "compare_mode": compare if compare in COMPARE_MODES else base["compare_mode"],
        "active_tool": tool if tool in TOOLS else base["active_tool"],
    }
    return normalized


def _snapshot(state: Mapping[str, Any]) -> dict[str, Any]:
    return deepcopy(dict(state))


def push_history(
    history: Iterable[Mapping[str, Any]] | None,
    state: Mapping[str, Any],
    max_entries: int = 32,
) -> list[dict[str, Any]]:
    """Append a state snapshot, deduplicating consecutive entries."""
    items = [_snapshot(item) for item in (history or [])]
    candidate = _snapshot(state)
    if items and items[-1] == candidate:
        return items[-max(1, int(max_entries)) :]
    items.append(candidate)
    return items[-max(1, int(max_entries)) :]


def undo_state(
    past: Iterable[Mapping[str, Any]] | None,
    current: Mapping[str, Any],
    future: Iterable[Mapping[str, Any]] | None,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    past_items = [_snapshot(item) for item in (past or [])]
    future_items = [_snapshot(item) for item in (future or [])]
    if not past_items:
        return _snapshot(current), past_items, future_items
    restored = past_items.pop()
    future_items = push_history(future_items, current)
    return restored, past_items, future_items


def redo_state(
    past: Iterable[Mapping[str, Any]] | None,
    current: Mapping[str, Any],
    future: Iterable[Mapping[str, Any]] | None,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    past_items = [_snapshot(item) for item in (past or [])]
    future_items = [_snapshot(item) for item in (future or [])]
    if not future_items:
        return _snapshot(current), past_items, future_items
    restored = future_items.pop()
    past_items = push_history(past_items, current)
    return restored, past_items, future_items


def normalize_timeline_markers(
    events: Iterable[Mapping[str, Any]] | None,
    clip_start: float,
    clip_end: float,
) -> list[dict[str, Any]]:
    """Return real markers that fall inside the selected scene.

    Unknown/bad events are discarded rather than fabricated.  This is important for
    Game Vision: a KILL marker only appears when an upstream detector actually emits it.
    """
    start = _number(clip_start, 0.0)
    end = max(start + 0.001, _number(clip_end, start + 0.001))
    span = end - start
    normalized: list[dict[str, Any]] = []
    for event in events or []:
        try:
            when = float(event.get("time"))
        except (TypeError, ValueError, AttributeError):
            continue
        if when < start or when > end:
            continue
        raw_type = str(event.get("type", "ACTION_PEAK")).strip().upper().replace(" ", "_")
        marker_type = raw_type if raw_type in MARKER_TYPES else "ACTION_PEAK"
        score = _clamp(event.get("score", 0.5), 0.0, 1.0, 0.5)
        label = str(event.get("label") or _MARKER_LABELS.get(marker_type, marker_type.title())).strip()
        normalized.append(
            {
                "time": round(when, 3),
                "type": marker_type,
                "label": label,
                "score": round(score, 3),
                "position_pct": round(((when - start) / span) * 100.0, 3),
            }
        )
    normalized.sort(key=lambda item: (item["time"], -item["score"]))
    return normalized


def _suggestion(
    suggestion_id: str,
    category: str,
    title: str,
    reason: str,
    patch: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "id": suggestion_id,
        "category": category,
        "title": title,
        "reason": reason,
        "patch": deepcopy(dict(patch)),
    }


def game_director_suggestions(
    state: Mapping[str, Any],
    markers: Iterable[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Produce deterministic, explainable scene-local recommendations.

    This intentionally does not pretend to be a remote LLM.  It turns existing editor
    decisions and detector events into useful actions and can later be augmented by the
    Creative Director without changing the UI contract.
    """
    duration = max(0.5, _number(state.get("source_duration", state.get("end", 15.0)), 15.0))
    current = normalize_editor_state(state, duration)
    real_markers = [dict(item) for item in (markers or [])]
    suggestions: list[dict[str, Any]] = []

    action_markers = [
        item for item in real_markers
        if str(item.get("type", "")).upper() in {"ACTION_PEAK", "KILL", "HOOK"}
    ]
    if action_markers:
        first = min(action_markers, key=lambda item: _number(item.get("time"), current["start"]))
        event_time = _number(first.get("time"), current["start"])
        lead = event_time - current["start"]
        if lead > 1.0:
            new_start = max(0.0, event_time - 0.8)
            if current["end"] - new_start >= 0.5:
                suggestions.append(
                    _suggestion(
                        "tighten_hook",
                        "AI",
                        "Aggancia prima il momento forte",
                        f"Il primo picco arriva dopo {lead:.1f}s: accorcia l'attesa iniziale.",
                        {"start": round(new_start, 3)},
                    )
                )
        if current["zoom"] <= 1.02:
            suggestions.append(
                _suggestion(
                    "action_reframe",
                    "FRAME",
                    "Dai più peso all'azione",
                    "C'è un picco reale nella scena: un leggero punch-in aumenta la leggibilità verticale.",
                    {"zoom": 1.10},
                )
            )

    if current.get("subtitles_enabled", True) and int(current.get("subtitle_y", 78)) > 82:
        suggestions.append(
            _suggestion(
                "caption_safe_zone",
                "CAPTION",
                "Porta i sottotitoli nella safe zone",
                "La posizione attuale rischia di sovrapporsi ai controlli delle piattaforme short.",
                {"subtitle_y": 78, "safe_zones": True},
            )
        )

    if int(current.get("volume", 100)) < 85:
        suggestions.append(
            _suggestion(
                "lift_game_audio",
                "AUDIO",
                "Alza leggermente il gameplay",
                "Il volume del progetto è sotto il livello di ascolto rapido consigliato per l'anteprima.",
                {"volume": 100},
            )
        )

    scene_len = current["end"] - current["start"]
    if scene_len > 30.0:
        suggestions.append(
            _suggestion(
                "shorten_scene",
                "AI",
                "Stringi la scena",
                "La selezione supera 30 secondi: ridurla mantiene il ritmo da Short.",
                {"end": min(current["end"], current["start"] + 30.0)},
            )
        )

    return suggestions


def apply_director_suggestion(
    state: Mapping[str, Any],
    suggestion: Mapping[str, Any],
    source_duration: float,
) -> dict[str, Any]:
    """Apply a Director patch to a copy of the current decisions and normalize it."""
    changed = _snapshot(state)
    patch = suggestion.get("patch", {}) if isinstance(suggestion, Mapping) else {}
    if isinstance(patch, Mapping):
        changed.update(deepcopy(dict(patch)))
    return normalize_editor_state(changed, source_duration)


def apply_all_director_suggestions(
    state: Mapping[str, Any],
    suggestions: Iterable[Mapping[str, Any]],
    source_duration: float,
) -> dict[str, Any]:
    changed = _snapshot(state)
    for suggestion in suggestions:
        changed = apply_director_suggestion(changed, suggestion, source_duration)
    return changed
