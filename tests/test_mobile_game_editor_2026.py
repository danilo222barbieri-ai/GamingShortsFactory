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
    assert "application/javascript js mjs;" in route
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

    assert 'send("preview",{...payload,intent:"edit"});send("open_editor",payload)' in ai
    assert 'send("preview",{...payload,intent:"create_short"});send("create_short",payload)' in ai
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
    assert re.search(
        r"if\(action==='close'\)\{\s*persistMobileEditorState\(message\).*?close\(\)",
        bridge,
        re.S,
    ), "Back must persist the flushed editor state before closing"


def test_workspace_has_professional_single_clip_hierarchy() -> None:
    html = _read(COMPONENT / "index.html")

    for element_id in (
        "backButton",
        "projectTitle",
        "editorStatus",
        "undoButton",
        "redoButton",
        "fullscreenButton",
        "previewStage",
        "gameplayVideo",
        "playButton",
        "scrubRange",
        "timelineTrack",
        "trimInRange",
        "trimOutRange",
        "eventMarkers",
        "moreButton",
        "saveDraftButton",
        "continueButton",
    ):
        assert f'id="{element_id}"' in html, element_id
    assert 'aria-label="Timeline singola clip"' in html
    assert 'aria-live="polite"' in html
    assert "9:16" in html


def test_primary_tools_and_static_panels_have_approved_order() -> None:
    html = _read(COMPONENT / "index.html")
    tools = re.findall(r'<button[^>]+data-tool="([^"]+)"[^>]*>\s*<span[^>]*>.*?</span>\s*([^<]+)\s*</button>', html, re.S)

    assert [label.strip() for _key, label in tools] == ["Taglio", "Inquadratura", "Testo", "Audio", "AI"]
    assert [key for key, _label in tools] == ["clip", "frame", "text", "audio", "ai"]
    for panel in ("clip", "frame", "text", "audio", "ai", "more"):
        assert f'data-panel="{panel}"' in html
    assert 'data-tool="more"' not in html


def test_mobile_accessibility_performance_and_safe_area_contract() -> None:
    html = _read(COMPONENT / "index.html")
    css = _read(COMPONENT / "editor.css")
    script = _read(COMPONENT / "editor.mjs")
    combined = "\n".join((html, css, script))

    assert "min-height: 44px" in css or "min-height:44px" in css
    assert "env(safe-area-inset-top)" in css
    assert "env(safe-area-inset-bottom)" in css
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert "overflow-x: hidden" in css
    assert "loadedmetadata" in script
    assert "timeupdate" in script
    assert "requestEditorAction(\"save_draft\")" in script
    assert "requestEditorAction(\"continue_to_short\")" in script
    for forbidden in (
        "MutationObserver",
        "setInterval",
        "streamlit:rerun",
        "createElement(\"canvas\")",
        "createElement('canvas')",
        "V389_",
        "V390_",
        "V391_",
        "V392_",
        "V393_",
        "V394_",
        "V395_",
    ):
        assert forbidden not in combined, forbidden


def test_desktop_editor_route_and_legacy_source_remain_separate() -> None:
    nginx = _read(WEB / "nginx.conf.template")
    desktop = _read(WEB / "editor_2027_component" / "index.html")

    desktop_route = nginx[nginx.index("location /editor-live/ {") :]
    desktop_route = desktop_route[: desktop_route.index("\n    }")]
    assert "alias /app/web/editor_2027_component/;" in desktop_route
    assert "game_editor_mobile_component" not in desktop_route
    assert "V394_MOBILE_EDITOR_FOOTER_RESTORE" in desktop


def test_fullscreen_gestures_and_ai_are_explicit_mobile_interactions() -> None:
    html = _read(COMPONENT / "index.html")
    css = _read(COMPONENT / "editor.css")
    script = _read(COMPONENT / "editor.mjs")

    assert "requestFullscreen" in script
    assert 'addEventListener("fullscreenchange"' in script
    assert "fullscreen_changed" in script
    assert "setPointerCapture" in script
    assert "releasePointerCapture" in script
    for event_name in ("pointerdown", "pointermove", "pointerup", "pointercancel", "lostpointercapture"):
        assert event_name in script
    assert "requestAnimationFrame" in script
    assert "projectGestureViewport" in script
    assert "touch-action: none" in css

    for action in ("Anteprima", "Applica", "Annulla anteprima"):
        assert action in script
    assert 'setAttribute("data-ai-action", "apply")' in script
    assert 'setAttribute("data-ai-action", "preview")' in script
    assert 'setAttribute("data-ai-action", "revert")' in script
    assert "previewSuggestion" in script
    assert 'id="resetFrameButton"' in html


def test_parent_fullscreen_fallback_hides_and_restores_global_chrome() -> None:
    app = _read(ROOT / "app.py")
    bridge = _mobile_bridge(app)

    assert "gsf-mobile-editor-fullscreen" in bridge
    assert "#gsf-global-gamebar" in bridge
    assert "#gsf-global-header" in bridge
    assert "#gsf-global-footer" in bridge
    assert "100dvh" in bridge
    assert "GSF_GAME_EDITOR_SHELL_CLOSE" in bridge
    assert "document.documentElement.classList.remove('gsf-mobile-editor-fullscreen')" in bridge

    script = _read(COMPONENT / "editor.mjs")
    assert "GSF_GAME_EDITOR_SHELL_CLOSE" in script
    assert "exitFullscreenForShellClose" in script
