#!/usr/bin/env python3
"""V415 Creator Hub redesign contract.

Owner-approved layout: header (photo, name, plan, settings) -> social status row
(YouTube, TikTok, Instagram, Facebook, Twitch with green/grey tick) -> counters
(Bozze, Shorts, Pubblicati) -> Bozze and Shorts with Riprendi/Rinomina/Elimina ->
Live e VOD (empty for now) -> Impostazioni (photo, name, social connect/disconnect,
plan, notifications, language, logout). Short actions must reach the companion
server: nginx routes /shorts/* to Streamlit, so the Hub uses /creator-hub/short/*.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = (ROOT / "web/creator_hub_v156_component/index.html").read_text(encoding="utf-8")
SERVER = (ROOT / "web/direct_upload_server.py").read_text(encoding="utf-8")
NGINX = (ROOT / "web/nginx.conf.template").read_text(encoding="utf-8")


def _script() -> str:
    m = re.search(r'<script id="v415CreatorHubRuntime">(.*?)</script>', HUB, re.S)
    assert m, "V415 runtime script missing"
    return m.group(1)


def test_single_runtime_replaces_stacked_layers():
    assert "V415_CREATOR_HUB_REDESIGN" in HUB
    assert HUB.count("<script") == 1, "the Hub must run exactly one script"
    assert "MutationObserver" not in HUB, "no observers: they grew per navigation cycle"
    for legacy in ("v403CreatorHubSimplifiedRuntime\">", "id=\"hubDashboardAd\"", "projectHubCards"):
        assert legacy not in HUB, legacy


def test_dashboard_order_and_social_ticks():
    order = [HUB.index(m) for m in ('id="profileName"', 'id="socialRow"', 'id="countDrafts"',
                                    'id="countPublished"', 'data-open="live"', 'id="draftStrip"', 'id="shortStrip"')]
    assert order == sorted(order), "dashboard sections out of the approved order"
    js = _script()
    for key in ("youtube", "tiktok", "instagram", "facebook", "twitch"):
        assert f'key:"{key}"' in js, key
    assert ".socialDot.connected .tick{background:var(--ok)}" in HUB
    assert "--ok:#22C55E" in HUB and "--off:#B7C4D0" in HUB


def test_card_actions_and_confirmed_delete():
    js = _script()
    for token in ('data-m="resume"', 'data-m="rename"', 'data-m="delete"', 'data-m="download"',
                  "Riprendi", "Rinomina", "Elimina", "Eliminare “",
                  '"/creator-hub/draft/rename"', '"/creator-hub/short/rename"', '"/creator-hub/short/delete"',
                  '"/drafts/delete?id="', '"/creator-hub/short/file?id="', '"X-GSF-CSRF"'):
        assert token in js, token
    # delete happens only from the confirmation sheet
    assert js.index("function openDelete") < js.index('postJson("/creator-hub/short/delete"')
    assert "/shorts/delete" not in js and "/shorts/file" not in js


def test_settings_page_contents():
    view = HUB[HUB.index('data-view="settings"'):HUB.index('id="sheet"')]
    for token in ('id="changePhotoBtn"', 'id="profileNameInput"', 'id="socialSettings"',
                  'id="profileOverviewPlan"', 'id="notifyBtn"', "Lingua", 'id="accountBtn"'):
        assert token in view, token
    assert HUB.count("Abbonamento") == 1, "the plan appears once (Impostazioni), no duplicate"
    assert re.search(r'\["profile","social","subscription","account"\]\.includes\(v\)\)v="settings"', _script())


def test_sources_replace_placeholder_with_real_library():
    view = HUB[HUB.index('data-view="live"'):HUB.index('data-view="settings"')]
    assert 'id="sourceLibrary"' in view
    for label in ('Upload','Twitch','YouTube','Live','VOD','Clip','Importati'):
        assert label in view
    assert '/creator-hub/sources' in _script()
    assert '/creator-hub/sources/activate' in _script()


def test_desktop_two_columns_and_brand_tokens():
    assert re.search(r"@media\(min-width:900px\)\{[^@]*\.dashGrid\{display:grid;grid-template-columns:minmax\(300px,360px\) minmax\(0,1fr\)", HUB)
    tokens = (ROOT / "design/brand/gsf-brand-tokens.css").read_text(encoding="utf-8")
    for name in ("--gsf-primary", "--gsf-ink", "--gsf-muted", "--gsf-line", "--gsf-font"):
        value = re.search(re.escape(name) + r":\s*([^;]+);", tokens).group(1).strip()
        assert f"{name}:{value}" in HUB.replace(": ", ":"), name


def test_short_routes_reach_the_companion_server():
    loc = NGINX[NGINX.index("location /creator-hub/ {"):]
    loc = loc[:loc.index("\n    }")]
    assert "proxy_pass http://127.0.0.1:8502;" in loc
    assert 'if clean in ("/shorts/file","/creator-hub/short/file"):' in SERVER
    block = SERVER[SERVER.index('if path in ("/creator-hub/short/rename","/creator-hub/short/delete"):'):]
    block = block[:block.index('if path=="/shorts/delete":')]
    assert "_security_csrf_valid(self,sid)" in block and "403" in block
    assert "_short_rename(sid,short_id" in block and "_short_delete(sid,short_id)" in block
    assert "def _short_rename(sid,short_id,title):" in SERVER


def test_short_rename_updates_only_the_title():
    src = SERVER[SERVER.index("def _short_rename(sid,short_id,title):"):]
    src = src[:src.index("\ndef ", 10)]
    saved = {}
    ns = {
        "_safe_id": lambda v: re.sub(r"[^A-Za-z0-9_-]", "", str(v or ""))[:80],
        "_v304_clean_title": lambda v, fb: re.sub(r"\s+", " ", str(v or "").strip())[:180] or fb,
        "_short_list": lambda sid: [{"id": "a", "title": "Old", "final_bytes": 9}, {"id": "b", "title": "B"}],
        "_short_index_save": lambda sid, rows: saved.setdefault("rows", rows),
    }
    exec(src, ns)  # noqa: S102 - pure helper under test
    row = ns["_short_rename"]("sid", "a", "  Nuovo   titolo ")
    assert row["title"] == "Nuovo titolo" and row["final_bytes"] == 9
    assert [r["title"] for r in saved["rows"]] == ["Nuovo titolo", "B"]
    assert ns["_short_rename"]("sid", "zzz", "x") == {}


def test_runtime_parses():
    node = shutil.which("node")
    if not node:
        return
    tmp = ROOT / "tools" / ".hub_v415_check.js"
    tmp.write_text(_script(), encoding="utf-8")
    try:
        result = subprocess.run([node, "--check", str(tmp)], capture_output=True, text=True)
    finally:
        tmp.unlink(missing_ok=True)
    assert result.returncode == 0, result.stderr[-400:]


if __name__ == "__main__":
    import sys
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except Exception as exc:  # pragma: no cover - CLI runner
                failed += 1
                print("FAIL", name, repr(exc)[:300])
    print("V415 Creator Hub redesign contract:", "FAIL" if failed else "PASS")
    sys.exit(1 if failed else 0)
