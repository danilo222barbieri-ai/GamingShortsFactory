from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _function_source(path: str, name: str) -> str:
    text = _source(path)
    tree = ast.parse(text)
    node = next(
        n for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name
    )
    return ast.get_source_segment(text, node) or ""


def test_home_mobile_frame_stays_fixed_and_cannot_create_white_ghost_space():
    embed = _source("web/home_v154_embed.py")
    app = _source("app.py")

    # The modern shell is a full-viewport page, rather than the old V429
    # header/footer inset wrapper. It must not scroll under GameBar.
    assert "@media (max-width:760px){" in embed
    assert "GSF_MOBILE_SURFACE_FIT" in app
    assert "height:100dvh !important;" in embed
    assert "position:fixed !important;" in embed
    assert "inset:0 !important;" in embed
    assert 'iframe[title*="gsf_home_v154"]' in embed
    assert "background:#050D16 !important;" in embed
    assert "z-index:1 !important;" in embed
    assert "z-index:120 !important;" in embed


def test_upload_handoff_bridge_preserves_video_readiness_and_errors():
    bridge = _function_source(
        "web/home_v154_embed.py",
        "_render_v428_uploader_handoff_reset_bridge",
    )

    # Never clear the actual video state or swallow an upload error. This bridge
    # may adjust presentation only, while the Home component owns the lifecycle.
    assert "GSF_V428_UPLOADER_HANDOFF_RESET" in bridge
    assert "data-gsf-has-source" in bridge
    assert "data-gsf-uploader-idle" in bridge
    assert "if(busy){" in bridge
    assert "if(event.origin!==P.location.origin" in bridge
    assert "event.data.state==='done'" in bridge
    assert "!circle.classList.contains('done')" in bridge
    assert "!status.classList.contains('error')" in bridge
    assert "P.addEventListener('message',onMessage)" in bridge
