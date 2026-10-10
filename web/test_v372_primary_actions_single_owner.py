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

# The Home tiles are page navigation. They must not also click hidden Streamlit
# controls or emit component values, because those operations rerun Streamlit and
# can immediately unmount/close the surface that V343 just opened.
click=re.search(r'document\.querySelectorAll\("\.feature"\)\.forEach\(b=>b\.addEventListener\("click",\(\)=>\{(.*?)\n \}\)\);',HOME,re.S)
ok(bool(click),'Home primary click block exists')
block=click.group(1)
ok('shellNav("ai")' in block,'Crea con IA routes through V343')
ok('shellNav("editor")' in block,'Game Editor routes through V343')
ok('shellNav("short")' in block,'Crea Short routes through V343')
ok('parentClick(' not in block,'Primary navigation never clicks hidden Streamlit controls')
ok('setEngine(' not in block,'Editor navigation does not mutate engine/backend state')
ok('value({' not in block,'Primary navigation does not trigger a Streamlit rerun')

# V220/V221 keep only their own surface bootstrap responsibilities when V343 is
# active. They must not close competing surfaces. V251 is a pure old router and
# therefore stands down completely under V343.
editor_i=GEN.find("if(t==='editor'){open();return}")
ok(editor_i>=0,'Editor V220 listener exists')
editor_window=GEN[max(0,editor_i-1000):editor_i+1800]
ok('P.__GSF_GLOBAL_SHELL_V343' in editor_window,'Editor V220 defers navigation ownership to V343')

ai_i=GEN.find("if(t==='ai'){open();return}")
ok(ai_i>=0,'AI V221 listener exists')
ai_window=GEN[max(0,ai_i-1000):ai_i+1900]
ok('P.__GSF_GLOBAL_SHELL_V343' in ai_window,'AI V221 defers navigation ownership to V343')
ok("if(t==='ai-state'){forwardState(e.data);return}" in ai_window,'AI state forwarding survives V343 ownership')

v251_i=GEN.find('# V251 ROUTE GUARD')
ok(v251_i>=0,'V251 route guard exists')
v251_window=GEN[v251_i:v251_i+3500]
ok('if(P.__GSF_GLOBAL_SHELL_V343)return;' in v251_window,'V251 route guard stands down under V343')

# The canonical V343 router itself must retain all three destinations.
spec=importlib.util.spec_from_file_location('v343',V343)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)
bridge=gzip.decompress(base64.b64decode(mod.JS_GZIP_B64)).decode('utf-8')
ok("if(target==='editor'){openEditor();return true}" in bridge,'V343 owns Editor')
ok("if(target==='short'){openShort();return true}" in bridge,'V343 owns Short')
ok("if(target==='ai')return openExisting('gsf-ai-overlay-v221')" in bridge,'V343 owns AI')

# On the real startup image the generated apps exist too. Enforce that the same
# contract reached those files, not only the source generator.
for name in ('GamingShortsFactory_V154_STRUCTURAL_HOME.py','GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'):
    path=ROOT/name
    if not path.is_file():
        continue
    runtime=path.read_text(encoding='utf-8')
    ok('V372_PRIMARY_ACTIONS_SINGLE_OWNER' in runtime,name+' carries V372 runtime marker')
    ok('if(P.__GSF_GLOBAL_SHELL_V343)return;' in runtime,name+' retires V251 runtime router')

print('V372 PRIMARY ACTION SINGLE OWNER CONTRACT: PASS',flush=True)
