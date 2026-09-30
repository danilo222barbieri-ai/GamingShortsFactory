import sys
sys.path.insert(0,"/app/web")

from ai_director_v124 import (
    build_director_plan,
    build_alternates,
    cloud_decision,
    feedback_event,
)
from guardian_intelligence_v124 import diagnose
from quality_control_v124 import inspect_final_video

candidate={
    "rank":1,
    "start":86.0,
    "event_time":94.0,
    "event":"clutch",
    "category":"event",
    "confidence":.93,
    "semantic_confidence":.97,
    "semantic_score":.95,
    "semantic_reaction":.82,
    "focus_x":63.0,
    "focus_y":41.0,
    "focus_confidence":.91,
    "hud_elements":["killfeed","minimap"],
    "caption_safe_y":81.0,
    "subject":"player",
    "score":1.08,
}
plan=build_director_plan(candidate,clip_duration=15,genre="FPS",profile="auto")
if plan.get("engine")!="v124-ai-os":
    raise SystemExit("V124 Director engine marker missing")
if plan["framing"].get("hud_mode")!="Smart Safe" or not plan["framing"].get("smart_reframe"):
    raise SystemExit("V124 Director did not enable real Smart Safe/reframe")
if not plan["text"].get("hook") or "youtube" not in plan["text"].get("social",{}):
    raise SystemExit("V124 Director social/hook plan missing")
if plan["edit"]["trim_end"]<=plan["edit"]["trim_start"]:
    raise SystemExit("V124 Director trim plan invalid")
if not plan["edit"]["replay"]["enabled"]:
    raise SystemExit("V124 clutch should recommend replay")

alts=build_alternates([
    dict(candidate,start=86.0),
    dict(candidate,start=48.0,event="reaction",score=.91),
    dict(candidate,start=120.0,event="kill",score=.88),
], [candidate], clip_duration=15, genre="FPS", limit=2)
if len(alts)!=2 or any(abs(float(x["start"])-86.0)<1 for x in alts):
    raise SystemExit("V124 alternate moment selection failed")
if not all(x.get("director_plan") for x in alts):
    raise SystemExit("V124 alternates missing Director plans")

strong=[
    {"time":10,"kind":"KILL","score":.98},
    {"time":30,"kind":"CLUTCH","score":.97},
    {"time":55,"kind":"VICTORY","score":.96},
]
route=cloud_decision(strong,duration_seconds=90,enabled=True)
if route.get("use_cloud") is not False or route.get("reason")!="local-consensus":
    raise SystemExit("V124 confidence router failed strong-local case")
route2=cloud_decision([{"time":10,"kind":"PEAK","score":.62}],duration_seconds=400,enabled=True)
if route2.get("use_cloud") is not True:
    raise SystemExit("V124 confidence router failed ambiguous case")

fb=feedback_event(candidate,"published",{"zoom":1.2})
if fb.get("action")!="published" or fb.get("event")!="clutch":
    raise SystemExit("V124 feedback event contract failed")

diag=diagnose(
    guardian={"status":"ready","repairs":["final_from_bucket"]},
    quality={"status":"warn","warnings":["audio_near_clipping"],"issues":[]},
    render_status="ready",
)
if diag.get("safe_action")!="normalize_audio_next_render":
    raise SystemExit("V124 Guardian audio diagnosis failed")

missing=inspect_final_video("/tmp/gsf-v124-file-that-does-not-exist.mp4")
if missing.get("status")!="error" or "final_missing_or_empty" not in missing.get("issues",[]):
    raise SystemExit("V124 Quality missing-file guard failed")

print("V124 AI OS core contracts: PASS")
