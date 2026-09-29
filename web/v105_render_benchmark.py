#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import tempfile
import threading
import time
from pathlib import Path

FFMPEG=os.environ.get("GSF_BENCH_FFMPEG","/usr/bin/ffmpeg")
FFPROBE=os.environ.get("GSF_BENCH_FFPROBE","/usr/bin/ffprobe")
CGROUP_MEMORY=Path("/sys/fs/cgroup/memory.current")

_BASE={
    "crf":14,
    "pix_fmt":"yuv420p",
    "profile":"high",
    "level":"4.2",
    "audio_bitrate":"192k",
    "audio_rate":48000,
    "audio_channels":2,
    "fpsmax":60,
    "x264_params":"rc-lookahead=16:ref=2:bframes=2",
}
PROFILES={
    "medium_crf14_t1":dict(_BASE,preset="medium",threads=1),
    "medium_crf14_t2":dict(_BASE,preset="medium",threads=2),
    "fast_crf14_t2":dict(_BASE,preset="fast",threads=2),
}


def describe_process_failure(returncode,stderr=b""):
    import signal
    rc=int(returncode)
    tail=(stderr or b"")[-800:].decode("utf-8","replace").strip()
    if rc<0:
        signum=-rc
        try:
            signame=signal.Signals(signum).name
        except Exception:
            signame=f"SIGNAL_{signum}"
        base=f"returncode={rc} ({signame})"
    else:
        base=f"returncode={rc}"
    if tail:
        base+=" stderr="+tail
    return base

def synthetic_fixture_command(output,duration=15):
    return [
        FFMPEG,"-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i","testsrc2=size=1920x1080:rate=60",
        "-f","lavfi","-i","sine=frequency=523:sample_rate=48000",
        "-t",str(float(duration)),"-shortest",
        "-c:v","libx264","-preset","ultrafast","-crf","18","-threads","2",
        "-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",
        "-movflags","+faststart",str(output),
    ]


def _ratio(value):
    try:
        a,b=str(value or "0/1").split("/",1)
        b=float(b)
        return float(a)/b if b else 0.0
    except Exception:
        return 0.0


def probe_master(path):
    cmd=[
        FFPROBE,"-v","error",
        "-show_entries",
        "stream=codec_type,codec_name,codec_tag_string,profile,level,pix_fmt,width,height,avg_frame_rate,r_frame_rate,sample_rate,channels:format=duration,size,bit_rate",
        "-of","json",str(path),
    ]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
    if r.returncode!=0:
        return {"ok":False,"errors":[(r.stderr or "ffprobe failed")[-500:]]}

    data=json.loads(r.stdout or "{}")
    streams=data.get("streams") or []
    video=next((x for x in streams if x.get("codec_type")=="video"),{})
    audio=next((x for x in streams if x.get("codec_type")=="audio"),{})
    errors=[]

    if str(video.get("codec_name","")).lower()!="h264":
        errors.append("video codec")
    if str(video.get("codec_tag_string","")).lower()!="avc1":
        errors.append("video tag")
    if str(video.get("profile","")).lower()!="high":
        errors.append("profile")
    if str(video.get("pix_fmt","")).lower() not in ("yuv420p","yuvj420p"):
        errors.append("pixel format")
    if (int(video.get("width") or 0),int(video.get("height") or 0))!=(1080,1920):
        errors.append("resolution")

    fps=max(_ratio(video.get("avg_frame_rate")),_ratio(video.get("r_frame_rate")))
    if fps<=0 or fps>60.05:
        errors.append("fps")

    if str(audio.get("codec_name","")).lower()!="aac":
        errors.append("audio codec")
    if int(audio.get("sample_rate") or 0)!=48000:
        errors.append("audio rate")
    if int(audio.get("channels") or 0)!=2:
        errors.append("audio channels")

    return {
        "ok":not errors,
        "errors":errors,
        "fps":round(fps,3),
        "video":video,
        "audio":audio,
        "format":data.get("format") or {},
    }


