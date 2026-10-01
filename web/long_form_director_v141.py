from __future__ import annotations


def _score(x):
    try:return float(x.get("brain_score",x.get("score",0)) or 0)
    except Exception:return 0.0


def build_long_form(moments,target_minutes=8):
    """Build a 6–10 minute gaming story from the same Director evidence used by Shorts."""
    rows=[dict(x) for x in (moments or []) if isinstance(x,dict)]
    target=max(360,min(600,int(float(target_minutes or 8)*60)))
    rows.sort(key=lambda x:float(x.get("start",0) or 0))
    if not rows:return {"engine":"v141-long-form","enabled":False,"chapters":[]}
    strongest=sorted(rows,key=_score,reverse=True)
    cold=strongest[0]
    chapters=[{"role":"cold_open","moments":[cold],"target":min(18,target*.04)}]
    used={id(cold)}
    buckets=[("setup",.16),("escalation",.28),("peak",.25),("reaction",.14),("resolution",.13)]
    n=len(rows)
    for role,weight in buckets:
        candidates=[]
        for i,x in enumerate(rows):
            if id(x) in used:continue
            pos=i/max(1,n-1)
            if role=="setup" and pos<=.30:candidates.append(x)
            elif role=="escalation" and .15<=pos<=.70:candidates.append(x)
            elif role=="peak" and x in strongest[:max(2,n//3)]:candidates.append(x)
            elif role=="reaction" and (x.get("reaction") or "reaction" in str(x.get("event","")).lower()):candidates.append(x)
            elif role=="resolution" and pos>=.65:candidates.append(x)
        candidates=sorted(candidates,key=_score,reverse=True)[:max(1,min(5,len(candidates)))]
        used.update(id(x) for x in candidates)
        chapters.append({"role":role,"moments":sorted(candidates,key=lambda x:float(x.get("start",0) or 0)),
                         "target":round(target*weight,1)})
    return {"engine":"v141-long-form","enabled":len(rows)>=4,"target_seconds":target,
            "chapters":chapters,"reuse_short_moments":True,"chronology_inside_chapters":True,
            "strategy":"story_strength_then_chronology"}


def compile_long_form_operations(plan):
    ops=[]
    for ci,ch in enumerate((plan or {}).get("chapters") or []):
        for x in ch.get("moments") or []:
            ops.append({"op":"insert_moment","chapter":ci,"role":ch.get("role"),"start":x.get("start"),
                        "event":x.get("event"),"score":_score(x)})
        if ci and ch.get("moments"):ops.append({"op":"chapter_transition","chapter":ci,"style":"minimal"})
    return ops
