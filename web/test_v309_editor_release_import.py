#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
EMBED = ROOT / 'web' / 'editor_2027_embed.py'
text = EMBED.read_text(encoding='utf-8')

checks = {
    'package release import retained': 'from web.ui_release import GSF_UI_RELEASE' in text,
    'script-context fallback exists': 'from ui_release import GSF_UI_RELEASE' in text,
    'fallback is guarded': 'except ModuleNotFoundError' in text,
}
failed = []
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + name)
    if not ok:
        failed.append(name)
if failed:
    raise SystemExit('V309 editor release import contract failed: ' + ', '.join(failed))
print('V309 editor release import contract: PASS')
