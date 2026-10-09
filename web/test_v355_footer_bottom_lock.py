#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FIX = HERE / 'fix_v355_footer_bottom_lock.py'
APP_NAME = 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
BASE = """# runtime\n# GSF_V354_FOOTER_TRUE_CENTER_SAFE_SIDES\n"""

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    app = root / APP_NAME
    app.write_text(BASE, encoding='utf-8')
    subprocess.run([sys.executable, str(FIX), str(root)], check=True)
    out = app.read_text(encoding='utf-8')
    for token in [
        'GSF_V355_FOOTER_BOTTOM_LOCK',
        'position:fixed!important',
        'left:0!important',
        'right:0!important',
        'bottom:0!important',
        'top:auto!important',
        'width:100%!important',
        'z-index:9997!important',
        "footer.dataset.gsfV355 = '1'",
    ]:
        assert token in out, f'missing V355 footer token: {token}'
    once = out
    subprocess.run([sys.executable, str(FIX), str(root)], check=True)
    assert app.read_text(encoding='utf-8') == once, 'V355 must be restart-safe'

print('V355 FOOTER BOTTOM LOCK: PASS', flush=True)
