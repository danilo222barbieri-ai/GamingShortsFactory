"""Two-pass selection orchestration for long live recordings."""
from __future__ import annotations
from typing import Callable, Iterable
from .live_scanner import WindowSignal, rank_windows
from .models import HighlightCandidate
from .refine import RefineConfig, dense_region, refine_candidate

DenseSignalLoader=Callable[[float,float],Iterable[WindowSignal]]

def two_pass_highlights(coarse_signals: Iterable[WindowSignal], *, dense_loader: DenseSignalLoader,
                        engine: str="automatico", limit: int=5, target_duration: int=30) -> list[HighlightCandidate]:
    coarse=rank_windows(coarse_signals,engine=engine,limit=limit)
    refined=[]
    cfg=RefineConfig(target_duration=float(target_duration),min_duration=min(15.0,float(target_duration)))
    for candidate in coarse:
        start,end=dense_region(candidate)
        dense=list(dense_loader(start,end))
        item=refine_candidate(dense,engine=engine,config=cfg)
        refined.append(item or candidate)
    refined.sort(key=lambda x:x.score,reverse=True)
    return refined[:max(1,int(limit))]
