#!/usr/bin/env python3
"""V403 final runtime migration.

Applied after historical migrations. V343 remains the only global chrome owner;
this module only wires durable project flow and bounded functional surfaces.
"""
from __future__ import annotations

from pathlib import Path
import py_compile
import re
import sys

MARK = "V403_APP_STABILITY_FLOW"
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path("/app")
APP = ROOT / "GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py"
SERVER = ROOT / "web" / "direct_upload_server.py"
NGINX = ROOT / "web" / "nginx.conf.template"
AI = ROOT / "web" / "ai_v221_component" / "index.html"
SHARE = ROOT / "web" / "share_v156_component" / "index.html"


SERVER_HELPERS = r'''
# V403_PROJECT_FLOW
from app_flow_v403 import new_snapshot as _v403_new_snapshot, transition as _v403_transition, reconcile_snapshot as _v403_reconcile_snapshot
_V403_FLOW_LOCK=threading.Lock()

def _v403_flow_path(sid):
    sid=_safe_id(sid)
    if not sid:return None
    root=ROOT/"sessions"/sid;root.mkdir(parents=True,exist_ok=True)
    return root/"project_flow_v403.json"

def _v403_flow_bucket_key(sid,state=None):
    sid=_safe_id(sid)
    if not sid:return ""
    account=""
    try:account=_safe_id((_creator_account_load(sid) or {}).get("account_id",""))
    except Exception:pass
    project=_safe_id((state or {}).get("project_id",""))
    if account and project:return f"creator-accounts/{account}/projects/{project}/flow_v403.json"
    return f"session-flow/{sid}/v403.json"

def _v403_source_ref(sid):
    sid=_safe_id(sid)
    if not sid:return ""
    marker=ROOT/"sessions"/sid/"media"/".direct_upload_ready.json"
    try:
        data=json.loads(marker.read_text(encoding="utf-8"))
        if not isinstance(data,dict):return ""
        raw=str(data.get("path") or "")
        if raw:
            name=Path(raw).name
            if name:return f"/media/{sid}/media/{urllib.parse.quote(name,safe='')}"
        key=str(data.get("bucket_key") or "")
        return ("bucket://"+key) if key else ""
    except Exception:return ""

def _v403_profile_payload(sid):
    try:
        p=_creator_account_load(sid) or {}
        if not isinstance(p,dict) or not p:return None
        return {"name":str(p.get("display_name") or p.get("nickname") or "Creator")[:120],"avatar":str(p.get("avatar") or "")[:1800000],"plan":str(p.get("plan") or "FREE")[:24],"account_id":str(p.get("account_id") or "")[:80],"version":int(float(p.get("updated_at") or 0))}
    except Exception:return None

def _v403_flow_load(sid):
    sid=_safe_id(sid)
    if not sid:return _v403_new_snapshot()
    path=_v403_flow_path(sid);data={}
    with _V403_FLOW_LOCK:
        try:
            if path and path.is_file():data=json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data,dict):data={}
        except Exception:data={}
        if not data and _bucket_enabled():
            try:
                seed=_v403_new_snapshot(project_id="p_"+sid,source_video_ref=_v403_source_ref(sid))
                obj=_s3().get_object(Bucket=S3_BUCKET,Key=_v403_flow_bucket_key(sid,seed));data=json.loads(obj["Body"].read().decode("utf-8"))
            except Exception:data={}
        if not isinstance(data,dict) or int(data.get("schema_version",0) or 0)!=403:data=_v403_new_snapshot(project_id="p_"+sid,source_video_ref=_v403_source_ref(sid))
        source=_v403_source_ref(sid)
        if source and not data.get("source_ready"):data=_v403_transition(data,"source_ready",{"source_video_ref":source})
        profile=_v403_profile_payload(sid)
        if profile:data=_v403_transition(data,"profile_valid",profile)
        try:
            stable,job=_final_local_paths(sid);render_doc={}
            if job and job.is_file():
                raw=json.loads(job.read_text(encoding="utf-8"));render_doc=raw if isinstance(raw,dict) else {}
            if stable and stable.is_file() and stable.stat().st_size>1024:
                data=_v403_transition(data,"render_completed",{"job_id":str(render_doc.get("job_id") or render_doc.get("pid") or (data.get("render") or {}).get("job_id") or "render"),"asset_ref":"/share/final"})
            elif str(render_doc.get("status") or "")=="running" and data.get("selected_candidate_id"):
                data=_v403_transition(data,"render_started",{"job_id":str(render_doc.get("job_id") or render_doc.get("pid") or "render-active"),"progress":float(render_doc.get("progress") or 0)})
            elif str(render_doc.get("status") or "")=="failed":data=_v403_transition(data,"render_failed",{"error":str(render_doc.get("error") or "Render non riuscito")[:180]})
        except Exception:pass
        if path:
            try:_write_json_atomic(path,data)
            except Exception:pass
    return data

def _v403_flow_save(sid,snapshot):
    sid=_safe_id(sid)
    if not sid:return snapshot
    path=_v403_flow_path(sid)
    with _V403_FLOW_LOCK:
        if path:_write_json_atomic(path,snapshot)
        if _bucket_enabled():
            try:_s3().put_object(Bucket=S3_BUCKET,Key=_v403_flow_bucket_key(sid,snapshot),Body=json.dumps(snapshot,ensure_ascii=False,separators=(",",":")).encode("utf-8"),ContentType="application/json",CacheControl="no-store")
            except Exception as exc:print("GSF_V403_FLOW_BUCKET_WARN",sid,repr(str(exc))[:180],flush=True)
    return snapshot

def _v403_flow_event(sid,event,payload=None):
    current=_v403_flow_load(sid)
    updated=_v403_transition(current,event,payload if isinstance(payload,dict) else {})
    return _v403_flow_save(sid,updated)

def _v403_candidates(rows):
    out=[]
    for i,row in enumerate((rows or [])[:3]):
        if not isinstance(row,dict):continue
        try:start=float(row.get("start_seconds") or row.get("start") or 0.0)
        except Exception:start=0.0
        try:end=float(row.get("end_seconds") or row.get("end") or 0.0)
        except Exception:end=0.0
        try:duration=float(row.get("duration") or row.get("duration_seconds") or 0.0)
        except Exception:duration=0.0
        if end<=start and duration>0:end=start+duration
        out.append({"id":str(row.get("id") or row.get("candidate_id") or f"m{i}"),"rank":i+1,"start_seconds":max(0.0,start),"end_seconds":max(start,end),"event":str(row.get("event") or row.get("title") or f"Momento {i+1}")[:80],"confidence":float(row.get("confidence") or 0.0),"score":float(row.get("score") or 0.0),"reason":str(row.get("reason") or "")[:480],"fusion_reason":str(row.get("fusion_reason") or row.get("reason") or "Momento selezionato dal Game Brain")[:480],"fusion_signals":row.get("fusion_signals") if isinstance(row.get("fusion_signals"),list) else [],"preview_ref":str(row.get("preview_ref") or row.get("video") or "")[:1024],"thumbnail_ref":str(row.get("thumbnail_ref") or row.get("cover") or "")[:1024],"subtitles_available":bool(row.get("subtitles_available") or row.get("subtitles"))})
    return out
'''

