#!/usr/bin/env python3
from pathlib import Path
import ast
import re
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
FINAL_APP = ROOT / 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
HOME = ROOT / 'web' / 'home_v154_component' / 'index.html'
MARK = 'V372_PRIMARY_ROUTES_HOME_HANDOFF'


def _call_name(node):
    fn = node.func
    if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name):
        return f'{fn.value.id}.{fn.attr}'
    return ''


def _executable_bridge(text):
    tree = ast.parse(text)
    candidates = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        arg = node.args[0]
        if not isinstance(arg, ast.Constant) or not isinstance(arg.value, str):
            continue
        bridge = arg.value
        if '__GSF_GLOBAL_SHELL_V343' not in bridge:
            continue
        heights = [
            kw.value.value for kw in node.keywords
            if kw.arg == 'height' and isinstance(kw.value, ast.Constant)
        ]
        candidates.append((_call_name(node), heights, bridge))

    executable = [
        row for row in candidates
        if row[0] == '_gsf_components_v343.html'
        and row[1] == [0]
        and "target==='editor'" in row[2]
        and "target==='short'" in row[2]
        and 'gsf-short-overlay-v343' in row[2]
    ]
    print(
        'V372 bridge inventory:',
        [(renderer, heights, len(bridge)) for renderer, heights, bridge in candidates],
        flush=True,
    )
    assert len(executable) == 1, (
        f'V372 expected one executable canonical V343 bridge, found {len(executable)} '
        f'from {len(candidates)} V343 string candidates'
    )
    return executable[0][2]


def _home_nav_body(home):
    match = re.search(
        r'function shellNav\(target,data=\{\}\)\{(?P<body>.*?)\n\s*\}',
        home,
        re.DOTALL,
    )
    assert match, 'V372 Home shellNav missing'
    return match.group('body')


def main():
    for path in (FINAL_APP, HOME):
        if not path.is_file():
            raise SystemExit(f'V372 runtime file missing: {path}')

    final_text = FINAL_APP.read_text(encoding='utf-8')
    home = HOME.read_text(encoding='utf-8')
    bridge = _executable_bridge(final_text)
    nav = _home_nav_body(home)

    # Home may emit intent, but must not own/guess parent surfaces anymore.
    assert MARK in home, 'V372 Home handoff marker missing'
    canonical = 'window.parent.postMessage({type:"GSF_SHELL_NAV",target,...data},location.origin);'
    assert canonical in nav, 'V372 Home does not delegate primary navigation to V343'
    for forbidden in ('getElementById(', 'querySelector(', 'parentClick(', 'handled='):
        assert forbidden not in nav, f'V372 Home shellNav still owns UI via {forbidden}'

    # Existing Home controls still emit all three requested intents.
    for target in ('ai', 'editor', 'short'):
        assert f'shellNav("{target}")' in home or f"shellNav('{target}')" in home, (
            f'V372 Home no longer emits {target} intent'
        )

    # The final executable V293 runtime must have real destinations for each intent.
    required = (
        "target==='ai'",
        "target==='editor'",
        "target==='short'",
        '/editor-live/',
        'gsf-ai-overlay-v221',
        'gsf-editor-overlay-v220',
        'gsf-short-overlay-v343',
    )
    missing = [token for token in required if token not in bridge]
    assert not missing, 'V372 final route contract missing: ' + ', '.join(missing)

    # Hub is deliberately outside the patch, but its canonical V343 route must survive.
    assert "target==='hub'" in bridge, 'V372 regression: V343 Hub route missing'

    print('V372 PRIMARY ROUTES FINAL RUNTIME CONTRACT: PASS', flush=True)


if __name__ == '__main__':
    main()
