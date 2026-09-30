"""V129: turn an existing worker scan into post-live highlights.

This reuses the production Game Brain; no eager video rendering and no second
ranking algorithm.
"""
from __future__ import annotations

from typing import Any

from game_brain_v112 import rerank_moments
from .models import HighlightCandidate, LiveJobStatus, LiveScanJob


def _num(value,default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def _event_pool(events,target_duration):
    duration=max(5.0,float(target_duration or 30))
    lead=min(8.0,max(2.0,duration*.30))
    rows=[]
    for event in events or []:
        if not isinstance(event,dict):
            continue
        if str(event.get("kind") or "").upper()=="SILENCE":
            continue
        t=_num(event.get("time"),-1.0)
        if t<0:
            continue
        score=max(
            _num(event.get("score"),0.0),
            _num(event.get("semantic_score"),0.0),
            .70*_num(event.get("semantic_confidence"),0.0)
            +.30*_num(event.get("semantic_excitement"),0.0),
        )
        if score<=0:
            continue
        rows.append((min(.999,max(.05,score)),max(0.0,t-lead)))
    rows.sort(reverse=True)
    return rows[:40]


def analysis_to_candidates(
    analysis:dict[str,Any],
    *,
    target_highlights=5,
    target_duration=30,
    genre="Auto",
    profile="auto",
):
    payload=dict(analysis or {})
    scan=dict(payload.get("scan") or payload)
    events=list(scan.get("event_map_v108") or [])
    diagnostics=(
        scan.get("diagnostics")
        or scan.get("candidate_diagnostics")
        or scan.get("rank_diagnostics")
        or {}
    )
    pool=_event_pool(events,target_duration)
    if not pool:
        return [],{
            "engine":"auto-highlights-v129",
            "selected":[],
            "selected_count":0,
            "reason":"no-events",
        }

    chosen,brain=rerank_moments(
        pool,
        diagnostics,
        clip_duration=float(target_duration),
        numero_clip=max(1,int(target_highlights or 5)),
        profile=str(profile or "auto"),
        genre=str(genre or "Auto"),
        events=events,
    )
    meta_rows=list((brain or {}).get("selected") or [])
    candidates=[]
    for index,chosen_row in enumerate(chosen):
        _score,_start=chosen_row
        meta=meta_rows[index] if index<len(meta_rows) and isinstance(meta_rows[index],dict) else {}
        start=max(0.0,float(meta.get("start",_start) or _start))
        duration=max(5.0,float(target_duration))
        candidates.append(
            HighlightCandidate(
                start_seconds=round(start,3),
                end_seconds=round(start+duration,3),
                score=round(float(meta.get("brain_score",_score) or _score),6),
                reason=str(meta.get("reason") or "HIGHLIGHT"),
                engine=str((brain or {}).get("engine") or "game-brain-v129"),
                confidence=round(float(meta.get("confidence",0.0) or 0.0),5),
                event=str(meta.get("event") or "highlight"),
                director_plan=dict(meta.get("director_plan") or {}),
            )
        )
    return candidates,{
        "engine":"auto-highlights-v129",
        "game_brain":brain,
        "event_count":len(events),
        "pool_size":len(pool),
        "selected_count":len(candidates),
    }


def apply_analysis_to_job(job:LiveScanJob,analysis:dict[str,Any],genre="Auto"):
    job.status=LiveJobStatus.SCANNING
    try:
        candidates,meta=analysis_to_candidates(
            analysis,
            target_highlights=job.target_highlights,
            target_duration=job.target_duration,
            genre=genre,
        )
        job.candidates=candidates
        job.status=LiveJobStatus.HIGHLIGHTS_READY if candidates else LiveJobStatus.FAILED
        return meta
    except Exception:
        job.status=LiveJobStatus.FAILED
        raise


def candidate_dict(candidate:HighlightCandidate):
    return {
        "start_seconds":candidate.start_seconds,
        "end_seconds":candidate.end_seconds,
        "duration":candidate.duration,
        "score":candidate.score,
        "reason":candidate.reason,
        "engine":candidate.engine,
        "confidence":candidate.confidence,
        "event":candidate.event,
        "director_plan":dict(candidate.director_plan or {}),
    }
