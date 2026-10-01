from __future__ import annotations

import math

ENGINE_VERSION="v131-director-intelligence"


def _num(value,default=0.0):
    try:
        value=float(value)
        return value if math.isfinite(value) else float(default)
    except Exception:
        return float(default)


def _clamp(value,low=0.0,high=1.0):
    return max(float(low),min(float(high),_num(value,low)))


def _dict(value):
    return dict(value) if isinstance(value,dict) else {}


def _list(value):
    return list(value) if isinstance(value,list) else []


def _profile_key(genre,event):
    g=str(genre or "Auto").strip().lower()
    event=str(event or "highlight").strip().lower()
    if "battle" in g:
        return "battle_royale"
    if "fps" in g or event in {"kill","multi_kill","clutch","victory"}:
        return "fps"
    if "racing" in g or event in {"overtake","crash"}:
        return "racing"
    if "sport" in g or event in {"goal","save","shot","assist"}:
        return "sports"
    return "general_gaming"


def _platform_variants(plan,target_duration):
    text=_dict(plan.get("text"))
    social=_dict(text.get("social"))
    hook=str(text.get("hook") or "").strip()
    out={}
    for key in ("youtube","tiktok","instagram"):
        copy=_dict(social.get(key))
        out[key]={
            "shared_master":True,
            "target_duration":round(max(5.0,min(60.0,_num(target_duration,15.0))),3),
            "hook":hook,
            "title":str(copy.get("title") or ""),
            "description":str(copy.get("description") or ""),
            "hashtags":[str(x) for x in _list(copy.get("hashtags")) if str(x).strip()][:8],
        }
    return out


def _editor_actions(moment,plan):
    edit=_dict(plan.get("edit"))
    framing=_dict(plan.get("framing"))
    style=_dict(plan.get("style"))
    text=_dict(plan.get("text"))
    actions=[]

    trim_start=max(0.0,_num(edit.get("trim_start"),0.0))
    trim_end=max(trim_start,_num(edit.get("trim_end"),trim_start))
    if trim_end>trim_start:
        actions.append({
            "action":"trim",
            "label":f"IN/OUT AI {trim_start:.1f}s → {trim_end:.1f}s",
            "values":{"inPoint":round(trim_start,3),"outPoint":round(trim_end,3)},
        })

    if framing.get("smart_reframe"):
        hud=[str(x).replace("_"," ") for x in _list(framing.get("hud_elements"))[:4]]
        label="Segui il soggetto"
        if hud:
            label+=" · proteggi "+", ".join(hud)
        actions.append({
            "action":"reframe",
            "label":label,
            "values":{
                "zoom":round(_num(framing.get("zoom"),1.0),3),
                "panX":round(_num(framing.get("pan_x"),0.0),3),
                "panY":round(_num(framing.get("pan_y"),0.0),3),
                "hudMode":str(framing.get("hud_mode") or "Smart Safe"),
            },
        })

    caption_style=str(text.get("caption_style") or "clean")
    actions.append({
        "action":"captions",
        "label":"Sottotitoli semantici · "+caption_style,
        "values":{
            "captionMode":"Auto",
            "captionY":round(_num(framing.get("caption_y"),76.0),2),
            "captionStyle":caption_style,
        },
    })

    slow=_dict(edit.get("slow_motion"))
    replay=_dict(edit.get("replay"))
    if slow.get("enabled"):
        actions.append({
            "action":"slow_motion",
            "label":"Slow motion sul momento forte",
            "values":slow,
        })
    if replay.get("enabled"):
        actions.append({
            "action":"replay",
            "label":"Micro-replay automatico",
            "values":replay,
        })

    accent=str(style.get("sound_accent") or "none")
    if accent!="none":
        actions.append({
            "action":"sound_design",
            "label":"Sound design · "+accent.replace("-"," "),
            "values":{
                "audioMode":str(style.get("audio_mode") or "Originale"),
                "accent":accent,
            },
        })

    hook=str(text.get("hook") or "").strip()
    if hook:
        actions.append({
            "action":"hook",
            "label":"Hook contestuale pronto",
            "values":{"hook":hook},
        })

    thumb=max(0.0,_num(edit.get("thumbnail_offset"),0.0))
    actions.append({
        "action":"thumbnail",
        "label":"Frame copertina sul picco",
        "values":{"offset":round(thumb,3)},
    })
    return actions



