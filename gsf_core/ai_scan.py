"""GSF Core AI Scan Engine.

Decoupled, reusable audio and video scan pipeline used by both
the web application and background worker services without requiring
Streamlit dependencies or AST extraction.
"""
from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


def find_ffmpeg() -> str:
    """Find FFmpeg binary from environment or standard search paths."""
    env = os.environ.get("FFMPEG_BINARY") or os.environ.get("FFMPEG_PATH")
    if env and shutil.which(env):
        return env
    found = shutil.which("ffmpeg")
    return found or "ffmpeg"


def find_ffprobe() -> str:
    """Find FFprobe binary from environment or standard search paths."""
    env = os.environ.get("FFPROBE_BINARY") or os.environ.get("FFPROBE_PATH")
    if env and shutil.which(env):
        return env
    found = shutil.which("ffprobe")
    return found or "ffprobe"


def get_video_duration(file_path: str | Path, ffprobe_bin: Optional[str] = None) -> float:
    """Extract video duration in seconds via ffprobe or ffmpeg."""
    probe = ffprobe_bin or find_ffprobe()
    try:
        res = subprocess.run(
            [
                probe,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(file_path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=25,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            val = float(res.stdout.strip())
            if math.isfinite(val) and val > 0:
                return val
    except Exception:
        pass
    return 0.0


def source_has_audio(file_path: str | Path, ffprobe_bin: Optional[str] = None) -> bool:
    """Return True when the source exposes at least one audio stream."""
    probe = ffprobe_bin or find_ffprobe()
    try:
        res = subprocess.run(
            [
                probe,
                "-v", "error",
                "-select_streams", "a:0",
                "-show_entries", "stream=index",
                "-of", "csv=p=0",
                str(file_path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            check=False,
        )
        return bool(res.returncode == 0 and res.stdout.strip())
    except Exception:
        return False


def gsf_norm_series(values: Sequence[float]) -> List[float]:
    """Normalize a series between 0.0 and 1.0 using 5th and 95th percentiles."""
    if not values:
        return []
    vals = [float(v) for v in values]
    ordered = sorted(vals)
    lo = ordered[max(0, int(len(ordered) * 0.05) - 1)]
    hi = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    span = max(1e-6, hi - lo)
    return [max(0.0, min(1.0, (v - lo) / span)) for v in vals]


def gsf_ai_scan_profile_for_duration(total_seconds: float) -> Dict[str, Any]:
    """Adaptive full-video scan profile adjusting frame rate and resolution."""
    total = max(0.0, float(total_seconds or 0.0))
    if total <= 3 * 60:
        return {
            "tier": "standard",
            "video_fps": 2.0,
            "analysis_width": 192,
            "adaptive": False,
            "keyframes_only": False,
        }
    if total <= 20 * 60:
        return {
            "tier": "medium_turbo",
            "video_fps": 0.5,
            "analysis_width": 128,
            "adaptive": True,
            "keyframes_only": True,
        }
    if total <= 60 * 60:
        return {
            "tier": "long_turbo",
            "video_fps": 0.35,
            "analysis_width": 112,
            "adaptive": True,
            "keyframes_only": True,
        }
    return {
        "tier": "very_long_turbo",
        "video_fps": 0.25,
        "analysis_width": 112,
        "adaptive": True,
        "keyframes_only": True,
    }


def gsf_interpolate_motion_points(points: Mapping[int, float], n: int) -> List[float]:
    """Interpolate sparse adaptive visual samples onto the 0.5 s AI grid."""
    n = max(0, int(n))
    if n <= 0:
        return []
    if not points:
        return [0.0] * n

    known = sorted(
        (max(0, int(k)), float(v))
        for k, v in points.items()
        if 0 <= int(k) < n
    )
    if not known:
        return [0.0] * n

    out = [0.0] * n
    first_i, first_v = known[0]
    for i in range(0, min(n, first_i + 1)):
        out[i] = first_v

    for idx in range(len(known) - 1):
        i0, v0 = known[idx]
        i1, v1 = known[idx + 1]
        if i1 <= i0:
            continue
        span = float(i1 - i0)
        for i in range(i0, min(n, i1 + 1)):
            alpha = (i - i0) / span
            out[i] = v0 * (1.0 - alpha) + v1 * alpha

    last_i, last_v = known[-1]
    for i in range(max(0, last_i), n):
        out[i] = last_v
    return out


def gsf_ai_scan_base(
    input_file: str | Path,
    ffmpeg_bin: Optional[str] = None,
    ffprobe_bin: Optional[str] = None,
) -> Dict[str, Any]:
    """Whole-game video & audio scan producing synchronized 0.5s highlight signals."""
    scan_t0 = time.perf_counter()
    ffmpeg = ffmpeg_bin or find_ffmpeg()
    ffprobe = ffprobe_bin or find_ffprobe()

    total_seconds = get_video_duration(input_file, ffprobe_bin=ffprobe)
    profile = gsf_ai_scan_profile_for_duration(total_seconds)
    video_fps = float(profile["video_fps"])
    analysis_width = int(profile["analysis_width"])
    keyframes_only = bool(profile.get("keyframes_only"))

    cmd_audio = [
        ffmpeg, "-hide_banner", "-threads", "1", "-i", str(input_file), "-vn",
        "-af",
        (
            "aresample=8000,asetnsamples=n=4000:p=0,"
            "astats=metadata=1:reset=1,"
            "ametadata=print:key=lavfi.astats.Overall.RMS_level,"
            "ametadata=print:key=lavfi.astats.Overall.Peak_level"
        ),
        "-f", "null", "-",
    ]

    cmd_video = [
        ffmpeg, "-hide_banner", "-threads", "1", "-i", str(input_file), "-an",
        "-vf",
    ]
    if keyframes_only:
        cmd_video.append(f"scale={analysis_width}:-2,select='gte(scene,0)',metadata=print")
    else:
        cmd_video.append(f"fps={video_fps:g},scale={analysis_width}:-2,select='gte(scene,0)',metadata=print")
    cmd_video.extend(["-f", "null", "-"])

    has_audio = source_has_audio(input_file, ffprobe_bin=ffprobe)

    def run_capture(cmd: Sequence[str]) -> Tuple[Optional[subprocess.CompletedProcess], float, str]:
        t0 = time.perf_counter()
        try:
            r = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=max(180.0, min(7200.0, total_seconds * 2.0)),
                check=False,
            )
            error = ""
            if r.returncode != 0 and (cmd is cmd_video or has_audio):
                error = "Scansione " + ("video" if cmd is cmd_video else "audio") + " non riuscita"
            return r, time.perf_counter() - t0, error
        except Exception as e:
            return None, time.perf_counter() - t0, str(e)

    with ThreadPoolExecutor(max_workers=2) as pool:
        fa = pool.submit(run_capture, cmd_audio)
        fv = pool.submit(run_capture, cmd_video)
        ra, audio_seconds, audio_error = fa.result()
        rv, video_seconds, video_error = fv.result()

    raw_audio = ""
    if ra is not None:
        raw_audio = (ra.stdout or "") + "\n" + (ra.stderr or "")

    raw_video = ""
    if rv is not None:
        raw_video = (rv.stdout or "") + "\n" + (rv.stderr or "")

    audio_points: Dict[int, Dict[str, float]] = {}
    current_t: Optional[float] = None
    for line in raw_audio.splitlines():
        mt = re.search(r"pts_time:([0-9.]+)", line)
        if mt:
            try:
                current_t = float(mt.group(1))
            except Exception:
                current_t = None
        if current_t is None:
            continue

        bucket = max(0, int(round(current_t * 2.0)))
        if "lavfi.astats.Overall.RMS_level=" in line:
            try:
                v = float(line.split("lavfi.astats.Overall.RMS_level=", 1)[1].strip().split()[0])
                if math.isfinite(v):
                    audio_points.setdefault(bucket, {})["rms"] = v
            except Exception:
                pass
        elif "lavfi.astats.Overall.Peak_level=" in line:
            try:
                v = float(line.split("lavfi.astats.Overall.Peak_level=", 1)[1].strip().split()[0])
                if math.isfinite(v):
                    audio_points.setdefault(bucket, {})["peak"] = v
            except Exception:
                pass

    motion_points: Dict[int, float] = {}
    current_t = None
    for line in raw_video.splitlines():
        mt = re.search(r"pts_time:([0-9.]+)", line)
        if mt:
            try:
                current_t = float(mt.group(1))
            except Exception:
                current_t = None

        if current_t is not None and "lavfi.scene_score=" in line:
            try:
                v = float(line.split("lavfi.scene_score=", 1)[1].strip().split()[0])
                bucket = max(0, int(round(current_t * 2.0)))
                motion_points[bucket] = max(motion_points.get(bucket, 0.0), max(0.0, v))
            except Exception:
                pass

    all_buckets = set(audio_points) | set(motion_points)
    if total_seconds > 0:
        all_buckets.add(max(0, int(math.ceil(total_seconds * 2.0)) - 1))

    meta = {
        "parallel": True,
        "tier": profile["tier"],
        "adaptive": bool(profile["adaptive"]),
        "video_fps": video_fps,
        "analysis_width": analysis_width,
        "keyframes_only": keyframes_only,
        "duration_seconds": round(total_seconds, 2),
        "audio_seconds": round(float(audio_seconds), 3),
        "video_seconds": round(float(video_seconds), 3),
        "wall_seconds": round(time.perf_counter() - scan_t0, 3),
        "audio_error": audio_error,
        "video_error": video_error,
    }

    if not all_buckets:
        return {
            "step": 0.5,
            "audio": [],
            "peak": [],
            "motion": [],
            "meta": meta,
        }

    n = max(all_buckets) + 2
    rms_raw: List[float] = []
    peak_raw: List[float] = []
    last_rms = -80.0
    last_peak = -80.0

    for i in range(n):
        ap = audio_points.get(i, {})
        r = ap.get("rms", last_rms)
        p = ap.get("peak", last_peak)
        last_rms = r
        last_peak = p
        rms_raw.append(r)
        peak_raw.append(p)

    motion_raw = gsf_interpolate_motion_points(motion_points, n)

    audio = gsf_norm_series(rms_raw)
    peak = gsf_norm_series(peak_raw)
    motion = gsf_norm_series(motion_raw)

    return {
        "step": 0.5,
        "audio": audio,
        "peak": peak,
        "motion": motion,
        "meta": meta,
    }


# Backward compatibility aliases
_gsf_norm_series = gsf_norm_series
_gsf_ai_scan_profile_for_duration = gsf_ai_scan_profile_for_duration
_gsf_interpolate_motion_points = gsf_interpolate_motion_points
_gsf_ai_scan_base = gsf_ai_scan_base
