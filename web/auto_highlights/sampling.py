"""Sampling plan for long VODs.

Pass 1 is deliberately sparse; promising regions can later receive a denser
second pass before any final render.
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SampleWindow:
    start_seconds: float
    duration_seconds: float

def sparse_sampling_plan(total_seconds: float, *, sample_seconds: int=8, every_seconds: int=30) -> list[SampleWindow]:
    total=max(0.0,float(total_seconds))
    sample=max(2,int(sample_seconds))
    step=max(sample,int(every_seconds))
    out=[]
    t=0.0
    while t<total:
        out.append(SampleWindow(t,min(float(sample),total-t)))
        t+=step
    return out

def estimated_sample_ratio(*, sample_seconds: int=8, every_seconds: int=30) -> float:
    return min(1.0,max(0.0,float(sample_seconds)/max(float(every_seconds),1.0)))
