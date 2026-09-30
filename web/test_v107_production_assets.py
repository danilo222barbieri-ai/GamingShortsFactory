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
if len(raw)<4000:
    raise SystemExit("FAIL production app icon payload unexpectedly small")

server=(root/"direct_upload_server.py").read_text(encoding="utf-8")
nginx=(root/"nginx.conf.template").read_text(encoding="utf-8")
for marker in ["/account/google/start","/account/facebook/start","/account/tiktok/start","/manifest.webmanifest","/editor-media/current","GSF_EDITOR_MEDIA_REDIRECT","/gsf-sw.js","/gsf-push.js","/push/public-key","/push/subscribe","/push/notify","GSF_PUSH_SENT","/drafts/save","/drafts/resume","/drafts/delete","_draft_cards_html","_draft_prepare_resume"]:
    if marker not in server:
        raise SystemExit(f"FAIL direct server missing {marker}")
for marker in ["location = /account {","location = /editor-media/current {","location = /gsf-sw.js {","location = /push/subscribe {","location = /drafts/resume {","location = /drafts/delete {","/gsf-push.js?v=3","@gsf_account_google_callback","@gsf_account_facebook_callback","@gsf_account_tiktok_callback","apple-touch-icon-180x180.png","location = /app-icon-192.png","location = /app-icon-512.png","mobile-web-app-capable","apple-mobile-web-app-title"]:
    if marker not in nginx:
        raise SystemExit(f"FAIL nginx missing {marker}")
for marker in ['"sizes":"192x192"','"sizes":"512x512"','"/app-icon-192.png?v=4"','"/app-icon-512.png?v=4"']:
    if marker not in server:
        raise SystemExit(f"FAIL manifest contract missing {marker}")

print("V107 production assets/routes test: PASS")

for marker in ["/job/status","/source/restore","GSF_SOURCE_RESTORED","json=1","gsfResumeDraft","visibilitychange","pageshow","CONDIVIDI O SCARICA","gsf-site-toast-stack","Upload completato","Short completato","_draft_index_key","_draft_index_save","GSF_DRAFT_RESUME_BLOCKED_SOURCE","GSF_FALLBACK_SOURCE_PERSISTED"]:
    if marker not in server:
        raise SystemExit("FAIL lifecycle/source restore asset missing: "+marker)
if "gsf-activity-hud" in server:
    raise SystemExit("FAIL obsolete bottom-right activity HUD survived")
if "location = /job/status {" not in nginx:
    raise SystemExit("FAIL nginx job status route missing")

if "target=\"_top\"" in server and "/drafts/resume" in server:
    raise SystemExit("FAIL draft resume still relies on destructive top-level navigation")
if '"failed_at":payload.get("failed_at")' not in server:
    raise SystemExit("FAIL job status does not expose render failure timestamp")
if "max_concurrency=max(1,min(4,_materialize_concurrency()))" not in server:
    raise SystemExit("FAIL fallback source persistence is not concurrency-bounded")

if "gsf-share-auto-open-token" in server:
    raise SystemExit("FAIL completion still auto-opens Share Hub")
if "onClick:()=>openShareHub()" not in server:
    raise SystemExit("FAIL Short completion toast is not optionally actionable")

for marker in ("GSF_JOB_STATUS_SELF_HEALED","download_ready","stable_ready"):
    if marker not in server:
        raise SystemExit("FAIL final Short job self-heal missing: "+marker)
