from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_mobile_home_removes_legacy_nav_footer_from_layout():
    bridge = (ROOT / "web/home_v154_embed.py").read_text(encoding="utf-8")
    compact = "".join(bridge.split())
    assert "GSF_V430_GLOBAL_GAMEBAR_SAFE_HOME" in bridge
    assert ".bottomNav,.siteFooter{display:none!important}" in compact
    assert "padding-bottom:max(18px,env(safe-area-inset-bottom))!important" in compact
    assert "ensureHomeGamebarSafeLayout(doc)" in compact


def test_mobile_home_stage_does_not_absorb_freed_nav_space():
    bridge = (ROOT / "web/home_v154_embed.py").read_text(encoding="utf-8")
    compact = "".join(bridge.split())
    assert "GSF_V431_STABLE_HOME_ACTION_POSITION" in bridge
    assert ".stage{" in compact
    assert "flex:00clamp(300px,42dvh,330px)!important" in compact
    assert "min-height:clamp(300px,42dvh,330px)!important" in compact
