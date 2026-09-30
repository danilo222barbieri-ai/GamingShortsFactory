"""V108 Game Vision helpers.

Pure, low-cost functions that reuse the existing 0.5 s AI prescan.  No media
decode happens here: the same audio/peak/motion arrays used to rank the three
AI moments feed Event Map and Game Vision.
"""

from __future__ import annotations

import math
import re


def _num(value, default=0.0):
    try:
        value=float(value)
        return value if math.isfinite(value) else float(default)
    except Exception:
        return float(default)


def _clean_series(scan, key):
    raw=(scan or {}).get(key) or []
    return [max(0.0,min(1.0,_num(x))) for x in raw]


def infer_game_genre(value):
    """Return a conservative editor/ranking profile from a game/title string."""
    text=re.sub(r"[^a-z0-9]+"," ",str(value or "").lower()).strip()
    if not text:
        return "Auto"

    # Specific Battle Royale titles before broad shooter terms.
    battle=(
        "fortnite","pubg","playerunknown","warzone","apex legends",
        "free fire","naraka","realm royale"
    )
    if any(x in text for x in battle):
        return "Battle Royale"

    racing=(
        "forza","gran turismo","assetto corsa","iracing","need for speed",
        "f1 20","formula 1","motogp","wrc","dirt rally","the crew",
        "project cars","racing"
    )
    if any(x in text for x in racing):
        return "Racing"

    sports=(
        "ea sports fc","fc 24","fc 25","fc 26","fc 27","fifa","efootball",
        "pes ","nba 2k","madden","nhl ","football","soccer","calcio",
        "rocket league"
    )
    if any(x in text for x in sports):
        return "Sports"

    fps=(
        "valorant","counter strike","counterstrike","cs2","call of duty",
        "overwatch","rainbow six","r6 siege","battlefield","doom",
        "quake","halo","destiny","the finals","xdefiant","fps"
    )
    if any(x in text for x in fps):
        return "FPS"

    return "Auto"


def genre_score_multiplier(genre, profile, features):
    """Small, bounded genre bias applied after the existing mature AI score."""
    g=str(genre or "Auto")
    f=features or {}
    if g=="Auto":
        return 1.0

    motion=_num(f.get("motion_avg"))
    motion_burst=_num(f.get("motion_burst"))
    sustained=_num(f.get("sustained_peak"))
    continuity=_num(f.get("continuity"))
    synergy=_num(f.get("synergy"))
    arc=_num(f.get("arc"))
    setup=_num(f.get("setup_score"))
    aftermath=_num(f.get("aftermath_score"))
    reaction=max(_num(f.get("reaction")),_num(f.get("reaction_cue")))
    event=_num(f.get("event_score"))
    dead=max(_num(f.get("dead_ratio")),_num(f.get("dead_streak_ratio")))

    if g in {"FPS","Battle Royale"}:
        fit=0.24*motion_burst+0.20*event+0.18*synergy+0.14*reaction+0.12*motion+0.12*sustained
    elif g=="Racing":
        fit=0.28*continuity+0.24*sustained+0.22*motion+0.14*synergy+0.12*arc
    elif g=="Sports":
        fit=0.24*arc+0.20*setup+0.20*aftermath+0.16*sustained+0.12*event+0.08*synergy
    else:
        fit=0.0

    # At most ~ +/- 6%. Genre helps resolve close calls; it never overrules
    # a clearly stronger moment from the base engine.
    centered=max(-1.0,min(1.0,(fit-0.42)/0.42))
    multiplier=1.0+0.055*centered-0.025*dead
    if str(profile or "")=="reaction":
        # Reaction mode remains primarily voice/reaction-driven.
        multiplier=1.0+(multiplier-1.0)*0.55
    return max(0.94,min(1.06,multiplier))


def _signal_rows(scan):
    audio=_clean_series(scan,"audio")
    peak=_clean_series(scan,"peak")
    motion=_clean_series(scan,"motion")
    n=min(len(audio),len(peak),len(motion))
    step=max(0.05,_num((scan or {}).get("step"),0.5))
    rows=[]
    prev_audio=audio[0] if n else 0.0
    for i in range(n):
        a,p,m=audio[i],peak[i],motion[i]
        da=max(0.0,a-prev_audio)
        prev_audio=a
        instant=0.38*a+0.34*m+0.18*p+0.10*min(a,m)
        rows.append({
            "i":i,"time":i*step,"audio":a,"peak":p,"motion":m,
            "audio_jump":da,"instant":instant,
        })
    return rows,step


