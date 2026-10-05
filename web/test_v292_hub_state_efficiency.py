#!/usr/bin/env python3
from pathlib import Path

path=Path('/app/web/direct_upload_server.py')
source=path.read_text(encoding='utf-8')
start=source.find('if clean=="/creator-hub/state":')
end=source.find('if clean=="/share/state":',start)
if start<0 or end<0:
    raise SystemExit('V292 creator-hub/state route not found')
block=source[start:end]

for provider in ('youtube','tiktok','instagram'):
    call=f'_{provider}_user_load(sid)'
    count=block.count(call)
    if count!=1:
        raise SystemExit(f'V292 creator-hub/state repeats {provider} load {count} times')
    cached=f'{provider}_connected=bool({call})'
    if cached not in block:
        raise SystemExit(f'V292 creator-hub/state missing cached {provider} state')

for marker in ('youtube_connected','tiktok_connected','instagram_connected'):
    if block.count(marker)<2:
        raise SystemExit('V292 cached social state is not reused: '+marker)

compile(source,str(path),'exec')
print('V292 creator-hub/state single-load social efficiency: PASS')
