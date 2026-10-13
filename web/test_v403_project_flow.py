#!/usr/bin/env python3
"""V403 durable project-flow behavioral contract."""
from __future__ import annotations

import copy
import math

from app_flow_v403 import (
    SCHEMA_VERSION,
    editor_handoff,
    new_snapshot,
    profile_for_display,
    reconcile_snapshot,
    resolve_route,
    short_handoff,
    transition,
)


def assert_finite_tree(value):
    if isinstance(value, float):
        assert math.isfinite(value), value
    elif isinstance(value, dict):
        for item in value.values():
            assert_finite_tree(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            assert_finite_tree(item)


def sample_moments():
    return [
        {
            "id": "m1",
            "index": 0,
            "start_seconds": 11.5,
            "end_seconds": 26.5,
            "duration": 15,
            "event": "clutch",
            "confidence": 0.93,
            "fusion_reason": "CLUTCH · Reaction · High Action",
            "video": "/media/sid/media/candidate_1.mp4",
        },
        {
            "id": "m2",
            "index": 1,
            "start_seconds": 55.0,
            "end_seconds": 70.0,
            "duration": 15,
            "event": "multi-kill",
            "confidence": 0.87,
            "video": "/media/sid/media/candidate_2.mp4",
        },
        {
            "id": "m3",
            "index": 2,
            "start_seconds": 101.0,
            "end_seconds": 116.0,
            "duration": 15,
            "event": "reaction",
            "confidence": 0.78,
            "video": "/media/sid/media/candidate_3.mp4",
        },
    ]


def test_schema_and_source_survive_routes():
    state = new_snapshot()
    assert state["schema"] == SCHEMA_VERSION == 403
    state = transition(state, "source_ready", {"video_ref": "/media/sid/upload/video.mp4", "ready": True})
    first_ref = state["source"]["video_ref"]
    for route in ("motori", "home", "hub", "motori"):
        state = transition(state, "route_requested", {"route": route})
        assert state["source"]["video_ref"] == first_ref
    assert_finite_tree(state)


def test_analysis_start_and_resume_are_idempotent():
    state = transition(new_snapshot(), "source_ready", {"video_ref": "video.mp4", "ready": True})
    state = transition(state, "analysis_started", {"request_id": "req-1", "engine": "auto", "duration": 15})
    version = state["version"]
    again = transition(state, "analysis_started", {"request_id": "req-1", "engine": "auto", "duration": 15})
    assert again == state
    assert again["version"] == version
    resumed = transition(again, "resume", {})
    assert resumed["analysis"]["request_id"] == "req-1"
    assert resumed["analysis"]["status"] == "running"
    assert resumed["version"] == version


def test_render_start_and_resume_are_idempotent():
    state = transition(new_snapshot(), "source_ready", {"video_ref": "video.mp4", "ready": True})
    state = transition(state, "analysis_completed", {"request_id": "req-1", "moments": sample_moments()})
    state = transition(state, "moment_selected", {"index": 0})
    state = transition(state, "render_started", {"job_id": "render-1"})
    version = state["version"]
    again = transition(state, "render_started", {"job_id": "render-1"})
    assert again == state
    resumed = transition(again, "resume", {})
    assert resumed["render"]["job_id"] == "render-1"
    assert resumed["render"]["status"] == "running"
    assert resumed["version"] == version


def test_analysis_completion_routes_to_moments_and_selection_persists():
    state = transition(new_snapshot(), "source_ready", {"video_ref": "video.mp4", "ready": True})
    state = transition(state, "analysis_started", {"request_id": "req-1", "engine": "best", "duration": 15})
    state = transition(state, "analysis_completed", {"request_id": "req-1", "moments": sample_moments()})
    assert state["route"] == "moments"
    assert len(state["moments"]) == 3
    state = transition(state, "moment_selected", {"index": 1})
    assert state["selected_moment"]["id"] == "m2"
    routed = transition(state, "route_requested", {"route": "hub"})
    resumed = transition(routed, "resume", {})
    assert resumed["selected_moment"]["id"] == "m2"
    assert resolve_route(resumed, "moments") == "moments"


def test_invalid_routes_fall_back_without_destroying_project():
    blank = new_snapshot()
    assert resolve_route(blank, "create_short") == "home"
    source = transition(blank, "source_ready", {"video_ref": "video.mp4", "ready": True})
    assert resolve_route(source, "create_short") == "motori"
    with_moments = transition(source, "analysis_completed", {"request_id": "req", "moments": sample_moments()})
    assert resolve_route(with_moments, "create_short") == "moments"
    assert resolve_route(with_moments, "editor") == "moments"
    assert with_moments["source"]["video_ref"] == "video.mp4"


def test_handoffs_come_from_persisted_selection():
    state = transition(new_snapshot(), "source_ready", {"video_ref": "video.mp4", "ready": True})
    state = transition(state, "analysis_completed", {"request_id": "req", "moments": sample_moments()})
    assert editor_handoff(state) is None
    assert short_handoff(state) is None
    state = transition(state, "moment_selected", {"index": 2})
    editor = editor_handoff(state)
    short = short_handoff(state)
    assert editor["moment_id"] == "m3"
    assert editor["start_seconds"] == 101.0
    assert editor["end_seconds"] == 116.0
    assert editor["source_ref"] == "video.mp4"
    assert short["moment_id"] == "m3"
    assert short["video"] == "/media/sid/media/candidate_3.mp4"


def test_render_completion_stays_on_create_short_ready_state():
    state = transition(new_snapshot(), "source_ready", {"video_ref": "video.mp4", "ready": True})
    state = transition(state, "analysis_completed", {"request_id": "req", "moments": sample_moments()})
    state = transition(state, "moment_selected", {"index": 0})
    state = transition(state, "route_requested", {"route": "create_short"})
    state = transition(state, "render_started", {"job_id": "r1"})
    state = transition(state, "render_completed", {"job_id": "r1", "asset_ref": "/share/final"})
    assert state["route"] == "create_short"
    assert state["render"]["status"] == "ready"
    assert state["render"]["asset_ref"] == "/share/final"


def test_profile_last_valid_payload_survives_refresh_failure():
    valid = {"account_id": "usr_1", "display_name": "Danilo", "avatar": "/creator-hub/avatar", "plan": "PRO", "updated_at": 10}
    shown = profile_for_display(None, valid, "valid")
    assert shown["display_name"] == "Danilo"
    stale = profile_for_display(shown, None, "unavailable")
    assert stale["display_name"] == "Danilo"
    assert stale["_profile_state"] == "stale"
    loading = profile_for_display(stale, None, "loading")
    assert loading["display_name"] == "Danilo"
    newer = dict(valid, display_name="Danilo B.", updated_at=11)
    refreshed = profile_for_display(loading, newer, "valid")
    assert refreshed["display_name"] == "Danilo B."
    signed_out = profile_for_display(refreshed, None, "signed_out")
    assert signed_out["_profile_state"] == "signed_out"
    assert "display_name" not in signed_out


def test_authoritative_reconcile_wins_without_regressing_version():
    local = transition(new_snapshot(), "source_ready", {"video_ref": "local.mp4", "ready": True})
    authoritative = copy.deepcopy(local)
    authoritative = transition(authoritative, "analysis_completed", {"request_id": "req", "moments": sample_moments()})
    merged = reconcile_snapshot(local, authoritative)
    assert merged["version"] == authoritative["version"]
    assert len(merged["moments"]) == 3
    stale = reconcile_snapshot(merged, local)
    assert stale == merged


def main():
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
        print("[PASS]", test.__name__)
    print("V403 PROJECT FLOW CONTRACT: PASS")


if __name__ == "__main__":
    main()
