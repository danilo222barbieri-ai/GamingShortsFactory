#!/usr/bin/env python3
from pathlib import Path
import py_compile
import re
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
SERVER = ROOT / 'web' / 'direct_upload_server.py'
NGINX = ROOT / 'web' / 'nginx.conf.template'
AI = ROOT / 'web' / 'ai_v221_component' / 'index.html'
HOME = ROOT / 'web' / 'home_v154_component' / 'index.html'

SERVER_MARK = '# V319 AI RESULTS BRIDGE'
SERVER_HELPER = r'''
# V319 AI RESULTS BRIDGE
_AI_RESULT_FILE_RE = re.compile(r'(?:^|[_-])(?:mini|candidate|preview)[_-]?([1-3])(?:[^0-9].*)?\.mp4$', re.IGNORECASE)

def _ai_results_payload(sid):
    sid = _safe_id(sid)
    if not sid:
        return {"ok":False,"previews":[],"count":0}
    media_dir = ROOT / "sessions" / sid / "media"
    if not media_dir.is_dir():
        return {"ok":True,"previews":[],"count":0}
    by_index = {}
    for path in media_dir.iterdir():
        if not path.is_file() or path.suffix.lower() != ".mp4":
            continue
        match = _AI_RESULT_FILE_RE.search(path.name)
        if not match:
            continue
        index = int(match.group(1))
        if index < 1 or index > 3:
            continue
        try:
            mtime = float(path.stat().st_mtime)
        except Exception:
            mtime = 0.0
        prev = by_index.get(index)
        if prev is None or mtime >= prev[0]:
            by_index[index] = (mtime, path)
    previews = []
    for index in sorted(by_index):
        mtime, path = by_index[index]
        previews.append({
            "index": index - 1,
            "title": "Momento " + str(index),
            "video": "/media/" + sid + "/media/" + urllib.parse.quote(path.name, safe=""),
            "mtime": mtime,
        })
    return {"ok":True,"previews":previews[:3],"count":min(3,len(previews))}
'''

SERVER_ROUTE = r'''
        # V319 AI RESULTS ROUTE
        if clean=="/ai/results":
            sid=_social_sid(self)
            _json(self,200,_ai_results_payload(sid))
            return
'''

NGINX_MARK = '# V319 AI RESULTS NGINX'
NGINX_BLOCK = r'''
    # V319 AI RESULTS NGINX
    location = /ai/results {
        add_header Set-Cookie "gsf_sid=$gsf_session_cookie; Path=/; Max-Age=31536000; SameSite=Lax; Secure; HttpOnly" always;
        proxy_pass http://127.0.0.1:8502/ai/results$is_args$args;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-GSF-Session-ID $gsf_session_cookie;
        add_header Cache-Control "no-store" always;
    }

'''

AI_STYLE = r'''<style id="v319AiResultsBridgeStyle">
/* V319 AI RESULTS BRIDGE */
@media(max-width:760px){
  #ai221.v319Analyzing .status,
  #ai221.v319ResultError .status{display:block!important}
  #ai221.v319Analyzing .status{color:#2d83c7!important;font-weight:850!important}
  #ai221.v319ResultError .status{color:#9a6a2d!important;font-weight:800!important}
  #ai221.v319Analyzing .create{opacity:.78!important;cursor:wait!important}
}
</style>'''

AI_JS = r'''
 /* V319 AI RESULTS BRIDGE */
 let v319PollToken=0;
 function v319Rows(payload){
   const rows=payload&&Array.isArray(payload.previews)?payload.previews:[];
   return rows.filter(d=>d&&d.video).slice(0,3);
 }
 function v319SetBusy(on,message){
   const root=document.getElementById("ai221");
   if(root){root.classList.toggle("v319Analyzing",!!on);if(on)root.classList.remove("v319ResultError");}
   create.disabled=!!on||!state.loaded;
   create.textContent=on?"ANALISI IN CORSO…":"TROVA I 3 MOMENTI MIGLIORI →";
   if(on&&status){status.textContent=message||"L’IA sta cercando i 3 momenti migliori…";}
 }
 function v319Fail(message){
   const root=document.getElementById("ai221");
   if(root){root.classList.remove("v319Analyzing");root.classList.add("v319ResultError");}
   create.disabled=!state.loaded;
   create.textContent="TROVA I 3 MOMENTI MIGLIORI →";
   if(status)status.textContent=message||"Analisi completata, ma i momenti non sono ancora disponibili. Riprova.";
 }
 async function v319PollResults(token,deadline){
   if(token!==v319PollToken)return;
   try{
     const response=await fetch("/ai/results?_="+Date.now(),{cache:"no-store",credentials:"same-origin"});
     if(response.ok){
       const payload=await response.json();
       const rows=v319Rows(payload);
       if(rows.length){
         state.previews=rows;
         sync();
         if(rows.length>=3||Date.now()>=deadline){
           v319SetBusy(false);
           return;
         }
         v319SetBusy(true,"Trovati "+rows.length+" di 3 momenti…");
       }
     }
   }catch(_e){}
   if(Date.now()>=deadline){v319Fail();return;}
   setTimeout(()=>v319PollResults(token,deadline),900);
 }
 function v319StartAnalysis(){
   if(!state.loaded)return;
   const requestId=Date.now().toString(36)+"-"+Math.random().toString(36).slice(2,9);
   state.previews=[];
   v317SyncResults();
   guide("creating");
   v319SetBusy(true,"L’IA sta cercando i 3 momenti migliori…");
   send("create",{engine:state.engine,duration:state.duration,request_id:requestId});
   const token=++v319PollToken;
   setTimeout(()=>v319PollResults(token,Date.now()+90000),350);
 }
'''

