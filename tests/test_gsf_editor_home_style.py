"""In-player mobile Game Editor skins.

V416 keeps the V414 layout (every control inside #previewStage) and the mini
player's Crea Short action; V417 (Night Arena) is the single app look loaded
last: mini player fills its slot, nothing useless covers the gameplay.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "web" / "game_editor_mobile_component"


def _read(name: str) -> str:
    return (COMPONENT / name).read_text(encoding="utf-8")


def _stage_html(html: str) -> str:
    start = html.index('<div id="previewStage"')
    end = html.index("</section>\n    </section>\n  </main>")
    return html[start:end]


def test_night_arena_skin_is_loaded_last() -> None:
    html = _read("index.html")
    assert html.index('href="./overlay_v414.css"') < html.index('href="./home_style_v416.css"') < html.index('href="./night_arena_v417.css"')
    assert '<meta name="color-scheme" content="dark">' in html


def test_nothing_useless_covers_the_gameplay() -> None:
    css = _read("night_arena_v417.css")
    assert ".v414-top-hud .editor-kicker,\n.ratio-badge,\n.v414-top-hud .ai-top-button { display: none !important; }" in css
    # Save status stays for screen readers; only errors are visible.
    assert '.v414-top-hud #editorStatus[data-state="error"]' in css
    assert ".editor-app.is-expanded .v414-top-hud #backButton { display: none; }" in css


def test_mini_player_fills_its_slot() -> None:
    css = _read("night_arena_v417.css")
    mini = re.search(r"\.editor-app\.is-mini \.preview-stage\s*\{(?P<body>.*?)\}", css, re.S)
    assert mini is not None
    # Sized from the iframe viewport, which the shell keeps between header and Game Bar.
    assert "width: min(calc(100vw - 20px), calc((100dvh - 20px) * 9 / 16));" in mini.group("body")
    assert "position:" not in mini.group("body")


def test_mini_player_has_crea_short_inside_the_video() -> None:
    stage = _stage_html(_read("index.html"))
    assert 'id="miniCreateShortButton"' in stage
    assert 'id="enterEditorButton"' in stage
    script = _read("editor.mjs")
    assert '$("#miniCreateShortButton").addEventListener("click", () => requestEditorAction("continue_to_short"));' in script


def test_mini_actions_only_show_in_mini_and_stay_in_stage() -> None:
    css = _read("home_style_v416.css")
    assert re.search(r"\.mini-short-button\s*\{[^}]*position:\s*absolute;[^}]*display:\s*none;", css, re.S)
    assert ".editor-app.is-mini .mini-short-button { display: inline-flex; }" in css
    # The mini player must not grow over the app header or the Game Bar/footer.
    mini_stage = re.search(r"\.editor-app\.is-mini \.preview-stage\s*\{(?P<body>.*?)\}", css, re.S)
    assert mini_stage is not None
    for prop in ("width:", "height:", "max-height:", "position:"):
        assert prop not in mini_stage.group("body"), prop


def test_tool_rail_order_and_labels_unchanged() -> None:
    stage = _stage_html(_read("index.html"))
    tools = re.findall(r'<button[^>]+data-tool="([^"]+)"[^>]*>.*?</button>', stage, re.S)
    assert tools == ["clip", "frame", "look", "hud", "text", "audio", "ai"]


def test_skin_uses_dark_glass_and_brand_tokens() -> None:
    css = _read("night_arena_v417.css")
    for token in ("#27AEF3", "#53E0EA", "#9D82FF", "backdrop-filter", "--v417-glass: rgba(10, 26, 42, .62);"):
        assert token in css, token


def test_play_never_covers_the_loading_message() -> None:
    css = _read("home_style_v416.css")
    assert "#mediaEmptyState:not([hidden]) ~ .v414-center-play { display: none !important; }" in css
    stage = _stage_html(_read("index.html"))
    assert stage.index('id="mediaEmptyState"') < stage.index('id="playButton"')


def test_sliders_are_styled_and_trim_handles_untouched() -> None:
    css = _read("home_style_v416.css")
    assert ".v414-transport input[type=\"range\"]::-webkit-slider-runnable-track" in css
    assert ".v414-tool-sheet input[type=\"range\"]::-webkit-slider-thumb" in css
    # The trim handles are invisible native ranges over the strip: never restyle them.
    assert ".trim-range" not in css.split("/* Sliders:")[1]
