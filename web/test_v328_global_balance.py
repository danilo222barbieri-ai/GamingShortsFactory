#!/usr/bin/env python3
from pathlib import Path
import ast
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
home=(root/'web/home_v154_component/index.html').read_text(encoding='utf-8')
hub=(root/'web/creator_hub_v156_component/index.html').read_text(encoding='utf-8')
shell_path=root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
shell=shell_path.read_text(encoding='utf-8')
start=(root/'web/start_web.sh').read_text(encoding='utf-8')

def call_name(node):
    fn=node.func
    if isinstance(fn,ast.Attribute) and isinstance(fn.value,ast.Name):
        return f'{fn.value.id}.{fn.attr}'
    return ''

tree=ast.parse(shell)
v343=[]
for node in ast.walk(tree):
    if not isinstance(node,ast.Call) or not node.args:
        continue
    arg=node.args[0]
    if isinstance(arg,ast.Constant) and isinstance(arg.value,str) and '__GSF_GLOBAL_SHELL_V343' in arg.value:
        v343.append((call_name(node),arg.value))
assert len(v343)==1, f'expected one V343 bridge, found {len(v343)}'
renderer,bridge=v343[0]

legacy_short='if(!opened)shellNav("short")' in home
canonical_v331_short='if(action==="short"){shellNav("short")' in home
checks={
    'home footer brand removed':'<span class="footerBrand">Gaming Shorts Factory</span>' not in home,
    'home balance marker':'v328HomeBalance' in home and 'height:28px!important' in home,
    'home logo styling preserved':'#home154 .brandOnly:before' in home,
    'home short routing preserved':legacy_short or canonical_v331_short,
    'live compact marker preserved':'v328LiveCompact' in hub,
    'live cards remain compact':'grid-template-rows:repeat(3,74px)!important' in hub,
    'legacy V327 editor parent bridge retired':'__GSF_V327_EDITOR_BRIDGE' not in shell,
    'legacy V328 parent bridge retired':'__GSF_V328_GLOBAL_BALANCE' not in shell,
    'legacy V328 footer is not created':'id="gsf-v328-global-footer"' not in bridge and "id='gsf-v328-global-footer'" not in bridge,
    'legacy V328 brand observer retired':'gsf-v328-brand-mark' not in shell,
    'V343 bridge is executable':renderer=='_gsf_components_v343.html',
    'V343 owns Editor route':"target==='editor'" in bridge and '/editor-live/' in bridge,
    'V328 layout migration still runs':'python /app/web/fix_v328_global_balance.py /app' in start,
    'V328 verification runs after V343 retirement':start.find('python /app/web/test_v328_global_balance.py /app')>start.find('python /app/web/fix_v343_single_global_shell.py /app')>=0,
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if failed: raise SystemExit('V328 layout-only contract failed: '+', '.join(failed))
compile(shell,str(shell_path),'exec')
print('V328 LAYOUT-ONLY CONTRACT: PASS')
