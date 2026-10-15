#!/usr/bin/env python3
import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

def _env_first(*names,default=""):
    for name in names:
        value=os.environ.get(name)
        if value:
            return value
    return default

def _cfg():
    return {
        "bucket":_env_first("GSF_S3_BUCKET","S3_BUCKET","BUCKET"),
        "access":_env_first("GSF_S3_ACCESS_KEY_ID","AWS_ACCESS_KEY_ID","ACCESS_KEY_ID"),
        "secret":_env_first("GSF_S3_SECRET_ACCESS_KEY","AWS_SECRET_ACCESS_KEY","SECRET_ACCESS_KEY"),
        "endpoint":_env_first("GSF_S3_ENDPOINT","AWS_ENDPOINT_URL","ENDPOINT"),
        "region":_env_first("GSF_S3_REGION","AWS_REGION","AWS_DEFAULT_REGION","REGION",default="auto"),
        "style":_env_first("GSF_S3_ADDRESSING_STYLE",default="virtual"),
    }

def _client(c):
    return boto3.client(
        "s3",
        endpoint_url=c["endpoint"],
        aws_access_key_id=c["access"],
        aws_secret_access_key=c["secret"],
        region_name=c["region"],
        config=Config(signature_version="s3v4",s3={"addressing_style":c["style"]}),
    )

def _load_analysis_object(s3,c,analysis_key,engine_version):
    try:
        obj=s3.get_object(Bucket=c["bucket"],Key=analysis_key)
        payload=json.loads(obj["Body"].read().decode("utf-8"))
        if str(payload.get("engine_version",""))!=str(engine_version):
            return None
        scan=payload.get("scan")
        if isinstance(scan,dict):
            meta=dict(scan.get("meta",{}) or {})
            meta["worker_prescan"]=True
            meta["worker_wall_seconds"]=payload.get("worker_wall_seconds")
            meta["worker_download_seconds"]=payload.get("download_seconds")
            scan["meta"]=meta
            return scan
    except ClientError as exc:
        code=str((exc.response.get("Error") or {}).get("Code",""))
        if code not in ("NoSuchKey","404","NotFound"):
            return None
    except Exception:
        return None
    return None


def _worker_status_request(req,timeout=3.0):
    last_exc=None
    for attempt in range(3):
        try:
            return urllib.request.urlopen(req,timeout=timeout)
        except urllib.error.HTTPError as exc:
            last_exc=exc
            if int(getattr(exc,"code",0) or 0) not in (502,503,504) or attempt>=2:
                raise
        except (urllib.error.URLError,TimeoutError,ConnectionError,OSError) as exc:
            last_exc=exc
            if attempt>=2:
                raise
        time.sleep(0.45*(attempt+1))
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("worker status retry exhausted")

def _worker_status(analysis_key):
    worker_url=str(os.environ.get("GSF_WORKER_URL","") or "").rstrip("/")
    if not worker_url:
        return {"reachable":False,"state":"unavailable"}

    token=str(os.environ.get("GSF_WORKER_TOKEN","") or "")
    try:
        query=urllib.parse.urlencode({"analysis_key":str(analysis_key)})
        headers={}
        if token:
            headers["X-GSF-Worker-Token"]=token
        req=urllib.request.Request(
            worker_url+"/status?"+query,
            headers=headers,
            method="GET",
        )
        with _worker_status_request(req,timeout=3.0) as resp:
            payload=json.loads(resp.read().decode("utf-8"))
        job=(payload or {}).get("job") or {}
        state=str(job.get("state","") or "").lower()
        return {
            "reachable":True,
            "state":state or "unknown",
            "error":str(job.get("error","") or ""),
        }
    except Exception:
        return {"reachable":False,"state":"unavailable"}


def load_prescan_from_marker(preview_dir,engine_version,wait_seconds=None):
    marker=Path(preview_dir)/".direct_upload_ready.json"
    try:
        data=json.loads(marker.read_text(encoding="utf-8"))
    except Exception:
        return None

    analysis_key=str(data.get("analysis_key","") or "")
    if not analysis_key:
        return None

    c=_cfg()
    if not all((c["bucket"],c["access"],c["secret"],c["endpoint"])):
        return None

    if wait_seconds is None:
        try:
            wait_seconds=float(os.environ.get("GSF_PRESCAN_WAIT_SECONDS","35"))
        except Exception:
            wait_seconds=35.0

    s3=_client(c)

    # Cached results always win immediately.
    scan=_load_analysis_object(s3,c,analysis_key,engine_version)
    if isinstance(scan,dict):
        return scan

    deadline=time.monotonic()+max(0.0,float(wait_seconds))
    while time.monotonic()<deadline:
        status=_worker_status(analysis_key)
        if not status.get("reachable"):
            # No useful reason to burn the wait budget when the worker itself
            # cannot be reached; the caller can safely run the local fallback.
            return None

        state=str(status.get("state","") or "").lower()
        if state=="error":
            return None
        if state not in ("queued","downloading","scanning","done"):
            return None

        # The worker may report done a fraction before the object is observable
        # from the web service. Keep a short consistency grace within deadline.
        scan=_load_analysis_object(s3,c,analysis_key,engine_version)
        if isinstance(scan,dict):
            return scan

        time.sleep(0.5)

    return None