SERVER_GET = r'''
        # V403_PROJECT_FLOW GET
        if clean=="/project/flow":
            sid=_social_sid(self)
            if not sid:_json(self,400,{"ok":False,"error":"invalid session"});return
            snap=_v403_reconcile_snapshot(_v403_flow_load(sid),_v403_flow_load(sid))
            _json(self,200,{"ok":True,"snapshot":snap})
            return
'''

SERVER_POST = r'''
        # V403_PROJECT_FLOW POST
        if path=="/project/flow":
            try:
                data=_read_json(self,max_bytes=256*1024);event=str((data or {}).get("event") or "")[:80];payload=(data or {}).get("payload") if isinstance((data or {}).get("payload"),dict) else {}
                if event=="analysis_completed" and isinstance(payload.get("candidates"),list):payload=dict(payload,candidates=_v403_candidates(payload.get("candidates")))
                _json(self,200,{"ok":True,"snapshot":_v403_flow_event(sid,event,payload)})
            except Exception as exc:_json(self,400,{"ok":False,"error":str(exc)[:220]})
            return
'''

NGINX_BLOCK = r'''
    # V403_APP_STABILITY_FLOW
    location = /moments-v403 { return 302 /moments-v403/; }
    location /moments-v403/ {
        alias /app/web/moments_v403_component/;
        index index.html;
        try_files $uri $uri/ /moments-v403/index.html;
        add_header Cache-Control "no-store" always;
    }
    location = /project/flow {
        add_header Set-Cookie "gsf_sid=$gsf_session_cookie; Path=/; Max-Age=31536000; SameSite=Lax; Secure; HttpOnly" always;
        proxy_pass http://127.0.0.1:8502/project/flow$is_args$args;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_set_header Host $host;
        proxy_set_header X-GSF-Session-ID $gsf_session_cookie;
        proxy_set_header Content-Type $content_type;
        add_header Cache-Control "no-store" always;
    }

'''

