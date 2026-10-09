#!/usr/bin/env python3
from pathlib import Path
import ast
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
MARK='V336_EXECUTABLE_SHELL_BRIDGE'
IMPORT='import streamlit.components.v1 as _gsf_components_v336'

# These five late mobile-shell patches are intentionally JavaScript bridges.
# Streamlit 1.49 st.html sanitizes/does not execute JavaScript, while
# streamlit.components.v1.html renders an executable same-origin iframe. The
# bridge scripts already target window.parent, which is exactly the parent DOM
# they need to control.
BRIDGES={
    'V328':'__GSF_V328_GLOBAL_BALANCE',
    'V330':'__GSF_V330_GLOBAL_CHROME',
    'V331':'__GSF_V331_PRIMARY_ACTIONS_ROUTING',
    'V332':'__GSF_V332_GLOBAL_FRAME_LOCK',
    'V334':'__GSF_V334_GLOBAL_CHROME_HARD_LOCK',
}


def call_name(node):
    fn=node.func
    if isinstance(fn,ast.Attribute) and isinstance(fn.value,ast.Name):
        return f'{fn.value.id}.{fn.attr}'
    return ''


def main():
    if not APP.is_file():
        raise SystemExit('V336 shell app missing')
    source=APP.read_text(encoding='utf-8')
    tree=ast.parse(source)
    lines=source.splitlines(keepends=True)
    found={}

    for node in ast.walk(tree):
        if not isinstance(node,ast.Call) or not node.args:
            continue
        arg=node.args[0]
        if not isinstance(arg,ast.Constant) or not isinstance(arg.value,str):
            continue
        body=arg.value
        hits=[name for name,marker in BRIDGES.items() if marker in body]
        if not hits:
            continue
        if len(hits)!=1:
            raise RuntimeError('V336 bridge call has ambiguous markers: '+','.join(hits))
        name=hits[0]
        qual=call_name(node)
        if name in found:
            raise RuntimeError(f'V336 duplicate bridge marker {name}')
        found[name]=(node,qual)

    missing=sorted(set(BRIDGES)-set(found))
    if missing:
        raise RuntimeError('V336 missing bridge markers: '+', '.join(missing))

    # Work from bottom to top so line-local replacements cannot disturb later
    # source positions. Every bridge currently starts with st.html(...).
    edits=[]
    for name,(node,qual) in found.items():
        if qual=='_gsf_components_v336.html':
            continue
        if qual!='st.html':
            raise RuntimeError(f'V336 unexpected renderer for {name}: {qual or "unknown"}')
        idx=node.lineno-1
        line=lines[idx]
        pos=line.find('st.html',node.col_offset)
        if pos<0:
            raise RuntimeError(f'V336 cannot locate st.html source for {name} at line {node.lineno}')
        edits.append((idx,pos,name))

    for idx,pos,name in sorted(edits,reverse=True):
        line=lines[idx]
        lines[idx]=line[:pos]+'_gsf_components_v336.html'+line[pos+len('st.html'):]

    converted=''.join(lines)
    if IMPORT not in converted:
        anchor='import streamlit as st\n'
        if anchor not in converted:
            raise RuntimeError('V336 Streamlit import anchor missing')
        converted=converted.replace(anchor,anchor+IMPORT+'\n',1)

    if MARK not in converted:
        marker_line=f'# {MARK} — executable parent DOM bridges for Streamlit 1.49.\n'
        converted=converted.replace(IMPORT+'\n',IMPORT+'\n'+marker_line,1)

    # Re-parse and prove each bridge is executable and keeps a zero-height
    # iframe. CSS-only st.html blocks remain untouched in the parent document.
    check=ast.parse(converted)
    verified={}
    for node in ast.walk(check):
        if not isinstance(node,ast.Call) or not node.args:
            continue
        arg=node.args[0]
        if not isinstance(arg,ast.Constant) or not isinstance(arg.value,str):
            continue
        for name,marker in BRIDGES.items():
            if marker not in arg.value:
                continue
            qual=call_name(node)
            heights=[k.value.value for k in node.keywords if k.arg=='height' and isinstance(k.value,ast.Constant)]
            if qual!='_gsf_components_v336.html':
                raise RuntimeError(f'V336 bridge {name} is not executable: {qual}')
            if heights!=[0]:
                raise RuntimeError(f'V336 bridge {name} must retain height=0, got {heights}')
            verified[name]=True

    missing_verified=sorted(set(BRIDGES)-set(verified))
    if missing_verified:
        raise RuntimeError('V336 verification missing: '+', '.join(missing_verified))
    if 'gsf-mobile-full-viewport-v181' not in converted:
        raise RuntimeError('V336 CSS-only parent shell marker missing')

    compile(converted,str(APP),'exec')
    if converted!=source:
        APP.write_text(converted,encoding='utf-8')
    print(f'{MARK} converted={len(edits)} verified={len(verified)}',flush=True)

if __name__=='__main__':
    main()
