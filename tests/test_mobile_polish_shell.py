"""Mobile shell polish contracts: surfaces fit the phone screen, no ghost V250 chrome,
one page canvas that continues the shell header, and a push client that actually parses."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "app.py").read_text(encoding="utf-8")
HEADER_RGB = "250,253,255"  # shell header/footer colour = #FAFDFF


def _mobile_page_block():
    start = APP.index("GSF_MOBILE_SURFACE_FIT")
    return APP[start:APP.index("#gsf-page-nav-v249{", start)]


def test_v250_page_chrome_is_hidden_on_phones():
    block = _mobile_page_block()
    assert ".gsf-page-top-v250,.gsf-page-footer-v250,.gsf-page-ad-v250{display:none!important}" in block


def test_surfaces_end_at_the_screen_and_editor_stops_at_the_game_bar():
    block = _mobile_page_block()
    for shell in ("#gsf-social-overlay-v159 .gsf-social-shell", "#gsf-creator-hub-live-v160 .gsf-hub-shell-v160",
                  "#gsf-ai-overlay-v221 .gsf-ai-shell", "#gsf-account-overlay-v223 .gsf-account-shell"):
        assert shell in block, shell
    assert "bottom:0!important;height:auto!important;" in block
    editor = block[block.index("#gsf-editor-overlay-v220 .gsf-editor-shell{"):]
    assert "top:var(--gsf-shell-content-top,44px)!important;" in editor
    assert "bottom:var(--gsf-shell-content-bottom,112px)!important;height:auto!important;" in editor
    # The rules must live inside the phone media query, not leak to desktop.
    media = APP.rindex("@media(max-width:760px){", 0, APP.index("GSF_MOBILE_SURFACE_FIT"))
    assert APP.index("GSF_MOBILE_SURFACE_FIT") - media < 2000


def test_page_canvas_starts_with_the_header_colour():
    assert f"rgba({HEADER_RGB},.99)" in APP, "shell header colour changed: update the canvas"
    surfaces = {
        "home": ROOT / "web/home_v154_component/index.html",
        "hub": ROOT / "web/creator_hub_v156_component/index.html",
        "ai": ROOT / "web/ai_v221_component/index.html",
        "editor": ROOT / "web/game_editor_mobile_component/editor.css",
    }
    for name, path in surfaces.items():
        text = path.read_text(encoding="utf-8")
        assert "GSF_HEADER_CANVAS" in text, name
        assert re.search(r"linear-gradient\(180deg,#FAFDFF 0%", text, re.I), name
    assert "linear-gradient(180deg,#FAFDFF 0%" in APP


def test_push_client_script_parses():
    src = (ROOT / "web/direct_upload_server.py").read_text(encoding="utf-8")
    start = src.index("def _push_client_bytes")
    end = src.index("\ndef ", start + 10)
    ns: dict = {}
    exec(src[start:end], ns)  # noqa: S102 - pure function returning a literal
    js = ns["_push_client_bytes"]()
    js = js.decode("utf-8") if isinstance(js, bytes) else js
    # The toast stylesheet is a double-quoted JS string: font names inside must not use double quotes.
    assert 'font-family:"Avenir' not in js
    node = shutil.which("node")
    if node:
        tmp = ROOT / "tools" / ".push_client_check.js"
        tmp.write_text(js, encoding="utf-8")
        try:
            result = subprocess.run([node, "--check", str(tmp)], capture_output=True, text=True)
        finally:
            tmp.unlink(missing_ok=True)
        assert result.returncode == 0, result.stderr[-400:]
