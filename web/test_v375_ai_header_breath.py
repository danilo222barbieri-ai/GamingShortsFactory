#!/usr/bin/env python3
from pathlib import Path
import sys

MARK = 'V375_AI_HEADER_BREATH'
TARGET = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app/web/ai_v221_component/index.html')

if not TARGET.is_file():
    raise SystemExit(f'V375 AI target missing: {TARGET}')

text = TARGET.read_text(encoding='utf-8')

checks = {
    'V308 mobile AI flow preserved': 'V308_MOBILE_AI_FLOW' in text,
    'V375 marker installed': MARK in text,
    'mobile-only breakpoint installed': '@media(max-width:920px)' in text,
    '30px header breathing room installed': 'body{padding-top:30px!important}' in text,
    'AI engine title preserved': 'Scegli il tuo Motore IA' in text,
    'Automatico engine preserved': 'Automatico' in text,
    'Momento migliore engine preserved': 'Momento migliore' in text,
    'Più azione engine preserved': 'Più azione' in text,
    'Reazioni engine preserved': 'Reazioni' in text,
}

failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise AssertionError('V375 AI header breath contract failed: ' + '; '.join(failed))

print('V375 AI HEADER BREATH CONTRACT: PASS', flush=True)
