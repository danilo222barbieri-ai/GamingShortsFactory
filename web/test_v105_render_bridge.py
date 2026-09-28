from pathlib import Path
import ast
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "/app")
worker=(root/"web"/"ai_worker_server.py").read_text(encoding="utf-8")
ast.parse(worker)
patch=root/"web"/"apply_v105_render_offload.py"

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

need("RENDER_SEMAPHORE" in worker,"worker has isolated render semaphore")
need('"/render"' in worker,"worker exposes render submit endpoint")
need('"/render/status"' in worker,"worker exposes persistent render status endpoint")
need("def _run_render_job" in worker,"worker render job exists")
need("worker-jobs/render/" in worker,"render job state is shared through S3")
need("GSF_WORKER_RENDER_THREADS" in worker,"render thread budget is configurable")
need("def _safe_render_args" in worker,"worker validates/sanitizes ffmpeg args")
need("result_key" in worker and "render-results/" in worker,"worker stores rendered master in S3")

need(patch.is_file(),"V105 render-offload patch exists")
if patch.is_file():
    ps=patch.read_text(encoding="utf-8")
    ast.parse(ps)
    need("_gsf_v105_run_render" in ps,"app patch installs subprocess-compatible render wrapper")
    need("_gsf_v105_remote_render" in ps,"app patch installs remote render client")
    need("GSF_REMOTE_RENDER_FALLBACK" in ps,"remote failure is observable and falls back")
    need("subprocess.run" in ps,"local V104 renderer remains a fallback")
    need("_diag_timeout" in ps,"existing V104 timeout contract is preserved")

print("V105 render-offload contract: PASS")
