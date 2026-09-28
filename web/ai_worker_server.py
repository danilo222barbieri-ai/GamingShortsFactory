#!/usr/bin/env python3
import ast
import hashlib
import json
import math
import os
import re
import subprocess
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig

PORT=int(os.environ.get("PORT","8600"))
WORKER_TOKEN=os.environ.get("GSF_WORKER_TOKEN","")
AI_APP_PATH=Path(os.environ.get("GSF_AI_APP_PATH","/app/GamingShortsFactory_V99_FINAL_ARCH.py"))
MAX_BODY=256*1024
JOBS={}
JOBS_LOCK=threading.Lock()
SCAN_SEMAPHORE=threading.Semaphore(max(1,int(os.environ.get("GSF_WORKER_SCAN_SLOTS","1"))))

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
S3_STYLE=_env_first("GSF_S3_ADDRESSING_STYLE",default="virtual")
_S3=None
_SCAN_FN=None

def _bucket_enabled():
    return bool(S3_BUCKET and S3_ACCESS_KEY and S3_SECRET_KEY and S3_ENDPOINT)

def _s3():
    global _S3
    if _S3 is None and _bucket_enabled():
        _S3=boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style":S3_STYLE},
                retries={"max_attempts":3,"mode":"standard"},
            ),
        )
    return _S3

def _duration_video(path):
    cmd=[
        "ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(path)
    ]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60)
    return float((r.stdout or "0").strip() or 0.0)

def _load_scan_fn():
    global _SCAN_FN
    if _SCAN_FN is not None:
        return _SCAN_FN
    source=AI_APP_PATH.read_text(encoding="utf-8")
    tree=ast.parse(source)
    wanted={
        "_gsf_ai_scan_profile_for_duration",
        "_gsf_interpolate_motion_points",
        "_gsf_norm_series",
        "_gsf_ai_scan_base",
    }
    found={}
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in wanted:
            found[node.name]=node
    missing=wanted-set(found)
    if missing:
        raise RuntimeError(f"worker scan functions missing: {sorted(missing)}")
    module=ast.Module(body=[found[name] for name in (
        "_gsf_ai_scan_profile_for_duration",
        "_gsf_interpolate_motion_points",
        "_gsf_norm_series",
        "_gsf_ai_scan_base",
    )],type_ignores=[])
    ast.fix_missing_locations(module)
    ns={
        "math":math,
        "re":re,
        "subprocess":subprocess,
        "time":time,
        "ThreadPoolExecutor":ThreadPoolExecutor,
        "FFMPEG_PATH":"/usr/local/bin/ffmpeg",
        "durata_video":_duration_video,
    }
    exec(compile(module,str(AI_APP_PATH),"exec"),ns,ns)
    _SCAN_FN=ns["_gsf_ai_scan_base"]
    return _SCAN_FN

def _authorized(handler):
    if not WORKER_TOKEN:
        return True
    return handler.headers.get("X-GSF-Worker-Token","")==WORKER_TOKEN

