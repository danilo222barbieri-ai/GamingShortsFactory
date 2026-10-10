#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, importlib.util, re, subprocess, sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
FIX=ROOT/'web'/'fix_v343_single_global_shell.py'
HUB=ROOT/'web'/'creator_hub_v156_component'/'index.html'
HOME=ROOT/'web'/'home_v154_component'/'index.html'

spec=importlib.util.spec_from_file_location('v343',FIX)
mod=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)
bridge=gzip.decompress(base64.b64decode(mod.JS_GZIP_B64)).decode('utf-8')


def contexts(text, token, before=1200, after=2200):
    print('\n--- CONTEXT',token,'---')
    for m in re.finditer(re.escape(token),text):
        print(text[max(0,m.start()-before):min(len(text),m.end()+after)])
        print('---')

print('=== V343 DECOMPRESSED BRIDGE DIAGNOSTICS ===')
for token in ['/creator-hub-v156/','creator-hub/state','dataset.loaded','GSF_HUB_FOCUS','focusHub','keepGlobalShellMounted','MutationObserver','GSF_SHELL_NAV']:
    print(token, 'COUNT', bridge.count(token))
for token in ['function focusHub','GSF_SHELL_NAV','creator-hub/state','keepGlobalShellMounted']:
    contexts(bridge,token)

home=HOME.read_text(encoding='utf-8')
print('\n=== HOME NAV/STATE DIAGNOSTICS ===')
for token in ['function shellNav','GSF_SHELL_NAV','creator-hub/state','syncAccountEntry()','gsf-creator-hub-live-v160','openHub']:
    print(token,'COUNT',home.count(token))
for token in ['function shellNav','GSF_SHELL_NAV','creator-hub/state']:
    contexts(home,token,1200,3000)

print('\n=== RAW HUB loadState CALL SITES ===')
hub=HUB.read_text(encoding='utf-8')
for m in re.finditer(r'loadState\(\);',hub):
    print(hub[max(0,m.start()-500):min(len(hub),m.end()+650)])
    print('---')

print('\n=== PATCHED HUB BOOTSTRAP DIAGNOSTICS ===')
subprocess.run([sys.executable,str(ROOT/'web'/'fix_v359_creator_hub_gamebar_fit.py'),str(HUB)],check=True)
hub=HUB.read_text(encoding='utf-8')
for token in ['loadState();','async function loadState','let stateLoadPromise=null;','V365_CREATOR_HUB_BOOTSTRAP_FIX','V366_CREATOR_HUB_STATE_STABILITY','V368_CREATOR_HUB_TOUCH_RECOVERY']:
    print(token,'COUNT',hub.count(token))
