#!/usr/bin/env python3
import json
import os
import time
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
            wait_seconds=float(os.environ.get("GSF_PRESCAN_WAIT_SECONDS","8"))
        except Exception:
            wait_seconds=8.0
    deadline=time.monotonic()+max(0.0,float(wait_seconds))
    s3=_client(c)
    while True:
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
            return None
        except ClientError as exc:
            code=str((exc.response.get("Error") or {}).get("Code",""))
            if code not in ("NoSuchKey","404","NotFound"):
                return None
        except Exception:
            return None
        if time.monotonic()>=deadline:
            return None
        time.sleep(0.5)
