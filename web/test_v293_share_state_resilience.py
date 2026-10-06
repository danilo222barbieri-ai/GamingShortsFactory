#!/usr/bin/env python3
from pathlib import Path
import sys

path=Path(sys.argv[1] if len(sys.argv)>1 else 'web/direct_upload_server.py')
s=path.read_text(encoding='utf-8')
start=s.find('if clean=="/share/state":')
end=s.find('if clean=="/share/final":', start)
if start < 0 or end < 0:
    raise SystemExit('FAIL: share/state handler block missing')
block=s[start:end]
checks=[
    ('share/state loads creator profile', '_creator_account_load(sid)' in block),
    ('share/state defines providers map', 'providers=dict(profile.get("providers") or {})' in block),
    ('facebook state reads defined providers', '"facebook":bool(providers.get("facebook"))' in block),
    ('twitch state reads defined providers', '"twitch":bool(providers.get("twitch"))' in block),
]
for label,ok in checks:
    print(('PASS: ' if ok else 'FAIL: ')+label)
    if not ok:
        raise SystemExit(1)
print('V293 share/state resilience: PASS')
