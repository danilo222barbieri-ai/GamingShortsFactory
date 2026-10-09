#!/usr/bin/env python3
from pathlib import Path
import ast
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
shell_path=root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
start_path=root/'web/start_web.sh'
shell=shell_path.read_text(encoding='utf-8')
start=start_path.read_text(encoding='utf-8')
tree=ast.parse(shell)

RETIRED=(
  '__GSF_V327_EDITOR_BRIDGE',
  '__GSF_V328_GLOBAL_BALANCE',
  '__GSF_V330_GLOBAL_CHROME',
  '__GSF_V331_PRIMARY_ACTIONS_ROUTING',
  '__GSF_V332_GLOBAL_FRAME_LOCK',
  '__GSF_V334_GLOBAL_CHROME_HARD_LOCK',
)

def call_name(node):
    fn=node.func
    if isinstance(fn,ast.Attribute) and isinstance(fn.value,ast.Name):
        return f'{fn.value.id}.{fn.attr}'
    return ''

v343=[]
unsupported=[]
for node in ast.walk(tree):
    if not isinstance(node,ast.Call) or not node.args:
        continue
    if call_name(node)=='st.html' and any(k.arg=='height' for k in node.keywords):
        unsupported.append(getattr(node,'lineno','?'))
    arg=node.args[0]
    if not isinstance(arg,ast.Constant) or not isinstance(arg.value,str):
        continue
    if '__GSF_GLOBAL_SHELL_V343' in arg.value:
        heights=[k.value.value for k in node.keywords if k.arg=='height' and isinstance(k.value,ast.Constant)]
        v343.append((call_name(node),heights[0] if heights else None))

checks={
  'Exactly one V343 executable bridge discovered':len(v343)==1,
  'V343 uses its own executable component':v343==[('_gsf_components_v343.html',0)],
  'No unsupported st.html height keyword':not unsupported,
  'V343 executable import exists':'import streamlit.components.v1 as _gsf_components_v343' in shell,
  'V336 compatibility marker exists':'V336_EXECUTABLE_SHELL_BRIDGE' in shell,
  'Retired bridge markers absent':all(x not in shell for x in RETIRED),
  'V343 runs before V336':0<=start.find('fix_v343_single_global_shell.py')<start.find('fix_v336_executable_shell_bridge.py'),
  'V336 runs before V335 cleanup':0<=start.find('fix_v336_executable_shell_bridge.py')<start.find('fix_v335_runtime_shell_recovery.py'),
  'V336 test runs after V335 cleanup':start.find('test_v336_executable_shell_bridge.py')>start.find('fix_v335_runtime_shell_recovery.py')>=0,
  'V336 test runs before final app generation':start.find('test_v336_executable_shell_bridge.py')<start.find('apply_v293_render_memory_guard.py'),
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if v343: print('V343 component:',v343)
if unsupported: print('Unsupported st.html height lines:',unsupported)
if failed: raise SystemExit('V336/V343 executable bridge contract failed: '+', '.join(failed))
print('V336 V343 EXECUTABLE BRIDGE CONTRACT: PASS')
