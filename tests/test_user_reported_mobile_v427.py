from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def _compact(value):
    return "".join(value.split())


def test_mini_editor_does_not_repeat_top_navigation_controls():
    html = _text("web/game_editor_mobile_component/index.html")
    compact = _compact(html)
    assert "GSF_V427_MINI_EDITOR_HEADER_CLEANUP" in html
    assert ".editor-app.is-mini.editor-header{display:none!important}" in compact


def test_home_obsolete_footer_is_hidden_without_waiting_for_parent_ready():
    home = _text("web/home_v154_component/index.html")
    compact = _compact(home)
    assert "GSF_V427_HOME_FOOTER_RACE" in home
    assert "htmlbody#home154#home154.siteFooter{display:none!important}" in compact


def test_ai_duration_choices_stay_on_one_horizontal_row():
    ai = _text("web/ai_v221_component/index.html")
    compact = _compact(ai)
    assert "GSF_V427_DURATION_INLINE" in ai
    assert ".seg{display:inline-grid;grid-template-columns:repeat(3,minmax(0,1fr))" in compact
    for seconds in (15, 30, 60):
        assert f'data-duration="{seconds}"' in ai


def test_alive_top_status_is_icon_only_not_a_text_pill_by_profile():
    alive = _text("web/gsf_alive_v418.js")
    compact = _compact(alive)
    assert "GSF_V427_ALIVE_HEADER_DOT" in alive
    assert 'bubbleEl.classList.toggle("header-dot",page.dock!=="bottom")' in compact
    assert "#gsf-alive-bubble.header-dot.l,#gsf-alive-bubble.header-dotsmall{display:none!important}" in compact
    assert "#gsf-alive-bubble.header-dot{width:38px;height:38px" in compact


def test_creator_hub_short_cards_use_real_video_preview():
    hub = _text("web/creator_hub_v156_component/index.html")
    assert "GSF_V427_SHORT_CARD_PREVIEW" in hub
    assert 'class="cardPreview"' in hub
    assert 'playsinline muted preload="metadata"' in hub
    assert '/creator-hub/short/file?id=' in hub


def test_instagram_keeps_meta_professional_fallback_after_direct_login():
    server = _text("web/direct_upload_server.py")
    assert "GSF_V428_INSTAGRAM_DIRECT_FIRST" in server
    assert "if INSTAGRAM_APP_ID and INSTAGRAM_APP_SECRET:" in server
    assert '"mode":"instagram_login"' in server
    # Meta/Facebook remains available only as the compatibility fallback.
    assert '"mode":"facebook_login"' in server
    assert "META_SCOPES" in server


def test_empty_ai_rank_pool_has_bounded_fallback_candidates():
    from web.ai_engines_v412 import fallback_rank_pool

    diagnostics = {
        "8.0": {"features": {"motion_burst": 0.35, "event_score": 0.20, "dead_ratio": 0.0}},
        "22.0": {"features": {"motion_burst": 0.90, "event_score": 0.85, "reaction": 0.72, "dead_ratio": 0.0}},
        "47.0": {"features": {"motion_burst": 0.45, "event_score": 0.35, "dead_ratio": 0.1}},
    }
    ranked = fallback_rank_pool(diagnostics, source_duration=75, clip_duration=15, target=3)
    assert ranked
    assert ranked[0][1] == 22.0
    assert all(0.0 <= start <= 60.0 for _, start in ranked)

    coverage = fallback_rank_pool({}, source_duration=90, clip_duration=15, target=3)
    assert 1 <= len(coverage) <= 3
    assert len({round(start, 3) for _, start in coverage}) == len(coverage)
    assert all(0.0 <= start <= 75.0 for _, start in coverage)


def test_app_uses_fallback_only_after_normal_ranker_returns_empty():
    app = _text("app.py")
    assert "GSF_V427_AI_EMPTY_POOL_FALLBACK" in app
    assert "fallback_rank_pool" in app
    assert "if not _pool:" in app