AI_RUNTIME = r'''
<style id="v403MotoriOnly">/* V403_APP_STABILITY_FLOW */#ai221{overflow-y:auto!important}#ai221>.panel:first-of-type{margin-bottom:0!important}</style>
<script id="v403MotoriRuntime">
(()=>{
 if(window.__GSF_V403_MOTORI)return;window.__GSF_V403_MOTORI=true;
 let job='',last='';
 const flow=async(event,payload={})=>{try{const r=await fetch('/project/flow',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json'},body:JSON.stringify({event,payload})});return r.ok?await r.json():null}catch(_e){return null}};
 const start=()=>{if(typeof state==='undefined'||!state.loaded)return;job='analysis-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8);flow('analysis_started',{job_id:job,engine:state.engine||'auto',duration:Number(state.duration)===30?30:15})};
 document.getElementById('createAi')?.addEventListener('click',start,true);
 window.addEventListener('message',e=>{if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_AI_STATE')return;const rows=Array.isArray(e.data.state?.previews)?e.data.state.previews.filter(Boolean).slice(0,3):[];if(!rows.length)return;const sig=rows.map((r,i)=>String(r.id||r.video||r.cover||i)+':'+String(r.start_seconds??r.start??'')).join('|');if(sig===last)return;last=sig;flow('analysis_completed',{job_id:job||'analysis-ready',candidates:rows}).finally(()=>{parent.postMessage({type:'GSF_V403_ANALYSIS_COMPLETE',count:rows.length},location.origin);parent.postMessage({type:'GSF_V403_OPEN_MOMENTS'},location.origin)})});
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)parent.postMessage({type:'GSF_V403_RECONCILE'},location.origin)});
})();
</script>
'''

