from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
from pathlib import Path

from web.render_gate_v293 import render_slot as _gsf_render_slot_v293

ENGINE_VERSION="v125-cinematic-ai"


def _num(value,default=0.0):
    try:
        value=float(value)
        return value if math.isfinite(value) else float(default)
    except Exception:
        return float(default)


def probe_media(path):
    proc=subprocess.run(
        [
            "/usr/bin/ffprobe","-v","error",
            "-show_entries","format=duration:stream=codec_type,width,height",
            "-of","json",str(path),
        ],
        capture_output=True,text=True,timeout=20,check=False,
    )
    if proc.returncode!=0:
        raise RuntimeError((proc.stderr or "ffprobe failed")[-300:])
    data=json.loads(proc.stdout or "{}")
    streams=list(data.get("streams") or [])
    return {
        "duration":max(0.0,_num((data.get("format") or {}).get("duration"),0.0)),
        "has_audio":any(str(x.get("codec_type") or "")=="audio" for x in streams),
        "width":int(next((x.get("width") for x in streams if x.get("codec_type")=="video"),0) or 0),
        "height":int(next((x.get("height") for x in streams if x.get("codec_type")=="video"),0) or 0),
    }


def _encode_tail(has_audio=True):
    args=[
        "-c:v","libx264",
        "-preset","fast",
        "-crf","14",
        "-pix_fmt","yuv420p",
        "-profile:v","high",
        "-level","4.2",
        "-threads","1" if os.environ.get("GSF_LOW_MEMORY_WEB","0").strip().lower() in {"1","true","yes","on"} else "2",
    ]
    if has_audio:
        args += ["-c:a","aac","-b:a","192k","-ar","48000","-ac","2"]
    args += ["-movflags","+faststart"]
    return args


def _run(cmd,timeout=180):
    if os.environ.get("GSF_LOW_MEMORY_WEB","0").strip().lower() in {"1","true","yes","on"}:
        # Direct /usr/bin calls bypass the launcher. Bound decoder/filter pools
        # before inputs as well as encoder threads, retaining the same graph/CRF.
        bounded=[cmd[0],"-filter_threads","1","-filter_complex_threads","1"]
        for arg in cmd[1:]:
            if arg=="-i":
                bounded += ["-threads","1"]
            bounded.append(arg)
        cmd=bounded
    with _gsf_render_slot_v293("cinematic-v125"):
        proc=subprocess.run(
            cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
            timeout=timeout,check=False,
        )
    if proc.returncode!=0:
        raise RuntimeError((proc.stderr or proc.stdout or "ffmpeg failed")[-1200:])
    return proc


def _slow_window(plan,duration):
    edit=(plan or {}).get("edit") or {}
    slow=(edit.get("slow_motion") or {}) if isinstance(edit,dict) else {}
    if not slow.get("enabled"):
        return None
    center=max(0.0,min(float(duration),_num(slow.get("center"),duration*.5)))
    window=max(.55,min(3.2,_num(slow.get("window"),1.6)))
    speed=max(.55,min(.95,_num(slow.get("speed"),.78)))
    start=max(0.0,center-window*.5)
    end=min(float(duration),center+window*.5)
    if end-start<.45:
        return None
    return start,end,speed


def _replay_window(plan,duration):
    edit=(plan or {}).get("edit") or {}
    replay=(edit.get("replay") or {}) if isinstance(edit,dict) else {}
    if not replay.get("enabled"):
        return None
    center=max(0.0,min(float(duration),_num(replay.get("center"),duration*.5)))
    window=max(.8,min(3.0,_num(replay.get("window"),1.8)))
    start=max(0.0,center-window*.5)
    end=min(float(duration),center+window*.5)
    if end-start<.55:
        return None
    return start,end


def build_slowmo_filter(duration,start,end,speed,has_audio):
    duration=max(.1,float(duration))
    start=max(0.0,min(duration,float(start)))
    end=max(start,min(duration,float(end)))
    speed=max(.55,min(.95,float(speed)))
    intervals=[]
    if start>.04:
        intervals.append((0.0,start,1.0,"normal"))
    intervals.append((start,end,speed,"slow"))
    if end<duration-.04:
        intervals.append((end,duration,1.0,"normal"))

    chunks=[]
    concat_inputs=[]
    for idx,(a,b,seg_speed,kind) in enumerate(intervals):
        if b-a<=.02:
            continue
        if kind=="slow":
            chunks.append(
                f"[0:v]trim=start={a:.4f}:end={b:.4f},"
                f"setpts=(PTS-STARTPTS)/{seg_speed:.5f}[v{idx}]"
            )
        else:
            chunks.append(
                f"[0:v]trim=start={a:.4f}:end={b:.4f},"
                f"setpts=PTS-STARTPTS[v{idx}]"
            )
        concat_inputs.append(f"[v{idx}]")
        if has_audio:
            if kind=="slow":
                chunks.append(
                    f"[0:a]atrim=start={a:.4f}:end={b:.4f},"
                    f"asetpts=PTS-STARTPTS,atempo={seg_speed:.5f}[a{idx}]"
                )
            else:
                chunks.append(
                    f"[0:a]atrim=start={a:.4f}:end={b:.4f},"
                    f"asetpts=PTS-STARTPTS[a{idx}]"
                )
            concat_inputs.append(f"[a{idx}]")

    count=len(intervals)
    if has_audio:
        chunks.append("".join(concat_inputs)+f"concat=n={count}:v=1:a=1[vout][aout]")
    else:
        chunks.append("".join(concat_inputs)+f"concat=n={count}:v=1:a=0[vout]")
    return ";".join(chunks)


