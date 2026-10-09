#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
APP = ROOT / 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
MARK = 'GSF_V349_FOOTER_CONTRACT'
V348_MARK = 'GSF_V348_TRANSPARENT_LOGO_FOOTER'

FOOTER_GEOMETRY_RE = re.compile(
    r'''#gsf-global-footer\{\s*'''
    r'''display:flex!important;\s*'''
    r'''visibility:visible!important;\s*'''
    r'''opacity:1!important;\s*'''
    r'''pointer-events:auto!important;\s*'''
    r'''position:fixed!important;\s*'''
    r'''left:0!important;\s*'''
    r'''right:0!important;\s*'''
    r'''bottom:max\(4px,env\(safe-area-inset-bottom\)\)!important;\s*'''
    r'''min-height:30px!important;\s*'''
    r'''height:30px!important;\s*'''
    r'''max-height:30px!important;\s*'''
    r'''z-index:2147483600!important;\s*'''
    r'''transform:none!important;\s*'''
    r'''\}''',
    re.MULTILINE,
)

GAMEBAR_OFFSET_RE = re.compile(
    r'''#gsf-global-gamebar\{\s*'''
    r'''bottom:calc\(34px \+ max\(8px,env\(safe-area-inset-bottom\)\)\)!important;\s*'''
    r'''\}''',
    re.MULTILINE,
)

VISIBLE_ONLY = '''#gsf-global-footer{
          display:flex!important;
          visibility:visible!important;
          opacity:1!important;
          pointer-events:auto!important;
        }'''


def main():
    if not APP.is_file():
        raise SystemExit('V349 runtime app missing')

    text = APP.read_text(encoding='utf-8')
    if MARK in text:
        print('V349 footer contract already applied', flush=True)
        return
    if V348_MARK not in text:
        raise SystemExit('V349 requires V348 footer hotfix first')

    text, footer_count = FOOTER_GEOMETRY_RE.subn(VISIBLE_ONLY, text, count=1)
    text, gamebar_count = GAMEBAR_OFFSET_RE.subn('', text, count=1)
    if footer_count != 1:
        raise SystemExit(f'V349 expected one V348 footer geometry block, found {footer_count}')
    if gamebar_count != 1:
        raise SystemExit(f'V349 expected one V348 Game Bar offset block, found {gamebar_count}')

    text += '\n# GSF_V349_FOOTER_CONTRACT — V343 owns geometry; V348 only keeps footer visible.\n'
    APP.write_text(text, encoding='utf-8')
    print('V349 footer contract applied', flush=True)


if __name__ == '__main__':
    main()
