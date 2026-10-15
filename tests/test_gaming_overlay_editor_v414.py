from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "web" / "game_editor_mobile_component"


def _read(name: str) -> str:
    path = COMPONENT / name
    assert path.is_file(), f"missing V414 editor source: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def _stage_html(html: str) -> str:
    start = html.index('id="previewStage"')
    stage_open = html.rfind("<", 0, start)
    script = html.index('<script type="module"', start)
    return html[stage_open:script]


def test_v414_loads_additive_overlay_after_base_stylesheet() -> None:
    html = _read("index.html")
    assert 'href="./editor.css"' in html
    assert 'href="./overlay_v414.css"' in html
    assert html.index('href="./editor.css"') < html.index('href="./overlay_v414.css"')


def test_gameplay_stage_owns_every_primary_editing_surface() -> None:
    html = _read("index.html")
    stage = _stage_html(html)
    for element_id in (
        "backButton",
        "projectTitle",
        "editorStatus",
        "undoButton",
        "redoButton",
        "fullscreenButton",
        "gameplayVideo",
        "playButton",
        "timelineTrack",
        "toolBar",
        "toolDock",
        "saveDraftButton",
        "continueButton",
    ):
        assert f'id="{element_id}"' in stage, element_id


def test_mini_player_expands_from_an_in_video_affordance() -> None:
    html = _read("index.html")
    stage = _stage_html(html)
    script = _read("editor.mjs")
    assert 'id="enterEditorButton"' in stage
    assert 'class="editor-app is-mini"' in html
    assert "enterEditorButton" in script
    assert "toggleFullscreen" in script
    assert 'classList.toggle("is-mini"' in script
    assert 'classList.toggle("is-expanded"' in script


def test_loading_layer_does_not_block_in_video_editor_controls() -> None:
    stage = _stage_html(_read("index.html"))
    tag = re.search(r'<div id="mediaEmptyState"[^>]*>', stage)
    assert tag is not None
    assert 'style="z-index:25"' in tag.group(0)
    css = _read("overlay_v414.css")
    assert ".v414-top-hud" in css and "z-index: 50" in css
    assert ".enter-editor-button" in css and "z-index: 45" in css


def test_save_draft_stays_reachable_on_phone_widths() -> None:
    # A phone-width media query once hid #saveDraftButton, leaving users unable
    # to save a draft from the expanded editor on iPhone-class screens.
    css = _read("overlay_v414.css")
    hidden = re.search(r"\.draft-button\s*\{[^}]*display:\s*none", css)
    assert hidden is None


def test_fullscreen_avoids_webkit_100vw_rounding_overflow() -> None:
    css = _read("overlay_v414.css")
    root_block = re.search(
        r"\.editor-app\.is-expanded,\s*\.editor-app:fullscreen,\s*\.editor-app:-webkit-full-screen\s*\{(?P<body>.*?)\}",
        css,
        re.S,
    )
    stage_block = re.search(
        r"\.editor-app\.is-expanded \.preview-stage,\s*\.editor-app:fullscreen \.preview-stage,\s*\.editor-app:-webkit-full-screen \.preview-stage\s*\{(?P<body>.*?)\}",
        css,
        re.S,
    )
    assert root_block is not None
    assert stage_block is not None
    assert "width: 100%;" in root_block.group("body")
    assert "max-width: none;" in root_block.group("body")
    assert "width: 100vw;" not in root_block.group("body")
    assert "width: 100%;" in stage_block.group("body")
    assert "height: 100%;" in stage_block.group("body")
    assert "width: 100vw;" not in stage_block.group("body")


def test_camera_and_ai_controls_are_inside_video_and_keep_legacy_tool_order() -> None:
    html = _read("index.html")
    stage = _stage_html(html)
    tools = re.findall(r'<button[^>]+data-tool="([^"]+)"[^>]*>.*?</button>', stage, re.S)
    assert tools == ["clip", "frame", "text", "audio", "ai"]
    for mode in ("static", "follow", "dynamic", "cinematic"):
        assert f'data-camera-mode="{mode}"' in stage
    for action in ("follow_action", "auto_vertical", "zoom_moments", "protect_hud", "auto_caption", "improve_all"):
        assert f'data-ai-quick="{action}"' in stage
    for label in ("Segui l'azione", "Auto 9:16", "Zoom momenti", "Proteggi HUD", "Auto caption", "Migliora tutto"):
        assert label in stage


def test_v414_glass_layer_is_video_first_not_external_card_layout() -> None:
    css = _read("overlay_v414.css")
    for token in (
        ".editor-app.is-mini",
        ".editor-app.is-expanded",
        ".preview-stage",
        ".v414-top-hud",
        ".v414-tool-rail",
        ".v414-timeline",
        ".v414-tool-sheet",
        "backdrop-filter",
        "env(safe-area-inset-top)",
        "env(safe-area-inset-bottom)",
    ):
        assert token in css, token
    assert "position: absolute" in css or "position:absolute" in css


def test_playback_state_reduces_nonessential_chrome_without_polling() -> None:
    css = _read("overlay_v414.css")
    script = _read("editor.mjs")
    assert ".is-playing" in css
    assert 'classList.add("is-playing")' in script
    assert 'classList.remove("is-playing")' in script
    combined = "\n".join((_read("index.html"), script, css))
    for forbidden in ("MutationObserver", "setInterval", "createElement(\"canvas\")", "createElement('canvas')"):
        assert forbidden not in combined, forbidden


def test_tool_sheet_is_static_and_closable_inside_stage() -> None:
    html = _read("index.html")
    stage = _stage_html(html)
    script = _read("editor.mjs")
    assert 'id="closeToolSheetButton"' in stage
    assert 'id="toolDock"' in stage
    assert "closeToolSheetButton" in script
    assert "is-tool-open" in script


def test_v414_node_state_contracts() -> None:
    result = subprocess.run(
        ["node", "--test", str(ROOT / "tests" / "js" / "gaming_overlay_editor_v414_state.test.mjs")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
