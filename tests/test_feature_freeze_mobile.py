from pathlib import Path

# Release regression contract: these four assertions and the synced Alive runtime must stay green through Railway promotion.
ROOT = Path(__file__).resolve().parents[1]


def test_short_source_uses_full_available_duration_without_entering_long_ai_wait():
    from web.ai_engines_v412 import effective_analysis_duration

    assert effective_analysis_duration(9.0, 15.0) == 9.0
    assert effective_analysis_duration(18.0, 30.0) == 18.0
    assert effective_analysis_duration(42.0, 60.0) == 42.0
    assert effective_analysis_duration(90.0, 60.0) == 60.0
    assert effective_analysis_duration(4.9, 15.0) == 0.0

    app = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "effective_analysis_duration" in app
    assert "_gsf_effective_analysis_duration" in app


def test_oauth_callbacks_return_to_the_canonical_creator_hub_shell():
    server = (ROOT / "web/direct_upload_server.py").read_text(encoding="utf-8")
    nav = (ROOT / "web/gsf_navigation_lifecycle.js").read_text(encoding="utf-8")

    assert 'target="/?gsf_page=hub&gsf_section=social"' in server
    assert "oauth_return" in server
    assert "GSF_OAUTH_CANONICAL_RETURN" in nav
    assert "q.has('oauth_return')" in nav


def test_mobile_home_uses_nested_frame_height_after_shell_is_ready():
    home = (ROOT / "web/home_v154_component/index.html").read_text(encoding="utf-8")
    assert "GSF_HOME_NESTED_VIEWPORT_FIX" in home
    assert "html.gsf-v343-parent-ready #home154" in home
    assert "height:100%!important" in home
    assert "min-height:100%!important" in home
    assert "max-height:100%!important" in home


def test_alive_notification_pill_cannot_expand_over_the_phone_ui():
    alive = (ROOT / "web/gsf_alive_v418.js").read_text(encoding="utf-8")
    assert "GSF_ALIVE_COMPACT_PILL" in alive
    assert "max-width:min(78vw,320px)" in alive
    assert "text-overflow:ellipsis" in alive
    assert "overflow:hidden" in alive
