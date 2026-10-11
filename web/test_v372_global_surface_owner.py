#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, importlib.util, re, sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
HOME=ROOT/'web'/'home_v154_component'/'index.html'
GEN=ROOT/'web'/'apply_v154_structural_home.py'
V343=ROOT/'web'/'fix_v343_single_global_shell.py'

def ok(cond,label):
    if not cond:
        raise AssertionError('FAIL: '+label)
    print('[ OK ] '+label,flush=True)

home=HOME.read_text(encoding='utf-8')
gen=GEN.read_text(encoding='utf-8')

# The three Home actions must all enter the same canonical parent router.
ok('if(action==="ai"){shellNav("ai")' in home,'Crea con IA uses canonical shell')
ok('if(action==="editor"){setEngine("manual",false);shellNav("editor")' in home,'Game Editor uses canonical shell without component rerun')
ok('if(action==="short"){shellNav("short")' in home,'Crea Short uses canonical shell')

# Legacy surface scripts may retain internal iframe messaging, but they must not
# mutate/open/close parent surfaces after V343 becomes the canonical owner.
def block(name,next_anchor):
    m=re.search(re.escape(name)+r" = r'''(.*?)"+re.escape(next_anchor),gen,re.S)
    ok(bool(m),name+' block exists')
    return m.group(1)

social=block('_social_surface_v159',"'''\ns = s.rstrip()")
editor=block('_editor_surface_v220',"'''\ns = s.rstrip()")
ai=block('_ai_surface_v221',"'''\ns = s.rstrip()")
account=block('_account_surface_v223',"'''\ns = s.rstrip()")
route_guard=block('_route_guard_v251',"'''\ns = s.rstrip()")

for label,text,guard in (
    ('V159 Social',social,'if(window.__GSF_GLOBAL_SHELL_V343)return;'),
    ('V220 Editor',editor,'if(window.__GSF_GLOBAL_SHELL_V343)return;'),
    ('V221 AI',ai,'if(window.__GSF_GLOBAL_SHELL_V343)return;'),
    ('V223 Account',account,'if(window.__GSF_GLOBAL_SHELL_V343)return;'),
    ('V251 Route Guard',route_guard,'if(P.__GSF_GLOBAL_SHELL_V343)return;'),
):
    ok(guard in text,label+' stands down from GSF_SHELL_NAV under V343')

spec=importlib.util.spec_from_file_location('v343',V343)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)
bridge=gzip.decompress(base64.b64decode(mod.JS_GZIP_B64)).decode('utf-8')
ok("if(target==='editor'){openEditor();return true}" in bridge,'V343 owns Editor route')
ok("if(target==='ai')return openExisting('gsf-ai-overlay-v221')" in bridge,'V343 owns AI route')
ok("if(target==='short'){openShort();return true}" in bridge,'V343 owns Short route')
ok("P.addEventListener('message',e=>{if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;route(e.data)},true)" in bridge,'V343 is the single canonical shell listener')

print('V372 GLOBAL SURFACE OWNER CONTRACT: PASS',flush=True)
