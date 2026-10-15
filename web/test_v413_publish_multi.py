#!/usr/bin/env python3
"""V413 Crea Short multi-publish contract (offline: no network, no secrets)."""
from __future__ import annotations

import io
import json
import re
import sys
import tempfile
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
import publish_multi_v413 as pm  # noqa: E402


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


# ---------------------------------------------------------------- payload
try:
    pm.normalize_request({"platforms": []})
    raise AssertionError("empty platform list must be rejected")
except ValueError as exc:
    check("almeno un social" in str(exc), exc)

try:
    pm.normalize_request({"platforms": ["youtube"], "shared": {"title": "  "}})
    raise AssertionError("YouTube without a title must be rejected")
except ValueError:
    pass

req = pm.normalize_request({
    "platforms": ["tiktok", "youtube", "youtube", "myspace", "instagram"],
    "privacy": "weird",
    "shared": {"title": "Clutch 1v4", "description": "Ultimo secondo", "hashtags": "#gaming, shorts #Gaming fyp"},
    "overrides": {"tiktok": {"description": "Versione TikTok", "hashtags": "#fyp #perte"}},
})
check(req["platforms"] == ["tiktok", "youtube", "instagram"], req["platforms"])
check(req["privacy"] == "public", "unknown privacy falls back to public")
yt, tt, ig = req["plans"]["youtube"], req["plans"]["tiktok"], req["plans"]["instagram"]
check(yt["tags"] == ["gaming", "shorts", "fyp"], yt["tags"])  # dedup, case-insensitive, Shorts already there
check(yt["title"] == "Clutch 1v4", yt)
check(tt["title"] == "" and tt["tags"] == ["fyp", "perte"], tt)
check(tt["caption"] == "Versione TikTok\n\n#fyp #perte", tt["caption"])
check(ig["caption"].startswith("Ultimo secondo"), ig)
req2 = pm.normalize_request({"platforms": ["youtube"], "shared": {"title": "x" * 300, "hashtags": "a b"}})
check(len(req2["plans"]["youtube"]["title"]) == 100, "YouTube title limit")
check(req2["plans"]["youtube"]["tags"][-1] == "Shorts", "YouTube always gets #Shorts")
long = pm.build_caption("d" * 2190, ["aaaa", "bbbb", "cccc"], 2200)
check(len(long) <= 2200 and "#aaaa" in long and "#cccc" not in long, "caption drops whole hashtags before cutting")
check(pm.parse_hashtags(["#a", "a", "b-c"]) == ["a", "b", "c"], pm.parse_hashtags(["#a", "a", "b-c"]))

# ---------------------------------------------------------------- signed links
secret = b"test-secret"
token, exp = pm.sign_share_link(secret, "sid_ABC-1", ttl=600, now=1000)
check(exp == 1600, exp)
check(pm.verify_share_link(secret, token, now=1500) == "sid_ABC-1", "valid link")
check(pm.verify_share_link(secret, token, now=1601) == "", "expired link")
check(pm.verify_share_link(b"other", token, now=1500) == "", "wrong secret")
body, sig = token.split(".")
check(pm.verify_share_link(secret, body + "." + sig[:-1] + ("A" if sig[-1] != "A" else "B"), now=1500) == "", "tampered link")
check(pm.verify_share_link(secret, "garbage", now=1500) == "", "garbage link")
check(re.fullmatch(r"[A-Za-z0-9_.-]+", token), "token is URL safe")


# ---------------------------------------------------------------- fake HTTP
class Resp(io.BytesIO):
    def __init__(self, data=b"{}", status=200, headers=None):
        super().__init__(data)
        self.status = status
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class Opener:
    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def __call__(self, req, timeout=0):
        data = req.data
        if hasattr(data, "read"):
            data = data.read()
        self.calls.append((req.get_method(), req.full_url, dict(req.header_items()), data))
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


tmp = Path(tempfile.mkdtemp()) / "short.mp4"
tmp.write_bytes(b"\0" * 4096)
plan = pm.normalize_request({"platforms": ["youtube", "tiktok"], "shared": {"title": "T", "hashtags": "#g"}})["plans"]

# YouTube: session -> one PUT
op = Opener([Resp(headers={"Location": "https://upload.example/session"}), Resp(json.dumps({"id": "abc123"}).encode())])
out = pm.youtube_upload("tok", str(tmp), plan["youtube"], "unlisted", opener=op)
check(out == {"ok": True, "id": "abc123", "url": "https://youtube.com/shorts/abc123", "privacy": "unlisted"}, out)
meta = json.loads(op.calls[0][3])
check(meta["snippet"]["categoryId"] == "20" and meta["status"]["privacyStatus"] == "unlisted", meta)
check(op.calls[0][2].get("X-upload-content-length") == "4096", op.calls[0][2])
check(op.calls[1][0] == "PUT" and op.calls[1][3] == b"\0" * 4096, "file uploaded in one PUT")

