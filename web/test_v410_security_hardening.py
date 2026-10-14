#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
web = root / "web"
nginx = (web / "nginx.conf.template").read_text(encoding="utf-8")
server = (web / "direct_upload_server.py").read_text(encoding="utf-8")
start = (web / "start_web.sh").read_text(encoding="utf-8")
requirements = (root / "requirements-web.txt").read_text(encoding="utf-8")

# Runtime hardening must be applied on every container start and be idempotent.
assert "fix_v410_security_hardening.py" in start, "V410 hardening patch is not applied at runtime"
assert "test_v410_security_hardening.py" in start, "V410 security contract is not verified at runtime"

# Nginx edge protections.
for token in (
    "GSF_SECURITY_V410",
    "limit_req_zone",
    "limit_conn_zone",
    "X-Content-Type-Options",
    "Strict-Transport-Security",
    "Referrer-Policy",
    "Permissions-Policy",
    "Content-Security-Policy",
):
    assert token in nginx, f"missing nginx security control: {token}"
assert "location = /drafts/delete" in nginx
assert "limit_except POST" in nginx, "draft deletion must not be reachable with GET"
assert "location /direct-upload/" in nginx and "limit_req" in nginx, "upload endpoints need rate limiting"

# Application protections: same-session CSRF, active media validation, encrypted social tokens.
for token in (
    "GSF_SECURITY_V410",
    "_security_csrf_token",
    "_security_csrf_valid",
    "_security_validate_media",
    "_security_encrypt_json",
    "_security_decrypt_json",
):
    assert token in server, f"missing application security control: {token}"

# GET must be non-destructive; deletion moves to POST and validates a CSRF token.
get_delete = 'if clean=="/drafts/delete":\n            _json(self,405'
assert get_delete in server, "GET /drafts/delete still performs a destructive action"
assert 'if clean=="/drafts/delete":' in server[server.index("def do_POST"):], "POST delete handler missing"
assert "_security_csrf_valid(self,sid)" in server, "draft deletion does not validate CSRF"

# Cryptography is already pinned transitively; make it an explicit runtime dependency for token sealing.
assert "cryptography==50.0.1" in requirements, "cryptography must be an explicit dependency"

# Security CI must exist and scan dependencies + source.
workflow = root / ".github" / "workflows" / "v410-security-gate.yml"
assert workflow.is_file(), "V410 security CI workflow missing"
wf = workflow.read_text(encoding="utf-8")
for token in ("pip-audit", "bandit", "test_v410_security_hardening.py"):
    assert token in wf, f"security CI missing {token}"

print("V410 security hardening contract: PASS")
