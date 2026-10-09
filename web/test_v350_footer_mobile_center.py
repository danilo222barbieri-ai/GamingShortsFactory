#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FIX = HERE / 'fix_v350_footer_mobile_center.py'
APP_NAME = 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'

BASE = """# runtime\n# GSF_V349_FOOTER_CONTRACT\n"""

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    app = root / APP_NAME
    app.write_text(BASE, encoding='utf-8')
    subprocess.run([sys.executable, str(FIX), str(root)], check=True)
    out = app.read_text(encoding='utf-8')

    required = [
        'GSF_V350_FOOTER_MOBILE_CENTER',
        'gsf-v350-socials',
        'gsf-v350-legal',
        "['Termini','/terms']",
        "['Privacy','/privacy']",
        "['Contatti','/contact']",
        'segnala|bug|privacy|term|contatt|contact',
        'left:50%!important;',
        'transform:translate(-50%,-50%)!important;'
    ]
    for token in required:
        assert token in out, f'missing V350 token: {token}'

    once = out
    subprocess.run([sys.executable, str(FIX), str(root)], check=True)
    assert app.read_text(encoding='utf-8') == once, 'V350 must be restart-safe'

print('V350 FOOTER MOBILE CENTER: PASS', flush=True)
