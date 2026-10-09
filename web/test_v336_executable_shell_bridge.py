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

MARKERS={
  'V328':'__GSF_V328_GLOBAL_BALANCE',
  'V330':'__GSF_V330_GLOBAL_CHROME',
  'V331':'__GSF_V331_PRIMARY_ACTIONS_ROUTING',
  'V332':'__GSF_V332_GLOBAL_FRAME_LOCK',
  'V334':'__GSF_V334_GLOBAL_CHROME_HARD_LOCK',
}

script_calls={}
remaining_st_html=[]
component_height=[]
for node in ast.walk(tree):
    if not isinstance(node,ast.Call) or not node.args:
        continue
    arg=node.args[0]
    if not isinstance(arg,ast.Constant) or not isinstance(arg.value,str):
        continue
    body=arg.value
    hits=[name for name,marker in MARKERS.items() if marker in body]
    if not hits:
        continue
    fn=node.func
    if isinstance(fn,ast.Attribute) and isinstance(fn.value,ast.Name):
        qual=f'{fn.value.id}.{fn.attr}'
    else:
        qual='other'
    for name in hits:
        script_calls[name]=qual
        if qual=='st.html': remaining_st_html.append(name)
        if qual=='_gsf_components_v336.html':
            h=[k.value for k in node.keywords if k.arg=='height' and isinstance(k.value,ast.Constant)]
            component_height.append((name,h[0] if h else None))

checks={
  'All five interactive bridges discovered':set(script_calls)==set(MARKERS),
  'Interactive bridges use executable component HTML':all(script_calls.get(k)=='_gsf_components_v336.html' for k in MARKERS),
  'No interactive bridge remains in st.html':not remaining_st_html,
  'All executable bridge iframes are zero-height':len(component_height)==len(MARKERS) and all(v==0 for _,v in component_height),
  'Executable components import exists':'import streamlit.components.v1 as _gsf_components_v336' in shell,
  'CSS-only parent st.html remains':'gsf-mobile-full-viewport-v181' in shell and 'st.html(r"""' in shell,
  'V336 marker exists':'V336_EXECUTABLE_SHELL_BRIDGE' in shell,
  'V336 conversion runs after V334':start.find('fix_v336_executable_shell_bridge.py')>start.find('fix_v334_global_chrome_hard_lock.py')>=0,
  'V336 conversion runs before V335 compatibility cleanup':0<=start.find('fix_v336_executable_shell_bridge.py')<start.find('fix_v335_runtime_shell_recovery.py'),
  'V336 test runs after V335 cleanup':start.find('test_v336_executable_shell_bridge.py')>start.find('fix_v335_runtime_shell_recovery.py')>=0,
  'V336 test runs before final app generation':start.find('test_v336_executable_shell_bridge.py')<start.find('apply_v293_render_memory_guard.py'),
}

failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if script_calls: print('V336 bridge functions:',script_calls)
if component_height: print('V336 component heights:',component_height)
if remaining_st_html: print('V336 non-executable bridges:',remaining_st_html)
if failed: raise SystemExit('V336 executable shell bridge contract failed: '+', '.join(failed))
print('V336 EXECUTABLE SHELL BRIDGE CONTRACT: PASS')
