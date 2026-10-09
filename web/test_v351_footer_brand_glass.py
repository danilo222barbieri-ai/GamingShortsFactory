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
        'GSF_V353_FOOTER_BALANCE_HIRES',
        'GSF_V354_FOOTER_TRUE_CENTER_SAFE_SIDES',
        'GSF_V355_FOOTER_BOTTOM_LOCK',
        'GSF_V356_FOOTER_SIDE_INSET',
        'GSF_V358_FOOTER_VERSION_LABEL',
        'gsf-v351-brand',
        'GSF - V358',
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
        'position:fixed!important',
        'left:0!important',
        'right:0!important',
        'bottom:0!important',
        'top:auto!important',
        'width:100%!important',
        'z-index:9997!important',
        'left:50%!important',
        'transform:translate(-50%,-50%)!important',
        'left:max(24px,env(safe-area-inset-left))!important',
        'right:max(24px,env(safe-area-inset-right))!important',
        'left:max(20px,env(safe-area-inset-left))!important',
        'right:max(20px,env(safe-area-inset-right))!important',
        'overflow:visible!important',
        'shape-rendering:geometricPrecision',
        "f.replaceChildren(brand, socials, legal);",
        "f.dataset.gsfV358 = '1';",
    ]
    for token in required:
        assert token in out, f'missing V358 footer token: {token}'

    assert 'left:max(12px,env(safe-area-inset-left))!important' not in out, 'mobile brand must stay inset from the edge'
    assert 'right:max(12px,env(safe-area-inset-right))!important' not in out, 'mobile legal links must stay inset from the edge'
    assert 'position:relative!important' not in out, 'footer container must stay fixed at bottom'
    assert 'grid-template-columns:minmax(0,1fr) auto minmax(0,1fr)' not in out, 'footer centering must not depend on side-column widths'
    assert out.count('<svg viewBox=') >= 5, 'all five social marks must remain vector SVGs'
    assert '>♪</span>' not in out
    assert '>f</span>' not in out
    assert '>◧</span>' not in out
    assert 'Segnala bug' not in out
    assert 'clickable.slice' not in out

    once = out
    subprocess.run([sys.executable, str(FIX), str(root)], check=True)
    assert app.read_text(encoding='utf-8') == once, 'footer patch must be restart-safe'

print('V358 FOOTER VERSION LABEL: PASS', flush=True)
