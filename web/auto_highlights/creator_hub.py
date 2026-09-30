"""Presentation helpers for the future Creator Hub Auto Highlights panel."""
from __future__ import annotations

def creator_hub_payload(folders: list[dict]) -> dict:
    ready=sum(1 for f in folders if f.get("status")=="ready")
    highlights=sum(len(f.get("highlights") or []) for f in folders)
    return {
        "title":"AUTO HIGHLIGHTS",
        "tagline":"Tu fai la live. GSF trova i momenti da pubblicare.",
        "ready_live_count":ready,
        "highlight_count":highlights,
        "folders":folders,
    }
