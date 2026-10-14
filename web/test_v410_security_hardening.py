#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
web = root / "web"
nginx = (web / "nginx.conf.template").read_text(encoding="utf-8")
server = (web / "direct_upload_server.py").read_text(encoding="utf-8")
secure_start = (web / "start_secure.sh").read_text(encoding="utf-8")
requirements = (root / "requirements-web.txt").read_text(encoding="utf-8")

# Runtime hardening must be applied and re-verified before the normal app boot.
assert "fix_v410_security_hardening.py" in secure_start, "V410 hardening patch is not applied at runtime"
assert "test_v410_security_hardening.py" in secure_start, "V410 security contract is not verified at runtime"
assert "start_web.sh" in secure_start, "secure entrypoint must hand off to the normal GSF boot"

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
assert "location /direct-upload/" in nginx and "zone=gsf_upload_v410" in nginx, "upload endpoints need rate limiting"

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
workflow = root / ".github" / "workflows" / "v410-security-gate.yml"
if (root / ".github").exists():
    assert workflow.is_file(), "V410 security CI workflow missing"
    wf = workflow.read_text(encoding="utf-8")
    for token in ("pip-audit", "bandit", "test_v410_security_hardening.py"):
        assert token in wf, f"security CI missing {token}"

print("V410 security hardening contract: PASS")