SHARE_RUNTIME = r'''
<style id="v403UnifiedCreateShortStyle">
#v403CreateShortPre{display:none}#share.v403PreRender>:not(#v403CreateShortPre){display:none!important}#share.v403PreRender #v403CreateShortPre{display:grid!important}#share.v403Ready #v403CreateShortPre{display:none!important}#v403CreateShortPre{min-height:100%;grid-template-columns:minmax(210px,34%) minmax(0,1fr);gap:14px;align-items:center;max-width:1060px;margin:0 auto;padding:12px}.v403Preview{aspect-ratio:9/16;max-height:70vh;border-radius:24px;overflow:hidden;background:#071526}.v403Preview video{width:100%;height:100%;object-fit:cover}.v403PreInfo{padding:20px;border:1px solid rgba(130,174,211,.28);border-radius:25px;background:rgba(255,255,255,.9)}.v403PreInfo h1{font-size:clamp(26px,4vw,42px)!important;margin:0 0 7px}.v403PreInfo p{color:#7084a0}.v403SelectedMeta{margin:13px 0;padding:11px;border-radius:15px;background:#eef8ff;color:#335f86;font-size:11px;font-weight:800}.v403PreActions{display:grid;grid-template-columns:1fr 1fr;gap:8px}.v403PreActions button{border:0;border-radius:15px;min-height:46px;font-weight:950;cursor:pointer}.v403Create{grid-column:1/-1;background:linear-gradient(135deg,#70cff7,#4da8f3);color:#fff}.v403Edit{background:#dff5ea;color:#25775d}.v403Draft{background:#eef4f8;color:#58718a}.v403Back{grid-column:1/-1;background:#f6f8fb;color:#58718a}.v403RenderStatus{margin-top:10px;color:#5d7c98;font-size:10px;font-weight:800}[data-v403-state="ready"]{display:none}
@media(max-width:760px){#v403CreateShortPre{grid-template-columns:1fr;align-content:start;padding:8px 8px 18px}.v403Preview{width:min(52vw,205px);max-height:42vh;margin:0 auto;border-radius:19px}.v403PreInfo{padding:13px}.v403PreActions{grid-template-columns:1fr}.v403Create,.v403Back{grid-column:auto}}
</style>
<div data-v403-state="ready" aria-hidden="true"></div>
<script id="v403UnifiedCreateShortRuntime">
(()=>{
 if(window.__GSF_V403_SHORT)return;window.__GSF_V403_SHORT=true;const share=document.getElementById('share');if(!share)return;
 const pre=document.createElement('section');pre.id='v403CreateShortPre';pre.setAttribute('data-v403-state','pre-render');pre.innerHTML=`<div class="v403Preview"><video id="v403SelectedVideo" controls playsinline preload="metadata"></video></div><div class="v403PreInfo"><h1>Crea il tuo Short</h1><p>La tua scelta è salvata. Puoi creare il video finale o modificarlo prima nel Game Editor.</p><div class="v403SelectedMeta" id="v403SelectedMeta">Recupero il momento selezionato…</div><div class="v403PreActions"><button class="v403Create" id="v403CreateFinal">CREA SHORT</button><button class="v403Edit" id="v403EditFinal">MODIFICA NEL GAME EDITOR</button><button class="v403Draft" id="v403SaveDraft">SALVA BOZZA</button><button class="v403Back" id="v403BackMoments">SCEGLI UN ALTRO MOMENTO</button></div><div class="v403RenderStatus" id="v403RenderStatus"></div></div>`;share.prepend(pre);
 let snap=null,timer=0;const post=(type,extra={})=>parent.postMessage({type,...extra},location.origin);const selected=()=>Array.isArray(snap?.candidates)?snap.candidates.find(x=>x&&x.id===snap.selected_candidate_id)||null:null;
 const flow=async(event,payload={})=>{try{const r=await fetch('/project/flow',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json'},body:JSON.stringify({event,payload})}),j=await r.json();if(j?.snapshot){snap=j.snapshot;sync()}return snap}catch(_e){return snap}};
 function sync(){const row=selected(),ready=!!(snap?.render?.status==='ready'&&snap?.final_asset_ref);share.classList.toggle('v403PreRender',!ready);share.classList.toggle('v403Ready',ready);share.setAttribute('data-v403-state',ready?'ready':'pre-render');const meta=document.getElementById('v403SelectedMeta'),video=document.getElementById('v403SelectedVideo'),status=document.getElementById('v403RenderStatus');if(!row){document.getElementById('v403CreateFinal').disabled=true;if(meta)meta.textContent='Nessun momento selezionato.';if(status)status.textContent='Torna ai momenti e scegline uno.';return}document.getElementById('v403CreateFinal').disabled=false;if(meta)meta.textContent=`${row.event||'Momento'} · ${Math.max(1,Math.round(Number(row.end_seconds||0)-Number(row.start_seconds||0)))}s`;const src=String(row.preview_ref||'');if(src&&video.getAttribute('src')!==src){video.src=src;video.load()}if(status)status.textContent=snap?.render?.status==='running'?'Creazione Short in corso… puoi cambiare pagina.':snap?.render?.status==='error'?(snap.render.error||'Creazione non riuscita. Puoi riprovare.'):'Pronto per creare.';if(ready&&typeof load==='function')load()}
 async function refresh(){try{const r=await fetch('/project/flow?_='+Date.now(),{credentials:'same-origin',cache:'no-store'}),j=await r.json();if(j?.snapshot){snap=j.snapshot}if(snap?.render?.status==='running'){try{const rs=await fetch('/share/state?_='+Date.now(),{credentials:'same-origin',cache:'no-store'}),sj=await rs.json();if(sj?.ready){snap=await flow('render_completed',{job_id:String(snap.render.job_id||''),asset_ref:String(sj.video_url||'/share/final')})||snap}}catch(_e){}}sync()}catch(_e){}}
 function poll(){clearTimeout(timer);timer=setTimeout(async()=>{await refresh();if(snap?.render?.status==='running')poll()},1000)}
 document.getElementById('v403CreateFinal').onclick=async()=>{if(!selected())return;if(snap?.render?.status==='running'){poll();return}const job='render-'+Date.now().toString(36);await flow('render_started',{job_id:job});post('GSF_V403_RENDER_REQUEST',{job_id:job,candidate_id:snap.selected_candidate_id});poll()};document.getElementById('v403EditFinal').onclick=()=>{if(selected())post('GSF_V403_OPEN_EDITOR',{candidate_id:snap.selected_candidate_id})};document.getElementById('v403SaveDraft').onclick=async()=>{try{await fetch('/drafts/save-current',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:'{}'});document.getElementById('v403RenderStatus').textContent='Bozza salvata.'}catch(_e){document.getElementById('v403RenderStatus').textContent='Bozza non salvata.'}};document.getElementById('v403BackMoments').onclick=()=>post('GSF_V403_OPEN_MOMENTS');
 window.addEventListener('message',e=>{if(e.origin===location.origin&&e.data?.type==='GSF_V403_FLOW_STATE'&&e.data.snapshot){snap=e.data.snapshot;sync()}});document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh()});window.addEventListener('pageshow',refresh);refresh();
})();
</script>
'''