def _narrative_plan(moment,plan,target):
    """Build a non-UI story plan from available semantic/game signals."""
    edit=_dict(plan.get("edit"))
    explanation=[str(x) for x in _list(plan.get("explanation")) if str(x).strip()]
    raw=[]
    for key in ("story_beats","beats","micro_scenes","segments"):
        raw.extend([_dict(x) for x in _list(moment.get(key) or plan.get(key)) if isinstance(x,dict)])
    start=max(0.0,_num(moment.get("start"),0.0))
    peak=max(0.0,_num(edit.get("thumbnail_offset"),target*.62))
    if not raw:
        raw=[
            {"role":"setup","start":max(0.0,start-2.2),"duration":min(2.2,target*.20)},
            {"role":"tension","start":max(0.0,start-.8),"duration":min(2.8,target*.28)},
            {"role":"payoff","start":start+peak,"duration":min(2.4,target*.24)},
        ]
    beats=[]
    for row in raw[:5]:
        role=str(row.get("role") or row.get("type") or "beat").lower()
        beats.append({"role":role,"start":round(max(0.0,_num(row.get("start"),start)),3),
                      "duration":round(max(.25,_num(row.get("duration"),1.0)),3),
                      "score":round(_clamp(row.get("score"),0,1),3)})
    roles={x["role"] for x in beats}
    arc="setup-tension-payoff" if {"setup","tension","payoff"}<=roles else "event-payoff"
    reaction=_dict(moment.get("reaction") or plan.get("reaction"))
    cold=bool(target>=10 and len(beats)>=2)
    dead=[]
    for row in _list(moment.get("dead_zones") or plan.get("dead_zones"))[:6]:
        if isinstance(row,dict) and _num(row.get("duration"),0)>=1.8:
            dead.append({"start":round(max(0.0,_num(row.get("start"),0)),3),
                         "duration":round(_num(row.get("duration"),0),3),
                         "action":"speed_up_or_micro_cut"})
    payoff_delay=max(0.0,min(target,_num(peak,target*.62)))
    drop_risk="high" if payoff_delay>min(5.0,target*.42) else ("medium" if payoff_delay>3.0 else "low")
    return {
        "arc":arc,"beats":beats,"multi_moment":len(beats)>=2,
        "cold_open":{"enabled":cold,"duration":round(min(1.0,max(.5,target*.05)),2),
                     "source_role":"payoff"},
        "smart_ending":{"mode":"reaction" if reaction else "payoff","tail":0.65 if reaction else 0.35},
        "reaction_intelligence":reaction,
        "pattern_interrupts":dead,
        "retention":{"early_drop_risk":drop_risk,"payoff_delay":round(payoff_delay,2),
                     "notes":explanation[:3]},
    }


def _director_intelligence(moment,plan,narrative,target,genre,event):
    """Deeper invisible Director signals; no UI contract changes."""
    reaction=_dict(moment.get("reaction") or plan.get("reaction"))
    state=_dict(moment.get("match_state") or plan.get("match_state") or moment.get("game_state"))
    game=str(moment.get("game") or plan.get("game") or "").strip()
    language=str(moment.get("language") or plan.get("language") or "auto").strip()
    beats=_list(narrative.get("beats"))
    # Context raises importance when stakes are visible (low health, late timer, deficit, final zone).
    stakes=0.0
    health=_num(state.get("health_pct"),100.0)
    if health<=20: stakes+=.28
    ammo=_num(state.get("ammo"),99)
    if ammo<=5: stakes+=.12
    timer=_num(state.get("timer_remaining"),999)
    if timer<=30: stakes+=.18
    if bool(state.get("overtime") or state.get("final_zone") or state.get("last_lap")): stakes+=.25
    deficit=abs(min(0.0,_num(state.get("score_delta"),0)))
    stakes+=min(.17,deficit*.05)
    reaction_strength=_clamp(reaction.get("strength") or reaction.get("score"),0,1)
    payoff=_num(_dict(narrative.get("retention")).get("payoff_delay"),target*.62)
    dead=sum(_num(x.get("duration"),0) for x in _list(narrative.get("pattern_interrupts")) if isinstance(x,dict))
    retention_score=_clamp(1.0-(payoff/max(target,1))*.55-(dead/max(target,1))*.35+reaction_strength*.15+stakes*.18,0,1)
    return {
        "story_understanding":{
            "arc":str(narrative.get("arc") or "event-payoff"),
            "stakes_score":round(_clamp(stakes,0,1),3),
            "match_state":state,
            "game":game or _profile_key(genre,event),
        },
        "multi_moment":{
            "enabled":len(beats)>=2,
            "sequence":[str(_dict(x).get("role") or "beat") for x in beats[:5]],
            "max_micro_scenes":3,
        },
        "reaction":{
            "strength":round(reaction_strength,3),
            "use_in_edit":reaction_strength>=.35,
            "comedic_pause":bool(reaction.get("laugh") or reaction.get("comedic")),
        },
        "retention_prediction":{
            "structural_score":round(retention_score,3),
            "payoff_delay":round(payoff,2),
            "dead_air_seconds":round(dead,2),
            "needs_pattern_interrupt":dead>=1.8,
        },
        "ab_variants":{
            "enabled":True,
            "A":"cold_open" if _dict(narrative.get("cold_open")).get("enabled") else "action_first",
            "B":"context_hook",
        },
        "creator_learning":{"enabled":True,"signals":["selected","edited","published"]},
        "game_specific":{"profile":game.lower().replace(" ","_") if game else _profile_key(genre,event),"hud_context":state},
        "language":{"detected":language,"publishing":"match_creator"},
        "smart_loop":{"candidate":bool(beats and target<=30),"ending":str(_dict(narrative.get("smart_ending")).get("mode") or "payoff")},
    }


