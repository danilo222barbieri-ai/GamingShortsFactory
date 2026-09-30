from pathlib import Path
import ast
import sys

sys.path.insert(0,"/app/web")
from game_vision_v108 import (
    build_event_map,
    tag_chosen_moments,
    window_event_map,
    infer_game_genre,
    genre_score_multiplier,
)

app_path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V108_GAME_VISION.py")
app=app_path.read_text(encoding="utf-8")
frontend=Path("/app/web/editor_2027_component/index.html").read_text(encoding="utf-8")
embed=Path("/app/web/editor_2027_embed.py").read_text(encoding="utf-8")
helper=Path("/app/web/game_vision_v108.py").read_text(encoding="utf-8")
worker=Path("/app/web/ai_worker_server.py").read_text(encoding="utf-8")

# --------------------------- pure event engine ---------------------------
n=34
audio=[0.04]*n
peak=[0.05]*n
motion=[0.03]*n
for i,(a,p,m) in {
    7:(0.42,0.58,0.66),
    8:(0.82,0.92,0.91),
    9:(0.68,0.78,0.80),
    20:(0.25,0.96,0.38),
    21:(0.67,0.91,0.55),
    27:(0.76,0.84,0.72),
}.items():
    audio[i]=a;peak[i]=p;motion[i]=m
scan={"step":0.5,"audio":audio,"peak":peak,"motion":motion}
events=build_event_map(scan,max_events=12)
if not events:
    raise SystemExit("FAIL V108 synthetic Event Map is empty")
active=[e for e in events if e.get("kind")!="SILENCE"]
if len(active)<2:
    raise SystemExit("FAIL V108 Event Map did not retain distinct peaks")
for a,b in zip(active,active[1:]):
    if abs(float(b["time"])-float(a["time"]))<1.45:
        raise SystemExit("FAIL V108 Event Map NMS kept duplicate neighboring peaks")
if not any(e.get("kind") in {"ACTION","IMPACT","REACTION","MOVEMENT","AUDIO","PEAK"} for e in active):
    raise SystemExit("FAIL V108 Event Map has no truthful signal event labels")

chosen=[(0.91,2.0),(0.79,8.0),(0.73,12.0)]
diagnostics={
    2.0:{"features":{"event_abs":4.0,"event_type":"kill_event","moment_category":"event","peak_pos":0.5},"why":{"event":"kill_event"}},
    8.0:{"features":{"event_abs":10.5,"event_type":"impact_event","moment_category":"action","peak_pos":0.5},"why":{"event":"impact_event"}},
    12.0:{"features":{"event_abs":14.0,"event_type":"","moment_category":"reaction","peak_pos":0.4},"why":{"category":"reaction"}},
}
tagged=tag_chosen_moments(events,chosen,diagnostics,15)
ranks=sorted({int(e["selected_rank"]) for e in tagged if e.get("selected_rank")})
if ranks!=[1,2,3]:
    raise SystemExit(f"FAIL V108 selected moments are not tagged AI 1/2/3: {ranks}")
if not any(e.get("selected_rank")==1 and e.get("kind")=="KILL" for e in tagged):
    raise SystemExit("FAIL V108 semantic KILL was not preserved from real diagnostics")

window=window_event_map(tagged,clip_start=3.0,clip_duration=6.0,max_events=8)
if any(float(e["time"])<0 or float(e["time"])>6.05 for e in window):
    raise SystemExit("FAIL V108 relative clip Event Map timestamps")
if any(float(e.get("absolute_time",0))<2.95 for e in window):
    raise SystemExit("FAIL V108 Event Map leaked an event outside the clip")

# --------------------------- game profiles -------------------------------
genre_cases={
    "Valorant ranked":"FPS",
    "Fortnite Zero Build":"Battle Royale",
    "Forza Motorsport":"Racing",
    "EA Sports FC 27":"Sports",
    "unknown indie game":"Auto",
}
for label,expected in genre_cases.items():
    actual=infer_game_genre(label)
    if actual!=expected:
        raise SystemExit(f"FAIL V108 genre {label}: {actual} != {expected}")

