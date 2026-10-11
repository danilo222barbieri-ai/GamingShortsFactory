#!/usr/bin/env python3
from pathlib import Path
import ast
import re
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
APP = ROOT / 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
MARK = 'V372_PRIMARY_ROUTES_RUNTIME'


def _call_name(node):
    fn = node.func
    if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name):
        return f'{fn.value.id}.{fn.attr}'
    return ''


def _bridge(text):
    tree = ast.parse(text)
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        arg = node.args[0]
        if not isinstance(arg, ast.Constant) or not isinstance(arg.value, str):
            continue
        if '__GSF_GLOBAL_SHELL_V343' in arg.value:
            found.append((_call_name(node), arg.value))
    assert len(found) == 1, f'V372 expected one executable V343 bridge, found {len(found)}'
    renderer, bridge = found[0]
    assert renderer == '_gsf_components_v343.html', f'V372 V343 renderer changed: {renderer}'
    return bridge


def _snippet(bridge, token, radius=900):
    idx = bridge.find(token)
    print(f'V372 DIAG token={token!r} index={idx}', flush=True)
    if idx >= 0:
        lo = max(0, idx - radius)
        hi = min(len(bridge), idx + len(token) + radius)
        print('--- V372 DIAG SNIPPET ---', flush=True)
        print(bridge[lo:hi], flush=True)
        print('--- END V372 DIAG SNIPPET ---', flush=True)
    return idx


def main():
    print('V372 RED final-runtime gate active', flush=True)
    if not APP.is_file():
        raise SystemExit(f'V372 final runtime missing: {APP}')
    text = APP.read_text(encoding='utf-8')
    bridge = _bridge(text)
    print(f'V372 DIAG executable bridge bytes={len(bridge)}', flush=True)

    for token in (
        "GSF_SHELL_NAV",
        "target==='ai'",
        "target==='editor'",
        "target==='short'",
        "gsf-ai-overlay-v221",
        "gsf-editor-overlay-v220",
        "gsf-short-overlay-v343",
    ):
        _snippet(bridge, token)

    # RED gate: V372 must own all three primary routes in the final executable
    # bridge. This marker is intentionally absent on the current broken runtime.
    assert MARK in bridge, 'V372 RED: final executable bridge has no V372 primary-route owner yet'

    # GREEN contract after the minimal repair.
    required = (
        "if(target==='ai')",
        "if(target==='editor')",
        "if(target==='short')",
        "'/editor-live/'",
        "gsf-ai-overlay-v221",
        "gsf-editor-overlay-v220",
        "gsf-short-overlay-v343",
    )
    missing = [token for token in required if token not in bridge]
    assert not missing, 'V372 final route contract missing: ' + ', '.join(missing)

    # One and only one message listener is allowed to claim the canonical route
    # owner marker. Hub behavior itself is deliberately outside this patch.
    assert bridge.count(MARK) == 1, f'V372 owner marker count={bridge.count(MARK)}'
    assert "target==='hub'" in bridge, 'V372 must preserve existing Hub route branch'
    print('V372 PRIMARY ROUTES FINAL RUNTIME CONTRACT: PASS', flush=True)


if __name__ == '__main__':
    main()
