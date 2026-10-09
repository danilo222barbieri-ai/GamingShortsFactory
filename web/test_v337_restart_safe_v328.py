#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
fix=(root/'web/fix_v328_global_balance.py').read_text(encoding='utf-8')
start=(root/'web/start_web.sh').read_text(encoding='utf-8')

checks={
    'V337 marker applied to V328':'V337_RESTART_SAFE_V328' in fix,
    'V328 recognizes V331 canonical Short route':'canonical_v331_short' in fix and 'if(action==="short"){shellNav("short")' in fix,
    'V328 preserves legacy fallback':'if(!opened)shellNav("short")' in fix,
    'V337 runs before V327 delegates to V328':0<=start.find('fix_v337_restart_safe_v328.py')<start.find('fix_v327_editor_open_bridge.py'),
    'V337 contract runs before V327':0<=start.find('test_v337_restart_safe_v328.py')<start.find('fix_v327_editor_open_bridge.py'),
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if failed: raise SystemExit('V337 restart-safe V328 contract failed: '+', '.join(failed))
compile(fix,str(root/'web/fix_v328_global_balance.py'),'exec')
print('V337 RESTART-SAFE V328 CONTRACT: PASS')
