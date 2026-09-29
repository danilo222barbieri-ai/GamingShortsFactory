#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
from pathlib import Path

FFMPEG="/usr/bin/ffmpeg"
GSF_FFMPEG="/usr/local/bin/ffmpeg"
FFPROBE="/usr/bin/ffprobe"


def run(cmd,timeout=120):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)
    if p.returncode!=0:
        raise SystemExit("V107 mobile codec smoke FAIL: "+(p.stderr or "")[-1800:])
    return p


def probe(path):
    p=run([FFPROBE,"-v","error","-show_streams","-of","json",str(path)],30)
    return json.loads(p.stdout or "{}")


with tempfile.TemporaryDirectory(prefix="gsf_mobile_codec_") as td:
    root=Path(td)

    # iPhone/iPad commonly upload HEVC in a QuickTime/MOV container, often 10-bit.
    encoders=run([FFMPEG,"-hide_banner","-encoders"],30).stdout
    if "libx265" not in encoders:
        raise SystemExit("V107 mobile codec smoke FAIL: libx265 unavailable")

    iphone=root/"iphone_hevc10.mov"
    run([
        FFMPEG,"-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i","testsrc2=size=720x1280:rate=30",
        "-f","lavfi","-i","sine=frequency=700:sample_rate=48000",
        "-t","0.55","-shortest",
        "-c:v","libx265","-preset","ultrafast",
        "-x265-params","pools=1:frame-threads=1:log-level=error",
        "-pix_fmt","yuv420p10le","-tag:v","hvc1",
        "-c:a","aac","-b:a","96k","-ar","48000","-ac","2",
        iphone,
    ],120)

    # Android/desktop alternate container accepted by the uploader.
    android=root/"android_gameplay.mkv"
    run([
        FFMPEG,"-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i","testsrc2=size=1280x720:rate=60",
        "-f","lavfi","-i","sine=frequency=600:sample_rate=44100",
        "-t","0.55","-shortest",
        "-c:v","libx264","-preset","ultrafast","-crf","28",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","96k",
        android,
    ],60)

    for label,src in (("iPhone HEVC MOV",iphone),("Android/Desktop MKV",android)):
        meta=probe(src)
        if not any(x.get("codec_type")=="video" for x in meta.get("streams",[])):
            raise SystemExit(f"V107 mobile codec smoke FAIL: {label} video probe")

        out=root/(src.stem+"_social.mp4")
        run([
            GSF_FFMPEG,"-hide_banner","-loglevel","error","-y",
            "-i",str(src),"-t","0.45",
            "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v","libx264","-preset","medium","-crf","14","-threads","1",
            "-x264-params","rc-lookahead=16:ref=2:bframes=2",
            "-profile:v","high","-level:v","4.2","-tag:v","avc1",
            "-pix_fmt","yuv420p","-fpsmax","60",
            "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",
            "-movflags","+faststart",str(out),
        ],180)

        final=probe(out)
        video=next((x for x in final.get("streams",[]) if x.get("codec_type")=="video"),{})
        audio=next((x for x in final.get("streams",[]) if x.get("codec_type")=="audio"),{})
        if video.get("codec_name")!="h264" or video.get("pix_fmt")!="yuv420p":
            raise SystemExit(f"V107 mobile codec smoke FAIL: {label} final video contract")
        if (int(video.get("width") or 0),int(video.get("height") or 0))!=(1080,1920):
            raise SystemExit(f"V107 mobile codec smoke FAIL: {label} final dimensions")
        if audio.get("codec_name")!="aac" or int(audio.get("sample_rate") or 0)!=48000:
            raise SystemExit(f"V107 mobile codec smoke FAIL: {label} final audio contract")

print("V107 iOS HEVC/MOV + Android/Desktop MKV codec smoke: PASS")
