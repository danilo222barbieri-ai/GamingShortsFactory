from pathlib import Path
import subprocess, tempfile, sys

sys.path.insert(0,"/app/web")
from cinematic_render_v125 import probe_media
from director_render_exec_v143 import execute_director_operations

with tempfile.TemporaryDirectory() as td:
    td=Path(td); src=td/"src.mp4"; out=td/"out.mp4"
    subprocess.run([
        "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i","testsrc2=size=640x360:rate=24",
        "-f","lavfi","-i","sine=frequency=660:sample_rate=44100",
        "-t","4","-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p",
        "-c:a","aac",str(src)
    ],check=True,timeout=45)
    ops=[
        {"op":"pattern_interrupt","start":1.0,"duration":.8,"mode":"speed_up_or_micro_cut"},
        {"op":"cold_open","duration":.6,"source":"payoff"},
        {"op":"cover","time":2.5,"path":"x.jpg","score":.9},
        {"op":"smart_ending","mode":"payoff","tail":.35},
    ]
    result=execute_director_operations(src,out,ops,recipe_start=0.0)
    assert result["ok"] and result["count"]>=2
    assert out.is_file() and out.stat().st_size>1024
    before=probe_media(src); after=probe_media(out)
    assert after["duration"]>3.0
    assert "cold_open" in result["applied"]
    assert "smart_ending" in result["applied"]

if len(sys.argv)>1:
    app=Path(sys.argv[1]).read_text(encoding="utf-8")
    for marker in ("director_render_exec_v143","GSF_V143_RENDER_APPLIED","ai_render_operations",
                   "Gaming Shorts Factory · V143 Render Execution"):
        assert marker in app,marker

print("V143 Render Execution: PASS")
