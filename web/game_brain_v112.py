from __future__ import annotations
import math

from ai_director_v124 import attach_director_plans, build_alternates
from feedback_learning_v127 import load_model as _load_learning_model, event_multiplier as _learning_multiplier

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

def _candidate(score,start,diagnostics,duration,events,genre,profile,semantic_injected=False,learning_model=None):
    d=_diag_for_start(diagnostics,start)
    f=(d.get("features") or {}) if isinstance(d,dict) else {}
    why=(d.get("why") or {}) if isinstance(d,dict) else {}
    near=_nearest_event(events,start,duration)
    category=str(f.get("moment_category") or why.get("category") or near.get("category") or "balanced").lower()
    event=_event_label(f.get("event_type") or why.get("event") or near.get("semantic") or near.get("kind"))
    base=_clamp(score)
    event_score=max(_clamp(f.get("event_score")),_clamp(near.get("score")),_clamp(near.get("semantic_score")))
    reaction=max(_clamp(f.get("reaction")),_clamp(f.get("reaction_cue")),_clamp(near.get("semantic_reaction")))
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
    semantic_conf=_clamp(near.get("semantic_confidence"))
    semantic_excite=_clamp(near.get("semantic_excitement"))
    semantic_signal=max(_clamp(near.get("semantic_score")),.70*semantic_conf+.30*semantic_excite)
    event_time=_num(near.get("time"),_num(start)+max(1.0,_num(duration,15.0))*.52)
    semantic_reaction=_clamp(near.get("semantic_reaction"))
    focus_conf=_clamp(near.get("focus_confidence"))
    focus_x=max(0.0,min(100.0,_num(near.get("focus_x"),50.0)))
    focus_y=max(0.0,min(100.0,_num(near.get("focus_y"),43.0)))
    caption_safe_y=max(15.0,min(88.0,_num(near.get("caption_safe_y"),78.0)))
    hud_elements=[]
    for label in near.get("hud_elements") or []:
        label=str(label or "").strip().lower().replace(" ","_")[:32]
        if label and label not in hud_elements:
            hud_elements.append(label)
        if len(hud_elements)>=8:
            break
    subject=str(near.get("subject") or "")[:80]
    quality=(
        .42*base+.14*event_score+.08*reaction+.08*motion+.06*synergy+
        .05*arc+.04*setup+.04*aftermath+.03*continuity+
        .10*semantic_signal+semantic_bonus+pbonus+gbonus-.16*dead
    )
    if semantic_injected:
        quality+=.035*semantic_signal
    learning_mult=_learning_multiplier(learning_model or {},event)
    quality*=learning_mult
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
        "semantic_injected":bool(semantic_injected),
        "semantic_confidence":semantic_conf,
        "semantic_score":semantic_signal,
        "semantic_reaction":semantic_reaction,
        "event_time":event_time,
        "focus_x":focus_x,
        "focus_y":focus_y,
        "focus_confidence":focus_conf,
        "hud_elements":hud_elements,
        "caption_safe_y":caption_safe_y,
        "subject":subject,
        "learning_multiplier":learning_mult,
        "original":(float(score),float(start)),
    }

def _inject_semantic_pool(pool,events,duration,max_injected=6):
    base=[]
    for item in pool or []:
        try:
            base.append((float(item[0]),float(item[1])))
        except Exception:
            continue
    existing=[x[1] for x in base]
    injected=[]
    d=max(1.0,_num(duration,15.0))
    lead=min(6.0,max(2.0,d*.32))
    rows=[]
    for e in events or []:
        if not isinstance(e,dict):
            continue
        source=str(e.get("source") or "").lower()
        if "gemini" not in source:
            continue
        conf=_clamp(e.get("semantic_confidence"))
        sem=_clamp(e.get("semantic_score"))
        excite=_clamp(e.get("semantic_excitement"))
        signal=max(sem,.70*conf+.30*excite)
        if conf<.62 or signal<.58:
            continue
        t=_num(e.get("time"),-1.0)
        if t<0:
            continue
        start=max(0.0,t-lead)
        rows.append((signal,conf,start,e))
    rows.sort(key=lambda x:(x[0],x[1]),reverse=True)
    min_gap=max(1.5,d*.22)
    for signal,conf,start,event in rows:
        if any(abs(start-old)<min_gap for old in existing):
            continue
        synthetic=min(.99,.70+.22*signal+.07*conf)
        base.append((synthetic,start))
        existing.append(start)
        injected.append({
            "start":start,
            "event":_event_label(event.get("semantic") or event.get("kind")),
            "confidence":conf,
            "semantic_score":signal,
            "source":str(event.get("source") or "gemini-v114"),
        })
        if len(injected)>=max(1,int(max_injected)):
            break
    return base,injected

