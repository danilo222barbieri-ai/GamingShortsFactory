#!/usr/bin/env python3
import json
import base64
import os
import re
import time
import threading
import uuid
import urllib.request
import urllib.parse
import secrets
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse, parse_qs

import boto3
from botocore.config import Config
from boto3.s3.transfer import TransferConfig
from gsf_perf import perf_event
from guardian_v113 import inspect_and_repair_local as _guardian_local, source_restore_plan as _guardian_source_plan
from quality_control_v124 import inspect_final_video as _quality_inspect
from guardian_intelligence_v124 import diagnose as _guardian_diagnose
from guardian_watchdog_v128 import ProactiveGuardian as _ProactiveGuardian
from feedback_learning_v127 import (
    load_model as _learning_load_model,
    save_model as _learning_save_model,
    update_model as _learning_update_model,
)
from content_memory_v145 import inspect_memory as _content_memory_inspect, upsert_memory as _content_memory_upsert
from social_analytics_v148 import collect as _social_analytics_collect, dynamic_performance_score as _social_dynamic_score

try:
    from pywebpush import webpush, WebPushException
except Exception:
    webpush=None
    WebPushException=Exception

ROOT=Path(os.environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime"))
APP_ICON_B64_PATH=Path("/app/web/app_icons/official_logo_180.valid.b64")
PORT=int(os.environ.get("GSF_DIRECT_UPLOAD_PORT","8502"))
MAX_FILE_BYTES=4*1024*1024*1024
MAX_CHUNK_BYTES=40*1024*1024
BUCKET_PART_BYTES=32*1024*1024
BUCKET_CONCURRENCY_DESKTOP=8
BUCKET_CONCURRENCY_MOBILE=3
ID_RE=re.compile(r"^[A-Za-z0-9_-]{1,80}$")
ALLOWED_EXT={".mp4",".mov",".mkv"}
_STATE_LOCKS={}
_STATE_LOCKS_GUARD=threading.Lock()
_QUALITY_CACHE={}
_QUALITY_LOCK=threading.Lock()
_AI_FEEDBACK_LOCK=threading.Lock()
_CONTENT_MEMORY_LOCK=threading.Lock()
_ANALYTICS_LOCK=threading.Lock()
_ANALYTICS_TICK={}
_AI_LEARNING_PATH=ROOT/"ai_learning_v127.json"
_AI_LEARNING_BUCKET_KEY="ai-feedback/global/model.json"
_GUARDIAN_WATCHDOG=None

def _env_first(*names,default=""):
    for name in names:
        value=os.environ.get(name)
        if value:
            return value
    return default

S3_BUCKET=_env_first("GSF_S3_BUCKET","S3_BUCKET","BUCKET")
S3_ACCESS_KEY=_env_first("GSF_S3_ACCESS_KEY_ID","AWS_ACCESS_KEY_ID","ACCESS_KEY_ID")
S3_SECRET_KEY=_env_first("GSF_S3_SECRET_ACCESS_KEY","AWS_SECRET_ACCESS_KEY","SECRET_ACCESS_KEY")
S3_ENDPOINT=_env_first("GSF_S3_ENDPOINT","AWS_ENDPOINT_URL","ENDPOINT")
S3_REGION=_env_first("GSF_S3_REGION","AWS_REGION","AWS_DEFAULT_REGION","REGION",default="auto")
S3_ADDRESSING_STYLE=_env_first("GSF_S3_ADDRESSING_STYLE",default="virtual")
PUBLIC_ORIGIN=_env_first("GSF_PUBLIC_ORIGIN",default="")
WORKER_URL=_env_first("GSF_WORKER_URL",default="").rstrip("/")
WORKER_TOKEN=_env_first("GSF_WORKER_TOKEN",default="")
PUBLIC_APP_URL=_env_first("GSF_PUBLIC_APP_URL",default="").rstrip("/")
VAPID_PRIVATE_KEY=_env_first("GSF_VAPID_PRIVATE_KEY",default="")
VAPID_PUBLIC_KEY=_env_first("GSF_VAPID_PUBLIC_KEY",default="")
VAPID_SUBJECT=_env_first("GSF_VAPID_SUBJECT",default="mailto:notifications@gamingshortsfactory.app")
TIKTOK_CLIENT_KEY=_env_first("GSF_TIKTOK_CLIENT_KEY",default="")
TIKTOK_CLIENT_SECRET=_env_first("GSF_TIKTOK_CLIENT_SECRET",default="")
YOUTUBE_CLIENT_ID=_env_first("GSF_YOUTUBE_CLIENT_ID",default="")
YOUTUBE_CLIENT_SECRET=_env_first("GSF_YOUTUBE_CLIENT_SECRET",default="")
YOUTUBE_SCOPE="https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/yt-analytics.readonly"
INSTAGRAM_APP_ID=_env_first("GSF_INSTAGRAM_APP_ID",default="")
INSTAGRAM_APP_SECRET=_env_first("GSF_INSTAGRAM_APP_SECRET",default="")
INSTAGRAM_SCOPES="instagram_business_basic,instagram_business_content_publish,instagram_business_manage_insights"
INSTAGRAM_REDIRECT_URI=(PUBLIC_APP_URL+"/auth/instagram/callback") if PUBLIC_APP_URL else ""
META_APP_ID=_env_first("GSF_META_APP_ID",default="")
META_APP_SECRET=_env_first("GSF_META_APP_SECRET",default="")
META_SCOPES="pages_show_list,instagram_basic,instagram_content_publish,pages_read_engagement"
_S3_CLIENT=None
_S3_LOCK=threading.Lock()

def _bucket_enabled():
    return bool(S3_BUCKET and S3_ACCESS_KEY and S3_SECRET_KEY and S3_ENDPOINT)

def _upload_concurrency_for_user_agent(user_agent):
    ua=str(user_agent or "").lower()
    mobile_markers=("iphone","ipad","ipod","android"," mobile","mobile/")
    if any(marker in ua for marker in mobile_markers):
        return BUCKET_CONCURRENCY_MOBILE
    return BUCKET_CONCURRENCY_DESKTOP


def _materialize_concurrency():
    try:
        value=int(os.environ.get("GSF_MATERIALIZE_CONCURRENCY","6") or 6)
    except Exception:
        value=6
    return max(1,min(8,value))


def _s3():
    global _S3_CLIENT
    if not _bucket_enabled():
        return None
    with _S3_LOCK:
        if _S3_CLIENT is None:
            _S3_CLIENT=boto3.client(
                "s3",
                endpoint_url=S3_ENDPOINT,
                aws_access_key_id=S3_ACCESS_KEY,
                aws_secret_access_key=S3_SECRET_KEY,
                region_name=S3_REGION,
                config=Config(
                    signature_version="s3v4",
                    s3={"addressing_style":S3_ADDRESSING_STYLE},
                    retries={"max_attempts":3,"mode":"standard"},
                ),
            )
        return _S3_CLIENT

def _final_bucket_key(sid):
    sid=_safe_id(sid)
    return f"final-results/{sid}/latest.mp4" if sid else ""

def _final_meta_key(sid):
    sid=_safe_id(sid)
    return f"final-results/{sid}/latest.json" if sid else ""

def _final_local_paths(sid):
    sid=_safe_id(sid)
    if not sid:
        return None,None
    root=ROOT/"sessions"/sid
    media=root/"media"
    media.mkdir(parents=True,exist_ok=True)
    return media/"gaming_short_finale_share.mp4", root/"render_job.json"

def _final_persist_to_bucket(sid,source_path,started_at=0.0):
    sid=_safe_id(sid)
    if not sid or not _bucket_enabled():
        raise RuntimeError("storage persistente non disponibile")
    stable,job=_final_local_paths(sid)
    source=Path(str(source_path or "")).resolve()
    expected=stable.resolve()
    if source!=expected or not source.is_file() or source.stat().st_size<=1024:
        raise ValueError("finale locale non valido")
    size=int(source.stat().st_size)
    completed=time.time()
    key=_final_bucket_key(sid)
    _s3().upload_file(
        str(source),S3_BUCKET,key,
        ExtraArgs={"ContentType":"video/mp4","CacheControl":"no-store"},
    )
    meta={
        "status":"ready",
        "started_at":float(started_at or 0.0),
        "completed_at":completed,
        "final_bytes":size,
        "bucket_key":key,
    }
    _s3().put_object(
        Bucket=S3_BUCKET,Key=_final_meta_key(sid),
        Body=json.dumps(meta,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
        ContentType="application/json",CacheControl="no-store",
    )
    print("GSF_FINAL_BUCKET_READY",sid,size,flush=True)
    return meta

def _final_restore_from_bucket(sid):
    sid=_safe_id(sid)
    if not sid or not _bucket_enabled():
        return {}
    stable,job=_final_local_paths(sid)
    if stable.is_file() and stable.stat().st_size>1024:
        return {}
    try:
        obj=_s3().get_object(Bucket=S3_BUCKET,Key=_final_meta_key(sid))
        meta=json.loads(obj["Body"].read().decode("utf-8"))
        if not isinstance(meta,dict):
            meta={}
        key=str(meta.get("bucket_key") or _final_bucket_key(sid))
        tmp=stable.with_suffix(".restore.tmp")
        tmp.unlink(missing_ok=True)
        _s3().download_file(S3_BUCKET,key,str(tmp))
        if not tmp.is_file() or tmp.stat().st_size<=1024:
            tmp.unlink(missing_ok=True)
            return {}
        os.replace(tmp,stable)
        payload={
            "status":"ready",
            "started_at":float(meta.get("started_at") or 0.0),
            "completed_at":float(meta.get("completed_at") or stable.stat().st_mtime or time.time()),
            "final_path":str(stable),
            "final_bytes":int(stable.stat().st_size),
            "pid":0,
            "restored_from_bucket":True,
        }
        _write_json_atomic(job,payload)
        print("GSF_FINAL_BUCKET_RESTORED",sid,payload["final_bytes"],flush=True)
        return payload
    except Exception as exc:
        print("GSF_FINAL_BUCKET_RESTORE_WARN",sid,repr(str(exc))[:220],flush=True)
        return {}

def _ensure_bucket_cors():
    if not _bucket_enabled():
        return
    configured=[]
    _default_shared_origins=(
        "https://gaming-shorts-factory-v79-production.up.railway.app,"
        "https://gaming-shorts-factory-demo-production.up.railway.app"
    )
    for raw in [
        PUBLIC_ORIGIN,
        os.environ.get("GSF_PUBLIC_ORIGINS",""),
        _default_shared_origins,
    ]:
        for item in str(raw or "").replace(";",",").split(","):
            origin=item.strip().rstrip("/")
            if origin and origin not in configured:
                configured.append(origin)
    if not configured:
        return
    try:
        existing=[]
        try:
            existing=list((_s3().get_bucket_cors(Bucket=S3_BUCKET) or {}).get("CORSRules") or [])
        except Exception:
            existing=[]

        target=None
        required_methods={"GET","HEAD","PUT","POST"}
        for rule in existing:
            methods=set(rule.get("AllowedMethods") or [])
            headers=set(rule.get("AllowedHeaders") or [])
            if required_methods.issubset(methods) and "*" in headers:
                target=rule
                break

        if target is None:
            target={
                "AllowedHeaders":["*"],
                "AllowedMethods":["GET","HEAD","PUT","POST"],
                "AllowedOrigins":[],
                "ExposeHeaders":["ETag"],
                "MaxAgeSeconds":3000,
            }
            existing.append(target)

        origins=[]
        for origin in list(target.get("AllowedOrigins") or []) + configured:
            origin=str(origin or "").strip().rstrip("/")
            if origin and origin not in origins:
                origins.append(origin)
        target["AllowedOrigins"]=origins

        exposed=list(target.get("ExposeHeaders") or [])
        if "ETag" not in exposed:
            exposed.append("ETag")
        target["ExposeHeaders"]=exposed
        target["MaxAgeSeconds"]=max(int(target.get("MaxAgeSeconds") or 0),3000)

        _s3().put_bucket_cors(
            Bucket=S3_BUCKET,
            CORSConfiguration={"CORSRules":existing},
        )
        print(f"GSF bucket CORS ready for {', '.join(origins)}",flush=True)
    except Exception as exc:
        print(f"GSF bucket CORS warning: {str(exc)[:180]}",flush=True)

def _state_lock(sid,upload_id):
    key=(str(sid),str(upload_id))
    with _STATE_LOCKS_GUARD:
        lock=_STATE_LOCKS.get(key)
        if lock is None:
            lock=threading.Lock()
            _STATE_LOCKS[key]=lock
        return lock

def _write_json_atomic(path,payload):
    tmp=Path(str(path)+".tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False),encoding="utf-8")
    os.replace(tmp,path)

def _safe_id(value):
    value=str(value or "")
    return value if ID_RE.fullmatch(value) else ""

def _safe_filename(value):
    try:
        value=unquote(str(value or "video.mp4"))
    except Exception:
        value="video.mp4"
    name=Path(value).name
    ext=Path(name).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise ValueError("unsupported extension")
    stem=re.sub(r"[^A-Za-z0-9_.-]+","_",Path(name).stem)[:80] or "video"
    return name,stem,ext

def _send_bytes(handler,status,body,content_type,cache_control="public, max-age=86400"):
    raw=bytes(body)
    handler.send_response(status)
    handler.send_header("Content-Type",content_type)
    handler.send_header("Content-Length",str(len(raw)))
    handler.send_header("Cache-Control",cache_control)
    handler.end_headers()
    handler.wfile.write(raw)

def _official_app_icon_bytes():
    return base64.b64decode(APP_ICON_B64_PATH.read_text(encoding="ascii").strip())

def _app_manifest_bytes():
    payload={
        "name":"Gaming Shorts Factory",
        "short_name":"GSF",
        "start_url":"/",
        "scope":"/",
        "display":"standalone",
        "background_color":"#f4fbff",
        "theme_color":"#a9dcff",
        "icons":[
            {
                "src":"/app-icon-192.png?v=4",
                "sizes":"192x192",
                "type":"image/png",
                "purpose":"any"
            },
            {
                "src":"/app-icon-512.png?v=4",
                "sizes":"512x512",
                "type":"image/png",
                "purpose":"any"
            }
        ]
    }
    return json.dumps(payload,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def _push_subscription_path(sid):
    sid=_safe_id(sid)
    if not sid:
        return None
    root=ROOT/"sessions"/sid
    root.mkdir(parents=True,exist_ok=True)
    return root/".push_subscription.json"

def _push_save_subscription(sid,payload):
    path=_push_subscription_path(sid)
    if path is None:
        raise ValueError("invalid session")
    endpoint=str((payload or {}).get("endpoint") or "")
    keys=dict((payload or {}).get("keys") or {})
    if not endpoint.startswith("https://") or not keys.get("p256dh") or not keys.get("auth"):
        raise ValueError("invalid push subscription")
    tmp=path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"endpoint":endpoint,"keys":keys},ensure_ascii=False),encoding="utf-8")
    os.replace(tmp,path)
    return True

def _push_private_key_path():
    if not VAPID_PRIVATE_KEY:
        return None
    root=ROOT/"push"
    root.mkdir(parents=True,exist_ok=True)
    path=root/"vapid_private.pem"
    if not path.is_file() or path.read_text(encoding="utf-8")!=VAPID_PRIVATE_KEY:
        path.write_text(VAPID_PRIVATE_KEY,encoding="utf-8")
        try:
            os.chmod(path,0o600)
        except Exception:
            pass
    return path

def _push_notify_sid(sid,title="Short pronto",body="Il tuo Short è pronto da condividere.",url="/",tag="gsf-short-ready"):
    sid=_safe_id(sid)
    sub_path=_push_subscription_path(sid)
    key_path=_push_private_key_path()
    if not sid or sub_path is None or not sub_path.is_file() or not key_path or webpush is None:
        return False
    try:
        subscription=json.loads(sub_path.read_text(encoding="utf-8"))
        payload=json.dumps({
            "title":str(title or "Short pronto")[:90],
            "body":str(body or "")[:220],
            "url":str(url or "/")[:500],
            "tag":str(tag or "gsf-short-ready")[:80],
        },ensure_ascii=False)
        webpush(
            subscription_info=subscription,
            data=payload,
            vapid_private_key=str(key_path),
            vapid_claims={"sub":VAPID_SUBJECT},
            ttl=600,
        )
        print("GSF_PUSH_SENT",sid,flush=True)
        return True
    except Exception as exc:
        status=getattr(getattr(exc,"response",None),"status_code",None)
        print("GSF_PUSH_ERROR",sid,status,repr(str(exc))[:240],flush=True)
        if status in (404,410):
            try:
                sub_path.unlink(missing_ok=True)
            except Exception:
                pass
        return False

def _push_service_worker_bytes():
    return r'''self.addEventListener("push",(event)=>{
  let data={};
  try{data=event.data?event.data.json():{};}catch(e){}
  event.waitUntil(self.registration.showNotification(data.title||"Gaming Shorts Factory",{
    body:data.body||"Il tuo Short è pronto.",
    icon:"/app-icon-192.png",
    badge:"/app-icon-192.png",
    tag:data.tag||"gsf-short-ready",
    renotify:true,
    data:{url:data.url||"/"},
    vibrate:[120,70,120]
  }));
});
self.addEventListener("notificationclick",(event)=>{
  event.notification.close();
  const target=(event.notification.data&&event.notification.data.url)||"/";
  event.waitUntil(clients.matchAll({type:"window",includeUncontrolled:true}).then((items)=>{
    for(const client of items){
      if("focus" in client){
        try{client.navigate(target);}catch(e){}
        return client.focus();
      }
    }
    return clients.openWindow?clients.openWindow(target):undefined;
  }));
});'''.encode("utf-8")


def _push_client_bytes():
    return r'''(()=>{
  if(window.__GSF_GLOBAL_NOTIFICATIONS_V2__)return;
  window.__GSF_GLOBAL_NOTIFICATIONS_V2__=true;
  const toU8=(s)=>{const pad="=".repeat((4-s.length%4)%4);const raw=atob((s+pad).replace(/-/g,"+").replace(/_/g,"/"));return Uint8Array.from([...raw].map(c=>c.charCodeAt(0)));};
  const subscribe=async(promptUser)=>{if(!("serviceWorker" in navigator)||!("PushManager" in window)||!("Notification" in window))return false;const reg=await navigator.serviceWorker.register("/gsf-sw.js?v=1",{scope:"/"});let permission=Notification.permission;if(permission==="default"&&promptUser)permission=await Notification.requestPermission();if(permission!=="granted")return false;const key=await fetch("/push/public-key",{cache:"no-store"}).then(r=>r.json()).then(x=>x.public_key||"");if(!key)return false;let sub=await reg.pushManager.getSubscription();if(!sub)sub=await reg.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:toU8(key)});await fetch("/push/subscribe",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(sub.toJSON())});return true;};

  const ensureToastUi=()=>{
    let host=document.getElementById("gsf-site-toast-stack");
    if(host)return host;
    const style=document.createElement("style");
    style.id="gsf-site-toast-style";
    style.textContent="#gsf-site-toast-stack{position:fixed;top:max(14px,env(safe-area-inset-top,0px));right:14px;z-index:2147483640;width:min(360px,calc(100vw - 28px));display:flex;flex-direction:column;gap:9px;pointer-events:none;font-family:Inter,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}.gsf-site-toast{position:relative;display:grid;grid-template-columns:44px minmax(0,1fr) 24px;gap:10px;align-items:center;padding:10px 10px 10px 11px;border:1px solid rgba(194,219,236,.92);border-radius:18px;background:rgba(255,255,255,.94);-webkit-backdrop-filter:blur(18px);backdrop-filter:blur(18px);box-shadow:0 15px 38px rgba(37,72,101,.18),inset 0 1px 0 rgba(255,255,255,.86);color:#24475f;pointer-events:auto;overflow:hidden;opacity:0;transform:translateY(-12px) scale(.98);transition:opacity .22s ease,transform .22s ease}.gsf-site-toast.gsf-show{opacity:1;transform:translateY(0) scale(1)}.gsf-site-toast.gsf-hide{opacity:0;transform:translateY(-9px) scale(.985)}.gsf-site-toast-icon{width:44px;height:44px;border-radius:13px;display:grid;place-items:center;background:linear-gradient(145deg,#eaf8ff,#bfe8ff);box-shadow:inset 0 1px 0 rgba(255,255,255,.88)}.gsf-site-toast-icon img{width:34px;height:34px;border-radius:10px;display:block}.gsf-site-toast-copy{min-width:0}.gsf-site-toast-title{font-size:13px;font-weight:900;line-height:1.15;color:#315b75;letter-spacing:.005em}.gsf-site-toast-body{margin-top:3px;font-size:11px;font-weight:650;line-height:1.3;color:#668195;white-space:normal}.gsf-site-toast-close{border:0;background:transparent;color:#86a0b1;width:24px;height:24px;border-radius:8px;font-size:18px;line-height:20px;padding:0;cursor:pointer}.gsf-site-toast-bar{position:absolute;left:0;bottom:0;height:3px;width:100%;background:linear-gradient(90deg,#8bd9f8,#8cc9ff);transform-origin:left center;animation:gsfToastLife 5.8s linear forwards}.gsf-site-toast[data-kind=error]{border-color:rgba(235,187,187,.9)}.gsf-site-toast[data-kind=error] .gsf-site-toast-icon{background:linear-gradient(145deg,#fff0f0,#ffd8d8)}.gsf-site-toast[data-kind=error] .gsf-site-toast-bar{background:linear-gradient(90deg,#ff9d9d,#ffc0c0)}@keyframes gsfToastLife{from{transform:scaleX(1)}to{transform:scaleX(0)}}@media(max-width:600px){#gsf-site-toast-stack{top:max(10px,env(safe-area-inset-top,0px));right:10px;width:calc(100vw - 20px)}.gsf-site-toast{grid-template-columns:42px minmax(0,1fr) 22px;border-radius:16px}.gsf-site-toast-icon{width:42px;height:42px}.gsf-site-toast-icon img{width:32px;height:32px}}";
    document.head.appendChild(style);
    host=document.createElement("div");
    host.id="gsf-site-toast-stack";
    host.setAttribute("aria-live","polite");
    document.body.appendChild(host);
    return host;
  };

  const seenPersistent=(token)=>{if(!token)return false;try{return localStorage.getItem("gsf-site-notice:"+token)==="1";}catch(e){return false;}};
  const markPersistent=(token)=>{if(!token)return;try{localStorage.setItem("gsf-site-notice:"+token,"1");}catch(e){}};
  const showToast=(title,body,kind="success",opts={})=>{
    const token=String(opts.token||"");
    if(opts.persistent&&token&&seenPersistent(token))return false;
    if(opts.persistent&&token)markPersistent(token);
    const host=ensureToastUi(),el=document.createElement("div");
    el.className="gsf-site-toast";el.dataset.kind=kind;
    const icon=document.createElement("div");icon.className="gsf-site-toast-icon";
    const img=document.createElement("img");img.src="/app-icon.png?v=4";img.alt="";icon.appendChild(img);
    const copy=document.createElement("div");copy.className="gsf-site-toast-copy";
    const strong=document.createElement("div");strong.className="gsf-site-toast-title";strong.textContent=String(title||"Gaming Shorts Factory");
    const small=document.createElement("div");small.className="gsf-site-toast-body";small.textContent=String(body||"");copy.append(strong,small);
    const close=document.createElement("button");close.className="gsf-site-toast-close";close.type="button";close.setAttribute("aria-label","Chiudi");close.textContent="×";
    const bar=document.createElement("div");bar.className="gsf-site-toast-bar";el.append(icon,copy,close,bar);host.prepend(el);
    while(host.children.length>3)host.lastElementChild?.remove();
    const remove=()=>{if(!el.isConnected)return;el.classList.add("gsf-hide");setTimeout(()=>el.remove(),240);};
    close.onclick=(ev)=>{ev.stopPropagation();remove();};
    if(typeof opts.onClick==="function"){el.style.cursor="pointer";el.addEventListener("click",(ev)=>{if(ev.target===close)return;opts.onClick();remove();});}
    requestAnimationFrame(()=>el.classList.add("gsf-show"));setTimeout(remove,5800);return true;
  };

  window.GSFPush={enable:()=>subscribe(true),ensure:()=>subscribe(false)};
  window.GSFNotify={show:(title,body,kind)=>showToast(title,body,kind||"success")};

  let uploadActive=false,uploadCycle=0,uploadDoneCycle=0,lastRenderStatus="";
  window.addEventListener("message",(event)=>{
    const d=event.data||{};if(d.type!=="gsf-upload")return;const state=String(d.state||"");
    if(state==="running"){if(!uploadActive){uploadCycle+=1;uploadActive=true;}}
    else if(state==="done"){uploadActive=false;if(uploadDoneCycle!==uploadCycle){uploadDoneCycle=uploadCycle;const name=String(d.name||"").trim();showToast("Upload completato",name?name+" è pronto per essere lavorato.":"Il video è pronto per essere lavorato.","success");}}
    else if(state==="error"){const wasActive=uploadActive;uploadActive=false;if(wasActive)showToast("Upload interrotto","Il caricamento non è stato completato. Puoi riprovare senza perdere il resto del lavoro.","error");}
  });

  window.addEventListener("beforeunload",(event)=>{if(!uploadActive)return;event.preventDefault();event.returnValue="";});

  const openShareHub=()=>{
    const target=[...document.querySelectorAll("button")].find((b)=>{const label=(b.innerText||b.textContent||"").trim().toUpperCase();return label.includes("CONDIVIDI O SCARICA")||label.includes("APRI SHARE HUB");});
    if(!target||target.disabled)return false;target.click();return true;
  };

  const syncReadyResult=()=>{
    const target=document.querySelector('.st-key-gsf_final_ready_sync_v111 button,[class*="st-key-gsf_final_ready_sync_v111"] button');
    if(!target||target.disabled)return false;
    target.click();
    return true;
  };

  const pollJob=async()=>{
    try{
      const j=await fetch("/job/status",{cache:"no-store"}).then(r=>r.json()),status=String(j.render_status||"");
      if(status==="ready"){
        const token=String(j.completed_at||j.started_at||"ready");
        showToast("Short completato","Il tuo Short è pronto per download e pubblicazione.","success",{token:"short-ready-"+token,persistent:true,onClick:()=>openShareHub()});
        if(lastRenderStatus!=="ready"){
          if(!syncReadyResult())setTimeout(syncReadyResult,250);
        }
      }else if(status==="failed"){
        const token=String(j.failed_at||j.started_at||"failed");
        showToast("Creazione Short non riuscita","Il rendering si è fermato. Il progetto e la bozza restano disponibili.","error",{token:"short-failed-"+token,persistent:true});
      }
      lastRenderStatus=status;
    }catch(e){}
  };

  setInterval(pollJob,1500);pollJob();
  document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="visible"){pollJob();subscribe(false).catch(()=>{});}});
  window.addEventListener("pageshow",()=>{pollJob();subscribe(false).catch(()=>{});});
  document.addEventListener("click",(event)=>{const b=event.target&&event.target.closest?event.target.closest("button"):null;if(!b)return;const label=(b.innerText||b.textContent||"").toUpperCase();if(label.includes("CREA SHORT"))subscribe(true).catch(()=>{});},true);
  window.addEventListener("load",()=>subscribe(false).catch(()=>{}),{once:true});
})();'''.encode("utf-8")

def _json(handler,status,payload):
    body=json.dumps(payload,ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type","application/json; charset=utf-8")
    handler.send_header("Content-Length",str(len(body)))
    handler.send_header("Cache-Control","no-store")
    handler.end_headers()
    handler.wfile.write(body)

def _read_json(handler,max_bytes=1024*1024):
    try:
        length=int(handler.headers.get("Content-Length","0") or 0)
    except Exception:
        length=0
    if length<=0 or length>max_bytes:
        raise ValueError("invalid body length")
    raw=handler.rfile.read(length)
    return json.loads(raw.decode("utf-8"))

def _trigger_prescan(payload):
    if not WORKER_URL:
        perf_event("prescan_queue_end",queued=False,reason="worker_url_missing")
        return
    t0=time.perf_counter()
    perf_event(
        "prescan_queue_start",
        analysis_key=str(payload.get("analysis_key","") or ""),
        source_size=int(payload.get("size",0) or 0),
    )
    try:
        data=json.dumps(payload,ensure_ascii=False).encode("utf-8")
        headers={"Content-Type":"application/json"}
        if WORKER_TOKEN:
            headers["X-GSF-Worker-Token"]=WORKER_TOKEN
        req=urllib.request.Request(
            WORKER_URL+"/prescan",
            data=data,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req,timeout=12) as resp:
            resp.read(4096)
        perf_event(
            "prescan_queue_end",
            queued=True,
            elapsed_seconds=round(time.perf_counter()-t0,3),
            analysis_key=str(payload.get("analysis_key","") or ""),
        )
        print(f"GSF worker prescan queued: {payload.get('analysis_key','')}",flush=True)
    except Exception as exc:
        perf_event(
            "prescan_queue_end",
            queued=False,
            elapsed_seconds=round(time.perf_counter()-t0,3),
            error_type=type(exc).__name__,
        )
        print(f"GSF worker prescan warning: {str(exc)[:180]}",flush=True)

def _materialize_bucket_object(sid,upload_id,key,original_name,safe_stem,ext,total,analysis_key):
    _materialize_t0=time.perf_counter()
    perf_event(
        "materialize_start",
        upload_id=str(upload_id),
        source_size=int(total or 0),
    )
    media=ROOT/"sessions"/sid/"media"
    media.mkdir(parents=True,exist_ok=True)
    final=media/f"source_bucket_{safe_stem}_{upload_id}{ext}"
    tmp=media/f".source_bucket_{safe_stem}_{upload_id}{ext}.tmp"
    try:
        cfg=TransferConfig(
            multipart_threshold=8*1024*1024,
            multipart_chunksize=8*1024*1024,
            max_concurrency=_materialize_concurrency(),
            max_io_queue=16,
            io_chunksize=1024*1024,
            use_threads=True,
        )
        with open(tmp,"wb") as out:
            _s3().download_fileobj(S3_BUCKET,key,out,Config=cfg)
            out.flush()
            os.fsync(out.fileno())
        if tmp.stat().st_size!=total:
            raise IOError(f"bucket materialization size mismatch {tmp.stat().st_size} != {total}")
        os.replace(tmp,final)
        marker=media/".direct_upload_ready.json"
        _write_json_atomic(marker,{
            "path":str(final),
            "name":original_name,
            "size":total,
            "upload_id":upload_id,
            "completed_at":time.time(),
            "storage":"railway_bucket",
            "bucket_key":key,
            "analysis_key":analysis_key,
        })
        try:
            os.utime(ROOT/"sessions"/sid/".active",None)
        except Exception:
            pass
        perf_event(
            "materialize_end",
            upload_id=str(upload_id),
            source_size=int(total or 0),
            elapsed_seconds=round(time.perf_counter()-_materialize_t0,3),
            ok=True,
        )
        print(f"GSF bucket materialized {upload_id}: {total} bytes",flush=True)
    except Exception as exc:
        tmp.unlink(missing_ok=True)
        error=media/".direct_upload_error.json"
        _write_json_atomic(error,{
            "upload_id":upload_id,
            "error":str(exc)[:240],
            "failed_at":time.time(),
        })
        perf_event(
            "materialize_error",
            upload_id=str(upload_id),
            source_size=int(total or 0),
            elapsed_seconds=round(time.perf_counter()-_materialize_t0,3),
            error_type=type(exc).__name__,
        )
        print(f"GSF bucket materialization failed {upload_id}: {str(exc)[:180]}",flush=True)



def _bucket_source_ref_from_path(sid,source_path):
    """Recover persistent bucket metadata from a materialized source filename."""
    sid=_safe_id(sid)
    source_path=str(source_path or "")
    if not sid or not source_path or not _bucket_enabled():
        return {}
    name=Path(source_path).name
    match=re.search(r"_([0-9a-fA-F]{20})(\.[A-Za-z0-9]{1,10})$",name)
    if not match:
        return {}
    upload_id=_safe_id(match.group(1))
    if not upload_id:
        return {}
    prefix=f"uploads/{sid}/{upload_id}/"
    try:
        rows=_s3().list_objects_v2(Bucket=S3_BUCKET,Prefix=prefix,MaxKeys=10).get("Contents") or []
        rows=[row for row in rows if str(row.get("Key") or "").startswith(prefix) and int(row.get("Size") or 0)>0]
        if not rows:
            return {}
        row=max(rows,key=lambda x:int(x.get("Size") or 0))
        key=str(row.get("Key") or "")
        head=_s3().head_object(Bucket=S3_BUCKET,Key=key)
        metadata=dict(head.get("Metadata") or {})
        original_name=str(metadata.get("gsf-original-name") or Path(key).name)
        original_name,safe_stem,ext=_safe_filename(original_name)
        total=int(head.get("ContentLength") or row.get("Size") or 0)
        if total<=0:
            return {}
        return {
            "name":original_name,
            "size":total,
            "upload_id":upload_id,
            "storage":"railway_bucket",
            "bucket_key":key,
            "analysis_key":f"analysis/{sid}/{upload_id}/v52-keyframe-turbo.json",
            "path":source_path,
            "safe_stem":safe_stem,
            "ext":ext,
        }
    except Exception as exc:
        print("GSF_SOURCE_REF_RECOVER_WARN",sid,repr(str(exc)),flush=True)
        return {}


def _restore_bucket_source(sid,source_path):
    sid=_safe_id(sid)
    ref=_bucket_source_ref_from_path(sid,source_path)
    if not ref:
        return ""
    try:
        _materialize_bucket_object(
            sid,
            str(ref["upload_id"]),
            str(ref["bucket_key"]),
            str(ref["name"]),
            str(ref["safe_stem"]),
            str(ref["ext"]),
            int(ref["size"]),
            str(ref["analysis_key"]),
        )
        marker=ROOT/"sessions"/sid/"media"/".direct_upload_ready.json"
        if marker.is_file():
            meta=json.loads(marker.read_text(encoding="utf-8"))
            restored=Path(str(meta.get("path") or ""))
            if restored.is_file() and str(meta.get("upload_id") or "")==str(ref["upload_id"]):
                print("GSF_SOURCE_RESTORED",sid,str(restored),flush=True)
                return str(restored)
    except Exception as exc:
        print("GSF_SOURCE_RESTORE_WARN",sid,repr(str(exc)),flush=True)
    return ""



def _persist_fallback_source_to_bucket(sid,upload_id,source_path,original_name,total):
    """Promote a direct-upload fallback source into persistent storage without blocking the browser."""
    sid=_safe_id(sid); upload_id=_safe_id(upload_id)
    source=Path(str(source_path or ""))
    if not sid or not upload_id or not source.is_file() or not _bucket_enabled():
        return {}
    try:
        original_name,safe_stem,ext=_safe_filename(original_name or source.name)
        key=f"uploads/{sid}/{upload_id}/{safe_stem}{ext}"
        analysis_key=f"analysis/{sid}/{upload_id}/v52-keyframe-turbo.json"
        size=int(total or source.stat().st_size)
        exists=False
        try:
            head=_s3().head_object(Bucket=S3_BUCKET,Key=key)
            exists=int(head.get("ContentLength") or 0)==size
        except Exception:
            exists=False
        if not exists:
            cfg=TransferConfig(
                multipart_threshold=16*1024*1024,
                multipart_chunksize=16*1024*1024,
                max_concurrency=max(1,min(4,_materialize_concurrency())),
                max_io_queue=8,
                io_chunksize=1024*1024,
                use_threads=True,
            )
            _s3().upload_file(
                str(source),S3_BUCKET,key,
                ExtraArgs={
                    "ContentType":"application/octet-stream",
                    "Metadata":{
                        "gsf-upload-id":upload_id,
                        "gsf-original-name":original_name[:200],
                    },
                },
                Config=cfg,
            )
        marker=ROOT/"sessions"/sid/"media"/".direct_upload_ready.json"
        if marker.is_file():
            try:
                current=json.loads(marker.read_text(encoding="utf-8"))
            except Exception:
                current={}
            if isinstance(current,dict) and str(current.get("upload_id") or "")==upload_id:
                current.update({
                    "storage":"direct_fallback_bucket",
                    "bucket_key":key,
                    "analysis_key":analysis_key,
                    "persistent_at":time.time(),
                })
                _write_json_atomic(marker,current)
        try:
            _trigger_prescan({
                "key":key,
                "analysis_key":analysis_key,
                "engine_version":"v52-keyframe-turbo",
                "name":original_name,
                "size":size,
            })
        except Exception:
            pass
        try:
            rows=_draft_index_load(sid)
            if isinstance(rows,list):
                changed=False
                for row in rows:
                    if str((row or {}).get("source_upload_id") or "")==upload_id and not (row or {}).get("source_persistent"):
                        row["source_persistent"]=True
                        changed=True
                if changed:
                    _draft_index_save(sid,rows)
        except Exception as exc:
            print("GSF_DRAFT_INDEX_PERSIST_WARN",sid,upload_id,repr(str(exc)),flush=True)
        print("GSF_FALLBACK_SOURCE_PERSISTED",sid,upload_id,key,flush=True)
        return {"bucket_key":key,"analysis_key":analysis_key}
    except Exception as exc:
        print("GSF_FALLBACK_SOURCE_PERSIST_WARN",sid,upload_id,repr(str(exc)),flush=True)
        return {}

def _html(handler,status,body):
    raw=str(body).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type","text/html; charset=utf-8")
    handler.send_header("Content-Length",str(len(raw)))
    handler.send_header("Cache-Control","no-store")
    handler.end_headers()
    handler.wfile.write(raw)

def _redirect(handler,url):
    handler.send_response(302)
    handler.send_header("Location",str(url))
    handler.send_header("Cache-Control","no-store")
    handler.end_headers()

def _social_sid(handler):
    return _safe_id(handler.headers.get("X-GSF-Session-ID"))


def _editor_media_current(handler,sid):
    sid=_safe_id(sid)
    if not sid:
        _json(handler,400,{"ok":False,"error":"invalid session"})
        return
    session_root=(ROOT/"sessions"/sid).resolve()
    marker=session_root/"editor2027_current.txt"
    try:
        media=Path(marker.read_text(encoding="utf-8").strip()).resolve()
        media.relative_to(session_root)
        if not media.is_file():
            raise FileNotFoundError(str(media))
        rel=media.relative_to(session_root)
        media_url="/media/"+urllib.parse.quote(sid,safe="")+"/"+"/".join(
            urllib.parse.quote(part,safe="") for part in rel.parts
        )
        stat=media.stat()
        stamp=str(stat.st_size)+"-"+str(int(stat.st_mtime))
        print("GSF_EDITOR_MEDIA_REDIRECT",sid,media_url,flush=True)
        _redirect(handler,media_url+"?v="+urllib.parse.quote(stamp,safe=""))
    except Exception as exc:
        print("GSF_EDITOR_MEDIA_MISSING",sid,repr(str(exc)),flush=True)
        _json(handler,404,{"ok":False,"error":"editor media unavailable"})


def _tiktok_user_key(sid):
    sid=_safe_id(sid)
    return f"social-connections/{sid}/tiktok.json" if sid else ""


def _tiktok_user_load(sid):
    sid=_safe_id(sid)
    if not sid:
        return {}
    local=ROOT/"sessions"/sid/"social"/"tiktok_token.json"
    try:
        payload=json.loads(local.read_text(encoding="utf-8"))
        if isinstance(payload,dict) and payload.get("access_token"):
            return payload
    except Exception:
        pass
    if not _bucket_enabled():
        return {}
    try:
        obj=_s3().get_object(Bucket=S3_BUCKET,Key=_tiktok_user_key(sid))
        payload=json.loads(obj["Body"].read().decode("utf-8"))
        if isinstance(payload,dict):
            _tiktok_user_write_local(sid,payload)
            return payload
    except Exception:
        pass
    return {}


def _tiktok_user_write_local(sid,payload):
    sid=_safe_id(sid)
    if not sid:
        return
    social=ROOT/"sessions"/sid/"social"
    social.mkdir(parents=True,exist_ok=True)
    token=dict(payload or {})
    token.setdefault("_saved_at",time.time())
    _write_json_atomic(social/"tiktok_token.json",token)
    _write_json_atomic(social/"tiktok_config.json",{
        "client_key":TIKTOK_CLIENT_KEY,
        "client_secret":TIKTOK_CLIENT_SECRET,
    })


def _tiktok_user_save(sid,payload):
    sid=_safe_id(sid)
    if not sid:
        raise RuntimeError("sessione browser non valida")
    _tiktok_user_write_local(sid,payload)
    if not _bucket_enabled():
        raise RuntimeError("storage persistente non disponibile")
    _s3().put_object(
        Bucket=S3_BUCKET,
        Key=_tiktok_user_key(sid),
        Body=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
        CacheControl="no-store",
    )



def _youtube_user_key(sid):
    sid=_safe_id(sid)
    return f"social-connections/{sid}/youtube.json" if sid else ""


def _youtube_user_load(sid):
    sid=_safe_id(sid)
    if not sid:
        return {}
    local=ROOT/"sessions"/sid/"social"/"youtube_token.json"
    try:
        payload=json.loads(local.read_text(encoding="utf-8"))
        if isinstance(payload,dict) and payload.get("token"):
            return payload
    except Exception:
        pass
    if not _bucket_enabled():
        return {}
    try:
        obj=_s3().get_object(Bucket=S3_BUCKET,Key=_youtube_user_key(sid))
        payload=json.loads(obj["Body"].read().decode("utf-8"))
        if isinstance(payload,dict):
            _youtube_user_write_local(sid,payload)
            return payload
    except Exception:
        pass
    return {}


def _youtube_user_write_local(sid,payload):
    sid=_safe_id(sid)
    if not sid:
        return
    social=ROOT/"sessions"/sid/"social"
    social.mkdir(parents=True,exist_ok=True)
    token=dict(payload or {})
    _write_json_atomic(social/"youtube_token.json",token)


def _youtube_user_save(sid,payload):
    sid=_safe_id(sid)
    if not sid:
        raise RuntimeError("sessione browser non valida")
    _youtube_user_write_local(sid,payload)
    if not _bucket_enabled():
        raise RuntimeError("storage persistente non disponibile")
    _s3().put_object(
        Bucket=S3_BUCKET,
        Key=_youtube_user_key(sid),
        Body=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
        CacheControl="no-store",
    )




def _instagram_user_key(sid):
    sid=_safe_id(sid)
    return f"social-connections/{sid}/instagram.json" if sid else ""


def _instagram_user_load(sid):
    sid=_safe_id(sid)
    if not sid:
        return {}
    local=ROOT/"sessions"/sid/"social"/"instagram_config.json"
    try:
        payload=json.loads(local.read_text(encoding="utf-8"))
        if isinstance(payload,dict) and payload.get("ig_user_id") and payload.get("access_token"):
            return payload
    except Exception:
        pass
    if not _bucket_enabled():
        return {}
    try:
        obj=_s3().get_object(Bucket=S3_BUCKET,Key=_instagram_user_key(sid))
        payload=json.loads(obj["Body"].read().decode("utf-8"))
        if isinstance(payload,dict):
            _instagram_user_write_local(sid,payload)
            return payload
    except Exception:
        pass
    return {}


def _instagram_user_write_local(sid,payload):
    sid=_safe_id(sid)
    if not sid:
        return
    social=ROOT/"sessions"/sid/"social"
    social.mkdir(parents=True,exist_ok=True)
    _write_json_atomic(social/"instagram_config.json",dict(payload or {}))


def _instagram_user_save(sid,payload):
    sid=_safe_id(sid)
    if not sid:
        raise RuntimeError("sessione browser non valida")
    _instagram_user_write_local(sid,payload)
    if not _bucket_enabled():
        raise RuntimeError("storage persistente non disponibile")
    _s3().put_object(
        Bucket=S3_BUCKET,
        Key=_instagram_user_key(sid),
        Body=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
        CacheControl="no-store",
    )




# ------------------------------------------------------------------
# Creator Hub account foundation.
# Account identity is separate from publish permissions: users can enter with
# Google, Facebook or TikTok, then connect YouTube/Instagram/etc. independently.
# ------------------------------------------------------------------
def _creator_session_key(sid):
    sid=_safe_id(sid)
    return f"creator-sessions/{sid}.json" if sid else ""


def _creator_profile_key(account_id):
    account_id=_safe_id(account_id)
    return f"creator-accounts/{account_id}/profile.json" if account_id else ""


def _creator_identity_key(provider,provider_uid):
    provider=re.sub(r"[^a-z0-9_-]+","",str(provider or "").lower())[:24]
    provider_uid=str(provider_uid or "").strip()
    if not provider or not provider_uid:
        return ""
    digest=uuid.uuid5(uuid.NAMESPACE_URL,provider+":"+provider_uid).hex
    return f"creator-identities/{provider}/{digest}.json"


def _creator_account_load(sid):
    sid=_safe_id(sid)
    if not sid:
        return {}
    local=ROOT/"sessions"/sid/"account.json"
    try:
        payload=json.loads(local.read_text(encoding="utf-8"))
        if isinstance(payload,dict) and payload.get("account_id"):
            return payload
    except Exception:
        pass
    if not _bucket_enabled():
        return {}
    try:
        obj=_s3().get_object(Bucket=S3_BUCKET,Key=_creator_session_key(sid))
        session_payload=json.loads(obj["Body"].read().decode("utf-8"))
        account_id=_safe_id(session_payload.get("account_id",""))
        if not account_id:
            return {}
        obj=_s3().get_object(Bucket=S3_BUCKET,Key=_creator_profile_key(account_id))
        profile=json.loads(obj["Body"].read().decode("utf-8"))
        if isinstance(profile,dict):
            local.parent.mkdir(parents=True,exist_ok=True)
            _write_json_atomic(local,profile)
            return profile
    except Exception:
        pass
    return {}


def _creator_account_save(sid,profile):
    sid=_safe_id(sid)
    profile=dict(profile or {})
    account_id=_safe_id(profile.get("account_id",""))
    if not sid or not account_id:
        raise RuntimeError("account/session non validi")
    local=ROOT/"sessions"/sid/"account.json"
    local.parent.mkdir(parents=True,exist_ok=True)
    _write_json_atomic(local,profile)
    if _bucket_enabled():
        _s3().put_object(
            Bucket=S3_BUCKET,
            Key=_creator_profile_key(account_id),
            Body=json.dumps(profile,ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
            CacheControl="no-store",
        )
        _s3().put_object(
            Bucket=S3_BUCKET,
            Key=_creator_session_key(sid),
            Body=json.dumps({"account_id":account_id,"updated_at":time.time()}).encode("utf-8"),
            ContentType="application/json",
            CacheControl="no-store",
        )


def _draft_dir(sid):
    sid=_safe_id(sid)
    root=ROOT/"sessions"/sid/"drafts"
    root.mkdir(parents=True,exist_ok=True)
    return root

def _draft_key(sid,draft_id):
    sid=_safe_id(sid); draft_id=_safe_id(draft_id)
    return f"drafts/{sid}/{draft_id}.json" if sid and draft_id else ""

def _draft_index_key(sid):
    sid=_safe_id(sid)
    return f"drafts/{sid}/_index.json" if sid else ""

def _draft_index_path(sid):
    return _draft_dir(sid)/"_index.json"

def _draft_summary(draft):
    draft=dict(draft or {})
    source_ref=dict(draft.get("source_ref") or {})
    return {
        "id":_safe_id(draft.get("id","")),
        "title":str(draft.get("title") or "Bozza")[:180],
        "source_name":str(draft.get("source_name") or source_ref.get("name") or "Gameplay")[:160],
        "created_at":float(draft.get("created_at") or 0),
        "updated_at":float(draft.get("updated_at") or 0),
        "source_persistent":bool(draft.get("source_persistent") or source_ref.get("bucket_key")),
        "source_upload_id":str(draft.get("source_upload_id") or source_ref.get("upload_id") or "")[:80],
    }

def _draft_index_load(sid):
    sid=_safe_id(sid)
    if not sid:
        return None
    local=_draft_index_path(sid)
    try:
        payload=json.loads(local.read_text(encoding="utf-8"))
        if isinstance(payload,dict) and isinstance(payload.get("drafts"),list):
            return list(payload["drafts"])
    except Exception:
        pass
    if _bucket_enabled():
        try:
            obj=_s3().get_object(Bucket=S3_BUCKET,Key=_draft_index_key(sid))
            payload=json.loads(obj["Body"].read().decode("utf-8"))
            if isinstance(payload,dict) and isinstance(payload.get("drafts"),list):
                _write_json_atomic(local,payload)
                return list(payload["drafts"])
        except Exception:
            pass
    return None

def _draft_index_save(sid,rows):
    sid=_safe_id(sid)
    if not sid:
        return
    cleaned=[]
    seen=set()
    for row in sorted(list(rows or []),key=lambda x:float((x or {}).get("updated_at") or 0),reverse=True):
        summary=_draft_summary(row)
        did=summary.get("id")
        if not did or did in seen:
            continue
        seen.add(did)
        cleaned.append(summary)
        if len(cleaned)>=50:
            break
    payload={"version":2,"updated_at":time.time(),"drafts":cleaned}
    _write_json_atomic(_draft_index_path(sid),payload)
    if _bucket_enabled():
        try:
            _s3().put_object(
                Bucket=S3_BUCKET,Key=_draft_index_key(sid),
                Body=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
                ContentType="application/json",CacheControl="no-store",
            )
        except Exception as exc:
            print("GSF_DRAFT_INDEX_SAVE_WARN",sid,repr(str(exc)),flush=True)

def _draft_index_upsert(sid,draft):
    rows=_draft_index_load(sid)
    if rows is None:
        rows=_draft_list_legacy(sid)
    did=_safe_id((draft or {}).get("id",""))
    rows=[row for row in rows if _safe_id((row or {}).get("id",""))!=did]
    rows.append(_draft_summary(draft))
    _draft_index_save(sid,rows)

def _draft_index_remove(sid,draft_id):
    rows=_draft_index_load(sid)
    if rows is None:
        rows=_draft_list_legacy(sid)
    did=_safe_id(draft_id)
    _draft_index_save(sid,[row for row in rows if _safe_id((row or {}).get("id",""))!=did])

def _draft_save(sid,payload):
    sid=_safe_id(sid)
    if not sid:
        raise ValueError("sessione non valida")
    payload=dict(payload or {})
    state=payload.get("state") if isinstance(payload.get("state"),dict) else {}
    raw_state=json.dumps(state,ensure_ascii=False,separators=(",",":"),default=str)
    if len(raw_state)>900000:
        raise ValueError("bozza troppo grande")
    draft_id=_safe_id(payload.get("id","")) or ("draft_"+uuid.uuid4().hex[:16])
    now=time.time()
    source_name=str(payload.get("source_name") or state.get("gsf_source_name") or "Gameplay")[:160]
    desired_source=str(state.get("gsf_source_path") or state.get("gsf_editor_source_path") or "")
    source_ref={}
    try:
        marker=ROOT/"sessions"/sid/"media"/".direct_upload_ready.json"
        if marker.is_file():
            meta=json.loads(marker.read_text(encoding="utf-8"))
            if isinstance(meta,dict):
                marker_path=str(meta.get("path") or "")
                marker_upload=_safe_id(meta.get("upload_id",""))
                desired_match=re.search(r"_([0-9a-fA-F]{20})(\.[A-Za-z0-9]{1,10})$",Path(desired_source).name) if desired_source else None
                desired_upload=_safe_id(desired_match.group(1)) if desired_match else ""
                same_source=(
                    not desired_source
                    or (marker_path and os.path.abspath(marker_path)==os.path.abspath(desired_source))
                    or (desired_upload and marker_upload and desired_upload==marker_upload)
                )
                if same_source:
                    source_ref={
                        "name":str(meta.get("name") or source_name),
                        "size":int(meta.get("size") or 0),
                        "upload_id":str(meta.get("upload_id") or ""),
                        "storage":str(meta.get("storage") or ""),
                        "bucket_key":str(meta.get("bucket_key") or ""),
                        "analysis_key":str(meta.get("analysis_key") or ""),
                        "path":str(marker_path or desired_source),
                    }
    except Exception:
        source_ref={}
    source_path=Path(str(desired_source or source_ref.get("path") or ""))
    if _bucket_enabled() and not source_ref.get("bucket_key"):
        recovered_ref=_bucket_source_ref_from_path(sid,str(source_path))
        if recovered_ref:
            source_ref.update(recovered_ref)
        elif source_path.is_file() and _safe_id(source_ref.get("upload_id","")):
            threading.Thread(
                target=_persist_fallback_source_to_bucket,
                args=(sid,_safe_id(source_ref.get("upload_id","")),str(source_path),source_ref.get("name") or source_name,int(source_ref.get("size") or source_path.stat().st_size)),
                daemon=True,
            ).start()
    if source_path.is_file():
        try:
            linked=_draft_dir(sid)/(draft_id+"_source"+source_path.suffix.lower())
            if not linked.exists():
                os.link(source_path,linked)
            source_ref["draft_path"]=str(linked)
            source_ref.setdefault("path",str(source_path))
        except Exception:
            pass
    draft={
        "version":2,
        "id":draft_id,
        "title":str(payload.get("title") or ("Bozza · "+source_name))[:180],
        "source_name":source_name,
        "created_at":float(payload.get("created_at") or now),
        "updated_at":now,
        "state":state,
        "source_ref":source_ref,
        "state_bytes":len(raw_state.encode("utf-8")),
    }
    path=_draft_dir(sid)/(draft_id+".json")
    _write_json_atomic(path,draft)
    if _bucket_enabled():
        _s3().put_object(
            Bucket=S3_BUCKET,Key=_draft_key(sid,draft_id),
            Body=json.dumps(draft,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
            ContentType="application/json",CacheControl="no-store"
        )
    _draft_index_upsert(sid,draft)
    print("GSF_DRAFT_SAVED",sid,draft_id,"state_bytes="+str(draft["state_bytes"]),"persistent_source="+str(bool(source_ref.get("bucket_key"))),flush=True)
    return draft

def _draft_load(sid,draft_id):
    sid=_safe_id(sid); draft_id=_safe_id(draft_id)
    if not sid or not draft_id:
        return {}
    path=_draft_dir(sid)/(draft_id+".json")
    try:
        data=json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data,dict):
            return data
    except Exception:
        pass
    if _bucket_enabled():
        try:
            obj=_s3().get_object(Bucket=S3_BUCKET,Key=_draft_key(sid,draft_id))
            data=json.loads(obj["Body"].read().decode("utf-8"))
            if isinstance(data,dict):
                _write_json_atomic(path,data)
                return data
        except Exception:
            pass
    return {}

def _draft_list_legacy(sid):
    found={}
    try:
        for path in _draft_dir(sid).glob("draft_*.json"):
            try:
                data=json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data,dict) and data.get("id"):
                    found[str(data["id"])]=data
            except Exception:
                pass
    except Exception:
        pass
    if _bucket_enabled():
        try:
            rows=_s3().list_objects_v2(Bucket=S3_BUCKET,Prefix=f"drafts/{sid}/",MaxKeys=40).get("Contents") or []
            for row in rows:
                key=str(row.get("Key") or "")
                if not key.endswith(".json") or key.endswith("/_index.json"):
                    continue
                try:
                    obj=_s3().get_object(Bucket=S3_BUCKET,Key=key)
                    data=json.loads(obj["Body"].read().decode("utf-8"))
                    if isinstance(data,dict) and data.get("id"):
                        found[str(data["id"])]=data
                except Exception:
                    pass
        except Exception as exc:
            print("GSF_DRAFT_LEGACY_LIST_WARN",sid,repr(str(exc)),flush=True)
    rows=sorted(found.values(),key=lambda x:float(x.get("updated_at") or 0),reverse=True)[:50]
    if rows:
        _draft_index_save(sid,rows)
    return [_draft_summary(row) for row in rows]

def _draft_list(sid):
    sid=_safe_id(sid)
    if not sid:
        return []
    rows=_draft_index_load(sid)
    if rows is None:
        rows=_draft_list_legacy(sid)
    return sorted(
        [row for row in rows if isinstance(row,dict) and _safe_id(row.get("id",""))],
        key=lambda x:float(x.get("updated_at") or 0),
        reverse=True,
    )[:20]

def _draft_delete(sid,draft_id):
    sid=_safe_id(sid); draft_id=_safe_id(draft_id)
    if not sid or not draft_id:
        return False
    root=_draft_dir(sid)
    try:
        (root/(draft_id+".json")).unlink(missing_ok=True)
        for p in root.glob(draft_id+"_source.*"):
            p.unlink(missing_ok=True)
    except Exception:
        pass
    if _bucket_enabled():
        try:
            _s3().delete_object(Bucket=S3_BUCKET,Key=_draft_key(sid,draft_id))
        except Exception:
            pass
    _draft_index_remove(sid,draft_id)
    print("GSF_DRAFT_DELETED",sid,draft_id,flush=True)
    return True

def _draft_prepare_resume(sid,draft):
    state=dict(draft.get("state") or {})
    source_ref=dict(draft.get("source_ref") or {})
    source_name=str(draft.get("source_name") or source_ref.get("name") or "Gameplay")
    source_hint=str(source_ref.get("path") or state.get("gsf_source_path") or state.get("gsf_editor_source_path") or "")
    if _bucket_enabled() and not source_ref.get("bucket_key"):
        recovered_ref=_bucket_source_ref_from_path(sid,source_hint)
        if recovered_ref:
            source_ref.update(recovered_ref)
            try:
                healed=dict(draft)
                healed["source_ref"]=source_ref
                did=_safe_id(healed.get("id",""))
                _write_json_atomic(_draft_dir(sid)/(did+".json"),healed)
                _s3().put_object(
                    Bucket=S3_BUCKET,Key=_draft_key(sid,did),
                    Body=json.dumps(healed,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
                    ContentType="application/json",CacheControl="no-store",
                )
                _draft_index_upsert(sid,healed)
            except Exception as exc:
                print("GSF_DRAFT_SOURCE_REF_HEAL_WARN",sid,repr(str(exc)),flush=True)
    candidate=Path(str(source_ref.get("draft_path") or source_ref.get("path") or state.get("gsf_source_path") or ""))
    if not candidate.is_file() and _bucket_enabled() and source_ref.get("bucket_key"):
        try:
            original_name,safe_stem,ext=_safe_filename(source_ref.get("name") or source_name)
            upload_id=_safe_id(source_ref.get("upload_id","")) or uuid.uuid4().hex[:20]
            _materialize_bucket_object(
                sid,upload_id,str(source_ref.get("bucket_key") or ""),
                original_name,safe_stem,ext,int(source_ref.get("size") or 0),
                str(source_ref.get("analysis_key") or "")
            )
            marker=ROOT/"sessions"/sid/"media"/".direct_upload_ready.json"
            if marker.is_file():
                meta=json.loads(marker.read_text(encoding="utf-8"))
                candidate=Path(str(meta.get("path") or ""))
        except Exception as exc:
            print("GSF_DRAFT_RESTORE_SOURCE_WARN",repr(str(exc)),flush=True)
    if not candidate.is_file():
        print("GSF_DRAFT_RESUME_BLOCKED_SOURCE",sid,_safe_id(draft.get("id","")),source_hint,flush=True)
        return None

    state["gsf_source_path"]=str(candidate)
    state["gsf_editor_source_path"]=str(candidate)
    state["gsf_source_name"]=source_name
    state["gsf_manual_editor_open"]=True
    try:
        marker=ROOT/"sessions"/sid/"media"/".direct_upload_ready.json"
        current={}
        if marker.is_file():
            current=json.loads(marker.read_text(encoding="utf-8"))
            if not isinstance(current,dict):
                current={}
        current.update({
            "path":str(candidate),"name":source_name,
            "size":int(candidate.stat().st_size),
            "upload_id":str(source_ref.get("upload_id") or current.get("upload_id") or "draft"),
            "completed_at":time.time(),
            "storage":str(source_ref.get("storage") or "draft"),
            "bucket_key":str(source_ref.get("bucket_key") or ""),
            "analysis_key":str(source_ref.get("analysis_key") or ""),
        })
        _write_json_atomic(marker,current)
    except Exception:
        pass
    print("GSF_DRAFT_RESUME_READY",sid,_safe_id(draft.get("id","")),str(candidate),flush=True)
    return state

def _draft_cards_html(sid):
    drafts=_draft_list(sid)
    if not drafts:
        return '<div class="draftEmpty">Nessuna bozza salvata.</div>'
    rows=[]
    for draft in drafts:
        did=_safe_id(draft.get("id",""))
        title=html.escape(str(draft.get("title") or "Bozza"))
        source=html.escape(str(draft.get("source_name") or "Gameplay"))
        persistent=bool(draft.get("source_persistent"))
        try:
            updated=time.strftime("%d/%m · %H:%M",time.localtime(float(draft.get("updated_at") or 0)))
        except Exception:
            updated=""
        href="/drafts/resume?id="+urllib.parse.quote(did,safe="")
        delete_href="/drafts/delete?id="+urllib.parse.quote(did,safe="")
        safety='<span class="draftSafe">salvata</span>' if persistent else '<span class="draftSafe draftSafeSync">sincronizzazione</span>'
        rows.append(
            '<div class="draftCard"><div class="draftInfo"><strong>'+title+'</strong><span>'+source+' · '+html.escape(updated)+' · '+safety+
            '</span></div><div class="draftActions"><a class="draftOpen" href="'+href+'" onclick="return gsfResumeDraft(event,this.href)">RIPRENDI</a>'+
            '<a class="draftDelete" href="'+delete_href+'" onclick="return confirm(\'Eliminare questa bozza?\')">ELIMINA</a></div></div>'
        )
    return (
        '<div id="draftInlineMessage" class="draftInlineMessage" aria-live="polite"></div>'
        '<div class="draftGrid">'+"".join(rows)+'</div>'
        '<script>'
        'async function gsfResumeDraft(ev,url){ev.preventDefault();'
        'const m=document.getElementById("draftInlineMessage");if(m){m.textContent="Recupero bozza…";m.className="draftInlineMessage show";}'
        'try{const sep=url.includes("?")?"&":"?";const r=await fetch(url+sep+"json=1",{cache:"no-store",credentials:"same-origin"});const j=await r.json();'
        'if(!r.ok||!j.ok)throw new Error(j.error||"Bozza non disponibile");'
        'window.top.location.href=j.url||"/";}'
        'catch(e){if(m){m.textContent=e.message||"Bozza non disponibile. Riprova.";m.className="draftInlineMessage show error";}}'
        'return false;}'
        '</script>'
    )

def _creator_login(sid,provider,provider_uid,display_name="",email="",avatar=""):
    sid=_safe_id(sid)
    provider=re.sub(r"[^a-z0-9_-]+","",str(provider or "").lower())[:24]
    provider_uid=str(provider_uid or "").strip()
    if not sid or not provider or not provider_uid:
        raise RuntimeError("identità provider non valida")

    current=_creator_account_load(sid)
    account_id=_safe_id(current.get("account_id","")) if isinstance(current,dict) else ""

    identity_key=_creator_identity_key(provider,provider_uid)
    if not account_id and _bucket_enabled() and identity_key:
        try:
            obj=_s3().get_object(Bucket=S3_BUCKET,Key=identity_key)
            mapped=json.loads(obj["Body"].read().decode("utf-8"))
            account_id=_safe_id(mapped.get("account_id",""))
        except Exception:
            account_id=""

    if not account_id:
        account_id="usr_"+uuid.uuid4().hex[:24]

    profile={}
    if _bucket_enabled():
        try:
            obj=_s3().get_object(Bucket=S3_BUCKET,Key=_creator_profile_key(account_id))
            payload=json.loads(obj["Body"].read().decode("utf-8"))
            if isinstance(payload,dict):
                profile=payload
        except Exception:
            pass
    if not profile and isinstance(current,dict):
        profile=dict(current)

    providers=dict(profile.get("providers") or {})
    providers[provider]={
        "id":provider_uid,
        "display_name":str(display_name or "").strip(),
        "email":str(email or "").strip(),
        "avatar":str(avatar or "").strip(),
        "linked_at":time.time(),
    }
    profile.update({
        "account_id":account_id,
        "display_name":str(display_name or profile.get("display_name") or "Creator").strip(),
        "email":str(email or profile.get("email") or "").strip(),
        "avatar":str(avatar or profile.get("avatar") or "").strip(),
        "plan":str(profile.get("plan") or "FREE"),
        "creator_level":int(profile.get("creator_level") or 1),
        "shorts_created":int(profile.get("shorts_created") or 0),
        "shorts_published":int(profile.get("shorts_published") or 0),
        "providers":providers,
        "updated_at":time.time(),
        "created_at":float(profile.get("created_at") or time.time()),
    })
    _creator_account_save(sid,profile)
    if _bucket_enabled() and identity_key:
        _s3().put_object(
            Bucket=S3_BUCKET,
            Key=identity_key,
            Body=json.dumps({"account_id":account_id,"provider":provider}).encode("utf-8"),
            ContentType="application/json",
            CacheControl="no-store",
        )
    return profile


def _creator_logout(sid):
    sid=_safe_id(sid)
    if not sid:
        return
    try:
        (ROOT/"sessions"/sid/"account.json").unlink(missing_ok=True)
    except Exception:
        pass
    if _bucket_enabled():
        try:
            _s3().delete_object(Bucket=S3_BUCKET,Key=_creator_session_key(sid))
        except Exception:
            pass


def _creator_state_begin(sid,provider,prefix):
    sid=_safe_id(sid)
    if not sid:
        raise RuntimeError("sessione browser non valida")
    state=str(prefix)+secrets.token_urlsafe(28)
    state_dir=ROOT/"social_oauth"
    state_dir.mkdir(parents=True,exist_ok=True)
    _write_json_atomic(state_dir/(state+".json"),{
        "created":time.time(),
        "sid":sid,
        "provider":str(provider),
    })
    return state


def _creator_state_finish(state,prefix):
    state=re.sub(r"[^A-Za-z0-9_-]+","",str(state or ""))[:180]
    if not state.startswith(prefix):
        return {}
    state_file=ROOT/"social_oauth"/(state+".json")
    try:
        pending=json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        pending={}
    try:
        state_file.unlink(missing_ok=True)
    except Exception:
        pass
    created=float(pending.get("created",0) or 0)
    if not created or time.time()-created>900:
        return {}
    return pending if isinstance(pending,dict) else {}


def _oauth_json(url,method="GET",data=None,headers=None,timeout=45):
    req=urllib.request.Request(
        str(url),
        data=data,
        headers=dict(headers or {}),
        method=method,
    )
    with urllib.request.urlopen(req,timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _creator_google_start(handler,sid):
    if not (PUBLIC_APP_URL and YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET):
        _html(handler,503,_creator_page(sid,"Accesso Google non ancora configurato sul server."))
        return
    try:
        state=_creator_state_begin(sid,"google","gsfacg_")
    except Exception as exc:
        _html(handler,400,str(exc))
        return
    params={
        "client_id":YOUTUBE_CLIENT_ID,
        "redirect_uri":PUBLIC_APP_URL,
        "response_type":"code",
        "scope":"openid email profile",
        "access_type":"online",
        "include_granted_scopes":"true",
        "prompt":"select_account",
        "state":state,
    }
    _redirect(handler,"https://accounts.google.com/o/oauth2/v2/auth?"+urllib.parse.urlencode(params))


def _creator_google_callback(handler,query):
    code=str((query.get("code") or [""])[0] or "")
    state=str((query.get("state") or [""])[0] or "")
    pending=_creator_state_finish(state,"gsfacg_")
    sid=_safe_id(pending.get("sid",""))
    if not sid:
        _html(handler,400,"Accesso Google scaduto o non valido.")
        return
    err=str((query.get("error_description") or query.get("error") or [""])[0] or "")
    if err or not code:
        _html(handler,400,_creator_page(sid,"Google: "+(err or "autorizzazione non completata")))
        return
    try:
        form=urllib.parse.urlencode({
            "client_id":YOUTUBE_CLIENT_ID,
            "client_secret":YOUTUBE_CLIENT_SECRET,
            "code":code,
            "grant_type":"authorization_code",
            "redirect_uri":PUBLIC_APP_URL,
        }).encode("utf-8")
        token=_oauth_json(
            "https://oauth2.googleapis.com/token",
            method="POST",
            data=form,
            headers={"Content-Type":"application/x-www-form-urlencoded"},
        )
        access=str(token.get("access_token","") or "")
        if not access:
            raise RuntimeError("Google non ha restituito un access token")
        info=_oauth_json(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization":"Bearer "+access},
        )
        uid=str(info.get("sub","") or "")
        if not uid:
            raise RuntimeError("Profilo Google non disponibile")
        _creator_login(
            sid,"google",uid,
            display_name=info.get("name",""),
            email=info.get("email",""),
            avatar=info.get("picture",""),
        )
        _redirect(handler,"/account")
    except Exception as exc:
        _html(handler,500,_creator_page(sid,"Accesso Google fallito: "+str(exc)[:220]))


def _creator_facebook_start(handler,sid):
    if not (PUBLIC_APP_URL and META_APP_ID and META_APP_SECRET):
        _html(handler,503,_creator_page(sid,"Accesso Facebook non ancora configurato sul server."))
        return
    try:
        state=_creator_state_begin(sid,"facebook","gsfacf_")
    except Exception as exc:
        _html(handler,400,str(exc))
        return
    params={
        "client_id":META_APP_ID,
        "redirect_uri":PUBLIC_APP_URL,
        "state":state,
        "response_type":"code",
        "scope":"public_profile,email",
    }
    _redirect(handler,"https://www.facebook.com/dialog/oauth?"+urllib.parse.urlencode(params))


def _creator_facebook_callback(handler,query):
    code=str((query.get("code") or [""])[0] or "")
    state=str((query.get("state") or [""])[0] or "")
    pending=_creator_state_finish(state,"gsfacf_")
    sid=_safe_id(pending.get("sid",""))
    if not sid:
        _html(handler,400,"Accesso Facebook scaduto o non valido.")
        return
    err=str((query.get("error_description") or query.get("error") or [""])[0] or "")
    if err or not code:
        _html(handler,400,_creator_page(sid,"Facebook: "+(err or "autorizzazione non completata")))
        return
    try:
        token_url="https://graph.facebook.com/oauth/access_token?"+urllib.parse.urlencode({
            "client_id":META_APP_ID,
            "client_secret":META_APP_SECRET,
            "redirect_uri":INSTAGRAM_REDIRECT_URI,
            "code":code,
        })
        token=_oauth_json(token_url)
        access=str(token.get("access_token","") or "")
        if not access:
            raise RuntimeError("Facebook non ha restituito un access token")
        info_url="https://graph.facebook.com/me?"+urllib.parse.urlencode({
            "fields":"id,name,email,picture",
            "access_token":access,
        })
        info=_oauth_json(info_url)
        uid=str(info.get("id","") or "")
        if not uid:
            raise RuntimeError("Profilo Facebook non disponibile")
        picture=((info.get("picture") or {}).get("data") or {}).get("url","") if isinstance(info.get("picture"),dict) else ""
        _creator_login(
            sid,"facebook",uid,
            display_name=info.get("name",""),
            email=info.get("email",""),
            avatar=picture,
        )
        _redirect(handler,"/account")
    except Exception as exc:
        _html(handler,500,_creator_page(sid,"Accesso Facebook fallito: "+str(exc)[:220]))


def _creator_tiktok_start(handler,sid):
    if not (PUBLIC_APP_URL and TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET):
        _html(handler,503,_creator_page(sid,"Accesso TikTok non ancora configurato sul server."))
        return
    try:
        state=_creator_state_begin(sid,"tiktok","gsfact_")
    except Exception as exc:
        _html(handler,400,str(exc))
        return
    params={
        "client_key":TIKTOK_CLIENT_KEY,
        "response_type":"code",
        "scope":"user.info.basic",
        "redirect_uri":PUBLIC_APP_URL,
        "state":state,
    }
    _redirect(handler,"https://www.tiktok.com/v2/auth/authorize/?"+urllib.parse.urlencode(params))


def _creator_tiktok_callback(handler,query):
    code=str((query.get("code") or [""])[0] or "")
    state=str((query.get("state") or [""])[0] or "")
    pending=_creator_state_finish(state,"gsfact_")
    sid=_safe_id(pending.get("sid",""))
    if not sid:
        _html(handler,400,"Accesso TikTok scaduto o non valido.")
        return
    err=str((query.get("error_description") or query.get("error") or [""])[0] or "")
    if err or not code:
        _html(handler,400,_creator_page(sid,"TikTok: "+(err or "autorizzazione non completata")))
        return
    try:
        form=urllib.parse.urlencode({
            "client_key":TIKTOK_CLIENT_KEY,
            "client_secret":TIKTOK_CLIENT_SECRET,
            "code":code,
            "grant_type":"authorization_code",
            "redirect_uri":PUBLIC_APP_URL,
        }).encode("utf-8")
        token=_oauth_json(
            "https://open.tiktokapis.com/v2/oauth/token/",
            method="POST",
            data=form,
            headers={"Content-Type":"application/x-www-form-urlencoded"},
        )
        access=str(token.get("access_token","") or "")
        uid=str(token.get("open_id","") or "")
        name=""
        avatar=""
        if access:
            try:
                info=_oauth_json(
                    "https://open.tiktokapis.com/v2/user/info/?fields=open_id,display_name,avatar_url",
                    headers={"Authorization":"Bearer "+access},
                )
                user=((info.get("data") or {}).get("user") or {}) if isinstance(info,dict) else {}
                uid=str(user.get("open_id","") or uid)
                name=str(user.get("display_name","") or "")
                avatar=str(user.get("avatar_url","") or "")
            except Exception:
                pass
        if not access or not uid:
            raise RuntimeError("Profilo TikTok non disponibile")
        _creator_login(sid,"tiktok",uid,display_name=name or "TikTok Creator",avatar=avatar)
        _redirect(handler,"/account")
    except Exception as exc:
        _html(handler,500,_creator_page(sid,"Accesso TikTok fallito: "+str(exc)[:220]))



def _auto_highlights_rows_for_account(account_id,limit=12):
    account_id=_safe_id(account_id)
    if not account_id or not _bucket_enabled():
        return []
    rows=[]
    per_provider=max(1,min(25,int(limit or 12)))
    for provider in ("youtube","twitch"):
        prefix=f"auto-highlights/{provider}/{account_id}/"
        try:
            listing=_s3().list_objects_v2(
                Bucket=S3_BUCKET,
                Prefix=prefix,
                MaxKeys=per_provider,
            )
        except Exception:
            continue
        for item in list((listing or {}).get("Contents") or []):
            key=str((item or {}).get("Key") or "")
            if not key.endswith(".json"):
                continue
            try:
                obj=_s3().get_object(Bucket=S3_BUCKET,Key=key)
                payload=json.loads(obj["Body"].read().decode("utf-8"))
                if not isinstance(payload,dict):
                    continue
                payload["_key"]=key
                payload["_provider"]=provider
                rows.append(payload)
            except Exception:
                continue
    rows.sort(key=lambda x:float((x or {}).get("created_at") or 0),reverse=True)
    return rows[:max(1,min(24,int(limit or 12)))]


def _auto_highlights_cards_html(sid):
    profile=_creator_account_load(sid)
    account_id=_safe_id((profile or {}).get("account_id",""))
    if not account_id:
        return '<div class="auto"><div class="auto-k">AUTO HIGHLIGHTS</div><div class="auto-title">Collega il tuo Creator Hub</div><div class="auto-sub">Accedi per vedere qui gli highlight trovati automaticamente dalle tue live.</div></div>'
    rows=_auto_highlights_rows_for_account(account_id,limit=12)
    if not rows:
        return '<div class="auto"><div class="auto-k">AUTO HIGHLIGHTS</div><div class="auto-title">Nessun highlight automatico ancora</div><div class="auto-sub">Quando una live collegata viene analizzata, GSF salverà qui i timestamp migliori senza renderizzare tutto il VOD.</div></div>'
    cards=[]
    for row in rows:
        provider=str(row.get("provider") or row.get("_provider") or "live").upper()
        title=html.escape(str(row.get("title") or "Live")[:140])
        candidates=list(row.get("candidates") or [])
        top=candidates[0] if candidates and isinstance(candidates[0],dict) else {}
        reason=html.escape(str(top.get("reason") or top.get("event") or "HIGHLIGHT").replace("_"," ")[:60])
        confidence=max(0,min(100,int(round(float(top.get("confidence") or 0.0)*100))))
        count=len(candidates)
        duration=int(row.get("target_duration") or (top.get("duration") if isinstance(top,dict) else 0) or 0)
        cards.append(
            '<div class="autoCard">'
            f'<div class="autoCardTop"><span class="autoProvider">{html.escape(provider)}</span><span class="autoReady">PRONTO</span></div>'
            f'<strong>{title}</strong>'
            f'<div class="autoMeta">{count} momenti · {duration}s · top: {reason} · {confidence}%</div>'
            '</div>'
        )
    return '<div class="auto"><div class="auto-k">AUTO HIGHLIGHTS PRONTI</div><div class="auto-title">GSF ha già trovato i momenti forti.</div><div class="auto-sub">Sono salvati come timestamp e metadati: nessun render inutile del VOD completo.</div><div class="autoGrid">'+"".join(cards)+'</div></div>'

def _creator_page(sid,message=""):
    profile=_creator_account_load(sid)
    if not profile:
        msg=f'<div class="notice">{html.escape(message)}</div>' if message else ""
        drafts_html=_draft_cards_html(sid)
        google_disabled="" if (YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET) else " unavailable"
        facebook_disabled="" if (META_APP_ID and META_APP_SECRET) else " unavailable"
        tiktok_disabled="" if (TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET) else " unavailable"
        return f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gaming Shorts Factory · Creator Hub</title>
<style>
*{{box-sizing:border-box}} body{{font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#f7fbff,#eef5fb);color:#17324d;margin:0;min-height:100vh}}
main{{max-width:860px;margin:0 auto;padding:22px 16px 34px}} .brand{{text-align:center;color:#648096;font-size:12px;font-weight:900;letter-spacing:.08em;margin-bottom:12px}}
.profile{{background:#fff;border:1px solid #dae8f2;border-radius:26px;padding:22px;box-shadow:0 16px 44px #193f5c12}}
.hero{{text-align:center;padding:4px 0 8px}} h1{{margin:0 0 6px;font-size:28px}} .lead{{color:#6b8295;line-height:1.45;margin:0 auto 16px;max-width:560px}}
.notice{{background:#eef8ff;border:1px solid #d2e9f8;border-radius:14px;padding:11px 13px;margin:0 0 15px;color:#426a86}}
.loginbox{{background:#f8fbfe;border:1px solid #e0ebf3;border-radius:18px;padding:14px}} .login-title{{font-size:13px;font-weight:900;text-align:center;margin-bottom:10px;color:#58768d}}
.providers{{display:grid;grid-template-columns:1fr;gap:9px}} .provider{{display:flex;align-items:center;justify-content:center;gap:9px;text-decoration:none;border:1px solid #d7e5ef;background:#fff;color:#1f3a50;border-radius:14px;padding:12px 14px;font-weight:850;box-shadow:0 5px 14px #325b7910}}
.provider .logo{{width:23px;height:23px;border-radius:8px;display:grid;place-items:center;background:#eff6fb;font-weight:950}} .provider.unavailable{{opacity:.45;pointer-events:none}}
h2{{font-size:16px;margin:20px 0 10px}} .socials{{display:grid;grid-template-columns:1fr 1fr;gap:9px}} .social{{color:#7890a2;background:#f8fbfe;border:1px solid #e0ebf3;border-radius:16px;padding:14px;display:flex;justify-content:space-between;align-items:center;font-size:12px}} .social strong{{font-size:13px;color:#496b83}} .social span{{font-weight:850}}
.auto{{background:linear-gradient(135deg,#eff9ff,#f3efff);border:1px solid #d7e7f1;border-radius:18px;padding:15px}} .auto-k{{font-size:11px;font-weight:950;letter-spacing:.08em;color:#607da0}} .auto-title{{font-size:18px;font-weight:950;margin:3px 0 5px}} .auto-sub{{font-size:12px;color:#73889b;line-height:1.45}}
.future{{border:1px dashed #cadde9;border-radius:17px;padding:14px;color:#7b90a1;font-size:12px;line-height:1.45}}
.draftGrid{{display:grid;gap:9px}}.draftCard{{display:flex;align-items:center;justify-content:space-between;gap:12px;background:#f8fbfe;border:1px solid #dce9f2;border-radius:16px;padding:13px 14px}}.draftInfo{{display:flex;flex-direction:column;gap:3px;min-width:0}}.draftInfo strong{{font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.draftInfo span{{font-size:10px;color:#7e92a2}}.draftActions{{display:flex;align-items:center;gap:6px;flex-wrap:wrap}}.draftOpen{{text-decoration:none;color:#356f91;background:linear-gradient(135deg,#eef8ff,#f1eeff);border:1px solid #cfe5f3;border-radius:12px;padding:8px 10px;font-size:10px;font-weight:900;box-shadow:0 4px 10px #345d7810}}.draftDelete{{text-decoration:none;color:#8b6170;background:linear-gradient(135deg,#fff7f9,#f8eef3);border:1px solid #ead5dd;border-radius:12px;padding:8px 10px;font-size:10px;font-weight:900;box-shadow:0 4px 10px #6f3e5110}}.draftEmpty{{font-size:12px;color:#71899a;background:#f8fbfe;border:1px dashed #cbdde9;border-radius:16px;padding:14px;line-height:1.45}}.draftSafe{{display:inline-flex;align-items:center;padding:2px 6px;border-radius:999px;background:#e9f8f0;color:#4f8468;font-size:9px;font-weight:900}}.draftSafeSync{{background:#fff7df;color:#9a7a37}}.draftInlineMessage{{display:none;margin:0 0 9px;padding:9px 11px;border-radius:12px;background:#eef8ff;border:1px solid #d3eaf8;color:#4b7189;font-size:11px;font-weight:750}}.draftInlineMessage.show{{display:block}}.draftInlineMessage.error{{background:#fff2f2;border-color:#f0d3d3;color:#916060}}.back{{display:block;text-align:center;margin:18px auto 0;color:#6d8799;text-decoration:none;font-size:11px;font-weight:800}}
.small{{font-size:11px;color:#8a9dab;text-align:center;line-height:1.45;margin:11px 0 0}}
@media(min-width:640px){{.providers{{grid-template-columns:1fr 1fr 1fr}}}}
@media(max-width:560px){{.socials{{grid-template-columns:1fr}}}}
</style></head><body><main><div class="brand">GAMING SHORTS FACTORY</div><div class="profile">
<div class="hero"><h1>Creator Hub</h1><p class="lead">Il tuo spazio per profilo, social, Short, livelli e Auto Highlights.</p></div>
{msg}
<div class="loginbox"><div class="login-title">ACCEDI AL CREATOR HUB</div><div class="providers">
<a class="provider{google_disabled}" href="/account/google/start"><span class="logo">G</span><span>Google</span></a>
<a class="provider{facebook_disabled}" href="/account/facebook/start"><span class="logo">f</span><span>Facebook</span></a>
<a class="provider{tiktok_disabled}" href="/account/tiktok/start"><span class="logo">♪</span><span>TikTok</span></a>
</div><p class="small">Il permesso YouTube per pubblicare viene richiesto separatamente quando colleghi il canale.</p></div>
<h2>Le tue bozze</h2>{drafts_html}<h2>I tuoi social</h2><div class="socials"><div class="social"><strong>YouTube</strong><span>Accedi per collegare</span></div><div class="social"><strong>TikTok</strong><span>Accedi per collegare</span></div><div class="social"><strong>Instagram</strong><span>Accedi per collegare</span></div><div class="social"><strong>Facebook</strong><span>Accedi per collegare</span></div></div>
<h2>Auto Highlights</h2><div class="auto"><div class="auto-k">AUTO HIGHLIGHTS</div><div class="auto-title">Tu fai la live. GSF trova i momenti da pubblicare.</div><div class="auto-sub">Accedi al Creator Hub per collegare i tuoi account e gestire le live.</div></div>
<h2>Prossimamente</h2><div class="future">Storico Short · Cloud · Piano Pro · Crediti AI · Achievement · Classifica Creator.</div>
<a class="back" href="/" onclick="if(window.parent!==window){{window.parent.location.hash='';return false;}}window.location.href='/';return false;">← Torna alla pagina principale</a>
</div></main></body></html>"""
    providers=dict(profile.get("providers") or {})
    name=html.escape(str(profile.get("display_name") or "Creator"))
    email=html.escape(str(profile.get("email") or ""))
    plan=html.escape(str(profile.get("plan") or "FREE"))
    level=int(profile.get("creator_level") or 1)
    shorts_created=int(profile.get("shorts_created") or 0)
    shorts_published=int(profile.get("shorts_published") or 0)
    avatar=str(profile.get("avatar") or "")
    avatar_html=(f'<img class="avatar" src="{html.escape(avatar,quote=True)}" alt="">' if avatar else '<div class="avatar fallback">C</div>')

    yt=bool((_youtube_user_load(sid) or {}).get("token"))
    tt=bool((_tiktok_user_load(sid) or {}).get("access_token"))
    igcfg=_instagram_user_load(sid) or {}
    ig=bool(igcfg.get("ig_user_id") and igcfg.get("access_token"))
    fb="facebook" in providers
    connected=sum([yt,tt,ig,fb])

    def social_card(label,connected_now,url):
        status="Collegato ✓" if connected_now else "Collega"
        cls=" connected" if connected_now else ""
        return f'<a class="social{cls}" href="{url}"><strong>{html.escape(label)}</strong><span>{status}</span></a>'

    socials=(
        social_card("YouTube",yt,"/social-connect/youtube/start")
        +social_card("TikTok",tt,"/social-connect/tiktok/start")
        +social_card("Instagram",ig,"/social-connect/instagram/start")
        +social_card("Facebook",fb,"/account/facebook/start")
    )
    provider_badges="".join(
        f'<span class="providerBadge">{html.escape(k.title())} ✓</span>'
        for k in providers.keys()
    ) or '<span class="providerBadge">Profilo attivo</span>'
    msg=f'<div class="notice">{html.escape(message)}</div>' if message else ""
    drafts_html=_draft_cards_html(sid)
    auto_highlights_html=_auto_highlights_cards_html(sid)

    return f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gaming Shorts Factory · Creator Hub</title>
<style>
*{{box-sizing:border-box}} body{{font-family:Inter,Arial,sans-serif;background:linear-gradient(180deg,#f7fbff,#eef5fb);color:#17324d;margin:0;min-height:100vh}}
main{{max-width:860px;margin:0 auto;padding:24px 16px 48px}} .top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}} .brand{{font-size:12px;font-weight:900;letter-spacing:.08em;color:#648096}} .back{{color:#477692;text-decoration:none;font-weight:800;font-size:13px}}
.profile{{background:#fff;border:1px solid #dae8f2;border-radius:26px;padding:22px;box-shadow:0 16px 44px #193f5c12}} .who{{display:flex;align-items:center;gap:14px}} .avatar{{width:58px;height:58px;border-radius:18px;object-fit:cover;background:#edf6fc}} .fallback{{display:grid;place-items:center;font-weight:950;font-size:22px}}
.name{{font-size:22px;font-weight:900}} .mail{{color:#7990a1;font-size:13px;margin-top:3px}} .badge{{display:inline-flex;margin-top:7px;background:linear-gradient(135deg,#4fade8,#647fe5);color:#fff;border-radius:999px;padding:5px 10px;font-size:11px;font-weight:900}}
.providerBadges{{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}} .providerBadge{{background:#eff6fb;color:#58768d;border-radius:999px;padding:5px 9px;font-size:10px;font-weight:800}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin:18px 0}} .stat{{background:#f7fbfe;border:1px solid #e0ebf3;border-radius:16px;padding:13px;text-align:center}} .stat b{{display:block;font-size:20px}} .stat span{{font-size:10px;color:#7e91a1;font-weight:800}}
.level{{background:linear-gradient(135deg,#eff9ff,#f2efff);border:1px solid #d7e7f1;border-radius:18px;padding:14px;margin-bottom:18px}} .levelHead{{display:flex;justify-content:space-between;font-weight:850;font-size:12px}} .bar{{height:8px;background:#dbe8f1;border-radius:999px;margin-top:9px;overflow:hidden}} .bar i{{display:block;width:18%;height:100%;background:linear-gradient(90deg,#4fade8,#647fe5);border-radius:999px}}
h2{{font-size:16px;margin:20px 0 10px}} .socials{{display:grid;grid-template-columns:1fr 1fr;gap:9px}} .social{{text-decoration:none;color:#294a62;background:#fff;border:1px solid #dbe8f1;border-radius:16px;padding:14px;display:flex;justify-content:space-between;align-items:center;font-size:12px}} .social strong{{font-size:13px}} .social span{{color:#5a7d96;font-weight:850}} .social.connected{{background:#f1fbf7;border-color:#cfeadf}} .social.connected span{{color:#3c8968}}
.notice{{background:#eef8ff;border:1px solid #d2e9f8;border-radius:14px;padding:11px 13px;margin:0 0 15px;color:#426a86}} .auto{{background:linear-gradient(135deg,#eff9ff,#f3efff);border:1px solid #d7e7f1;border-radius:18px;padding:15px}} .auto-k{{font-size:11px;font-weight:950;letter-spacing:.08em;color:#607da0}} .auto-title{{font-size:17px;font-weight:950;margin:3px 0 5px}} .auto-sub{{font-size:12px;color:#73889b;line-height:1.45}} .future{{border:1px dashed #cadde9;border-radius:17px;padding:14px;color:#7b90a1;font-size:12px;line-height:1.45}}
.draftGrid{{display:grid;gap:9px}}.draftCard{{display:flex;align-items:center;justify-content:space-between;gap:12px;background:#f8fbfe;border:1px solid #dce9f2;border-radius:16px;padding:13px 14px}}.draftInfo{{display:flex;flex-direction:column;gap:3px;min-width:0}}.draftInfo strong{{font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.draftInfo span{{font-size:10px;color:#7e92a2}}.draftActions{{display:flex;align-items:center;gap:6px;flex-wrap:wrap}}.draftOpen{{text-decoration:none;color:#356f91;background:linear-gradient(135deg,#eef8ff,#f1eeff);border:1px solid #cfe5f3;border-radius:12px;padding:8px 10px;font-size:10px;font-weight:900;box-shadow:0 4px 10px #345d7810}}.draftDelete{{text-decoration:none;color:#8b6170;background:linear-gradient(135deg,#fff7f9,#f8eef3);border:1px solid #ead5dd;border-radius:12px;padding:8px 10px;font-size:10px;font-weight:900;box-shadow:0 4px 10px #6f3e5110}}.draftEmpty{{font-size:12px;color:#71899a;background:#f8fbfe;border:1px dashed #cbdde9;border-radius:16px;padding:14px;line-height:1.45}}.draftSafe{{display:inline-flex;align-items:center;padding:2px 6px;border-radius:999px;background:#e9f8f0;color:#4f8468;font-size:9px;font-weight:900}}.draftSafeSync{{background:#fff7df;color:#9a7a37}}.draftInlineMessage{{display:none;margin:0 0 9px;padding:9px 11px;border-radius:12px;background:#eef8ff;border:1px solid #d3eaf8;color:#4b7189;font-size:11px;font-weight:750}}.draftInlineMessage.show{{display:block}}.draftInlineMessage.error{{background:#fff2f2;border-color:#f0d3d3;color:#916060}}.logout{{display:block;text-align:center;color:#8a6170;text-decoration:none;font-size:12px;font-weight:800;margin-top:18px}} .back-bottom{{display:block;text-align:center;color:#6d8799;text-decoration:none;font-size:11px;font-weight:800;margin-top:14px}}
.autoGrid{{display:grid;gap:8px;margin-top:12px}} .autoCard{{background:#ffffffc9;border:1px solid #dce8f2;border-radius:14px;padding:11px 12px}} .autoCardTop{{display:flex;justify-content:space-between;gap:8px;margin-bottom:5px}} .autoProvider,.autoReady{{font-size:9px;font-weight:950;letter-spacing:.06em}} .autoProvider{{color:#5b7891}} .autoReady{{color:#3f8a69;background:#eaf8f1;border-radius:999px;padding:3px 7px}} .autoCard strong{{display:block;font-size:12px}} .autoMeta{{font-size:10px;color:#70879a;margin-top:4px;line-height:1.4}}
@media(max-width:560px){{.stats{{grid-template-columns:1fr 1fr 1fr}} .stat{{padding:10px 5px}} .stat b{{font-size:17px}} .socials{{grid-template-columns:1fr}}}}
</style></head><body><main>
<div class="top"><div class="brand">GAMING SHORTS FACTORY</div></div>
<div class="profile">{msg}<div class="who">{avatar_html}<div><div class="name">{name}</div><div class="mail">{email}</div><span class="badge">{plan}</span><div class="providerBadges">{provider_badges}</div></div></div>
<div class="stats"><div class="stat"><b>{shorts_created}</b><span>SHORT CREATI</span></div><div class="stat"><b>{shorts_published}</b><span>PUBBLICATI</span></div><div class="stat"><b>{connected}/4</b><span>SOCIAL</span></div></div>
<div class="level"><div class="levelHead"><span>Creator Level {level} · Rookie</span><span>18%</span></div><div class="bar"><i></i></div></div>
<h2>Le tue bozze</h2>{drafts_html}<h2>I tuoi social</h2><div class="socials">{socials}</div>
<h2>Auto Highlights</h2>{auto_highlights_html}
<h2>Prossimamente</h2><div class="future">Storico Short · Cloud · Piano Pro · Crediti AI · Achievement · Classifica Creator.</div>
<a class="logout" href="/account/logout">Esci dal Creator Hub</a><a class="back-bottom" href="/" onclick="if(window.parent!==window){{window.parent.location.hash='';return false;}}window.location.href='/';return false;">← Torna alla pagina principale</a>
</div></main></body></html>"""


def _social_page(sid,message=""):
    tiktok_connected=bool((_tiktok_user_load(sid) or {}).get("access_token"))
    youtube_connected=bool((_youtube_user_load(sid) or {}).get("token"))
    instagram_connected=bool(
        (_instagram_user_load(sid) or {}).get("ig_user_id")
        and (_instagram_user_load(sid) or {}).get("access_token")
    )
    tiktok_badge="✅ TikTok collegato" if tiktok_connected else "TikTok non ancora collegato"
    youtube_badge="✅ YouTube collegato" if youtube_connected else "YouTube non ancora collegato"
    instagram_badge="✅ Instagram collegato" if instagram_connected else "Instagram non ancora collegato"
    tiktok_button="Ricollega TikTok" if tiktok_connected else "Collega TikTok"
    youtube_button="Ricollega YouTube" if youtube_connected else "Collega YouTube"
    instagram_button="Ricollega Instagram" if instagram_connected else "Collega Instagram"
    msg=f'<div class="msg">{html.escape(message)}</div>' if message else ""
    instagram_note=(
        ""
        if (INSTAGRAM_APP_ID and INSTAGRAM_APP_SECRET) or (META_APP_ID and META_APP_SECRET)
        else '<div class="note">Configurazione Instagram non ancora presente sul server.</div>'
    )
    return f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gaming Shorts Factory · Collega social</title>
<style>
body{{font-family:Arial,sans-serif;background:#f5f8fc;color:#17324d;margin:0}}
main{{max-width:720px;margin:6vh auto;padding:24px}}
.card{{background:white;border-radius:24px;padding:30px;box-shadow:0 12px 40px #15304a18}}
h1{{margin:0 0 8px}} p{{line-height:1.5;color:#5c7185}}
.grid{{display:grid;grid-template-columns:1fr;gap:14px;margin-top:18px}}
.social{{border:1px solid #dbe7f1;border-radius:18px;padding:18px}}
.btn{{display:block;text-align:center;text-decoration:none;background:#1687ff;color:white;font-weight:700;
padding:15px 18px;border-radius:14px;margin-top:14px}}
.status{{padding:12px 14px;border-radius:14px;background:#eef7ff;margin:14px 0}}
.msg{{padding:12px 14px;border-radius:14px;background:#eef8ee;margin:14px 0}}
.note{{font-size:13px;color:#8a6d3b;background:#fff8e7;border-radius:10px;padding:10px 12px;margin:8px 0}}
.small{{font-size:13px;color:#71869a}}
.close{{display:block;width:100%;border:0;background:#17324d;color:white;font-weight:750;padding:15px 18px;
border-radius:14px;margin-top:22px;cursor:pointer;font-size:15px}}
.back{{display:block;text-align:center;margin-top:12px;color:#315c80;text-decoration:none}}
</style></head><body><main><div class="card">
<h1>Collega i social</h1>
<p>Collega gli account qui. Gaming Shorts Factory resta aperta nell'altra scheda e il video non viene toccato.</p>
{msg}
<div class="grid">
  <div class="social">
    <strong>TikTok</strong>
    <div class="status">{tiktok_badge}</div>
    <a class="btn" href="/social-connect/tiktok/start">{tiktok_button}</a>
  </div>
  <div class="social">
    <strong>YouTube</strong>
    <div class="status">{youtube_badge}</div>
    <a class="btn" href="/social-connect/youtube/start">{youtube_button}</a>
  </div>
  <div class="social">
    <strong>Instagram</strong>
    <div class="status">{instagram_badge}</div>
    {instagram_note}
    <a class="btn" href="/social-connect/instagram/start">{instagram_button}</a>
  </div>
</div>
<p class="small">Dopo il collegamento vedrai ✅. Chiudi questa scheda e torna allo Short già pronto nell'app.</p>
<button class="close" onclick="window.close()">Chiudi questa scheda e torna all'app</button>
<a class="back" href="/">Apri comunque Gaming Shorts Factory</a>
</div></main></body></html>"""


def _tiktok_oauth_start(handler,sid):
    sid=_safe_id(sid)
    if not sid:
        _html(handler,400,"Sessione browser non valida. Riapri /social-connect.")
        return
    if not (PUBLIC_APP_URL and TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET):
        _html(handler,503,"Configurazione TikTok incompleta")
        return
    state="gsfsc_"+secrets.token_urlsafe(28)
    state_dir=ROOT/"social_oauth"
    state_dir.mkdir(parents=True,exist_ok=True)
    _write_json_atomic(state_dir/(state+".json"),{
        "created":time.time(),
        "sid":sid,
    })
    # Keep the already-registered root redirect URI. Nginx intercepts only
    # our gsfsc_ OAuth states and routes them back to this helper.
    redirect_uri=PUBLIC_APP_URL
    params={
        "client_key":TIKTOK_CLIENT_KEY,
        "response_type":"code",
        "scope":"user.info.basic,video.publish,video.list",
        "redirect_uri":redirect_uri,
        "state":state,
    }
    _redirect(handler,"https://www.tiktok.com/v2/auth/authorize/?"+urllib.parse.urlencode(params))


def _tiktok_oauth_callback(handler,query):
    code=str((query.get("code") or [""])[0] or "")
    state=re.sub(r"[^A-Za-z0-9_-]+","",str((query.get("state") or [""])[0] or ""))[:160]
    err=str((query.get("error_description") or query.get("error") or [""])[0] or "")
    state_file=ROOT/"social_oauth"/(state+".json")
    try:
        pending=json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        pending={}
    try:
        state_file.unlink(missing_ok=True)
    except Exception:
        pass
    created=float(pending.get("created",0) or 0)
    sid=_safe_id(pending.get("sid",""))
    if not state or not sid or not created or time.time()-created>900:
        _html(handler,400,"Stato OAuth scaduto o non valido. Riapri /social-connect.")
        return
    if err:
        _html(handler,400,_social_page(sid,"TikTok: "+err))
        return
    if not code:
        _html(handler,400,_social_page(sid,"TikTok non ha restituito il codice di autorizzazione."))
        return

    redirect_uri=PUBLIC_APP_URL
    form=urllib.parse.urlencode({
        "client_key":TIKTOK_CLIENT_KEY,
        "client_secret":TIKTOK_CLIENT_SECRET,
        "code":code,
        "grant_type":"authorization_code",
        "redirect_uri":redirect_uri,
    }).encode("utf-8")
    req=urllib.request.Request(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data=form,
        headers={"Content-Type":"application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req,timeout=45) as resp:
            payload=json.loads(resp.read().decode("utf-8"))
        token=dict(payload or {})
        if not token.get("access_token"):
            raise RuntimeError(str(payload))
        now=time.time()
        token["_saved_at"]=now
        token["saved_at"]=now
        token["expires_at"]=now+int(token.get("expires_in",0) or 0)
        token["refresh_expires_at"]=now+int(token.get("refresh_expires_in",0) or 0)
        _tiktok_user_save(sid,token)
        _redirect(handler,"/social-connect")
    except Exception as exc:
        _html(handler,500,_social_page(sid,"Collegamento TikTok fallito: "+str(exc)[:220]))


def _youtube_oauth_start(handler,sid):
    sid=_safe_id(sid)
    if not sid:
        _html(handler,400,"Sessione browser non valida. Riapri /social-connect.")
        return
    if not (PUBLIC_APP_URL and YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET):
        _html(handler,503,_social_page(sid,"Configurazione YouTube incompleta sul server."))
        return
    state="gsfyt_"+secrets.token_urlsafe(28)
    state_dir=ROOT/"social_oauth"
    state_dir.mkdir(parents=True,exist_ok=True)
    _write_json_atomic(state_dir/(state+".json"),{
        "created":time.time(),
        "sid":sid,
        "platform":"YouTube",
    })
    params={
        "client_id":YOUTUBE_CLIENT_ID,
        "redirect_uri":PUBLIC_APP_URL,
        "response_type":"code",
        "scope":YOUTUBE_SCOPE,
        "access_type":"offline",
        "include_granted_scopes":"true",
        "prompt":"consent",
        "state":state,
    }
    _redirect(handler,"https://accounts.google.com/o/oauth2/v2/auth?"+urllib.parse.urlencode(params))


def _youtube_oauth_callback(handler,query):
    code=str((query.get("code") or [""])[0] or "")
    state=re.sub(r"[^A-Za-z0-9_-]+","",str((query.get("state") or [""])[0] or ""))[:160]
    err=str((query.get("error_description") or query.get("error") or [""])[0] or "")
    state_file=ROOT/"social_oauth"/(state+".json")
    try:
        pending=json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        pending={}
    try:
        state_file.unlink(missing_ok=True)
    except Exception:
        pass
    created=float(pending.get("created",0) or 0)
    sid=_safe_id(pending.get("sid",""))
    if not state.startswith("gsfyt_") or not sid or not created or time.time()-created>900:
        _html(handler,400,"Stato OAuth YouTube scaduto o non valido. Riapri /social-connect.")
        return
    if err:
        _html(handler,400,_social_page(sid,"YouTube: "+err))
        return
    if not code:
        _html(handler,400,_social_page(sid,"YouTube non ha restituito il codice di autorizzazione."))
        return

    form=urllib.parse.urlencode({
        "client_id":YOUTUBE_CLIENT_ID,
        "client_secret":YOUTUBE_CLIENT_SECRET,
        "code":code,
        "grant_type":"authorization_code",
        "redirect_uri":PUBLIC_APP_URL,
    }).encode("utf-8")
    req=urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=form,
        headers={"Content-Type":"application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req,timeout=45) as resp:
            payload=json.loads(resp.read().decode("utf-8"))
        access=str(payload.get("access_token","") or "")
        refresh=str(payload.get("refresh_token","") or "")
        if not access:
            raise RuntimeError(str(payload))
        scopes=str(payload.get("scope","") or YOUTUBE_SCOPE).split()
        token={
            "token":access,
            "refresh_token":refresh,
            "token_uri":"https://oauth2.googleapis.com/token",
            "client_id":YOUTUBE_CLIENT_ID,
            "client_secret":YOUTUBE_CLIENT_SECRET,
            "scopes":scopes or [YOUTUBE_SCOPE],
        }
        _youtube_user_save(sid,token)
        _redirect(handler,"/social-connect")
    except Exception as exc:
        _html(handler,500,_social_page(sid,"Collegamento YouTube fallito: "+str(exc)[:220]))


def _instagram_oauth_start(handler,sid):
    sid=_safe_id(sid)
    if not sid:
        _html(handler,400,"Sessione browser non valida. Riapri /social-connect.")
        return
    if not PUBLIC_APP_URL:
        _html(handler,503,_social_page(sid,"Configurazione URL pubblica Instagram incompleta sul server."))
        return

    # Prefer Meta's current Instagram Login flow. It does not require a
    # Facebook Page and uses the Instagram App ID shown under
    # Instagram > API setup with Instagram login.
    if INSTAGRAM_APP_ID and INSTAGRAM_APP_SECRET:
        mode="instagram_login"
        state="gsfig_"+secrets.token_urlsafe(28)
        state_dir=ROOT/"social_oauth"
        state_dir.mkdir(parents=True,exist_ok=True)
        _write_json_atomic(state_dir/(state+".json"),{
            "created":time.time(),
            "sid":sid,
            "platform":"Instagram",
            "mode":mode,
        })
        params={
            "client_id":INSTAGRAM_APP_ID,
            "redirect_uri":INSTAGRAM_REDIRECT_URI,
            "state":state,
            "response_type":"code",
            "scope":INSTAGRAM_SCOPES,
            "force_reauth":"true",
            "enable_fb_login":"0",
        }
        _redirect(handler,"https://www.instagram.com/oauth/authorize?"+urllib.parse.urlencode(params))
        return

    # Backward-compatible Facebook Login path for an already configured Meta
    # app. New installs should use Instagram Login above.
    if not (META_APP_ID and META_APP_SECRET):
        _html(handler,503,_social_page(
            sid,
            "Instagram richiede GSF_INSTAGRAM_APP_ID e GSF_INSTAGRAM_APP_SECRET sul server."
        ))
        return

    state="gsfig_"+secrets.token_urlsafe(28)
    state_dir=ROOT/"social_oauth"
    state_dir.mkdir(parents=True,exist_ok=True)
    _write_json_atomic(state_dir/(state+".json"),{
        "created":time.time(),
        "sid":sid,
        "platform":"Instagram",
        "mode":"facebook_login",
    })
    params={
        "client_id":META_APP_ID,
        "redirect_uri":INSTAGRAM_REDIRECT_URI,
        "state":state,
        "response_type":"code",
        "scope":META_SCOPES,
    }
    _redirect(handler,"https://www.facebook.com/dialog/oauth?"+urllib.parse.urlencode(params))


def _instagram_oauth_callback(handler,query):
    code=str((query.get("code") or [""])[0] or "")
    state=re.sub(r"[^A-Za-z0-9_-]+","",str((query.get("state") or [""])[0] or ""))[:160]
    err=str((query.get("error_description") or query.get("error_message") or query.get("error") or [""])[0] or "")
    state_file=ROOT/"social_oauth"/(state+".json")
    try:
        pending=json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        pending={}
    try:
        state_file.unlink(missing_ok=True)
    except Exception:
        pass
    created=float(pending.get("created",0) or 0)
    sid=_safe_id(pending.get("sid",""))
    mode=str(pending.get("mode","") or "")
    if not state.startswith("gsfig_") or not sid or not created or time.time()-created>900:
        _html(handler,400,"Stato OAuth Instagram scaduto o non valido. Riapri /social-connect.")
        return
    if err:
        _html(handler,400,_social_page(sid,"Instagram: "+err))
        return
    if not code:
        _html(handler,400,_social_page(sid,"Instagram non ha restituito il codice di autorizzazione."))
        return

    if mode=="instagram_login":
        try:
            form=urllib.parse.urlencode({
                "client_id":INSTAGRAM_APP_ID,
                "client_secret":INSTAGRAM_APP_SECRET,
                "grant_type":"authorization_code",
                "redirect_uri":INSTAGRAM_REDIRECT_URI,
                "code":code,
            }).encode("utf-8")
            req=urllib.request.Request(
                "https://api.instagram.com/oauth/access_token",
                data=form,
                headers={"Content-Type":"application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req,timeout=45) as resp:
                token_payload=json.loads(resp.read().decode("utf-8"))

            short_token=""
            expires_in=0
            if isinstance(token_payload,dict):
                short_token=str(token_payload.get("access_token","") or "")
                expires_in=int(token_payload.get("expires_in",0) or 0)
                if not short_token:
                    rows=token_payload.get("data")
                    if isinstance(rows,list) and rows and isinstance(rows[0],dict):
                        short_token=str(rows[0].get("access_token","") or "")
                        expires_in=int(rows[0].get("expires_in",0) or 0)
            if not short_token:
                raise RuntimeError("Instagram non ha restituito un access token.")

            access_token=short_token
            long_expires=expires_in
            try:
                long_url="https://graph.instagram.com/access_token?"+urllib.parse.urlencode({
                    "grant_type":"ig_exchange_token",
                    "client_secret":INSTAGRAM_APP_SECRET,
                    "access_token":short_token,
                })
                with urllib.request.urlopen(long_url,timeout=45) as resp:
                    long_payload=json.loads(resp.read().decode("utf-8"))
                if isinstance(long_payload,dict) and long_payload.get("access_token"):
                    access_token=str(long_payload.get("access_token"))
                    long_expires=int(long_payload.get("expires_in",0) or 0)
            except Exception:
                pass

            me_url="https://graph.instagram.com/me?"+urllib.parse.urlencode({
                "fields":"user_id,username,id,account_type",
                "access_token":access_token,
            })
            with urllib.request.urlopen(me_url,timeout=45) as resp:
                me_payload=json.loads(resp.read().decode("utf-8"))

            profile=me_payload
            if isinstance(me_payload,dict) and isinstance(me_payload.get("data"),list) and me_payload["data"]:
                profile=me_payload["data"][0]
            if not isinstance(profile,dict):
                raise RuntimeError(str(me_payload))

            # user_id is the professional account ID needed for publishing.
            ig_id=str(profile.get("user_id","") or profile.get("id","") or "")
            username=str(profile.get("username","") or "")
            account_type=str(profile.get("account_type","") or "")
            if not ig_id:
                raise RuntimeError("Instagram non ha restituito l'ID dell'account professionale.")

            now=time.time()
            _instagram_user_save(sid,{
                "ig_user_id":ig_id,
                "access_token":access_token,
                "username":username,
                "account_type":account_type,
                "api_host":"https://graph.instagram.com",
                "oauth_mode":"instagram_login",
                "saved_at":now,
                "expires_at":now+long_expires if long_expires else 0,
            })
            _redirect(handler,"/social-connect")
        except Exception as exc:
            _html(handler,500,_social_page(sid,"Collegamento Instagram fallito: "+str(exc)[:220]))
        return

    # Legacy Facebook Login callback.
    try:
        token_url="https://graph.facebook.com/oauth/access_token?"+urllib.parse.urlencode({
            "client_id":META_APP_ID,
            "client_secret":META_APP_SECRET,
            "redirect_uri":PUBLIC_APP_URL,
            "code":code,
        })
        with urllib.request.urlopen(token_url,timeout=45) as resp:
            token_payload=json.loads(resp.read().decode("utf-8"))
        user_token=str(token_payload.get("access_token","") or "")
        if not user_token:
            raise RuntimeError(str(token_payload))

        try:
            long_url="https://graph.facebook.com/oauth/access_token?"+urllib.parse.urlencode({
                "grant_type":"fb_exchange_token",
                "client_id":META_APP_ID,
                "client_secret":META_APP_SECRET,
                "fb_exchange_token":user_token,
            })
            with urllib.request.urlopen(long_url,timeout=45) as resp:
                long_payload=json.loads(resp.read().decode("utf-8"))
            if long_payload.get("access_token"):
                user_token=str(long_payload.get("access_token"))
        except Exception:
            pass

        accounts_url="https://graph.facebook.com/me/accounts?"+urllib.parse.urlencode({
            "fields":"name,access_token,tasks,instagram_business_account",
            "access_token":user_token,
        })
        with urllib.request.urlopen(accounts_url,timeout=45) as resp:
            accounts_payload=json.loads(resp.read().decode("utf-8"))
        pages=accounts_payload.get("data") if isinstance(accounts_payload,dict) else None
        if not isinstance(pages,list):
            raise RuntimeError(str(accounts_payload))

        chosen=None
        for page in pages:
            if not isinstance(page,dict):
                continue
            ig=(page.get("instagram_business_account") or {})
            ig_id=str(ig.get("id","") or "")
            page_token=str(page.get("access_token","") or "")
            if ig_id and page_token:
                chosen=(ig_id,page_token)
                break
        if not chosen:
            raise RuntimeError("Nessun account Instagram professionale collegato a una Pagina Facebook.")

        ig_id,page_token=chosen
        username=""
        try:
            info_url="https://graph.facebook.com/"+urllib.parse.quote(ig_id,safe="")+"?"+urllib.parse.urlencode({
                "fields":"id,username",
                "access_token":page_token,
            })
            with urllib.request.urlopen(info_url,timeout=30) as resp:
                info_payload=json.loads(resp.read().decode("utf-8"))
            username=str(info_payload.get("username","") or "")
        except Exception:
            pass

        _instagram_user_save(sid,{
            "ig_user_id":ig_id,
            "access_token":page_token,
            "username":username,
            "api_host":"https://graph.facebook.com",
            "oauth_mode":"facebook_login",
            "saved_at":time.time(),
        })
        _redirect(handler,"/social-connect")
    except Exception as exc:
        _html(handler,500,_social_page(sid,"Collegamento Instagram fallito: "+str(exc)[:220]))


def _ai_learning_restore():
    if _AI_LEARNING_PATH.is_file() or not _bucket_enabled():
        return _learning_load_model(_AI_LEARNING_PATH)
    try:
        obj=_s3().get_object(Bucket=S3_BUCKET,Key=_AI_LEARNING_BUCKET_KEY)
        raw=obj["Body"].read()
        payload=json.loads(raw.decode("utf-8"))
        if isinstance(payload,dict):
            _learning_save_model(_AI_LEARNING_PATH,payload)
            print(
                "GSF_V127_LEARNING_RESTORED",
                "feedback="+str(int(payload.get("total_feedback",0) or 0)),
                flush=True,
            )
            return payload
    except Exception:
        pass
    return _learning_load_model(_AI_LEARNING_PATH)

def _ai_learning_update(row):
    model=_learning_load_model(_AI_LEARNING_PATH)
    model=_learning_update_model(model,row)
    _learning_save_model(_AI_LEARNING_PATH,model)
    if _bucket_enabled():
        try:
            _s3().put_object(
                Bucket=S3_BUCKET,
                Key=_AI_LEARNING_BUCKET_KEY,
                Body=json.dumps(model,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
                ContentType="application/json",
                CacheControl="no-store",
            )
        except Exception as exc:
            print("GSF_V127_LEARNING_BUCKET_WARN",repr(str(exc))[:180],flush=True)
    return model

def _ai_feedback_store(sid,event):
    sid=_safe_id(sid)
    if not sid or not isinstance(event,dict):
        return False
    allowed_actions={"selected","rejected","opened_editor","published","replaced","trimmed"}
    action=str(event.get("action") or "").strip().lower()
    if action not in allowed_actions:
        action="selected"
    row={
        "created_at":time.time(),
        "engine":str(event.get("engine") or "v124-ai-os")[:64],
        "action":action,
        "rank":int(event.get("rank") or 0),
        "start":float(event.get("start") or 0.0),
        "event":str(event.get("event") or "highlight")[:48],
        "brain_score":float(event.get("brain_score") or 0.0),
        "confidence":float(event.get("confidence") or 0.0),
        "semantic_injected":bool(event.get("semantic_injected")),
    }
    root=ROOT/"sessions"/sid
    root.mkdir(parents=True,exist_ok=True)
    path=root/"ai_feedback.jsonl"
    with _AI_FEEDBACK_LOCK:
        existing=[]
        if path.is_file():
            try:
                existing=path.read_text(encoding="utf-8").splitlines()[-499:]
            except Exception:
                existing=[]
        existing.append(json.dumps(row,ensure_ascii=False,separators=(",",":")))
        path.write_text("\n".join(existing)+"\n",encoding="utf-8")
        if _bucket_enabled():
            try:
                _s3().put_object(
                    Bucket=S3_BUCKET,
                    Key=f"ai-feedback/{sid}/events.jsonl",
                    Body=path.read_bytes(),
                    ContentType="application/x-ndjson",
                    CacheControl="no-store",
                )
            except Exception as exc:
                print("GSF_V124_FEEDBACK_BUCKET_WARN",sid,repr(str(exc))[:180],flush=True)
        try:
            model=_ai_learning_update(row)
            print(
                "GSF_V127_LEARNING",
                "feedback="+str(int(model.get("total_feedback",0) or 0)),
                "event="+str(row.get("event") or ""),
                "action="+str(row.get("action") or ""),
                flush=True,
            )
        except Exception as exc:
            print("GSF_V127_LEARNING_WARN",repr(str(exc))[:180],flush=True)
    print(
        "GSF_V124_FEEDBACK",
        sid,
        "action="+action,
        "rank="+str(row["rank"]),
        "event="+row["event"],
        flush=True,
    )
    return True

def _content_memory_path(sid):
    sid=_safe_id(sid)
    if not sid:
        return None
    root=ROOT/"sessions"/sid
    root.mkdir(parents=True,exist_ok=True)
    return root/"content_memory_v145.json"

def _content_memory_key(sid):
    sid=_safe_id(sid)
    return f"content-memory/{sid}/memory_v145.json" if sid else ""

def _content_memory_load(sid):
    sid=_safe_id(sid)
    if not sid:
        return []
    path=_content_memory_path(sid)
    if path is not None and path.is_file():
        try:
            rows=json.loads(path.read_text(encoding="utf-8"))
            if isinstance(rows,list):
                return [x for x in rows if isinstance(x,dict)]
        except Exception:
            pass
    if _bucket_enabled():
        try:
            obj=_s3().get_object(Bucket=S3_BUCKET,Key=_content_memory_key(sid))
            rows=json.loads(obj["Body"].read().decode("utf-8"))
            if isinstance(rows,list):
                rows=[x for x in rows if isinstance(x,dict)]
                if path is not None:
                    _write_json_atomic(path,rows)
                return rows
        except Exception:
            pass
    return []

def _content_memory_save(sid,rows):
    sid=_safe_id(sid)
    if not sid:
        return False
    clean=[dict(x) for x in (rows or []) if isinstance(x,dict)][:500]
    path=_content_memory_path(sid)
    if path is not None:
        _write_json_atomic(path,clean)
    if _bucket_enabled():
        try:
            _s3().put_object(
                Bucket=S3_BUCKET,Key=_content_memory_key(sid),
                Body=json.dumps(clean,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
                ContentType="application/json",CacheControl="no-store",
            )
        except Exception as exc:
            print("GSF_V145_MEMORY_BUCKET_WARN",sid,repr(str(exc))[:180],flush=True)
    return True

def _content_memory_check(sid,record):
    sid=_safe_id(sid)
    if not sid or not isinstance(record,dict):
        return {"duplicate":False,"recommendation":"new_content","source_count":0,"series_count":0}
    with _CONTENT_MEMORY_LOCK:
        rows=_content_memory_load(sid)
        return _content_memory_inspect(rows,record)

def _content_memory_record(sid,record):
    sid=_safe_id(sid)
    if not sid or not isinstance(record,dict):
        return {}
    with _CONTENT_MEMORY_LOCK:
        rows=_content_memory_load(sid)
        merged=_content_memory_upsert(rows,record,max_rows=500)
        _content_memory_save(sid,merged)
        state=_content_memory_inspect(merged,record)
    print(
        "GSF_V145_MEMORY_RECORDED",
        sid,
        "fp="+str(record.get("fingerprint") or "")[:12],
        "source_count="+str(state.get("source_count") or 0),
        flush=True,
    )
    return state

def _analytics_path(sid):
    sid=_safe_id(sid)
    if not sid:
        return None
    root=ROOT/"sessions"/sid
    root.mkdir(parents=True,exist_ok=True)
    return root/"social_analytics_v148.json"

def _analytics_key(sid):
    sid=_safe_id(sid)
    return f"social-analytics/{sid}/analytics_v148.json" if sid else ""

def _analytics_load(sid):
    sid=_safe_id(sid)
    if not sid:
        return {"records":[]}
    path=_analytics_path(sid)
    if path is not None and path.is_file():
        try:
            payload=json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload,dict):
                return payload
        except Exception:
            pass
    if _bucket_enabled():
        try:
            obj=_s3().get_object(Bucket=S3_BUCKET,Key=_analytics_key(sid))
            payload=json.loads(obj["Body"].read().decode("utf-8"))
            if isinstance(payload,dict):
                if path is not None:
                    _write_json_atomic(path,payload)
                return payload
        except Exception:
            pass
    return {"records":[]}

def _analytics_save(sid,payload):
    sid=_safe_id(sid)
    if not sid or not isinstance(payload,dict):
        return False
    path=_analytics_path(sid)
    if path is not None:
        _write_json_atomic(path,payload)
    if _bucket_enabled():
        try:
            _s3().put_object(
                Bucket=S3_BUCKET,Key=_analytics_key(sid),
                Body=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
                ContentType="application/json",CacheControl="no-store",
            )
        except Exception as exc:
            print("GSF_V148_ANALYTICS_BUCKET_WARN",sid,repr(str(exc))[:180],flush=True)
    return True

def _youtube_analytics_token(sid):
    token=dict(_youtube_user_load(sid) or {})
    refresh=str(token.get("refresh_token") or "")
    client_id=str(token.get("client_id") or YOUTUBE_CLIENT_ID or "")
    client_secret=str(token.get("client_secret") or YOUTUBE_CLIENT_SECRET or "")
    if not refresh or not client_id or not client_secret:
        return token
    try:
        form=urllib.parse.urlencode({
            "client_id":client_id,
            "client_secret":client_secret,
            "refresh_token":refresh,
            "grant_type":"refresh_token",
        }).encode("utf-8")
        req=urllib.request.Request(
            "https://oauth2.googleapis.com/token",
            data=form,
            headers={"Content-Type":"application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req,timeout=30) as resp:
            payload=json.loads(resp.read().decode("utf-8"))
        access=str(payload.get("access_token") or "")
        if access:
            token["token"]=access
            token["access_token"]=access
            token["refresh_token"]=refresh
            token["client_id"]=client_id
            token["client_secret"]=client_secret
            token["scopes"]=str(payload.get("scope") or YOUTUBE_SCOPE).split()
            token["_analytics_refreshed_at"]=time.time()
            try:_youtube_user_save(sid,token)
            except Exception:pass
    except Exception as exc:
        print("GSF_V148_YOUTUBE_REFRESH_WARN",sid,repr(str(exc))[:180],flush=True)
    return token

def _tiktok_analytics_token(sid):
    token=dict(_tiktok_user_load(sid) or {})
    refresh=str(token.get("refresh_token") or "")
    expiry=float(token.get("expires_at") or 0.0)
    if not refresh or not TIKTOK_CLIENT_KEY or not TIKTOK_CLIENT_SECRET:
        return token
    if expiry and expiry-time.time()>600:
        return token
    try:
        form=urllib.parse.urlencode({
            "client_key":TIKTOK_CLIENT_KEY,
            "client_secret":TIKTOK_CLIENT_SECRET,
            "grant_type":"refresh_token",
            "refresh_token":refresh,
        }).encode("utf-8")
        req=urllib.request.Request(
            "https://open.tiktokapis.com/v2/oauth/token/",
            data=form,
            headers={"Content-Type":"application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req,timeout=30) as resp:
            payload=json.loads(resp.read().decode("utf-8"))
        if payload.get("access_token"):
            now=time.time()
            token.update(dict(payload))
            token["expires_at"]=now+int(payload.get("expires_in",0) or 0)
            token["refresh_expires_at"]=now+int(payload.get("refresh_expires_in",0) or 0)
            token["_analytics_refreshed_at"]=now
            try:_tiktok_user_save(sid,token)
            except Exception:pass
    except Exception as exc:
        print("GSF_V148_TIKTOK_REFRESH_WARN",sid,repr(str(exc))[:180],flush=True)
    return token

def _analytics_token_for(sid,platform):
    p=str(platform or "").lower()
    if p.startswith("you"):
        return _youtube_analytics_token(sid)
    if p.startswith("tik"):
        return _tiktok_analytics_token(sid)
    if p.startswith("inst"):
        return _instagram_user_load(sid)
    return {}

def _analytics_register(sid,record):
    sid=_safe_id(sid)
    if not sid or not isinstance(record,dict):
        return {}
    platform=str(record.get("platform") or "").strip()
    content_id=str(record.get("content_id") or "").strip()
    fingerprint=str(record.get("content_fingerprint") or "").strip()
    if not platform or not content_id:
        return {"ok":False,"error":"platform/content_id required"}
    with _ANALYTICS_LOCK:
        data=_analytics_load(sid)
        rows=[dict(x) for x in (data.get("records") or []) if isinstance(x,dict)]
        key=(platform.lower(),content_id)
        existing=None
        for row in rows:
            if (str(row.get("platform") or "").lower(),str(row.get("content_id") or ""))==key:
                existing=row;break
        now=time.time()
        payload={
            "platform":platform,
            "content_id":content_id,
            "id_type":str(record.get("id_type") or ""),
            "content_fingerprint":fingerprint,
            "registered_at":float((existing or {}).get("registered_at") or now),
            "updated_at":now,
            "status":str((existing or {}).get("status") or "registered"),
            "metadata":dict(record.get("metadata") or {}),
        }
        if existing is not None:
            existing.update(payload)
        else:
            rows.append(payload)
        data["records"]=rows[-300:]
        data["updated_at"]=now
        _analytics_save(sid,data)
    return {"ok":True,"record":payload}

def _analytics_collect_one(sid,row):
    token=_analytics_token_for(sid,row.get("platform"))
    if not token:
        return {**dict(row),"status":"needs_connection","last_error":"account not connected","updated_at":time.time()}
    content_id=str(row.get("content_id") or "")
    if not content_id:
        return {**dict(row),"status":"invalid","last_error":"missing content id","updated_at":time.time()}
    try:
        result=_social_analytics_collect(
            row.get("platform"),token,content_id,
            id_type=str(row.get("id_type") or ""),
        )
        out={**dict(row),"status":"ok","last_error":"","updated_at":time.time(),
             "analytics":result,"performance_score":float(result.get("performance_score") or 0.0)}
        fp=str(out.get("content_fingerprint") or "")
        if fp:
            with _CONTENT_MEMORY_LOCK:
                memory_rows=_content_memory_load(sid)
                changed=False
                for item in memory_rows:
                    if str(item.get("fingerprint") or "")==fp:
                        item["performance_score"]=out["performance_score"]
                        item["platform"]=str(out.get("platform") or item.get("platform") or "")
                        item["analytics_updated_at"]=out["updated_at"]
                        changed=True
                        break
                if changed:
                    _content_memory_save(sid,memory_rows)
        return out
    except Exception as exc:
        return {**dict(row),"status":"error","last_error":str(exc)[:300],"updated_at":time.time()}

def _analytics_collect_all(sid,force=False):
    sid=_safe_id(sid)
    if not sid:
        return {"ok":False,"records":[]}
    now=time.time()
    if not force and now-float(_ANALYTICS_TICK.get(sid,0) or 0)<900:
        data=_analytics_load(sid)
        return {"ok":True,"records":list(data.get("records") or []),"cached":True}
    with _ANALYTICS_LOCK:
        data=_analytics_load(sid)
        rows=[dict(x) for x in (data.get("records") or []) if isinstance(x,dict)]
    refreshed=[_analytics_collect_one(sid,row) for row in rows]
    with _ANALYTICS_LOCK:
        data["records"]=refreshed
        data["updated_at"]=now
        _analytics_save(sid,data)
        _ANALYTICS_TICK[sid]=now
    return {"ok":True,"records":refreshed,"cached":False}

def _analytics_context(sid):
    data=_analytics_load(sid)
    rows=[dict(x) for x in (data.get("records") or []) if isinstance(x,dict)]
    scored=[x for x in rows if float(x.get("performance_score") or 0)>0]
    if not scored:
        return {"samples":0,"best_strategy":"","best_platform":"","mean_score":0.0}
    best=max(scored,key=lambda x:float(x.get("performance_score") or 0.0))
    mean=sum(float(x.get("performance_score") or 0.0) for x in scored)/len(scored)
    strategies={}
    for row in scored:
        strategy=str((row.get("metadata") or {}).get("ab_strategy") or "")
        if strategy:
            strategies.setdefault(strategy,[]).append(float(row.get("performance_score") or 0.0))
    best_strategy=""
    if strategies:
        best_strategy=max(
            strategies,
            key=lambda k:sum(strategies[k])/max(1,len(strategies[k]))
        )
    return {
        "samples":len(scored),
        "best_strategy":best_strategy,
        "best_platform":str(best.get("platform") or ""),
        "mean_score":round(mean,4),
        "best_score":round(float(best.get("performance_score") or 0.0),4),
    }

def _quality_report_path(sid):
    sid=_safe_id(sid)
    return (ROOT/"sessions"/sid/"quality_report.json") if sid else None

def _quality_bucket_key(sid):
    sid=_safe_id(sid)
    return f"final-results/{sid}/quality.json" if sid else ""

def _quality_load(sid):
    sid=_safe_id(sid)
    if not sid:
        return {}
    with _QUALITY_LOCK:
        cached=dict(_QUALITY_CACHE.get(sid) or {})
    if cached:
        return cached
    path=_quality_report_path(sid)
    if path is not None and path.is_file():
        try:
            payload=json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload,dict):
                with _QUALITY_LOCK:
                    _QUALITY_CACHE[sid]=dict(payload)
                return payload
        except Exception:
            pass
    return {}

def _quality_store(sid,payload):
    sid=_safe_id(sid)
    if not sid or not isinstance(payload,dict):
        return
    path=_quality_report_path(sid)
    if path is not None:
        try:
            _write_json_atomic(path,payload)
        except Exception:
            pass
    with _QUALITY_LOCK:
        _QUALITY_CACHE[sid]=dict(payload)
    if _bucket_enabled():
        try:
            _s3().put_object(
                Bucket=S3_BUCKET,
                Key=_quality_bucket_key(sid),
                Body=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
                ContentType="application/json",
                CacheControl="no-store",
            )
        except Exception as exc:
            print("GSF_QUALITY_BUCKET_WARN",sid,repr(str(exc))[:180],flush=True)

def _quality_schedule(sid,stable):
    sid=_safe_id(sid)
    stable=Path(stable) if stable is not None else None
    if not sid or stable is None or not stable.is_file() or stable.stat().st_size<=1024:
        return {}
    size=int(stable.stat().st_size)
    mtime=float(stable.stat().st_mtime)
    current=_quality_load(sid)
    if (
        current
        and int(current.get("source_size") or 0)==size
        and abs(float(current.get("source_mtime") or 0.0)-mtime)<0.01
        and str(current.get("status") or "") in ("pass","warn","fail")
    ):
        return current
    with _QUALITY_LOCK:
        running=dict(_QUALITY_CACHE.get(sid) or {})
        if (
            str(running.get("status") or "")=="analyzing"
            and int(running.get("source_size") or 0)==size
            and abs(float(running.get("source_mtime") or 0.0)-mtime)<0.01
        ):
            return running
        marker={
            "engine":"v124-quality-control",
            "status":"analyzing",
            "score":None,
            "issues":[],
            "warnings":[],
            "source_size":size,
            "source_mtime":mtime,
            "started_at":time.time(),
        }
        _QUALITY_CACHE[sid]=dict(marker)

    def run():
        try:
            report=_quality_inspect(stable)
            report["source_size"]=size
            report["source_mtime"]=mtime
            _quality_store(sid,report)
            print(
                "GSF_V124_QUALITY",
                sid,
                "status="+str(report.get("status") or ""),
                "score="+str(report.get("score")),
                "issues="+str(len(report.get("issues") or [])),
                "warnings="+str(len(report.get("warnings") or [])),
                flush=True,
            )
        except Exception as exc:
            report={
                "engine":"v124-quality-control",
                "status":"error",
                "score":0,
                "issues":["quality_control_failed"],
                "warnings":[],
                "error":str(exc)[:220],
                "source_size":size,
                "source_mtime":mtime,
                "checked_at":time.time(),
            }
            _quality_store(sid,report)
            print("GSF_V124_QUALITY_WARN",sid,repr(str(exc))[:220],flush=True)

    threading.Thread(target=run,name=f"gsf-quality-{sid[:8]}",daemon=True).start()
    return marker

_GUARDIAN_CACHE={}
_GUARDIAN_CACHE_LOCK=threading.Lock()
_GUARDIAN_MIN_INTERVAL=max(2.0,float(os.environ.get("GSF_GUARDIAN_MIN_INTERVAL","5") or 5))

def _guardian_restore_source_from_marker(sid):
    sid=_safe_id(sid)
    if not sid or not _bucket_enabled():
        return ""
    marker=ROOT/"sessions"/sid/"media"/".direct_upload_ready.json"
    try:
        meta=_guardian_source_plan(ROOT/"sessions"/sid)
        if not meta:
            return ""
        key=str(meta.get("bucket_key") or "")
        upload_id=_safe_id(meta.get("upload_id",""))
        if not upload_id:
            parts=[part for part in key.split("/") if part]
            if len(parts)>=3 and parts[0]=="uploads" and _safe_id(parts[1])==sid:
                upload_id=_safe_id(parts[2])
        if not upload_id:
            return ""
        original_name,safe_stem,ext=_safe_filename(meta.get("name") or Path(key).name)
        total=int(meta.get("size") or 0)
        if total<=0:
            head=_s3().head_object(Bucket=S3_BUCKET,Key=key)
            total=int(head.get("ContentLength") or 0)
        if total<=0:
            return ""
        analysis_key=str(meta.get("analysis_key") or f"analysis/{sid}/{upload_id}/v52-keyframe-turbo.json")
        _materialize_bucket_object(
            sid,upload_id,key,original_name,safe_stem,ext,total,analysis_key
        )
        fresh=json.loads(marker.read_text(encoding="utf-8")) if marker.is_file() else {}
        restored=Path(str((fresh or {}).get("path") or ""))
        if restored.is_file():
            print("GSF_GUARDIAN_SOURCE_RESTORED",sid,str(restored),flush=True)
            return str(restored)
    except Exception as exc:
        print("GSF_GUARDIAN_SOURCE_RESTORE_WARN",sid,repr(str(exc))[:220],flush=True)
    return ""

def _guardian_tick(sid,force=False):
    sid=_safe_id(sid)
    if not sid:
        return {"ok":False,"error":"invalid session"}
    now=time.time()
    with _GUARDIAN_CACHE_LOCK:
        cached=dict(_GUARDIAN_CACHE.get(sid) or {})
        if not force and cached and now-float(cached.get("checked_at") or 0)<_GUARDIAN_MIN_INTERVAL:
            return cached
    root=ROOT/"sessions"/sid
    root.mkdir(parents=True,exist_ok=True)
    try:
        result=_guardian_local(root,now=now,stale_after=900)
        extra_repairs=[]
        if result.get("needs_final_restore") and _bucket_enabled():
            restored=_final_restore_from_bucket(sid)
            if restored:
                result=_guardian_local(root,now=time.time(),stale_after=900)
                extra_repairs.append("final_from_bucket")
        if result.get("needs_source_restore") and _bucket_enabled():
            restored_source=_guardian_restore_source_from_marker(sid)
            if restored_source:
                result=_guardian_local(root,now=time.time(),stale_after=900)
                extra_repairs.append("source_from_bucket")
        repairs=[]
        for repair in list(result.get("repairs") or [])+extra_repairs:
            if repair and repair not in repairs:
                repairs.append(repair)
        result["repairs"]=repairs
        if repairs:
            print("GSF_GUARDIAN_REPAIR",sid,",".join(repairs),flush=True)
        with _GUARDIAN_CACHE_LOCK:
            _GUARDIAN_CACHE[sid]=dict(result)
        return result
    except Exception as exc:
        result={"ok":False,"error":str(exc)[:180],"checked_at":now}
        with _GUARDIAN_CACHE_LOCK:
            _GUARDIAN_CACHE[sid]=dict(result)
        print("GSF_GUARDIAN_WARN",sid,repr(str(exc))[:220],flush=True)
        return result

def _guardian_quality_for_sid(sid):
    sid=_safe_id(sid)
    if not sid:
        return {}
    stable,_job=_final_local_paths(sid)
    if stable is None or not stable.is_file():
        return {}
    return _quality_schedule(sid,stable)

def _start_proactive_guardian():
    global _GUARDIAN_WATCHDOG
    if _GUARDIAN_WATCHDOG is not None:
        return _GUARDIAN_WATCHDOG
    enabled=str(os.environ.get("GSF_PROACTIVE_GUARDIAN","1") or "1").strip().lower() not in ("0","false","off","no")
    if not enabled:
        print("GSF_V128_GUARDIAN disabled",flush=True)
        return None
    _GUARDIAN_WATCHDOG=_ProactiveGuardian(
        ROOT,
        _guardian_tick,
        quality_fn=_guardian_quality_for_sid,
        interval=max(15.0,float(os.environ.get("GSF_GUARDIAN_WATCHDOG_INTERVAL","60") or 60)),
        active_window=max(300.0,float(os.environ.get("GSF_GUARDIAN_ACTIVE_WINDOW","21600") or 21600)),
        max_sessions=max(1,int(os.environ.get("GSF_GUARDIAN_MAX_SESSIONS","24") or 24)),
        failure_limit=3,
        breaker_seconds=300.0,
    )
    _GUARDIAN_WATCHDOG.start()
    print(
        "GSF_V128_GUARDIAN started",
        "interval="+str(_GUARDIAN_WATCHDOG.interval),
        "max_sessions="+str(_GUARDIAN_WATCHDOG.max_sessions),
        flush=True,
    )
    return _GUARDIAN_WATCHDOG

class Handler(BaseHTTPRequestHandler):
    server_version="GSFDirectUpload/2.0"

    def log_message(self,fmt,*args):
        return

    def do_GET(self):
        path=urlparse(self.path)
        clean=path.path.rstrip("/")
        if clean in ("","/health"):
            _json(self,200,{
                "ok":True,
                "bucket":_bucket_enabled(),
                "worker":bool(WORKER_URL),
                "proactive_guardian":bool(_GUARDIAN_WATCHDOG is not None),
                "guardian_last_run":float(getattr(_GUARDIAN_WATCHDOG,"last_run",0.0) or 0.0),
            })
            return
        if clean in ("/app-icon.png","/favicon.ico"):
            try:
                _send_bytes(self,200,_official_app_icon_bytes(),"image/png","public, max-age=604800")
            except Exception as exc:
                _json(self,500,{"ok":False,"error":"app icon unavailable"})
            return
        if clean=="/manifest.webmanifest":
            _send_bytes(self,200,_app_manifest_bytes(),"application/manifest+json; charset=utf-8","public, max-age=3600")
            return
        if clean=="/gsf-sw.js":
            _send_bytes(self,200,_push_service_worker_bytes(),"application/javascript; charset=utf-8","no-cache")
            return
        if clean=="/gsf-push.js":
            _send_bytes(self,200,_push_client_bytes(),"application/javascript; charset=utf-8","no-cache")
            return
        if clean=="/push/public-key":
            _json(self,200,{"ok":bool(VAPID_PUBLIC_KEY),"public_key":VAPID_PUBLIC_KEY})
            return
        if clean=="/quality/status":
            sid=_social_sid(self)
            if not sid:
                _json(self,400,{"ok":False,"error":"invalid session"})
                return
            stable,_job=_final_local_paths(sid)
            report=_quality_schedule(sid,stable) if stable is not None else {}
            _json(self,200,{"ok":True,"quality":report})
            return
        if clean=="/guardian/watchdog":
            summary=dict(getattr(_GUARDIAN_WATCHDOG,"last_summary",{}) or {})
            _json(self,200,{
                "ok":True,
                "enabled":bool(_GUARDIAN_WATCHDOG is not None),
                "summary":summary,
            })
            return
        if clean=="/guardian/status":
            sid=_social_sid(self)
            if not sid:
                _json(self,400,{"ok":False,"error":"invalid session"})
                return
            guardian=_guardian_tick(sid,force=True)
            quality=_quality_load(sid)
            diagnosis=_guardian_diagnose(
                guardian=guardian,
                quality=quality,
                render_status=str(guardian.get("status") or ""),
            )
            _json(self,200,{
                "ok":bool(guardian.get("ok")),
                "guardian":guardian,
                "diagnosis":diagnosis,
                "quality":quality,
                "bucket":_bucket_enabled(),
                "worker_configured":bool(WORKER_URL),
            })
            return
        if clean=="/job/status":
            sid=_social_sid(self);payload={}
            if sid:
                _guardian_tick(sid)
            job=None
            stable=None
            if sid:
                session_root=ROOT/"sessions"/sid
                job=session_root/"render_job.json"
                stable=session_root/"media"/"gaming_short_finale_share.mp4"
                if job.is_file():
                    try:
                        payload=json.loads(job.read_text(encoding="utf-8"))
                        if not isinstance(payload,dict):payload={}
                    except Exception:payload={}
            status=str(payload.get("status") or "")
            if sid and stable is not None and not stable.is_file() and status not in ("running","cancelled"):
                restored=_final_restore_from_bucket(sid)
                if restored:
                    payload=restored
                    status="ready"
            started=float(payload.get("started_at") or 0.0)
            stable_ready=False
            stable_bytes=0
            stable_mtime=0.0
            try:
                if stable is not None and stable.is_file():
                    stable_bytes=int(stable.stat().st_size)
                    stable_mtime=float(stable.stat().st_mtime)
                    stable_ready=stable_bytes>1024 and started>0 and stable_mtime>=started-1.0
            except Exception:
                stable_ready=False
            # Self-heal the browser-visible job state from the durable local
            # final artifact. This closes the gap where FFmpeg succeeded but
            # a rerun interrupted the final JSON status update.
            if stable_ready and status!="cancelled":
                if status!="ready":
                    status="ready"
                    payload.update({
                        "status":"ready",
                        "completed_at":payload.get("completed_at") or stable_mtime or time.time(),
                        "final_path":str(stable),
                        "final_bytes":stable_bytes,
                        "pid":0,
                    })
                    if job is not None:
                        try:
                            _write_json_atomic(job,payload)
                            print("GSF_JOB_STATUS_SELF_HEALED",sid,stable_bytes,flush=True)
                        except Exception as exc:
                            print("GSF_JOB_STATUS_HEAL_WARN",sid,repr(str(exc)),flush=True)
            elif status=="ready" and not stable_ready:
                # Never tell the UI a Short is ready if the actual file is not.
                status="missing"
            if status=="running":
                if started and time.time()-started>900:
                    status="stale"
            quality={}
            if sid and stable_ready and stable is not None:
                quality=_quality_schedule(sid,stable)
            _json(self,200,{
                "ok":True,
                "render_status":status,
                "started_at":payload.get("started_at"),
                "completed_at":payload.get("completed_at"),
                "failed_at":payload.get("failed_at"),
                "final_bytes":stable_bytes if stable_ready else payload.get("final_bytes"),
                "download_ready":bool(stable_ready),
                "quality_status":str((quality or {}).get("status") or ""),
                "quality_score":(quality or {}).get("score"),
                "quality_issues":list((quality or {}).get("issues") or [])[:8],
                "quality_warnings":list((quality or {}).get("warnings") or [])[:8],
                "guardian_diagnosis":_guardian_diagnose(
                    guardian={},
                    quality=quality,
                    render_status=status,
                ),
            })
            return
        if clean=="/source/restore":
            sid=_social_sid(self)
            requested=str((parse_qs(path.query).get("path") or [""])[0])
            restored=_restore_bucket_source(sid,requested)
            if restored:
                _json(self,200,{"ok":True,"path":restored})
            else:
                _json(self,404,{"ok":False,"error":"source unavailable"})
            return
        if clean=="/editor-media/current":
            _editor_media_current(self,_social_sid(self))
            return
        if clean=="/drafts/resume":
            sid=_social_sid(self)
            query=parse_qs(path.query)
            draft_id=_safe_id((query.get("id") or [""])[0])
            wants_json=str((query.get("json") or [""])[0])=="1"
            draft=_draft_load(sid,draft_id)
            if not sid or not isinstance(draft,dict) or not draft:
                if wants_json:
                    _json(self,404,{"ok":False,"error":"Bozza non trovata."})
                else:
                    _html(self,404,"Bozza non trovata.")
                return
            state=_draft_prepare_resume(sid,draft)
            if not isinstance(state,dict):
                message="La bozza è salva, ma il video sorgente non è ancora recuperabile. Riprova tra poco."
                if wants_json:
                    _json(self,409,{"ok":False,"error":message})
                else:
                    _html(self,409,_creator_page(sid,message))
                return
            root=ROOT/"sessions"/sid
            root.mkdir(parents=True,exist_ok=True)
            _write_json_atomic(root/"session_state.json",state)
            _write_json_atomic(root/"draft_resume.json",{"draft_id":draft_id,"created_at":time.time()})
            target="/?draft_resume="+urllib.parse.quote(draft_id,safe="")
            if wants_json:
                _json(self,200,{"ok":True,"url":target})
            else:
                _redirect(self,target)
            return
        if clean=="/drafts/delete":
            sid=_social_sid(self)
            draft_id=_safe_id((parse_qs(path.query).get("id") or [""])[0])
            if sid and draft_id:
                _draft_delete(sid,draft_id)
            _redirect(self,"/account")
            return
        if clean=="/share/state":
            sid=_social_sid(self)
            if not sid:
                _json(self,400,{"ok":False,"error":"Sessione browser non valida."})
                return
            stable,_job=_final_local_paths(sid)
            ready=bool(stable and stable.is_file() and stable.stat().st_size>1024)
            final_bytes=int(stable.stat().st_size) if ready else 0
            if not ready and _bucket_enabled():
                try:
                    head=_s3().head_object(Bucket=S3_BUCKET,Key=_final_bucket_key(sid))
                    final_bytes=int(head.get("ContentLength") or 0)
                    ready=final_bytes>1024
                except Exception:
                    pass
            _json(self,200,{
                "ok":True,
                "ready":ready,
                "final_bytes":final_bytes,
                "video_url":"/share/final" if ready else "",
                "social":{
                    "youtube":bool(_youtube_user_load(sid)),
                    "tiktok":bool(_tiktok_user_load(sid)),
                    "instagram":bool(_instagram_user_load(sid)),
                    "facebook":False,
                },
            })
            return
        if clean=="/share/final":
            sid=_social_sid(self)
            if not sid:
                _html(self,400,"Sessione browser non valida.")
                return
            stable,_job=_final_local_paths(sid)
            if not (stable and stable.is_file() and stable.stat().st_size>1024):
                _final_restore_from_bucket(sid)
            if stable and stable.is_file() and stable.stat().st_size>1024:
                _redirect(self,f"/media/{sid}/media/gaming_short_finale_share.mp4")
            else:
                _html(self,404,"Short finale non ancora disponibile.")
            return
        if clean=="/creator-hub/state":
            sid=_social_sid(self)
            if not sid:
                _json(self,400,{"ok":False,"error":"Sessione browser non valida."})
                return
            profile=_creator_account_load(sid) or {}
            providers=dict(profile.get("providers") or {}) if isinstance(profile,dict) else {}
            drafts=[]
            for row in _draft_list(sid)[:6]:
                if not isinstance(row,dict):
                    continue
                drafts.append({
                    "id":_safe_id(row.get("id","")),
                    "title":str(row.get("title") or row.get("source_name") or "Gameplay")[:120],
                    "source_name":str(row.get("source_name") or "Gameplay")[:120],
                    "duration":int(row.get("duration") or 0),
                    "updated_at":float(row.get("updated_at") or 0),
                })
            project={}
            account_id=_safe_id(profile.get("account_id","")) if isinstance(profile,dict) else ""
            try:
                project_root=(ROOT/"creator-projects"/account_id) if account_id else (ROOT/"sessions"/sid/"projects")
                idx=json.loads((project_root/"index.json").read_text(encoding="utf-8"))
                pid=_safe_id(idx.get("active_project_id",""))
                if pid:
                    pdata=json.loads((project_root/pid/"project_state.json").read_text(encoding="utf-8"))
                    project={
                        "id":pid,
                        "updated_at":float(pdata.get("updated_at") or idx.get("updated_at") or 0),
                        "has_source":bool((pdata.get("state") or {}).get("gsf_source_path") or (pdata.get("state") or {}).get("gsf_editor_source_path")),
                    }
            except Exception:
                pass
            _json(self,200,{
                "ok":True,
                "account":{
                    "connected":bool(account_id),
                    "id":account_id,
                    "display_name":str(profile.get("display_name") or "Creator")[:120] if isinstance(profile,dict) else "Creator",
                    "plan":str(profile.get("plan") or "FREE")[:24] if isinstance(profile,dict) else "FREE",
                },
                "social":{
                    "youtube":bool(_youtube_user_load(sid)),
                    "tiktok":bool(_tiktok_user_load(sid)),
                    "instagram":bool(_instagram_user_load(sid)),
                    "facebook":False,
                },
                "stats":{
                    "shorts_created":int(profile.get("shorts_created") or 0) if isinstance(profile,dict) else 0,
                    "shorts_published":int(profile.get("shorts_published") or 0) if isinstance(profile,dict) else 0,
                    "drafts":len(_draft_list(sid)),
                    "social":sum(1 for x in (_youtube_user_load(sid),_tiktok_user_load(sid),_instagram_user_load(sid)) if x),
                },
                "drafts":drafts,
                "project":project,
            })
            return
        if clean=="/account":
            sid=_social_sid(self)
            if not sid:
                _html(self,400,"Sessione browser non valida.")
                return
            _html(self,200,_creator_page(sid))
            return
        if clean=="/account/logout":
            sid=_social_sid(self)
            _creator_logout(sid)
            _redirect(self,"/account")
            return
        if clean=="/account/google/start":
            _creator_google_start(self,_social_sid(self))
            return
        if clean=="/account/google/callback":
            _creator_google_callback(self,parse_qs(path.query))
            return
        if clean=="/account/facebook/start":
            _creator_facebook_start(self,_social_sid(self))
            return
        if clean=="/account/facebook/callback":
            _creator_facebook_callback(self,parse_qs(path.query))
            return
        if clean=="/account/tiktok/start":
            _creator_tiktok_start(self,_social_sid(self))
            return
        if clean=="/account/tiktok/callback":
            _creator_tiktok_callback(self,parse_qs(path.query))
            return
        if clean=="/social-connect":
            sid=_social_sid(self)
            if not sid:
                _html(self,400,"Sessione browser non valida.")
                return
            _html(self,200,_social_page(sid))
            return
        if clean=="/social-connect/tiktok/start":
            _tiktok_oauth_start(self,_social_sid(self))
            return
        if clean=="/social-connect/tiktok/callback":
            _tiktok_oauth_callback(self,parse_qs(path.query))
            return
        if clean=="/social-connect/youtube/start":
            _youtube_oauth_start(self,_social_sid(self))
            return
        if clean=="/social-connect/youtube/callback":
            _youtube_oauth_callback(self,parse_qs(path.query))
            return
        if clean=="/social-connect/instagram/start":
            _instagram_oauth_start(self,_social_sid(self))
            return
        if clean in ("/social-connect/instagram/callback","/auth/instagram/callback"):
            _instagram_oauth_callback(self,parse_qs(path.query))
            return
        if clean=="/capabilities":
            _json(self,200,{
                "ok":True,
                "bucket":_bucket_enabled(),
                "worker":bool(WORKER_URL),
                "part_size":BUCKET_PART_BYTES,
                "concurrency":_upload_concurrency_for_user_agent(self.headers.get("User-Agent","")),
                "materialize_part_size":8*1024*1024,
                "materialize_concurrency":_materialize_concurrency(),
                "fallback_chunk_size":16*1024*1024,
                "fallback_concurrency":6,
            })
            return
        if clean=="/bucket/status":
            sid=_safe_id(self.headers.get("X-GSF-Session-ID"))
            upload_id=_safe_id((parse_qs(path.query).get("upload_id") or [""])[0])
            if not sid or not upload_id:
                _json(self,400,{"ok":False,"error":"invalid status id"})
                return
            media=ROOT/"sessions"/sid/"media"
            marker=media/".direct_upload_ready.json"
            error=media/".direct_upload_error.json"
            if marker.is_file():
                try:
                    data=json.loads(marker.read_text(encoding="utf-8"))
                    if str(data.get("upload_id",""))==upload_id:
                        _json(self,200,{"ok":True,"ready":True})
                        return
                except Exception:
                    pass
            if error.is_file():
                try:
                    data=json.loads(error.read_text(encoding="utf-8"))
                    if str(data.get("upload_id",""))==upload_id:
                        _json(self,500,{"ok":False,"ready":False,"error":str(data.get("error","preparation failed"))})
                        return
                except Exception:
                    pass
            _json(self,200,{"ok":True,"ready":False})
            return
        _json(self,404,{"ok":False,"error":"not found"})

    def do_POST(self):
        path=urlparse(self.path).path.rstrip("/")
        sid=_safe_id(self.headers.get("X-GSF-Session-ID"))
        if not sid:
            _json(self,400,{"ok":False,"error":"invalid session"})
            return

        if path=="/ai/feedback":
            try:
                data=_read_json(self,max_bytes=64*1024)
                ok=_ai_feedback_store(sid,data)
                _json(self,200,{"ok":bool(ok)})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return

        if path=="/content-memory/check":
            try:
                data=_read_json(self,max_bytes=128*1024)
                record=data.get("record") if isinstance(data.get("record"),dict) else data
                state=_content_memory_check(sid,record)
                _json(self,200,{"ok":True,"memory":state})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return

        if path=="/content-memory/record":
            try:
                data=_read_json(self,max_bytes=128*1024)
                record=data.get("record") if isinstance(data.get("record"),dict) else data
                state=_content_memory_record(sid,record)
                _json(self,200,{"ok":True,"memory":state})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return

        if path=="/social-analytics/register":
            try:
                data=_read_json(self,max_bytes=128*1024)
                state=_analytics_register(sid,data)
                _json(self,200,state)
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:220]})
            return

        if path=="/social-analytics/collect":
            try:
                data=_read_json(self,max_bytes=64*1024)
                force=bool(data.get("force",False)) if isinstance(data,dict) else False
                state=_analytics_collect_all(sid,force=force)
                state["context"]=_analytics_context(sid)
                _json(self,200,state)
            except Exception as exc:
                _json(self,500,{"ok":False,"error":str(exc)[:240]})
            return

        if path=="/social-analytics/context":
            try:
                _json(self,200,{"ok":True,"context":_analytics_context(sid)})
            except Exception as exc:
                _json(self,500,{"ok":False,"error":str(exc)[:220]})
            return

        if path=="/drafts/save":
            try:
                data=_read_json(self,max_bytes=1024*1024)
                draft=_draft_save(sid,data)
                _json(self,200,{"ok":True,"id":draft.get("id"),"title":draft.get("title")})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return

        if path=="/push/subscribe":
            try:
                _push_save_subscription(sid,_read_json(self,max_bytes=64*1024))
                _json(self,200,{"ok":True})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return

        if path=="/push/notify":
            try:
                data=_read_json(self,max_bytes=64*1024)
                sent=_push_notify_sid(
                    sid,
                    title=data.get("title") or "Short pronto",
                    body=data.get("body") or "Il tuo Short è pronto da condividere.",
                    url=data.get("url") or "/",
                    tag=data.get("tag") or "gsf-short-ready",
                )
                _json(self,200,{"ok":True,"sent":bool(sent)})
            except Exception as exc:
                _json(self,500,{"ok":False,"error":str(exc)[:180]})
            return

        if path=="/final/persist":
            try:
                data=_read_json(self,max_bytes=64*1024)
                meta=_final_persist_to_bucket(
                    sid,
                    data.get("path"),
                    float(data.get("started_at") or 0.0),
                )
                _json(self,200,{"ok":True,"final_bytes":meta.get("final_bytes"),"completed_at":meta.get("completed_at")})
            except Exception as exc:
                _json(self,500,{"ok":False,"error":str(exc)[:220]})
            return

        if path=="/bucket/init":
            if not _bucket_enabled():
                _json(self,503,{"ok":False,"error":"bucket unavailable"})
                return
            try:
                data=_read_json(self)
                original_name,safe_stem,ext=_safe_filename(data.get("name"))
                total=int(data.get("size",0))
                content_type=str(data.get("type") or "application/octet-stream")
                if total<=0 or total>MAX_FILE_BYTES:
                    raise ValueError("file size not allowed")
                upload_id=uuid.uuid4().hex[:20]
                key=f"uploads/{sid}/{upload_id}/{safe_stem}{ext}"
                analysis_key=f"analysis/{sid}/{upload_id}/v52-keyframe-turbo.json"
                created=_s3().create_multipart_upload(
                    Bucket=S3_BUCKET,
                    Key=key,
                    ContentType=content_type,
                    Metadata={
                        "gsf-upload-id":upload_id,
                        "gsf-original-name":original_name[:200],
                    },
                )
                multipart_id=created["UploadId"]
                count=(total+BUCKET_PART_BYTES-1)//BUCKET_PART_BYTES
                urls=[]
                for part_number in range(1,count+1):
                    url=_s3().generate_presigned_url(
                        "upload_part",
                        Params={
                            "Bucket":S3_BUCKET,
                            "Key":key,
                            "UploadId":multipart_id,
                            "PartNumber":part_number,
                        },
                        ExpiresIn=3600,
                    )
                    urls.append({"number":part_number,"url":url})
                _json(self,200,{
                    "ok":True,
                    "mode":"bucket",
                    "upload_id":upload_id,
                    "multipart_id":multipart_id,
                    "key":key,
                    "analysis_key":analysis_key,
                    "part_size":BUCKET_PART_BYTES,
                    "concurrency":_upload_concurrency_for_user_agent(self.headers.get("User-Agent","")),
                    "parts":urls,
                })
            except Exception as exc:
                _json(self,500,{"ok":False,"error":str(exc)[:240]})
            return

        if path=="/bucket/complete":
            if not _bucket_enabled():
                _json(self,503,{"ok":False,"error":"bucket unavailable"})
                return
            try:
                data=_read_json(self)
                upload_id=_safe_id(data.get("upload_id"))
                multipart_id=str(data.get("multipart_id") or "")
                key=str(data.get("key") or "")
                analysis_key=str(data.get("analysis_key") or "")
                original_name,safe_stem,ext=_safe_filename(data.get("name"))
                total=int(data.get("size",0))
                parts=data.get("parts") or []
                prefix=f"uploads/{sid}/{upload_id}/"
                expected_analysis=f"analysis/{sid}/{upload_id}/"
                if not upload_id or not multipart_id or not key.startswith(prefix):
                    raise ValueError("invalid multipart metadata")
                if not analysis_key.startswith(expected_analysis):
                    raise ValueError("invalid analysis key")
                if total<=0 or total>MAX_FILE_BYTES:
                    raise ValueError("invalid file size")
                clean_parts=[]
                for item in parts:
                    pn=int(item.get("PartNumber",0))
                    etag=str(item.get("ETag") or "").strip()
                    if pn<=0 or not etag:
                        raise ValueError("invalid multipart part")
                    clean_parts.append({"PartNumber":pn,"ETag":etag})
                clean_parts.sort(key=lambda x:x["PartNumber"])
                _s3().complete_multipart_upload(
                    Bucket=S3_BUCKET,
                    Key=key,
                    UploadId=multipart_id,
                    MultipartUpload={"Parts":clean_parts},
                )

                prescan_payload={
                    "key":key,
                    "analysis_key":analysis_key,
                    "engine_version":"v52-keyframe-turbo",
                    "name":original_name,
                    "size":total,
                }
                threading.Thread(
                    target=_trigger_prescan,
                    args=(prescan_payload,),
                    daemon=True,
                ).start()
                threading.Thread(
                    target=_materialize_bucket_object,
                    args=(sid,upload_id,key,original_name,safe_stem,ext,total,analysis_key),
                    daemon=True,
                ).start()
                _json(self,202,{"ok":True,"upload_id":upload_id,"preparing":True})
            except Exception as exc:
                _json(self,500,{"ok":False,"error":str(exc)[:240]})
            return

        if path=="/bucket/abort":
            try:
                data=_read_json(self)
                upload_id=_safe_id(data.get("upload_id"))
                key=str(data.get("key") or "")
                multipart_id=str(data.get("multipart_id") or "")
                if not _bucket_enabled() or not upload_id or not key.startswith(f"uploads/{sid}/{upload_id}/"):
                    raise ValueError("invalid abort metadata")
                _s3().abort_multipart_upload(Bucket=S3_BUCKET,Key=key,UploadId=multipart_id)
                _json(self,200,{"ok":True})
            except Exception as exc:
                _json(self,400,{"ok":False,"error":str(exc)[:180]})
            return

        _json(self,404,{"ok":False,"error":"not found"})

    def do_PUT(self):
        if self.path.split("?",1)[0].rstrip("/") != "/chunk":
            _json(self,404,{"ok":False,"error":"not found"})
            return

        sid=_safe_id(self.headers.get("X-GSF-Session-ID"))
        upload_id=_safe_id(self.headers.get("X-GSF-Upload-ID"))
        if not sid or not upload_id:
            _json(self,400,{"ok":False,"error":"invalid session or upload id"})
            return

        try:
            original_name,safe_stem,ext=_safe_filename(self.headers.get("X-GSF-Filename"))
            total=int(self.headers.get("X-GSF-File-Size","0"))
            start=int(self.headers.get("X-GSF-Chunk-Start","0"))
            index=int(self.headers.get("X-GSF-Chunk-Index","0"))
            count=int(self.headers.get("X-GSF-Chunk-Count","0"))
            length=int(self.headers.get("Content-Length","0"))
        except Exception:
            _json(self,400,{"ok":False,"error":"invalid upload metadata"})
            return

        if total<=0 or total>MAX_FILE_BYTES or start<0 or start>=total:
            _json(self,413,{"ok":False,"error":"file size not allowed"})
            return
        if length<=0 or length>MAX_CHUNK_BYTES or start+length>total:
            _json(self,413,{"ok":False,"error":"chunk size not allowed"})
            return
        if count<=0 or index<0 or index>=count:
            _json(self,400,{"ok":False,"error":"invalid chunk index"})
            return

        media=ROOT/"sessions"/sid/"media"
        upload_dir=ROOT/"sessions"/sid/"direct_upload"/upload_id
        media.mkdir(parents=True,exist_ok=True)
        upload_dir.mkdir(parents=True,exist_ok=True)
        data_path=upload_dir/"upload.tmp"
        state_path=upload_dir/"state.json"
        lock=_state_lock(sid,upload_id)

        try:
            with lock:
                if state_path.is_file():
                    state=json.loads(state_path.read_text(encoding="utf-8"))
                    if (
                        int(state.get("total",0))!=total
                        or int(state.get("count",0))!=count
                        or str(state.get("ext",""))!=ext
                    ):
                        _json(self,409,{"ok":False,"error":"upload metadata changed"})
                        return
                else:
                    state={
                        "total":total,
                        "count":count,
                        "name":original_name,
                        "stem":safe_stem,
                        "ext":ext,
                        "ranges":{},
                        "received":[],
                    }
                    with open(data_path,"wb") as seed:
                        seed.truncate(total)
                    _write_json_atomic(state_path,state)

                ranges=dict(state.get("ranges",{}) or {})
                this_range=[start,length]
                existing=ranges.get(str(index))
                if existing is not None and list(existing)!=this_range:
                    _json(self,409,{"ok":False,"error":"chunk metadata changed"})
                    return
                for other_index,other_range in ranges.items():
                    if str(other_index)==str(index):
                        continue
                    try:
                        other_start=int(other_range[0])
                        other_end=other_start+int(other_range[1])
                    except Exception:
                        continue
                    this_end=start+length
                    if start<other_end and other_start<this_end:
                        _json(self,409,{"ok":False,"error":"overlapping chunk ranges"})
                        return
                ranges[str(index)]=this_range
                state["ranges"]=ranges
                _write_json_atomic(state_path,state)

            fd=os.open(str(data_path),os.O_WRONLY)
            try:
                remaining=length
                offset=start
                while remaining>0:
                    block=self.rfile.read(min(1024*1024,remaining))
                    if not block:
                        raise IOError("client disconnected")
                    view=memoryview(block)
                    written=0
                    while written<len(view):
                        n=os.pwrite(fd,view[written:],offset+written)
                        if n<=0:
                            raise IOError("short positional write")
                        written+=n
                    offset+=len(block)
                    remaining-=len(block)
            finally:
                os.close(fd)

            completed=False
            with lock:
                state=json.loads(state_path.read_text(encoding="utf-8"))
                received={int(x) for x in (state.get("received",[]) or [])}
                received.add(index)
                state["received"]=sorted(received)
                _write_json_atomic(state_path,state)

                if len(received)==count and received==set(range(count)):
                    fd=os.open(str(data_path),os.O_RDONLY)
                    try:
                        os.fsync(fd)
                    finally:
                        os.close(fd)

                    if data_path.stat().st_size!=total:
                        _json(self,409,{"ok":False,"error":"incomplete upload"})
                        return

                    final=media/f"source_direct_{safe_stem}_{upload_id}{ext}"
                    os.replace(data_path,final)
                    marker=media/".direct_upload_ready.json"
                    _write_json_atomic(marker,{
                        "path":str(final),
                        "name":original_name,
                        "size":total,
                        "upload_id":upload_id,
                        "completed_at":time.time(),
                        "storage":"direct_fallback",
                    })
                    if _bucket_enabled():
                        threading.Thread(
                            target=_persist_fallback_source_to_bucket,
                            args=(sid,upload_id,str(final),original_name,total),
                            daemon=True,
                        ).start()
                    state_path.unlink(missing_ok=True)
                    try:
                        upload_dir.rmdir()
                    except OSError:
                        pass
                    try:
                        os.utime(ROOT/"sessions"/sid/".active",None)
                    except Exception:
                        pass
                    completed=True

            _json(self,200,{
                "ok":True,
                "completed":completed,
                "index":index,
                "bytes":start+length
            })
        except Exception as exc:
            _json(self,500,{"ok":False,"error":str(exc)[:160]})

def _start_social_analytics_worker():
    interval=max(900,int(os.environ.get("GSF_SOCIAL_ANALYTICS_INTERVAL","1800") or 1800))
    def run():
        time.sleep(45)
        while True:
            try:
                sessions=ROOT/"sessions"
                if sessions.is_dir():
                    for root in list(sessions.iterdir())[:200]:
                        if not root.is_dir():
                            continue
                        sid=_safe_id(root.name)
                        if not sid:
                            continue
                        try:
                            data=_analytics_load(sid)
                            if data.get("records"):
                                result=_analytics_collect_all(sid,force=True)
                                print(
                                    "GSF_V148_ANALYTICS_REFRESH",
                                    sid,
                                    "records="+str(len(result.get("records") or [])),
                                    flush=True,
                                )
                        except Exception as exc:
                            print("GSF_V148_ANALYTICS_WARN",sid,repr(str(exc))[:180],flush=True)
            except Exception as exc:
                print("GSF_V148_ANALYTICS_LOOP_WARN",repr(str(exc))[:180],flush=True)
            time.sleep(interval)
    threading.Thread(target=run,name="gsf-social-analytics-v148",daemon=True).start()


if __name__=="__main__":
    ROOT.mkdir(parents=True,exist_ok=True)
    _ensure_bucket_cors()
    _ai_learning_restore()
    _start_proactive_guardian()
    _start_social_analytics_worker()
    server=ThreadingHTTPServer(("127.0.0.1",PORT),Handler)
    print(
        f"GSF direct upload server listening on 127.0.0.1:{PORT} "
        f"bucket={'on' if _bucket_enabled() else 'off'} worker={'on' if WORKER_URL else 'off'}",
        flush=True
    )
    server.serve_forever()
