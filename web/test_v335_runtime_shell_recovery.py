#!/usr/bin/env python3
from pathlib import Path
import ast
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
shell_path=root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
shell=shell_path.read_text(encoding='utf-8')
start=(root/'web/start_web.sh').read_text(encoding='utf-8')

def call_name(node):
    fn=node.func
    if isinstance(fn,ast.Attribute) and isinstance(fn.value,ast.Name):
        return f'{fn.value.id}.{fn.attr}'
    return ''

tree=ast.parse(shell)
bad=[]
v343=[]
for node in ast.walk(tree):
    if not isinstance(node,ast.Call):
        continue
    fn=node.func
    if isinstance(fn,ast.Attribute) and fn.attr=='html' and isinstance(fn.value,ast.Name) and fn.value.id=='st':
        if any(k.arg=='height' for k in node.keywords):
            bad.append(getattr(node,'lineno','?'))
    if not node.args:
        continue
    arg=node.args[0]
    if isinstance(arg,ast.Constant) and isinstance(arg.value,str) and '__GSF_GLOBAL_SHELL_V343' in arg.value:
        v343.append((call_name(node),arg.value))

assert len(v343)==1, f'expected one V343 bridge after V335, found {len(v343)}'
renderer,bridge=v343[0]
checks={
  'No unsupported st.html height keyword':not bad,
  'Editor route survives repair':'gsf-editor-overlay-v220' in bridge and "target==='editor'" in bridge and '/editor-live/' in bridge,
  'Short route survives repair':'gsf-short-overlay-v343' in bridge and "target==='short'" in bridge,
  'Global chrome survives repair':'gsf-global-header' in bridge and 'gsf-global-gamebar' in bridge and 'gsf-global-footer' in bridge,
  'V343 executable bridge survives repair':renderer=='_gsf_components_v343.html' and 'GSF_GLOBAL_SHELL_V343' in shell,
  'V335 runs after V336 compatibility gate':start.find('fix_v335_runtime_shell_recovery.py')>start.find('fix_v336_executable_shell_bridge.py')>=0,
  'V335 test runs after repair':start.find('test_v335_runtime_shell_recovery.py')>start.find('fix_v335_runtime_shell_recovery.py')>=0,
  'Runtime guard finishes before final app generation':start.find('test_v335_runtime_shell_recovery.py')<start.find('apply_v293_render_memory_guard.py'),
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if bad: print('Unsupported st.html height keyword at shell lines:',bad)
if failed: raise SystemExit('V335 runtime shell recovery contract failed: '+', '.join(failed))
print('V335 V343 RUNTIME SHELL RECOVERY CONTRACT: PASS')
