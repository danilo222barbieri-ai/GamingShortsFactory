#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
home=(ROOT/'web'/'home_v154_component'/'index.html').read_text(encoding='utf-8')

def ok(cond,label):
    if not cond:
        raise AssertionError('FAIL: '+label)
    print('[ OK ] '+label,flush=True)

m=re.search(r'document\.querySelectorAll\("\.feature"\)\.forEach\(b=>b\.addEventListener\("click",\(\)=>\{(.*?)\n\s*\}\)\);',home,re.S)
ok(bool(m),'Home feature action handler exists')
body=m.group(1)

ai=re.search(r'if\(action==="ai"\)\{(.*?)\}',body,re.S)
editor=re.search(r'if\(action==="editor"\)\{(.*?)\}',body,re.S)
short=re.search(r'if\(action==="short"\)\{(.*?)\}',body,re.S)
ok(bool(ai) and bool(editor) and bool(short),'all three primary actions exist')

ok('shellNav("ai")' in ai.group(1),'IA routes through shell')
ok('value(' not in ai.group(1),'IA navigation does not rerun Streamlit')

ok('setEngine("manual",false)' in editor.group(1),'Editor selects manual locally without emitting component state')
ok('shellNav("editor")' in editor.group(1),'Editor routes through shell')
ok('value(' not in editor.group(1),'Editor navigation does not rerun Streamlit')

ok('shellNav("short")' in short.group(1),'Short routes through shell')
ok('parentClick(' not in short.group(1) and 'value(' not in short.group(1),'Short navigation does not use hidden Streamlit controls or rerun')

print('V372 NAVIGATION NO-RERUN CONTRACT: PASS',flush=True)
