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


def test_home_mobile_frame_stays_between_global_header_and_gamebar():
    embed = _source("web/home_v154_embed.py")

    assert "GSF_V429_HOME_SHELL_BOUNDS" in embed
    assert "top:var(--gsf-shell-content-top,44px) !important;" in embed
    assert "bottom:var(--gsf-shell-content-bottom,112px) !important;" in embed
    assert "height:auto !important;" in embed
    assert "height:100% !important;" in embed
    assert "min-height:0 !important;" in embed


def test_notifications_use_one_compact_event_surface_on_mobile():
    bridge = _function_source(
        "web/home_v154_embed.py",
        "_render_v428_uploader_handoff_reset_bridge",
    )

    assert "GSF_V429_COMPACT_NOTIFICATIONS" in bridge
    assert "width:min(300px,calc(100vw - 28px))!important" in bridge
    assert "min-height:48px!important" in bridge
    assert "grid-template-columns:20px minmax(0,1fr) 20px!important" in bridge
    assert "font-size:14px!important" in bridge
    assert "font-size:12px!important" in bridge

    # V418 may keep its guidance whispers, but event notifications have one owner.
    assert "GSF_V429_SINGLE_EVENT_NOTIFICATIONS" in bridge
    assert "moment.selected" in bridge
    assert "recovered" in bridge
    assert "originalAlive.call(notify,state)" in bridge
