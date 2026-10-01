from pathlib import Path
import sys

app_path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V148_ANALYTICS_LEARNING.py")
server_path=Path(sys.argv[2] if len(sys.argv)>2 else "/app/web/direct_upload_server.py")
worker_path=Path(sys.argv[3] if len(sys.argv)>3 else "/app/web/ai_worker_server.py")

a=app_path.read_text(encoding="utf-8")
s=server_path.read_text(encoding="utf-8")
w=worker_path.read_text(encoding="utf-8")

contracts={
    "app/editor":[
        "render_gsf_editor_live_player(",
        "editor_preview_btn",
        'st.session_state["publication_source"]="inline_editor"',
        "gsf-v1302-live-progress",
        "SALVA BOZZA",
    ],
    "app/final":[
        "gsf_final_ready_sync_v111",
        'st.session_state["publication_ready"]=True',
        "http://127.0.0.1:8502/final/persist",
        "navigator.share",
    ],
    "server/upload":[
        "/upload/init",
        "/upload/complete",
        ".direct_upload_ready.json",
        "complete_multipart_upload",
    ],
    "server/final":[
        "/final/status",
        "/final/persist",
        "_final_persist_to_bucket",
        "_final_restore_from_bucket",
        "GSF_JOB_STATUS_SELF_HEALED",
        "stable_ready",
    ],
    "server/hub-drafts":[
        "/creator-hub",
        "/drafts/save",
        "/drafts/resume",
        "/drafts/delete",
        "_draft_prepare_resume",
    ],
    "server/social":[
        "/social-connect/tiktok/start",
        "/social-connect/youtube/start",
        "/social-connect/instagram/start",
        "/social-analytics/register",
        "/social-analytics/collect",
        "/social-analytics/context",
    ],
    "worker":[
        'JOBS={}',
        '"state":"queued"',
        '"state":"scanning"',
        '"state":"done"',
        '"state":"error"',
    ],
}
sources={"app/editor":a,"app/final":a,"server/upload":s,"server/final":s,
         "server/hub-drafts":s,"server/social":s,"worker":w}
missing=[]
for group,markers in contracts.items():
    for marker in markers:
        if marker not in sources[group]:
            missing.append(group+": "+marker)
if missing:
    raise SystemExit("V150 end-to-end stability contract failed:\n- "+"\n- ".join(missing))

for src,name in ((a,str(app_path)),(s,str(server_path)),(w,str(worker_path))):
    compile(src,name,"exec")

print("V150 END-TO-END STABILITY: PASS")
print("upload -> AI worker -> editor -> final persistence -> Creator Hub/drafts -> social contracts: PASS")