APP_RUNTIME = r'''
# V403_APP_STABILITY_FLOW — final browser owner for durable Motori -> Moments -> Editor -> Crea Short routing.
if GSF_WEB_MODE:
    st.html(r"""
    <div style="display:none!important"><script>
    ((P)=>{
      if(P.__GSF_V403_FLOW)return;P.__GSF_V403_FLOW=true;const D=P.document;let refreshPromise=null;
      const ensureStyle=()=>{if(D.getElementById('gsf-v403-shell-style'))return;const s=D.createElement('style');s.id='gsf-v403-shell-style';s.textContent=`.gsfV403Surface{position:fixed;left:0;right:0;top:64px;bottom:58px;z-index:7000;opacity:0;visibility:hidden;pointer-events:none;background:#f8fcff}.gsfV403Surface.is-open{opacity:1;visibility:visible;pointer-events:auto}.gsfV403Surface iframe{width:100%;height:100%;border:0;background:transparent}@media(max-width:760px){.gsfV403Surface{top:58px;bottom:70px}}`;D.head.appendChild(s)};
      const hide=id=>{const o=D.getElementById(id);if(o){o.classList.remove('is-open');o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none'}};const closeV403=()=>{hide('gsf-moments-overlay-v403');hide('gsf-short-overlay-v403')};
      const surface=(id,src,title)=>{ensureStyle();let o=D.getElementById(id);if(!o){o=D.createElement('section');o.id=id;o.className='gsfV403Surface';o.innerHTML=`<iframe title="${title}" src="${src}" allow="fullscreen; autoplay; clipboard-write"></iframe>`;D.body.appendChild(o)}return o};const open=(id,src,title)=>{const o=surface(id,src,title);if(id!=='gsf-moments-overlay-v403')hide('gsf-moments-overlay-v403');if(id!=='gsf-short-overlay-v403')hide('gsf-short-overlay-v403');o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';return o};
      const flow=async(event,payload={})=>{try{const r=await P.fetch('/project/flow',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json'},body:JSON.stringify({event,payload})});return r.ok?await r.json():null}catch(_e){return null}};const get=async()=>{try{const r=await P.fetch('/project/flow?_='+Date.now(),{credentials:'same-origin',cache:'no-store'});return r.ok?await r.json():null}catch(_e){return null}};
      const broadcast=async()=>{const j=await get();if(!j?.snapshot)return null;for(const id of ['gsf-moments-overlay-v403','gsf-short-overlay-v403']){const f=D.getElementById(id)?.querySelector('iframe');try{f?.contentWindow?.postMessage({type:'GSF_V403_FLOW_STATE',snapshot:j.snapshot},P.location.origin)}catch(_e){}}return j.snapshot};const openMoments=async()=>{await flow('route',{route:'moments'});open('gsf-moments-overlay-v403','/moments-v403/?v=403','I tuoi 3 momenti');broadcast()};const openShort=async()=>{await flow('route',{route:'create_short'});hide('gsf-short-overlay-v331');open('gsf-short-overlay-v403','/share-v156/?v=403','Crea Short');broadcast()};const openEditor=async()=>{await flow('route',{route:'editor'});closeV403();P.postMessage({type:'GSF_SHELL_NAV',target:'editor',source:'v403'},P.location.origin)};
      const clickRender=()=>{const nodes=[...D.querySelectorAll('button,a,[role=button]')].filter(x=>!x.closest('#gsf-short-overlay-v403'));for(const q of ['crea short finale','crea il tuo short','crea short','genera short']){const n=nodes.find(x=>(x.innerText||x.textContent||'').toLowerCase().includes(q));if(n){n.click();return true}}return false};
      async function reconcile(reason){if(refreshPromise)return refreshPromise;refreshPromise=(async()=>{try{const snap=await broadcast();const route=String(snap?.route||'');if(route==='moments')open('gsf-moments-overlay-v403','/moments-v403/?v=403','I tuoi 3 momenti');else if(route==='create_short')open('gsf-short-overlay-v403','/share-v156/?v=403','Crea Short');P.postMessage({type:'GSF_V403_FLOW_STATE',snapshot:snap,reason},P.location.origin)}finally{refreshPromise=null}})();return refreshPromise}
      P.addEventListener('message',async e=>{if(e.origin!==P.location.origin||!e.data)return;const t=String(e.data.type||'');if(t==='GSF_V403_OPEN_MOMENTS'||t==='GSF_V403_ANALYSIS_COMPLETE'){openMoments();return}if(t==='GSF_V403_OPEN_SHORT'){if(e.data.candidate_id)await flow('candidate_selected',{candidate_id:String(e.data.candidate_id)});openShort();return}if(t==='GSF_V403_OPEN_EDITOR'){if(e.data.candidate_id)await flow('candidate_selected',{candidate_id:String(e.data.candidate_id)});openEditor();return}if(t==='GSF_V403_RENDER_REQUEST'){setTimeout(clickRender,40);return}if(t==='GSF_V403_RECONCILE'){reconcile('component');return}if(t==='GSF_SHELL_NAV'&&e.data.source!=='v403'){const target=String(e.data.target||'').toLowerCase();if(target==='short'||target==='create_short'){setTimeout(openShort,0);return}if(target==='moments'){setTimeout(openMoments,0);return}if(['home','hub','projects','drafts','live','ai','motori'].includes(target)){closeV403();flow('route',{route:target==='ai'?'motori':target})}}},true);D.addEventListener('visibilitychange',()=>{if(!D.hidden)reconcile('visibilitychange')});P.addEventListener('pageshow',()=>reconcile('pageshow'));setTimeout(()=>reconcile('boot'),350);
    })(window.parent);
    </script></div>
    """,height=0)
'''