def _overlap(a,b,duration):
    d=max(1.0,_num(duration,15.0))
    a0,a1=a["start"],a["start"]+d; b0,b1=b["start"],b["start"]+d
    return max(0.0,min(a1,b1)-max(a0,b0))/d

def rerank_moments(pool,diagnostics,clip_duration=15,numero_clip=3,profile="auto",genre="Auto",events=None):
    events=events or []
    learning_model=_load_learning_model()
    augmented_pool,injected=_inject_semantic_pool(pool,events,clip_duration,max_injected=6)
    injected_starts=[float(x["start"]) for x in injected]
    candidates=[]
    for item in augmented_pool:
        try: score,start=float(item[0]),float(item[1])
        except Exception: continue
        is_injected=any(abs(start-x)<0.001 for x in injected_starts)
        candidates.append(_candidate(
            score,start,diagnostics,clip_duration,events,genre,profile,
            semantic_injected=is_injected,learning_model=learning_model
        ))
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
    director_selected=attach_director_plans(
        selected,clip_duration=clip_duration,genre=genre,profile=profile
    )
    alternates=build_alternates(
        candidates,director_selected,
        clip_duration=clip_duration,genre=genre,profile=profile,limit=3
    )
    meta={
        "engine":"game-brain-v127-learning",
        "pool_size":len(pool or []),
        "augmented_pool_size":len(augmented_pool),
        "semantic_injected_count":len(injected),
        "semantic_injected":injected,
        "selected_count":len(chosen),
        "genre":str(genre or "Auto"),"profile":str(profile or "auto"),
        "learning":{
            "engine":str((learning_model or {}).get("engine") or "v127-learning-ranker"),
            "total_feedback":int((learning_model or {}).get("total_feedback",0) or 0),
        },
        "selected":[{
            "rank":i+1,"start":round(c["start"],3),"brain_score":round(c["score"],5),
            "base_score":round(c["base_score"],5),"confidence":round(c["confidence"],4),
            "category":c["category"],"event":c["event"],"reason":c["reason"],
            "semantic_injected":bool(c.get("semantic_injected")),
            "semantic_confidence":round(_num(c.get("semantic_confidence")),4),
            "semantic_score":round(_num(c.get("semantic_score")),4),
            "semantic_reaction":round(_num(c.get("semantic_reaction")),4),
            "event_time":round(_num(c.get("event_time"),c.get("start")),3),
            "focus_x":round(_num(c.get("focus_x"),50.0),2),
            "focus_y":round(_num(c.get("focus_y"),43.0),2),
            "focus_confidence":round(_num(c.get("focus_confidence")),4),
            "hud_elements":list(c.get("hud_elements") or []),
            "caption_safe_y":round(_num(c.get("caption_safe_y"),78.0),2),
            "subject":str(c.get("subject") or ""),
            "learning_multiplier":round(_num(c.get("learning_multiplier"),1.0),6),
            "director_plan":dict(c.get("director_plan") or {}),
        } for i,c in enumerate(director_selected)],
        "alternates":[{
            "rank":i+1,
            "start":round(_num(c.get("start")),3),
            "brain_score":round(_num(c.get("score")),5),
            "confidence":round(_num(c.get("confidence")),4),
            "event":str(c.get("event") or "highlight"),
            "reason":str(c.get("reason") or "HIGHLIGHT"),
            "director_plan":dict(c.get("director_plan") or {}),
        } for i,c in enumerate(alternates)],
    }
    return chosen,meta
