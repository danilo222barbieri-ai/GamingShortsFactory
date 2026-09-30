"""Low-cost first-pass scanner for long live recordings.

This module ranks already-extracted time-window signals. Heavy media decoding is
kept outside so the worker can sample a long VOD without holding it in memory.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .models import HighlightCandidate


@dataclass(frozen=True)
class WindowSignal:
    start_seconds: float
    end_seconds: float
    action: float = 0.0
    speech: float = 0.0
    audio_peak: float = 0.0
    reaction: float = 0.0
    scene_change: float = 0.0

    def normalized(self) -> "WindowSignal":
        clamp=lambda x:max(0.0,min(1.0,float(x)))
        return WindowSignal(
            max(0.0,float(self.start_seconds)),
            max(float(self.start_seconds),float(self.end_seconds)),
            clamp(self.action),clamp(self.speech),clamp(self.audio_peak),
            clamp(self.reaction),clamp(self.scene_change),
        )


ENGINE_WEIGHTS={
    "automatico": {"action":.30,"speech":.15,"audio_peak":.20,"reaction":.25,"scene_change":.10},
    "azione": {"action":.55,"speech":.05,"audio_peak":.20,"reaction":.10,"scene_change":.10},
    "reazioni": {"action":.10,"speech":.20,"audio_peak":.20,"reaction":.45,"scene_change":.05},
    "momento_migliore": {"action":.25,"speech":.15,"audio_peak":.20,"reaction":.30,"scene_change":.10},
}


def score_window(signal: WindowSignal, engine: str="automatico") -> float:
    s=signal.normalized()
    w=ENGINE_WEIGHTS.get(engine,ENGINE_WEIGHTS["automatico"])
    return sum(getattr(s,k)*v for k,v in w.items())


def _overlap(a: HighlightCandidate,b: HighlightCandidate) -> float:
    inter=max(0.0,min(a.end_seconds,b.end_seconds)-max(a.start_seconds,b.start_seconds))
    shorter=max(0.001,min(a.duration,b.duration))
    return inter/shorter


def rank_windows(signals: Iterable[WindowSignal], *, engine: str="automatico", limit: int=5,
                 max_overlap: float=.35) -> list[HighlightCandidate]:
    ranked=[]
    for raw in signals:
        s=raw.normalized()
        if s.end_seconds<=s.start_seconds:
            continue
        score=score_window(s,engine)
        reason=max(
            (("azione",s.action),("voce",s.speech),("picco audio",s.audio_peak),
             ("reazione",s.reaction),("cambio scena",s.scene_change)),
            key=lambda x:x[1]
        )[0]
        ranked.append(HighlightCandidate(s.start_seconds,s.end_seconds,score,reason,engine))
    ranked.sort(key=lambda c:c.score,reverse=True)
    selected=[]
    for candidate in ranked:
        if all(_overlap(candidate,old)<=max_overlap for old in selected):
            selected.append(candidate)
            if len(selected)>=max(1,int(limit)):
                break
    return selected