def _memory_current():
    try:
        return int(CGROUP_MEMORY.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def _monitor_peak(stop,box):
    peak=_memory_current() or 0
    while not stop.is_set():
        cur=_memory_current()
        if cur is not None:
            peak=max(peak,cur)
        stop.wait(0.05)
    cur=_memory_current()
    if cur is not None:
        peak=max(peak,cur)
    box["peak_bytes"]=peak or None


def render_command(source,output,profile):
    cfg=PROFILES[profile]
    vf=(
        "crop=w='max(2,trunc((ih*9/16)/2)*2)':"
        "h='max(2,trunc(ih/2)*2)':x='max(0,(iw-ow)/2)':y=0,"
        "scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int,"
        "unsharp=5:5:0.08:3:3:0.02"
    )
    return [
        FFMPEG,"-hide_banner","-loglevel","error","-y",
        "-i",str(source),"-vf",vf,
        "-c:v","libx264",
        "-preset",str(cfg["preset"]),
        "-crf",str(cfg["crf"]),
        "-threads",str(cfg["threads"]),
        "-x264-params",str(cfg["x264_params"]),
        "-profile:v",str(cfg["profile"]),
        "-level:v",str(cfg["level"]),
        "-tag:v","avc1",
        "-pix_fmt",str(cfg["pix_fmt"]),
        "-fpsmax",str(cfg["fpsmax"]),
        "-c:a","aac",
        "-b:a",str(cfg["audio_bitrate"]),
        "-ar",str(cfg["audio_rate"]),
        "-ac",str(cfg["audio_channels"]),
        "-movflags","+faststart",
        str(output),
    ]


def _ssim(reference,candidate):
    cmd=[
        FFMPEG,"-hide_banner","-i",str(reference),"-i",str(candidate),
        "-lavfi","[0:v][1:v]ssim","-f","null","-",
    ]
    try:
        r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=300)
        text=(r.stderr or "")[-8000:]
        m=re.findall(r"All:([0-9.]+)",text)
        return float(m[-1]) if m else None
    except Exception:
        return None


def run_profile(source,output,profile,timeout=900):
    stop=threading.Event()
    box={}
    watcher=threading.Thread(target=_monitor_peak,args=(stop,box),daemon=True)
    watcher.start()
    t0=time.perf_counter()
    try:
        r=subprocess.run(
            render_command(source,output,profile),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            timeout=timeout,
        )
        elapsed=time.perf_counter()-t0
    finally:
        stop.set()
        watcher.join(timeout=2)

    ok=r.returncode==0 and Path(output).is_file() and Path(output).stat().st_size>0
    probe=probe_master(output) if ok else {"ok":False,"errors":["render failed"]}
    return {
        "profile":profile,
        "returncode":int(r.returncode),
        "elapsed_seconds":round(elapsed,3),
        "peak_memory_bytes":box.get("peak_bytes"),
        "output_bytes":Path(output).stat().st_size if ok else 0,
        "master":probe,
        "stderr_tail":"" if ok else (r.stderr or b"")[-1200:].decode("utf-8","replace"),
    }


def run_benchmark(durations=(15,30),workdir=None):
    own=None
    if workdir is None:
        own=tempfile.TemporaryDirectory(prefix="gsf_v105_bench_")
        root=Path(own.name)
    else:
        root=Path(workdir)
        root.mkdir(parents=True,exist_ok=True)

    results=[]
    try:
        for duration in durations:
            fixture=root/f"fixture_{int(duration)}s.mp4"
            fr=subprocess.run(
                synthetic_fixture_command(fixture,duration),
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=max(180,int(duration)*12)
            )
            if fr.returncode!=0:
                raise RuntimeError(
                    "fixture generation failed: "
                    +describe_process_failure(fr.returncode,fr.stderr)
                )

            by_name={}
            for profile in PROFILES:
                out=root/f"{profile}_{int(duration)}s.mp4"
                row=run_profile(fixture,out,profile,timeout=max(300,int(duration)*30))
                row["duration_seconds"]=float(duration)
                by_name[profile]=(row,out)
                results.append(row)

            baseline=by_name["medium_crf14_t1"][1]
            for profile,(row,out) in by_name.items():
                row["ssim_vs_baseline"]=1.0 if profile=="medium_crf14_t1" else _ssim(baseline,out)
                print("GSF_BENCHMARK "+json.dumps(row,separators=(",",":"),ensure_ascii=False),flush=True)

        return results
    finally:
        if own is not None:
            own.cleanup()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--durations",default="15,30")
    parser.add_argument("--workdir",default="")
    args=parser.parse_args()
    durations=tuple(float(x) for x in args.durations.split(",") if x.strip())
    results=run_benchmark(durations,workdir=(args.workdir or None))
    print("GSF_BENCHMARK_SUMMARY "+json.dumps(results,separators=(",",":"),ensure_ascii=False),flush=True)


if __name__=="__main__":
    main()
