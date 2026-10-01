from pathlib import Path
import importlib.util, subprocess, tempfile, sys

sys.path.insert(0,"/app/web")
from one_click_v130 import build_one_click_package
from director_pipeline_v142 import run_director_pipeline, apply_pipeline_to_recipe

rows=[]
for i,start in enumerate((.35,1.1,2.0,3.0),1):
    rows.append({
        "rank":i,"start":start,"event":"kill" if i<4 else "reaction",
        "reason":"TEST MOMENT","confidence":.82,"brain_score":1.0-i*.08,
        "reaction":{"strength":.65 if i==4 else .25},
        "match_state":{"health_pct":18 if i==3 else 80,"ammo":4 if i==3 else 20},
        "director_plan":{
            "edit":{"trim_start":0.0,"trim_end":3.0,"target_duration":3.0,
                    "thumbnail_offset":1.2,
                    "replay":{"enabled":i==3,"center":1.5,"window":.8},
                    "slow_motion":{"enabled":i==3,"center":1.4,"window":.7,"speed":.8}},
            "framing":{"smart_reframe":True,"zoom":1.12,"pan_x":0,"pan_y":0,
                       "hud_mode":"Smart Safe","hud_elements":["health","ammo"]},
            "style":{"audio_mode":"Originale","sound_accent":"impact-hit" if i==3 else "none"},
            "text":{"hook":"CLUTCH IMPOSSIBILE","caption_style":"clean"},
            "quality_rules":{},
        },
    })
brain={"engine":"test","selected":rows,"alternates":[]}
brain["one_click"]=build_one_click_package(brain,clip_duration=3.0,genre="FPS",target_count=3)

with tempfile.TemporaryDirectory() as td:
    td=Path(td); video=td/"input.mp4"
    cmd=["/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
         "-f","lavfi","-i","testsrc2=size=640x360:rate=24",
         "-f","lavfi","-i","sine=frequency=440:sample_rate=44100",
         "-t","4","-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p",
         "-c:a","aac",str(video)]
    subprocess.run(cmd,check=True,timeout=45)
    pipe=run_director_pipeline(
        video,4.0,brain,brain["one_click"],td/"runtime",
        selected_start=2.0,
        creator_event={"signal":"selected","cut_density":.7,"zoom_aggression":.6,
                       "caption_density":1,"replay_preference":1,"cold_open":1},
    )
    assert pipe["ready"]
    assert int(pipe["evidence"]["frames"]["sample_count"])>0
    assert pipe["vision"]["cover_candidates"]
    assert pipe["render"]["operation_count"]>=5
    assert pipe["long_form"]["enabled"]
    assert len(pipe["content_fingerprint"])==64
    recipe=apply_pipeline_to_recipe({"start":2.0,"duration":3.0},pipe)
    assert recipe["ai_render_operations"]
    assert recipe["ai_ab_strategy"] in ("A","B")
    assert recipe["ai_cover"]["path"]
    assert (td/"runtime"/"creator_style.json").is_file()

if len(sys.argv)>1:
    app=Path(sys.argv[1]).read_text(encoding="utf-8")
    for marker in ("_gsf_v142_enrich_recipe","GSF_V142_READY","director_pipeline_v142",
                   'st.session_state["gsf_v142_runtime"]'):
        assert marker in app,marker

print("V142 Director Runtime E2E: PASS")
