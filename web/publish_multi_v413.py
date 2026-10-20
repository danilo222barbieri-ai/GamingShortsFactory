"""V413 — Crea Short multi-publish engine.

Pure, dependency-free helpers used by ``direct_upload_server.py`` to publish
the final Short to several social platforms with one click:

* ``normalize_request``  — validates the page payload and builds the per
  platform metadata (shared texts + optional per-platform overrides).
* ``youtube_upload``     — official YouTube Data API v3 resumable upload.
* ``tiktok_direct_post`` — official TikTok Content Posting API (Direct Post).
* ``sign_share_link`` / ``verify_share_link`` — short-lived signed links that
  let Dropbox Saver, WhatsApp, Telegram, X and e-mail reach the final video
  without the browser session cookie.

Every network call goes through an injectable ``opener`` so the whole flow is
testable offline. No token, secret or personal data is ever logged here.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import time
import urllib.error
import urllib.request

MARKER = "V413_PUBLISH_MULTI"

PLATFORMS = ("youtube", "tiktok", "instagram", "facebook")
# Platforms this server can publish to by itself today. Instagram needs Meta
# app credentials and Facebook publishing is not implemented yet.
SUPPORTED = ("youtube", "tiktok")

LIMITS = {
    "youtube": {"title": 100, "description": 5000, "tags": 30},
    "tiktok": {"title": 0, "description": 2200, "tags": 30},
    "instagram": {"title": 0, "description": 2200, "tags": 30},
    "facebook": {"title": 255, "description": 5000, "tags": 30},
}
PRIVACY = ("public", "unlisted", "private")

YOUTUBE_UPLOAD_URL = (
    "https://www.googleapis.com/upload/youtube/v3/videos"
    "?uploadType=resumable&part=snippet,status"
)
TIKTOK_CREATOR_INFO = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
TIKTOK_DIRECT_INIT = "https://open.tiktokapis.com/v2/post/publish/video/init/"

_TAG_RE = re.compile(r"#?([0-9A-Za-zÀ-ÖØ-öø-ÿ_]{1,60})")


# --------------------------------------------------------------------------
# Payload normalisation
# --------------------------------------------------------------------------
def parse_hashtags(raw) -> list[str]:
    """Accept '#a #b', 'a, b' or a list; return unique tags without '#'."""
    if isinstance(raw, (list, tuple)):
        raw = " ".join(str(x) for x in raw)
    out: list[str] = []
    seen = set()
    for match in _TAG_RE.finditer(str(raw or "")):
        tag = match.group(1)
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            out.append(tag)
    return out


def _clip(text, limit):
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(text or "")).strip()
    return text[:limit] if limit else text


def build_caption(description, tags, limit):
    """Description followed by hashtags, trimmed to the platform limit."""
    description = _clip(description, 0)
    tag_line = " ".join("#" + t for t in tags)
    caption = (description + ("\n\n" if description and tag_line else "") + tag_line).strip()
    if limit and len(caption) > limit:
        # Keep whole hashtags: drop tags from the end before cutting the text.
        kept = list(tags)
        while kept and len(caption) > limit:
            kept.pop()
            tag_line = " ".join("#" + t for t in kept)
            caption = (description + ("\n\n" if description and tag_line else "") + tag_line).strip()
        caption = caption[:limit]
    return caption


def normalize_request(payload) -> dict:
    """Validate the page payload. Raises ValueError with an Italian message."""
    if not isinstance(payload, dict):
        raise ValueError("Richiesta non valida.")
    wanted = []
    for p in payload.get("platforms") or []:
        p = str(p or "").strip().lower()
        if p in PLATFORMS and p not in wanted:
            wanted.append(p)
    if not wanted:
        raise ValueError("Scegli almeno un social.")

    base = payload.get("shared") if isinstance(payload.get("shared"), dict) else {}
    title = _clip(base.get("title"), 0)
    description = _clip(base.get("description"), 0)
    tags = parse_hashtags(base.get("hashtags"))
    privacy = str(payload.get("privacy") or "public").lower()
    if privacy not in PRIVACY:
        privacy = "public"
    overrides = payload.get("overrides") if isinstance(payload.get("overrides"), dict) else {}

    plans = {}
    for p in wanted:
        lim = LIMITS[p]
        o = overrides.get(p) if isinstance(overrides.get(p), dict) else {}
        p_title = _clip(o.get("title"), 0) if str(o.get("title") or "").strip() else title
        p_desc = _clip(o.get("description"), 0) if str(o.get("description") or "").strip() else description
        p_tags = parse_hashtags(o.get("hashtags")) if str(o.get("hashtags") or "").strip() else list(tags)
        if p == "youtube" and not any(t.lower() == "shorts" for t in p_tags):
            p_tags.append("Shorts")
        p_tags = p_tags[: lim["tags"]]
        plans[p] = {
            "platform": p,
            "title": _clip(p_title, lim["title"]) if lim["title"] else "",
            "description": _clip(p_desc, lim["description"]),
            "tags": p_tags,
            "caption": build_caption(p_desc or p_title, p_tags, lim["description"]),
        }
    if "youtube" in plans and not plans["youtube"]["title"].strip():
        raise ValueError("Serve un titolo per YouTube.")
    return {"platforms": wanted, "privacy": privacy, "plans": plans}


# --------------------------------------------------------------------------
# HTTP helpers
# --------------------------------------------------------------------------
class PublishError(RuntimeError):
    pass


class PublishUnconfirmed(PublishError):
    def __init__(self,publish_id):
        self.publish_id=publish_id
        super().__init__("TikTok sta ancora elaborando il video: pubblicazione non confermata. Controlla lo stato prima di riprovare.")


def tiktok_post_status(access_token,publish_id,opener=None):
    data=_json_call(opener,"https://open.tiktokapis.com/v2/post/publish/status/fetch/",access_token,{"publish_id":publish_id},timeout=10)
    code,_message=_api_error(data)
    if code:raise PublishError("Stato TikTok non disponibile. Ricollega l'account se necessario.")
    return str((data.get("data") or {}).get("status") or "")


def _open(opener, req, timeout):
    return (opener or urllib.request.urlopen)(req, timeout=timeout)


def _json_call(opener, url, token, body, timeout=30):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + str(token or ""),
            "Content-Type": "application/json; charset=UTF-8",
        },
        method="POST",
    )
    try:
        with _open(opener, req, timeout) as resp:
            return json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        try:
            return json.loads(exc.read().decode("utf-8") or "{}")
        except Exception:
            raise PublishError(f"HTTP {exc.code}") from None


def _api_error(payload):
    err = (payload or {}).get("error") or {}
    if isinstance(err, dict):
        code = str(err.get("code") or "")
        if code and code != "ok":
            return code, str(err.get("message") or code)
    return "", ""


# --------------------------------------------------------------------------
# YouTube
# --------------------------------------------------------------------------
def youtube_upload(access_token, video_path, plan, privacy="public", opener=None, made_for_kids=False):
    """Resumable upload: one session request, then the file in one PUT."""
    if not access_token:
        raise PublishError("YouTube non collegato.")
    size = os.path.getsize(video_path)
    body = {
        "snippet": {
            "title": plan.get("title") or "Gaming Short",
            "description": build_caption(plan.get("description"), plan.get("tags") or [], 5000),
            "categoryId": "20",
            "tags": list(plan.get("tags") or [])[:30],
        },
        "status": {
            "privacyStatus": privacy if privacy in PRIVACY else "public",
            "selfDeclaredMadeForKids": bool(made_for_kids),
        },
    }
    last = ""
    for attempt in range(3):
        start = urllib.request.Request(
            YOUTUBE_UPLOAD_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + access_token,
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Type": "video/mp4",
                "X-Upload-Content-Length": str(size),
            },
            method="POST",
        )
        try:
            with _open(opener, start, 30) as resp:
                location = resp.headers.get("Location") or ""
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            if exc.code in (401, 403):
                raise PublishError(_youtube_reason(detail) or "YouTube ha rifiutato l'accesso: ricollega l'account.")
            last = f"HTTP {exc.code}"
            if exc.code >= 500:
                time.sleep(min(8, 2 ** attempt))
                continue
            raise PublishError(_youtube_reason(detail) or f"YouTube HTTP {exc.code}")
        if not location:
            raise PublishError("YouTube non ha aperto la sessione di upload.")
        with open(video_path, "rb") as fh:
            put = urllib.request.Request(
                location,
                data=fh,
                headers={"Content-Type": "video/mp4", "Content-Length": str(size)},
                method="PUT",
            )
            try:
                with _open(opener, put, 600) as resp:
                    payload = json.loads(resp.read().decode("utf-8") or "{}")
            except urllib.error.HTTPError as exc:
                last = f"HTTP {exc.code}"
                if exc.code >= 500:
                    time.sleep(min(8, 2 ** attempt))
                    continue
                raise PublishError(_youtube_reason(exc.read().decode("utf-8", "replace")[:300]) or f"YouTube upload HTTP {exc.code}")
        video_id = str(payload.get("id") or "")
        if not video_id:
            raise PublishError("YouTube non ha restituito l'ID del video.")
        return {
            "ok": True,
            "id": video_id,
            "url": f"https://youtube.com/shorts/{video_id}",
            "privacy": body["status"]["privacyStatus"],
        }
    raise PublishError(f"YouTube non risponde ({last}). Riprova tra poco.")


def _youtube_reason(detail):
    try:
        err = json.loads(detail).get("error") or {}
        reason = ((err.get("errors") or [{}])[0] or {}).get("reason") or ""
    except Exception:
        return ""
    if reason in ("quotaExceeded", "uploadLimitExceeded"):
        return "Limite giornaliero di YouTube raggiunto. Riprova domani."
    if reason in ("authError", "insufficientPermissions", "forbidden"):
        return "Permessi YouTube insufficienti: ricollega l'account."
    return str(err.get("message") or "")[:160]


# --------------------------------------------------------------------------
# TikTok
# --------------------------------------------------------------------------
def tiktok_chunk_plan(size):
    size = max(0, int(size or 0))
    if size <= 0:
        return 0, 0
    if size <= 64 * 1024 * 1024:
        return size, 1
    chunk = 32 * 1024 * 1024
    return chunk, max(1, size // chunk)


def _tiktok_privacy(options, wanted):
    options = [str(x) for x in options or [] if str(x)]
    if wanted == "public" and "PUBLIC_TO_EVERYONE" in options:
        return options, "PUBLIC_TO_EVERYONE"
    if "SELF_ONLY" in options:
        return options, "SELF_ONLY"
    if options:
        return options, options[0]
    raise PublishError("TikTok non ha restituito opzioni di privacy.")


def tiktok_direct_post(access_token, video_path, plan, privacy="public", opener=None):
    if not access_token:
        raise PublishError("TikTok non collegato.")
    info = _json_call(opener, TIKTOK_CREATOR_INFO, access_token, {})
    code, message = _api_error(info)
    if code:
        if code in ("access_token_invalid", "scope_not_authorized"):
            raise PublishError("TikTok ha rifiutato l'accesso: ricollega l'account.")
        raise PublishError("TikTok: " + message)
    creator = info.get("data") or {}
    options, level = _tiktok_privacy(creator.get("privacy_level_options"), privacy)
    size = os.path.getsize(video_path)
    max_sec = int(creator.get("max_video_post_duration_sec") or 0)
    chunk, count = tiktok_chunk_plan(size)

    def init(level_):
        return _json_call(opener, TIKTOK_DIRECT_INIT, access_token, {
            "post_info": {
                "title": (plan.get("caption") or "")[:2200],
                "privacy_level": level_,
                "disable_comment": bool(creator.get("comment_disabled")),
                "disable_duet": bool(creator.get("duet_disabled")),
                "disable_stitch": bool(creator.get("stitch_disabled")),
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": size,
                "chunk_size": chunk,
                "total_chunk_count": count,
            },
        })

    started = init(level)
    code, message = _api_error(started)
    if code == "unaudited_client_can_only_post_to_private_accounts" and level != "SELF_ONLY" and "SELF_ONLY" in options:
        level = "SELF_ONLY"
        started = init(level)
        code, message = _api_error(started)
    if code:
        if code == "spam_risk_too_many_posts":
            raise PublishError("TikTok: troppi post oggi, riprova più tardi.")
        raise PublishError("TikTok: " + message)
    data = started.get("data") or {}
    upload_url = str(data.get("upload_url") or "")
    publish_id = str(data.get("publish_id") or "")
    if not upload_url or not publish_id:
        raise PublishError("TikTok non ha restituito l'indirizzo di upload.")

    sent = 0
    with open(video_path, "rb") as fh:
        for index in range(count):
            this = size - sent if index == count - 1 else chunk
            blob = fh.read(this)
            req = urllib.request.Request(
                upload_url,
                data=blob,
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Length": str(len(blob)),
                    "Content-Range": f"bytes {sent}-{sent + len(blob) - 1}/{size}",
                },
                method="PUT",
            )
            try:
                with _open(opener, req, 300) as resp:
                    status = int(getattr(resp, "status", 200) or 200)
            except urllib.error.HTTPError as exc:
                if exc.code>=500:raise PublishUnconfirmed(publish_id) from None
                raise PublishError(f"TikTok upload HTTP {exc.code}") from None
            except (OSError,TimeoutError):
                # The transport can accept bytes before its response is lost.
                raise PublishUnconfirmed(publish_id) from None
            if status>=500:raise PublishUnconfirmed(publish_id)
            if status not in (200, 201, 206):
                raise PublishError(f"TikTok upload HTTP {status}")
            sent += len(blob)
    # TikTok accepting bytes does not mean the post was published.
    for attempt in range(30):
        try:state=tiktok_post_status(access_token,publish_id,opener)
        except Exception:raise PublishUnconfirmed(publish_id) from None
        if state=="PUBLISH_COMPLETE":break
        if state=="FAILED":raise PublishError("TikTok non ha pubblicato il video. Verifica l'account e riprova.")
        if attempt<29:time.sleep(2)
    else:raise PublishUnconfirmed(publish_id)
    return {
        "ok": True,
        "id": publish_id,
        "privacy": level,
        "private_only": level == "SELF_ONLY" and privacy == "public",
        "max_duration_sec": max_sec,
    }


# --------------------------------------------------------------------------
# Signed share links
# --------------------------------------------------------------------------
def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def sign_share_link(secret: bytes, sid: str, ttl: int = 86400, now: float | None = None) -> tuple[str, int]:
    if not secret or not sid:
        raise ValueError("share link unavailable")
    exp = int((now if now is not None else time.time()) + max(60, int(ttl)))
    body = _b64(f"{sid}.{exp}".encode("utf-8"))
    sig = _b64(hmac.new(secret, b"gsf-share-v413:" + body.encode("ascii"), hashlib.sha256).digest()[:18])
    return f"{body}.{sig}", exp


def verify_share_link(secret: bytes, token: str, now: float | None = None) -> str:
    """Return the session id for a valid, unexpired token, else ''."""
    try:
        body, sig = str(token or "").split(".", 1)
        expected = _b64(hmac.new(secret, b"gsf-share-v413:" + body.encode("ascii"), hashlib.sha256).digest()[:18])
        if not secret or not hmac.compare_digest(expected, sig):
            return ""
        sid, exp = _unb64(body).decode("utf-8").rsplit(".", 1)
        if int(exp) < (now if now is not None else time.time()):
            return ""
        return sid if re.fullmatch(r"[A-Za-z0-9_-]{1,80}", sid) else ""
    except Exception:
        return ""