def _json(handler,status,payload):
    body=json.dumps(payload,ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type","application/json; charset=utf-8")
    handler.send_header("Content-Length",str(len(body)))
    handler.send_header("Cache-Control","no-store")
    handler.end_headers()
    handler.wfile.write(body)

def _read_json(handler):
    length=int(handler.headers.get("Content-Length","0") or 0)
    if length<=0 or length>MAX_BODY:
        raise ValueError("invalid body")
    return json.loads(handler.rfile.read(length).decode("utf-8"))

def _job_id(analysis_key):
    return hashlib.sha256(str(analysis_key).encode("utf-8")).hexdigest()[:20]

def _object_exists(key):
    try:
        _s3().head_object(Bucket=S3_BUCKET,Key=key)
        return True
    except ClientError as exc:
        code=str((exc.response.get("Error") or {}).get("Code",""))
        if code in ("NoSuchKey","404","NotFound"):
            return False
        raise

def _run_job(job_id,key,analysis_key,engine_version,name,size):
    with SCAN_SEMAPHORE:
        started=time.perf_counter()
        local=None
        try:
            with JOBS_LOCK:
                JOBS[job_id]={"state":"downloading","started_at":time.time(),"analysis_key":analysis_key}
            if _object_exists(analysis_key):
                with JOBS_LOCK:
                    JOBS[job_id]={"state":"done","cached":True,"analysis_key":analysis_key}
                return

            suffix=Path(name or key).suffix.lower()
            if suffix not in (".mp4",".mov",".mkv"):
                suffix=".mp4"
            work=Path(tempfile.mkdtemp(prefix="gsf_worker_"))
            local=work/f"source{suffix}"

            dl_t0=time.perf_counter()
            cfg=TransferConfig(
                multipart_threshold=8*1024*1024,
                multipart_chunksize=16*1024*1024,
                max_concurrency=max(2,int(os.environ.get("GSF_WORKER_DOWNLOAD_CONCURRENCY","8"))),
                use_threads=True,
            )
            with open(local,"wb") as out:
                _s3().download_fileobj(S3_BUCKET,key,out,Config=cfg)
            download_seconds=time.perf_counter()-dl_t0
            if size and local.stat().st_size!=int(size):
                raise IOError("worker download size mismatch")

            with JOBS_LOCK:
                JOBS[job_id]={"state":"scanning","download_seconds":round(download_seconds,3),"analysis_key":analysis_key}

            scan=_load_scan_fn()(str(local))
            meta=dict(scan.get("meta",{}) or {})
            meta["worker_prescan"]=True
            meta["worker_service"]=True
            scan["meta"]=meta
            wall=time.perf_counter()-started
            payload={
                "engine_version":engine_version,
                "source_key":key,
                "analysis_key":analysis_key,
                "created_at":time.time(),
                "download_seconds":round(download_seconds,3),
                "worker_wall_seconds":round(wall,3),
                "scan":scan,
            }
            _s3().put_object(
                Bucket=S3_BUCKET,
                Key=analysis_key,
                Body=json.dumps(payload,separators=(",",":"),ensure_ascii=False).encode("utf-8"),
                ContentType="application/json",
            )
            with JOBS_LOCK:
                JOBS[job_id]={
                    "state":"done",
                    "analysis_key":analysis_key,
                    "download_seconds":round(download_seconds,3),
                    "wall_seconds":round(wall,3),
                }
            print(
                f"GSF worker done {analysis_key} download={download_seconds:.2f}s wall={wall:.2f}s",
                flush=True
            )
        except Exception as exc:
            with JOBS_LOCK:
                JOBS[job_id]={"state":"error","analysis_key":analysis_key,"error":str(exc)[:240]}
            print(f"GSF worker failed {analysis_key}: {str(exc)[:240]}",flush=True)
        finally:
            if local is not None:
                try:
                    work=local.parent
                    local.unlink(missing_ok=True)
                    work.rmdir()
                except Exception:
                    pass

class Handler(BaseHTTPRequestHandler):
    server_version="GSFAIWorker/1.0"

    def log_message(self,fmt,*args):
        return

    def do_GET(self):
        path=urlparse(self.path)
        if path.path.rstrip("/") in ("","/health"):
            _json(self,200,{"ok":True,"bucket":_bucket_enabled(),"app":AI_APP_PATH.name})
            return
        if path.path.rstrip("/")=="/status":
            analysis_key=(parse_qs(path.query).get("analysis_key") or [""])[0]
            job_id=_job_id(analysis_key)
            with JOBS_LOCK:
                state=dict(JOBS.get(job_id,{}) or {})
            if not state and _bucket_enabled() and analysis_key:
                try:
                    if _object_exists(analysis_key):
                        state={"state":"done","cached":True,"analysis_key":analysis_key}
                except Exception:
                    pass
            _json(self,200,{"ok":True,"job":state})
            return
        _json(self,404,{"ok":False,"error":"not found"})

    def do_POST(self):
        if self.path.rstrip("/")!="/prescan":
            _json(self,404,{"ok":False,"error":"not found"})
            return
        if not _authorized(self):
            _json(self,403,{"ok":False,"error":"forbidden"})
            return
        if not _bucket_enabled():
            _json(self,503,{"ok":False,"error":"bucket unavailable"})
            return
        try:
            data=_read_json(self)
            key=str(data.get("key") or "")
            analysis_key=str(data.get("analysis_key") or "")
            engine_version=str(data.get("engine_version") or "")
            name=str(data.get("name") or "")
            size=int(data.get("size",0) or 0)
            if not key.startswith("uploads/") or not analysis_key.startswith("analysis/"):
                raise ValueError("invalid keys")
            if engine_version!="v52-keyframe-turbo":
                raise ValueError("unsupported engine version")
            job_id=_job_id(analysis_key)
            if _object_exists(analysis_key):
                _json(self,200,{"ok":True,"cached":True,"job_id":job_id})
                return
            with JOBS_LOCK:
                existing=JOBS.get(job_id)
                if existing and existing.get("state") in ("downloading","scanning","queued"):
                    _json(self,202,{"ok":True,"queued":True,"job_id":job_id,"existing":True})
                    return
                JOBS[job_id]={"state":"queued","analysis_key":analysis_key}
            threading.Thread(
                target=_run_job,
                args=(job_id,key,analysis_key,engine_version,name,size),
                daemon=True,
            ).start()
            _json(self,202,{"ok":True,"queued":True,"job_id":job_id})
        except Exception as exc:
            _json(self,400,{"ok":False,"error":str(exc)[:240]})

if __name__=="__main__":
    _load_scan_fn()
    server=ThreadingHTTPServer(("0.0.0.0",PORT),Handler)
    print(
        f"GSF AI worker listening on 0.0.0.0:{PORT} "
        f"bucket={'on' if _bucket_enabled() else 'off'}",
        flush=True
    )
    server.serve_forever()
