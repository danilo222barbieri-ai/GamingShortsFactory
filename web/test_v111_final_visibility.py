from pathlib import Path
import sys

app=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V111_FINAL_VISIBLE.py")
server=Path(sys.argv[2] if len(sys.argv)>2 else "/app/web/direct_upload_server.py")
a=app.read_text(encoding="utf-8")
s=server.read_text(encoding="utf-8")

app_required=[
    "gsf_final_ready_sync_v111",
    "GSF_FINAL_BUCKET_PERSISTED",
    "http://127.0.0.1:8502/final/persist",
    'st.session_state["publication_final_bytes"]',
    'st.session_state["publication_ready"]=True',
]
server_required=[
    "const syncReadyResult=()=>",
    'if(lastRenderStatus!=="ready")',
    'path=="/final/persist"',
    "def _final_persist_to_bucket",
    "def _final_restore_from_bucket",
    'f"final-results/{sid}/latest.mp4"',
    "_final_restore_from_bucket(sid)",
    "GSF_FINAL_BUCKET_RESTORED",
]
missing=[x for x in app_required if x not in a]+[x for x in server_required if x not in s]
if missing:
    raise SystemExit("V111 final visibility contract failed: "+repr(missing))

compile(a,str(app),"exec")
compile(s,str(server),"exec")
print("V111 final visibility + persistence: PASS")
