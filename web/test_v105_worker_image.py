#!/usr/bin/env python3
from pathlib import Path

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

docker_path=Path("/app/web/Dockerfile.worker")
req_path=Path("/app/web/requirements-worker.txt")
need(docker_path.is_file(),"dedicated worker Dockerfile exists")
need(req_path.is_file(),"dedicated worker requirements exist")

docker=docker_path.read_text(encoding="utf-8")
req=req_path.read_text(encoding="utf-8")

need("ffmpeg" in docker,"worker image installs FFmpeg")
need("boto3==" in req,"worker boto3 dependency is pinned")
need("apply_v99_final_arch.py" in docker,"worker generates V99 final scan source")
need("ai_worker_server.py" in docker,"worker starts AI worker server")
need("GamingShortsFactory_V99_FINAL_ARCH.py" in docker,"worker points at V99 scan app")
need("streamlit" not in docker.lower(),"worker image does not start/install Streamlit")
need("nginx" not in docker.lower(),"worker image does not install Nginx")
need("apply_v104" not in docker,"worker image excludes social patches")
need("apply_v105" not in docker,"worker image excludes web performance patches")
need("test_v104" not in docker,"worker image excludes web/social regression suite")

print("V105 worker image contract: PASS")
