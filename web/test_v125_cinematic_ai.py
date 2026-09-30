from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,"/app/web")

from cinematic_render_v125 import apply_cinematic_plan, extract_thumbnail, probe_media

app_path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V125_CINEMATIC_AI.py")
app=app_path.read_text(encoding="utf-8")
brain_patch=Path("/app/web/apply_v112_game_brain.py").read_text(encoding="utf-8")
cinematic=Path("/app/web/cinematic_render_v125.py").read_text(encoding="utf-8")

for marker in (
    "ALTERNATIVE AI",
    "gsf_v125_rank_overrides",
    "RIPRISTINA SCELTA AI",
    "GSF_V125_CINEMATIC_APPLIED",
    "ai_director_plan",
    "cinematic_render_v125",
):
    if marker not in app:
        raise SystemExit("V125 app marker missing: "+marker)

for marker in (
    "gsf_v125_rank_overrides",
    "replacement_override",
    "replaced_from_start",
    "rank_overrides",
):
    if marker not in brain_patch:
        raise SystemExit("V125 real rank override marker missing: "+marker)

for marker in (
    "def apply_segment_slowmo",
    "def append_replay",
    "def apply_cinematic_plan",
    "def extract_thumbnail",
    "atempo=",
    "concat=n=",
):
    if marker not in cinematic:
        raise SystemExit("V125 cinematic engine marker missing: "+marker)

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    src=root/"source.mp4"
    out=root/"cinematic.mp4"
    thumb=root/"thumb.jpg"

    # Real A/V source: 6 seconds, vertical, moving test pattern + sine audio.
    cmd=[
        "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i","testsrc2=size=360x640:rate=30:duration=6",
        "-f","lavfi","-i","sine=frequency=660:sample_rate=48000:duration=6",
        "-shortest","-c:v","libx264","-preset","ultrafast","-crf","24",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","96k",str(src),
    ]
    proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60,check=False)
    if proc.returncode!=0 or not src.is_file():
        raise SystemExit("V125 synthetic video generation failed: "+(proc.stderr or "")[-500:])

    plan={
        "edit":{
            "slow_motion":{"enabled":True,"center":2.5,"window":1.2,"speed":0.75},
            "replay":{"enabled":True,"center":3.0,"window":1.4},
            "thumbnail_offset":3.05,
        }
    }
    before=probe_media(src)
    result=apply_cinematic_plan(src,out,plan)
    after=probe_media(out)
    if not result.get("ok") or not out.is_file() or out.stat().st_size<4096:
        raise SystemExit("V125 cinematic render failed: "+repr(result))
    applied=[x.get("effect") for x in result.get("effects",[]) if x.get("applied")]
    if "slow_motion" not in applied or "replay" not in applied:
        raise SystemExit("V125 cinematic effects not both applied: "+repr(result))
    if after["duration"] <= before["duration"]+1.0:
        raise SystemExit(
            "V125 segmented replay/slowmo did not extend duration: "+
            repr((before["duration"],after["duration"]))
        )
    if not after["has_audio"]:
        raise SystemExit("V125 cinematic render lost audio")

    thumb_result=extract_thumbnail(src,thumb,plan["edit"]["thumbnail_offset"],width=360)
    if not thumb_result.get("ok") or not thumb.is_file() or thumb.stat().st_size<512:
        raise SystemExit("V125 thumbnail extraction failed")
    magic=thumb.read_bytes()[:2]
    if magic!=b"\xff\xd8":
        raise SystemExit("V125 thumbnail is not JPEG")

compile(app,str(app_path),"exec")
print("V125 cinematic AI real FFmpeg contracts: PASS")
