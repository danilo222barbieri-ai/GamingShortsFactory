#!/usr/bin/env python3
"""V403 final runtime migration.

Runs after historical V319/V320/V396 compatibility gates. It patches the
materialized production app and browser surfaces last, so old boot contracts
stay valid while the visible runtime uses the V403 durable flow.
"""
from __future__ import annotations

from pathlib import Path
import py_compile
import sys

MARK = "V403_APP_STABILITY_FLOW"
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path("/app")
APP = ROOT / "GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py"
SERVER = ROOT / "web/direct_upload_server.py"
NGINX = ROOT / "web/nginx.conf.template"
AI = ROOT / "web/ai_v221_component/index.html"
SHARE = ROOT / "web/share_v156_component/index.html"

SERVER_HELPERS = r'''
# V403_APP_STABILITY_FLOW
from app_flow_v403 import new_snapshot as _v403_new_snapshot, transition as _v403_transition

_V403_FLOW_LOCK=threading.Lock()

def _v403_flow_local_path(sid):
    sid=_safe_id(sid)
    if not sid:return None
    root=ROOT/"sessions"/sid
    root.mkdir(parents=True,exist_ok=True)
    return root/"project_flow_v403.json"

def _v403_flow_bucket_key(sid):
    sid=_safe_id(sid)
    if not sid:return ""
    try:
        profile=_creator_account_load(sid) or {}
        account_id=_safe_id(profile.get("account_id","")) if isinstance(profile,dict) else ""
    except Exception:
        account_id=""
    return f"creator-accounts/{account_id}/flow/v403.json" if account_id else f"session-flow/{sid}/v403.json"

def _v403_source_ref(sid):
    sid=_safe_id(sid)
    if not sid:return ""
    marker=ROOT/"sessions"/sid/"media"/".direct_upload_ready.json"
    try:
        data=json.loads(marker.read_text(encoding="utf-8"))
        if not isinstance(data,dict):return ""
        path=str(data.get("path") or "")
        if path:
            return f"/media/{sid}/media/{urllib.parse.quote(Path(path).name,safe='')}"
        key=str(data.get("bucket_key") or "")
        return "bucket://"+key if key else ""
    except Exception:
        return ""

def _v403_profile_payload(sid):
    try:
        profile=_creator_account_load(sid) or {}
        if not isinstance(profile,dict) or not profile:return None
        return {
            "name":str(profile.get("display_name") or "Creator")[:120],
            "avatar":str(profile.get("avatar") or "")[:1800000],
            "plan":str(profile.get("plan") or "FREE")[:24],
            "account_id":str(profile.get("account_id") or "")[:80],
            "version":int(float(profile.get("updated_at") or 0)),
        }
    except Exception:
        return None

def _v403_flow_read_bucket(sid):
    if not _bucket_enabled():return {}
    try:
        obj=_s3().get_object(Bucket=S3_BUCKET,Key=_v403_flow_bucket_key(sid))
        data=json.loads(obj["Body"].read().decode("utf-8"))
        return data if isinstance(data,dict) else {}
    except Exception:return {}

def _v403_flow_write_bucket(sid,snapshot):
    if not _bucket_enabled():return False
    try:
        _s3().put_object(Bucket=S3_BUCKET,Key=_v403_flow_bucket_key(sid),Body=json.dumps(snapshot,ensure_ascii=False,separators=(",",":")).encode("utf-8"),ContentType="application/json",CacheControl="no-store")
        return True
    except Exception:return False

def _v403_flow_load(sid):
    sid=_safe_id(sid)
    if not sid:return _v403_new_snapshot()
    path=_v403_flow_local_path(sid)
    data={}
    with _V403_FLOW_LOCK:
        try:
            data=json.loads(path.read_text(encoding="utf-8")) if path and path.is_file() else {}
            if not isinstance(data,dict):data={}
        except Exception:data={}
        if not data:data=_v403_flow_read_bucket(sid)
        if not data:data=_v403_new_snapshot(project_id="p_"+sid,source_video_ref=_v403_source_ref(sid))
        source_ref=_v403_source_ref(sid)
        if source_ref and not data.get("source_video_ref"):
            data=_v403_transition(data,"source_ready",{"source_video_ref":source_ref})
        profile=_v403_profile_payload(sid)
        if profile:data=_v403_transition(data,"profile_valid",profile)
        # Reconcile render state without ever starting a new render.
        try:
            stable,job=_final_local_paths(sid)
            render_doc={}
            if job and job.is_file():
                render_doc=json.loads(job.read_text(encoding="utf-8"))
                if not isinstance(render_doc,dict):render_doc={}
            if stable and stable.is_file() and stable.stat().st_size>1024:
                data=_v403_transition(data,"render_completed",{"job_id":str(render_doc.get("job_id") or render_doc.get("pid") or data.get("render",{}).get("job_id") or "render"),"asset_ref":"/share/final"})
            elif str(render_doc.get("status") or "")=="running" and data.get("selected_candidate_id"):
                data=_v403_transition(data,"render_started",{"job_id":str(render_doc.get("job_id") or render_doc.get("pid") or data.get("render",{}).get("job_id") or "render-active"),"progress":float(render_doc.get("progress") or 0)})
            elif str(render_doc.get("status") or "")=="failed":
                data=_v403_transition(data,"render_failed",{"error":str(render_doc.get("error") or "Render non riuscito")[:180]})
        except Exception:pass
        if path:
            try:_write_json_atomic(path,data)
            except Exception:pass
    return data

def _v403_flow_save(sid,snapshot):
    sid=_safe_id(sid)
    if not sid:return snapshot
    path=_v403_flow_local_path(sid)
    with _V403_FLOW_LOCK:
        try:_write_json_atomic(path,snapshot)
        except Exception:pass
        _v403_flow_write_bucket(sid,snapshot)
    return snapshot

def _v403_flow_event(sid,event,payload=None):
    current=_v403_flow_load(sid)
    updated=_v403_transition(current,event,payload if isinstance(payload,dict) else {})
    return _v403_flow_save(sid,updated)

def _v403_num(value,default=0.0):
    try:
        value=float(value)
        return value if value==value and abs(value)!=float("inf") else float(default)
    except Exception:return float(default)

def _v403_candidates_from_previews(rows):
    out=[]
    for i,row in enumerate((rows or [])[:3]):
        if not isinstance(row,dict):continue
        start=max(0.0,_v403_num(row.get("start_seconds",row.get("start",0.0))))
        end=max(start,_v403_num(row.get("end_seconds",row.get("end",start)),start))
        duration=max(0.0,_v403_num(row.get("duration",row.get("duration_seconds",0.0))))
        if end<=start and duration>0:end=start+duration
        out.append({
            "id":str(row.get("id") or row.get("candidate_id") or f"m{i}"),
            "rank":i+1,
            "start_seconds":start,"end_seconds":end,
            "event":str(row.get("event") or row.get("title") or f"Momento {i+1}")[:80],
            "confidence":_v403_num(row.get("confidence")),"score":_v403_num(row.get("score")),
            "reason":str(row.get("reason") or "")[:480],
            "fusion_reason":str(row.get("fusion_reason") or row.get("reason") or "Momento selezionato dal Game Brain")[:480],
            "fusion_signals":row.get("fusion_signals") if isinstance(row.get("fusion_signals"),list) else [],
            "preview_ref":str(row.get("video") or row.get("preview_ref") or "")[:1024],
            "thumbnail_ref":str(row.get("cover") or row.get("thumbnail_ref") or "")[:1024],
            "subtitles_available":bool(row.get("subtitles_available",False)),
        })
    return out
'''

