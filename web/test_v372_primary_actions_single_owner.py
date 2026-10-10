#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, importlib.util, re, sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
HOME=(ROOT/'web/home_v154_component/index.html').read_text(encoding='utf-8')
GEN=(ROOT/'web/apply_v154_structural_home.py').read_text(encoding='utf-8')
V343=ROOT/'web/fix_v343_single_global_shell.py'

def ok(cond,label):
    if not cond:
        raise AssertionError('FAIL: '+label)
    print('[ OK ] '+label,flush=True)

# All three Home primary actions must emit canonical shell routes.
click=re.search(r'document\.querySelectorAll\("\.feature"\)\.forEach\(b=>b\.addEventListener\("click",\(\)=>\{(.*?)\n \}\)\);',HOME,re.S)
ok(bool(click),'Home primary click block exists')
block=click.group(1)
ok('shellNav("ai")' in block,'Crea con IA routes through V343')
ok('shellNav("editor")' in block,'Game Editor routes through V343')
ok('shellNav("short")' in block,'Crea Short routes through V343')

# Legacy action routers may remain for fallback, but must stand down when V343 owns the shell.
for marker,token in [
    ('Editor V220',"if(t==='editor'){open();return}"),
    ('AI V221',"if(t==='ai'){open();return}"),
    ('V251 route guard',"# V251 ROUTE GUARD"),
]:
    i=GEN.find(token)
    ok(i>=0,marker+' exists')
    window=GEN[max(0,i-900):i+1500]
    ok('__GSF_GLOBAL_SHELL_V343' in window,marker+' stands down under V343')

# The canonical V343 router must own all three destinations.
spec=importlib.util.spec_from_file_location('v343',V343)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)
bridge=gzip.decompress(base64.b64decode(mod.JS_GZIP_B64)).decode('utf-8')
ok("if(target==='editor'){openEditor();return true}" in bridge,'V343 owns Editor')
ok("if(target==='short'){openShort();return true}" in bridge,'V343 owns Short')
ok("if(target==='ai')return openExisting('gsf-ai-overlay-v221')" in bridge,'V343 owns AI')

print('V372 PRIMARY ACTION SINGLE OWNER CONTRACT: PASS',flush=True)
