#!/usr/bin/env python3
from pathlib import Path
import ast, base64, gzip, importlib.util, re, sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
FIX=ROOT/'web'/'fix_v343_single_global_shell.py'
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
HUB=ROOT/'web'/'creator_hub_v156_component'/'index.html'

spec=importlib.util.spec_from_file_location('v343',FIX)
mod=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)
bridge=gzip.decompress(base64.b64decode(mod.JS_GZIP_B64)).decode('utf-8')

print('=== V343 DECOMPRESSED BRIDGE DIAGNOSTICS ===')
for token in [
    'id="gsf-creator-hub-live-v160"',
    '/creator-hub-v156/',
    'creator-hub/state',
    'dataset.loaded',
    'GSF_HUB_FOCUS',
    'iframe',
    'MutationObserver',
    'GSF_SHELL_NAV',
]:
    print(token, 'COUNT', bridge.count(token))

for token in ['/creator-hub-v156/','gsf-creator-hub-live-v160','GSF_HUB_FOCUS']:
    print('\n--- CONTEXT',token,'---')
    for m in re.finditer(re.escape(token),bridge):
        a=max(0,m.start()-900); b=min(len(bridge),m.end()+1500)
        print(bridge[a:b])
        print('---')

print('\n=== RAW HUB BOOTSTRAP DIAGNOSTICS ===')
hub=HUB.read_text(encoding='utf-8')
for token in ['loadState();','async function loadState','let stateLoadPromise=null;','V365_CREATOR_HUB_BOOTSTRAP_FIX','V366_CREATOR_HUB_STATE_STABILITY']:
    print(token,'COUNT',hub.count(token))

print('\n=== APP SHELL BRIDGE COUNT ===')
app=APP.read_text(encoding='utf-8')
tree=ast.parse(app)
bridges=[]
for node in ast.walk(tree):
    if not isinstance(node,ast.Call) or not node.args:
        continue
    arg=node.args[0]
    if isinstance(arg,ast.Constant) and isinstance(arg.value,str) and '__GSF_GLOBAL_SHELL_V343' in arg.value:
        bridges.append(arg.value)
print('V343 executable bridge calls',len(bridges))
if bridges:
    runtime=bridges[0]
    for token in ['id="gsf-creator-hub-live-v160"','/creator-hub-v156/','creator-hub/state','GSF_HUB_FOCUS']:
        print('APP BRIDGE',token,'COUNT',runtime.count(token))
