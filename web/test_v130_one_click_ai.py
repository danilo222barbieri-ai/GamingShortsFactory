from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0,"/app/web")

from ai_director_v124 import build_director_plan
from one_click_v130 import ENGINE_VERSION, build_one_click_package

app_path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V130_ONE_CLICK_AI.py")
app=app_path.read_text(encoding="utf-8")
editor=Path("/app/web/editor_2027_component/index.html").read_text(encoding="utf-8")
brain_src=Path("/app/web/game_brain_v112.py").read_text(encoding="utf-8")

rows=[]
events=[
    ("clutch",.94,18.0,{"focus_x":58,"focus_y":42,"focus_confidence":.91,"hud_elements":["minimap","killfeed"],"caption_safe_y":79}),
    ("goal",.90,48.0,{"focus_x":50,"focus_y":45,"focus_confidence":.86,"hud_elements":["scoreboard","timer"],"caption_safe_y":81}),
    ("overtake",.88,78.0,{"focus_x":63,"focus_y":52,"focus_confidence":.83,"hud_elements":["speedometer","lap_counter"],"caption_safe_y":75}),
]
for rank,(event,conf,start,extra) in enumerate(events,1):
    moment={
        "rank":rank,
        "start":start,
        "brain_score":conf,
        "confidence":conf,
        "event":event,
        "reason":event.upper(),
        "semantic_confidence":conf-.03,
        "semantic_reaction":.72 if event=="clutch" else .25,
        "event_time":start+7.0,
        "learning_multiplier":1.02,
        **extra,
    }
    moment["director_plan"]=build_director_plan(moment,clip_duration=15.0,genre="Auto",profile="auto")
    rows.append(moment)

brain={
    "engine":"game-brain-v127-learning",
    "selected":rows,
    "alternates":[],
    "genre":"Auto",
    "profile":"auto",
}
package=build_one_click_package(brain,clip_duration=15.0,genre="Auto",profile="auto")

if package.get("engine")!=ENGINE_VERSION:
    raise SystemExit("V130 engine mismatch")
if package.get("prepared_count")!=3 or len(package.get("shorts") or [])!=3:
    raise SystemExit("V130 did not prepare three mounted Shorts")
if package.get("encoding_policy")!="render-only-after-user-selection":
    raise SystemExit("V130 lazy encoding cost policy regressed")
for short in package["shorts"]:
    if not short.get("mounted") or short.get("status")!="mounted":
        raise SystemExit("V130 short package not mounted")
    if short.get("render",{}).get("strategy")!="encode-on-selection":
        raise SystemExit("V130 render strategy regressed")
    if not short.get("editor_actions"):
        raise SystemExit("V130 Editor Assistant actions missing")
    if not short.get("second_opinion",{}).get("explanation"):
        raise SystemExit("V130 second opinion missing")
    if set((short.get("social") or {}).keys())!={"youtube","tiktok","instagram"}:
        raise SystemExit("V130 social optimizer package incomplete")
    if not short.get("quality_gate",{}).get("before_publish"):
        raise SystemExit("V130 QC gate missing")

for marker in (
    "def _gsf_v130_short_for_start(",
    '_recipe["one_click_engine"]="v130-one-click-ai"',
    '"one_click_v130"',
    "AI SECOND OPINION",
    "ONE CLICK AI",
    "GSF_V130_PACKAGE_WARN",
):
    if marker not in app:
        raise SystemExit("V130 app marker missing: "+marker)

for marker in (
    "const textPlan=(plan.text&&typeof plan.text==='object')?plan.text:{}",
    "const assistantActions=Array.isArray(plan.assistant_actions)?plan.assistant_actions:[]",
    "const captionStyle=String(textPlan.caption_style||'clean').toLowerCase()",
    "state.captionMode='Auto'",
    "state.captionOn=true",
    "suggerimenti:",
):
    if marker not in editor:
        raise SystemExit("V130 Editor marker missing: "+marker)

for marker in (
    "from one_click_v130 import build_one_click_package as _build_one_click_package",
    'meta["one_click"]=_build_one_click_package(',
):
    if marker not in brain_src:
        raise SystemExit("V130 Game Brain marker missing: "+marker)

compile(app,str(app_path),"exec")
print("V130 One Click AI contracts: PASS")

# V131 invisible Director intelligence contract
assert "_director_intelligence" in Path("/app/web/one_click_v130.py").read_text(encoding="utf-8")
assert '"director_intelligence":intelligence' in Path("/app/web/one_click_v130.py").read_text(encoding="utf-8")
assert '"retention_prediction"' in Path("/app/web/one_click_v130.py").read_text(encoding="utf-8")
assert '"creator_learning"' in Path("/app/web/one_click_v130.py").read_text(encoding="utf-8")
assert '"game_specific"' in Path("/app/web/one_click_v130.py").read_text(encoding="utf-8")
assert '"ab_variants"' in Path("/app/web/one_click_v130.py").read_text(encoding="utf-8")


# V131 session-wide Director intelligence contract
src=Path("/app/web/one_click_v130.py").read_text(encoding="utf-8")
for marker in ("_session_intelligence","duplicate_detector","series_ai","best_of_session","long_form","content_memory","safety_privacy","copyright_audio","visual_cleanup","trend_adaptation","content_calendar","post_publish_learning"):
    assert marker in src, marker


# V132 game recognition + wired session intelligence
src=Path("/app/web/one_click_v130.py").read_text(encoding="utf-8")
for marker in ("_recognize_game","game_recognition","semantic_hud_context","session_intelligence"):
    assert marker in src, marker
