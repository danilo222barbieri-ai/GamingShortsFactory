"""V403 durable app/project flow state.

Pure metadata state machine used by the Streamlit parent and component bridges.
It intentionally owns no media bytes, rendering, network requests or UI.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import time
from typing import Any, Mapping

SCHEMA_VERSION = 403
EDITOR_COMPONENT_ID = "gsf_editor_2027_v1086"

ROUTE_HOME = "home"
ROUTE_HUB = "hub"
ROUTE_PROJECTS = "projects"
ROUTE_DRAFTS = "drafts"
ROUTE_LIVE = "live"
ROUTE_MOTORI = "motori"
ROUTE_MOMENTS = "moments"
ROUTE_EDITOR = "editor"
ROUTE_CREATE_SHORT = "create_short"

STATIC_ROUTES = {ROUTE_HOME, ROUTE_HUB, ROUTE_PROJECTS, ROUTE_DRAFTS, ROUTE_LIVE}
PROJECT_ROUTES = {ROUTE_MOTORI, ROUTE_MOMENTS, ROUTE_EDITOR, ROUTE_CREATE_SHORT}
ALL_ROUTES = STATIC_ROUTES | PROJECT_ROUTES

_MAX_CANDIDATES = 12
_MAX_TEXT = 2048


def _now() -> float:
    return round(time.time(), 3)


def _text(value: Any, limit: int = _MAX_TEXT) -> str:
    value = "" if value is None else str(value)
    return value[:limit]


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default)
    return number if math.isfinite(number) else float(default)


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _json_copy(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, ensure_ascii=False))
    except Exception:
        return None


def _candidate(row: Any, index: int) -> dict | None:
    if not isinstance(row, Mapping):
        return None
    start = max(0.0, _finite(row.get("start_seconds", row.get("start", 0.0))))
    end = max(start, _finite(row.get("end_seconds", row.get("end", start))))
    cid = _text(row.get("id") or row.get("candidate_id") or f"m{index}", 128)
    if not cid:
        cid = f"m{index}"
    result = {
        "id": cid,
        "rank": max(1, _int(row.get("rank"), index + 1)),
        "start_seconds": start,
        "end_seconds": end,
        "duration": max(0.0, end - start),
        "event": _text(row.get("event") or row.get("type") or "MOMENT", 80),
        "confidence": max(0.0, min(1.0, _finite(row.get("confidence"), 0.0))),
        "score": _finite(row.get("score"), 0.0),
        "reason": _text(row.get("reason"), 480),
        "fusion_reason": _text(row.get("fusion_reason"), 480),
        "fusion_signals": _json_copy(row.get("fusion_signals") or []),
        "thumbnail_ref": _text(row.get("thumbnail_ref") or row.get("thumbnail") or "", 1024),
        "preview_ref": _text(row.get("preview_ref") or row.get("preview") or "", 1024),
        "subtitles_available": bool(row.get("subtitles_available", False)),
    }
    return result


def _clean_candidates(rows: Any) -> list[dict]:
    if not isinstance(rows, (list, tuple)):
        return []
    out: list[dict] = []
    seen: set[str] = set()
    for i, row in enumerate(rows[:_MAX_CANDIDATES]):
        c = _candidate(row, i)
        if not c or c["id"] in seen:
            continue
        seen.add(c["id"])
        out.append(c)
    out.sort(key=lambda c: (c["rank"], c["start_seconds"], c["id"]))
    return out


def _profile_payload(payload: Any) -> dict | None:
    if not isinstance(payload, Mapping):
        return None
    data = {str(k): _json_copy(v) for k, v in payload.items() if k not in {"error", "status"}}
    if not any(data.get(k) for k in ("name", "avatar", "plan", "account_id", "id")):
        return None
    data["version"] = max(0, _int(payload.get("version"), 0))
    return data


def _job_token(kind: str, snapshot: Mapping[str, Any], job_id: str) -> str:
    raw = "|".join(
        (
            kind,
            _text(snapshot.get("project_id"), 128),
            _text(job_id, 128),
            _text(snapshot.get("selected_candidate_id"), 128),
        )
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def new_snapshot(*, project_id: str = "", source_video_ref: str = "", profile: Mapping[str, Any] | None = None) -> dict:
    now = _now()
    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "version": 1,
        "updated_at": now,
        "project_id": _text(project_id, 128),
        "draft_id": "",
        "source_video_ref": _text(source_video_ref, 1024),
        "source_ready": bool(source_video_ref),
        "route": ROUTE_HOME,
        "engine": "auto",
        "duration": 30,
        "analysis": {
            "status": "idle",
            "job_id": "",
            "progress": 0.0,
            "request_token": "",
            "issue_count": 0,
            "error": "",
        },
        "candidates": [],
        "selected_candidate_id": "",
        "selected_candidate_index": None,
        "editor": {"status": "idle", "updated_at": 0.0},
        "render": {
            "status": "idle",
            "job_id": "",
            "progress": 0.0,
            "request_token": "",
            "issue_count": 0,
            "error": "",
        },
        "final_asset_ref": "",
        "profile": {"status": "unavailable", "data": None, "error": "", "version": 0},
        "last_reconciled_at": 0.0,
    }
    if profile:
        snapshot = transition(snapshot, "profile_valid", profile)
    return snapshot


def _ensure_snapshot(snapshot: Any) -> dict:
    if not isinstance(snapshot, Mapping):
        return new_snapshot()
    base = new_snapshot(project_id=_text(snapshot.get("project_id"), 128), source_video_ref=_text(snapshot.get("source_video_ref"), 1024))
    for key, value in snapshot.items():
        if key in base:
            base[key] = copy.deepcopy(value)
    base["schema_version"] = SCHEMA_VERSION
    base["version"] = max(1, _int(base.get("version"), 1))
    base["source_video_ref"] = _text(base.get("source_video_ref"), 1024)
    base["source_ready"] = bool(base.get("source_ready") or base["source_video_ref"])
    base["candidates"] = _clean_candidates(base.get("candidates"))
    if not isinstance(base.get("analysis"), Mapping):
        base["analysis"] = new_snapshot()["analysis"]
    else:
        base["analysis"] = {**new_snapshot()["analysis"], **dict(base["analysis"])}
    if not isinstance(base.get("render"), Mapping):
        base["render"] = new_snapshot()["render"]
    else:
        base["render"] = {**new_snapshot()["render"], **dict(base["render"])}
    if not isinstance(base.get("profile"), Mapping):
        base["profile"] = new_snapshot()["profile"]
    else:
        base["profile"] = {**new_snapshot()["profile"], **dict(base["profile"])}
    if not isinstance(base.get("editor"), Mapping):
        base["editor"] = new_snapshot()["editor"]
    return base


def _selected(snapshot: Mapping[str, Any]) -> tuple[int | None, dict | None]:
    wanted = _text(snapshot.get("selected_candidate_id"), 128)
    candidates = snapshot.get("candidates") if isinstance(snapshot.get("candidates"), list) else []
    for i, row in enumerate(candidates):
        if isinstance(row, Mapping) and _text(row.get("id"), 128) == wanted and wanted:
            return i, dict(row)
    idx = snapshot.get("selected_candidate_index")
    if isinstance(idx, int) and 0 <= idx < len(candidates):
        row = candidates[idx]
        if isinstance(row, Mapping):
            return idx, dict(row)
    return None, None


def resolve_route(snapshot: Mapping[str, Any] | None, requested_route: str) -> str:
    s = _ensure_snapshot(snapshot)
    requested = _text(requested_route, 64).lower().strip()
    aliases = {
        "ai": ROUTE_MOTORI,
        "motors": ROUTE_MOTORI,
        "momenti": ROUTE_MOMENTS,
        "short": ROUTE_CREATE_SHORT,
        "crea_short": ROUTE_CREATE_SHORT,
        "creator_hub": ROUTE_HUB,
        "progetti": ROUTE_PROJECTS,
        "bozze": ROUTE_DRAFTS,
    }
    requested = aliases.get(requested, requested)
    if requested not in ALL_ROUTES:
        requested = ROUTE_HOME
    if requested in STATIC_ROUTES:
        return requested
    if requested == ROUTE_MOTORI:
        return ROUTE_MOTORI if s.get("source_ready") else ROUTE_HOME
    candidates = s.get("candidates") or []
    _, selected = _selected(s)
    if requested == ROUTE_MOMENTS:
        return ROUTE_MOMENTS if candidates else (ROUTE_MOTORI if s.get("source_ready") else ROUTE_HOME)
    if requested in {ROUTE_EDITOR, ROUTE_CREATE_SHORT}:
        if selected:
            return requested
        if candidates:
            return ROUTE_MOMENTS
        return ROUTE_MOTORI if s.get("source_ready") else ROUTE_HOME
    return ROUTE_HOME


def _touch(snapshot: dict, changed: bool) -> dict:
    if changed:
        snapshot["version"] = max(1, _int(snapshot.get("version"), 1)) + 1
        snapshot["updated_at"] = _now()
    snapshot["route"] = resolve_route(snapshot, snapshot.get("route", ROUTE_HOME))
    return snapshot


def transition(snapshot: Mapping[str, Any] | None, event: str, payload: Mapping[str, Any] | None = None) -> dict:
    s = _ensure_snapshot(snapshot)
    before = json.dumps(s, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    p = dict(payload or {}) if isinstance(payload or {}, Mapping) else {}
    event = _text(event, 80).lower().strip()

    if event == "source_ready":
        ref = _text(p.get("source_video_ref") or s.get("source_video_ref"), 1024)
        if ref:
            s["source_video_ref"] = ref
            s["source_ready"] = True
            if s.get("route") == ROUTE_HOME:
                s["route"] = ROUTE_MOTORI

    elif event == "route":
        s["route"] = resolve_route(s, _text(p.get("route"), 64))

    elif event == "analysis_started":
        job_id = _text(p.get("job_id"), 128)
        if job_id:
            a = dict(s["analysis"])
            same = a.get("status") == "running" and a.get("job_id") == job_id
            s["engine"] = _text(p.get("engine") or s.get("engine") or "auto", 64)
            s["duration"] = max(1, min(300, _int(p.get("duration"), s.get("duration", 30))))
            if not same:
                a["issue_count"] = max(0, _int(a.get("issue_count"), 0)) + 1
                a["request_token"] = _job_token("analysis", s, job_id)
            a.update({"status": "running", "job_id": job_id, "progress": max(0.0, min(1.0, _finite(p.get("progress"), 0.0))), "error": ""})
            s["analysis"] = a
            s["route"] = ROUTE_MOTORI

    elif event == "analysis_progress":
        a = dict(s["analysis"])
        if a.get("status") == "running":
            a["progress"] = max(float(a.get("progress") or 0.0), max(0.0, min(1.0, _finite(p.get("progress"), 0.0))))
            s["analysis"] = a

    elif event == "analysis_failed":
        a = dict(s["analysis"])
        a.update({"status": "error", "error": _text(p.get("error"), 480)})
        s["analysis"] = a
        s["route"] = ROUTE_MOTORI

    elif event == "analysis_completed":
        rows = _clean_candidates(p.get("candidates"))
        a = dict(s["analysis"])
        incoming_job = _text(p.get("job_id") or a.get("job_id"), 128)
        a.update({"status": "ready", "job_id": incoming_job, "progress": 1.0, "error": ""})
        s["analysis"] = a
        s["candidates"] = rows
        idx, selected = _selected(s)
        if not selected:
            s["selected_candidate_id"] = ""
            s["selected_candidate_index"] = None
        else:
            s["selected_candidate_index"] = idx
        s["route"] = ROUTE_MOMENTS if rows else ROUTE_MOTORI

    elif event == "candidate_selected":
        candidates = s.get("candidates") or []
        wanted_id = _text(p.get("candidate_id"), 128)
        idx = p.get("index")
        chosen_i: int | None = None
        if wanted_id:
            for i, row in enumerate(candidates):
                if _text((row or {}).get("id"), 128) == wanted_id:
                    chosen_i = i
                    break
        elif isinstance(idx, int) and 0 <= idx < len(candidates):
            chosen_i = idx
        if chosen_i is not None:
            s["selected_candidate_index"] = chosen_i
            s["selected_candidate_id"] = _text(candidates[chosen_i].get("id"), 128)
            if s.get("route") not in {ROUTE_EDITOR, ROUTE_CREATE_SHORT}:
                s["route"] = ROUTE_MOMENTS

    elif event == "editor_opened":
        if _selected(s)[1]:
            s["route"] = ROUTE_EDITOR
            s["editor"] = {"status": "open", "updated_at": _now()}

    elif event == "editor_updated":
        if _selected(s)[1]:
            s["editor"] = {"status": "dirty", "updated_at": _now()}

    elif event == "render_started":
        _, selected = _selected(s)
        job_id = _text(p.get("job_id"), 128)
        if selected and job_id:
            r = dict(s["render"])
            same = r.get("status") == "running" and r.get("job_id") == job_id
            if not same:
                r["issue_count"] = max(0, _int(r.get("issue_count"), 0)) + 1
                r["request_token"] = _job_token("render", s, job_id)
            r.update({"status": "running", "job_id": job_id, "progress": max(0.0, min(1.0, _finite(p.get("progress"), 0.0))), "error": ""})
            s["render"] = r
            s["route"] = ROUTE_CREATE_SHORT

    elif event == "render_progress":
        r = dict(s["render"])
        if r.get("status") == "running":
            r["progress"] = max(float(r.get("progress") or 0.0), max(0.0, min(1.0, _finite(p.get("progress"), 0.0))))
            s["render"] = r

    elif event == "render_failed":
        r = dict(s["render"])
        r.update({"status": "error", "error": _text(p.get("error"), 480)})
        s["render"] = r
        s["route"] = resolve_route(s, ROUTE_CREATE_SHORT)

    elif event == "render_completed":
        _, selected = _selected(s)
        asset = _text(p.get("asset_ref"), 1024)
        if selected and asset:
            r = dict(s["render"])
            r.update({"status": "ready", "job_id": _text(p.get("job_id") or r.get("job_id"), 128), "progress": 1.0, "error": ""})
            s["render"] = r
            s["final_asset_ref"] = asset
            s["route"] = ROUTE_CREATE_SHORT

    elif event == "draft_saved":
        s["draft_id"] = _text(p.get("draft_id") or s.get("draft_id"), 128)

    elif event == "profile_valid":
        data = _profile_payload(p)
        if data:
            current = s.get("profile") if isinstance(s.get("profile"), Mapping) else {}
            current_version = max(0, _int(current.get("version"), 0))
            incoming_version = max(0, _int(data.get("version"), 0))
            if current.get("data") is None or incoming_version >= current_version:
                s["profile"] = {"status": "valid", "data": data, "error": "", "version": incoming_version}

    elif event == "profile_refreshing":
        prof = dict(s["profile"])
        prof["status"] = "refreshing" if prof.get("data") else "loading"
        prof["error"] = ""
        s["profile"] = prof

    elif event == "profile_refresh_failed":
        prof = dict(s["profile"])
        prof["status"] = "stale" if prof.get("data") else "unavailable"
        prof["error"] = _text(p.get("error"), 480)
        s["profile"] = prof

    elif event == "signed_out":
        s["profile"] = {"status": "signed_out", "data": None, "error": "", "version": 0}

    elif event == "reset":
        project_id = _text(p.get("project_id"), 128)
        return new_snapshot(project_id=project_id)

    after = json.dumps(s, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _touch(s, after != before)


def reconcile_snapshot(local: Mapping[str, Any] | None, authoritative: Mapping[str, Any] | None) -> dict:
    """Reconcile foreground/resume state.

    Server/authoritative state wins for project work. A valid locally displayed
    profile is retained if the server payload is temporarily missing/stale.
    Reconciliation never creates jobs or increments issue counters.
    """
    l = _ensure_snapshot(local)
    a = _ensure_snapshot(authoritative)
    same_project = bool(a.get("project_id")) and a.get("project_id") == l.get("project_id")
    if same_project:
        merged = copy.deepcopy(a if _int(a.get("version"), 0) >= _int(l.get("version"), 0) else l)
    else:
        merged = copy.deepcopy(a if a.get("project_id") else l)

    lprof = l.get("profile") if isinstance(l.get("profile"), Mapping) else {}
    mprof = merged.get("profile") if isinstance(merged.get("profile"), Mapping) else {}
    if lprof.get("data") and not mprof.get("data"):
        merged["profile"] = copy.deepcopy(lprof)
        if merged["profile"].get("status") not in {"valid", "stale", "refreshing"}:
            merged["profile"]["status"] = "stale"

    merged["route"] = resolve_route(merged, merged.get("route", ROUTE_HOME))
    merged["last_reconciled_at"] = _now()
    return _ensure_snapshot(merged)


def analysis_request_token(snapshot: Mapping[str, Any] | None) -> str:
    s = _ensure_snapshot(snapshot)
    return _text((s.get("analysis") or {}).get("request_token"), 128)


def render_request_token(snapshot: Mapping[str, Any] | None) -> str:
    s = _ensure_snapshot(snapshot)
    return _text((s.get("render") or {}).get("request_token"), 128)


def editor_handoff(snapshot: Mapping[str, Any] | None) -> dict:
    s = _ensure_snapshot(snapshot)
    _, selected = _selected(s)
    if not selected:
        return {}
    return {
        "component_id": EDITOR_COMPONENT_ID,
        "project_id": s.get("project_id", ""),
        "source_video_ref": s.get("source_video_ref", ""),
        "candidate_id": selected.get("id", ""),
        "start_seconds": selected.get("start_seconds", 0.0),
        "end_seconds": selected.get("end_seconds", 0.0),
        "duration": selected.get("duration", 0.0),
    }


def create_short_handoff(snapshot: Mapping[str, Any] | None) -> dict:
    s = _ensure_snapshot(snapshot)
    _, selected = _selected(s)
    if not selected:
        return {}
    render = s.get("render") if isinstance(s.get("render"), Mapping) else {}
    return {
        "project_id": s.get("project_id", ""),
        "source_video_ref": s.get("source_video_ref", ""),
        "candidate_id": selected.get("id", ""),
        "start_seconds": selected.get("start_seconds", 0.0),
        "end_seconds": selected.get("end_seconds", 0.0),
        "duration": selected.get("duration", 0.0),
        "state": "ready" if render.get("status") == "ready" and s.get("final_asset_ref") else "pre-render",
        "final_asset_ref": s.get("final_asset_ref", ""),
    }


__all__ = [
    "SCHEMA_VERSION",
    "EDITOR_COMPONENT_ID",
    "ROUTE_HOME",
    "ROUTE_HUB",
    "ROUTE_PROJECTS",
    "ROUTE_DRAFTS",
    "ROUTE_LIVE",
    "ROUTE_MOTORI",
    "ROUTE_MOMENTS",
    "ROUTE_EDITOR",
    "ROUTE_CREATE_SHORT",
    "new_snapshot",
    "transition",
    "reconcile_snapshot",
    "resolve_route",
    "analysis_request_token",
    "render_request_token",
    "editor_handoff",
    "create_short_handoff",
]
