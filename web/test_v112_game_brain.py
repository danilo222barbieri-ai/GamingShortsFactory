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

app=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V112_GAME_BRAIN.py").read_text(encoding="utf-8")
embed=Path("/app/web/editor_2027_embed.py").read_text(encoding="utf-8")
front=Path("/app/web/editor_2027_component/index.html").read_text(encoding="utf-8")
for marker in ("GSF_V112_GAME_BRAIN","_pool_target=max(8","__brain_v112__","gsf_v112_brain_context","shortlist_target=8"):
    if marker not in app: raise SystemExit("V112 app contract missing: "+marker)
for marker in ("brain_context=_brain_hint","gsf_v112_brain_context"):
    if marker not in embed: raise SystemExit("V112 editor bridge missing: "+marker)
for marker in ("let brainContext={};","AI CONSIGLIO","brainApply","args.brain_context"):
    if marker not in front: raise SystemExit("V112 editor UI missing: "+marker)
compile(app,"<v112>","exec")
print("V112 Game Brain + Editor intelligence: PASS")
