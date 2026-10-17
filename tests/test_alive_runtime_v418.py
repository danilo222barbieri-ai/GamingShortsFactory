"""GSF Alive 2 (V418): one shared runtime, inlined verbatim in every surface.

web/gsf_alive_v418.js is canonical; tools/gsf_alive_inline.py keeps the copies
identical. Each surface mounts it once, gives it real orbs to breathe and real
next-step targets to guide to, and feeds it real lifecycle events.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gsf_alive_inline  # noqa: E402

RUNTIME = (ROOT / "web" / "gsf_alive_v418.js").read_text(encoding="utf-8")
PAGES = {
    "web/home_v154_component/index.html": ("home", ["upload", "create_with_ai", "create_short", "choose_moment"], ["upload.started", "upload.completed", "watchRender"]),
    "web/ai_v221_component/index.html": ("ai", ["create_with_ai", "choose_moment", "create_short"], ["ai.started", "ai.found", "moment.selected", "watchRender"]),
    "web/share_v156_component/index.html": ("short", ["publish", "connect_social"], ["publish.started", "publish.completed", "render.completed", "social.status"]),
    "web/creator_hub_v156_component/index.html": ("hub", ["connect_social", "upload"], ["social.status"]),
}


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_every_surface_inlines_the_runtime_verbatim() -> None:
    assert gsf_alive_inline.check() == []
    assert sorted(gsf_alive_inline.SURFACES) == sorted(PAGES)


def test_runtime_never_closes_its_script_and_respects_reduced_motion() -> None:
    assert "</script" not in RUNTIME.lower()
    assert "prefers-reduced-motion" in RUNTIME
    assert "pointer-events:none" in RUNTIME.replace(" ", "")


def test_each_page_mounts_once_with_orbs_targets_and_real_events() -> None:
    for rel, (name, targets, events) in PAGES.items():
        html = _read(rel)
        assert html.count('mount({page:"' + name + '"') == 1, rel
        assert html.index("GSF_ALIVE:END */") < html.index('mount({page:"' + name + '"'), rel
        assert "data-alive-orb" in html, rel
        for action in targets:
            assert action in html and "data-alive-next" in html, (rel, action)
        for event in events:
            assert event in html, (rel, event)


def test_render_is_followed_only_when_the_server_really_runs_it() -> None:
    # No page fakes a render: they ask the runtime to watch /job/status instead.
    for rel in PAGES:
        page = gsf_alive_inline.BLOCK.sub("", _read(rel))
        assert "render.started" not in page, rel
    assert '"/job/status?alive=1' in RUNTIME


def test_core_contract_in_node() -> None:
    node = shutil.which("node")
    if not node:
        import pytest

        pytest.skip("node not available")
    out = subprocess.run([node, "--test", str(ROOT / "tests/js/gsf_alive_v418.test.mjs")], capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stdout[-2000:] + out.stderr[-2000:]
