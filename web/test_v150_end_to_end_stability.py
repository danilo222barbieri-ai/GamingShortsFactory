from pathlib import Path
import sys

app_path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V148_ANALYTICS_LEARNING.py")
server_path=Path(sys.argv[2] if len(sys.argv)>2 else "/app/web/direct_upload_server.py")
worker_path=Path(sys.argv[3] if len(sys.argv)>3 else "/app/web/ai_worker_server.py")
pipeline_path=Path("/app/web/director_pipeline_v142.py")
render_path=Path("/app/web/director_render_exec_v143.py")

a=app_path.read_text(encoding="utf-8")
s=server_path.read_text(encoding="utf-8")
w=worker_path.read_text(encoding="utf-8")
p=pipeline_path.read_text(encoding="utf-8")
r=render_path.read_text(encoding="utf-8")

contracts={
 "app/editor-render":[
   "render_gsf_editor_live_player(",
   "_gsf_v142_enrich_recipe",
   "performance_context=_gsf_v148_performance_context()",
   "ai_render_operations",
   "director_render_exec_v143",
   "gsf-v1302-live-progress",
   "SALVA BOZZA",
 ],
 "app/final-persistence":[
   "gsf_final_ready_sync_v111",
   'st.session_state["publication_ready"]=True',
   "http://127.0.0.1:8502/final/persist",
   "navigator.share",
 ],
 "server/upload-persistence":[
   ".direct_upload_ready.json",
   "complete_multipart_upload",
   "_materialize_bucket_object",
   "_persist_fallback_source_to_bucket",
 ],
 "server/final-recovery":[
   "_final_persist_to_bucket",
   "_final_restore_from_bucket",
   "GSF_JOB_STATUS_SELF_HEALED",
   "stable_ready",
   "final-results/{sid}/latest.mp4",
 ],
 "server/hub-drafts":[
   "_draft_save",
   "_draft_prepare_resume",
   "_draft_delete",
   "/drafts/save",
   "/drafts/resume",
   "/drafts/delete",
   "_draft_cards_html",
 ],
 "server/social-learning":[
   "/social-analytics/register",
   "/social-analytics/collect",
   "/social-analytics/context",
   "_analytics_collect_all",
   "_analytics_context",
   "_start_social_analytics_worker",
 ],
 "worker-ai":[
   "from ai_director_v124 import cloud_decision",
   "router=cloud_decision(",
   '"state":"queued"',
   '"state":"scanning"',
   '"state":"done"',
   '"state":"error"',
 ],
 "director-connected":[
   "from creator_learning_v138 import choose_ab, learn, load_profile, save_profile",
   "from director_orchestrator_v136 import build_director_evidence",
   "from long_form_director_v141 import build_long_form, compile_long_form_operations",
   "from render_director_v139 import compile_render_plan",
   'performance_context=None',
   'visual_scoring_v144',
   'content_memory_v145',
   'out["ai_render_operations"]',
   'source":"performance_learning"',
   'completion<.55',
   'share>=.04',
 ],
 "render-execution":[
   "def execute_director_operations",
   "ffmpeg",
 ],
}
sources={
 "app/editor-render":a,"app/final-persistence":a,
 "server/upload-persistence":s,"server/final-recovery":s,"server/hub-drafts":s,
 "server/social-learning":s,"worker-ai":w,"director-connected":p,"render-execution":r,
}
missing=[]
for group,markers in contracts.items():
 for marker in markers:
  if marker not in sources[group]:
   missing.append(group+": "+marker)
if missing:
 raise SystemExit("V150 connected-system contract failed:\n- "+"\n- ".join(missing))

for src,name in ((a,str(app_path)),(s,str(server_path)),(w,str(worker_path)),(p,str(pipeline_path)),(r,str(render_path))):
 compile(src,name,"exec")

print("V150 CONNECTED SYSTEM: PASS")
print("upload persistence -> AI worker -> Director -> learned performance -> editor/render -> final recovery -> Hub/drafts -> social learning: PASS")
