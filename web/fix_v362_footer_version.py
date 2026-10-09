#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
APP = ROOT / 'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
MARK = 'GSF_V362_VISIBLE_VERSION'

if not APP.is_file():
    raise SystemExit('V362 footer runtime app missing')
text = APP.read_text(encoding='utf-8')
if MARK in text:
    print('V362 footer version already applied', flush=True)
    raise SystemExit(0)
if 'GSF_V351_FOOTER_BRAND_GLASS' not in text:
    raise SystemExit('V362 footer version requires V351 footer first')
if 'GSF - V361' not in text:
    raise SystemExit('V362 footer expected V361 visible label')
text = text.replace("brand.innerHTML = '<span>GSF - V361</span>';", "brand.innerHTML = '<span>GSF - V362</span>';", 1)
text += "\n# GSF_V362_VISIBLE_VERSION\n"
APP.write_text(text, encoding='utf-8')
print('V362 footer visible version applied', flush=True)
