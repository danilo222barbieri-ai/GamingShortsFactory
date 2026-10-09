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
        'GSF_V351_FOOTER_BRAND_GLASS',
        'gsf-v351-footer-shell',
        'gsf-v351-socials',
        'gsf-v351-legal',
        'data-social="youtube"',
        'data-social="tiktok"',
        'data-social="instagram"',
        'data-social="facebook"',
        'data-social="twitch"',
        "['Termini','/terms']",
        "['Privacy','/privacy']",
        "['Contatti','/contact']",
        'grid-template-columns:minmax(0,1fr) auto minmax(0,1fr)',
        'backdrop-filter:blur(18px)',
        "f.replaceChildren(spacer, socials, legal);",
    ]
    for token in required:
        assert token in out, f'missing V351 footer token: {token}'

    assert 'Segnala bug' not in out, 'V351 footer must not render Segnala bug'
    assert 'clickable.slice' not in out, 'V351 must not infer social controls from old footer nodes'

    once = out
    subprocess.run([sys.executable, str(FIX), str(root)], check=True)
    assert app.read_text(encoding='utf-8') == once, 'V351 must be restart-safe'

print('V351 FOOTER BRAND GLASS: PASS', flush=True)
