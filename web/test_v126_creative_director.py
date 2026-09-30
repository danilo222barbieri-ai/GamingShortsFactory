from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,"/app/web")

from creative_render_v126 import apply_sound_design, build_audio_filter
from cinematic_render_v125 import probe_media

app_path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V126_CREATIVE_DIRECTOR.py")
app=app_path.read_text(encoding="utf-8")
creative=Path("/app/web/creative_render_v126.py").read_text(encoding="utf-8")

for marker in (
    "def _gsf_v126_hook_for_start",
    "_gsf_v126_hook_for_start(float(_card",
    "GSF_V126_SOUND_APPLIED",
    "creative_render_v126",
    "Gaming Shorts Factory · V126 Creative Director",
):
    if marker not in app:
        raise SystemExit("V126 app marker missing: "+marker)

for marker in (
    "def apply_sound_design",
    "def build_audio_filter",
    "alimiter=limit=0.95",
    "volume=",
    '"-c:v","copy"',
):
    if marker not in creative:
        raise SystemExit("V126 creative renderer marker missing: "+marker)

plan={
    "edit":{"event_offset":2.6},
    "style":{"sound_accent":"riser-hit"},
}
af,profile=build_audio_filter(plan,6.0)
if "between(t" not in af or "alimiter" not in af:
    raise SystemExit("V126 event audio filter missing dynamic windows")
if profile.get("accent")!="riser-hit":
    raise SystemExit("V126 audio profile selection failed")

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    src=root/"src.mp4"
    out=root/"sound.mp4"
    cmd=[
        "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i","testsrc2=size=360x640:rate=30:duration=6",
        "-f","lavfi","-i","sine=frequency=440:sample_rate=48000:duration=6",
        "-shortest","-c:v","libx264","-preset","ultrafast","-crf","25",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","96k",str(src),
    ]
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60,check=False)
    if p.returncode!=0:
        raise SystemExit("V126 source generation failed: "+(p.stderr or "")[-400:])
    before=probe_media(src)
    result=apply_sound_design(src,out,plan)
    after=probe_media(out)
    if not result.get("ok") or not result.get("applied"):
        raise SystemExit("V126 sound design not applied: "+repr(result))
    if not out.is_file() or out.stat().st_size<4096 or not after.get("has_audio"):
        raise SystemExit("V126 sound output invalid")
    if abs(after["duration"]-before["duration"])>.2:
        raise SystemExit("V126 sound design changed clip duration")
    if out.read_bytes()==src.read_bytes():
        raise SystemExit("V126 sound design output unexpectedly identical")

compile(app,str(app_path),"exec")
print("V126 Creative Director real audio contracts: PASS")
