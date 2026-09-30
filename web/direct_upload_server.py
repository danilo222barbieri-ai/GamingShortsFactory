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
YOUTUBE_SCOPE="https://www.googleapis.com/auth/youtube.upload"
INSTAGRAM_APP_ID=_env_first("GSF_INSTAGRAM_APP_ID",default="")
INSTAGRAM_APP_SECRET=_env_first("GSF_INSTAGRAM_APP_SECRET",default="")
INSTAGRAM_SCOPES="instagram_business_basic,instagram_business_content_publish"
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
                "src":"/app-icon-192.png",
                "sizes":"192x192",
                "type":"image/png",
                "purpose":"any"
            },
            {
                "src":"/app-icon-512.png",
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
  const toU8=(s)=>{const pad="=".repeat((4-s.length%4)%4);const raw=atob((s+pad).replace(/-/g,"+").replace(/_/g,"/"));return Uint8Array.from([...raw].map(c=>c.charCodeAt(0)));};
  const subscribe=async(promptUser)=>{if(!("serviceWorker" in navigator)||!("PushManager" in window)||!("Notification" in window))return false;const reg=await navigator.serviceWorker.register("/gsf-sw.js?v=1",{scope:"/"});let permission=Notification.permission;if(permission==="default"&&promptUser)permission=await Notification.requestPermission();if(permission!=="granted")return false;const key=await fetch("/push/public-key",{cache:"no-store"}).then(r=>r.json()).then(x=>x.public_key||"");if(!key)return false;let sub=await reg.pushManager.getSubscription();if(!sub)sub=await reg.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:toU8(key)});await fetch("/push/subscribe",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(sub.toJSON())});return true;};
  window.GSFPush={enable:()=>subscribe(true),ensure:()=>subscribe(false)};
  let uploadActive=false,lastRenderStatus="";
  const ensureHud=()=>{let el=document.getElementById("gsf-activity-hud");if(el)return el;const style=document.createElement("style");style.textContent="#gsf-activity-hud{position:fixed;right:16px;bottom:18px;z-index:2147482998;display:none;align-items:center;gap:10px;max-width:min(360px,calc(100vw - 30px));padding:11px 14px;border-radius:16px;border:1px solid rgba(185,215,233,.9);background:rgba(255,255,255,.94);backdrop-filter:blur(14px);box-shadow:0 12px 30px rgba(45,83,110,.18);color:#446b84;font:800 11px/1.25 ui-sans-serif,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}#gsf-activity-hud .spin{width:17px;height:17px;border:2px solid #d5e8f3;border-top-color:#735ee2;border-radius:50%;animation:gsfSpin .8s linear infinite;flex:0 0 17px}#gsf-activity-hud.done .spin{animation:none;border:0;width:18px;height:18px}#gsf-activity-hud.done .spin:before{content:'✓';display:grid;place-items:center;width:18px;height:18px;border-radius:50%;background:#daf3e7;color:#35815f;font-size:12px}@keyframes gsfSpin{to{transform:rotate(360deg)}}@media(max-width:600px){#gsf-activity-hud{right:10px;left:10px;bottom:76px;max-width:none}}";document.head.appendChild(style);el=document.createElement("div");el.id="gsf-activity-hud";el.innerHTML='<span class="spin"></span><span class="txt"></span>';document.body.appendChild(el);return el;};
  const showHud=(txt,done=false)=>{const el=ensureHud();el.classList.toggle("done",!!done);el.querySelector(".txt").textContent=txt;el.style.display="flex";};const hideHud=()=>{const el=document.getElementById("gsf-activity-hud");if(el)el.style.display="none";};
  window.addEventListener("message",(event)=>{const d=event.data||{};if(d.type!=="gsf-upload")return;if(d.state==="running"){uploadActive=true;showHud("Caricamento video in corso · "+Number(d.progress||0)+"%");}else if(d.state==="done"){uploadActive=false;showHud("Video caricato ✓",true);setTimeout(()=>{if(lastRenderStatus!=="running")hideHud();},1600);}else if(d.state==="error"){uploadActive=false;showHud("Upload interrotto · riprova",true);setTimeout(()=>{if(lastRenderStatus!=="running")hideHud();},2200);}});
  window.addEventListener("beforeunload",(event)=>{if(!uploadActive)return;event.preventDefault();event.returnValue="";});
  const pollJob=async()=>{try{const j=await fetch("/job/status",{cache:"no-store"}).then(r=>r.json());const status=String(j.render_status||"");lastRenderStatus=status;if(status==="running")showHud("Creazione Short in corso · puoi continuare a usare l’app");else if(status==="ready"&&!uploadActive){showHud("Short pronto · apri lo Share Hub",true);setTimeout(()=>{if(!uploadActive)hideHud();},2500);}else if(status==="failed"&&!uploadActive){showHud("Creazione Short interrotta · riprova",true);setTimeout(()=>{if(!uploadActive)hideHud();},3000);}else if(!uploadActive)hideHud();}catch(e){}};setInterval(pollJob,1500);pollJob();
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
    source_ref={}
    try:
        marker=ROOT/"sessions"/sid/"media"/".direct_upload_ready.json"
        if marker.is_file():
            meta=json.loads(marker.read_text(encoding="utf-8"))
            if isinstance(meta,dict):
                source_ref={
                    "name":str(meta.get("name") or source_name),
                    "size":int(meta.get("size") or 0),
                    "upload_id":str(meta.get("upload_id") or ""),
                    "storage":str(meta.get("storage") or ""),
                    "bucket_key":str(meta.get("bucket_key") or ""),
                    "analysis_key":str(meta.get("analysis_key") or ""),
                    "path":str(meta.get("path") or state.get("gsf_source_path") or ""),
                }
    except Exception:
        source_ref={}
    source_path=Path(str(state.get("gsf_source_path") or source_ref.get("path") or ""))
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
        "id":draft_id,
        "title":str(payload.get("title") or ("Bozza · "+source_name))[:180],
        "source_name":source_name,
        "created_at":float(payload.get("created_at") or now),
        "updated_at":now,
        "state":state,
        "source_ref":source_ref,
    }
    path=_draft_dir(sid)/(draft_id+".json")
    _write_json_atomic(path,draft)
    if _bucket_enabled():
        _s3().put_object(
            Bucket=S3_BUCKET,Key=_draft_key(sid,draft_id),
            Body=json.dumps(draft,ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",CacheControl="no-store"
        )
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

def _draft_list(sid):
    sid=_safe_id(sid)
    found={}
    if not sid:
        return []
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
            rows=_s3().list_objects_v2(Bucket=S3_BUCKET,Prefix=f"drafts/{sid}/",MaxKeys=30).get("Contents") or []
            for row in rows:
                key=str(row.get("Key") or "")
                if not key.endswith(".json"):
                    continue
                try:
                    obj=_s3().get_object(Bucket=S3_BUCKET,Key=key)
                    data=json.loads(obj["Body"].read().decode("utf-8"))
                    if isinstance(data,dict) and data.get("id"):
                        found[str(data["id"])]=data
                except Exception:
                    pass
        except Exception:
            pass
    return sorted(found.values(),key=lambda x:float(x.get("updated_at") or 0),reverse=True)[:20]

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
    return True

def _draft_prepare_resume(sid,draft):
    state=dict(draft.get("state") or {})
    source_ref=dict(draft.get("source_ref") or {})
    source_name=str(draft.get("source_name") or source_ref.get("name") or "Gameplay")
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
    if candidate.is_file():
        state["gsf_source_path"]=str(candidate)
        state["gsf_editor_source_path"]=str(candidate)
        state["gsf_source_name"]=source_name
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
        try:
            updated=time.strftime("%d/%m · %H:%M",time.localtime(float(draft.get("updated_at") or 0)))
        except Exception:
            updated=""
        href="/drafts/resume?id="+urllib.parse.quote(did,safe="")
        delete_href="/drafts/delete?id="+urllib.parse.quote(did,safe="")
        rows.append(
            '<div class="draftCard"><div class="draftInfo"><strong>'+title+'</strong><span>'+source+' · '+html.escape(updated)+
            '</span></div><div class="draftActions"><a class="draftOpen" href="'+href+'">RIPRENDI</a>'+
            '<a class="draftDelete" href="'+delete_href+'" onclick="return confirm(\'Eliminare questa bozza?\')">ELIMINA</a></div></div>'
        )
    return '<div class="draftGrid">'+"".join(rows)+'</div>'

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
.draftGrid{{display:grid;gap:9px}}.draftCard{{display:flex;align-items:center;justify-content:space-between;gap:12px;background:#f8fbfe;border:1px solid #dce9f2;border-radius:16px;padding:13px 14px}}.draftInfo{{display:flex;flex-direction:column;gap:3px;min-width:0}}.draftInfo strong{{font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.draftInfo span{{font-size:10px;color:#7e92a2}}.draftActions{{display:flex;align-items:center;gap:6px;flex-wrap:wrap}}.draftOpen{{text-decoration:none;color:#356f91;background:linear-gradient(135deg,#eef8ff,#f1eeff);border:1px solid #cfe5f3;border-radius:12px;padding:8px 10px;font-size:10px;font-weight:900;box-shadow:0 4px 10px #345d7810}}.draftDelete{{text-decoration:none;color:#8b6170;background:linear-gradient(135deg,#fff7f9,#f8eef3);border:1px solid #ead5dd;border-radius:12px;padding:8px 10px;font-size:10px;font-weight:900;box-shadow:0 4px 10px #6f3e5110}}.draftEmpty{{font-size:12px;color:#71899a;background:#f8fbfe;border:1px dashed #cbdde9;border-radius:16px;padding:14px;line-height:1.45}}.back{{display:block;text-align:center;margin:18px auto 0;color:#6d8799;text-decoration:none;font-size:11px;font-weight:800}}
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
<a class="back" href="/" onclick="if(window.opener){window.close();return false;}">← Torna alla pagina principale</a>
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
.draftGrid{{display:grid;gap:9px}}.draftCard{{display:flex;align-items:center;justify-content:space-between;gap:12px;background:#f8fbfe;border:1px solid #dce9f2;border-radius:16px;padding:13px 14px}}.draftInfo{{display:flex;flex-direction:column;gap:3px;min-width:0}}.draftInfo strong{{font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.draftInfo span{{font-size:10px;color:#7e92a2}}.draftActions{{display:flex;align-items:center;gap:6px;flex-wrap:wrap}}.draftOpen{{text-decoration:none;color:#356f91;background:linear-gradient(135deg,#eef8ff,#f1eeff);border:1px solid #cfe5f3;border-radius:12px;padding:8px 10px;font-size:10px;font-weight:900;box-shadow:0 4px 10px #345d7810}}.draftDelete{{text-decoration:none;color:#8b6170;background:linear-gradient(135deg,#fff7f9,#f8eef3);border:1px solid #ead5dd;border-radius:12px;padding:8px 10px;font-size:10px;font-weight:900;box-shadow:0 4px 10px #6f3e5110}}.draftEmpty{{font-size:12px;color:#71899a;background:#f8fbfe;border:1px dashed #cbdde9;border-radius:16px;padding:14px;line-height:1.45}}.logout{{display:block;text-align:center;color:#8a6170;text-decoration:none;font-size:12px;font-weight:800;margin-top:18px}} .back-bottom{{display:block;text-align:center;color:#6d8799;text-decoration:none;font-size:11px;font-weight:800;margin-top:14px}}
@media(max-width:560px){{.stats{{grid-template-columns:1fr 1fr 1fr}} .stat{{padding:10px 5px}} .stat b{{font-size:17px}} .socials{{grid-template-columns:1fr}}}}
</style></head><body><main>
<div class="top"><div class="brand">GAMING SHORTS FACTORY</div></div>
<div class="profile">{msg}<div class="who">{avatar_html}<div><div class="name">{name}</div><div class="mail">{email}</div><span class="badge">{plan}</span><div class="providerBadges">{provider_badges}</div></div></div>
<div class="stats"><div class="stat"><b>{shorts_created}</b><span>SHORT CREATI</span></div><div class="stat"><b>{shorts_published}</b><span>PUBBLICATI</span></div><div class="stat"><b>{connected}/4</b><span>SOCIAL</span></div></div>
<div class="level"><div class="levelHead"><span>Creator Level {level} · Rookie</span><span>18%</span></div><div class="bar"><i></i></div></div>
<h2>Le tue bozze</h2>{drafts_html}<h2>I tuoi social</h2><div class="socials">{socials}</div>
<h2>Auto Highlights</h2><div class="auto"><div class="auto-k">AUTO HIGHLIGHTS</div><div class="auto-title">Tu fai la live. GSF trova i momenti da pubblicare.</div><div class="auto-sub">Collega i tuoi account live per trovare automaticamente i momenti migliori e portarli nel Game Editor.</div></div>
<h2>Prossimamente</h2><div class="future">Storico Short · Cloud · Piano Pro · Crediti AI · Achievement · Classifica Creator.</div>
<a class="logout" href="/account/logout">Esci dal Creator Hub</a><a class="back-bottom" href="/" onclick="if(window.opener){window.close();return false;}">← Torna alla pagina principale</a>
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
        "scope":"user.info.basic,video.publish",
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


class Handler(BaseHTTPRequestHandler):
    server_version="GSFDirectUpload/2.0"

    def log_message(self,fmt,*args):
        return

    def do_GET(self):
        path=urlparse(self.path)
        clean=path.path.rstrip("/")
        if clean in ("","/health"):
            _json(self,200,{"ok":True,"bucket":_bucket_enabled(),"worker":bool(WORKER_URL)})
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
        if clean=="/job/status":
            sid=_social_sid(self);payload={}
            if sid:
                job=ROOT/"sessions"/sid/"render_job.json"
                if job.is_file():
                    try:
                        payload=json.loads(job.read_text(encoding="utf-8"))
                        if not isinstance(payload,dict):payload={}
                    except Exception:payload={}
            status=str(payload.get("status") or "")
            if status=="running":
                started=float(payload.get("started_at") or 0.0)
                if started and time.time()-started>900:status="stale"
            _json(self,200,{"ok":True,"render_status":status,"started_at":payload.get("started_at"),"completed_at":payload.get("completed_at")})
            return
        if clean=="/editor-media/current":
            _editor_media_current(self,_social_sid(self))
            return
        if clean=="/drafts/resume":
            sid=_social_sid(self)
            draft_id=_safe_id((parse_qs(path.query).get("id") or [""])[0])
            draft=_draft_load(sid,draft_id)
            if not sid or not isinstance(draft,dict) or not draft:
                _html(self,404,"Bozza non trovata.")
                return
            state=_draft_prepare_resume(sid,draft)
            root=ROOT/"sessions"/sid
            root.mkdir(parents=True,exist_ok=True)
            _write_json_atomic(root/"session_state.json",state)
            _write_json_atomic(root/"draft_resume.json",{"draft_id":draft_id,"created_at":time.time()})
            _redirect(self,"/?draft_resume="+urllib.parse.quote(draft_id,safe=""))
            return
        if clean=="/drafts/delete":
            sid=_social_sid(self)
            draft_id=_safe_id((parse_qs(path.query).get("id") or [""])[0])
            if sid and draft_id:
                _draft_delete(sid,draft_id)
            _redirect(self,"/account")
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

if __name__=="__main__":
    ROOT.mkdir(parents=True,exist_ok=True)
    _ensure_bucket_cors()
    server=ThreadingHTTPServer(("127.0.0.1",PORT),Handler)
    print(
        f"GSF direct upload server listening on 127.0.0.1:{PORT} "
        f"bucket={'on' if _bucket_enabled() else 'off'} worker={'on' if WORKER_URL else 'off'}",
        flush=True
    )
    server.serve_forever()
