#!/usr/bin/env python3
from pathlib import Path
import ast
import subprocess
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
APP = ROOT / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
START = ROOT / 'web/start_web.sh'
FIX = ROOT / 'web/fix_v348_transparent_logo_footer.py'

if not APP.is_file() or not START.is_file():
    raise SystemExit('V348 contract inputs missing')

source = APP.read_text(encoding='utf-8')
start = START.read_text(encoding='utf-8')
tree = ast.parse(source)


def call_name(node):
    fn = node.func
    if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name):
        return f'{fn.value.id}.{fn.attr}'
    return ''

bridges = []
for node in ast.walk(tree):
    if not isinstance(node, ast.Call) or not node.args:
        continue
    if call_name(node) != '_gsf_components_v343.html':
        continue
    arg = node.args[0]
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and 'GSF_GLOBAL_SHELL_V343' in arg.value:
        bridges.append(arg.value)

bridge = bridges[0] if len(bridges) == 1 else ''
marker = 'GSF_V348_TRANSPARENT_LOGO_FOOTER'

fix_anchor = 'python /app/web/fix_v348_transparent_logo_footer.py /app'
test_anchor = 'python /app/web/test_v348_transparent_logo_footer.py /app'
v343_anchor = 'python /app/web/fix_v343_single_global_shell.py /app'
v336_anchor = 'python /app/web/fix_v336_executable_shell_bridge.py /app'

checks = {
    'exactly one V343 executable bridge remains': len(bridges) == 1,
    'V348 marker installed exactly once': bridge.count(marker) == 1,
    'user logo is installed as transparent vector data': (
        'gsf-global-logo-v348' in bridge
        and 'data:image/svg+xml;base64,' in bridge
        and 'background:transparent!important' in bridge
        and 'box-shadow:none!important' in bridge
    ),
    'old brand tile is replaced without touching profile photo': (
        "img[src^=\"data:image/svg+xml\"]" in bridge
        and "oldLogo.src=LOGO" in bridge
    ),
    'global footer is force-visible and fixed': (
        '#gsf-global-footer{' in bridge
        and 'display:flex!important' in bridge
        and 'visibility:visible!important' in bridge
        and 'opacity:1!important' in bridge
        and 'position:fixed!important' in bridge
        and 'bottom:0!important' in bridge
    ),
    'Game Bar reserves the footer area': (
        '#gsf-global-gamebar{' in bridge
        and '--gsf-v348-footer-space' in bridge
        and 'env(safe-area-inset-bottom' in bridge
    ),
    'footer polish is reapplied after Streamlit mutations': 'MutationObserver' in bridge,
    'V348 runs after V343 and before V336': (
        0 <= start.find(v343_anchor) < start.find(fix_anchor) < start.find(v336_anchor)
    ),
    'V348 contract runs immediately after its fix': (
        start.find(test_anchor) > start.find(fix_anchor) >= 0
        and start.find(test_anchor) < start.find(v336_anchor)
    ),
}

# The runtime patch must be restart-safe: applying it again cannot alter the source.
idempotent = False
if FIX.is_file() and bridge:
    before = source
    result = subprocess.run(
        [sys.executable, str(FIX), str(ROOT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=15,
    )
    after = APP.read_text(encoding='utf-8')
    idempotent = result.returncode == 0 and before == after
checks['V348 patch is restart-safe and idempotent'] = idempotent

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(('PASS: ' if ok else 'FAIL: ') + name)
if failed:
    raise SystemExit('V348 transparent logo/footer contract failed: ' + ', '.join(failed))
print('V348 TRANSPARENT LOGO + FOOTER CONTRACT: PASS', flush=True)
