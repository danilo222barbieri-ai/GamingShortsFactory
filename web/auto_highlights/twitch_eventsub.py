"""Twitch EventSub verification and stream.offline normalization."""
from __future__ import annotations
import hashlib
import hmac
from dataclasses import dataclass
from typing import Mapping, Optional

MESSAGE_ID = "twitch-eventsub-message-id"
MESSAGE_TIMESTAMP = "twitch-eventsub-message-timestamp"
MESSAGE_SIGNATURE = "twitch-eventsub-message-signature"
MESSAGE_TYPE = "twitch-eventsub-message-type"


@dataclass(frozen=True)
class EventSubEnvelope:
    message_id: str
    timestamp: str
    message_type: str
    signature: str


def _headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {str(k).lower(): str(v) for k, v in headers.items()}


def envelope(headers: Mapping[str, str]) -> EventSubEnvelope:
    h = _headers(headers)
    return EventSubEnvelope(
        message_id=h.get(MESSAGE_ID, ""),
        timestamp=h.get(MESSAGE_TIMESTAMP, ""),
        message_type=h.get(MESSAGE_TYPE, ""),
        signature=h.get(MESSAGE_SIGNATURE, ""),
    )


def expected_signature(secret: str, headers: Mapping[str, str], raw_body: bytes) -> str:
    e = envelope(headers)
    message = e.message_id.encode() + e.timestamp.encode() + raw_body
    digest = hmac.new(secret.encode("ascii"), message, hashlib.sha256).hexdigest()
    return "sha256=" + digest


def verify_signature(secret: str, headers: Mapping[str, str], raw_body: bytes) -> bool:
    e = envelope(headers)
    if not secret or not e.message_id or not e.timestamp or not e.signature:
        return False
    expected = expected_signature(secret, headers, raw_body)
    return hmac.compare_digest(expected, e.signature)


def verification_challenge(payload: Mapping) -> Optional[str]:
    challenge = payload.get("challenge")
    return str(challenge) if challenge is not None else None


def stream_offline_event(payload: Mapping) -> Optional[dict[str, str]]:
    subscription = payload.get("subscription") or {}
    if subscription.get("type") != "stream.offline":
        return None
    event = payload.get("event") or {}
    broadcaster_id = str(event.get("broadcaster_user_id") or "")
    if not broadcaster_id:
        return None
    return {
        "provider": "twitch",
        "event": "stream.offline",
        "broadcaster_user_id": broadcaster_id,
        "broadcaster_user_login": str(event.get("broadcaster_user_login") or ""),
        "broadcaster_user_name": str(event.get("broadcaster_user_name") or ""),
    }
