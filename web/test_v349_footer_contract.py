#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FIX = HERE / 'fix_v349_footer_contract.py'
APP_NAME = 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'

LEGACY = r'''# generated runtime
# GSF_V348_TRANSPARENT_LOGO_FOOTER
BROKEN_CSS = r"""
#gsf-global-footer{
  display:flex!important;
  visibility:visible!important;
  opacity:1!important;
  pointer-events:auto!important;
  position:fixed!important;
  left:0!important;
  right:0!important;
  bottom:max(4px,env(safe-area-inset-bottom))!important;
  min-height:30px!important;
  height:30px!important;
  max-height:30px!important;
  z-index:2147483600!important;
  transform:none!important;
}
#gsf-global-gamebar{
  bottom:calc(34px + max(8px,env(safe-area-inset-bottom)))!important;
}
"""
'''


def run_fix(root: Path):
    assert FIX.is_file(), 'V349 production fix is missing'
    return subprocess.run(
        [sys.executable, str(FIX), str(root)],
        check=True,
        text=True,
        capture_output=True,
    )


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        app = root / APP_NAME
        app.write_text(LEGACY, encoding='utf-8')

        run_fix(root)
        out = app.read_text(encoding='utf-8')

        assert 'GSF_V349_FOOTER_CONTRACT' in out, 'V349 marker missing'
        assert '#gsf-global-footer{' in out, 'footer visibility rule disappeared'
        for token in (
            'bottom:max(4px,env(safe-area-inset-bottom))!important;',
            'min-height:30px!important;',
            'height:30px!important;',
            'max-height:30px!important;',
            'z-index:2147483600!important;',
            '#gsf-global-gamebar{',
            'bottom:calc(34px + max(8px,env(safe-area-inset-bottom)))!important;',
        ):
            assert token not in out, f'legacy V348 geometry still active: {token}'

        for token in (
            'display:flex!important;',
            'visibility:visible!important;',
            'opacity:1!important;',
            'pointer-events:auto!important;',
        ):
            assert token in out, f'footer visibility guard lost: {token}'

        once = out
        run_fix(root)
        twice = app.read_text(encoding='utf-8')
        assert twice == once, 'V349 is not restart-safe/idempotent'

    print('V349 FOOTER CONTRACT: PASS', flush=True)


if __name__ == '__main__':
    main()
