from __future__ import annotations

import math

ENGINE_VERSION="v131-narrative-director"


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



def _narrative_director(moment,plan,target):
    """Build an executable story/retention plan from Game Brain evidence."""
    moment=_dict(moment); plan=_dict(plan)
    edit=_dict(plan.get("edit")); text=_dict(plan.get("text"))
    start=max(0.0,_num(moment.get("start"),0.0))
    peak=max(0.0,_num(edit.get("thumbnail_offset"),target*0.62))
    peak=min(target,peak)
    reaction=_clamp(moment.get("reaction_score",moment.get("audio_score",0.0)),0,1)
    tension=_clamp(moment.get("tension_score",moment.get("context_score",0.0)),0,1)
    payoff=_clamp(moment.get("confidence",0.0),0,1)
    setup_end=max(1.0,min(peak-0.35,target*0.36))
    story=[
        {"role":"setup","start":0.0,"end":round(setup_end,3)},
        {"role":"tension","start":round(setup_end,3),"end":round(max(setup_end,peak),3)},
        {"role":"payoff","start":round(max(setup_end,peak),3),"end":round(target,3)},
    ]
    if reaction>=0.35 and target-peak>=0.7:
        story[-1]["role"]="payoff_reaction"
    cold_open={
        "enabled":bool(payoff>=0.62 and peak>=2.2),
        "source_start":round(max(0.0,peak-0.35),3),
        "duration":round(min(0.85,max(0.5,target*0.05)),3),
        "return_to_start":True,
    }
    interrupts=[]
    dead=_list(moment.get("dead_zones"))+_list(plan.get("dead_zones"))
    for i,row in enumerate(dead[:3]):
        if isinstance(row,dict):
            a=max(0.0,_num(row.get("start"),0)); b=min(target,_num(row.get("end"),a))
            if b-a>=1.6:
                interrupts.append({"at":round(a,3),"duration":round(b-a,3),
                                   "type":("speed_up" if i%2==0 else "micro_crop")})
    first_payoff=peak+(0.0 if cold_open["enabled"] else 0.0)
    risk="low"
    if not cold_open["enabled"] and first_payoff>max(4.0,target*0.38): risk="high"
    elif not cold_open["enabled"] and first_payoff>2.8: risk="medium"
    ending="reaction" if reaction>=0.45 else ("scoreboard" if str(moment.get("event","")).lower() in {"victory","goal"} else "cut_on_payoff")
    hook=str(text.get("hook") or "").strip()
    return {
        "arc":"setup-tension-payoff",
        "segments":story,
        "multi_moment":{"enabled":True,"max_scenes":3,"same_event_only":True},
        "cold_open":cold_open,
        "pattern_interrupts":interrupts,
        "retention":{"opening_risk":risk,"payoff_at":round(peak,3),
                     "first_2_8s_has_hook":bool(cold_open["enabled"] or hook)},
        "smart_ending":{"mode":ending,"protect_reaction":reaction>=0.45},
        "auto_loop":{"candidate":bool(cold_open["enabled"] and ending=="cut_on_payoff")},
        "signals":{"tension":round(tension,3),"reaction":round(reaction,3),"payoff":round(payoff,3)},
        "ab_openings":[
            {"variant":"action_first","cold_open":cold_open},
            {"variant":"text_hook","hook":hook,"cold_open":{"enabled":False}},
        ],
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

    narrative=_narrative_director(moment,plan,target)

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
        "narrative_director":narrative,
        "retention_prediction":dict(narrative.get("retention") or {}),
        "ab_openings":list(narrative.get("ab_openings") or []),
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
        "editor_actions":_editor_actions(moment,plan)+[{"action":"narrative_mount","label":"Story Director · setup → tensione → payoff","values":narrative}],
        "render":{
            "strategy":"encode-on-selection",
            "shared_social_master":True,
            "plan":plan,
        },
    }
    return package


def build_one_click_package(brain,clip_duration=15.0,genre="Auto",profile="auto",target_count=3):
    brain=_dict(brain)
    selected=[x for x in _list(brain.get("selected")) if isinstance(x,dict)]
    alternates=[x for x in _list(brain.get("alternates")) if isinstance(x,dict)]
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
        "source_engine":str(brain.get("engine") or ""),
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
