"""GSF Auto Highlights foundation.

Provider-neutral contracts only. No production wiring yet.
The goal is to let Twitch EventSub and YouTube completed-live detection feed the
same lightweight analysis queue without downloading/rendering full VODs first.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional


class LiveProvider(str, Enum):
    TWITCH = "twitch"
    YOUTUBE = "youtube"


class LiveJobStatus(str, Enum):
    WAITING_FOR_VOD = "waiting_for_vod"
    READY_TO_SCAN = "ready_to_scan"
    SCANNING = "scanning"
    HIGHLIGHTS_READY = "highlights_ready"
    FAILED = "failed"


@dataclass(frozen=True)
class LiveSource:
    provider: LiveProvider
    account_id: str
    broadcast_id: str
    title: str = ""
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    vod_id: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HighlightCandidate:
    start_seconds: float
    end_seconds: float
    score: float
    reason: str
    engine: str = "game-brain-v129"
    confidence: float = 0.0
    event: str = "highlight"
    director_plan: Mapping[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_seconds - self.start_seconds)


@dataclass
class LiveScanJob:
    source: LiveSource
    status: LiveJobStatus = LiveJobStatus.WAITING_FOR_VOD
    target_highlights: int = 5
    target_duration: int = 30
    candidates: list[HighlightCandidate] = field(default_factory=list)

    def mark_vod_ready(self, vod_id: str) -> None:
        self.source = LiveSource(
            provider=self.source.provider,
            account_id=self.source.account_id,
            broadcast_id=self.source.broadcast_id,
            title=self.source.title,
            started_at=self.source.started_at,
            ended_at=self.source.ended_at,
            vod_id=vod_id,
            metadata=self.source.metadata,
        )
        self.status = LiveJobStatus.READY_TO_SCAN