m=genre_score_multiplier("FPS","action",{
    "motion_avg":0.8,"motion_burst":0.9,"sustained_peak":0.7,
    "continuity":0.6,"synergy":0.8,"arc":0.5,"setup_score":0.5,
    "aftermath_score":0.6,"reaction":0.4,"reaction_cue":0.6,
    "event_score":0.8,"dead_ratio":0.0,"dead_streak_ratio":0.0,
})
if not (0.94<=m<=1.06):
    raise SystemExit("FAIL V108 genre multiplier escaped quality guardrail")

# ----------------------- shared-data architecture ------------------------
for marker in (
    "GSF_V108_GAME_VISION = True",
    "_gsf_v108_rank_base=_gsf_ai_rank_v3",
    "_scan,_scan_hit=_gsf_ai_scan_cached",
    'st.session_state["gsf_v108_event_map"]',
    'st.session_state["gsf_v108_game_genre"]',
    'st.session_state["gsf_v108_chosen_moments"]',
    "event_map_cache_hit",
    "clip_start=float(start)",
    "source_duration=float(durata_effettiva)",
    "source_duration=float(_gsf_manual_duration)",
):
    if marker not in app:
        raise SystemExit(f"FAIL V108 generated app contract missing: {marker}")

if "subprocess" in helper or "ffmpeg" in helper.lower():
    raise SystemExit("FAIL V108 Event Map helper performs media processing instead of reusing prescan")
if 'scan["event_map_v108"]=build_event_map(scan,max_events=18)' not in worker:
    raise SystemExit("FAIL worker does not persist V108 Event Map with prescan")

# -------------------------- Editor contract ------------------------------
for marker in (
    'id="eventLayer"',
    "marker.className='eventMarker'",
    "renderEventMap",
    "marker.onclick",
    "video.currentTime=",
    'id="visionScan"',
    "runVisionScan",
    "GAME VISION · ",
    "visionProfile",
    "visionZones",
    "prefers-reduced-motion",
    "span.textContent='FULL ×2'",
    "playing?'#i-pause':'#i-play'",
    "event.ctrlKey||event.metaKey",
    "state.captionMode='Auto'",
    "state.audioMode='Game Boost'",
    "analyzeVisionFrames",
    "regionMetrics",
    "motionCentroid",
    "visionDetections",
    "GAME VISION · ANALISI VISIVA",
    "FACE CAM",
    "video.videoWidth",
    "ctx.drawImage(video,0,0,w,h)",
):
    if marker not in frontend:
        raise SystemExit(f"FAIL V108 Editor feature missing: {marker}")

for fake in ("AIM LOCK · 00:03","ACTION PEAK · 00:07","KILL EVENT · 00:10","VOICE REACTION · 00:13"):
    if fake in frontend:
        raise SystemExit("FAIL V108 Editor still contains static/fake Event Map data")

for marker in (
    "event_map=_events",
    "vision_profile=_genre",
    "vision_zones=vision_zones_for_genre(_genre)",
    "window_event_map(",
):
    if marker not in embed:
        raise SystemExit(f"FAIL V108 Editor bridge missing: {marker}")

# Event intelligence is metadata, never part of mutable editor snapshots.
state_block=embed.split("def editor_2027_initial_state",1)[1].split("def editor_2027_clip_bounds",1)[0]
if "event_map" in state_block or "vision_zones" in state_block:
    raise SystemExit("FAIL V108 static intelligence metadata pollutes Undo/Redo editor state")

# Generated app must still parse cleanly.
ast.parse(app)
print("V108 Game Vision + Event Map contract: PASS")

if "fetch(" in frontend.split("async function analyzeVisionFrames",1)[1].split("function renderVisionDetections",1)[0]:
    raise SystemExit("FAIL visual Game Vision calls the network instead of analyzing local video frames")
if "96,h=54" not in frontend:
    raise SystemExit("FAIL visual Game Vision is not using the lightweight low-resolution scan")
