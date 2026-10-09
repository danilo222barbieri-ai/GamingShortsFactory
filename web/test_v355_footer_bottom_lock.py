#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FIX = HERE / 'fix_v351_footer_brand_glass.py'
APP_NAME = 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
BASE = """# runtime\n# GSF_V349_FOOTER_CONTRACT\n# GSF_V350_FOOTER_MOBILE_CENTER\n"""

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    app = root / APP_NAME
    app.write_text(BASE, encoding='utf-8')
    subprocess.run([sys.executable, str(FIX), str(root)], check=True)
    out = app.read_text(encoding='utf-8')
    required = [
        'GSF_V355_FOOTER_BOTTOM_LOCK',
        'position:fixed!important',
        'left:0!important',
        'right:0!important',
        'bottom:0!important',
        'z-index:9997!important',
        'left:50%!important',
        'transform:translate(-50%,-50%)!important',
        'left:max(14px,env(safe-area-inset-left))!important',
        'right:max(14px,env(safe-area-inset-right))!important',
    ]
    for token in required:
        assert token in out, f'missing V355 footer token: {token}'
    assert 'position:relative!important' not in out, 'footer container must not become document-flow relative'

print('V355 FOOTER BOTTOM LOCK: PASS', flush=True)