CREATE_OLD = 'create.addEventListener("click",()=>{if(!state.loaded)return;guide("creating");status.textContent="L’IA sta cercando i momenti migliori…";send("create",{engine:state.engine,duration:state.duration})});'
CREATE_NEW = 'create.addEventListener("click",v319StartAnalysis);'

HOME_OLD = 'value({event:"create_ai",duration,engine:nextEngine});'
HOME_NEW = 'value({event:"create_ai",duration,engine:nextEngine,request_id:String(e.data.request_id||Date.now())}); /* V319 CREATE NONCE */'


def patch_server_text(text: str) -> str:
    if SERVER_MARK in text and '# V319 AI RESULTS ROUTE' in text:
        return text
    helper_anchor = 'class Handler(BaseHTTPRequestHandler):'
    if helper_anchor not in text:
        raise RuntimeError('V319 direct server Handler anchor missing')
    out = text.replace(helper_anchor, SERVER_HELPER + '\n' + helper_anchor, 1)
    route_anchor = '        if clean in ("","/health"):'
    if route_anchor not in out:
        raise RuntimeError('V319 direct server GET anchor missing')
    out = out.replace(route_anchor, SERVER_ROUTE + '\n' + route_anchor, 1)
    return out


def patch_nginx_text(text: str) -> str:
    if NGINX_MARK in text:
        return text
    anchor = '    # V221 living AI engines surface.'
    if anchor not in text:
        raise RuntimeError('V319 nginx AI anchor missing')
    return text.replace(anchor, NGINX_BLOCK + anchor, 1)


def patch_ai_text(text: str) -> str:
    if 'id="v319AiResultsBridgeStyle"' in text and 'function v319StartAnalysis()' in text and CREATE_NEW in text:
        return text
    if '</head>' not in text:
        raise RuntimeError('V319 AI </head> anchor missing')
    if 'v317SyncResults();' not in text:
        raise RuntimeError('V319 requires V317 compact AI flow')
    if CREATE_OLD not in text:
        raise RuntimeError('V319 AI create handler anchor missing')
    out = text.replace('</head>', AI_STYLE + '\n</head>', 1)
    out = out.replace(CREATE_OLD, AI_JS + '\n ' + CREATE_NEW, 1)
    return out


def patch_home_text(text: str) -> str:
    if 'V319 CREATE NONCE' in text:
        return text
    if HOME_OLD not in text:
        raise RuntimeError('V319 Home V291 create bridge anchor missing')
    return text.replace(HOME_OLD, HOME_NEW, 1)


def _write(path: Path, patcher, label: str) -> None:
    if not path.is_file():
        raise RuntimeError('V319 missing '+label+': '+str(path))
    before=path.read_text(encoding='utf-8')
    after=patcher(before)
    path.write_text(after,encoding='utf-8')
    print('V319 '+label+' applied changed=',before!=after,flush=True)


def main() -> None:
    _write(SERVER,patch_server_text,'AI results endpoint')
    _write(NGINX,patch_nginx_text,'nginx AI results route')
    _write(AI,patch_ai_text,'AI create/result UI bridge')
    _write(HOME,patch_home_text,'Home create nonce bridge')
    py_compile.compile(str(SERVER),doraise=True)
    print('V319 AI create/results bridge: PASS',flush=True)


if __name__=='__main__':
    main()