def build_short_package(moment,clip_duration=15.0,genre="Auto",profile="auto"):
    moment=_dict(moment)
    plan=_dict(moment.get("director_plan"))
    edit=_dict(plan.get("edit"))
    framing=_dict(plan.get("framing"))
    style=_dict(plan.get("style"))
    text=_dict(plan.get("text"))
    quality=_dict(plan.get("quality_rules"))

    rank=max(1,int(_num(moment.get("rank"),1)))
    start=max(0.0,_num(moment.get("start"),0.0))
    confidence=_clamp(moment.get("confidence"),0,1)
    event=str(moment.get("event") or plan.get("event") or "highlight").strip().lower()
    reason=str(moment.get("reason") or event.replace("_"," ").upper())
    target=max(5.0,min(60.0,_num(edit.get("target_duration"),clip_duration)))

    explanation=[str(x) for x in _list(plan.get("explanation")) if str(x).strip()]
    if not explanation:
        explanation=[f"Evento: {reason}",f"Confidenza: {round(confidence*100)}%"]

    narrative=_narrative_plan(moment,plan,target)\n    intelligence=_director_intelligence(moment,plan,narrative,target,genre,event)

    package={
        "engine":ENGINE_VERSION,
        "rank":rank,
        "start":round(start,3),
        "brain_score":round(_num(moment.get("brain_score"),moment.get("score")),5),
        "confidence":round(confidence,4),
        "event":event,
        "reason":reason,
        "game_profile":_profile_key(genre,event),
        "status":"mounted",
        "narrative_director":narrative,\n        "director_intelligence":intelligence,
        "mounted":True,
        "mount":{
            "trim":{
                "start":round(_num(edit.get("trim_start"),0.0),3),
                "end":round(_num(edit.get("trim_end"),target),3),
                "target_duration":round(target,3),
            },
            "framing":{
                "smart_reframe":bool(framing.get("smart_reframe")),
                "focus_x":round(_num(framing.get("focus_x"),50.0),2),
                "focus_y":round(_num(framing.get("focus_y"),43.0),2),
                "zoom":round(_num(framing.get("zoom"),1.0),3),
                "pan_x":round(_num(framing.get("pan_x"),0.0),3),
                "pan_y":round(_num(framing.get("pan_y"),0.0),3),
                "hud_mode":str(framing.get("hud_mode") or "Off"),
                "hud_elements":[str(x) for x in _list(framing.get("hud_elements"))[:8]],
            },
            "captions":{
                "mode":"semantic-auto",
                "style":str(text.get("caption_style") or "clean"),
                "safe_y":round(_num(framing.get("caption_y"),76.0),2),
            },
            "audio":{
                "mode":str(style.get("audio_mode") or "Originale"),
                "accent":str(style.get("sound_accent") or "none"),
                "normalize":bool(style.get("normalize_audio")),
            },
            "cinematic":{
                "slow_motion":_dict(edit.get("slow_motion")),
                "replay":_dict(edit.get("replay")),
                "cold_open":_dict(narrative.get("cold_open")),
                "smart_ending":_dict(narrative.get("smart_ending")),
                "pattern_interrupts":_list(narrative.get("pattern_interrupts")),
            },
            "hook":str(text.get("hook") or ""),
            "thumbnail_offset":round(_num(edit.get("thumbnail_offset"),0.0),3),
        },
        "social":_platform_variants(plan,target),
        "quality_rules":quality,
        "quality_gate":{
            "required":True,
            "before_publish":True,
            "block_on_fail":False,
            "guardian_recovery":True,
        },
        "second_opinion":{
            "summary":reason+" · "+str(round(confidence*100))+"%",
            "explanation":explanation[:6],
            "semantic_confidence":round(_num(moment.get("semantic_confidence"),0.0),4),
            "focus_confidence":round(_num(moment.get("focus_confidence"),0.0),4),
            "learning_multiplier":round(_num(moment.get("learning_multiplier"),1.0),6),
        },
        "editor_actions":_editor_actions(moment,plan),
        "render":{
            "strategy":"encode-on-selection",
            "shared_social_master":True,
            "plan":plan,
            "narrative":narrative,
        },
    }
    return package


