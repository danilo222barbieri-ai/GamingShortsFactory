from __future__ import annotations

from pathlib import Path
import math

import numpy as np
from PIL import Image


def _clamp(v):
    try:
        return max(0.0,min(1.0,float(v)))
    except Exception:
        return 0.0


def _load(path,size=(192,108)):
    img=Image.open(path).convert("RGB")
    img.thumbnail(size,Image.Resampling.BILINEAR)
    arr=np.asarray(img,dtype=np.float32)/255.0
    return arr


def analyze_frame(path,previous=None):
    """Cheap local visual analysis: no network/model dependency."""
    arr=_load(path)
    gray=arr.mean(axis=2)
    brightness=float(gray.mean())
    contrast=_clamp(float(gray.std())/.22)
    gx=np.abs(np.diff(gray,axis=1)).mean() if gray.shape[1]>1 else 0.0
    gy=np.abs(np.diff(gray,axis=0)).mean() if gray.shape[0]>1 else 0.0
    sharpness=_clamp((float(gx)+float(gy))/.20)
    sat=(arr.max(axis=2)-arr.min(axis=2))
    saturation=_clamp(float(sat.mean())/.45)
    h,w=gray.shape
    y0,y1=max(0,int(h*.22)),min(h,int(h*.78))
    x0,x1=max(0,int(w*.22)),min(w,int(w*.78))
    center=gray[y0:y1,x0:x1]
    center_detail=_clamp((float(center.std()) if center.size else 0.0)/.22)
    exposure=1.0-min(1.0,abs(brightness-.52)/.52)
    motion=.0
    if previous is not None and isinstance(previous,np.ndarray) and previous.shape==arr.shape:
        motion=_clamp(float(np.abs(arr-previous).mean())/.20)
    subject=_clamp(.50*center_detail+.25*sharpness+.25*contrast)
    action=_clamp(.52*motion+.28*sharpness+.20*contrast)
    quality=_clamp(.26*sharpness+.22*contrast+.17*saturation+.18*subject+.17*exposure)
    labels=[]
    if action>=.62: labels.append("high_action")
    if subject>=.62: labels.append("strong_subject")
    if brightness<.15: labels.append("underexposed")
    if brightness>.90: labels.append("overexposed")
    return {
        "path":str(path),
        "labels":labels,
        "sharpness":round(sharpness,4),
        "contrast":round(contrast,4),
        "saturation":round(saturation,4),
        "subject_score":round(subject,4),
        "action_score":round(action,4),
        "brightness":round(brightness,4),
        "exposure_score":round(exposure,4),
        "visual_quality":round(quality,4),
        "_array":arr,
    }


def enrich_frame_manifest(manifest):
    """Produce provider-compatible visual observations for V137 consumers."""
    frames=[dict(x) for x in (dict(manifest or {}).get("frames") or []) if isinstance(x,dict)]
    out=[]; prev=None
    for row in frames:
        p=str(row.get("path") or "")
        if not p or not Path(p).is_file():
            continue
        try:
            obs=analyze_frame(p,previous=prev)
            prev=obs.pop("_array",None)
            obs["time"]=row.get("time")
            obs["ocr"]=[]
            out.append(obs)
        except Exception:
            continue
    return out


def best_visual_frame(manifest):
    rows=enrich_frame_manifest(manifest)
    if not rows:
        return {}
    return max(rows,key=lambda x:(
        float(x.get("visual_quality") or 0.0)*.52+
        float(x.get("action_score") or 0.0)*.30+
        float(x.get("subject_score") or 0.0)*.18
    ))
