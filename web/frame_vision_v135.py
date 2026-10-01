from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path


def sample_times(duration: float, moments=None, interval: float = 2.0, max_frames: int = 36):
    """Choose deterministic frame times, biased toward Director moments."""
    duration=max(0.0,float(duration or 0.0))
    points=set()
    for row in moments or []:
        if not isinstance(row,dict):
            continue
        t=max(0.0,min(duration,float(row.get("start",0.0) or 0.0)))
        points.update((max(0.0,t-.7),t,min(duration,t+.7)))
    if duration:
        step=max(.5,float(interval or 2.0))
        t=0.0
        while t<=duration and len(points)<max_frames:
            points.add(round(t,3)); t+=step
    return sorted(points)[:max_frames]


def extract_frames(video_path, out_dir, times, width=640):
    """Extract JPEG evidence frames with ffmpeg; no OpenCV dependency."""
    src=Path(video_path); out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    results=[]
    for i,t in enumerate(times):
        dst=out/f"vision_{i:03d}_{int(float(t)*1000):08d}.jpg"
        cmd=["ffmpeg","-hide_banner","-loglevel","error","-ss",f"{float(t):.3f}","-i",str(src),
             "-frames:v","1","-vf",f"scale={int(width)}:-2","-q:v","3","-y",str(dst)]
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if p.returncode==0 and dst.exists() and dst.stat().st_size>0:
            results.append({"time":round(float(t),3),"path":str(dst),"bytes":dst.stat().st_size})
    return results


def build_frame_manifest(video_path,duration,moments=None,out_dir=None):
    """Materialize a compact frame-evidence manifest for vision/OCR providers."""
    src=Path(video_path)
    target=Path(out_dir) if out_dir else src.parent/(src.stem+"_vision")
    times=sample_times(duration,moments)
    frames=extract_frames(src,target,times)
    manifest={
        "engine":"v135-frame-vision",
        "source":str(src),"duration":round(float(duration or 0.0),3),
        "sample_count":len(frames),"frames":frames,
        "capabilities":["game_recognition","hud_context","cover_selection","privacy_ocr","overlay_detection"],
        "provider_ready":True,
    }
    (target/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    return manifest
