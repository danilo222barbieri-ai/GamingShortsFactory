"""V416: Home-style skin for the in-player mobile Game Editor.

The editor keeps the V414 layout (every control inside #previewStage); this
layer only changes the look and adds a Crea Short action to the mini player.
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


def test_home_skin_is_loaded_last() -> None:
    html = _read("index.html")
    assert 'href="./home_style_v416.css"' in html
    assert html.index('href="./overlay_v414.css"') < html.index('href="./home_style_v416.css"')
    assert '<meta name="color-scheme" content="light">' in html


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


def test_skin_uses_light_glass_and_brand_tokens() -> None:
    css = _read("home_style_v416.css")
    for token in ("--gsf-primary: #27AEF3", "--gsf-short: #5ED6A0", "--gsf-ai: #9D82FF", "backdrop-filter"):
        assert token in css, token
    assert "rgba(255, 255, 255, .76)" in css


def test_play_never_covers_the_loading_message() -> None:
    css = _read("home_style_v416.css")
    assert "#mediaEmptyState:not([hidden]) ~ .v414-center-play { display: none !important; }" in css
    stage = _stage_html(_read("index.html"))
    assert stage.index('id="mediaEmptyState"') < stage.index('id="playButton"')
