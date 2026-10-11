#!/usr/bin/env python3
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('fix_v331',HERE/'fix_v331_primary_actions_routing.py')
MOD=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(MOD)

modern='''
<script>
function shellNav(target){
  window.parent.postMessage({type:"GSF_SHELL_NAV",target},window.parent.location.origin);
}
function route(target){ if(target==="editor") return shellNav("editor"); }
if(action==="short"){shellNav("short");value({event:"create_short",duration,engine});}
</script>
'''

# A later canonical shell owns Editor routing. V331 must be restart-safe and
# must not demand its now-obsolete direct-panel anchor.
out=MOD.patch_home(modern)
assert out==modern, 'modern canonical Home must pass V331 unchanged'

legacy='''
if(action==="short"){parentClick(["crea short","crea short finale","crea il tuo short"]);value({event:"create_short",duration,engine});}
const panel=doc.getElementById(ids[target]);
       handled=show(panel);
'''
legacy_out=MOD.patch_home(legacy)
assert 'shellNav("short")' in legacy_out, 'legacy Short route must still migrate'
assert 'GSF_V331_EDITOR_DIRECT_LOAD' in legacy_out, 'legacy Editor direct-load migration must remain supported'

bad='''if(action==="short"){shellNav("short");value({event:"create_short",duration,engine});}'''
try:
    MOD.patch_home(bad)
except RuntimeError:
    pass
else:
    raise AssertionError('V331 must still reject an unknown Home architecture')

print('V331 RESTART SAFE CONTRACT: PASS',flush=True)
