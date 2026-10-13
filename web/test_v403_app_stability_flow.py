from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app_flow_v403 import (  # noqa: E402
    EDITOR_COMPONENT_ID,
    ROUTE_CREATE_SHORT,
    ROUTE_EDITOR,
    ROUTE_MOMENTS,
    ROUTE_MOTORI,
    analysis_request_token,
    create_short_handoff,
    editor_handoff,
    new_snapshot,
    reconcile_snapshot,
    render_request_token,
    resolve_route,
    transition,
)


def _candidate(idx: int, start: float, end: float, event: str = "KILL") -> dict:
    return {
        "id": f"m{idx}",
        "rank": idx + 1,
        "start_seconds": start,
        "end_seconds": end,
        "event": event,
        "confidence": 0.8 + idx * 0.03,
        "fusion_reason": f"{event} · High Action",
    }


def _base_snapshot() -> dict:
    s = new_snapshot(project_id="p_v403", source_video_ref="gsf://source/p_v403.mp4")
    return transition(s, "source_ready", {"source_video_ref": "gsf://source/p_v403.mp4"})


def test_project_and_source_survive_route_changes() -> None:
    s = _base_snapshot()
    project_id = s["project_id"]
    source_ref = s["source_video_ref"]
    for route in (ROUTE_MOTORI, "home", "hub", ROUTE_MOTORI):
        s = transition(s, "route", {"route": route})
        assert s["project_id"] == project_id
        assert s["source_video_ref"] == source_ref


def test_resume_does_not_duplicate_analysis_job() -> None:
    s = _base_snapshot()
    s = transition(s, "analysis_started", {"job_id": "a1", "engine": "auto", "duration": 30})
    before = analysis_request_token(s)
    duplicate = transition(s, "analysis_started", {"job_id": "a1", "engine": "auto", "duration": 30})
    resumed = reconcile_snapshot(copy.deepcopy(duplicate), copy.deepcopy(duplicate))
    assert analysis_request_token(duplicate) == before
    assert analysis_request_token(resumed) == before
    assert resumed["analysis"]["issue_count"] == 1


def test_resume_does_not_duplicate_render_job() -> None:
    s = _base_snapshot()
    s = transition(s, "analysis_completed", {"job_id": "a1", "candidates": [_candidate(0, 10, 40)]})
    s = transition(s, "candidate_selected", {"index": 0})
    s = transition(s, "render_started", {"job_id": "r1"})
    before = render_request_token(s)
    duplicate = transition(s, "render_started", {"job_id": "r1"})
    resumed = reconcile_snapshot(copy.deepcopy(duplicate), copy.deepcopy(duplicate))
    assert render_request_token(duplicate) == before
    assert render_request_token(resumed) == before
    assert resumed["render"]["issue_count"] == 1


def test_profile_keeps_last_valid_payload_during_refresh_failure() -> None:
    s = _base_snapshot()
    valid = {"name": "Creator", "avatar": "avatar://1", "plan": "Pro", "version": 7}
    s = transition(s, "profile_valid", valid)
    s = transition(s, "profile_refreshing", {})
    assert s["profile"]["data"] == valid
    s = transition(s, "profile_refresh_failed", {"error": "temporary"})
    assert s["profile"]["data"] == valid
    assert s["profile"]["status"] == "stale"


def test_analysis_completion_routes_to_dedicated_moments() -> None:
    s = _base_snapshot()
    candidates = [_candidate(0, 10, 40), _candidate(1, 50, 80, "CLUTCH"), _candidate(2, 90, 120, "VICTORY")]
    s = transition(s, "analysis_completed", {"job_id": "a1", "candidates": candidates})
    assert s["route"] == ROUTE_MOMENTS
    assert len(s["candidates"]) == 3


def test_candidate_selection_persists_across_route_and_resume() -> None:
    s = _base_snapshot()
    candidates = [_candidate(0, 10, 40), _candidate(1, 50, 80), _candidate(2, 90, 120)]
    s = transition(s, "analysis_completed", {"job_id": "a1", "candidates": candidates})
    s = transition(s, "candidate_selected", {"index": 1})
    selected_id = s["selected_candidate_id"]
    moved = transition(s, "route", {"route": "hub"})
    restored = reconcile_snapshot(copy.deepcopy(moved), copy.deepcopy(s))
    assert moved["selected_candidate_id"] == selected_id
    assert restored["selected_candidate_id"] == selected_id
    assert restored["selected_candidate_index"] == 1