def patch_server_text(text: str) -> str:
    if "# V403_PROJECT_FLOW\nfrom app_flow_v403" not in text:
        anchor="class Handler(BaseHTTPRequestHandler):"
        if anchor not in text:raise RuntimeError("V403 server Handler anchor missing")
        text=text.replace(anchor,SERVER_HELPERS+"\n\n"+anchor,1)
    if "# V403_PROJECT_FLOW GET" not in text:
        anchor='        if clean=="/source/restore":'
        if anchor not in text:anchor='        if clean=="/account":'
        if anchor not in text:raise RuntimeError("V403 server GET anchor missing")
        text=text.replace(anchor,SERVER_GET+"\n"+anchor,1)
    if "# V403_PROJECT_FLOW POST" not in text:
        anchor='        if path=="/editor/state/save":'
        if anchor not in text:raise RuntimeError("V403 server POST anchor missing")
        text=text.replace(anchor,SERVER_POST+"\n"+anchor,1)
    return text


def patch_nginx_text(text: str) -> str:
    if "# V403_APP_STABILITY_FLOW" in text:return text
    anchor="    # V221 living AI engines surface."
    if anchor not in text:anchor="    # V220 persistent Game Editor surface."
    if anchor not in text:raise RuntimeError("V403 nginx anchor missing")
    return text.replace(anchor,NGINX_BLOCK+anchor,1)


