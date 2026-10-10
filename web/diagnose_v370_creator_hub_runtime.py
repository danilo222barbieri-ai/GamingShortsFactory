#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, importlib.util, re, subprocess, sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
FIX=ROOT/'web'/'fix_v343_single_global_shell.py'
HUB=ROOT/'web'/'creator_hub_v156_component'/'index.html'

spec=importlib.util.spec_from_file_location('v343',FIX)
mod=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)
bridge=gzip.decompress(base64.b64decode(mod.JS_GZIP_B64)).decode('utf-8')

print('=== V343 DECOMPRESSED BRIDGE DIAGNOSTICS ===')
for token in [
    '/creator-hub-v156/',
    'creator-hub/state',
    'dataset.loaded',
    'GSF_HUB_FOCUS',
    'ensureHubSurface',
    'focusHub',
    'keepGlobalShellMounted',
    'MutationObserver',
    'GSF_SHELL_NAV',
]:
    print(token, 'COUNT', bridge.count(token))

for token in ['creator-hub/state','/creator-hub-v156/','keepGlobalShellMounted','MutationObserver','GSF_HUB_FOCUS']:
    print('\n--- CONTEXT',token,'---')
    for m in re.finditer(re.escape(token),bridge):
        a=max(0,m.start()-1200); b=min(len(bridge),m.end()+1800)
        print(bridge[a:b])
        print('---')

print('\n=== RAW HUB loadState CALL SITES ===')
hub=HUB.read_text(encoding='utf-8')
for m in re.finditer(r'loadState\(\);',hub):
    a=max(0,m.start()-500); b=min(len(hub),m.end()+650)
    print(hub[a:b])
    print('---')

print('\n=== PATCHED HUB BOOTSTRAP DIAGNOSTICS ===')
# Apply the exact runtime Hub patch chain used by startup, in a disposable checkout.
subprocess.run([sys.executable,str(ROOT/'web'/'fix_v359_creator_hub_gamebar_fit.py'),str(HUB)],check=True)
hub=HUB.read_text(encoding='utf-8')
for token in ['loadState();','async function loadState','let stateLoadPromise=null;','V365_CREATOR_HUB_BOOTSTRAP_FIX','V366_CREATOR_HUB_STATE_STABILITY','V368_CREATOR_HUB_TOUCH_RECOVERY']:
    print(token,'COUNT',hub.count(token))
print('\n=== PATCHED HUB loadState CALL SITES ===')
for m in re.finditer(r'loadState\(\);',hub):
    a=max(0,m.start()-550); b=min(len(hub),m.end()+750)
    print(hub[a:b])
    print('---')
