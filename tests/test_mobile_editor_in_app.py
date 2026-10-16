"""The app itself must open the canonical mobile Game Editor 2026, not only its standalone page.

Regression for two defects that kept phones on the legacy editor:
- the V220 overlay markup was indented 4 spaces after a </style> inside st.markdown, so Markdown
  rendered it as a code block: the overlay element never existed and the 2026 bridge never ran;
- so the V343 shell fallback created its own overlay and loaded /editor-live/ (legacy editor).
"""
from __future__ import annotations

import re
from pathlib import Path

APP = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")


def _markdown_blocks():
    # Bodies of st.markdown("""...""", unsafe_allow_html=True) calls.
    return re.findall(r'st\.markdown\(\s*(?:r|f|rf|fr)?"""(.*?)"""\s*,\s*unsafe_allow_html=True', APP, re.S)


def test_editor_overlay_markup_is_html_not_a_code_block():
    # The overlay is a persistent top-level surface installed into Streamlit's index.html
    # (web/install_adsense_bridge.py reads every _GSF_SURFACE_* constant), so it never
    # passes through st.markdown and can never render as a Markdown code block.
    surfaces = re.findall(r'^_GSF_SURFACE_(\w+) = r"""(.*?)"""', APP, re.S | re.M)
    editor = [body for name, body in surfaces if 'id="gsf-editor-overlay-v220"' in body]
    assert editor, "V220 editor overlay must be a persistent _GSF_SURFACE_* surface"
    assert editor[0].lstrip().startswith('<div id="gsf-editor-overlay-v220"')
    assert not [b for b in _markdown_blocks() if 'id="gsf-editor-overlay-v220"' in b], "overlay must not also be mounted through st.markdown"


def test_overlay_exists_before_the_bridge_reads_it():
    # The 2026 bridge starts with getElementById('gsf-editor-overlay-v220') and returns when it is missing.
    overlay = APP.index('<div id="gsf-editor-overlay-v220" aria-hidden="true">')
    bridge = APP.index("/* GSF_MOBILE_EDITOR_2026_BRIDGE */")
    assert overlay < bridge
    assert "const o=document.getElementById('gsf-editor-overlay-v220'); if(!o)return;" in APP[overlay:bridge]


def test_bridge_still_selects_the_same_sources():
    assert "const MOBILE_EDITOR_SRC='/game-editor-mobile/';" in APP
    assert "const DESKTOP_EDITOR_SRC='/editor-live/';" in APP
    assert "window.matchMedia('(max-width: 760px)')" in APP