def build_event_map(scan, max_events=18):
    """Derive a compact truthful Event Map from the existing prescan arrays."""
    rows,step=_signal_rows(scan)
    n=len(rows)
    if n<3:
        return []

    pre_n=max(1,int(round(2.0/step)))
    post_n=max(1,int(round(3.0/step)))
    scored=[]
    for i,row in enumerate(rows):
        pre=rows[max(0,i-pre_n):i]
        post=rows[i+1:min(n,i+post_n+1)]
        pre_avg=sum(0.50*x["audio"]+0.50*x["motion"] for x in pre)/len(pre) if pre else 0.0
        post_avg=sum(0.46*x["audio"]+0.42*x["motion"]+0.12*x["peak"] for x in post)/len(post) if post else 0.0
        surge=max(0.0,row["instant"]-pre_avg)
        synergy=min(row["audio"],row["motion"])
        score=(
            0.38*row["instant"]+
            0.24*surge+
            0.18*post_avg+
            0.12*synergy+
            0.08*row["motion"]
        )
        if surge<0.10 and row["instant"]<0.70:
            score*=0.72
        score=max(0.0,min(1.0,score))
        scored.append((score,surge,post_avg))

    # Adaptive threshold: normalized source signals vary by title/capture.
    ranked=sorted((x[0] for x in scored),reverse=True)
    qidx=min(len(ranked)-1,max(0,int(round(len(ranked)*0.16))))
    adaptive=ranked[qidx] if ranked else 0.0
    threshold=max(0.38,min(0.62,adaptive*0.86))

    active=[]
    for i,row in enumerate(rows):
        score,surge,post_avg=scored[i]
        if score<threshold:
            continue
        left=max(0,i-2); right=min(n,i+3)
        if score+1e-9 < max(scored[j][0] for j in range(left,right)):
            continue

        a,p,m=row["audio"],row["peak"],row["motion"]
        burst=max(0.0,p-a)
        if m>=0.58 and a>=0.34:
            kind="ACTION"
        elif burst>=0.26 or (row["audio_jump"]>=0.24 and p>=0.56):
            kind="IMPACT"
        elif row["audio_jump"]>=0.20 and a>=0.48:
            kind="REACTION"
        elif m>=0.62:
            kind="MOVEMENT"
        elif a>=0.64:
            kind="AUDIO"
        else:
            kind="PEAK"

        active.append({
            "time":round(row["time"],3),
            "score":round(score,4),
            "kind":kind,
            "audio":round(a,4),
            "peak":round(p,4),
            "motion":round(m,4),
            "surge":round(surge,4),
            "post":round(post_avg,4),
        })

    # Non-maximum suppression prevents one firefight/explosion from becoming
    # six nearly identical markers.
    active.sort(key=lambda x:x["score"],reverse=True)
    kept=[]
    min_gap=max(1.5,step*3.0)
    for event in active:
        if any(abs(event["time"]-old["time"])<min_gap for old in kept):
            continue
        kept.append(event)
        if len(kept)>=max(4,int(max_events)):
            break

    # Long genuinely quiet stretches are useful navigation landmarks too.
    silence=[]
    run_start=None
    for i,row in enumerate(rows+[{"audio":1.0,"motion":1.0,"time":n*step}]):
        quiet=row["audio"]<0.10 and row["motion"]<0.07
        if quiet and run_start is None:
            run_start=i
        elif not quiet and run_start is not None:
            run_len=i-run_start
            secs=run_len*step
            if secs>=2.5:
                mid=(run_start+(run_len-1)/2.0)*step
                silence.append({
                    "time":round(mid,3),
                    "duration":round(secs,3),
                    "score":round(min(0.42,0.18+secs/30.0),4),
                    "kind":"SILENCE",
                    "audio":0.0,"peak":0.0,"motion":0.0,
                })
            run_start=None

    # Reserve a few slots for silence without crowding out meaningful peaks.
    silence=sorted(silence,key=lambda x:x.get("duration",0),reverse=True)[:3]
    all_events=kept+silence
    all_events.sort(key=lambda x:x["time"])
    return all_events[:max(1,int(max_events))]


def _diag_for_start(diagnostics, start):
    if not isinstance(diagnostics,dict):
        return {}
    target=_num(start)
    best=None
    for key,value in diagnostics.items():
        if str(key).startswith("__") or not isinstance(value,dict):
            continue
        try:
            dist=abs(float(key)-target)
        except Exception:
            continue
        if best is None or dist<best[0]:
            best=(dist,value)
    return best[1] if best and best[0]<=0.15 else {}


