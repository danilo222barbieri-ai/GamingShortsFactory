from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

from cinematic_render_v125 import probe_media
from web.render_gate_v293 import render_slot as _gsf_render_slot_v293

ENGINE_VERSION="v126-creative-director"


def _num(value,default=0.0):
    try:
        value=float(value)
        return value if math.isfinite(value) else float(default)
    except Exception:
        return float(default)


def _profile(plan,duration):
    plan=dict(plan or {})
    edit=dict(plan.get("edit") or {})
    style=dict(plan.get("style") or {})
    accent=str(style.get("sound_accent") or "none").strip().lower()
    event=max(0.0,min(float(duration),_num(edit.get("event_offset"),duration*.5)))
    presets={
        "impact-hit":(.88,1.08,.42,.48),
        "riser-hit":(.82,1.10,.68,.62),
        "victory-rise":(.90,1.08,.45,1.10),
        "impact-crowd":(.84,1.10,.58,.78),
        "cinematic-hit":(.82,1.09,.70,.82),
        "bass-hit":(.86,1.08,.45,.55),
        "whoosh":(.90,1.06,.35,.50),
        "duck-and-lift":(.78,1.08,.72,.85),
    }
    row=presets.get(accent)
    if not row:
        return None
    pre_gain,hit_gain,pre_window,post_window=row
    return {
        "accent":accent,
        "event":event,
        "pre_start":max(0.0,event-pre_window),
        "pre_end":max(0.0,event-.06),
        "hit_start":max(0.0,event-.04),
        "hit_end":min(float(duration),event+post_window),
        "pre_gain":pre_gain,
        "hit_gain":hit_gain,
    }


def build_audio_filter(plan,duration):
    prof=_profile(plan,duration)
    if not prof:
        return "",{}
    filters=[]
    if prof["pre_end"]>prof["pre_start"]+.02:
        filters.append(
            "volume="+f"{prof['pre_gain']:.4f}"+":enable='between(t,"+f"{prof['pre_start']:.4f},{prof['pre_end']:.4f}"+")'"
        )
    if prof["hit_end"]>prof["hit_start"]+.02:
        filters.append(
            "volume="+f"{prof['hit_gain']:.4f}"+":enable='between(t,"+f"{prof['hit_start']:.4f},{prof['hit_end']:.4f}"+")'"
        )
    filters.append("alimiter=limit=0.95:attack=5:release=50")
    return ",".join(filters),prof


def apply_sound_design(input_path,output_path,plan):
    src=Path(input_path)
    out=Path(output_path)
    out.parent.mkdir(parents=True,exist_ok=True)
    meta=probe_media(src)
    if not meta.get("has_audio"):
        shutil.copyfile(src,out)
        return {"ok":True,"applied":False,"engine":ENGINE_VERSION,"reason":"no-audio"}
    af,prof=build_audio_filter(plan,meta.get("duration") or 0.0)
    if not af:
        shutil.copyfile(src,out)
        return {"ok":True,"applied":False,"engine":ENGINE_VERSION,"reason":"no-accent"}
    cmd=[
        "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
        "-i",str(src),"-map","0:v:0","-map","0:a:0","-c:v","copy",
        "-af",af,"-c:a","aac","-b:a","192k","-ar","48000","-ac","2",
        "-movflags","+faststart",str(out),
    ]
    with _gsf_render_slot_v293("creative-v126"):
        proc=subprocess.run(
            cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
            timeout=max(60,min(180,int(meta.get("duration") or 0)*6+45)),check=False,
        )
    if proc.returncode!=0:
        raise RuntimeError((proc.stderr or proc.stdout or "sound design failed")[-1000:])
    if not out.is_file() or out.stat().st_size<1024:
        raise RuntimeError("sound design output missing")
    return {
        "ok":True,"applied":True,"engine":ENGINE_VERSION,
        "accent":prof.get("accent"),"event":round(_num(prof.get("event")),3),
        "pre_gain":prof.get("pre_gain"),"hit_gain":prof.get("hit_gain"),
    }
