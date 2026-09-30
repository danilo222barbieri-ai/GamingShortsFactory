"""Serializable Creator Hub view-models for Auto Highlights live folders."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Iterable
from .models import HighlightCandidate

@dataclass(frozen=True)
class LiveHighlightItem:
    id: str
    start_seconds: float
    end_seconds: float
    score_percent: int
    reason: str
    engine: str
    status: str = "ready_for_editor"

@dataclass
class LiveFolder:
    id: str
    provider: str
    account_id: str
    broadcast_id: str
    title: str
    ended_at: str
    status: str = "ready"
    highlights: list[LiveHighlightItem] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)

def build_live_folder(*, provider: str, account_id: str, broadcast_id: str, title: str,
                      ended_at: str, candidates: Iterable[HighlightCandidate]) -> LiveFolder:
    safe_id=f"{provider}:{broadcast_id}"
    items=[]
    for i,c in enumerate(candidates,1):
        items.append(LiveHighlightItem(
            id=f"{safe_id}:h{i}",
            start_seconds=round(float(c.start_seconds),3),
            end_seconds=round(float(c.end_seconds),3),
            score_percent=max(0,min(100,round(float(c.score)*100))),
            reason=str(c.reason),
            engine=str(c.engine),
        ))
    return LiveFolder(safe_id,provider,account_id,broadcast_id,title,ended_at,highlights=items)
