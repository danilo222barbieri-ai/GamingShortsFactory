#!/usr/bin/env python3
import json
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

ROOT=Path(os.environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime"))
PORT=int(os.environ.get("GSF_DIRECT_UPLOAD_PORT","8502"))
MAX_FILE_BYTES=4*1024*1024*1024
MAX_CHUNK_BYTES=40*1024*1024
BUCKET_PART_BYTES=32*1024*1024
BUCKET_CONCURRENCY=10
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
TIKTOK_CLIENT_KEY=_env_first("GSF_TIKTOK_CLIENT_KEY",default="")
TIKTOK_CLIENT_SECRET=_env_first("GSF_TIKTOK_CLIENT_SECRET",default="")
YOUTUBE_CLIENT_ID=_env_first("GSF_YOUTUBE_CLIENT_ID",default="")
YOUTUBE_CLIENT_SECRET=_env_first("GSF_YOUTUBE_CLIENT_SECRET",default="")
YOUTUBE_SCOPE="https://www.googleapis.com/auth/youtube.upload"
META_APP_ID=_env_first("GSF_META_APP_ID",default="")
META_APP_SECRET=_env_first("GSF_META_APP_SECRET",default="")
META_SCOPES="pages_show_list,instagram_basic,instagram_content_publish,pages_read_engagement"
_S3_CLIENT=None
_S3_LOCK=threading.Lock()

def _bucket_enabled():
    return bool(S3_BUCKET and S3_ACCESS_KEY and S3_SECRET_KEY and S3_ENDPOINT)

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
    if not _bucket_enabled() or not PUBLIC_ORIGIN:
        return
    try:
        _s3().put_bucket_cors(
            Bucket=S3_BUCKET,
            CORSConfiguration={
                "CORSRules":[{
                    "AllowedHeaders":["*"],
                    "AllowedMethods":["GET","HEAD","PUT","POST"],
                    "AllowedOrigins":[PUBLIC_ORIGIN],
                    "ExposeHeaders":["ETag"],
                    "MaxAgeSeconds":3000,
                }]
            },
        )
        print(f"GSF bucket CORS ready for {PUBLIC_ORIGIN}",flush=True)
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
        return
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
        print(f"GSF worker prescan queued: {payload.get('analysis_key','')}",flush=True)
    except Exception as exc:
        print(f"GSF worker prescan warning: {str(exc)[:180]}",flush=True)

def _materialize_bucket_object(sid,upload_id,key,original_name,safe_stem,ext,total,analysis_key):
    media=ROOT/"sessions"/sid/"media"
    media.mkdir(parents=True,exist_ok=True)
    final=media/f"source_bucket_{safe_stem}_{upload_id}{ext}"
    tmp=media/f".source_bucket_{safe_stem}_{upload_id}{ext}.tmp"
    try:
        cfg=TransferConfig(
            multipart_threshold=8*1024*1024,
            multipart_chunksize=8*1024*1024,
            max_concurrency=12,
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
        print(f"GSF bucket materialized {upload_id}: {total} bytes",flush=True)
    except Exception as exc:
        tmp.unlink(missing_ok=True)
        error=media/".direct_upload_error.json"
        _write_json_atomic(error,{
            "upload_id":upload_id,
            "error":str(exc)[:240],
            "failed_at":time.time(),
        })
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
        if META_APP_ID and META_APP_SECRET
        else '<div class="note">Configurazione Meta non ancora presente sul server.</div>'
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
    if not (PUBLIC_APP_URL and META_APP_ID and META_APP_SECRET):
        _html(handler,503,_social_page(
            sid,
            "Instagram richiede GSF_META_APP_ID e GSF_META_APP_SECRET sul server."
        ))
        return
    state="gsfig_"+secrets.token_urlsafe(28)
    state_dir=ROOT/"social_oauth"
    state_dir.mkdir(parents=True,exist_ok=True)
    _write_json_atomic(state_dir/(state+".json"),{
        "created":time.time(),
        "sid":sid,
        "platform":"Instagram",
    })
    params={
        "client_id":META_APP_ID,
        "redirect_uri":PUBLIC_APP_URL,
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
    if not state.startswith("gsfig_") or not sid or not created or time.time()-created>900:
        _html(handler,400,"Stato OAuth Instagram scaduto o non valido. Riapri /social-connect.")
        return
    if err:
        _html(handler,400,_social_page(sid,"Instagram: "+err))
        return
    if not code:
        _html(handler,400,_social_page(sid,"Instagram non ha restituito il codice di autorizzazione."))
        return

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

        # Prefer a long-lived user token when Meta allows the exchange.
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
        if clean=="/social-connect/instagram/callback":
            _instagram_oauth_callback(self,parse_qs(path.query))
            return
        if clean=="/capabilities":
            _json(self,200,{
                "ok":True,
                "bucket":_bucket_enabled(),
                "worker":bool(WORKER_URL),
                "part_size":BUCKET_PART_BYTES,
                "concurrency":BUCKET_CONCURRENCY,
                "materialize_part_size":8*1024*1024,
                "materialize_concurrency":12,
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
                    "concurrency":BUCKET_CONCURRENCY,
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