def _semantic_label(value, fallback=""):
    raw=str(value or "").strip().lower().replace("-","_").replace(" ","_")
    if not raw:
        return str(fallback or "")
    rules=(
        ("kill","KILL"),("goal","GOAL"),("victor","VICTORY"),("win","VICTORY"),
        ("reaction","REACTION"),("impact","IMPACT"),("explosion","IMPACT"),
        ("shot","SHOT"),("death","DEATH"),("assist","ASSIST"),
    )
    for needle,label in rules:
        if needle in raw:
            return label
    return str(fallback or "EVENT")


def tag_chosen_moments(events, chosen, diagnostics, clip_duration):
    """Attach AI #1/#2/#3 to the same physical events used by ranking."""
    out=[dict(x) for x in (events or []) if isinstance(x,dict)]
    duration=max(1.0,_num(clip_duration,15.0))

    for rank,item in enumerate(chosen or [],1):
        try:
            score,start=float(item[0]),float(item[1])
        except Exception:
            continue
        diag=_diag_for_start(diagnostics,start)
        features=(diag.get("features") or {}) if isinstance(diag,dict) else {}
        why=(diag.get("why") or {}) if isinstance(diag,dict) else {}

        event_abs=features.get("event_abs")
        if event_abs is None:
            peak_pos=max(0.0,min(1.0,_num(features.get("peak_pos"),0.5)))
            event_abs=start+duration*peak_pos
        event_abs=max(0.0,_num(event_abs,start+duration*0.5))

        semantic=str(features.get("event_type") or why.get("event") or "")
        category=str(features.get("moment_category") or why.get("category") or "balanced")
        label=_semantic_label(semantic)
        if not label:
            label={
                "reaction":"REACTION","action":"ACTION","story":"STORY",
                "event":"EVENT","balanced":"HIGHLIGHT"
            }.get(category,"HIGHLIGHT")

        nearest=None
        for idx,event in enumerate(out):
            if event.get("kind")=="SILENCE":
                continue
            dist=abs(_num(event.get("time"))-event_abs)
            if nearest is None or dist<nearest[0]:
                nearest=(dist,idx)
        max_match=max(2.25,min(4.0,duration*0.20))
        if nearest and nearest[0]<=max_match:
            event=out[nearest[1]]
            event["selected_rank"]=rank
            event["selected_start"]=round(start,3)
            event["selected_score"]=round(score,5)
            event["category"]=category
            if semantic:
                event["semantic"]=semantic
                event["kind"]=label
        else:
            out.append({
                "time":round(event_abs,3),
                "score":round(max(0.55,min(1.0,score)),4),
                "kind":label,
                "selected_rank":rank,
                "selected_start":round(start,3),
                "selected_score":round(score,5),
                "category":category,
                "semantic":semantic,
            })

    out.sort(key=lambda x:_num(x.get("time")))
    return out


def window_event_map(events, clip_start, clip_duration, max_events=14):
    """Convert absolute Event Map timestamps to the currently loaded editor clip."""
    start=max(0.0,_num(clip_start))
    duration=max(0.05,_num(clip_duration,15.0))
    end=start+duration
    out=[]
    for event in events or []:
        if not isinstance(event,dict):
            continue
        t=_num(event.get("time"),-1.0)
        # Small tolerance keeps an event exactly on a trim edge visible.
        if t<start-0.05 or t>end+0.05:
            continue
        row=dict(event)
        row["absolute_time"]=round(t,3)
        row["time"]=round(max(0.0,min(duration,t-start)),3)
        out.append(row)

    # Selected markers first if a dense clip would exceed the UI budget.
    if len(out)>max_events:
        chosen=[x for x in out if x.get("selected_rank")]
        rest=[x for x in out if not x.get("selected_rank")]
        rest.sort(key=lambda x:_num(x.get("score")),reverse=True)
        out=chosen+rest[:max(0,int(max_events)-len(chosen))]
        out.sort(key=lambda x:_num(x.get("time")))
    return out


def vision_zones_for_genre(genre):
    g=str(genre or "Auto")
    return {
        "FPS":["CROSSHAIR","KILLFEED","MINIMAP"],
        "Battle Royale":["PLAYER","KILLFEED","MINIMAP"],
        "Racing":["VEHICLE","HUD"],
        "Sports":["ACTION","SCOREBOARD"],
        "Auto":["ACTION","HUD"],
    }.get(g,["ACTION","HUD"])
