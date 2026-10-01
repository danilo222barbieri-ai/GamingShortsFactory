from __future__ import annotations

import csv
import io
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from cinematic_render_v125 import probe_media
from ocr_privacy_v146 import classify_sensitive


def _run(cmd, timeout=180):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout,check=False)
    if p.returncode!=0:
        raise RuntimeError((p.stderr or p.stdout or "command failed")[-1400:])
    return p


def _sample_times(duration,step=.8,max_frames=40):
    duration=max(0.0,float(duration or 0.0))
    if duration<=0:return []
    pts=[]; t=.15
    while t<duration and len(pts)<max_frames:
        pts.append(round(t,3)); t+=max(.45,float(step))
    if not pts or pts[-1]<duration-.25:
        pts.append(round(max(0.0,duration-.15),3))
    return pts[:max_frames]


def _extract_frame(video_path,dst,time_sec,width=960):
    _run([
        "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
        "-ss",f"{float(time_sec):.3f}","-i",str(video_path),
        "-frames:v","1","-vf",f"scale={int(width)}:-2","-q:v","2",str(dst),
    ],timeout=40)
    return dst


def _ocr_line_boxes(image_path,languages="eng+ita"):
    if not shutil.which("tesseract"):
        return []
    p=subprocess.run(
        ["tesseract",str(image_path),"stdout","-l",languages,"--psm","11","tsv"],
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30,check=False,
    )
    if p.returncode!=0 or not p.stdout.strip():
        return []
    img=Image.open(image_path)
    iw,ih=img.size
    groups={}
    reader=csv.DictReader(io.StringIO(p.stdout),delimiter="	")
    for row in reader:
        text=str(row.get("text") or "").strip()
        if not text:continue
        try:
            conf=float(row.get("conf") or -1)
            if conf<20:continue
            left=int(float(row.get("left") or 0)); top=int(float(row.get("top") or 0))
            width=int(float(row.get("width") or 0)); height=int(float(row.get("height") or 0))
            key=(row.get("page_num"),row.get("block_num"),row.get("par_num"),row.get("line_num"))
        except Exception:
            continue
        g=groups.setdefault(key,{"words":[],"x0":left,"y0":top,"x1":left+width,"y1":top+height})
        g["words"].append(text)
        g["x0"]=min(g["x0"],left); g["y0"]=min(g["y0"],top)
        g["x1"]=max(g["x1"],left+width); g["y1"]=max(g["y1"],top+height)
    out=[]
    for g in groups.values():
        text=" ".join(g["words"])
        findings=classify_sensitive(text,[])
        if not findings:continue
        pad_x=max(4,int((g["x1"]-g["x0"])*.06))
        pad_y=max(3,int((g["y1"]-g["y0"])*.18))
        x0=max(0,g["x0"]-pad_x); y0=max(0,g["y0"]-pad_y)
        x1=min(iw,g["x1"]+pad_x); y1=min(ih,g["y1"]+pad_y)
        out.append({
            "text":text[:220],
            "findings":findings,
            "x":round(x0/max(1,iw),6),
            "y":round(y0/max(1,ih),6),
            "w":round((x1-x0)/max(1,iw),6),
            "h":round((y1-y0)/max(1,ih),6),
        })
    return out


def _qr_present(image_path):
    if not shutil.which("zbarimg"):
        return False
    p=subprocess.run(
        ["zbarimg","--quiet","--raw",str(image_path)],
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=12,check=False,
    )
    return bool((p.stdout or "").strip())


def scan_final_video(video_path,out_dir=None):
    src=Path(video_path)
    meta=probe_media(src)
    root=Path(out_dir) if out_dir else src.parent/(src.stem+"_privacy_v149")
    root.mkdir(parents=True,exist_ok=True)
    frames=[]; qrs=[]
    for i,t in enumerate(_sample_times(meta["duration"])):
        dst=root/f"privacy_{i:03d}_{int(t*1000):08d}.jpg"
        try:
            _extract_frame(src,dst,t)
            boxes=_ocr_line_boxes(dst)
            qr=_qr_present(dst)
            if boxes:
                frames.append({"time":t,"boxes":boxes})
            if qr:
                qrs.append({"time":t,"path":str(dst)})
        except Exception:
            continue
    report={
        "engine":"v149-privacy-cleanup",
        "duration":round(meta["duration"],3),
        "width":meta["width"],"height":meta["height"],
        "detections":frames,
        "qr_frames":qrs,
        "mask_count":sum(len(x["boxes"]) for x in frames),
        "publish_guard":"review" if qrs else "clear",
    }
    try:
        (root/"privacy_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    except Exception:
        pass
    return report


def _mask_filters(report):
    width=max(2,int(report.get("width") or 0)); height=max(2,int(report.get("height") or 0))
    filters=[]
    for frame in report.get("detections") or []:
        t=float(frame.get("time") or 0.0)
        for box in frame.get("boxes") or []:
            x=max(0,min(width-2,int(float(box.get("x") or 0)*width)))
            y=max(0,min(height-2,int(float(box.get("y") or 0)*height)))
            w=max(8,min(width-x,int(math.ceil(float(box.get("w") or 0)*width))))
            h=max(8,min(height-y,int(math.ceil(float(box.get("h") or 0)*height))))
            start=max(0.0,t-.55); end=t+.75
            filters.append(
                f"drawbox=x={x}:y={y}:w={w}:h={h}:color=black@0.86:t=fill:"
                f"enable='between(t,{start:.3f},{end:.3f})'"
            )
    return filters


def cleanup_video(input_path,output_path,report=None):
    src=Path(input_path); out=Path(output_path); out.parent.mkdir(parents=True,exist_ok=True)
    report=dict(report or scan_final_video(src))
    filters=_mask_filters(report)
    if not filters:
        shutil.copyfile(src,out)
        return {
            "ok":True,"engine":"v149-privacy-cleanup","applied":False,
            "mask_count":0,"publish_guard":report.get("publish_guard","clear"),
            "report":report,
        }
    meta=probe_media(src)
    cmd=["/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(src),"-vf",",".join(filters)]
    cmd+=["-c:v","libx264","-preset","fast","-crf","15","-pix_fmt","yuv420p","-profile:v","high","-level","4.2","-threads","2"]
    if meta["has_audio"]:
        cmd+=["-c:a","copy"]
    else:
        cmd+=["-an"]
    cmd+=["-movflags","+faststart",str(out)]
    _run(cmd,timeout=480)
    return {
        "ok":True,"engine":"v149-privacy-cleanup","applied":True,
        "mask_count":len(filters),"publish_guard":report.get("publish_guard","clear"),
        "report":report,
    }
