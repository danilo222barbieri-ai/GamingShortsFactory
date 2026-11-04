#!/usr/bin/env python3
"""
Benchmark for Gaming Shorts Factory — AI Performance Engine 2.0 (Blocco 6).
Measures end-to-end latency on 15s, 30s, and 60s gameplay videos with:
- Adaptive fast_short scan (144px width, 2fps) + persistent disk/memory scan cache
- Singleton Whisper Tiny reuse (0.000s re-init penalty)
- Zero-subprocess precision boundary refinement (precision_refine_boundary)
- 3-worker parallel preview encode (scale=360:-2:flags=fast_bilinear, tune=zerolatency)
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "web"))

from tools.benchmark_blocco1 import (
    FFMPEG_PATH,
    generate_synthetic_gameplay,
    measure_audio_scan,
    measure_stream_parsing,
    measure_video_scan,
)
from ai_performance_engine_v2 import (
    get_cached_whisper_tiny,
    load_cached_scan,
    precision_refine_boundary,
    save_cached_scan,
    scan_profile_for_duration,
)
from game_vision_v108 import build_event_map


def measure_v2_preview_encode(video_path: str, start: float, duration: float, out_path: str) -> float:
    import subprocess
    t0 = time.perf_counter()
    cmd = [
        FFMPEG_PATH, "-y",
        "-ss", str(start),
        "-i", str(video_path),
        "-t", str(duration),
        "-vf", "scale=360:-2:flags=fast_bilinear",
        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-crf", "28", "-threads", "2",
        "-c:a", "aac", "-b:a", "96k",
        "-movflags", "+faststart",
        str(out_path),
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return time.perf_counter() - t0


def run_v2_benchmark(duration_s: float, clip_dur: float = 15.0):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        video_path = str(tmp_dir / f"gameplay_{int(duration_s)}s.mp4")
        generate_synthetic_gameplay(duration_s, video_path)

        prof = scan_profile_for_duration(duration_s)
        t_scan0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=2) as pool:
            f_aud = pool.submit(measure_audio_scan, video_path)
            f_vid = pool.submit(
                measure_video_scan,
                video_path,
                fps=float(prof["video_fps"]),
                width=int(prof["analysis_width"]),
            )
            _, raw_aud = f_aud.result()
            _, raw_vid = f_vid.result()
        parse_s, aud_pts, vid_pts = measure_stream_parsing(raw_aud, raw_vid)
        scan_wall_s = time.perf_counter() - t_scan0

        n_buckets = max(1, int(duration_s * 2))
        scan = {
            "step": 0.5,
            "audio": [float((aud_pts.get(i) or {}).get("rms", -30.0) + 60.0) / 60.0 for i in range(n_buckets)],
            "peak": [float((aud_pts.get(i) or {}).get("peak", -20.0) + 60.0) / 60.0 for i in range(n_buckets)],
            "motion": [float(vid_pts.get(i, 0.15)) for i in range(n_buckets)],
            "meta": {"duration_seconds": duration_s, "tier": prof["tier"]},
        }
        save_cached_scan(video_path, scan, preview_dir=tmp_dir)

        t_cache0 = time.perf_counter()
        _, hit = load_cached_scan(video_path, preview_dir=tmp_dir)
        cache_hit_s = time.perf_counter() - t_cache0

        t_whisp0 = time.perf_counter()
        _ = get_cached_whisper_tiny()
        whisper_reuse_s = time.perf_counter() - t_whisp0

        t_ev0 = time.perf_counter()
        _ = build_event_map(scan)
        events_s = time.perf_counter() - t_ev0

        starts = [0.0] if duration_s <= clip_dur else [0.0, max(0.0, (duration_s - clip_dur) / 2.0), max(0.0, duration_s - clip_dur)]
        t_ref0 = time.perf_counter()
        for s in starts:
            precision_refine_boundary(scan, s, min(clip_dur, duration_s), total_seconds=duration_s, genre="FPS")
        refine_s = time.perf_counter() - t_ref0

        t_prev0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=min(3, len(starts))) as pool:
            futs = [
                pool.submit(measure_v2_preview_encode, video_path, s, min(clip_dur, duration_s), str(tmp_dir / f"p_{i}.mp4"))
                for i, s in enumerate(starts)
            ]
            for f in as_completed(futs):
                f.result()
        preview_s = time.perf_counter() - t_prev0

        total_cold_s = scan_wall_s + events_s + refine_s + preview_s
        total_cached_s = cache_hit_s + events_s + refine_s + preview_s

        print(
            f"[{int(duration_s)}s video] "
            f"scan={scan_wall_s:.3f}s | cache_hit={cache_hit_s:.4f}s | whisper_reuse={whisper_reuse_s:.4f}s | "
            f"refine_v2={refine_s:.4f}s | previews_3w={preview_s:.3f}s | "
            f"TOTAL_FIRST_RUN={total_cold_s:.3f}s | TOTAL_CACHED_RUN={total_cached_s:.3f}s"
        )


if __name__ == "__main__":
    # Warm singleton once at process boot
    get_cached_whisper_tiny()
    for d in (15.0, 30.0, 60.0):
        run_v2_benchmark(d, clip_dur=15.0)
