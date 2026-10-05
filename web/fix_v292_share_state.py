#!/usr/bin/env python3
from pathlib import Path
import sys

MARKER='GSF_V292_SHARE_STATE_PROVIDER_FIX'

def main():
    target=Path(sys.argv[1] if len(sys.argv)>1 else '/app/web/direct_upload_server.py')
    if not target.exists():
        local=Path(__file__).with_name('direct_upload_server.py')
        target=local if local.exists() else target
    source=target.read_text(encoding='utf-8')
    if MARKER in source:
        print('V292 share/state fix already applied:',target)
        return

    old='''        if clean=="/share/state":\n            sid=_social_sid(self)\n            if not sid:\n                _json(self,400,{"ok":False,"error":"Sessione browser non valida."})\n                return\n            stable,_job=_final_local_paths(sid)\n'''
    new='''        if clean=="/share/state":\n            # GSF_V292_SHARE_STATE_PROVIDER_FIX\n            sid=_social_sid(self)\n            if not sid:\n                _json(self,400,{"ok":False,"error":"Sessione browser non valida."})\n                return\n            profile=_creator_account_load(sid) or {}\n            providers=dict(profile.get("providers") or {}) if isinstance(profile,dict) else {}\n            stable,_job=_final_local_paths(sid)\n'''
    if old not in source:
        raise SystemExit('V292 share/state patch anchor missing')
    source=source.replace(old,new,1)
    compile(source,str(target),'exec')
    target.write_text(source,encoding='utf-8')
    print('V292 share/state provider fix applied:',target)

if __name__=='__main__':
    main()
