#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
web = root / "web"
nginx = (web / "nginx.conf.template").read_text(encoding="utf-8")
server = (web / "direct_upload_server.py").read_text(encoding="utf-8")
secure_start = (web / "start_secure.sh").read_text(encoding="utf-8")
requirements = (root / "requirements-web.txt").read_text(encoding="utf-8")

# Security now lives directly in the canonical nginx/server files (canonical UI
# pipeline). The image must copy them as-is: re-running the V410 patches at build
# time would make the served files differ from the repository.
dockerfile = root / 'Dockerfile'
if dockerfile.is_file():
    docker = dockerfile.read_text(encoding='utf-8')
    assert 'fix_v410_security_hardening.py' not in docker
    assert 'fix_v410_1_edge_identity.py' not in docker
    assert 'python /app/web/test_v410_security_hardening.py /app' in docker
    assert 'CMD ["/app/web/start_web.sh"]' in docker

# Nginx edge protections.
security_headers = (
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Strict-Transport-Security",
    "Content-Security-Policy",
)
for token in (
    "GSF_SECURITY_V410",
    "GSF_SECURITY_V410_EDGE_ID",
    "limit_req_zone",
    "limit_conn_zone",
    "$gsf_client_key",
    "$http_x_real_ip",
    *security_headers,
):
    assert token in nginx, f"missing nginx security control: {token}"
assert "location = /drafts/delete" in nginx
assert "limit_except POST" in nginx, "draft deletion must not be reachable with GET"
assert "location /direct-upload/" in nginx and "zone=gsf_upload_v410" in nginx, "upload endpoints need rate limiting"
assert "zone=gsf_upload_v410:10m rate=20r/s" in nginx, "upload abuse guard must not throttle normal parallel upload"
assert "burst=80 nodelay" in nginx, "parallel upload burst allowance missing"
assert 'payment=(self)' in nginx, "same-origin payment capability must remain available"

# Nginx does not inherit server-level add_header directives into a location that
# declares any add_header of its own. Every such location must therefore carry
# the full browser-hardening set locally as well.
location_blocks = re.findall(r"(?ms)^    location[^\n]*\{\n.*?^    \}\n", nginx)
assert location_blocks, "nginx location parsing found no blocks"
for block in location_blocks:
    if "add_header " not in block:
        continue
    first_line = block.splitlines()[0].strip()
    for header in security_headers:
        assert f"add_header {header} " in block, f"{first_line} shadows security header {header}"

# Application protections: same-session CSRF, active media validation, encrypted social tokens.
for token in (
    "GSF_SECURITY_V410",
    "_security_csrf_token",
    "_security_csrf_valid",
    "_security_validate_media",
    "_security_encrypt_json",
    "_security_decrypt_json",
    "_security_write_json",
    "Fernet",
):
    assert token in server, f"missing application security control: {token}"
assert "_security_validate_media(tmp,ext)" in server, "bucket materialization is not validated"
assert "_security_validate_media(data_path,ext)" in server, "fallback upload is not validated"
assert "_security_encrypt_json(payload)" in server, "social token bucket writes are not sealed"

# GET must be non-destructive; deletion moves to POST and validates a CSRF token.
get_delete = 'if clean=="/drafts/delete":\n            _json(self,405'
assert get_delete in server, "GET /drafts/delete still performs a destructive action"
post = server[server.index("def do_POST"):]
assert 'if path=="/drafts/delete":' in post, "POST delete handler missing"
assert "_security_csrf_valid(self,sid)" in post, "draft deletion does not validate CSRF"
assert "gsfDeleteDraft" in server and 'method:"POST"' in server, "draft UI does not use protected POST deletion"

# Cryptography is already pinned transitively; make it an explicit runtime dependency for token sealing.
assert "cryptography==50.0.1" in requirements, "cryptography must be an explicit dependency"

# In a repository checkout, CI must continuously scan dependencies + source.
workflow = root / ".github" / "workflows" / "gsf-ci.yml"  # V410 checks run in the single GSF CI job
if (root / ".github").exists():
    assert workflow.is_file(), "V410 security CI workflow missing"
    wf = workflow.read_text(encoding="utf-8")
    for token in ("pip-audit", "bandit", "test_v410_security_hardening.py", "fix_v410_1_edge_identity.py"):
        assert token in wf, f"security CI missing {token}"

print("V410 security hardening contract: PASS")