def test_create_short_without_selection_fails_safe() -> None:
    s = _base_snapshot()
    assert resolve_route(s, ROUTE_CREATE_SHORT) == ROUTE_MOTORI
    candidates = [_candidate(0, 10, 40)]
    s = transition(s, "analysis_completed", {"job_id": "a1", "candidates": candidates})
    assert resolve_route(s, ROUTE_CREATE_SHORT) == ROUTE_MOMENTS


def test_editor_and_create_short_handoffs_use_selected_candidate() -> None:
    s = _base_snapshot()
    candidates = [_candidate(0, 10, 40), _candidate(1, 51.5, 81.5, "CLUTCH")]
    s = transition(s, "analysis_completed", {"job_id": "a1", "candidates": candidates})
    s = transition(s, "candidate_selected", {"index": 1})
    e = editor_handoff(s)
    c = create_short_handoff(s)
    assert e["component_id"] == "gsf_editor_2027_v1086"
    assert e["candidate_id"] == "m1"
    assert e["start_seconds"] == 51.5 and e["end_seconds"] == 81.5
    assert c["candidate_id"] == "m1"
    assert c["source_video_ref"] == s["source_video_ref"]


def test_final_render_stays_on_create_short_route_and_becomes_ready() -> None:
    s = _base_snapshot()
    s = transition(s, "analysis_completed", {"job_id": "a1", "candidates": [_candidate(0, 10, 40)]})
    s = transition(s, "candidate_selected", {"index": 0})
    s = transition(s, "route", {"route": ROUTE_CREATE_SHORT})
    s = transition(s, "render_started", {"job_id": "r1"})
    s = transition(s, "render_completed", {"job_id": "r1", "asset_ref": "gsf://final/p_v403.mp4"})
    assert s["route"] == ROUTE_CREATE_SHORT
    assert s["render"]["status"] == "ready"
    assert s["final_asset_ref"] == "gsf://final/p_v403.mp4"


def test_gamebar_route_resolution_is_stateless_and_idempotent() -> None:
    s = _base_snapshot()
    first = resolve_route(s, "hub")
    s2 = transition(s, "route", {"route": ROUTE_EDITOR})
    second = resolve_route(s2, "hub")
    assert first == "hub" == second
    assert resolve_route(s2, "home") == "home"
    assert resolve_route(s2, ROUTE_MOTORI) == ROUTE_MOTORI


def test_editor_identity_locked() -> None:
    assert EDITOR_COMPONENT_ID == "gsf_editor_2027_v1086"
    editor_embed = (ROOT / "editor_2027_embed.py").read_text(encoding="utf-8")
    assert "gsf_editor_2027_v1086" in editor_embed


def test_motori_does_not_own_final_candidate_cards() -> None:
    html = (ROOT / "ai_v221_component" / "index.html").read_text(encoding="utf-8")
    lowered = html.lower()
    assert 'class="moments"' not in lowered
    assert 'class="moment"' not in lowered
    assert "i tuoi 3 momenti" not in lowered


def test_dedicated_moments_surface_contract() -> None:
    html = (ROOT / "moments_v403_component" / "index.html").read_text(encoding="utf-8")
    lowered = html.lower()
    for token in (
        "i tuoi 3 momenti",
        "data-candidate-id",
        "crea short",
        "modifica nel game editor",
        "fullscreen",
        "overflow-y:auto",
        "fusion_reason",
    ):
        assert token in lowered, token


def test_unified_create_short_surface_has_two_states() -> None:
    html = (ROOT / "share_v156_component" / "index.html").read_text(encoding="utf-8")
    lowered = html.lower()
    for token in (
        "data-v403-state=\"pre-render\"",
        "data-v403-state=\"ready\"",
        "crea short",
        "salva bozza",
        "scegli un altro momento",
        "download",
    ):
        assert token in lowered, token


def test_snapshot_is_json_serializable_metadata_only() -> None:
    s = _base_snapshot()
    s = transition(s, "analysis_completed", {"job_id": "a1", "candidates": [_candidate(0, 10, 40)]})
    s = transition(s, "candidate_selected", {"index": 0})
    raw = json.dumps(s, sort_keys=True)
    assert "bytes" not in raw.lower()
    assert len(raw) < 200_000


def main() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for test in tests:
        test()
    print(f"V403 APP STABILITY FLOW: PASS ({len(tests)} tests)")


if __name__ == "__main__":
    main()