# YouTube quota error surfaces an Italian message
quota = urllib.error.HTTPError("u", 403, "x", {}, io.BytesIO(json.dumps({"error": {"errors": [{"reason": "quotaExceeded"}]}}).encode()))
try:
    pm.youtube_upload("tok", str(tmp), plan["youtube"], opener=Opener([quota]))
    raise AssertionError("quota must fail")
except pm.PublishError as exc:
    check("Limite giornaliero" in str(exc), exc)

try:
    pm.youtube_upload("", str(tmp), plan["youtube"])
    raise AssertionError("missing token must fail")
except pm.PublishError:
    pass

# TikTok: creator info -> unaudited public refused -> retry SELF_ONLY -> PUT
creator = {"data": {"privacy_level_options": ["PUBLIC_TO_EVERYONE", "SELF_ONLY"]}, "error": {"code": "ok"}}
refused = {"error": {"code": "unaudited_client_can_only_post_to_private_accounts", "message": "no"}}
accepted = {"data": {"upload_url": "https://up.tiktok/x", "publish_id": "p_1"}, "error": {"code": "ok"}}
op = Opener([Resp(json.dumps(creator).encode()), Resp(json.dumps(refused).encode()), Resp(json.dumps(accepted).encode()), Resp(status=201)])
out = pm.tiktok_direct_post("tok", str(tmp), plan["tiktok"], "public", opener=op)
check(out["ok"] and out["id"] == "p_1" and out["privacy"] == "SELF_ONLY" and out["private_only"], out)
init = json.loads(op.calls[2][3])
check(init["source_info"] == {"source": "FILE_UPLOAD", "video_size": 4096, "chunk_size": 4096, "total_chunk_count": 1}, init)
check(op.calls[3][2].get("Content-range") == "bytes 0-4095/4096", op.calls[3][2])
check(pm.tiktok_chunk_plan(100 * 1024 * 1024) == (32 * 1024 * 1024, 3), "large files use 32MB chunks")

# ---------------------------------------------------------------- wiring
server = (ROOT / "web" / "direct_upload_server.py").read_text(encoding="utf-8")
for token in ("import publish_multi_v413 as _pm413", 'path in ("/publish/multi","/share/link")', 'clean=="/publish/status"',
              'clean.startswith("/share/public/")', '"csrf_token":_security_csrf_token(sid)', '"dropbox_app_key":DROPBOX_APP_KEY',
              "_security_csrf_valid(self,sid)", "GSF_DROPBOX_APP_KEY"):
    check(token in server, "server wiring missing: " + token)
check('or job["results"][platform].get("status")!="queued"' in server, "runner must only publish queued (connected) platforms")
check("print(" not in server.split("def _publish_run")[1].split("def _publish_start")[0].replace('print("GSF_V413_PUBLISH_OK",sid,platform,flush=True)', "").replace('print("GSF_V413_PUBLISH_FAIL",sid,platform,type(exc).__name__,flush=True)', ""),
      "publish runner must not log tokens or payloads")

nginx = (ROOT / "web" / "nginx.conf.template").read_text(encoding="utf-8")
for loc in ("location = /publish/multi {", "location = /share/link {", "location = /publish/status {", "location ^~ /share/public/ {"):
    check(loc in nginx, "nginx route missing: " + loc)
pub = nginx.split("location ^~ /share/public/ {")[1].split("\n    }\n")[0]
check("Set-Cookie" not in pub and 'X-GSF-Session-ID ""' in pub, "public links must not use the browser session")
multi = nginx.split("location = /publish/multi {")[1].split("\n    }\n")[0]
check("limit_except POST" in multi and "X-GSF-Session-ID $gsf_session_cookie" in multi, "publish route is POST + session bound")

page = (ROOT / "web" / "share_v156_component" / "index.html").read_text(encoding="utf-8")
for token in ("V413_CREA_SHORT", "/publish/multi", "/publish/status", "/share/link", "/share/state", "X-GSF-CSRF",
              'data-platform="youtube"', 'data-platform="tiktok"', 'data-platform="instagram"', 'data-platform="facebook"',
              'data-share="whatsapp"', 'data-share="telegram"', 'data-share="email"', 'data-share="x"', 'data-share="copy"',
              'data-share="dropbox"', 'data-share="download"', "dropins.js", "navigator.share", "GSF_SHARE_FOCUS", "GSF_SHELL_NAV",
              'data-scope="tiktok"', "prefers-reduced-motion:reduce", "--gsf-primary:#27AEF3"):
    check(token in page, "page contract missing: " + token)
check("innerHTML=r." not in page and "innerHTML='<span" not in page, "server strings must not be injected as HTML")
check(page.count("<script") == 1, "single self-contained script")

print("V413 PUBLISH MULTI CONTRACT: PASS")
