#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARKER='GSF_V292_HUB_STATE_SINGLE_SOCIAL_LOAD'
ROUTE_RE=re.compile(r'^        if (?:clean|path)==["\']/[^"\']+["\']:',re.M)


def route_block(source,route):
    needle=f'        if clean=="{route}":'
    start=source.find(needle)
    if start<0:
        return -1,-1,''
    nxt=ROUTE_RE.search(source,start+len(needle))
    end=nxt.start() if nxt else len(source)
    return start,end,source[start:end]


def main():
    target=Path(sys.argv[1] if len(sys.argv)>1 else '/app/web/direct_upload_server.py')
    if not target.exists():
        local=Path(__file__).with_name('direct_upload_server.py')
        target=local if local.exists() else target
    source=target.read_text(encoding='utf-8')
    if MARKER in source:
        print('V292 hub-state efficiency already applied:',target)
        return

    start,end,block=route_block(source,'/creator-hub/state')
    if start<0 or end<=start:
        raise SystemExit('V292 hub-state route anchor missing')

    for provider in ('youtube','tiktok','instagram'):
        old=f'bool(_{provider}_user_load(sid))'
        if block.count(old)<1:
            raise SystemExit('V292 hub-state loader anchor missing: '+provider)
        block=block.replace(old,f'{provider}_connected')

    social_anchor='            social={\n'
    if social_anchor not in block:
        raise SystemExit('V292 hub-state social mapping anchor missing')
    cached=(
        '            # GSF_V292_HUB_STATE_SINGLE_SOCIAL_LOAD\n'
        '            youtube_connected=bool(_youtube_user_load(sid))\n'
        '            tiktok_connected=bool(_tiktok_user_load(sid))\n'
        '            instagram_connected=bool(_instagram_user_load(sid))\n'
    )
    block=block.replace(social_anchor,cached+social_anchor,1)
    source=source[:start]+block+source[end:]
    compile(source,str(target),'exec')
    target.write_text(source,encoding='utf-8')
    print('V292 hub-state single-load optimization applied:',target)

if __name__=='__main__':
    main()
