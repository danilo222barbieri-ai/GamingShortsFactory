#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
home=(root/'web/home_v154_component/index.html').read_text(encoding='utf-8')
shell=(root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py').read_text(encoding='utf-8')
start=(root/'web/start_web.sh').read_text(encoding='utf-8')
fix=(root/'web/fix_v331_primary_actions_routing.py').read_text(encoding='utf-8')

checks={
    'V331 shell bridge present':'V331_PRIMARY_ACTIONS_ROUTING' in shell,
    'Home Short always routes canonically':'if(action==="short"){shellNav("short")' in home,
    'Home does not depend on text-click to open Short':'if(action==="short"){parentClick(["crea short"' not in home,
    'Editor frame is loaded by the canonical action':'GSF_V331_EDITOR_DIRECT_LOAD' in home and "'/editor-live/?v=331'" in home,
    'Editor overlay has a retrying direct opener':'v331OpenEditor' in shell and 'attempt<20' in shell,
    'Editor lazy frame gets loaded':'/editor-live/?v=331' in shell and "dataset.loaded='1'" in shell,
    'Short has a real always-open surface':'gsf-short-overlay-v331' in shell and 'Crea Short' in shell,
    'Short CSS is injected into the parent document':"style.id='gsf-v331-primary-actions-style'" in shell and 'D.head.appendChild(style)' in shell,
    'Short route opens the surface':"target==='short'" in shell and 'v331OpenShort' in shell,
    'Short render uses stable Streamlit keys':'.st-key-gsf-major-create-short button' in shell and '.st-key-create_final_short_v54 button' in shell,
    'Short can jump to Editor':"target:'editor'" in shell,
    'V331 is idempotent':'V331_PRIMARY_ACTIONS_ROUTING' in fix and 'if MARK not in app_text' in fix,
    'startup runs V331 after V330':start.find('fix_v331_primary_actions_routing.py')>start.find('fix_v330_global_chrome.py')>=0,
    'startup validates V331 before final app generation':start.find('test_v331_primary_actions_routing.py')<start.find('apply_v293_render_memory_guard.py'),
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if failed: raise SystemExit('V331 primary actions routing contract failed: '+', '.join(failed))
print('V331 PRIMARY ACTIONS ROUTING CONTRACT: PASS')
