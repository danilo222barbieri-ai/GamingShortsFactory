#!/usr/bin/env python3
import os
import direct_upload_server as server

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

need(
    server._upload_concurrency_for_user_agent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/154 Safari/537.36"
    )==8,
    "desktop upload concurrency capped at 8",
)
need(
    server._upload_concurrency_for_user_agent(
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) Mobile/15E148 Safari"
    )==3,
    "iPhone upload concurrency capped at 3",
)
need(
    server._upload_concurrency_for_user_agent(
        "Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) Mobile/15E148 Safari"
    )==3,
    "iPad upload concurrency capped at 3",
)
need(
    server._upload_concurrency_for_user_agent(
        "Mozilla/5.0 (Linux; Android 16; Pixel 10) Chrome/154 Mobile Safari"
    )==3,
    "Android upload concurrency capped at 3",
)
need(server.BUCKET_PART_BYTES==32*1024*1024,"bucket part size remains 32 MB")

old=os.environ.get("GSF_MATERIALIZE_CONCURRENCY")
try:
    os.environ["GSF_MATERIALIZE_CONCURRENCY"]="6"
    need(server._materialize_concurrency()==6,"materialization concurrency reads configured value")
    os.environ["GSF_MATERIALIZE_CONCURRENCY"]="99"
    need(server._materialize_concurrency()==8,"materialization concurrency upper-bounded at 8")
    os.environ["GSF_MATERIALIZE_CONCURRENCY"]="0"
    need(server._materialize_concurrency()==1,"materialization concurrency lower-bounded at 1")
finally:
    if old is None:
        os.environ.pop("GSF_MATERIALIZE_CONCURRENCY",None)
    else:
        os.environ["GSF_MATERIALIZE_CONCURRENCY"]=old

source=open("/app/web/direct_upload_server.py",encoding="utf-8").read()
need('"concurrency":_upload_concurrency_for_user_agent(' in source,
     "bucket init/capabilities expose device-aware concurrency")
need("max_concurrency=_materialize_concurrency()" in source,
     "S3 materialization uses bounded configurable concurrency")

print("V105 upload policy: PASS")
