"""Provider-neutral orchestration for a post-live Auto Highlights job."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .models import LiveJobStatus, LiveProvider, LiveScanJob, LiveSource
from .twitch_vod import ArchivedVod


@dataclass(frozen=True)
class ScanQueueMessage:
    provider: str
    account_id: str
    broadcast_id: str
    vod_id: str
    target_highlights: int
    target_duration: int

    def as_dict(self) -> dict:
        return {
            "kind": "auto_highlights.scan",
            "provider": self.provider,
            "account_id": self.account_id,
            "broadcast_id": self.broadcast_id,
            "vod_id": self.vod_id,
            "target_highlights": self.target_highlights,
            "target_duration": self.target_duration,
        }


def twitch_offline_job(
    *, broadcaster_id: str, vod: Optional[ArchivedVod], target_highlights: int = 5, target_duration: int = 30
) -> LiveScanJob:
    source = LiveSource(
        provider=LiveProvider.TWITCH,
        account_id=str(broadcaster_id),
        broadcast_id=str(broadcaster_id),
        title=vod.title if vod else "",
        vod_id=vod.video_id if vod else None,
        metadata={"vod_url": vod.url if vod else ""},
    )
    job = LiveScanJob(
        source=source,
        target_highlights=max(1, int(target_highlights)),
        target_duration=max(5, int(target_duration)),
    )
    if vod:
        job.status = LiveJobStatus.READY_TO_SCAN
    return job


def queue_message(job: LiveScanJob) -> Optional[ScanQueueMessage]:
    if job.status != LiveJobStatus.READY_TO_SCAN or not job.source.vod_id:
        return None
    return ScanQueueMessage(
        provider=job.source.provider.value,
        account_id=job.source.account_id,
        broadcast_id=job.source.broadcast_id,
        vod_id=job.source.vod_id,
        target_highlights=job.target_highlights,
        target_duration=job.target_duration,
    )
