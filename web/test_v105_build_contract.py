from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else "/app")
web=(root/"requirements-web.txt").read_text(encoding="utf-8")
worker=(root/"requirements-worker.txt").read_text(encoding="utf-8")
constraints=root/"constraints-v105.txt"
start=(root/"web"/"start_web.sh").read_text(encoding="utf-8")
docker=(root/"Dockerfile.web").read_text(encoding="utf-8") if (root/"Dockerfile.web").is_file() else ""

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print("PASS:",msg)

need(constraints.is_file(),"V105 constraints file exists")
c=constraints.read_text(encoding="utf-8") if constraints.is_file() else ""
for name,version in [
    ("streamlit","1.49.1"),
    ("faster-whisper","1.2.1"),
    ("numpy","2.5.3"),
    ("boto3","1.43.104"),
    ("botocore","1.43.104"),
    ("google-api-python-client","2.200.0"),
    ("google-auth-oauthlib","1.4.1"),
    ("google-auth-httplib2","0.4.2"),
    ("ctranslate2","4.8.2"),
    ("av","18.1.0"),
]:
    need(f"{name}=={version}" in c or f"{name}=={version}" in web or f"{name}=={version}" in worker,
         f"{name} pinned to tested version")

need(">=" not in web,"web top-level requirements use exact pins")
need(">=" not in worker,"worker top-level requirements use exact pins")
need("-c /app/constraints-v105.txt" in docker,"web install applies V105 constraints")
need("print_v105_dependency_versions.py" not in docker,"dependency diagnostic removed from production build")
need("inspect_v105_social_current.py" not in docker,"social diagnostic removed from production build")
need("GamingShortsFactory_V105_ISOLATED.py" in start,"start script launches final isolated V105 candidate")
print("V105 build reproducibility contract: PASS")
