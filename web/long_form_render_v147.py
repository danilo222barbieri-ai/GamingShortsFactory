from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path
from cinematic_render_v125 import probe_media


def _f(v,d=0.0):
    try:return float(v)
    except Exception:return float(d)


def _merge_windows(windows,duration,gap=1.5):
    clean=[]
    for a,b,role,score in windows:
        a=max(0.0,min(duration,a)); b=max(a,min(duration,b))
        if b-a<.8: continue
        clean.append([a,b,role,score])
    clean.sort(key=lambda x:x[0])
    merged=[]
    for row in clean:
        if merged and row[0]<=merged[-1][1]+gap:
            merged[-1][1]=max(merged[-1][1],row[1])
            if row[3]>merged[-1][3]:
                merged[-1][2],merged[-1][3]=row[2],row[3]
        else:
            merged.append(row)
    return merged


def chapter_windows(plan,source_duration,target_seconds=None):
    """Expand Director chapter moments into real edit windows."""
    duration=max(0.0,_f(source_duration))
    target=max(30.0,min(duration or 30.0,_f(target_seconds,_f((plan or {}).get("target_seconds"),480))))
    role_span={
        "cold_open":8.0,"setup":42.0,"escalation":55.0,
        "peak":38.0,"reaction":24.0,"resolution":38.0,
    }
    windows=[]
    for ch in (dict(plan or {}).get("chapters") or []):
        if not isinstance(ch,dict): continue
        role=str(ch.get("role") or "story")
        span=role_span.get(role,36.0)
        for m in ch.get("moments") or []:
            if not isinstance(m,dict): continue
            t=max(0.0,min(duration,_f(m.get("start"))))
            score=_f(m.get("brain_score",m.get("score",.5)),.5)
            pre=span*(.35 if role!="setup" else .48)
            post=span-pre
            windows.append((t-pre,t+post,role,score))
    windows=_merge_windows(windows,duration)
    if not windows and duration:
        return [{"start":0.0,"end":min(duration,target),"role":"source","score":.5}]
    total=sum(b-a for a,b,_,_ in windows)
    # Expand strongest windows until we approach the target without exceeding source.
    if total<target and windows:
        order=sorted(range(len(windows)),key=lambda i:windows[i][3],reverse=True)
        remaining=target-total
        for i in order:
            if remaining<=.2: break
            left=windows[i][0]-(windows[i-1][1] if i>0 else 0.0)
            right=(windows[i+1][0] if i+1<len(windows) else duration)-windows[i][1]
            grow=min(remaining,max(0.0,left)+max(0.0,right))
            gl=min(max(0.0,left),grow*.45)
            gr=min(max(0.0,right),grow-gl)
            windows[i][0]-=gl; windows[i][1]+=gr; remaining-=gl+gr
        windows=_merge_windows(windows,duration,gap=.05)
    # If the story still cannot fill target, include chronological context gaps.
    total=sum(b-a for a,b,_,_ in windows)
    if total<target and duration>total:
        gaps=[]; cursor=0.0
        for a,b,_,_ in windows:
            if a-cursor>8:gaps.append((cursor,a))
            cursor=max(cursor,b)
        if duration-cursor>8:gaps.append((cursor,duration))
        for a,b in sorted(gaps,key=lambda x:x[1]-x[0],reverse=True):
            need=target-sum(y-x for x,y,_,_ in windows)
            if need<=.2: break
            take=min(need,b-a)
            windows.append([a,a+take,"context",.2])
        windows=_merge_windows(windows,duration,gap=.05)
    rows=[{"start":round(a,3),"end":round(b,3),"role":role,"score":round(score,3)}
          for a,b,role,score in windows]
    return rows


def render_long_form(source_path,output_path,plan,source_duration,target_seconds=None):
    """Render a real 16:9 YouTube long-form cut from Director windows."""
    src=Path(source_path); out=Path(output_path); out.parent.mkdir(parents=True,exist_ok=True)
    windows=chapter_windows(plan,source_duration,target_seconds=target_seconds)
    if not windows:
        raise RuntimeError("no long-form windows")
    meta=probe_media(src)
    has_audio=bool(meta.get("has_audio"))
    filters=[]; inputs=[]
    for i,row in enumerate(windows):
        a,b=float(row["start"]),float(row["end"])
        filters.append(
            f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS,"
            "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1"
            f"[v{i}]"
        )
        inputs.append(f"[v{i}]")
        if has_audio:
            filters.append(
                f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{i}]"
            )
            inputs.append(f"[a{i}]")
    filters.append(
        "".join(inputs)+(
            f"concat=n={len(windows)}:v=1:a=1[vout][aout]"
            if has_audio else
            f"concat=n={len(windows)}:v=1:a=0[vout]"
        )
    )
    cmd=[
        "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(src),
        "-filter_complex",";".join(filters),"-map","[vout]",
        "-c:v","libx264","-preset","fast","-crf","16","-pix_fmt","yuv420p",
    ]
    if has_audio:
        cmd+=["-map","[aout]","-c:a","aac","-b:a","192k","-ar","48000"]
    else:
        cmd+=["-an"]
    cmd+=["-movflags","+faststart",str(out)]
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=1800,check=False)
    if p.returncode!=0 or not out.is_file() or out.stat().st_size<=1024:
        raise RuntimeError((p.stderr or p.stdout or "long-form render failed")[-1800:])
    return {
        "ok":True,"engine":"v147-long-form-render","output":str(out),
        "windows":windows,"segment_count":len(windows),
        "planned_seconds":round(sum(x["end"]-x["start"] for x in windows),2),
    }
