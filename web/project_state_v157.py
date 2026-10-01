"""GSF V158 durable project state.

One active project survives Streamlit reruns/reconnects. If Creator Hub login is
available, the same project id/state is mirrored to persistent object storage
under the creator account so a project is not tied to a single browser process.
Large media bytes are never serialized here; only lightweight state/references.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import re
import time
import uuid

SKIP_PARTS=("secret","password","access_token","refresh_token","client_secret","oauth","credential","bytes")
MAX_VALUE=180_000
MAX_TOTAL=900_000
_ID_RE=re.compile(r"^[A-Za-z0-9_-]{1,80}$")

def _safe_id(value):
    value=str(value or "")
    return value if _ID_RE.match(value) else ""

def _safe(v):
    if v is None or isinstance(v,(str,int,float,bool)): return v
    if isinstance(v,Path): return str(v)
    if isinstance(v,(list,tuple)):
        if len(v)>5000: raise ValueError("large list")
        return [_safe(x) for x in v]
    if isinstance(v,dict):
        if len(v)>1000: raise ValueError("large dict")
        return {str(k):_safe(x) for k,x in v.items()}
    raise TypeError(type(v).__name__)

def _read_json(path):
    try:
        data=json.loads(Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data,dict) else {}
    except Exception:
        return {}

def _write_json(path,payload):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=Path(str(path)+".tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    os.replace(tmp,path)

def _account_id(session_root):
    return _safe_id(_read_json(Path(session_root)/"account.json").get("account_id",""))

def _runtime_root(session_root):
    p=Path(session_root)
    try:
        return p.parent.parent
    except Exception:
        return Path(os.environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime"))

def _project_root(session_root,account_id=""):
    account_id=_safe_id(account_id)
    if account_id:
        return _runtime_root(session_root)/"creator-projects"/account_id
    return Path(session_root)/"projects"

def _env_first(*names,default=""):
    for name in names:
        v=os.environ.get(name)
        if v: return v
    return default

def _bucket_cfg():
    return {
        "bucket":_env_first("GSF_S3_BUCKET","S3_BUCKET","BUCKET"),
        "access":_env_first("GSF_S3_ACCESS_KEY_ID","AWS_ACCESS_KEY_ID","ACCESS_KEY_ID"),
        "secret":_env_first("GSF_S3_SECRET_ACCESS_KEY","AWS_SECRET_ACCESS_KEY","SECRET_ACCESS_KEY"),
        "endpoint":_env_first("GSF_S3_ENDPOINT","AWS_ENDPOINT_URL","ENDPOINT"),
        "region":_env_first("GSF_S3_REGION","AWS_REGION","AWS_DEFAULT_REGION","REGION",default="auto"),
        "style":_env_first("GSF_S3_ADDRESSING_STYLE",default="virtual"),
    }

_S3=None
def _s3():
    global _S3
    cfg=_bucket_cfg()
    if not all((cfg["bucket"],cfg["access"],cfg["secret"],cfg["endpoint"])):
        return None
    if _S3 is None:
        try:
            import boto3
            from botocore.config import Config
            _S3=boto3.client(
                "s3",endpoint_url=cfg["endpoint"],
                aws_access_key_id=cfg["access"],aws_secret_access_key=cfg["secret"],
                region_name=cfg["region"],
                config=Config(signature_version="s3v4",s3={"addressing_style":cfg["style"]},retries={"max_attempts":3,"mode":"standard"}),
            )
        except Exception:
            _S3=False
    return _S3 if _S3 is not False else None

def _bucket_get(key):
    cli=_s3()
    if not cli or not key: return {}
    try:
        obj=cli.get_object(Bucket=_bucket_cfg()["bucket"],Key=key)
        data=json.loads(obj["Body"].read().decode("utf-8"))
        return data if isinstance(data,dict) else {}
    except Exception:
        return {}

def _bucket_put(key,payload):
    cli=_s3()
    if not cli or not key: return False
    try:
        cli.put_object(
            Bucket=_bucket_cfg()["bucket"],Key=key,
            Body=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf-8"),
            ContentType="application/json",CacheControl="no-store",
        )
        return True
    except Exception:
        return False

def _index_key(account_id):
    account_id=_safe_id(account_id)
    return f"creator-accounts/{account_id}/projects/index.json" if account_id else ""

def _state_key(account_id,project_id):
    account_id=_safe_id(account_id); project_id=_safe_id(project_id)
    return f"creator-accounts/{account_id}/projects/{project_id}/project_state.json" if account_id and project_id else ""

def _load_index(root,account_id):
    local=_read_json(Path(root)/"index.json")
    if local: return local
    if account_id:
        remote=_bucket_get(_index_key(account_id))
        if remote:
            try: _write_json(Path(root)/"index.json",remote)
            except Exception: pass
            return remote
    return {}

def ensure_project(session_state,session_root):
    account_id=_account_id(session_root)
    root=_project_root(session_root,account_id)
    root.mkdir(parents=True,exist_ok=True)

    pid=_safe_id(session_state.get("gsf_active_project_id",""))
    if not pid:
        idx=_load_index(root,account_id)
        pid=_safe_id(idx.get("active_project_id",""))
    if not pid:
        pid="p_"+uuid.uuid4().hex[:16]

    session_state["gsf_active_project_id"]=pid
    session_state["gsf_creator_account_id"]=account_id
    project=root/pid
    project.mkdir(parents=True,exist_ok=True)

    idx={"version":158,"active_project_id":pid,"updated_at":time.time()}
    try: _write_json(root/"index.json",idx)
    except Exception: pass
    # A new account/project identity is important enough to persist immediately.
    if account_id:
        _bucket_put(_index_key(account_id),idx)
    return project

def restore_project(session_state,session_root):
    project=ensure_project(session_state,session_root)
    marker=(str(project),session_state.get("gsf_active_project_id"))
    if session_state.get("_gsf_v158_project_restored")==marker:
        return project
    session_state["_gsf_v158_project_restored"]=marker

    account_id=_safe_id(session_state.get("gsf_creator_account_id",""))
    pid=_safe_id(session_state.get("gsf_active_project_id",""))
    p=project/"project_state.json"
    data=_read_json(p)
    if not data and account_id:
        data=_bucket_get(_state_key(account_id,pid))
        if data:
            try: _write_json(p,data)
            except Exception: pass

    state=data.get("state",{}) if isinstance(data,dict) else {}
    if isinstance(state,dict):
        for k,v in state.items():
            k=str(k)
            if k not in session_state and not any(x in k.lower() for x in SKIP_PARTS):
                session_state[k]=v
    return project

def save_project(session_state,session_root):
    project=ensure_project(session_state,session_root)
    payload={}; total=0
    for k,v in list(session_state.items()):
        k=str(k)
        if k.startswith("_") or any(x in k.lower() for x in SKIP_PARTS): continue
        try:
            sv=_safe(v); raw=json.dumps(sv,ensure_ascii=False,separators=(",",":"))
        except Exception:
            continue
        if len(raw)>MAX_VALUE or total+len(raw)>MAX_TOTAL: continue
        payload[k]=sv; total+=len(raw)

    account_id=_safe_id(session_state.get("gsf_creator_account_id","")) or _account_id(session_root)
    pid=_safe_id(session_state.get("gsf_active_project_id",""))
    doc={
        "version":158,"updated_at":time.time(),"project_id":pid,
        "account_id":account_id,"state":payload,
    }
    dst=project/"project_state.json"
    try: _write_json(dst,doc)
    except Exception: pass

    # Avoid an object-store write on every harmless Streamlit rerun.
    raw=json.dumps({"project_id":pid,"account_id":account_id,"state":payload},ensure_ascii=False,separators=(",",":"),sort_keys=True)
    digest=hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if account_id and digest!=session_state.get("_gsf_v158_bucket_digest"):
        if _bucket_put(_state_key(account_id,pid),doc):
            session_state["_gsf_v158_bucket_digest"]=digest
            idx={"version":158,"active_project_id":pid,"updated_at":doc["updated_at"]}
            try: _write_json(_project_root(session_root,account_id)/"index.json",idx)
            except Exception: pass
            _bucket_put(_index_key(account_id),idx)
    return project
