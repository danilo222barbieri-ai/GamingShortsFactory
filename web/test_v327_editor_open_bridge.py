#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
shell=(root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py').read_text(encoding='utf-8')
fix=(root/'web'/'fix_v327_editor_open_bridge.py').read_text(encoding='utf-8')

checks={
    'V327 bridge marker present':'V327_EDITOR_OPEN_BRIDGE' in shell,
    'editor stays lazy until tapped':'data-src="/editor-live/"' in shell and 'data-loaded="0"' in shell,
    'shell nav editor is captured':"String(e.data.target||'')==='editor'" in shell,
    'editor iframe loads on tap':"f.src=(f.dataset.src||'/editor-live/')+'?v=327'" in shell,
    'editor overlay is opened':"o.classList.add('is-open')" in shell and "o.style.pointerEvents='auto'" in shell,
    'bridge persists editor-open state':"gsf_editor_overlay_open_v223" in shell,
    'fix is idempotent':'if MARK in text:return text' in fix,
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if failed: raise SystemExit('V327 editor open bridge contract failed: '+', '.join(failed))
print('V327 EDITOR OPEN BRIDGE CONTRACT: PASS')

v328=root/'web/test_v328_global_balance.py'
if not v328.is_file(): raise SystemExit('V328 test missing')
subprocess.run([sys.executable,str(v328),str(root)],check=True)
