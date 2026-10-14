#!/usr/bin/env python3
from pathlib import Path
import sys

MARKER = "GSF_EDGE_IDENTITY_V410"


def patch_nginx(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    if "GSF_SECURITY_V410" not in text:
        raise RuntimeError("V410 base security patch must run before edge identity patch")

    anchor = "# GSF_SECURITY_V410 — edge hardening, abuse control and browser policy\n"
    identity = '''# GSF_EDGE_IDENTITY_V410 — Railway documents X-Real-IP as the original client IP.
# Accept only IP-shaped values and fall back to the socket peer if the header is absent/malformed.
map $http_x_real_ip $gsf_client_identity_v410 {
    ~^[0-9A-Fa-f:.]{2,45}$ $http_x_real_ip;
    default $remote_addr;
}

'''
    if anchor not in text:
        raise RuntimeError("V410 edge hardening anchor missing")
    text = text.replace(anchor, identity + anchor, 1)

    old_req = "limit_req_zone $binary_remote_addr zone=gsf_api_v410:10m rate=20r/s;"
    old_upload = "limit_req_zone $binary_remote_addr zone=gsf_upload_v410:10m rate=5r/s;"
    old_conn = "limit_conn_zone $binary_remote_addr zone=gsf_conn_v410:10m;"
    replacements = (
        (old_req, "limit_req_zone $gsf_client_identity_v410 zone=gsf_api_v410:10m rate=20r/s;"),
        (old_upload, "limit_req_zone $gsf_client_identity_v410 zone=gsf_upload_v410:10m rate=5r/s;"),
        (old_conn, "limit_conn_zone $gsf_client_identity_v410 zone=gsf_conn_v410:10m;"),
    )
    for old, new in replacements:
        if old not in text:
            raise RuntimeError(f"V410 edge identity anchor missing: {old}")
        text = text.replace(old, new, 1)

    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    nginx = root / "web" / "nginx.conf.template"
    changed = patch_nginx(nginx)
    print(f"V410 Railway edge identity applied nginx={int(changed)}")


if __name__ == "__main__":
    main()
