#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
PATCH=ROOT/'web'/'fix_v319_ai_results_bridge.py'
SERVER=ROOT/'web'/'direct_upload_server.py'
NGINX=ROOT/'web'/'nginx.conf.template'
AI=ROOT/'web'/'ai_v221_component'/'index.html'
HOME=ROOT/'web'/'home_v154_component'/'index.html'

def fail(msg): print('[FAIL]',msg); raise SystemExit(1)
def ok(msg): print('[ OK ]',msg)

if not PATCH.is_file(): fail('V319 patch missing')
spec=importlib.util.spec_from_file_location('v319_ai_results_bridge',PATCH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

server='''import re\nimport urllib.parse\nclass Handler(BaseHTTPRequestHandler):\n    def do_GET(self):\n        path=urlparse(self.path)\n        clean=path.path.rstrip("/")\n        if clean in ("","/health"):\n            return\n'''
nginx='''server {\n    # V221 living AI engines surface.\n}\n'''
ai='''<html><head></head><body><script>\nfunction v317SyncResults(){}\nfunction sync(){v317SyncResults();}\ncreate.addEventListener("click",()=>{if(!state.loaded)return;guide("creating");status.textContent="L’IA sta cercando i momenti migliori…";send("create",{engine:state.engine,duration:state.duration})});\n</script></body></html>'''
home='''if(action==="create"){value({event:"create_ai",duration,engine:nextEngine});}'''

for label,patcher,sample in (
 ('server',mod.patch_server_text,server),
 ('nginx',mod.patch_nginx_text,nginx),
 ('AI',mod.patch_ai_text,ai),
 ('Home',mod.patch_home_text,home),
):
 patched=patcher(sample)
 if patcher(patched)!=patched: fail('V319 '+label+' patch is not idempotent')
 ok('V319 '+label+' patch idempotent')

# Regression: V320 intentionally replaces V319's click handler. A Railway
# process restart reruns V319 before V320, so V319 must recognize the later
# handler as an already-migrated successor instead of aborting startup.
v319_ai=mod.patch_ai_text(ai)
v320_successor=v319_ai.replace(
 'create.addEventListener("click",v319StartAnalysis);',
 '/* V320 MOBILE AI STABILITY */\ncreate.addEventListener("click",v320StartAnalysis);',
 1,
)
try:
 restarted=mod.patch_ai_text(v320_successor)
except Exception as exc:
 fail('V319 restart after V320 successor crashes: '+repr(exc))
if restarted!=v320_successor:
 fail('V319 rewrites AI after V320 successor handoff')
ok('V319 restart-safe after V320 click-handler handoff')

checks=(
 (mod.patch_server_text(server),'if clean=="/ai/results":','server results route'),
 (mod.patch_server_text(server),'(?:mini|candidate|preview)','server preview discovery'),
 (mod.patch_nginx_text(nginx),'location = /ai/results','nginx results route'),
 (mod.patch_ai_text(ai),'fetch("/ai/results?_="+Date.now()','AI result polling'),
 (mod.patch_ai_text(ai),'request_id:requestId','AI unique request id'),
 (mod.patch_ai_text(ai),'ANALISI IN CORSO…','AI busy feedback'),
 (mod.patch_home_text(home),'V319 CREATE NONCE','Home create nonce'),
)
for haystack,marker,label in checks:
 if marker not in haystack: fail(label+' missing')
 ok(label)

print('\nV319 AI RESULTS BRIDGE CONTRACT: PASS')
