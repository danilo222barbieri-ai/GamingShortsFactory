"""Night Arena: one single look for the whole app.

web/gsf_night_arena.css is the canonical theme. Every user-facing surface
inlines it verbatim between GSF_NIGHT_ARENA:BEGIN / GSF_NIGHT_ARENA:END so a
page can never drift back to a private palette.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = (ROOT / "web" / "gsf_night_arena.css").read_text(encoding="utf-8").strip()
SURFACES = [
    "web/creator_hub_v156_component/index.html",
    "web/ai_v221_component/index.html",
    "web/game_editor_mobile_component/index.html",
    "web/share_v156_component/index.html",
    "web/home_v154_component/index.html",
]
BLOCK = re.compile(r"/\* GSF_NIGHT_ARENA:BEGIN \*/\n(.*?)\n/\* GSF_NIGHT_ARENA:END \*/", re.S)


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_theme_keeps_the_official_brand_hues() -> None:
    for hue in ("#27AEF3", "#53E0EA", "#5ED6A0", "#9D82FF"):
        assert hue in THEME, hue
    assert "color-scheme:dark" in THEME
    assert "prefers-reduced-motion" in THEME


def test_every_surface_inlines_the_canonical_theme_verbatim() -> None:
    for rel in SURFACES:
        blocks = BLOCK.findall(_read(rel))
        assert len(blocks) == 1, f"{rel}: expected exactly one Night Arena block"
        assert blocks[0].strip() == THEME, f"{rel}: Night Arena block drifted from web/gsf_night_arena.css"


def test_page_overrides_follow_the_shared_theme() -> None:
    for rel in SURFACES:
        html = _read(rel)
        assert html.index("GSF_NIGHT_ARENA:END") < html.index("GSF_NIGHT_ARENA_PAGE:BEGIN"), rel


def test_no_surface_declares_a_light_color_scheme() -> None:
    for rel in SURFACES:
        html = _read(rel)
        assert 'content="light"' not in html, rel
        assert "color-scheme:light" not in html.replace(" ", ""), rel


def test_hub_empty_states_offer_the_next_step() -> None:
    hub = _read("web/creator_hub_v156_component/index.html")
    assert "data-empty-cta" in hub
    assert 'shell("home",{section:""})' in hub
    # Social status: connected is a full green ring, otherwise dashed with "+".
    assert ".socialDot.connected{border:3px solid #5ED6A0" in hub
    assert "border:2px dashed" in hub
