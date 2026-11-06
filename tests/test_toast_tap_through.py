"""Passive notifications must not swallow taps on the header or app controls."""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _client_css():
    text = (ROOT / "web/direct_upload_server.py").read_text(encoding="utf-8")
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == "_push_client_bytes")
    return ast.get_source_segment(text, node)


def test_passive_toast_body_lets_taps_through():
    css = _client_css()
    body = re.search(r"\.gsf-site-toast\{[^}]*\}", css).group(0)
    assert "pointer-events:none" in body


def test_only_real_controls_take_taps():
    css = _client_css()
    assert ".gsf-site-toast[data-kind=confirm],.gsf-site-toast-close,.gsf-site-toast-action{pointer-events:auto}" in css
    assert ".gsf-site-toast.gsf-hide button{pointer-events:none}" in css
