from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
COMPONENT = WEB / "game_editor_mobile_component"


def _read(path: Path) -> str:
    assert path.is_file(), f"missing canonical mobile editor source: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def _mobile_bridge(app: str) -> str:
    start = app.index("/* GSF_MOBILE_EDITOR_2026_BRIDGE */")
    end = app.index("/* GSF_MOBILE_EDITOR_2026_BRIDGE_END */", start)
    return app[start:end]


def test_mobile_editor_is_a_direct_canonical_nginx_surface() -> None:
    nginx = _read(WEB / "nginx.conf.template")
    index = _read(COMPONENT / "index.html")
    css = _read(COMPONENT / "editor.css")
    script = _read(COMPONENT / "editor.mjs")

    assert 'id="gameEditorApp"' in index
    assert 'href="./editor.css"' in index
    assert 'src="./editor.mjs"' in index
    assert css.strip() and script.strip()
    assert "location = /game-editor-mobile {" in nginx
    route = nginx[nginx.index("location /game-editor-mobile/ {") :]
    route = route[: route.index("\n    }")]
    assert "alias /app/web/game_editor_mobile_component/;" in route
    assert "try_files $uri $uri/ /game-editor-mobile/index.html;" in route
    assert 'add_header Cache-Control "no-store" always;' in route
    assert 'add_header X-Frame-Options "SAMEORIGIN" always;' in route
    assert "Content-Security-Policy" in route


def test_component_ready_init_handshake_is_same_origin_and_complete() -> None:
    script = _read(COMPONENT / "editor.mjs")

    assert "GSF_GAME_EDITOR_READY" in script
    assert "GSF_GAME_EDITOR_INIT" in script
    assert "event.origin !== location.origin" in script
    assert "event.source !== parent" in script
    assert "session" in script
    assert "project" in script
    assert "media" in script
    assert "initial_state" in script
    assert "event_map" in script
    assert "brain_context" in script
    assert "ai_suggestions" in script


def test_ai_actions_are_distinct_and_keep_selected_moment_payload() -> None:
    ai = _read(WEB / "ai_v221_component" / "index.html")
    app = _read(ROOT / "app.py")

    assert 'send("open_editor",selectedPayload())' in ai
    assert 'send("create_short",selectedPayload())' in ai
    assert 'send("preview",{...selectedPayload(),intent:' not in ai
    for field in ("candidate_id", "video", "start_time", "end_time"):
        assert field in ai

    bridge = app[app.index("if(e.data.type==='GSF_AI_UI')") :]
    bridge = bridge[: bridge.index("if(e.data.type!=='GSF_SHELL_NAV')")]
    for field in ("candidate_id", "video", "start_time", "end_time", "duration", "engine", "index"):
        assert re.search(rf"\b{field}\s*:\s*e\.data\.{field}\b", bridge), field


def test_shell_selects_new_editor_only_for_mobile_and_sends_init() -> None:
    app = _read(ROOT / "app.py")
    bridge = _mobile_bridge(app)

    assert "matchMedia('(max-width: 760px)')" in bridge
    assert "'/game-editor-mobile/'" in bridge
    assert "'/editor-live/'" in bridge
    assert "GSF_GAME_EDITOR_READY" in bridge
    assert "GSF_GAME_EDITOR_INIT" in bridge
    for field in ("session", "project", "media", "initial_state", "event_map", "brain_context", "ai_suggestions"):
        assert re.search(rf"\b{field}\s*:", bridge), field


def test_mobile_continue_uses_named_short_route_without_label_lookup() -> None:
    app = _read(ROOT / "app.py")
    bridge = _mobile_bridge(app)

    assert "continue_to_short" in bridge
    assert re.search(r"GSF_SHELL_NAV['\"]\s*,\s*target\s*:\s*['\"]short", bridge)
    for forbidden in ("innerText", "textContent", "querySelectorAll('button", 'querySelectorAll("button'):
        assert forbidden not in bridge


def test_mobile_actions_use_ordered_save_ack_and_explicit_destinations() -> None:
    app = _read(ROOT / "app.py")
    bridge = _mobile_bridge(app)

    assert "mobileSaveChain" in bridge
    assert "'/editor/state/save'" in bridge
    assert "'/creator-hub/project/save-draft'" in bridge
    assert "GSF_GAME_EDITOR_SAVE_STATUS" in bridge
    assert "sequence" in bridge
    for action in ("autosave", "save_draft", "continue_to_short", "close", "fullscreen_changed"):
        assert action in bridge
    save_index = bridge.index("persistMobileEditorState")
    route_index = bridge.index("navigateMobileEditorToShort", save_index)
    assert save_index < route_index
