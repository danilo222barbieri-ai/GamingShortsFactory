#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import v105_render_benchmark as bench

FFMPEG="/usr/bin/ffmpeg"
FFPROBE="/usr/bin/ffprobe"
RENDER_PROFILE="medium_crf14_t1"

CASES={
    "landscape_1080p30_48k_stereo":{
        "size":"1920x1080","fps":30,"duration":3.0,"audio":True,"sample_rate":48000,"channels":2,
    },
    "landscape_1080p60_44k_mono":{
        "size":"1920x1080","fps":60,"duration":3.0,"audio":True,"sample_rate":44100,"channels":1,
    },
    "landscape_1440p60_no_audio":{
        "size":"2560x1440","fps":60,"duration":3.0,"audio":False,"sample_rate":0,"channels":0,
    },
    "portrait_1080x1920_60":{
        "size":"1080x1920","fps":60,"duration":3.0,"audio":True,"sample_rate":48000,"channels":2,
    },
    "rotated_iphone_1080p60":{
        "size":"1920x1080","fps":60,"duration":3.0,"audio":True,"sample_rate":48000,"channels":2,"rotate":90,
    },
    "vfr_1080p":{
        "size":"1920x1080","fps":60,"duration":3.0,"audio":True,"sample_rate":48000,"channels":2,"vfr":True,
    },
}


def _run(cmd,timeout=180):
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    if r.returncode!=0:
        raise RuntimeError(bench.describe_process_failure(r.returncode,r.stderr))
    return r


def build_source(name,path):
    cfg=CASES[name]
    cmd=[
        FFMPEG,"-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i",f"testsrc2=size={cfg['size']}:rate={cfg['fps']}",
    ]
    if cfg.get("audio"):
        cmd += [
            "-f","lavfi","-i",
            f"sine=frequency=659:sample_rate={int(cfg['sample_rate'])}",
        ]

    if cfg.get("vfr"):
        cmd += [
            "-vf",
            "select='if(lt(mod(t,1),0.5),not(mod(n,2)),1)'",
            "-fps_mode","vfr",
        ]

    cmd += [
        "-t",str(float(cfg["duration"])),
    ]
    if cfg.get("audio"):
        cmd += ["-shortest"]

    cmd += [
        "-c:v","libx264","-preset","ultrafast","-crf","28",
        "-threads","1","-pix_fmt","yuv420p",
    ]
    if cfg.get("rotate"):
        cmd += ["-metadata:s:v:0",f"rotate={int(cfg['rotate'])}"]

    if cfg.get("audio"):
        cmd += [
            "-c:a","aac","-b:a","128k",
            "-ar",str(int(cfg["sample_rate"])),
            "-ac",str(int(cfg["channels"])),
        ]
    cmd += ["-movflags","+faststart",str(path)]
    _run(cmd,timeout=180)
    return Path(path)


def probe_source(path):
    cmd=[
        FFPROBE,"-v","error",
        "-show_entries",
        "stream=codec_type,codec_name,width,height,pix_fmt,avg_frame_rate,r_frame_rate,sample_rate,channels:stream_tags=rotate:stream_side_data=rotation:format=duration,size",
        "-of","json",str(path),
    ]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
    if r.returncode!=0:
        raise RuntimeError("ffprobe source failed: "+(r.stderr or "")[-500:])
    return json.loads(r.stdout or "{}")


def run_matrix(workdir=None):
    own=None
    if workdir is None:
        own=tempfile.TemporaryDirectory(prefix="gsf_v105_stress_")
        root=Path(own.name)
    else:
        root=Path(workdir)
        root.mkdir(parents=True,exist_ok=True)

    rows=[]
    try:
        for name in CASES:
            src=root/f"{name}_source.mp4"
            out=root/f"{name}_final.mp4"
            build_source(name,src)
            source_probe=probe_source(src)
            result=bench.run_profile(src,out,RENDER_PROFILE,timeout=300)
            row={
                "case":name,
                "source":source_probe,
                "render":result,
                "ok":bool(result.get("master",{}).get("ok")),
            }
            rows.append(row)
            print("GSF_STRESS_CASE "+json.dumps(row,separators=(",",":"),ensure_ascii=False),flush=True)
        return rows
    finally:
        if own is not None:
            own.cleanup()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--workdir",default="")
    args=parser.parse_args()
    rows=run_matrix(args.workdir or None)
    failed=[r["case"] for r in rows if not r.get("ok")]
    summary={"ok":not failed,"failed":failed,"count":len(rows)}
    print("GSF_STRESS_SUMMARY "+json.dumps(summary,separators=(",",":")),flush=True)
    if failed:
        raise SystemExit(2)


if __name__=="__main__":
    main()
