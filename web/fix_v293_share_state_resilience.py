#!/usr/bin/env python3
from pathlib import Path
import sys

path=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/app/web/direct_upload_server.py')
s=path.read_text(encoding='utf-8')
start=s.find('if clean=="/share/state":')
end=s.find('if clean=="/share/final":',start)
if start < 0 or end < 0:
    raise RuntimeError('V293 share/state block missing')
block=s[start:end]
profile_line='            profile=_creator_account_load(sid) or {}\n'
providers_line='            providers=dict(profile.get("providers") or {}) if isinstance(profile,dict) else {}\n'
snapshot_line='            social_snapshot=_creator_social_snapshot(sid,providers)\n'
if snapshot_line.strip() in block and '"social":social_snapshot' in block:
    print('V293 share/state resilience already applied:',path)
    raise SystemExit(0)

sid_anchor='''            if not sid:\n                _json(self,400,{"ok":False,"error":"Sessione browser non valida."})\n                return\n'''
if sid_anchor not in block:
    raise RuntimeError('V293 share/state session anchor missing')

if providers_line.strip() not in block:
    insertion=profile_line+providers_line+snapshot_line
    block=block.replace(sid_anchor,sid_anchor+insertion,1)
elif snapshot_line.strip() not in block:
    block=block.replace(providers_line,providers_line+snapshot_line,1)

if '"social":social_snapshot' not in block:
    raise RuntimeError('V293 share/state modern social response missing')

s=s[:start]+block+s[end:]
path.write_text(s,encoding='utf-8')
print('V293 share/state resilience applied:',path)
