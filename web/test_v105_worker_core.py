from pathlib import Path
import ast
import sys

worker=Path(sys.argv[1] if len(sys.argv)>1 else "/app/web/ai_worker_server.py")
worker_s=worker.read_text(encoding="utf-8")
ast.parse(worker_s)

root=Path(sys.argv[2] if len(sys.argv)>2 else "/app")
worker_docker=root/"Dockerfile.worker"
worker_req=root/"requirements-worker.txt"
extractor=root/"web"/"extract_ai_scan_core.py"

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

need("import ast" not in worker_s,"worker does not AST-parse monolithic app at runtime")
need("AI_APP_PATH" not in worker_s,"worker no longer depends on generated V99 app path at runtime")
need("from generated_ai_scan_core import _gsf_ai_scan_base" in worker_s,
     "worker imports focused generated scan core")
need("def _save_job_state" in worker_s and "def _load_job_state" in worker_s,
     "worker persists and reloads job state")
need("worker-jobs/prescan/" in worker_s,"prescan shared-state key exists")
need("_save_job_state(job_id" in worker_s,"job transitions write shared state")
need("_load_job_state(job_id" in worker_s,"status endpoint can recover cross-replica state")

need(extractor.is_file(),"AI scan-core extractor exists")
if extractor.is_file():
    ex=extractor.read_text(encoding="utf-8")
    ast.parse(ex)
    need("ast.unparse" in ex,"extractor emits source module at build time")
    need("_gsf_ai_scan_base" in ex,"extractor targets scan engine")

need(worker_docker.is_file(),"worker-specific Dockerfile exists")
if worker_docker.is_file():
    d=worker_docker.read_text(encoding="utf-8")
    need("apply_v99_final_arch.py" in d,"worker build reaches V99 scan checkpoint")
    need("apply_v100_smart_reframe.py" not in d,"worker build does not replay post-V99 UI/render patches")
    need("extract_ai_scan_core.py" in d,"worker build generates focused core")
    need("CMD [\"python\",\"/app/web/ai_worker_server.py\"]" in d,
         "worker image starts worker directly")

need(worker_req.is_file(),"minimal worker requirements exist")
if worker_req.is_file():
    req=worker_req.read_text(encoding="utf-8").lower()
    need("streamlit" not in req,"worker does not install Streamlit")
    need("faster-whisper" not in req,"worker does not install Whisper")
    need("google-api-python-client" not in req,"worker does not install Google social SDK")
    need("boto3" in req,"worker keeps S3 dependency")

print("V105 worker-core contract: PASS")
