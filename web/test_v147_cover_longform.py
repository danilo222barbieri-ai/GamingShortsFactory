from pathlib import Path
import subprocess,tempfile,sys

sys.path.insert(0,"/app/web")
from long_form_director_v141 import build_long_form
from long_form_render_v147 import chapter_windows,render_long_form
from director_pipeline_v142 import apply_pipeline_to_recipe

frontend=Path("/app/web/editor_2027_component/index.html").read_text(encoding="utf-8")
wrapper=Path("/app/web/editor_2027_embed.py").read_text(encoding="utf-8")
for marker in (
    'data-panel="cover"','<span>COVER</span>','AI MIGLIORE','FRAME ATTUALE',
    "coverMode:'Auto'","coverTime:0","coverLocked:false","if(name==='cover')",
):
    assert marker in frontend,marker
for marker in ('"coverMode": "Auto"','"coverTime": 0.0','"coverLocked": False'):
    assert marker in wrapper,marker

pipe={
 "engine":"v142-director-runtime",
 "selected_short":{"render":{"plan":{"edit":{"thumbnail_offset":1.0}}}},
 "render":{"operations":[],"operation_count":0,"publish_guard":"clear"},
 "vision":{"cover_candidates":[{"time":7.0,"path":"auto.jpg","score":.8}]},
 "ab":{},"creator_profile":{},
}
recipe=apply_pipeline_to_recipe(
 {"start":20.0,"duration":15.0,
  "editor_2027_state":{"coverMode":"Manual","coverTime":4.2,"coverLocked":True}},
 pipe,
)
assert abs(float(recipe["ai_thumbnail_offset"])-4.2)<1e-6
assert abs(float(recipe["ai_director_plan"]["edit"]["thumbnail_offset"])-4.2)<1e-6
assert recipe["ai_cover"]["source"]=="game_editor"

moments=[
 {"start":5,"event":"setup","brain_score":.5},
 {"start":35,"event":"kill","brain_score":.8},
 {"start":70,"event":"reaction","brain_score":.7,"reaction":True},
 {"start":100,"event":"kill","brain_score":.9},
 {"start":130,"event":"win","brain_score":1.0},
]
plan=build_long_form(moments,6)
wins=chapter_windows(plan,150,target_seconds=120)
assert wins and sum(x["end"]-x["start"] for x in wins)>60

with tempfile.TemporaryDirectory() as td:
    td=Path(td); src=td/"src.mp4"; out=td/"long.mp4"
    subprocess.run([
      "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
      "-f","lavfi","-i","testsrc2=size=640x360:rate=24",
      "-f","lavfi","-i","sine=frequency=330:sample_rate=44100",
      "-t","12","-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p","-c:a","aac",str(src)
    ],check=True,timeout=60)
    mini={"target_seconds":10,"chapters":[
      {"role":"cold_open","moments":[{"start":2,"brain_score":1}]},
      {"role":"peak","moments":[{"start":7,"brain_score":.9}]},
      {"role":"resolution","moments":[{"start":10,"brain_score":.7}]},
    ]}
    r=render_long_form(src,out,mini,12,target_seconds=10)
    assert r["ok"] and out.is_file() and out.stat().st_size>1024

print("V147 Cover Editor + Long-form Render: PASS")
