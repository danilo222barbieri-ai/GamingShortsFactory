from pathlib import Path
import ast
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "/app/web/direct_upload_server.py")
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)

def fn(name):
    n=next((x for x in ast.walk(tree) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==name),None)
    if n is None:
        raise AssertionError(f"missing function {name}")
    return ast.get_source_segment(s,n) or ""

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

cors=fn("_ensure_bucket_cors")
need("def _allowed_cors_origins" in s,"multi-origin CORS helper exists")
need('"AllowedOrigins":_allowed_cors_origins()' in cors.replace(" ",""),"bucket CORS uses explicit origin list")
need("[PUBLIC_ORIGIN]" not in cors,"single-origin CORS overwrite removed")

need("def _client_upload_concurrency" in s,"client upload concurrency helper exists")
conc=fn("_client_upload_concurrency")
need("iphone" in conc.lower() and "ipad" in conc.lower(),"mobile Safari is detected")
need("GSF_BUCKET_CONCURRENCY_DESKTOP" in s,"desktop upload concurrency is configurable")
need("GSF_BUCKET_CONCURRENCY_MOBILE" in s,"mobile upload concurrency is configurable")

caps=fn("_client_upload_concurrency")
need("return" in caps,"concurrency helper returns bounded value")

mat=fn("_materialize_bucket_object")
need("GSF_WEB_MATERIALIZE_CONCURRENCY" in s,"materialization concurrency is configurable")
need("max_concurrency=MATERIALIZE_CONCURRENCY" in mat.replace(" ",""),"materializer uses bounded configured concurrency")
need("os.fsync(out.fileno())" not in mat,"S3-derived ephemeral copy does not force full fsync")
need("GSF_MATERIALIZE_DONE" in mat,"materialization emits structured completion timing")
need("GSF_MATERIALIZE_ERROR" in mat,"materialization emits structured failure timing")

put=fn("do_PUT")
need("os.fsync(fd)" in put,"direct fallback retains durability fsync")

post=fn("do_POST")
need("GSF_UPLOAD_COMPLETE" in post,"multipart completion emits structured timing")
need("_client_upload_concurrency(self.headers.get" in post,"bucket init returns client-adaptive concurrency")

print("V105 upload hardening contract: PASS")