def _session_intelligence(rows,genre="Auto"):
    """Session-wide intelligence used by Director without adding UI."""
    rows=[_dict(x) for x in _list(rows) if isinstance(x,dict)]
    fingerprints=set(); unique=[]; duplicates=[]
    for row in rows:
        event=str(row.get("event") or "highlight").lower()
        start=round(_num(row.get("start"),0.0)/3.0)
        reason=str(row.get("reason") or "").lower().strip()[:42]
        fp=(event,start,reason)
        if fp in fingerprints:
            duplicates.append({"event":event,"start":round(_num(row.get("start"),0),2)})
        else:
            fingerprints.add(fp); unique.append(row)
    groups={}
    for row in unique:
        key=str(row.get("event") or "highlight").lower()
        groups.setdefault(key,[]).append(row)
    series=[{"theme":k,"parts":len(v)} for k,v in groups.items() if len(v)>=2]
    ranked=sorted(unique,key=lambda x:_num(x.get("brain_score"),x.get("score")),reverse=True)
    return {
        "duplicate_detector":{"unique":len(unique),"duplicates":duplicates[:12]},
        "series_ai":{"candidates":series[:6]},
        "best_of_session":{
            "shorts":[round(_num(x.get("start"),0),2) for x in ranked[:3]],
            "compilation":[round(_num(x.get("start"),0),2) for x in ranked[3:7]],
            "long_form_intro":[round(_num(x.get("start"),0),2) for x in ranked[:2]],
        },
        "long_form":{
            "enabled":len(unique)>=4,
            "target_minutes":[6,10],
            "chapter_strategy":"narrative_strength_then_chronology",
        },
        "content_memory":{"fingerprints":[str(x) for x in list(fingerprints)[:24]],"avoid_republish":True},
        "safety_privacy":{
            "scan":["nickname","chat","email","notification","ip","qr_code"],
            "action":"warn_before_publish",
        },
        "copyright_audio":{"scan":True,"action":"flag_before_publish"},
        "visual_cleanup":{"detect":["discord","xbox","playstation","system_notification","popup"],"auto_cover_candidate":True},
        "trend_adaptation":{"enabled":True,"weight":"light","preserve_creator_style":True},
        "content_calendar":{"enabled":True,"inputs":["material","platform_history","content_type"]},
        "post_publish_learning":{"signals":["watch_time","completion_rate","scroll_away","retention_curve"],"when_connected":True},
    }


def build_one_click_package(brain,clip_duration=15.0,genre="Auto",profile="auto",target_count=3):
    brain=_dict(brain)
    selected=[x for x in _list(brain.get("selected")) if isinstance(x,dict)]
    alternates=[x for x in _list(brain.get("alternates")) if isinstance(x,dict)]\n    session_intelligence=_session_intelligence(selected+alternates,genre=genre)
    target=max(1,min(3,int(target_count or 3)))
    shorts=[
        build_short_package(row,clip_duration=clip_duration,genre=genre,profile=profile)
        for row in selected[:target]
    ]
    alt_packages=[
        build_short_package(row,clip_duration=clip_duration,genre=genre,profile=profile)
        for row in alternates[:3]
    ]
    return {
        "engine":ENGINE_VERSION,
        "source_engine":str(brain.get("engine") or ""),\n        "session_intelligence":session_intelligence,
        "ready":bool(shorts),
        "target_count":target,
        "prepared_count":len(shorts),
        "all_available_mounted":len(shorts)==min(target,len(selected)),
        "encoding_policy":"render-only-after-user-selection",
        "shared_social_master":True,
        "profile":str(profile or brain.get("profile") or "auto"),
        "genre":str(genre or brain.get("genre") or "Auto"),
        "shorts":shorts,
        "alternates":alt_packages,
    }
