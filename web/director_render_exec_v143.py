from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from cinematic_render_v125 import probe_media
from quality_supreme_v399 import encoder_args, quality_profile
from web.render_gate_v293 import render_slot as _gsf_render_slot_v293


def _f(v,d=0.0):
    try:return float(v)
    except Exception:return float(d)


def _run(cmd,timeout=180):
    with _gsf_render_slot_v293("director-v143"):
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout,check=False)
    if p.returncode!=0:
        raise RuntimeError((p.stderr or p.stdout or "ffmpeg failed")[-1200:])


def _signals(meta, *, motion=0.0, detail=0.0, action_peak=0.0):
    return {
        "motion": motion,
        "detail": detail,
        "action_peak": action_peak,
        "source_width": int(meta.get("width") or 0),
        "source_height": int(meta.get("height") or 0),
    }


def _tail(has_audio=True, signals=None):
    return encoder_args(quality_profile(signals), has_audio=has_audio)


def _speed_window(src,out,start,end,speed):
    meta=probe_media(src); dur=float(meta.get("duration") or 0.0); has_audio=bool(meta.get("has_audio"))
    start=max(0.0,min(dur,start)); end=max(start,min(dur,end)); speed=max(1.05,min(1.8,speed))
    if end-start<.35:
        shutil.copyfile(src,out); return False
    parts=[]
    if start>.03: parts.append((0.0,start,1.0))
    parts.append((start,end,speed))
    if end<dur-.03: parts.append((end,dur,1.0))
    chunks=[]; ins=[]
    for i,(a,b,s) in enumerate(parts):
        chunks.append(f"[0:v]trim=start={a:.4f}:end={b:.4f},setpts=(PTS-STARTPTS)/{s:.5f}[v{i}]")
        ins.append(f"[v{i}]")
        if has_audio:
            chunks.append(f"[0:a]atrim=start={a:.4f}:end={b:.4f},asetpts=PTS-STARTPTS,atempo={s:.5f}[a{i}]")
            ins.append(f"[a{i}]")
    if has_audio:
        chunks.append("".join(ins)+f"concat=n={len(parts)}:v=1:a=1[vout][aout]")
    else:
        chunks.append("".join(ins)+f"concat=n={len(parts)}:v=1:a=0[vout]")
    cmd=["/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(src),"-filter_complex",";".join(chunks),"-map","[vout]"]
    if has_audio: cmd+=["-map","[aout]"]
    cmd+=_tail(has_audio,_signals(meta,motion=.96,detail=.82,action_peak=.90))+[str(out)]
    _run(cmd)
    return True


def _prepend_cold_open(src,out,duration,peak):
    meta=probe_media(src); dur=float(meta.get("duration") or 0.0); has_audio=bool(meta.get("has_audio"))
    cold=max(.35,min(1.25,float(duration or .7))); peak=max(0.0,min(dur,peak))
    a=max(0.0,peak-cold*.45); b=min(dur,a+cold)
    if b-a<.25:
        shutil.copyfile(src,out); return False
    if has_audio:
        graph=(f"[0:v]trim=start={a:.4f}:end={b:.4f},setpts=PTS-STARTPTS[cv];"
               f"[0:a]atrim=start={a:.4f}:end={b:.4f},asetpts=PTS-STARTPTS[ca];"
               "[0:v]setpts=PTS-STARTPTS[mv];[0:a]asetpts=PTS-STARTPTS[ma];"
               "[cv][ca][mv][ma]concat=n=2:v=1:a=1[vout][aout]")
    else:
        graph=(f"[0:v]trim=start={a:.4f}:end={b:.4f},setpts=PTS-STARTPTS[cv];"
               "[0:v]setpts=PTS-STARTPTS[mv];[cv][mv]concat=n=2:v=1:a=0[vout]")
    cmd=["/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(src),"-filter_complex",graph,"-map","[vout]"]
    if has_audio: cmd+=["-map","[aout]"]
    cmd+=_tail(has_audio,_signals(meta,motion=.80,detail=.75,action_peak=.95))+[str(out)]
    _run(cmd)
    return True


def _smart_finish(src,out):
    meta=probe_media(src); dur=float(meta.get("duration") or 0.0); has_audio=bool(meta.get("has_audio"))
    if dur<1.0:
        shutil.copyfile(src,out); return False
    fade=.14; start=max(0.0,dur-fade)
    vf=f"fade=t=out:st={start:.4f}:d={fade:.4f}"
    cmd=["/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(src),"-vf",vf]
    if has_audio: cmd+=["-af",f"afade=t=out:st={start:.4f}:d={fade:.4f}"]
    cmd+=_tail(has_audio,_signals(meta,motion=.35,detail=.60,action_peak=.40))+[str(out)]
    _run(cmd)
    return True


def execute_director_operations(input_path,output_path,operations,recipe_start=0.0):
    """Execute V139 operations not already handled by V125/V126/base renderer."""
    src=Path(input_path); out=Path(output_path); out.parent.mkdir(parents=True,exist_ok=True)
    work_a=out.with_name(out.stem+".a.tmp.mp4"); work_b=out.with_name(out.stem+".b.tmp.mp4")
    current=src; applied=[]; recipe_start=float(recipe_start or 0.0)
    ops=[dict(x) for x in (operations or []) if isinstance(x,dict)]
    try:
        for row in [x for x in ops if x.get("op")=="pattern_interrupt"][:2]:
            local=max(0.0,_f(row.get("start"))-recipe_start)
            dur=max(.35,_f(row.get("duration"),1.5))
            target=work_a if current!=work_a else work_b
            if _speed_window(current,target,local,local+dur,1.28):
                current=target; applied.append("pattern_interrupt")
        cold=next((x for x in ops if x.get("op")=="cold_open"),None)
        cover=next((x for x in ops if x.get("op")=="cover"),None)
        if cold:
            peak=max(0.0,_f((cover or {}).get("time"),0)-recipe_start)
            if peak<=0:
                peak=float(probe_media(current).get("duration") or 0)*.62
            target=work_a if current!=work_a else work_b
            if _prepend_cold_open(current,target,_f(cold.get("duration"),.7),peak):
                current=target; applied.append("cold_open")
        if any(x.get("op")=="smart_ending" for x in ops):
            target=work_a if current!=work_a else work_b
            if _smart_finish(current,target):
                current=target; applied.append("smart_ending")
        if current.resolve()!=out.resolve():
            shutil.copyfile(current,out)
        return {"ok":True,"engine":"v143-render-execution","applied":applied,"count":len(applied)}
    finally:
        for p in (work_a,work_b):
            try:p.unlink(missing_ok=True)
            except Exception:pass
