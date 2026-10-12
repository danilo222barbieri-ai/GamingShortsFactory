#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
home=(root/'web/home_v154_component/index.html').read_text(encoding='utf-8')
shell=(root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py').read_text(encoding='utf-8')
start=(root/'web/start_web.sh').read_text(encoding='utf-8')
fix=(root/'web/fix_v331_primary_actions_routing.py').read_text(encoding='utf-8')

legacy_editor=('GSF_V331_EDITOR_DIRECT_LOAD' in home and "'/editor-live/?v=331'" in home)
# V343 deliberately removes the old Home-local Editor route and becomes the
# single global navigation owner. On a restart V331 runs before V343, so the
# already-canonical generated shell/home must be accepted instead of forcing
# the retired V331 marker back into Home.
canonical_shell=('GSF_GLOBAL_SHELL_V343' in shell and "target==='editor'" in shell and '/editor-live/' in shell)
editor_route_ok=legacy_editor or canonical_shell
legacy_short_css=("style.id='gsf-v331-primary-actions-style'" in shell and 'D.head.appendChild(style)' in shell)
legacy_v331_shell=('V331_PRIMARY_ACTIONS_ROUTING' in shell and 'v331OpenEditor' in shell and 'v331OpenShort' in shell)

checks={
    'V331 shell bridge present before V343 retirement':legacy_v331_shell or canonical_shell,
    'Home Short always routes canonically':'if(action==="short"){shellNav("short")' in home,
    'Home does not depend on text-click to open Short':'if(action==="short"){parentClick(["crea short"' not in home,
    'Editor route is restart-safe':editor_route_ok,
    'V331 restart-safe shim is active':'V337_RESTART_SAFE_V331' in fix,
    'Editor opener is owned by V331 or canonical V343':(('v331OpenEditor' in shell and 'attempt<20' in shell) or canonical_shell),
    'Editor lazy frame gets loaded':(("/editor-live/?v=331" in shell and "dataset.loaded='1'" in shell) or canonical_shell),
    'Short has a real always-open surface':(('gsf-short-overlay-v331' in shell and 'Crea Short' in shell) or ('gsf-short-overlay-v343' in shell and canonical_shell)),
    'Short presentation is owned by legacy V331 or canonical shell':legacy_short_css or canonical_shell,
    'Short route opens the surface':(("target==='short'" in shell and 'v331OpenShort' in shell) or canonical_shell),
    'Short render is owned by V331 or canonical V343':(('.st-key-gsf-major-create-short button' in shell and '.st-key-create_final_short_v54 button' in shell) or canonical_shell),
    'Short can jump to Editor':("target:'editor'" in shell) or canonical_shell,
    'V331 is idempotent':'V331_PRIMARY_ACTIONS_ROUTING' in fix and 'if MARK not in app_text' in fix,
    'startup runs V331 before V333 and V343':0<=start.find('fix_v331_primary_actions_routing.py')<start.find('fix_v333_home_cta_touch_fix.py')<start.find('fix_v343_single_global_shell.py'),
    'startup validates V331 before V343 takeover':0<=start.find('test_v331_primary_actions_routing.py')<start.find('fix_v343_single_global_shell.py'),
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if failed: raise SystemExit('V331 primary actions routing contract failed: '+', '.join(failed))
print('V331 PRIMARY ACTIONS ROUTING CONTRACT: PASS')
