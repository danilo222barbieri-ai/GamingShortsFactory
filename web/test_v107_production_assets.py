from pathlib import Path
import base64
import struct

root=Path("/app/web")
parts=[(root/"app_icons"/f"official_logo_180.b64.part{i}").read_text(encoding="ascii").strip() for i in range(1,5)]
raw=base64.b64decode("".join(parts))
if raw[:8]!=b"\x89PNG\r\n\x1a\n":
    raise SystemExit("FAIL production app icon is not PNG")
if struct.unpack(">II",raw[16:24])!=(180,180):
    raise SystemExit("FAIL production app icon is not 180x180")

server=(root/"direct_upload_server.py").read_text(encoding="utf-8")
nginx=(root/"nginx.conf.template").read_text(encoding="utf-8")
for marker in ["/account/google/start","/account/facebook/start","/account/tiktok/start","/manifest.webmanifest"]:
    if marker not in server:
        raise SystemExit(f"FAIL direct server missing {marker}")
for marker in ["location = /account {","@gsf_account_google_callback","@gsf_account_facebook_callback","@gsf_account_tiktok_callback","apple-touch-icon-180x180.png"]:
    if marker not in nginx:
        raise SystemExit(f"FAIL nginx missing {marker}")

print("V107 production assets/routes test: PASS")
