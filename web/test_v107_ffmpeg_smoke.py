#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile


def run(cmd, timeout=90):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)
    if p.returncode!=0:
        raise SystemExit("FAIL ffmpeg smoke: "+(p.stderr or "")[-1200:])
    return p


def probe(path):
    p=run([
        "/usr/bin/ffprobe","-v","error","-show_streams","-show_format",
        "-of","json",path
    ],30)
    return json.loads(p.stdout)


with tempfile.TemporaryDirectory(prefix="gsf_v107_ffmpeg_") as td:
    src=os.path.join(td,"source.mp4")
    run([
        "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i","testsrc2=size=640x360:rate=30",
        "-f","lavfi","-i","sine=frequency=500:sample_rate=48000",
        "-t","0.45","-c:v","libx264","-preset","ultrafast","-crf","28",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","96k","-shortest",
        "-movflags","+faststart",src
    ],45)

    cases=[
        (
            "9x16",os.path.join(td,"short.mp4"),
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "eq=brightness=0.05:contrast=1.08,setpts=PTS/1.0",
            (1080,1920),
        ),
        (
            "16x9",os.path.join(td,"wide.mp4"),
            "scale=-2:1080,eq=brightness=0.0:contrast=1.0,setpts=PTS/1.0",
            (1920,1080),
        ),
    ]

    for label,out,vf,size in cases:
        run([
            "/usr/local/bin/ffmpeg","-y","-i",src,"-t","0.4",
            "-vf",vf,
            "-af","atempo=1.0,volume=1.0,alimiter=limit=0.95:attack=5:release=50",
            "-c:v","libx264","-preset","medium","-crf","14","-threads","1",
            "-x264-params","rc-lookahead=16:ref=2:bframes=2",
            "-profile:v","high","-level:v","4.2","-tag:v","avc1",
            "-pix_fmt","yuv420p","-fpsmax","60",
            "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",
            "-metadata:s:v:0","rotate=0","-movflags","+faststart",out
        ],120)
        meta=probe(out)
        streams=meta.get("streams") or []
        video=next((x for x in streams if x.get("codec_type")=="video"),{})
        audio=next((x for x in streams if x.get("codec_type")=="audio"),{})
        if (int(video.get("width") or 0),int(video.get("height") or 0))!=size:
            raise SystemExit(f"FAIL {label}: wrong dimensions {video.get('width')}x{video.get('height')}")
        if video.get("codec_name")!="h264" or str(video.get("pix_fmt","")).lower() not in ("yuv420p","yuvj420p"):
            raise SystemExit(f"FAIL {label}: incompatible video stream")
        if audio.get("codec_name")!="aac":
            raise SystemExit(f"FAIL {label}: missing AAC audio")
        if os.path.getsize(out)<1000:
            raise SystemExit(f"FAIL {label}: empty output")

print("V107 real FFmpeg 9:16 + 16:9 render smoke: PASS")
