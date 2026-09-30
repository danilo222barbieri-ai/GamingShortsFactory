"""Twitch OAuth helpers for GSF Auto Highlights.

No HTTP server routes are registered here yet. Secrets/tokens must stay server-side.
"""
from __future__ import annotations
import secrets
from urllib.parse import urlencode

TWITCH_AUTHORIZE_URL = "https://id.twitch.tv/oauth2/authorize"
TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_VALIDATE_URL = "https://id.twitch.tv/oauth2/validate"


def new_oauth_state() -> str:
    return secrets.token_urlsafe(32)


def build_authorize_url(*, client_id: str, redirect_uri: str, state: str, scopes=()) -> str:
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
    }
    scopes = tuple(str(s).strip() for s in scopes if str(s).strip())
    if scopes:
        params["scope"] = " ".join(scopes)
    return TWITCH_AUTHORIZE_URL + "?" + urlencode(params)


def token_exchange_payload(*, client_id: str, client_secret: str, code: str, redirect_uri: str) -> dict[str, str]:
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
