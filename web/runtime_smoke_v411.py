#!/usr/bin/env python3
"""Essential live surface and CSRF/header checks against the built image."""
import hashlib, json, os, re, urllib.error, urllib.request
from pathlib import Path
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

def dump_generated_creator_hub_state():
    path=Path('/app/web/direct_upload_server.py')
    try:
        source=path.read_text(encoding='utf-8')
        lines=source.splitlines()
        start=source.index('if clean=="/creator-hub/state":')
        end=source.index('if clean=="/account":',start)
        start_line=source.count('\n',0,start)+1
        end_line=source.count('\n',0,end)+1
        print(f'V411 GENERATED CREATOR HUB STATE lines={start_line}-{end_line}',flush=True)
        for number in range(max(1,start_line-8),min(len(lines),end_line+8)+1):
            print(f'{number:05d}: {lines[number-1]}',flush=True)
        matches=[]
        for match in re.finditer(r'bad[ _-]*request',source,flags=re.I):
            line=source.count('\n',0,match.start())+1
            matches.append(line)
        print('V411 GENERATED BAD REQUEST LINES',matches,flush=True)
        for line in matches:
            lo=max(1,line-10); hi=min(len(lines),line+10)
            print(f'V411 GENERATED BAD REQUEST CONTEXT {lo}-{hi}',flush=True)
            for number in range(lo,hi+1):
                print(f'{number:05d}: {lines[number-1]}',flush=True)
    except Exception as exc:
        print('V411 GENERATED SERVER DIAGNOSTIC FAILED',repr(exc),flush=True)

status,headers,body=request('/healthz')
assert status==200 and json.loads(body)['ok'] is True
status,headers,body=request('/',headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/140.0 Safari/537.36'})
assert status==200 and b'Streamlit' in body and b'GSF Mobile Only Gate' not in body
for path,marker in [('/creator-hub-v156/','V403_CREATOR_HUB_SIMPLIFIED'),('/ai-v221/','id="ai404"'),('/editor-live/','V395_MOBILE_EDITOR_ATOMIC_SKIN'),('/share-v156/','V413_CREA_SHORT')]:
    status,headers,body=request(path)
    assert status==200 and marker in body.decode('utf-8'), (path,status)
    assert headers.get('X-Content-Type-Options')=='nosniff', (path,'missing security headers')
mobile_assets=(
    ('/game-editor-mobile/','index.html','text/html',b'id="gameEditorApp"'),
    ('/game-editor-mobile/editor.css','editor.css','text/css',b'.editor-app'),
    ('/game-editor-mobile/editor.mjs','editor.mjs','javascript',b'GSFGameEditor2026'),
    ('/game-editor-mobile/editor_state.mjs','editor_state.mjs','javascript',b'normalizeEditorState'),
)
for url,name,content_type,marker in mobile_assets:
    status,headers,body=request(url)
    expected=(Path('/app/web/game_editor_mobile_component')/name).read_bytes()
    assert status==200 and marker in body, (url,status)
    assert body==expected, (url,'served bytes differ',hashlib.sha256(body).hexdigest(),hashlib.sha256(expected).hexdigest())
    assert content_type in str(headers.get('Content-Type','')).lower(), (url,headers.get('Content-Type'))
    assert headers.get('Cache-Control')=='no-store', (url,'unexpected cache',headers.get('Cache-Control'))
    assert headers.get('X-Content-Type-Options')=='nosniff', (url,'missing nosniff')
    assert headers.get('X-Frame-Options')=='SAMEORIGIN', (url,'missing same-origin framing')
status,headers,body=request('/creator-hub/state')
try:
    identity=json.loads(body)
except Exception:
    identity={}
if status!=200:
    print('V411 CREATOR HUB STATE FAILURE',status,body[:500],COOKIE,flush=True)
    dump_generated_creator_hub_state()
assert status==200, ('creator hub state status',status,body[:500],COOKIE)
assert identity.get('csrf_token'), ('creator hub csrf token missing',identity,COOKIE)
stable_cookie=COOKIE
stable_csrf=identity['csrf_token']
status,_,body=request('/creator-hub/state')
assert status==200 and COOKIE==stable_cookie, ('creator hub session changed',stable_cookie,COOKIE)
assert json.loads(body).get('csrf_token')==stable_csrf, ('creator hub csrf changed for stable session',stable_cookie)
status,_,_=request('/drafts/delete?id=v411-nonexistent')
assert status in (403,405)
status,_,_=request('/drafts/delete?id=v411-nonexistent',method='POST')
assert status==403, ('missing CSRF accepted',status)
status,_,_=request('/drafts/delete?id=v411-nonexistent',method='POST',headers={'X-GSF-CSRF':identity['csrf_token']})
assert status==404, ('authorized non-existing draft must fail safely',status)
# V413 multi-publish: CSRF enforced, invalid share links fail closed.
status,_,_=request('/publish/multi',method='POST')
assert status==403, ('publish without CSRF accepted',status)
status,_,_=request('/share/link',method='POST')
assert status==403, ('share link without CSRF accepted',status)
status,_,body=request('/publish/multi',method='POST',headers={'X-GSF-CSRF':identity['csrf_token'],'Content-Type':'application/json'})
assert status==400 and json.loads(body).get('ok') is False, ('empty publish must be rejected',status,body[:200])
status,_,_=request('/publish/status')
assert status==200, ('publish status',status)
status,headers,_=request('/share/public/not-a-valid-token')
assert status==404 and 'gsf_sid' not in str(headers.get('Set-Cookie','')), ('invalid public share link',status)
# Canonical UI pipeline: mobile Home is served, and the companion still rejects
# requests that bypass the edge session (security must not be weakened).
status,headers,body=request('/')
assert status==200 and b'Streamlit' in body, ('mobile home',status)
try:
    direct=urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8502/creator-hub/state'),timeout=10)
    direct_status=direct.status
except urllib.error.HTTPError as error:
    direct_status=error.code
assert direct_status==400, ('companion accepted a request without edge session id',direct_status)
health=json.loads(request('/healthz')[2])
assert re.fullmatch(r'[0-9a-f]{64}',health.get('ui_digest','')), ('healthz must expose the canonical UI digest',health)
print('V411 essential UI/security runtime smoke: PASS')
