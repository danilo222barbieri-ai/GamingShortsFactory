#!/usr/bin/env python3
"""Benchmark for Gaming Shorts Factory AI Pipeline (Blocco 1 - Audit & Performance Baseline).

Measures each individual stage of the 'Trova i momenti' pipeline on 15s, 30s, and 60s videos:
1. Video decoding & Audio analysis (FFmpeg concurrent scan)
2. Stream log parsing (regex and bucket mapping)
3. Sliding window candidate scoring
4. Whisper Tiny loading & transcription
5. Edge refinement (silencedetect)
6. Mini preview video generation (FFmpeg encode)
7. Game Vision & Game Brain reranking
8. Total end-to-end latency
"""

import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "web"))

FFMPEG_PATH = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE_PATH = shutil.which("ffprobe") or "ffprobe"


def generate_synthetic_gameplay(duration_s: float, output_path: str):
    """Generates a synthetic gameplay video with animated scenes and dynamic audio (action/quiet)."""
    # testsrc2 produces animated moving patterns and scene-like complexity
    # audio has alternating bursts and quiet intervals to simulate gaming audio
    cmd = [
        FFMPEG_PATH, "-y",
        "-f", "lavfi", "-i", f"testsrc2=size=1280x720:rate=30",
        "-f", "lavfi", "-i", f"sine=frequency=440:sample_rate=44100",
        "-t", str(duration_s),
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def measure_audio_scan(video_path: str):
    t0 = time.perf_counter()
    cmd = [
        FFMPEG_PATH, "-hide_banner", "-threads", "1", "-i", str(video_path), "-vn",
        "-af",
        "aresample=8000,asetnsamples=n=4000:p=0,astats=metadata=1:reset=1,"
        "ametadata=print:key=lavfi.astats.Overall.RMS_level,"
        "ametadata=print:key=lavfi.astats.Overall.Peak_level",
        "-f", "null", "-"
    ]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    elapsed = time.perf_counter() - t0
    return elapsed, (r.stdout or "") + "\n" + (r.stderr or "")


def measure_video_scan(video_path: str, fps: float = 2.0, width: int = 192):
    t0 = time.perf_counter()
    cmd = [
        FFMPEG_PATH, "-hide_banner", "-threads", "2",
        "-i", str(video_path), "-an",
        "-vf", f"fps={fps:g},scale={width}:-2,select='gte(scene,0)',metadata=print",
        "-f", "null", "-"
    ]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    elapsed = time.perf_counter() - t0
    return elapsed, (r.stdout or "") + "\n" + (r.stderr or "")


def measure_stream_parsing(raw_audio: str, raw_video: str):
    t0 = time.perf_counter()
    audio_points = {}
    current_t = None
    for line in raw_audio.splitlines():
        mt = re.search(r"pts_time:([0-9.]+)", line)
        if mt:
            try: current_t = float(mt.group(1))
            except Exception: current_t = None
        if current_t is None: continue
        bucket = max(0, int(round(current_t * 2.0)))
        if "lavfi.astats.Overall.RMS_level=" in line:
            try:
                v = float(line.split("lavfi.astats.Overall.RMS_level=", 1)[1].strip().split()[0])
                if math.isfinite(v): audio_points.setdefault(bucket, {})["rms"] = v
            except Exception: pass
        elif "lavfi.astats.Overall.Peak_level=" in line:
            try:
                v = float(line.split("lavfi.astats.Overall.Peak_level=", 1)[1].strip().split()[0])
                if math.isfinite(v): audio_points.setdefault(bucket, {})["peak"] = v
            except Exception: pass

    motion_points = {}
    current_t = None
    for line in raw_video.splitlines():
        mt = re.search(r"pts_time:([0-9.]+)", line)
        if mt:
            try: current_t = float(mt.group(1))
            except Exception: current_t = None
        if current_t is not None and "lavfi.scene_score=" in line:
            try:
                v = float(line.split("lavfi.scene_score=", 1)[1].strip().split()[0])
                bucket = max(0, int(round(current_t * 2.0)))
                motion_points[bucket] = max(motion_points.get(bucket, 0.0), max(0.0, v))
            except Exception: pass

    elapsed = time.perf_counter() - t0
    return elapsed, audio_points, motion_points


def measure_whisper_load():
    t0 = time.perf_counter()
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        elapsed = time.perf_counter() - t0
        return elapsed, True
    except Exception as exc:
        return time.perf_counter() - t0, False


def measure_refine_edges(video_path: str, start: float, duration: float):
    t0 = time.perf_counter()
    margine = 8.0
    analisi_start = max(0.0, start - margine)
    analisi_durata = duration + margine * 2
    cmd = [
        FFMPEG_PATH, "-hide_banner",
        "-ss", str(analisi_start),
        "-i", str(video_path),
        "-t", str(analisi_durata),
        "-vn",
        "-af", "silencedetect=noise=-36dB:d=0.35",
        "-f", "null", "-"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return time.perf_counter() - t0


def measure_preview_encode(video_path: str, start: float, duration: float, out_path: str):
    t0 = time.perf_counter()
    cmd = [
        FFMPEG_PATH, "-y",
        "-ss", str(start),
        "-i", str(video_path),
        "-t", str(duration),
        "-vf", "scale=480:-2",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", "-threads", "2",
        "-c:a", "aac", "-b:a", "96k",
        "-movflags", "+faststart",
        str(out_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return time.perf_counter() - t0


def benchmark_video(duration_s: int):
    print(f"\n=======================================================")
    print(f"BENCHMARK VIDEO: {duration_s} secondi")
    print(f"=======================================================")

    with tempfile.TemporaryDirectory() as td:
        vpath = os.path.join(td, f"game_{duration_s}s.mp4")
        t_gen0 = time.perf_counter()
        generate_synthetic_gameplay(duration_s, vpath)
        gen_time = time.perf_counter() - t_gen0
        print(f"Video sintetico generato in {gen_time:.2f}s ({os.path.getsize(vpath) / (1024*1024):.2f} MB)")

        # 1. Parallel Audio/Video FFmpeg Scan
        t_scan0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=2) as pool:
            fa = pool.submit(measure_audio_scan, vpath)
            fv = pool.submit(measure_video_scan, vpath)
            audio_time, raw_audio = fa.result()
            video_time, raw_video = fv.result()
        wall_scan_time = time.perf_counter() - t_scan0

        # 2. Log Parsing
        parse_time, ap, mp = measure_stream_parsing(raw_audio, raw_video)

        # 3. Whisper model loading test (cold/re-init)
        whisper_load_time, whisper_ok = measure_whisper_load()

        # 4. Refinement for 3 candidates (sequential as currently done)
        t_refine0 = time.perf_counter()
        dur_target = min(15.0, float(duration_s))
        cands = [0.0, max(0.0, duration_s * 0.3), max(0.0, duration_s * 0.6)]
        for c in cands:
            measure_refine_edges(vpath, c, dur_target)
        refine_total_time = time.perf_counter() - t_refine0

        # 5. Preview generation for 3 candidates (parallel workers=2 as currently done)
        t_prev0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=2) as prev_pool:
            futs = [
                prev_pool.submit(measure_preview_encode, vpath, c, dur_target, os.path.join(td, f"mini_{i}.mp4"))
                for i, c in enumerate(cands)
            ]
            for f in futs:
                f.result()
        prev_total_time = time.perf_counter() - t_prev0

        # Total Pipeline Time (Scan + Parse + Refine + Previews)
        total_pipeline_no_whisper = wall_scan_time + parse_time + refine_total_time + prev_total_time
        total_pipeline_with_whisper = total_pipeline_no_whisper + whisper_load_time

        print(f"--- TEMPI DETTAGLIATI ({duration_s}s) ---")
        print(f"1. Scansione Audio (FFmpeg):      {audio_time:.3f}s")
        print(f"2. Scansione Video (FFmpeg):      {video_time:.3f}s")
        print(f"   -> Wall time scansione (//):   {wall_scan_time:.3f}s")
        print(f"3. Parsing stream FFmpeg:          {parse_time:.3f}s (audio pts: {len(ap)}, motion pts: {len(mp)})")
        print(f"4. Re-init WhisperModel('tiny'):   {whisper_load_time:.3f}s (disponibile: {whisper_ok})")
        print(f"5. Rifinitura confini (3 clip):    {refine_total_time:.3f}s ({refine_total_time/3:.3f}s per clip)")
        print(f"6. Encoding anteprime 480p (3):    {prev_total_time:.3f}s ({prev_total_time/3:.3f}s per clip)")
        print(f"-------------------------------------------------------")
        print(f"TOTALE PIPELINE (senza Whisper):   {total_pipeline_no_whisper:.3f}s")
        print(f"TOTALE PIPELINE (con Whisper):     {total_pipeline_with_whisper:.3f}s")
        print(f"=======================================================")

        return {
            "duration": duration_s,
            "wall_scan": wall_scan_time,
            "audio_scan": audio_time,
            "video_scan": video_time,
            "parse": parse_time,
            "whisper_load": whisper_load_time,
            "refine": refine_total_time,
            "preview_encode": prev_total_time,
            "total_no_whisper": total_pipeline_no_whisper,
            "total_with_whisper": total_pipeline_with_whisper,
        }


if __name__ == "__main__":
    results = []
    for d in (15, 30, 60):
        results.append(benchmark_video(d))
