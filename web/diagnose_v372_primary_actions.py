#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, importlib.util, re, sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
V343=ROOT/'web'/'fix_v343_single_global_shell.py'
GEN=ROOT/'web'/'apply_v154_structural_home.py'
HOME=ROOT/'web'/'home_v154_component'/'index.html'

spec=importlib.util.spec_from_file_location('v343',V343)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)
bridge=gzip.decompress(base64.b64decode(mod.JS_GZIP_B64)).decode('utf-8')

def ctx(text, token, before=900, after=2200):
    i=text.find(token)
    print(f'\n=== {token} ===')
    if i<0:
        print('MISSING')
    else:
        print(text[max(0,i-before):min(len(text),i+len(token)+after)])

for tok in ['OLD_IDS','const closeCompeting','const ensureEditorSurface','const openEditor','const ensureShortSurface','const openShort','function route(data={})']:
    ctx(bridge,tok)

home=HOME.read_text(encoding='utf-8')
ctx(home,'document.querySelectorAll(".feature").forEach(b=>b.addEventListener("click"',500,1800)

gen=GEN.read_text(encoding='utf-8')
print('\n=== NAV LISTENER COUNTS IN GENERATOR ===')
print('GSF_SHELL_NAV count',gen.count("type!=='GSF_SHELL_NAV'"))
for tok in ["if(t==='editor'){open();return}","if(t==='ai'){open();return}","# V251 ROUTE GUARD","if(t==='ai-state')return;"]:
    print(tok, gen.count(tok))
ctx(gen,'# V251 ROUTE GUARD',200,2400)
