#!/usr/bin/env python3
from pathlib import Path

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

req=Path("/app/requirements-web.txt").read_text(encoding="utf-8")
constraints_path=Path("/app/constraints-web.txt")

streamlit_wheel=(
    "streamlit @ https://core-previews.s3-us-west-2.amazonaws.com/pr-17589/"
    "streamlit-1.66.0-py3-none-any.whl"
    "#sha256=841f0d2ac3b59d7501a95a2771ee31b8cb3bf0f210258135089e75ab9157a7fa"
)
need(streamlit_wheel in req,"Streamlit Pillow 13 preview wheel pinned to official URL and SHA256")
need("streamlit==" not in req,"legacy Streamlit PyPI pin removed")

expected_direct={
    "faster-whisper":"1.2.1",
    "numpy":"2.5.3",
    "google-api-python-client":"2.200.0",
    "google-auth-oauthlib":"1.4.1",
    "google-auth-httplib2":"0.4.2",
    "boto3":"1.43.104",
    "cryptography":"50.0.1",
}
for name,version in expected_direct.items():
    need(f"{name}=={version}" in req,f"{name} pinned to tested version")
    need(f"{name}>=" not in req,f"{name} open lower-bound removed")

need(constraints_path.is_file(),"full web constraints file exists")
constraints=constraints_path.read_text(encoding="utf-8")
for line in [
    "botocore==1.43.104",
    "cryptography==50.0.1",
    "ctranslate2==4.8.2",
    "onnxruntime==1.30.0",
    "pandas==2.3.3",
    "pillow==13.0.0",
    "pyarrow==25.0.1",
    "requests==2.34.2",
    "streamlit==1.66.0",
    "tokenizers==0.23.2",
]:
    need(line in constraints,f"constraint locks {line}")

print("V105 dependency lock: PASS")
