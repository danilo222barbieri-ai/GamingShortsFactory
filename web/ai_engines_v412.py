"""V412 AI engines: the data contract between the AI ranker and the Crea con IA page.

The Streamlit app owns the AI run (ranking, alternates, mini previews). This
module turns that state into a small JSON "results sheet" written next to the
mini previews, merges it with the preview files for ``/ai/results``, and swaps
one ranked moment for an AI alternate ("Cambia short").

Everything here is pure Python (no Streamlit import) so it can be unit tested
and imported by both ``app.py`` and ``web/direct_upload_server.py``.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping

META_FILENAME = "ai_results_meta.json"
ENGINE_PROFILES = {"auto": "auto", "best": "director", "action": "action", "reaction": "reaction"}
REFINE_PROFILES = ("auto", "director")
_MINI_RE = re.compile(r"(?:^|[_-])mini_([1-3])_(\d+(?:\.\d+)?)(?:_[0-9a-f]+)?\.mp4$", re.IGNORECASE)
_START_TOLERANCE = 0.06
_ALT_TOLERANCE = 0.35

_EVENT_TITLES = {
    "multi_kill": "Kill multipla",
    "victory": "Vittoria",
    "clutch": "Clutch",
    "goal": "Gol decisivo",
    "boss": "Scontro col boss",
    "reaction": "Reazione forte",
    "kill": "Eliminazione",
    "impact": "Impatto",
    "overtake": "Sorpasso",
    "crash": "Crash",
    "save": "Parata",
    "assist": "Assist",
    "death": "KO",
    "shot": "Tiro",
}
_CATEGORY_TITLES = {"action": "Momento d'azione", "reaction": "Reazione", "story": "Momento con storia"}
_CATEGORY_TAGS = {"action": "Azione", "reaction": "Voce", "story": "Racconto", "event": "Evento"}
_PROFILE_NAMES = {"auto": "AUTO", "action": "AZIONE", "reaction": "REAZIONI", "director": "STORIA"}


def _num(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if out == out else default


def effective_analysis_duration(source_duration: Any, requested_duration: Any) -> float:
    """Use the full available source, preserving normal longer-source analysis."""
    source = max(0.0, _num(source_duration, 0.0))
    requested = max(0.1, _num(requested_duration, 15.0))
    return min(source, requested) if source > 0 else requested


def cache_profile(profile: Any) -> str:
    """Normalised engine profile used in the AI cache key (one cache slot per engine)."""
    text = str(profile or "").strip().lower()
    return text if text in ENGINE_PROFILES.values() else "legacy"


def should_refine(profile: Any, modalita: str = "") -> bool:
    """Only AUTO and STORIA move the clip borders; AZIONE/REAZIONI keep the detected peak."""
    text = str(profile or "").strip().lower()
    if text in ENGINE_PROFILES.values():
        return text in REFINE_PROFILES
    return modalita in ("🚀 AUTO TOTALE", "🎬 AI Director")


def whole_source_meta(source_duration, selected_duration, *, request_id, video_url):
    """Publish a usable candidate before analysis, without claiming AI success."""
    source, requested = _num(source_duration), _num(selected_duration)
    if not 0 < source < requested:
        return None
    return {"version": 1, "request_id": request_id, "status": "analyzing", "whole_source": True,
            "updated_at": time.time(), "items": [{"index": 0, "start_time": 0,
            "end_time": source, "video": video_url, "whole_source": True,
            "label": "Il tuo video è già pronto",
            "why": f"Dura {source:g} s, quindi non serve cercare un segmento da {requested:g} s.",
            "alternates": [], "signals": [], "score": None}]}


def run_duration_analysis(input_file, mode, duration, *, source_duration, rank, scan, cache_token=None, voice=None):
    """Only skip segment selection. Full-video scan and voice analysis still run."""
    if not 0 < _num(source_duration) < _num(duration):
        return rank(input_file, mode, clip_duration=duration, numero_clip=3, cache_token=cache_token)
    full_scan, cache_hit = scan(input_file, cache_token=cache_token)
    if not isinstance(full_scan, Mapping) or not full_scan:
        raise RuntimeError("Analisi del gameplay non disponibile")
    scan_meta = dict(full_scan.get("meta") or {})
    if scan_meta.get("video_error") or scan_meta.get("audio_error"):
        raise RuntimeError("Analisi del gameplay non riuscita. Il video intero resta disponibile.")
    voice_result = None
    if voice is not None:
        voice_result, _ = voice(input_file, 0.0, float(source_duration), cache_token=cache_token, force=True)
    # Reuse the existing event/genre/Game Brain stages on a VALID whole-source
    # window. They must not receive the impossible requested crop duration.
    _, diagnostics = rank(input_file, mode, clip_duration=float(source_duration), numero_clip=1, cache_token=cache_token)
    diagnostics = dict(diagnostics or {})
    diagnostics.update({"__whole_source__": True, "__scan_cache_hit__": cache_hit, "__voice__": voice_result})
    return [(0.0, 0.0)], diagnostics


def _score(row: Mapping[str, Any]) -> int | None:
    raw = _num(row.get("brain_score"), -1.0)
    if raw <= 0:
        return None
    return int(max(1, min(99, round(min(raw, 1.0) * 100))))


def _title(row: Mapping[str, Any]) -> str:
    event = str(row.get("event") or "").lower()
    if event in _EVENT_TITLES:
        return _EVENT_TITLES[event]
    category = str(row.get("category") or "").lower()
    return _CATEGORY_TITLES.get(category, "Momento forte")


def _why(row: Mapping[str, Any]) -> str:
    plan = row.get("director_plan") if isinstance(row.get("director_plan"), Mapping) else {}
    text = plan.get("text") if isinstance(plan.get("text"), Mapping) else {}
    hook = str(text.get("hook") or "").strip()
    confidence = _num(row.get("confidence"), 0.0)
    parts = []
    if hook:
        parts.append(hook.rstrip(".…") + ".")
    if confidence > 0:
        parts.append(f"Confidenza IA {int(round(confidence * 100))}%.")
    return " ".join(parts)


def _signals(row: Mapping[str, Any]) -> list[str]:
    tags: list[str] = []
    event = str(row.get("event") or "").lower()
    if event in _EVENT_TITLES:
        tags.append(_EVENT_TITLES[event])
    category = _CATEGORY_TAGS.get(str(row.get("category") or "").lower())
    if category and category not in tags:
        tags.append(category)
    if _num(row.get("semantic_reaction")) >= 0.6 and "Voce" not in tags:
        tags.append("Voce alta")
    return tags[:3]


def _item(row: Mapping[str, Any], start: float, duration: float, index: int) -> dict[str, Any]:
    return {
        "index": index,
        "start_time": round(start, 3),
        "end_time": round(start + duration, 3),
        "score": _score(row),
        "label": _title(row),
        "why": _why(row),
        "signals": _signals(row),
    }


def build_results_meta(
    candidates: Iterable[Any],
    brain: Mapping[str, Any] | None,
    *,
    duration: float,
    profile: str = "",
    request_id: str = "",
    durations: Mapping[float, float] | None = None,
    timings: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Describe the three shorts on screen (and their alternates) for the AI page."""
    brain = brain if isinstance(brain, Mapping) else {}
    selected = [r for r in (brain.get("selected") or []) if isinstance(r, Mapping)]
    alternates = [r for r in (brain.get("alternates") or []) if isinstance(r, Mapping)]
    durations = durations or {}
    duration = max(1.0, _num(duration, 15.0))
    items = []
    for index, raw_start in enumerate(list(candidates or [])[:3]):
        start = _num(raw_start, -1.0)
        if start < 0:
            continue
        row = min(selected, key=lambda r: abs(_num(r.get("start"), -999) - start), default={})
        if row and abs(_num(row.get("start"), -999) - start) > max(3.0, duration):
            row = selected[index] if index < len(selected) else {}
        clip = _num(durations.get(round(start, 3)), duration) or duration
        items.append(_item(row, start, clip, index))
    alt_items = []
    for j, row in enumerate(alternates[:3]):
        start = _num(row.get("start"), -1.0)
        if start < 0:
            continue
        alt_items.append(_item(row, start, duration, 3 + j))
    for item in items:
        item["alternates"] = alt_items
    pool = brain.get("pool_size") or brain.get("augmented_pool_size")
    return {
        "version": 1,
        "request_id": str(request_id or "")[:40],
        "engine": _PROFILE_NAMES.get(str(profile or "").lower(), ""),
        "profile": str(profile or ""),
        "pool_size": int(_num(pool, 0)),
        "duration": duration,
        "updated_at": time.time(),
        "items": items,
        "timings": dict(timings or {}),
    }