def apply_segment_slowmo(input_path,output_path,plan):
    src=Path(input_path)
    out=Path(output_path)
    meta=probe_media(src)
    window=_slow_window(plan,meta["duration"])
    if not window:
        shutil.copyfile(src,out)
        return {"applied":False,"effect":"slow_motion"}
    start,end,speed=window
    graph=build_slowmo_filter(meta["duration"],start,end,speed,meta["has_audio"])
    cmd=["/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(src),"-filter_complex",graph,"-map","[vout]"]
    if meta["has_audio"]:
        cmd += ["-map","[aout]"]
    cmd += _encode_tail(meta["has_audio"])+[str(out)]
    _run(cmd,timeout=180)
    return {
        "applied":True,
        "effect":"slow_motion",
        "start":round(start,3),"end":round(end,3),"speed":round(speed,3),
    }


def append_replay(main_path,source_path,output_path,plan):
    main=Path(main_path)
    source=Path(source_path)
    out=Path(output_path)
    src_meta=probe_media(source)
    main_meta=probe_media(main)
    window=_replay_window(plan,src_meta["duration"])
    if not window:
        shutil.copyfile(main,out)
        return {"applied":False,"effect":"replay"}
    start,end=window
    has_audio=bool(main_meta["has_audio"] and src_meta["has_audio"])
    if has_audio:
        graph=(
            "[0:v]setpts=PTS-STARTPTS[mv];"
            "[0:a]asetpts=PTS-STARTPTS[ma];"
            f"[1:v]trim=start={start:.4f}:end={end:.4f},setpts=PTS-STARTPTS[rv];"
            f"[1:a]atrim=start={start:.4f}:end={end:.4f},asetpts=PTS-STARTPTS[ra];"
            "[mv][ma][rv][ra]concat=n=2:v=1:a=1[vout][aout]"
        )
    else:
        graph=(
            "[0:v]setpts=PTS-STARTPTS[mv];"
            f"[1:v]trim=start={start:.4f}:end={end:.4f},setpts=PTS-STARTPTS[rv];"
            "[mv][rv]concat=n=2:v=1:a=0[vout]"
        )
    cmd=[
        "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
        "-i",str(main),"-i",str(source),
        "-filter_complex",graph,
        "-map","[vout]",
    ]
    if has_audio:
        cmd += ["-map","[aout]"]
    cmd += _encode_tail(has_audio)+[str(out)]
    _run(cmd,timeout=180)
    return {
        "applied":True,"effect":"replay",
        "start":round(start,3),"end":round(end,3),
    }


def apply_cinematic_plan(input_path,output_path,plan):
    src=Path(input_path)
    out=Path(output_path)
    out.parent.mkdir(parents=True,exist_ok=True)
    work=out.with_name(out.stem+".slow.tmp.mp4")
    work2=out.with_name(out.stem+".replay.tmp.mp4")
    for p in (work,work2):
        p.unlink(missing_ok=True)
    effects=[]
    try:
        slow=apply_segment_slowmo(src,work,plan)
        effects.append(slow)
        base=work if slow.get("applied") else src
        replay=append_replay(base,src,work2,plan)
        effects.append(replay)
        final_source=work2 if replay.get("applied") else base
        if final_source.resolve()!=out.resolve():
            shutil.copyfile(final_source,out)
        before=probe_media(src)
        after=probe_media(out)
        return {
            "ok":True,
            "engine":ENGINE_VERSION,
            "effects":effects,
            "duration_before":round(before["duration"],3),
            "duration_after":round(after["duration"],3),
        }
    finally:
        work.unlink(missing_ok=True)
        work2.unlink(missing_ok=True)


def extract_thumbnail(input_path,output_path,offset_seconds=0.0,width=720):
    src=Path(input_path)
    out=Path(output_path)
    out.parent.mkdir(parents=True,exist_ok=True)
    meta=probe_media(src)
    offset=max(0.0,min(max(0.0,meta["duration"]-.08),_num(offset_seconds,meta["duration"]*.5)))
    vf=f"scale='min({int(width)},iw)':-2"
    cmd=[
        "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
        "-ss",f"{offset:.4f}","-i",str(src),
        "-frames:v","1","-vf",vf,
        "-q:v","2",str(out),
    ]
    _run(cmd,timeout=60)
    if not out.is_file() or out.stat().st_size<512:
        raise RuntimeError("thumbnail extraction failed")
    return {
        "ok":True,"engine":ENGINE_VERSION,
        "offset":round(offset,3),"bytes":int(out.stat().st_size),
    }
