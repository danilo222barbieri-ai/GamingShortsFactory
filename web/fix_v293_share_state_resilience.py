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
marker='providers=dict(profile.get("providers") or {}) if isinstance(profile,dict) else {}'
if marker in block:
    print('V293 share/state resilience already applied:',path)
    raise SystemExit(0)
old='''        if clean=="/share/state":\n            sid=_social_sid(self)\n            if not sid:\n                _json(self,400,{"ok":False,"error":"Sessione browser non valida."})\n                return\n            stable,_job=_final_local_paths(sid)\n'''
new='''        if clean=="/share/state":\n            sid=_social_sid(self)\n            if not sid:\n                _json(self,400,{"ok":False,"error":"Sessione browser non valida."})\n                return\n            profile=_creator_account_load(sid) or {}\n            providers=dict(profile.get("providers") or {}) if isinstance(profile,dict) else {}\n            stable,_job=_final_local_paths(sid)\n'''
if old not in s:
    raise RuntimeError('V293 share/state anchor missing')
s=s.replace(old,new,1)
path.write_text(s,encoding='utf-8')
print('V293 share/state resilience applied:',path)
