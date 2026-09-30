from __future__ import annotations

import json
import math
import re
import subprocess
import time
from pathlib import Path


ENGINE_VERSION="v124-quality-control"


def _num(value,default=0.0):
    try:
        value=float(value)
        return value if math.isfinite(value) else float(default)
    except Exception:
        return float(default)


def _ffprobe(path):
    cmd=[
        "/usr/bin/ffprobe","-v","error",
        "-show_streams","-show_format",
        "-of","json",
        str(path),
    ]
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=20,check=False)
    if proc.returncode!=0:
        raise RuntimeError((proc.stderr or "ffprobe failed")[-300:])
    payload=json.loads(proc.stdout or "{}")
    return payload if isinstance(payload,dict) else {}


def _parse_rate(value):
    raw=str(value or "0/1")
    try:
        if "/" in raw:
            a,b=raw.split("/",1)
            b=float(b or 1)
            return float(a)/b if b else 0.0
        return float(raw)
    except Exception:
        return 0.0


def _black_detect(path,duration):
    cmd=[
        "/usr/bin/ffmpeg","-hide_banner","-loglevel","info",
        "-i",str(path),
        "-vf","blackdetect=d=0.18:pix_th=0.10",
        "-an","-f","null","-",
    ]
    try:
        proc=subprocess.run(cmd,capture_output=True,text=True,timeout=max(20,min(60,int(duration*2)+15)),check=False)
        text=(proc.stderr or "")+"\n"+(proc.stdout or "")
    except Exception:
        return {"black_seconds":0.0,"black_ratio":0.0,"segments":[]}
    segments=[]
    total=0.0
    for match in re.finditer(r"black_start:([0-9.]+)\s+black_end:([0-9.]+)\s+black_duration:([0-9.]+)",text):
        start,end,span=(float(match.group(1)),float(match.group(2)),float(match.group(3)))
        segments.append({"start":round(start,3),"end":round(end,3),"duration":round(span,3)})
        total+=span
    ratio=total/max(.001,float(duration or 0.0))
    return {
        "black_seconds":round(total,3),
        "black_ratio":round(max(0.0,min(1.0,ratio)),4),
        "segments":segments[:12],
    }


def _audio_detect(path,duration):
    cmd=[
        "/usr/bin/ffmpeg","-hide_banner","-loglevel","info",
        "-i",str(path),
        "-af","volumedetect",
        "-vn","-f","null","-",
    ]
    try:
        proc=subprocess.run(cmd,capture_output=True,text=True,timeout=max(20,min(60,int(duration*2)+15)),check=False)
        text=(proc.stderr or "")+"\n"+(proc.stdout or "")
    except Exception:
        return {}
    def find(pattern):
        m=re.search(pattern,text)
        return float(m.group(1)) if m else None
    return {
        "mean_db":find(r"mean_volume:\s*(-?[0-9.]+) dB"),
        "max_db":find(r"max_volume:\s*(-?[0-9.]+) dB"),
    }


def inspect_final_video(path):
    source=Path(path)
    started=time.time()
    report={
        "engine":ENGINE_VERSION,
        "status":"error",
        "score":0,
        "issues":[],
        "warnings":[],
        "facts":{},
        "checked_at":started,
    }
    if not source.is_file() or source.stat().st_size<=1024:
        report["issues"].append("final_missing_or_empty")
        return report

    try:
        probe=_ffprobe(source)
    except Exception as exc:
        report["issues"].append("probe_failed")
        report["error"]=str(exc)[:220]
        return report

    streams=list(probe.get("streams") or [])
    video=next((x for x in streams if x.get("codec_type")=="video"),{})
    audio=next((x for x in streams if x.get("codec_type")=="audio"),{})
    fmt=probe.get("format") or {}

    width=int(_num(video.get("width"),0))
    height=int(_num(video.get("height"),0))
    duration=max(
        _num(fmt.get("duration"),0.0),
        _num(video.get("duration"),0.0),
        _num(audio.get("duration"),0.0),
    )
    fps=_parse_rate(video.get("avg_frame_rate") or video.get("r_frame_rate"))
    vcodec=str(video.get("codec_name") or "")
    acodec=str(audio.get("codec_name") or "")
    size=int(source.stat().st_size)
    aspect=(float(width)/float(height)) if width and height else 0.0

    facts={
        "size_bytes":size,
        "width":width,
        "height":height,
        "aspect":round(aspect,4),
        "duration":round(duration,3),
        "fps":round(fps,3),
        "video_codec":vcodec,
        "audio_codec":acodec,
        "has_audio":bool(audio),
        "is_vertical":bool(height>width),
    }

    issues=[]
    warnings=[]
    if not video:
        issues.append("video_stream_missing")
    if duration<4.5:
        issues.append("duration_too_short")
    elif duration>61.0:
        warnings.append("duration_over_short_limit")
    if width<540 or height<960:
        warnings.append("resolution_low")
    if vcodec not in ("h264","hevc","av1","vp9"):
        warnings.append("video_codec_unusual")
    if fps and (fps<23 or fps>61.5):
        warnings.append("fps_unusual")
    if width and height and not (height>width):
        warnings.append("not_vertical")
    if not audio:
        warnings.append("audio_missing")

    black=_black_detect(source,duration)
    facts.update(black)
    if black.get("black_ratio",0.0)>.14:
        issues.append("too_many_black_frames")
    elif black.get("black_ratio",0.0)>.05:
        warnings.append("black_frames_detected")

    audio_stats=_audio_detect(source,duration) if audio else {}
    facts["audio"]=audio_stats
    max_db=audio_stats.get("max_db") if audio_stats else None
    mean_db=audio_stats.get("mean_db") if audio_stats else None
    if max_db is not None and max_db>-0.05:
        warnings.append("audio_near_clipping")
    if mean_db is not None and mean_db<-42:
        warnings.append("audio_very_low")

    # Explainable score, intentionally conservative. Warnings reduce score but
    # never block publishing unless the file is genuinely broken.
    score=100
    score-=35*len(issues)
    score-=7*len(warnings)
    score=max(0,min(100,score))
    status="pass" if not issues and score>=86 else ("warn" if not issues else "fail")

    report.update({
        "status":status,
        "score":int(score),
        "issues":issues,
        "warnings":warnings,
        "facts":facts,
        "elapsed_seconds":round(time.time()-started,3),
    })
    return report
