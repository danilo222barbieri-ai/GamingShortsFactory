#!/usr/bin/env python3
"""Essential live surface and CSRF/header checks against the built image."""
import json, os, re, urllib.error, urllib.request
BASE = 'http://127.0.0.1:' + os.environ.get('PORT', '8080')
COOKIE = ''

def request(path, method='GET', headers=None):
    global COOKIE
    h={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) Mobile/15E148 Safari/605.1', **(headers or {})}
    if COOKIE:h['Cookie']=COOKIE
    req=urllib.request.Request(BASE+path,method=method,headers=h,data=b'{}' if method=='POST' else None)
    try:r=urllib.request.urlopen(req,timeout=15)
    except urllib.error.HTTPError as error:r=error
    with r:
        cookie=r.headers.get('Set-Cookie','')
        if 'gsf_sid=' in cookie:COOKIE=re.search(r'gsf_sid=[^;]+',cookie)[0]
        return r.status,r.headers,r.read()

status,headers,body=request('/healthz')
assert status==200 and json.loads(body)['ok'] is True
for path,marker in [('/creator-hub-v156/','V403_CREATOR_HUB_SIMPLIFIED'),('/ai-v221/','id="ai404"'),('/editor-live/','V395_MOBILE_EDITOR_ATOMIC_SKIN'),('/share-v156/','V405_PUBLISH_SHORT_LIVE')]:
    status,headers,body=request(path)
    assert status==200 and marker in body.decode('utf-8'), (path,status)
    assert headers.get('X-Content-Type-Options')=='nosniff', (path,'missing security headers')
status,headers,body=request('/creator-hub/state')
identity=json.loads(body)
assert status==200 and identity.get('csrf_token')
status,_,_=request('/drafts/delete?id=v411-nonexistent')
assert status in (403,405)
status,_,_=request('/drafts/delete?id=v411-nonexistent',method='POST')
assert status==403, ('missing CSRF accepted',status)
status,_,_=request('/drafts/delete?id=v411-nonexistent',method='POST',headers={'X-GSF-CSRF':identity['csrf_token']})
assert status==404, ('authorized non-existing draft must fail safely',status)
print('V411 essential UI/security runtime smoke: PASS')

