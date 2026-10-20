"""V423 live OAuth compatibility entrypoint.

Keep the stable direct-upload server untouched while production OAuth contracts are
corrected in one narrow layer: TikTok Direct Post scopes, authoritative Creator
Hub social state, and a cache-busted/no-store return after provider consent.
"""
from __future__ import annotations

import time
import urllib.parse

import direct_upload_server as base


# Direct Post requires publishing permission. video.list is analytics-only and
# must not block connecting an otherwise valid TikTok publishing account.
base.TIKTOK_SCOPE = "user.info.basic,video.publish"


_original_redirect = base._redirect


def _fresh_social_redirect(handler, url):
    """Prevent mobile Safari from restoring a stale/broken Hub snapshot."""
    if url == "/?gsf_hub=social":
        location = url + "&oauth_return=" + str(int(time.time() * 1000))
        handler.send_response(302)
        handler.send_header("Location", location)
        handler.send_header("Cache-Control", "no-store, max-age=0")
        handler.send_header("Pragma", "no-cache")
        handler.send_header("Content-Length", "0")
        handler.end_headers()
        return
    return _original_redirect(handler, url)


base._redirect = _fresh_social_redirect


def _tiktok_oauth_callback(handler, query):
    state = str((query.get("state") or [""])[0] or "")
    prefix = "gsfact_" if state.startswith("gsfact_") else "gsfsc_"
    pending = base._social_state_finish(handler, state, prefix, "tiktok")
    sid = base._safe_id(pending.get("sid", ""))
    if not sid:
        base._html(handler, 400, "Stato OAuth TikTok non valido o scaduto.")
        return
    if query.get("error") or not query.get("code"):
        base._html(handler, 400, "Autorizzazione TikTok non completata.")
        return
    try:
        form = {
            "client_key": base.TIKTOK_CLIENT_KEY,
            "client_secret": base.TIKTOK_CLIENT_SECRET,
            "code": query["code"][0],
            "grant_type": "authorization_code",
            "redirect_uri": pending.get("redirect_uri") or base.PUBLIC_APP_URL,
        }
        token = base._oauth_json(
            "https://open.tiktokapis.com/v2/oauth/token/",
            method="POST",
            data=urllib.parse.urlencode(form).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        access = str(token.get("access_token") or "")
        uid = str(token.get("open_id") or "")
        if not access or not uid or token.get("error"):
            raise ValueError("Invalid token response")
        info = base._oauth_json(
            "https://open.tiktokapis.com/v2/user/info/?fields=open_id,display_name,avatar_url",
            headers={"Authorization": "Bearer " + access},
        )
        user = (info.get("data") or {}).get("user") or {}
        if str(user.get("open_id") or "") != uid:
            raise ValueError("Invalid account identity")
        login = pending.get("login") or prefix == "gsfact_"
        if login:
            mapped = base._oauth_object_read(base._creator_identity_key("tiktok", uid))
            current = base._creator_account_load(sid) or {}
            if mapped.get("account_id") and current.get("account_id") and mapped["account_id"] != current["account_id"]:
                raise ValueError("Account already linked")
            base._creator_login(
                sid,
                "tiktok",
                uid,
                display_name=user.get("display_name") or "TikTok Creator",
                avatar=user.get("avatar_url") or "",
            )
        else:
            granted = set(str(token.get("scope") or "").split(","))
            if not {"user.info.basic", "video.publish"} <= granted:
                raise ValueError("Required permissions were not granted")
            now = time.time()
            expiry = int(token.get("expires_in") or 0)
            if expiry <= 0:
                raise ValueError("Invalid token expiry")
            token.update(
                saved_at=now,
                _saved_at=now,
                expires_at=now + expiry,
                refresh_expires_at=now + int(token.get("refresh_expires_in") or 0),
            )
            base._tiktok_user_save(sid, token)
        base._redirect(handler, "/?gsf_hub=social")
    except Exception:
        base._html(handler, 502, "Collegamento TikTok non riuscito. Riprova dal Creator Hub.")


base._tiktok_oauth_callback = _tiktok_oauth_callback


def _creator_hub_state(handler, path):
    sid = base._social_sid(handler)
    if not sid:
        base._json(handler, 400, {"ok": False, "error": "Sessione browser non valida."})
        return

    scope = str((urllib.parse.parse_qs(path.query).get("scope") or [""])[0] or "")
    if scope == "header":
        profile = base._creator_account_load(sid) or {}
        account_id = base._safe_id(profile.get("account_id", "")) if isinstance(profile, dict) else ""
        avatar = str(profile.get("avatar") or "") if isinstance(profile, dict) else ""
        if avatar.startswith("data:image/"):
            avatar = "/creator-hub/avatar?v=" + str(int(float(profile.get("updated_at") or 0) * 1000))
        base._json(
            handler,
            200,
            {
                "ok": True,
                "csrf_token": base._security_csrf_token(sid),
                "account": {
                    "connected": bool(account_id),
                    "id": account_id,
                    "display_name": str(profile.get("display_name") or "Creator")[:120] if isinstance(profile, dict) else "Creator",
                    "avatar": avatar[:1800],
                    "plan": str(profile.get("plan") or "FREE")[:24] if isinstance(profile, dict) else "FREE",
                    "creator_level": int(profile.get("creator_level") or 1) if isinstance(profile, dict) else 1,
                },
            },
        )
        return

    profile = base._creator_account_load(sid) or {}
    providers = dict(profile.get("providers") or {}) if isinstance(profile, dict) else {}
    social_snapshot = base._creator_social_snapshot(sid, providers)
    limits = base._storage_limits_for_sid(sid)
    all_drafts = base._draft_list(sid)
    all_shorts = base._short_list(sid)

    drafts = []
    for row in all_drafts[: max(1, int(limits.get("drafts") or base.FREE_DRAFT_LIMIT))]:
        if not isinstance(row, dict):
            continue
        drafts.append(
            {
                "id": base._safe_id(row.get("id", "")),
                "title": str(row.get("title") or row.get("source_name") or "Gameplay")[:120],
                "source_name": str(row.get("source_name") or "Gameplay")[:120],
                "duration": int(row.get("duration") or 0),
                "updated_at": float(row.get("updated_at") or 0),
            }
        )

    project = {}
    account_id = base._safe_id(profile.get("account_id", "")) if isinstance(profile, dict) else ""
    try:
        project_root = (base.ROOT / "creator-projects" / account_id) if account_id else (base.ROOT / "sessions" / sid / "projects")
        idx = base.json.loads((project_root / "index.json").read_text(encoding="utf-8"))
        pid = base._safe_id(idx.get("active_project_id", ""))
        if pid:
            pdata = base.json.loads((project_root / pid / "project_state.json").read_text(encoding="utf-8"))
            project = {
                "id": pid,
                "updated_at": float(pdata.get("updated_at") or idx.get("updated_at") or 0),
                "has_source": bool((pdata.get("state") or {}).get("gsf_source_path") or (pdata.get("state") or {}).get("gsf_editor_source_path")),
                "title": str(pdata.get("title") or idx.get("active_project_title") or "Progetto corrente")[:180],
            }
    except Exception:
        pass

    base._json(
        handler,
        200,
        {
            "ok": True,
            "csrf_token": base._security_csrf_token(sid),
            "account": {
                "connected": bool(account_id),
                "id": account_id,
                "display_name": str(profile.get("display_name") or "Creator")[:120] if isinstance(profile, dict) else "Creator",
                "avatar": (
                    (
                        "/creator-hub/avatar"
                        if str(profile.get("avatar") or "").startswith("data:image/")
                        else str(profile.get("avatar") or "")[:1800000]
                    )
                    if isinstance(profile, dict)
                    else ""
                ),
                "plan": str(profile.get("plan") or "FREE")[:24] if isinstance(profile, dict) else "FREE",
                "creator_level": int(profile.get("creator_level") or 1) if isinstance(profile, dict) else 1,
            },
            "social": {
                "youtube": bool(social_snapshot.get("youtube")),
                "tiktok": bool(social_snapshot.get("tiktok")),
                "instagram": bool(social_snapshot.get("instagram")),
                "facebook": bool(social_snapshot.get("facebook")),
                "twitch": bool(social_snapshot.get("twitch")),
            },
            "stats": {
                "shorts_created": len(all_shorts),
                "shorts_published": sum(1 for row in all_shorts if (row or {}).get("published")),
                "drafts": len(all_drafts),
                "social": sum(1 for connected in social_snapshot.values() if connected),
            },
            "limits": limits,
            "usage": {"drafts": len(all_drafts), "shorts": len(all_shorts)},
            "drafts": drafts,
            "shorts": [
                {
                    "id": base._safe_id((row or {}).get("id", "")),
                    "title": str((row or {}).get("title") or "Short")[:120],
                    "source_name": str((row or {}).get("source_name") or "")[:120],
                    "completed_at": float((row or {}).get("completed_at") or 0),
                    "final_bytes": int((row or {}).get("final_bytes") or 0),
                    "published": list((row or {}).get("published") or [])[:8],
                }
                for row in all_shorts[: max(1, int(limits.get("shorts") or base.FREE_SHORT_LIMIT))]
            ],
            "project": project,
        },
    )


class Handler(base.Handler):
    def do_GET(self):
        path = urllib.parse.urlparse(self.path)
        if path.path.rstrip("/") == "/creator-hub/state":
            _creator_hub_state(self, path)
            return
        return super().do_GET()


if __name__ == "__main__":
    base.ROOT.mkdir(parents=True, exist_ok=True)
    base._ensure_bucket_cors()
    base._ai_learning_restore()
    base._start_proactive_guardian()
    base._start_social_analytics_worker()
    base._start_twitch_token_validation()
    server = base.ThreadingHTTPServer(("127.0.0.1", base.PORT), Handler)
    print(
        f"GSF direct upload server V423 listening on 127.0.0.1:{base.PORT} "
        f"bucket={'on' if base._bucket_enabled() else 'off'} worker={'on' if base.WORKER_URL else 'off'}",
        flush=True,
    )
    server.serve_forever()
