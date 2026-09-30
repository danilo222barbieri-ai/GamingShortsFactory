"""Second-pass refinement for Auto Highlights.

Takes coarse promising regions and dense local signals, then chooses a natural
short window around the strongest local peak without rendering media.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .live_scanner import WindowSignal, score_window
from .models import HighlightCandidate

@dataclass(frozen=True)
class RefineConfig:
    target_duration: float = 30.0
    min_duration: float = 15.0
    lead_seconds: float = 6.0
    tail_seconds: float = 4.0

def refine_candidate(signals: Iterable[WindowSignal], *, engine: str="automatico",
                     config: RefineConfig=RefineConfig()) -> HighlightCandidate | None:
    rows=[s.normalized() for s in signals if s.end_seconds>s.start_seconds]
    if not rows:
        return None
    peak=max(rows,key=lambda s:score_window(s,engine))
    target=max(config.min_duration,config.target_duration)
    center=(peak.start_seconds+peak.end_seconds)/2.0
    start=max(0.0,center-target/2.0-config.lead_seconds/2.0)
    end=start+target
    # Prefer a nearby low-energy boundary when available, reducing abrupt cuts.
    before=[s for s in rows if s.start_seconds<=center and s.start_seconds>=max(0,start-8)]
    after=[s for s in rows if s.end_seconds>=center and s.end_seconds<=end+8]
    if before:
        quiet=min(before,key=lambda s:score_window(s,engine))
        if score_window(quiet,engine)<score_window(peak,engine)*.45:
            start=max(0.0,quiet.start_seconds)
    end=max(start+config.min_duration,end)
    if after:
        quiet=min(after,key=lambda s:score_window(s,engine))
        if quiet.start_seconds>=start+config.min_duration and score_window(quiet,engine)<score_window(peak,engine)*.45:
            end=quiet.end_seconds
    reason=max((("azione",peak.action),("voce",peak.speech),("picco audio",peak.audio_peak),
                ("reazione",peak.reaction),("cambio scena",peak.scene_change)),key=lambda x:x[1])[0]
    return HighlightCandidate(start,end,score_window(peak,engine),reason,engine)

def dense_region(coarse: HighlightCandidate, *, padding_seconds: float=20.0) -> tuple[float,float]:
    pad=max(0.0,float(padding_seconds))
    return max(0.0,coarse.start_seconds-pad), coarse.end_seconds+pad