def patch_ai_text(text: str) -> str:
    if 'id="v403MotoriRuntime"' in text:return text
    panel=re.compile(r'\n\s*<section class="panel">\s*<div class="panelHead"><div class="panelTitle">Le tue 3 migliori giocate</div>.*?</section>',re.DOTALL)
    text,n=panel.subn("",text,count=1)
    if not n and ('class="moments"' in text or 'class="moment"' in text):raise RuntimeError("V403 Motori results panel anchor missing")
    text=re.sub(r'\n\s*function renderMoments\(\)\{.*?\n\s*\}\n\s*function sync\(\)\{','\n function sync(){',text,count=1,flags=re.DOTALL)
    text=text.replace(';renderMoments();',';')
    text=re.sub(r'\n\s*document\.querySelectorAll\("\.moment"\)\.forEach\(card=>card\.addEventListener\("click",.*?\);','',text,count=1)
    if "</head>" not in text:raise RuntimeError("V403 Motori head anchor missing")
    text=text.replace("</head>",AI_RUNTIME.split('<script',1)[0]+"</head>",1)
    script='<script'+AI_RUNTIME.split('<script',1)[1]
    anchor=' send("ready");'
    if anchor not in text:raise RuntimeError("V403 Motori ready anchor missing")
    text=text.replace(anchor,script+"\n"+anchor,1)
    return text


def patch_share_text(text: str) -> str:
    if 'id="v403UnifiedCreateShortRuntime"' in text:return text
    if "</body>" not in text:raise RuntimeError("V403 Share body anchor missing")
    return text.replace("</body>",SHARE_RUNTIME+"\n</body>",1)


def patch_app_text(text: str) -> str:
    if "# V403_APP_STABILITY_FLOW — final browser owner" in text:return text
    out=text.rstrip()+"\n\n"+APP_RUNTIME+"\n";compile(out,str(APP),"exec");return out


def _write(path: Path,patcher,label: str) -> None:
    if not path.is_file():raise RuntimeError(f"V403 missing {label}: {path}")
    before=path.read_text(encoding="utf-8");after=patcher(before);path.write_text(after,encoding="utf-8");print(f"V403 {label} changed={before!=after}",flush=True)


def main() -> None:
    _write(SERVER,patch_server_text,"project flow API");_write(NGINX,patch_nginx_text,"nginx routes");_write(AI,patch_ai_text,"Motori analysis-only");_write(SHARE,patch_share_text,"unified Crea Short");_write(APP,patch_app_text,"runtime bridge")
    py_compile.compile(str(SERVER),doraise=True);py_compile.compile(str(APP),doraise=True);print("V403 APP STABILITY FLOW MIGRATION: PASS",flush=True)


if __name__=="__main__":main()
