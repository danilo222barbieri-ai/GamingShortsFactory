from pathlib import Path
import ast
import shutil
import subprocess
import sys

sys.path.insert(0,"/app/web")
from zoomout_v109 import build_zoomout_filter

app_path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V109_ZOOMOUT.py")
app=app_path.read_text(encoding="utf-8")
frontend=Path("/app/web/editor_2027_component/index.html").read_text(encoding="utf-8")
embed=Path("/app/web/editor_2027_embed.py").read_text(encoding="utf-8")

for marker in (
    "GSF_V109_ZOOMOUT = True",
    "_gsf_v109_render_video_filters_base=_gsf_render_video_filters",
    "GSF_ZOOMOUT_NATIVE_RENDER",
    "GSF_FINAL_BUTTON_CLICK",
    "GSF_FINAL_STALE_RELEASED",
):
    if marker not in app:
        raise SystemExit("FAIL V109 generated app marker missing: "+marker)

if "on_click=_gsf_v107_queue_final_render" in app:
    raise SystemExit("FAIL final Short still depends on Streamlit callback queueing")

for marker in (
    'id="videoBg"',
    'data-editor-build="2027.6-zoomout"',
    "min=\".8\" max=\"2\"",
    "video.style.objectFit=zoomOut?'contain':'cover'",
    "syncBlurBackground",
):
    if marker not in frontend:
        raise SystemExit("FAIL V109 live zoom-out marker missing: "+marker)

if "gsf_editor_2027_v1086" not in embed:
    raise SystemExit("FAIL V109 component cache-bust missing")
if '"zoom": _clamp(state.get("zoom"), 0.8, 2.0, 1.0)' not in embed:
    raise SystemExit("FAIL V109 render kwargs still clamp zoom to >=1")

# The one-pass split/blur/overlay graph must parse in the production FFmpeg.
ffmpeg=shutil.which("ffmpeg")
if not ffmpeg:
    raise SystemExit("FAIL ffmpeg unavailable for V109 zoom-out smoke")
for fmt in ("9:16 Short","16:9 Originale"):
    vf=build_zoomout_filter(fmt,0.8,0,0,0,1,1)
    cmd=[
        ffmpeg,"-hide_banner","-loglevel","error",
        "-f","lavfi","-i","testsrc2=size=1280x720:rate=30",
        "-t","0.35","-vf",vf,"-an","-f","null","-",
    ]
    run=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
    if run.returncode!=0:
        raise SystemExit("FAIL V109 ffmpeg zoom-out "+fmt+": "+(run.stderr or "")[-1200:])

ast.parse(app)
print("V109 native zoom-out + Short queue contract: PASS")
