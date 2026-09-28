from pathlib import Path
import ast,sys

direct=Path(sys.argv[1]).read_text(encoding="utf-8")
worker=Path(sys.argv[2]).read_text(encoding="utf-8")
app=Path(sys.argv[3]).read_text(encoding="utf-8")
ast.parse(direct); ast.parse(worker); ast.parse(app)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

need('STORAGE_PREFIX=str(os.environ.get("GSF_STORAGE_PREFIX"' in direct,"direct uploader reads storage prefix")
need("def _prefixed_key" in direct,"direct uploader has key prefix helper")
need('key=_prefixed_key(f"uploads/' in direct,"uploaded media key is namespaced")
need('analysis_key=_prefixed_key(f"analysis/' in direct,"analysis key is namespaced")
for fn in ("_tiktok_user_key","_youtube_user_key","_instagram_user_key"):
    node=next(n for n in ast.parse(direct).body if isinstance(n,ast.FunctionDef) and n.name==fn)
    src=ast.get_source_segment(direct,node) or ""
    need("_prefixed_key(" in src,f"{fn} is namespaced")

need("def _logical_key" in worker,"worker can strip namespace")
need('_logical_key(key).startswith("uploads/")' in worker,"worker accepts namespaced upload keys")
need('_logical_key(analysis_key).startswith("analysis/")' in worker,"worker accepts namespaced analysis keys")

need("def _gsf_v105_storage_key" in app,"app has shared storage-key helper")
for fn in (
    "_gsf_shared_tiktok_load","_gsf_shared_tiktok_save",
    "_gsf_shared_youtube_load","_gsf_shared_youtube_save",
    "_gsf_shared_instagram_load","_gsf_shared_instagram_save",
    "_gsf_v105_remote_render","_gsf_instagram_publish_reel_file",
):
    node=next(n for n in ast.parse(app).body if isinstance(n,ast.FunctionDef) and n.name==fn)
    src=ast.get_source_segment(app,node) or ""
    need("_gsf_v105_storage_key(" in src,f"{fn} uses environment storage namespace")

need("staging/v105" not in app and "prod/" not in app,"namespace value is configuration, not hardcoded")
print("V105 storage isolation: PASS")
