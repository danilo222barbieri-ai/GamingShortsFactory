"""Twitch archived-video resolver for Auto Highlights.

Network transport is intentionally injected so this stays testable and does not
couple the foundation to the production web stack.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional

TWITCH_VIDEOS_URL = "https://api.twitch.tv/helix/videos"


@dataclass(frozen=True)
class ArchivedVod:
    video_id: str
    title: str
    url: str
    created_at: str
    duration: str


def videos_request(*, broadcaster_id: str, first: int = 20) -> tuple[str, dict[str, str]]:
    first = max(1, min(int(first), 100))
    return TWITCH_VIDEOS_URL, {
        "user_id": str(broadcaster_id),
        "type": "archive",
        "first": str(first),
    }


def parse_latest_archive(payload: Mapping[str, Any]) -> Optional[ArchivedVod]:
    rows = payload.get("data") or []
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, Mapping) or row.get("type") != "archive":
            continue
        video_id = str(row.get("id") or "")
        if not video_id:
            continue
        return ArchivedVod(
            video_id=video_id,
            title=str(row.get("title") or ""),
            url=str(row.get("url") or ""),
            created_at=str(row.get("created_at") or ""),
            duration=str(row.get("duration") or ""),
        )
    return None


def resolve_latest_archive(
    *, broadcaster_id: str, fetch_json: Callable[[str, Mapping[str, str]], Mapping[str, Any]]
) -> Optional[ArchivedVod]:
    url, params = videos_request(broadcaster_id=broadcaster_id)
    return parse_latest_archive(fetch_json(url, params))
