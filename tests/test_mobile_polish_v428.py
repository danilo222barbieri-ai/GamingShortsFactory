"""V428 regressions for the user-approved mobile polish pass.

These are intentionally product-level contracts: they protect the working flow while
we remove UI clutter and make final Short creation explicit.
"""
from __future__ import annotations

import ast
import secrets
import tempfile
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _source(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _function_source(path: str, name: str) -> str:
    text = _source(path)
    tree = ast.parse(text)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(text, node) or ""


def test_editor_done_closes_to_draft_and_only_create_short_continues_to_render():
    editor = _source("web/game_editor_mobile_component/editor.mjs")
    assert '$("#continueButton").addEventListener("click", () => requestEditorAction("close"));' in editor
    assert '$("#miniCreateShortButton").addEventListener("click", () => requestEditorAction("continue_to_short"));' in editor

    app = _source("app.py")
    close = app.index("if(action==='close')")
    close_block = app[close:close + 500]
    assert "navigate({target:'home'})" in close_block
    assert "target:'short'" not in close_block


def test_expanded_editor_hides_placeholder_project_identity():
    editor_page = _source("web/game_editor_mobile_component/index.html")
    assert "GSF_V428_HIDE_EXPANDED_PLACEHOLDER_TITLE" in editor_page
    assert ".editor-app.is-expanded .project-identity{display:none!important}" in editor_page


def test_moments_screen_is_clean_swipeable_and_uses_create_short_language():
    page = _source("web/ai_v221_component/index.html")
    assert 'id="runChip"' not in page
    assert 'id="savedChip"' not in page
    assert 'id="findMoreMoments"' in page
    assert 'id="momentDots"' in page
    assert "GSF_V428_MOMENT_CAROUSEL" in page
    assert "scroll-snap-type:x mandatory" in page
    assert "scroll-snap-align:center" in page
    assert "renderMomentDots" in page
    assert ">Crea Short</button>" in page
    assert ">Pubblica</button>" not in page
    assert 'data-alive-next="create_short publish"' not in page
    assert 'data-alive-next="create_short"' in page


def test_home_legacy_nav_is_hidden_when_global_gamebar_owns_navigation():
    home = _source("web/home_v154_component/index.html")
    assert "GSF_V428_GLOBAL_GAMEBAR_OWNS_NAV" in home
    assert "html.gsf-v343-parent-ready #home154 .bottomNav{display:none!important}" in home


def test_home_uploader_returns_to_idle_after_handoff_without_forgetting_source():
    embed = _source("web/home_v154_embed.py")
    # Source readiness must remain true for AI/Editor/Crea Short; only the uploader
    # presentation is reset after the direct-upload handoff.
    assert "loaded=bool(loaded)" in embed
    assert "GSF_V428_UPLOADER_HANDOFF_RESET" in embed
    assert "data-gsf-uploader-idle" in embed
    assert "replaceConfirm" in embed
    assert "loadedCheck" in embed
    assert "CARICA<br>IL TUO GAMEPLAY" in embed
    assert "gsf-upload" in embed
    assert "state==='done'" in embed


def test_global_notifications_are_one_readable_pen_surface_outside_header():
    server = _source("web/direct_upload_server.py")
    client = _function_source("web/direct_upload_server.py", "_push_client_bytes")
    assert "GSF_V428_PEN_NOTIFICATIONS" in client
    assert "const inline=false" in client
    assert "Caveat" in client
    assert "kind==='error'?9000:6500" in client
    # The old placement literally squeezed notifications between brand and profile.
    assert "brand.getBoundingClientRect().right" not in client
    assert "account.getBoundingClientRect().left" not in client
    assert "def _push_client_bytes" in server


def test_instagram_prefers_direct_instagram_oauth_when_direct_credentials_exist():
    text = _source("web/direct_upload_server.py")
    tree = ast.parse(text)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_instagram_oauth_start")

    with tempfile.TemporaryDirectory() as folder:
        redirects: list[str] = []
        writes: list[tuple[Path, dict]] = []
        ns = {
            "_safe_id": lambda value: str(value) if value else "",
            "_html": lambda *args, **kwargs: None,
            "_social_page": lambda sid, message="": message,
            "_redirect": lambda handler, url: redirects.append(url),
            "_write_json_atomic": lambda path, payload: writes.append((Path(path), dict(payload))),
            "PUBLIC_APP_URL": "https://gsf.test",
            "INSTAGRAM_APP_ID": "ig-direct",
            "INSTAGRAM_APP_SECRET": "ig-secret",
            "INSTAGRAM_REDIRECT_URI": "https://gsf.test/auth/instagram/callback",
            "INSTAGRAM_SCOPES": "instagram_business_basic,instagram_business_content_publish",
            "META_APP_ID": "meta-app",
            "META_APP_SECRET": "meta-secret",
            "META_SCOPES": "pages_show_list,instagram_basic,instagram_content_publish",
            "ROOT": Path(folder),
            "secrets": secrets,
            "time": time,
            "urllib": __import__("urllib"),
        }
        exec(compile(ast.Module(body=[node], type_ignores=[]), "<instagram-start>", "exec"), ns)
        ns["_instagram_oauth_start"](object(), "browserA")

        assert redirects, "Instagram OAuth must redirect to a provider"
        url = urllib.parse.urlsplit(redirects[0])
        query = urllib.parse.parse_qs(url.query)
        assert url.netloc == "www.instagram.com"
        assert url.path == "/oauth/authorize"
        assert query["client_id"] == ["ig-direct"]
        assert query["redirect_uri"] == ["https://gsf.test/auth/instagram/callback"]
        assert writes and writes[0][1]["mode"] == "instagram_login"
