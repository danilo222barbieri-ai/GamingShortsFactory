#!/usr/bin/env python3
from pathlib import Path
import sys

SHARE = Path('/app/web/share_v156_component/index.html')
mode = (sys.argv[1] if len(sys.argv) > 1 else '').strip().lower()
if mode not in {'pre','post'}:
    raise SystemExit('usage: fix_v297_share_anchor_compat.py pre|post')

text = SHARE.read_text(encoding='utf-8')
if mode == 'pre':
    old = '<main id="share" class="gsfFinalSurface">'
    new = '<main id="share">'
    if old in text:
        text = text.replace(old, new, 1)
    elif '<main id="share">' not in text:
        raise RuntimeError('V297 Share pre anchor missing')
else:
    old = '<main id="share" data-v297-layout="share">'
    new = '<main id="share" class="gsfFinalSurface" data-v297-layout="share">'
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise RuntimeError('V297 Share post anchor missing')

SHARE.write_text(text, encoding='utf-8')
print(f'V297 Share anchor compatibility {mode}: PASS', flush=True)