SERVER_GET = r'''
        # V403 durable project flow GET
        if clean=="/project/flow":
            sid=_social_sid(self)
            if not sid:_json(self,400,{"ok":False,"error":"Sessione browser non valida."}); return
            _json(self,200,{"ok":True,"snapshot":_v403_flow_load(sid)})
            return
'''

SERVER_POST = r'''
        # V403 durable project flow POST
        if path=="/project/flow":
            try:
                data=_read_json(self,max_bytes=256*1024)
                event=str(data.get("event") or "")[:80]
                payload=data.get("payload") if isinstance(data.get("payload"),dict) else {}
                if event=="analysis_completed" and isinstance(payload.get("candidates"),list):
                    payload=dict(payload);payload["candidates"]=_v403_candidates_from_previews(payload.get("candidates"))
                _json(self,200,{"ok":True,"snapshot":_v403_flow_event(sid,event,payload)})
            except Exception as exc:_json(self,400,{"ok":False,"error":str(exc)[:180]})
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

AI_STYLE = r'''
<style id="v403MotoriOnly">
/* V403_APP_STABILITY_FLOW — Motori is config/progress only. */
#ai221>.panel:has(.moments),#ai221 .selectedShortPage,#ai221 .momentNextActions,#ai221 .momentFullscreen{display:none!important}
#ai221{overflow-y:auto!important}#ai221>.panel:first-of-type{margin-bottom:0!important}
</style>
'''

# Inserted inside the existing AI IIFE so it can read the authoritative local
# `state` object populated by V291/V319/V320.
AI_JS = r'''
 /* V403_APP_STABILITY_FLOW Motori bridge */
 let v403LastSig="",v403StableSince=0,v403Opened="";
 const v403Flow=async(event,payload={})=>{try{const r=await fetch("/project/flow",{method:"POST",credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json"},body:JSON.stringify({event,payload})});return r.ok?await r.json():null}catch(_e){return null}};
 const v403Create=document.getElementById("createAi");
 if(v403Create)v403Create.addEventListener("click",()=>{const job="analysis-"+Date.now().toString(36)+"-"+Math.random().toString(36).slice(2,8);v403Flow("analysis_started",{job_id:job,engine:state.engine||"auto",duration:Number(state.duration)||30})},true);
 const v403Watch=()=>{const rows=(Array.isArray(state.previews)?state.previews:[]).filter(r=>r&&(r.video||r.cover)).slice(0,3);if(!rows.length)return;const sig=rows.map((r,i)=>String(r.id||r.video||r.cover||i)+"|"+String(r.start_seconds??r.start??"")+"|"+String(r.end_seconds??r.end??"")).join("::");if(sig!==v403LastSig){v403LastSig=sig;v403StableSince=Date.now();return}if(rows.length<3&&Date.now()-v403StableSince<1600)return;if(v403Opened===sig)return;v403Opened=sig;v403Flow("analysis_completed",{job_id:"analysis-ready",candidates:rows}).finally(()=>{try{parent.postMessage({type:"GSF_V403_OPEN_MOMENTS"},location.origin)}catch(_e){}})};
 setInterval(v403Watch,320);document.addEventListener("visibilitychange",()=>{if(!document.hidden)v403Watch()});
'''

SHARE_PATCH = r'''
<style id="v403UnifiedCreateShortStyle">
/* V403 unified pre-render + ready surface */
#v403CreateShortPre{display:none}#share.v403PreRender>:not(#v403CreateShortPre){display:none!important}#share.v403PreRender #v403CreateShortPre{display:grid!important}#share.v403Ready #v403CreateShortPre{display:none!important}
#v403CreateShortPre{min-height:100%;grid-template-columns:minmax(210px,34%) minmax(0,1fr);gap:14px;align-items:center;max-width:1060px;margin:0 auto;padding:12px}.v403Preview{aspect-ratio:9/16;max-height:70vh;border-radius:24px;overflow:hidden;background:#071526;box-shadow:0 16px 38px rgba(34,83,122,.16)}.v403Preview video{width:100%;height:100%;object-fit:cover}.v403PreInfo{padding:20px;border:1px solid rgba(130,174,211,.28);border-radius:25px;background:rgba(255,255,255,.88);box-shadow:0 14px 34px rgba(53,99,140,.08)}.v403PreInfo h1{font-size:clamp(26px,4vw,42px)!important;margin:0 0 7px}.v403PreInfo p{color:#7084a0;line-height:1.45}.v403SelectedMeta{margin:13px 0;padding:11px;border-radius:15px;background:#eef8ff;color:#335f86;font-size:11px;font-weight:800}.v403PreActions{display:grid;grid-template-columns:1fr 1fr;gap:8px}.v403PreActions button{border:0;border-radius:15px;min-height:46px;font-weight:950;font-size:10.5px;cursor:pointer}.v403Create{grid-column:1/-1;background:linear-gradient(135deg,#70cff7,#4da8f3);color:#fff}.v403Edit{background:#dff5ea;color:#25775d}.v403Draft{background:#eef4f8;color:#58718a}.v403Back{grid-column:1/-1;background:#f6f8fb;color:#58718a}.v403RenderStatus{margin-top:10px;color:#5d7c98;font-size:10px;font-weight:800}
@media(max-width:760px){#share.v403PreRender.v396MobileMode>#v396MobilePublishSurface{display:none!important}#share.v403PreRender.v396MobileMode>#v403CreateShortPre{display:grid!important}#v403CreateShortPre{grid-template-columns:1fr;align-content:start;padding:8px 8px 18px}.v403Preview{width:min(52vw,205px);max-height:42vh;margin:0 auto;border-radius:19px}.v403PreInfo{padding:13px;border-radius:20px}.v403PreInfo h1{font-size:24px!important}.v403PreInfo p{font-size:10.5px}.v403PreActions{grid-template-columns:1fr}.v403Create,.v403Back{grid-column:auto}.v403PreActions button{min-height:44px}}
</style>
<script id="v403UnifiedCreateShortRuntime">
(()=>{
 if(window.__GSF_V403_SHORT)return;window.__GSF_V403_SHORT=true;const share=document.getElementById('share');if(!share)return;
 const pre=document.createElement('section');pre.id='v403CreateShortPre';pre.setAttribute('data-v403-state','pre-render');pre.innerHTML=`<span data-v403-state="ready" hidden></span><div class="v403Preview"><video id="v403SelectedVideo" controls playsinline preload="metadata"></video></div><div class="v403PreInfo"><h1>Crea il tuo Short</h1><p>Hai scelto il momento. Puoi crearlo subito, modificarlo nel Game Editor o salvarlo come bozza.</p><div class="v403SelectedMeta" id="v403SelectedMeta">Recupero il momento selezionato…</div><div class="v403PreActions"><button class="v403Create" id="v403CreateFinal">CREA SHORT</button><button class="v403Edit" id="v403EditFinal">GAME EDITOR</button><button class="v403Draft" id="v403SaveDraft">SALVA BOZZA</button><button class="v403Back" id="v403BackMoments">SCEGLI UN ALTRO MOMENTO</button></div><div class="v403RenderStatus" id="v403RenderStatus"></div></div>`;share.prepend(pre);
 let snap=null;const post=(type,extra={})=>{try{parent.postMessage({type,...extra},location.origin)}catch(_e){}};const selected=()=>{if(!snap||!Array.isArray(snap.candidates))return null;return snap.candidates.find(x=>x&&x.id===snap.selected_candidate_id)||null};const fmt=n=>{n=Math.max(0,Number(n||0));return `${Math.floor(n/60)}:${String(Math.floor(n%60)).padStart(2,'0')}`};
 const flow=async(event,payload={})=>{try{const r=await fetch('/project/flow',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json'},body:JSON.stringify({event,payload})});if(r.ok){const j=await r.json();if(j.snapshot){snap=j.snapshot;sync();return j.snapshot}}}catch(_e){}return null};
 function sync(){const row=selected(),ready=!!(snap&&snap.render&&snap.render.status==='ready'&&snap.final_asset_ref);share.classList.toggle('v403PreRender',!ready);share.classList.toggle('v403Ready',ready);share.setAttribute('data-v403-state',ready?'ready':'pre-render');const meta=document.getElementById('v403SelectedMeta'),video=document.getElementById('v403SelectedVideo'),status=document.getElementById('v403RenderStatus');if(!row){if(meta)meta.textContent='Nessun momento selezionato.';if(status)status.textContent='Torna ai momenti e scegline uno.';document.getElementById('v403CreateFinal').disabled=true;return}document.getElementById('v403CreateFinal').disabled=false;if(meta)meta.textContent=`${row.event||'Momento'} · ${fmt(row.start_seconds)} · ${Math.max(1,Math.round(Number(row.end_seconds||0)-Number(row.start_seconds||0)))}s`;const src=String(row.preview_ref||'');if(video&&src&&video.getAttribute('src')!==src){video.src=src;video.load()}if(status)status.textContent=snap.render?.status==='running'?'Creazione in corso… puoi cambiare pagina, il lavoro non si perde.':snap.render?.status==='error'?(snap.render.error||'Creazione non riuscita. Riprova.'):'Pronto per creare.'}
 async function refresh(){try{const r=await fetch('/project/flow?_='+Date.now(),{credentials:'same-origin',cache:'no-store'});if(r.ok){const j=await r.json();snap=j.snapshot||null;sync()}}catch(_e){}}
 document.getElementById('v403CreateFinal').onclick=async()=>{if(!selected())return;const job='render-'+Date.now().toString(36);await flow('render_started',{job_id:job});post('GSF_V403_CREATE_FINAL',{job_id:job,candidate_id:snap.selected_candidate_id})};document.getElementById('v403EditFinal').onclick=()=>{if(selected())post('GSF_V403_OPEN_EDITOR',{candidate_id:snap.selected_candidate_id})};document.getElementById('v403SaveDraft').onclick=async()=>{try{const r=await fetch('/drafts/save-current',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:'{}'});const j=await r.json();document.getElementById('v403RenderStatus').textContent=r.ok?'Bozza salvata.':(j.error||'Bozza non salvata.')}catch(_e){document.getElementById('v403RenderStatus').textContent='Bozza non salvata.'}};document.getElementById('v403BackMoments').onclick=()=>post('GSF_V403_OPEN_MOMENTS');
 window.addEventListener('message',e=>{if(e.origin!==location.origin||!e.data)return;if(e.data.type==='GSF_V403_FLOW_STATE'&&e.data.snapshot){snap=e.data.snapshot;sync()}});document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh()});setInterval(()=>{if(snap?.render?.status==='running')refresh()},1400);refresh();
})();
</script>
'''

APP_BLOCK = r'''
# V403_APP_STABILITY_FLOW — final browser owner for Motori -> Moments -> Editor -> Crea Short.
if GSF_WEB_MODE:
    st.html(r"""
    <div style="display:none!important"><script>
    ((P)=>{
      if(P.__GSF_V403_FLOW)return;P.__GSF_V403_FLOW=true;const D=P.document;
      const ensureStyle=()=>{if(D.getElementById('gsf-v403-shell-style'))return;const s=D.createElement('style');s.id='gsf-v403-shell-style';s.textContent=`.gsfV403Surface{position:fixed;left:0;right:0;top:64px;bottom:58px;z-index:7000;opacity:0;visibility:hidden;pointer-events:none;background:#f8fcff}.gsfV403Surface.is-open{opacity:1;visibility:visible;pointer-events:auto}.gsfV403Surface iframe{display:block;width:100%;height:100%;border:0;background:transparent}@media(max-width:760px){.gsfV403Surface{top:58px;bottom:70px}}`;D.head.appendChild(s)};
      const hide=id=>{const o=D.getElementById(id);if(!o)return;o.classList.remove('is-open');o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';o.setAttribute('aria-hidden','true')};const closeCompeting=keep=>['gsf-social-overlay-v159','gsf-creator-hub-live-v160','gsf-editor-overlay-v220','gsf-ai-overlay-v221','gsf-account-overlay-v223','gsf-short-overlay-v331','gsf-moments-overlay-v403','gsf-short-overlay-v403'].forEach(id=>{if(id!==keep)hide(id)});
      const surface=(id,src,title)=>{ensureStyle();let o=D.getElementById(id);if(o)return o;o=D.createElement('section');o.id=id;o.className='gsfV403Surface';o.setAttribute('aria-hidden','true');o.innerHTML=`<iframe title="${title}" src="${src}" allow="fullscreen; autoplay; clipboard-write"></iframe>`;D.body.appendChild(o);return o};const openSurface=(id,src,title)=>{const o=surface(id,src,title);closeCompeting(id);o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';o.setAttribute('aria-hidden','false');return o};
      const flow=async(event,payload={})=>{try{const r=await P.fetch('/project/flow',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json'},body:JSON.stringify({event,payload})});return r.ok?await r.json():null}catch(_e){return null}};const getFlow=async()=>{try{const r=await P.fetch('/project/flow?_='+Date.now(),{credentials:'same-origin',cache:'no-store'});return r.ok?await r.json():null}catch(_e){return null}};const broadcast=async()=>{const j=await getFlow();if(!j?.snapshot)return;['gsf-moments-overlay-v403','gsf-short-overlay-v403'].forEach(id=>{const f=D.getElementById(id)?.querySelector('iframe');try{f?.contentWindow?.postMessage({type:'GSF_V403_FLOW_STATE',snapshot:j.snapshot},P.location.origin)}catch(_e){}});return j.snapshot};
      const openMoments=()=>{openSurface('gsf-moments-overlay-v403','/moments-v403/?v=403','I tuoi 3 momenti');broadcast()};const openShort=()=>{hide('gsf-short-overlay-v331');openSurface('gsf-short-overlay-v403','/share-v156/?v=403','Crea Short');broadcast()};
      const openEditor=async()=>{hide('gsf-moments-overlay-v403');hide('gsf-short-overlay-v403');const snap=await broadcast();const rows=Array.isArray(snap?.candidates)?snap.candidates:[],row=rows.find(x=>x&&x.id===snap?.selected_candidate_id)||null;const payload={type:'GSF_SHELL_NAV',target:'editor'};if(row){payload.video_url=String(row.preview_ref||'');payload.duration=Math.max(.5,Number(row.end_seconds||0)-Number(row.start_seconds||0)||Number(row.duration)||15);payload.start_seconds=Number(row.start_seconds||0);payload.end_seconds=Number(row.end_seconds||0);payload.candidate_id=String(row.id||'')}try{P.postMessage(payload,P.location.origin)}catch(_e){}};
      const clickFinal=()=>{const nodes=[...D.querySelectorAll('button,a,[role=button]')].filter(x=>!x.closest('#gsf-short-overlay-v403')&&!x.closest('#gsf-short-overlay-v331'));for(const wanted of ['crea short finale','crea il tuo short','crea short']){const el=nodes.find(x=>String(x.innerText||x.textContent||'').trim().toLowerCase().includes(wanted));if(el){el.click();return true}}return false};
      P.addEventListener('message',async e=>{if(e.origin!==P.location.origin||!e.data)return;const t=String(e.data.type||'');if(t==='GSF_V403_OPEN_MOMENTS'){openMoments();return}if(t==='GSF_V403_CANDIDATE_SELECTED'){await flow('candidate_selected',{candidate_id:String(e.data.candidate_id||'')});broadcast();return}if(t==='GSF_V403_OPEN_EDITOR'){if(e.data.candidate_id)await flow('candidate_selected',{candidate_id:String(e.data.candidate_id)});openEditor();return}if(t==='GSF_V403_OPEN_SHORT'){if(e.data.candidate_id)await flow('candidate_selected',{candidate_id:String(e.data.candidate_id)});openShort();return}if(t==='GSF_V403_CREATE_FINAL'){setTimeout(()=>{if(!clickFinal())broadcast()},40);return}if(t==='GSF_SHELL_NAV'){const target=String(e.data.target||'');if(target==='moments'){openMoments();return}if(target==='short'){hide('gsf-short-overlay-v331');openShort();return}}},true);D.addEventListener('visibilitychange',()=>{if(!D.hidden)broadcast()});P.addEventListener('focus',broadcast,{passive:true});setTimeout(broadcast,400);
    })(window.parent);
    </script></div>
    """, height=0)
'''


def patch_server_text(text: str) -> str:
    if MARK not in text:
        anchor="class Handler(BaseHTTPRequestHandler):"
        if anchor not in text:raise RuntimeError("V403 server Handler anchor missing")
        text=text.replace(anchor,SERVER_HELPERS+"\n"+anchor,1)
    if '# V403 durable project flow GET' not in text:
        anchor='        if clean=="/source/restore":'
        if anchor not in text:raise RuntimeError("V403 server GET anchor missing")
        text=text.replace(anchor,SERVER_GET+"\n"+anchor,1)
    if '# V403 durable project flow POST' not in text:
        anchor='        if path=="/editor/state/save":'
        if anchor not in text:raise RuntimeError("V403 server POST anchor missing")
        text=text.replace(anchor,SERVER_POST+"\n"+anchor,1)
    return text


def patch_nginx_text(text: str) -> str:
    if MARK in text:return text
    anchor="    # V221 living AI engines surface."
    if anchor not in text:raise RuntimeError("V403 nginx AI anchor missing")
    return text.replace(anchor,NGINX_BLOCK+anchor,1)


def patch_ai_text(text: str) -> str:
    if 'id="v403MotoriOnly"' not in text:
        if "</head>" not in text:raise RuntimeError("V403 AI head anchor missing")
        text=text.replace("</head>",AI_STYLE+"\n</head>",1)
    if "V403_APP_STABILITY_FLOW Motori bridge" not in text:
        anchor=' send("ready");'
        if anchor not in text:raise RuntimeError("V403 AI ready anchor missing")
        text=text.replace(anchor,AI_JS+"\n"+anchor,1)
    return text


def patch_share_text(text: str) -> str:
    if 'id="v403UnifiedCreateShortRuntime"' in text:return text
    if "</body>" not in text:raise RuntimeError("V403 Share body anchor missing")
    return text.replace("</body>",SHARE_PATCH+"\n</body>",1)


def patch_app_text(text: str) -> str:
    if "# V403_APP_STABILITY_FLOW — final browser owner" in text:return text
    out=text.rstrip()+"\n\n"+APP_BLOCK+"\n";compile(out,str(APP),"exec");return out


def _write(path: Path, patcher, label: str) -> None:
    if not path.is_file():raise RuntimeError(f"V403 missing {label}: {path}")
    before=path.read_text(encoding="utf-8");after=patcher(before);path.write_text(after,encoding="utf-8");print(f"V403 {label} changed={before != after}",flush=True)


def main() -> None:
    _write(SERVER,patch_server_text,"project flow API");_write(NGINX,patch_nginx_text,"nginx routes");_write(AI,patch_ai_text,"Motori split");_write(SHARE,patch_share_text,"unified Crea Short");_write(APP,patch_app_text,"runtime shell routing")
    py_compile.compile(str(SERVER),doraise=True);py_compile.compile(str(APP),doraise=True);print("V403 app stability flow: PASS",flush=True)


if __name__ == "__main__":main()