def write_results_meta(directory: Path | str, meta: Mapping[str, Any]) -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / META_FILENAME
    tmp = directory / (META_FILENAME + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(meta, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    os.replace(tmp, path)
    return path


def read_results_meta(directory: Path | str) -> dict[str, Any] | None:
    try:
        data = json.loads((Path(directory) / META_FILENAME).read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) and isinstance(data.get("items"), list) else None


def mini_files(directory: Path | str) -> list[tuple[int, float, float, str]]:
    """(index 1-3, start, mtime, filename) for each start-stamped mini preview."""
    out = []
    try:
        entries = list(Path(directory).iterdir())
    except Exception:
        return out
    for path in entries:
        if not path.is_file():
            continue
        match = _MINI_RE.search(path.name)
        if not match:
            continue
        try:
            mtime = float(path.stat().st_mtime)
        except OSError:
            mtime = 0.0
        out.append((int(match.group(1)), float(match.group(2)), mtime, path.name))
    return out


def merge_results(meta: Mapping[str, Any] | None, files: Iterable[tuple[int, float, float, str]], url_for) -> dict[str, Any] | None:
    """Join the results sheet with the mini preview files. None when there is no sheet."""
    if not isinstance(meta, Mapping):
        return None
    if meta.get("status") == "analyzing" and time.time() - _num(meta.get("updated_at"), time.time()) >= 120:
        meta = {**meta, "status": "failed", "error_code": "analysis_timeout",
                "error": "L’analisi ha superato il tempo disponibile. Il video è conservato: puoi riprovare o continuare nell’Editor."}
    if meta.get("status") == "failed" and not meta.get("whole_source"):
        return {"ok":True,"status":"failed","request_id":str(meta.get("request_id") or ""),
                "error_code":str(meta.get("error_code") or "analysis_failed"),
                "error":str(meta.get("error") or "Analisi non riuscita. Riprova."),
                "previews":[],"count":0}
    files = list(files)
    previews = []
    for item in meta.get("items") or []:
        if not isinstance(item, Mapping):
            continue
        index = int(_num(item.get("index"), -1))
        start = _num(item.get("start_time"), -1.0)
        best = None
        for file_index, file_start, mtime, name in files:
            if file_index == index + 1 and abs(file_start - start) <= _START_TOLERANCE:
                if best is None or mtime >= best[0]:
                    best = (mtime, name)
        row = dict(item)
        row["video"] = str(item.get("video") or "") if meta.get("whole_source") else url_for(best[1]) if best else ""
        row["mtime"] = best[0] if best else 0.0
        previews.append(row)
    ready = [row for row in previews if row["video"]]
    return {
        "ok": True,
        "status": str(meta.get("status") or "success"),
        "whole_source": bool(meta.get("whole_source")),
        "error": str(meta.get("error") or ""),
        "request_id": str(meta.get("request_id") or ""),
        "engine": str(meta.get("engine") or ""),
        "pool_size": int(_num(meta.get("pool_size"), 0)),
        "previews": previews[:3],
        "count": len(ready[:3]),
        "timings": dict(meta.get("timings") or {}),
    }


def apply_replacement(state: MutableMapping[str, Any], index: int, start_time: float, *, restore: bool = False, duration: float = 15.0) -> bool:
    """Swap the short at ``index`` with the AI alternate starting at ``start_time``.

    Works on the Streamlit session-state keys the AI run already uses, so the
    preview, editor and final render all follow the new moment. ``restore``
    puts back the moment the AI originally chose for that slot.
    """
    candidates = list(state.get("auto_clip_candidati") or [])
    if not 0 <= int(index) < len(candidates):
        return False
    index = int(index)
    wanted = _num(start_time, -1.0)
    brain = dict(state.get("gsf_v112_brain_context") or {})
    selected = [dict(r) for r in (brain.get("selected") or []) if isinstance(r, Mapping)]
    alternates = [dict(r) for r in (brain.get("alternates") or []) if isinstance(r, Mapping)]
    originals = dict(state.get("gsf_v412_replaced") or {})
    old_start = _num(candidates[index])

    pick = None
    for row in alternates:
        if abs(_num(row.get("start"), -999) - wanted) <= _ALT_TOLERANCE:
            pick = row
            break
    if pick is None and restore:
        original = originals.get(str(index))
        if isinstance(original, Mapping) and abs(_num(original.get("start"), -999) - wanted) <= _ALT_TOLERANCE:
            pick = dict(original)
    if pick is None:
        return False

    new_start = _num(pick.get("start"))
    old_pos = next((i for i, r in enumerate(selected) if abs(_num(r.get("start"), -999) - old_start) <= _ALT_TOLERANCE), None)
    if old_pos is None and index < len(selected):
        old_pos = index  # border refinement may have moved the start slightly
    old_row = dict(selected[old_pos]) if old_pos is not None else {"start": old_start, "brain_score": 0.0, "event": "highlight"}
    old_row["start"] = old_start
    if not restore and str(index) not in originals:
        originals[str(index)] = dict(old_row)
    if restore:
        originals.pop(str(index), None)

    alternates = [r for r in alternates if abs(_num(r.get("start"), -999) - new_start) > _ALT_TOLERANCE]
    alternates.insert(0, {k: v for k, v in old_row.items() if k != "rank"})
    new_row = dict(pick)
    new_row["rank"] = index + 1
    if old_pos is not None:
        selected[old_pos] = new_row
    else:
        selected.append(new_row)
    brain["selected"] = selected
    brain["alternates"] = alternates[:4]

    candidates[index] = new_start
    scores = list(state.get("ai_director_scores") or [])
    if index < len(scores):
        scores[index] = (_num(pick.get("brain_score"), _num(scores[index][0] if scores[index] else 0)), new_start)
    refined = dict(state.get("clip_rifinite") or {})
    if refined:
        refined[round(new_start, 3)] = refined.pop(round(old_start, 3), float(duration))

    state["auto_clip_candidati"] = candidates
    state["ai_director_scores"] = scores
    state["clip_rifinite"] = refined
    state["gsf_v112_brain_context"] = brain
    state["gsf_v412_replaced"] = originals
    state["auto_clip_scelta"] = new_start
    state["preview_key"] = None
    state.pop("preview_bytes", None)
    return True


def select_candidate(state: MutableMapping[str, Any], index: Any, start_time: Any = None) -> bool:
    """Make the short the creator picked on the AI page the active one."""
    candidates = list(state.get("auto_clip_candidati") or [])
    wanted = _num(start_time, -1.0)
    if wanted >= 0:
        for start in candidates:
            if abs(_num(start) - wanted) <= _ALT_TOLERANCE:
                state["auto_clip_scelta"] = _num(start)
                state["preview_key"] = None
                return True
    i = int(_num(index, -1))
    if 0 <= i < len(candidates):
        state["auto_clip_scelta"] = _num(candidates[i])
        state["preview_key"] = None
        return True
    return False
