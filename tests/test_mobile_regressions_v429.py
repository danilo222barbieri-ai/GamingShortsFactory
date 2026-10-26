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


def test_restored_home_keeps_full_viewport_and_original_gamebar_reserve():
    embed = _function_source("web/home_v154_embed.py", "render_home_v154")
    home = _source("web/home_v154_component/index.html")

    # V429 clipped the approved fullscreen Home. Protect its deliberate removal,
    # plus the original internal reserve that keeps action cards above Game Bar.
    assert "GSF_V429_HOME_SHELL_BOUNDS" not in embed
    assert "position:fixed !important;" in embed
    assert "inset:0 !important;" in embed
    assert "height:100dvh !important;" in embed
    assert "GSF_HOME_SHELL_FIT" in home
    assert "const need=Math.max(68" in home
    assert "GSF_V428_GLOBAL_GAMEBAR_OWNS_NAV" not in home


def test_notifications_keep_one_parent_owned_bounded_event_surface():
    client = _function_source("web/direct_upload_server.py", "_push_client_bytes")
    bridge = _function_source(
        "web/home_v154_embed.py", "_render_v428_uploader_handoff_reset_bridge",
    )

    # The uploader bridge is behavior-only; notification layout belongs to the
    # existing global service, not the retired V429 local CSS/Alive adapter.
    assert "GSF_V429_COMPACT_NOTIFICATIONS" not in bridge
    assert "GSF_V429_SINGLE_EVENT_NOTIFICATIONS" not in bridge
    assert "UI.GSFNotify&&UI.GSFNotify.continuityVersion===1" in client
    assert "host.id='gsf-site-toast-stack'" in client
    assert "records.size>=8" in client
    assert "filter(r=>r.el).length<2" in client
    assert "aliveSeen.get(job)===stamp" in client
    assert "upsert('alive:'+job" in client
    assert 'if(!window.GSFNotify.handles("upload"))' in client
    assert 'if(!window.GSFNotify.handles("render"))' in client
