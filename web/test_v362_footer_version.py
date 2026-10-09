#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FIX351 = HERE / 'fix_v351_footer_brand_glass.py'
FIX362 = HERE / 'fix_v362_footer_version.py'
APP_NAME = 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
BASE = """# runtime\n# GSF_V349_FOOTER_CONTRACT\n# GSF_V350_FOOTER_MOBILE_CENTER\n"""

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    app = root / APP_NAME
    app.write_text(BASE, encoding='utf-8')
    subprocess.run([sys.executable, str(FIX351), str(root)], check=True)
    subprocess.run([sys.executable, str(FIX362), str(root)], check=True)
    out = app.read_text(encoding='utf-8')
    assert 'GSF_V362_VISIBLE_VERSION' in out
    assert 'GSF - V362' in out
    assert 'GSF - V361</span>' not in out
    assert 'gsf-v351-socials' in out
    assert 'gsf-v351-legal' in out
    once = out
    subprocess.run([sys.executable, str(FIX362), str(root)], check=True)
    assert app.read_text(encoding='utf-8') == once

print('V362 FOOTER VERSION LABEL: PASS', flush=True)
