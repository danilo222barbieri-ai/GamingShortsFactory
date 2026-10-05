#!/usr/bin/env python3
from pathlib import Path

path=Path('/app/web/direct_upload_server.py')
source=path.read_text(encoding='utf-8')
start=source.find('if clean=="/share/state":')
end=source.find('if clean=="/share/final":',start)
if start<0 or end<0:
    raise SystemExit('V292 share/state route not found')
block=source[start:end]

required=(
    'profile=_creator_account_load(sid) or {}',
    'providers=dict(profile.get("providers") or {}) if isinstance(profile,dict) else {}',
    '"facebook":bool(providers.get("facebook"))',
    '"twitch":bool(providers.get("twitch"))',
)
for marker in required:
    if marker not in block:
        raise SystemExit('V292 share/state regression: missing '+marker)

# Ensure provider state is initialized before the response tries to use it.
profile_pos=block.find('profile=_creator_account_load(sid) or {}')
providers_pos=block.find('providers=dict(profile.get("providers") or {})')
facebook_pos=block.find('"facebook":bool(providers.get("facebook"))')
if not (0 <= profile_pos < providers_pos < facebook_pos):
    raise SystemExit('V292 share/state provider initialization order is unsafe')

compile(source,str(path),'exec')
print('V292 share/state empty-session/provider-state regression: PASS')
