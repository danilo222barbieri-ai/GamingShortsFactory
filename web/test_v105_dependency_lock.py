#!/usr/bin/env python3
from pathlib import Path

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

req=Path("/app/requirements-web.txt").read_text(encoding="utf-8")
constraints_path=Path("/app/constraints-web.txt")
docker=Path("/app/Dockerfile").read_text(encoding="utf-8")

expected_direct={
    "streamlit":"1.49.1",
    "faster-whisper":"1.2.1",
    "numpy":"2.5.3",
    "google-api-python-client":"2.200.0",
    "google-auth-oauthlib":"1.4.1",
    "google-auth-httplib2":"0.4.2",
    "boto3":"1.43.104",
}
for name,version in expected_direct.items():
    need(f"{name}=={version}" in req,f"{name} pinned to tested version")
    need(f"{name}>=" not in req,f"{name} open lower-bound removed")

need(constraints_path.is_file(),"full web constraints file exists")
constraints=constraints_path.read_text(encoding="utf-8")
for line in [
    "botocore==1.43.104",
    "ctranslate2==4.8.2",
    "onnxruntime==1.30.0",
    "pandas==2.3.3",
    "pyarrow==25.0.1",
    "requests==2.34.2",
    "tokenizers==0.23.2",
]:
    need(line in constraints,f"constraint locks {line}")

need(
    "pip install -r /app/requirements-web.txt -c /app/constraints-web.txt" in docker,
    "Docker build enforces tested constraints",
)
need(
    "COPY constraints-web.txt /app/constraints-web.txt" in docker,
    "Docker image copies constraints before install",
)

print("V105 dependency lock: PASS")
