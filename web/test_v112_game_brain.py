from pathlib import Path
import sys
sys.path.insert(0,"/app/web")
from game_brain_v112 import rerank_moments

def diag(cat,event,event_score,reaction,motion,dead=0.0,arc=.5,setup=.5,after=.5,synergy=.5,continuity=.5):
    return {"features":{
        "moment_category":cat,"event_type":event,"event_score":event_score,
        "reaction":reaction,"reaction_cue":reaction,"motion_burst":motion,
        "dead_ratio":dead,"dead_streak_ratio":dead,"arc":arc,
        "setup_score":setup,"aftermath_score":after,"synergy":synergy,
        "continuity":continuity,
    }}

pool=[(.84,10.0),(.83,13.0),(.82,48.0),(.80,82.0),(.78,120.0)]
diagnostics={
    "10.0":diag("action","kill",.95,.45,.92),
    "13.0":diag("action","kill",.94,.44,.91),
    "48.0":diag("reaction","reaction",.78,.98,.50),
    "82.0":diag("story","victory",.92,.72,.55,arc=.95,setup=.8,after=.9),
    "120.0":diag("balanced","peak",.65,.40,.65,dead=.55),
}
chosen,meta=rerank_moments(pool,diagnostics,clip_duration=15,numero_clip=3,profile="auto",genre="FPS",events=[])
starts=[round(x[1],1) for x in chosen]
if len(chosen)!=3 or 10.0 not in starts or 48.0 not in starts or 82.0 not in starts or 13.0 in starts:
    raise SystemExit("V112 diversity/semantic ranking failed: "+repr(starts))
if meta.get("pool_size")!=5 or len(meta.get("selected") or [])!=3:
    raise SystemExit("V112 metadata contract failed")
if not all("confidence" in x and "reason" in x for x in meta["selected"]):
    raise SystemExit("V112 confidence/explanation missing")

# V115: a strong semantic event absent from the local shortlist must be able
# to enter the final top three.
semantic_pool=[(.86,10.0),(.84,48.0),(.72,140.0)]
semantic_diagnostics={
    "10.0":diag("action","kill",.90,.40,.90),
    "48.0":diag("reaction","reaction",.78,.96,.45),
    "140.0":diag("balanced","peak",.55,.30,.50,dead=.25),
}
semantic_events=[
    {
        "time":94.0,
        "kind":"CLUTCH",
        "semantic":"clutch",
        "category":"event",
        "semantic_confidence":.97,
        "semantic_excitement":.98,
        "semantic_reaction":.82,
        "semantic_score":.95,
        "score":.95,
        "subject":"player",
        "focus_x":63.0,
        "focus_y":41.0,
        "focus_confidence":.93,
        "hud_elements":["killfeed","minimap"],
        "caption_safe_y":81.0,
        "source":"gemini-v117",
    }
]
semantic_chosen,semantic_meta=rerank_moments(
    semantic_pool,semantic_diagnostics,
    clip_duration=15,numero_clip=3,profile="auto",genre="FPS",
    events=semantic_events,
)
semantic_starts=[float(x[1]) for x in semantic_chosen]
if not any(86.0<=x<=92.5 for x in semantic_starts):
    raise SystemExit("V115 semantic candidate injection failed: "+repr(semantic_starts))
if semantic_meta.get("semantic_injected_count",0)<1:
    raise SystemExit("V115 semantic injection metadata missing")
if not any(x.get("semantic_injected") and x.get("event")=="clutch" for x in semantic_meta.get("selected",[])):
    raise SystemExit("V115 injected clutch did not survive final ranking")

clutch_rows=[x for x in semantic_meta.get("selected",[]) if x.get("event")=="clutch"]
if not clutch_rows:
    raise SystemExit("V117 clutch metadata row missing")
clutch=clutch_rows[0]
if clutch.get("focus_x")!=63.0 or clutch.get("focus_y")!=41.0 or clutch.get("focus_confidence")<.9:
    raise SystemExit("V117 semantic focus metadata did not reach selected clip: "+repr(clutch))
if clutch.get("hud_elements")!=["killfeed","minimap"] or clutch.get("caption_safe_y")!=81.0:
    raise SystemExit("V117 HUD/caption-safe metadata did not reach selected clip: "+repr(clutch))
if clutch.get("subject")!="player":
    raise SystemExit("V117 subject metadata did not reach selected clip")

app=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V112_GAME_BRAIN.py").read_text(encoding="utf-8")
embed=Path("/app/web/editor_2027_embed.py").read_text(encoding="utf-8")
front=Path("/app/web/editor_2027_component/index.html").read_text(encoding="utf-8")
for marker in ("GSF_V112_GAME_BRAIN","_pool_target=max(8","__brain_v112__","gsf_v112_brain_context","shortlist_target=8"):
    if marker not in app: raise SystemExit("V112 app contract missing: "+marker)
for marker in ("brain_context=_brain_hint","gsf_v112_brain_context"):
    if marker not in embed: raise SystemExit("V112 editor bridge missing: "+marker)
for marker in ("let brainContext={};","AI CONSIGLIO","brainApply","args.brain_context","semanticFocusFromBrain","semanticHudDetections","AI+LOCALE","caption_safe_y","hud_elements"):
    if marker not in front: raise SystemExit("V112 editor UI missing: "+marker)
compile(app,"<v112>","exec")
print("V117 Game Brain + semantic Editor intelligence: PASS")
