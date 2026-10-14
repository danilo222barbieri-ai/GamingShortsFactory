#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARKER = "GSF_SECURITY_V410_EDGE_ID"

SECURITY_HEADERS = (
    'add_header X-Content-Type-Options "nosniff" always;',
    'add_header X-Frame-Options "SAMEORIGIN" always;',
    'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
    'add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(self)" always;',
    'add_header Strict-Transport-Security "max-age=15552000" always;',
    'add_header Content-Security-Policy "default-src \'self\' data: blob: https:; script-src \'self\' \'unsafe-inline\' \'unsafe-eval\' https:; style-src \'self\' \'unsafe-inline\' https:; img-src \'self\' data: blob: https:; media-src \'self\' blob: https:; connect-src \'self\' https: wss:; frame-src \'self\' https:; object-src \'none\'; base-uri \'self\'; form-action \'self\' https:; frame-ancestors \'self\';" always;',
)


def _propagate_location_security_headers(text: str) -> str:
    """Preserve hardening where a local add_header shadows server inheritance."""
    pattern = re.compile(r"(?ms)^    location[^\n]*\{\n.*?^    \}\n")

    def patch_block(match):
        block = match.group(0)
        if "add_header " not in block:
            return block
        missing = []
        for directive in SECURITY_HEADERS:
            header = directive.split()[1]
            if f"add_header {header} " not in block:
                missing.append("        " + directive)
        if not missing:
            return block
        closing = "    }\n"
        body = block[:-len(closing)].rstrip("\n")
        return body + "\n\n" + "\n".join(missing) + "\n" + closing

    return pattern.sub(patch_block, text)


def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    if "GSF_SECURITY_V410" not in text:
        raise RuntimeError("V410 base hardening must be applied first")

    old = """# GSF_SECURITY_V410 — edge hardening, abuse control and browser policy
limit_req_zone $binary_remote_addr zone=gsf_api_v410:10m rate=20r/s;
limit_req_zone $binary_remote_addr zone=gsf_upload_v410:10m rate=5r/s;
limit_conn_zone $binary_remote_addr zone=gsf_conn_v410:10m;
"""
    new = """# GSF_SECURITY_V410 — edge hardening, abuse control and browser policy
# GSF_SECURITY_V410_EDGE_ID — Railway publishes the remote client as X-Real-IP.
map $http_x_real_ip $gsf_client_key {
    "~^[0-9A-Fa-f:.]{2,45}$" $http_x_real_ip;
    default $binary_remote_addr;
}
limit_req_zone $gsf_client_key zone=gsf_api_v410:10m rate=20r/s;
limit_req_zone $gsf_client_key zone=gsf_upload_v410:10m rate=20r/s;
limit_conn_zone $gsf_client_key zone=gsf_conn_v410:10m;
"""
    if old not in text:
        raise RuntimeError("V410.1 edge-zone anchor missing")
    text = text.replace(old, new, 1)

    # Keep browser APIs locked down without precluding a same-origin payment flow.
    text = text.replace(
        'add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;',
        'add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(self)" always;',
        1,
    )

    # Eight-lane uploads should never be throttled by the abuse guard.
    text = text.replace(
        "limit_req zone=gsf_upload_v410 burst=24 nodelay;",
        "limit_req zone=gsf_upload_v410 burst=80 nodelay;",
        1,
    )

    # A location-level add_header disables inheritance from the server block.
    # Copy the complete hardening set into every such route so cache/cookie
    # headers cannot silently remove browser security headers at runtime.
    text = _propagate_location_security_headers(text)

    path.write_text(text, encoding="utf-8")
    return True


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "/app").resolve()
    path = root / "web" / "nginx.conf.template"
    if not path.is_file():
        raise SystemExit(f"V410.1 invalid app root: {root}")
    changed = patch(path)
    print(f"V410.1 proxy-aware edge hardening applied={int(changed)}")


if __name__ == "__main__":
    main()
