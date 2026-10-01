"""GSF V157 durable project-state helpers.

Keeps navigation cheap and makes project state recoverable without storing
large media blobs in Streamlit session state. Media paths remain references
to files already owned by the session/project.
"""
from __future__ import annotations
from pathlib import Path
import json, os, time, uuid

SKIP_PARTS=("secret","password","access_token","refresh_token","client_secret","oauth","credential","bytes")
MAX_VALUE=180_000
MAX_TOTAL=900_000

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

def ensure_project(session_state, session_root):
    root=Path(session_root)/"projects"
    root.mkdir(parents=True,exist_ok=True)
    pid=str(session_state.get("gsf_active_project_id","") or "")
    if not pid:
        pid="p_"+uuid.uuid4().hex[:16]
        session_state["gsf_active_project_id"]=pid
    project=root/pid
    project.mkdir(parents=True,exist_ok=True)
    return project

def restore_project(session_state, session_root):
    project=ensure_project(session_state,session_root)
    p=project/"project_state.json"
    if session_state.get("_gsf_v157_project_restored"): return project
    session_state["_gsf_v157_project_restored"]=True
    try: data=json.loads(p.read_text(encoding="utf-8"))
    except Exception: return project
    state=data.get("state",{}) if isinstance(data,dict) else {}
    if isinstance(state,dict):
        for k,v in state.items():
            if k not in session_state and not any(x in k.lower() for x in SKIP_PARTS):
                session_state[k]=v
    return project

def save_project(session_state, session_root):
    project=ensure_project(session_state,session_root)
    payload={}; total=0
    for k,v in list(session_state.items()):
        k=str(k)
        if k.startswith("_") or any(x in k.lower() for x in SKIP_PARTS): continue
        try:
            sv=_safe(v); raw=json.dumps(sv,ensure_ascii=False,separators=(",",":"))
        except Exception: continue
        if len(raw)>MAX_VALUE or total+len(raw)>MAX_TOTAL: continue
        payload[k]=sv; total+=len(raw)
    doc={"version":157,"updated_at":time.time(),"project_id":session_state.get("gsf_active_project_id"),"state":payload}
    dst=project/"project_state.json"; tmp=project/"project_state.json.tmp"
    try:
        tmp.write_text(json.dumps(doc,ensure_ascii=False),encoding="utf-8"); os.replace(tmp,dst)
    except Exception: pass
    return project
