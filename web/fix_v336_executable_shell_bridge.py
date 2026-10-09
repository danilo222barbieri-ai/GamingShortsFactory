#!/usr/bin/env python3
from pathlib import Path
import ast
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
MARK='V336_EXECUTABLE_SHELL_BRIDGE'
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


def main():
    if not APP.is_file():
        raise SystemExit('V336 shell app missing')
    source=APP.read_text(encoding='utf-8')
    if any(marker in source for marker in RETIRED):
        raise RuntimeError('V336 found retired parent bridge markers after V343 cleanup')

    tree=ast.parse(source)
    v343=[]
    unsupported=[]
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call):
            continue
        qual=call_name(node)
        if qual=='st.html' and any(k.arg=='height' for k in node.keywords):
            unsupported.append(getattr(node,'lineno','?'))
        if not node.args:
            continue
        arg=node.args[0]
        if not isinstance(arg,ast.Constant) or not isinstance(arg.value,str):
            continue
        if '__GSF_GLOBAL_SHELL_V343' not in arg.value:
            continue
        heights=[k.value.value for k in node.keywords if k.arg=='height' and isinstance(k.value,ast.Constant)]
        v343.append((qual,heights))

    if len(v343)!=1:
        raise RuntimeError(f'V336 expected one V343 executable bridge, found {len(v343)}')
    qual,heights=v343[0]
    if qual!='_gsf_components_v343.html':
        raise RuntimeError(f'V336 V343 bridge is not executable: {qual}')
    if heights!=[0]:
        raise RuntimeError(f'V336 V343 bridge must use height=0, got {heights}')
    if unsupported:
        raise RuntimeError('V336 unsupported st.html height keyword remains at lines '+','.join(map(str,unsupported)))
    if 'import streamlit.components.v1 as _gsf_components_v343' not in source:
        raise RuntimeError('V336 V343 executable components import missing')

    if MARK not in source:
        anchor='import streamlit.components.v1 as _gsf_components_v343\n'
        if anchor not in source:
            raise RuntimeError('V336 V343 import anchor missing')
        source=source.replace(anchor,anchor+f'# {MARK} — V343 is executable; legacy parent bridges are retired.\n',1)

    compile(source,str(APP),'exec')
    APP.write_text(source,encoding='utf-8')
    print(f'{MARK} V343 verified=1 retired={len(RETIRED)}',flush=True)

if __name__=='__main__':
    main()
