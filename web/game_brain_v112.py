from __future__ import annotations
import math

def _num(v,default=0.0):
    try:
        x=float(v)
        return x if math.isfinite(x) else float(default)
    except Exception:
        return float(default)

def _clamp(v,lo=0.0,hi=1.0):
    return max(lo,min(hi,_num(v)))

def _diag_for_start(diagnostics,start):
    if not isinstance(diagnostics,dict):
        return {}
    target=_num(start); best=None
    for key,value in diagnostics.items():
        if str(key).startswith("__") or not isinstance(value,dict):
            continue
        try: dist=abs(float(key)-target)
        except Exception: continue
        if best is None or dist<best[0]: best=(dist,value)
    return best[1] if best and best[0]<=0.20 else {}

def _event_label(raw):
    t=str(raw or "").strip().lower().replace("-","_").replace(" ","_")
    if not t: return "highlight"
    rules=(
        ("multi","multi_kill"),("kill","kill"),("victor","victory"),("win","victory"),
        ("goal","goal"),("clutch","clutch"),("boss","boss"),("reaction","reaction"),
        ("explosion","impact"),("impact","impact"),("assist","assist"),("death","death"),
        ("overtake","overtake"),("crash","crash"),("save","save"),("shot","shot"),
    )
    for needle,label in rules:
        if needle in t: return label
    return t[:40]

def _nearest_event(events,start,duration):
    center=_num(start)+max(1.0,_num(duration,15.0))*0.5
    best=None
    for e in events or []:
        if not isinstance(e,dict) or str(e.get("kind","")).upper()=="SILENCE":
            continue
        dist=abs(_num(e.get("time"),-999)-center)
        if best is None or dist<best[0]: best=(dist,e)
    if best and best[0]<=max(3.0,_num(duration,15.0)*0.45):
        return best[1]
    return {}

def _candidate(score,start,diagnostics,duration,events,genre,profile):
    d=_diag_for_start(diagnostics,start)
    f=(d.get("features") or {}) if isinstance(d,dict) else {}
    why=(d.get("why") or {}) if isinstance(d,dict) else {}
    near=_nearest_event(events,start,duration)
    category=str(f.get("moment_category") or why.get("category") or "balanced").lower()
    event=_event_label(f.get("event_type") or why.get("event") or near.get("semantic") or near.get("kind"))
    base=_clamp(score)
    event_score=max(_clamp(f.get("event_score")),_clamp(near.get("score")))
    reaction=max(_clamp(f.get("reaction")),_clamp(f.get("reaction_cue")))
    motion=max(_clamp(f.get("motion_burst")),_clamp(f.get("motion_avg")))
    synergy=_clamp(f.get("synergy")); arc=_clamp(f.get("arc"))
    setup=_clamp(f.get("setup_score")); aftermath=_clamp(f.get("aftermath_score"))
    continuity=_clamp(f.get("continuity"))
    dead=max(_clamp(f.get("dead_ratio")),_clamp(f.get("dead_streak_ratio")))
    semantic_bonus={
        "multi_kill":.14,"victory":.13,"clutch":.13,"goal":.12,"boss":.10,
        "kill":.08,"overtake":.08,"save":.07,"impact":.06,"reaction":.06,
        "assist":.03,"shot":.02,"death":-.03,"highlight":0.0,"peak":0.0,
    }.get(event,.02)
    profile=str(profile or "auto").lower(); pbonus=0.0
    if profile=="reaction": pbonus=.10*reaction+.03*event_score
    elif profile=="action": pbonus=.08*motion+.05*event_score
    elif profile=="director": pbonus=.05*arc+.04*setup+.04*aftermath
    else: pbonus=.03*event_score+.02*arc+.02*reaction
    g=str(genre or "Auto"); gbonus=0.0
    if g in ("FPS","Battle Royale"): gbonus=.025*motion+.025*event_score+.015*reaction
    elif g=="Sports": gbonus=.03*arc+.025*event_score+.015*aftermath
    elif g=="Racing": gbonus=.03*continuity+.025*motion+.015*arc
    quality=(
        .46*base+.14*event_score+.08*reaction+.08*motion+.06*synergy+
        .05*arc+.04*setup+.04*aftermath+.03*continuity+
        semantic_bonus+pbonus+gbonus-.16*dead
    )
    quality=max(0.0,min(1.35,quality))
    signals=[base,event_score,reaction,motion,synergy,arc]
    strong=sum(1 for x in signals if x>=.62)
    confidence=max(.25,min(.99,.40+.075*strong+.18*min(1.0,quality)-.18*dead))
    reason=event.upper().replace("_"," ")
    if event in ("highlight","peak"):
        reason={"reaction":"REAZIONE","action":"AZIONE","story":"STORIA","event":"EVENTO"}.get(category,"HIGHLIGHT")
    return {
        "start":_num(start),"base_score":base,"score":quality,"confidence":confidence,
        "category":category,"event":event,"reason":reason,"dead":dead,
        "original":(float(score),float(start)),
    }

def _overlap(a,b,duration):
    d=max(1.0,_num(duration,15.0))
    a0,a1=a["start"],a["start"]+d; b0,b1=b["start"],b["start"]+d
    return max(0.0,min(a1,b1)-max(a0,b0))/d

def rerank_moments(pool,diagnostics,clip_duration=15,numero_clip=3,profile="auto",genre="Auto",events=None):
    candidates=[]
    for item in pool or []:
        try: score,start=float(item[0]),float(item[1])
        except Exception: continue
        candidates.append(_candidate(score,start,diagnostics,clip_duration,events or [],genre,profile))
    candidates.sort(key=lambda x:(x["score"],x["confidence"],x["base_score"]),reverse=True)
    want=max(1,int(numero_clip or 3)); selected=[]
    while candidates and len(selected)<want:
        best=None
        for c in candidates:
            penalty=0.0
            for old in selected:
                ov=_overlap(c,old,clip_duration)
                same_event=c["event"]==old["event"] and c["event"] not in ("highlight","peak")
                same_cat=c["category"]==old["category"]
                distance=abs(c["start"]-old["start"])
                penalty=max(
                    penalty,
                    .50*ov+(.12 if same_event else 0.0)+(.055 if same_cat else 0.0)+
                    (.08 if distance<clip_duration*.65 else 0.0)
                )
            mmr=c["score"]-penalty
            if best is None or mmr>best[0]: best=(mmr,c)
        if best is None: break
        selected.append(best[1]); candidates.remove(best[1])
    selected.sort(key=lambda x:x["score"],reverse=True)
    chosen=[(float(c["original"][0]),float(c["start"])) for c in selected]
    meta={
        "engine":"game-brain-v112","pool_size":len(pool or []),"selected_count":len(chosen),
        "genre":str(genre or "Auto"),"profile":str(profile or "auto"),
        "selected":[{
            "rank":i+1,"start":round(c["start"],3),"brain_score":round(c["score"],5),
            "base_score":round(c["base_score"],5),"confidence":round(c["confidence"],4),
            "category":c["category"],"event":c["event"],"reason":c["reason"],
        } for i,c in enumerate(selected)],
    }
    return chosen,meta
