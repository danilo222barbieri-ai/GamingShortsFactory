#!/usr/bin/env python3
import re
import sys
from pathlib import Path

IMPORT_LINE = (
    "from job_state_v401 import (ACTIVE_JOB_STATES, enrich_job_state, "
    "persist_job_state, load_job_state, recover_persisted_state)"
)
HELPER_MARKER = "GSF_V401_PERSISTENT_JOB_STATE"

HELPERS = r'''
# GSF_V401_PERSISTENT_JOB_STATE
def _set_job_state(job_id,payload):
    state=enrich_job_state(payload)
    with JOBS_LOCK:
        JOBS[job_id]=state
    if _bucket_enabled():
        try:
            persist_job_state(_s3(),S3_BUCKET,job_id,state)
        except Exception as exc:
            print(f"GSF V401 job-state persist warning {job_id}: {str(exc)[:160]}",flush=True)
    return state


def _get_job_state(job_id,analysis_key=""):
    with JOBS_LOCK:
        state=dict(JOBS.get(job_id,{}) or {})
    if state:
        return state

    if _bucket_enabled() and analysis_key:
        try:
            if _object_exists(analysis_key):
                state=enrich_job_state({"state":"done","cached":True,"analysis_key":analysis_key})
                with JOBS_LOCK:
                    JOBS[job_id]=state
                return state
        except Exception:
            pass

    if _bucket_enabled():
        try:
            persisted=load_job_state(_s3(),S3_BUCKET,job_id)
            if persisted:
                return recover_persisted_state(persisted)
        except ClientError as exc:
            code=str((exc.response.get("Error") or {}).get("Code",""))
            if code not in ("NoSuchKey","404","NotFound"):
                print(f"GSF V401 job-state load warning {job_id}: {code[:80]}",flush=True)
        except Exception as exc:
            print(f"GSF V401 job-state load warning {job_id}: {str(exc)[:160]}",flush=True)
    return {}
'''.strip()


def _replace_job_assignments(source):
    pattern=re.compile(
        r'(?ms)^(?P<indent>[ \t]*)with JOBS_LOCK:\n'
        r'(?P=indent)[ \t]+JOBS\[job_id\]=(?P<payload>\{.*?\})(?=\n)'
    )

    def repl(match):
        indent=match.group("indent")
        payload=match.group("payload")
        return f"{indent}_set_job_state(job_id,{payload})"

    return pattern.sub(repl,source)


def patch_worker_source(text):
    source=str(text)

    if IMPORT_LINE not in source:
        anchor="from auto_highlights.engine_v129 import analysis_to_candidates, candidate_dict\n"
        if anchor not in source:
            raise RuntimeError("V401 worker import anchor missing")
        source=source.replace(anchor,anchor+IMPORT_LINE+"\n",1)

    if HELPER_MARKER not in source:
        anchor="\n\ndef _run_job(job_id,key,analysis_key,engine_version,name,size):"
        if anchor not in source:
            raise RuntimeError("V401 worker helper anchor missing")
        source=source.replace(anchor,"\n\n"+HELPERS+anchor,1)

    old_queue='''            with JOBS_LOCK:\n                existing=JOBS.get(job_id)\n                if existing and existing.get("state") in ("downloading","scanning","queued"):\n                    _json(self,202,{"ok":True,"queued":True,"job_id":job_id,"existing":True})\n                    return\n                JOBS[job_id]={"state":"queued","analysis_key":analysis_key}\n'''
    new_queue='''            with JOBS_LOCK:\n                existing=JOBS.get(job_id)\n                if existing and existing.get("state") in ACTIVE_JOB_STATES:\n                    _json(self,202,{"ok":True,"queued":True,"job_id":job_id,"existing":True})\n                    return\n            _set_job_state(job_id,{"state":"queued","analysis_key":analysis_key})\n'''
    if old_queue in source:
        source=source.replace(old_queue,new_queue,1)

    source=_replace_job_assignments(source)

    old_status='''            with JOBS_LOCK:\n                state=dict(JOBS.get(job_id,{}) or {})\n            if not state and _bucket_enabled() and analysis_key:\n                try:\n                    if _object_exists(analysis_key):\n                        state={"state":"done","cached":True,"analysis_key":analysis_key}\n                except Exception:\n                    pass\n'''
    new_status='''            state=_get_job_state(job_id,analysis_key)\n'''
    if old_status in source:
        source=source.replace(old_status,new_status,1)

    source=source.replace(
        'existing.get("state") in ("downloading","scanning","queued")',
        'existing.get("state") in ACTIVE_JOB_STATES',
        1,
    )

    required=(IMPORT_LINE,HELPER_MARKER,'existing.get("state") in ACTIVE_JOB_STATES','state=_get_job_state(job_id,analysis_key)')
    missing=[item for item in required if item not in source]
    if missing:
        raise RuntimeError("V401 worker patch incomplete: "+", ".join(missing))
    if "JOBS[job_id]={" in source:
        raise RuntimeError("V401 worker patch left direct job-state assignment")

    compile(source,"ai_worker_server.py","exec")
    return source


def patch_worker_file(path):
    path=Path(path)
    text=path.read_text(encoding="utf-8")
    patched=patch_worker_source(text)
    if patched!=text:
        path.write_text(patched,encoding="utf-8")
        print("V401 worker persistent job-state patch applied",flush=True)
    else:
        print("V401 worker persistent job-state patch already active",flush=True)
    return patched!=text


if __name__=="__main__":
    target=Path(sys.argv[1]) if len(sys.argv)>1 else Path("/app/web/ai_worker_server.py")
    patch_worker_file(target)
