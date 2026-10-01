from __future__ import annotations

import math
import re


ENGINE_VERSION = "v124-ai-os"


def _num(value, default=0.0):
    try:
        value=float(value)
        return value if math.isfinite(value) else float(default)
    except Exception:
        return float(default)


def _clamp(value, low=0.0, high=1.0):
    return max(float(low), min(float(high), _num(value, low)))


def _clean_label(value, fallback="Gaming"):
    text=re.sub(r"[_\-]+"," ",str(value or "")).strip()
    text=re.sub(r"\s+"," ",text)
    return text[:72] or fallback


def _event_name(value):
    raw=str(value or "highlight").strip().lower().replace("-","_").replace(" ","_")
    aliases={
        "multikill":"multi_kill",
        "multi_kill":"multi_kill",
        "win":"victory",
        "winner":"victory",
        "victory":"victory",
        "headshot":"kill",
        "goal":"goal",
        "clutch":"clutch",
        "boss":"boss",
        "reaction":"reaction",
        "impact":"impact",
        "explosion":"impact",
        "overtake":"overtake",
        "crash":"crash",
        "save":"save",
        "kill":"kill",
        "assist":"assist",
        "death":"death",
        "shot":"shot",
    }
    return aliases.get(raw, raw[:40] or "highlight")


_EVENT_COPY={
    "multi_kill":("MULTI KILL","Una sequenza che esplode in pochi secondi"),
    "victory":("VITTORIA","Il momento che chiude tutto"),
    "clutch":("CLUTCH","Sembrava finita, poi cambia tutto"),
    "goal":("GOAL","L'azione che decide la partita"),
    "boss":("BOSS","Il momento più pesante dello scontro"),
    "reaction":("REACTION","La reazione dice tutto"),
    "kill":("KILL","Il colpo che cambia la scena"),
    "impact":("IMPATTO","Il momento più violento della clip"),
    "overtake":("SORPASSO","Il sorpasso che non doveva riuscire"),
    "crash":("CRASH","Un attimo e cambia tutto"),
    "save":("PARATA","La giocata che salva tutto"),
    "assist":("ASSIST","La giocata che apre tutto"),
    "death":("KO","Qui gira tutto male"),
    "shot":("TIRO","L'occasione che accende la scena"),
    "highlight":("HIGHLIGHT","Il momento forte del gameplay"),
    "peak":("HIGHLIGHT","Il momento forte del gameplay"),
}


def _event_copy(event):
    return _EVENT_COPY.get(_event_name(event),(_clean_label(event,"HIGHLIGHT").upper(),"Il momento forte del gameplay"))


def _event_strength(event):
    return {
        "multi_kill":1.00,
        "victory":.98,
        "clutch":.98,
        "goal":.96,
        "boss":.91,
        "overtake":.88,
        "save":.84,
        "kill":.82,
        "impact":.80,
        "reaction":.78,
        "crash":.77,
        "assist":.66,
        "shot":.58,
        "death":.52,
        "highlight":.62,
        "peak":.62,
    }.get(_event_name(event),.60)


def _hashtags(event, genre):
    genre_key=str(genre or "Gaming").lower()
    tags=["#gaming","#shorts","#gameplay"]
    if "fps" in genre_key:
        tags+=["#fps","#clutch"]
    elif "battle" in genre_key:
        tags+=["#battleroyale","#gamingclips"]
    elif "racing" in genre_key:
        tags+=["#racing","#simracing"]
    elif "sport" in genre_key:
        tags+=["#gaming","#sports"]
    else:
        tags+=["#gamingclips"]
    event_tag={
        "multi_kill":"#multikill",
        "victory":"#victory",
        "clutch":"#clutch",
        "goal":"#goal",
        "boss":"#bossfight",
        "reaction":"#reaction",
        "kill":"#gamingmoment",
        "overtake":"#overtake",
        "crash":"#crash",
        "save":"#save",
    }.get(_event_name(event))
    if event_tag:
        tags.append(event_tag)
    out=[]
    for tag in tags:
        if tag not in out:
            out.append(tag)
    return out[:7]


def _social_pack(event, genre, subject=""):
    label,hook=_event_copy(event)
    subject=_clean_label(subject,"")
    core=(label.title() if label else "Gaming")
    if subject and subject.lower() not in ("player","action","gameplay"):
        core=f"{core} · {subject}"
    tags=_hashtags(event,genre)
    tag_text=" ".join(tags)

    youtube_title=(f"{core} — {hook}" if len(core)+len(hook)<83 else core)[:95]
    youtube_desc=(f"{hook}. Momento selezionato da GSF AI Director.\n\n{tag_text}")[:900]
    tiktok_caption=(f"{hook} 👀 {tag_text}")[:500]
    instagram_caption=(f"{hook}.\n\n{tag_text}")[:1000]

    return {
        "youtube":{
            "title":youtube_title,
            "description":youtube_desc,
            "hashtags":tags,
        },
        "tiktok":{
            "title":"",
            "description":tiktok_caption,
            "hashtags":tags,
        },
        "instagram":{
            "title":"",
            "description":instagram_caption,
            "hashtags":tags,
        },
    }


def build_director_plan(candidate, clip_duration=15.0, genre="Auto", profile="auto"):
    candidate=dict(candidate or {})
    event=_event_name(candidate.get("event"))
    category=str(candidate.get("category") or "balanced").lower()
    confidence=_clamp(candidate.get("confidence"),0,1)
    semantic_conf=_clamp(candidate.get("semantic_confidence"),0,1)
    focus_conf=_clamp(candidate.get("focus_confidence"),0,1)
    event_strength=_event_strength(event)
    reaction=_clamp(candidate.get("semantic_reaction"),0,1)
    start=max(0.0,_num(candidate.get("start"),0.0))
    event_time=max(start,_num(candidate.get("event_time"),start+float(clip_duration)*.52))
    duration=max(5.0,min(60.0,_num(clip_duration,15.0)))
    relative_event=max(0.0,min(duration,event_time-start))

    # Narrative window: preserve setup before high-impact events and aftermath
    # after victories/reactions. The render still keeps the user's final say.
    if event in ("clutch","victory","goal","multi_kill"):
        lead=max(2.8,min(5.2,duration*.28))
        aftermath=max(2.3,min(4.5,duration*.24))
    elif event in ("reaction","crash","boss"):
        lead=max(2.0,min(4.2,duration*.23))
        aftermath=max(2.8,min(4.8,duration*.27))
    else:
        lead=max(1.6,min(3.6,duration*.20))
        aftermath=max(1.8,min(3.5,duration*.20))

    target_duration=max(8.0,min(duration,lead+aftermath+max(4.0,duration*.35)))
    target_duration=min(30.0,target_duration)
    trim_start=max(0.0,relative_event-lead)
    trim_end=min(duration,max(trim_start+5.0,relative_event+aftermath))
    if trim_end-trim_start<min(target_duration,duration):
        pad=min(target_duration,duration)-(trim_end-trim_start)
        before=min(trim_start,pad*.50)
        trim_start-=before
        trim_end=min(duration,trim_end+(pad-before))
        if trim_end-trim_start<min(target_duration,duration):
            trim_start=max(0.0,trim_end-min(target_duration,duration))

    focus_x=max(8.0,min(92.0,_num(candidate.get("focus_x"),50.0)))
    focus_y=max(8.0,min(92.0,_num(candidate.get("focus_y"),43.0)))
    caption_y=max(18.0,min(86.0,_num(candidate.get("caption_safe_y"),78.0)))
    hud=list(candidate.get("hud_elements") or [])[:8]
    subject=_clean_label(candidate.get("subject"),"")

    smart_reframe=bool(focus_conf>=.42 or hud or str(genre) in ("FPS","Battle Royale","Sports","Racing"))
    zoom=1.06
    if event in ("kill","multi_kill","clutch","goal","save"):
        zoom=1.12
    elif event in ("victory","boss","crash"):
        zoom=1.08
    if focus_conf<.35:
        zoom=min(zoom,1.04)

    # Convert semantic focal point into the Editor's gentle pan domain.
    pan_x=max(-14.0,min(14.0,(50.0-focus_x)*.28))
    pan_y=max(-10.0,min(10.0,(47.0-focus_y)*.18))

    look="Competitive"
    intensity=68
    if event in ("boss","victory","crash"):
        look="Boss Cinematic"
        intensity=62
    elif event in ("reaction","highlight","peak"):
        look="Clean"
        intensity=58

    audio_mode="Game Boost" if event_strength>=.72 else "Originale"
    sound_accent={
        "multi_kill":"impact-hit",
        "kill":"impact-hit",
        "clutch":"riser-hit",
        "victory":"victory-rise",
        "goal":"impact-crowd",
        "boss":"cinematic-hit",
        "crash":"bass-hit",
        "overtake":"whoosh",
        "reaction":"duck-and-lift",
    }.get(event,"none")

    slowmo_enabled=event in ("kill","multi_kill","goal","save","crash","overtake") and event_strength>=.76
    slowmo_speed=.72 if event in ("goal","save","overtake") else .78
    replay_enabled=event in ("multi_kill","clutch","goal","save","crash","victory") and confidence>=.62
    replay_window=max(1.2,min(2.6,duration*.14))

    label,hook=_event_copy(event)
    hook_text=hook
    if event=="reaction" and reaction>=.75:
        hook_text="Aspetta di sentire la reazione…"
    elif event=="clutch":
        hook_text="Sembrava finita. Poi succede questo."
    elif event=="multi_kill":
        hook_text="Tre secondi e cambia tutto."
    elif event=="goal":
        hook_text="Questa azione decide tutto."

    thumbnail_offset=max(0.0,min(duration,relative_event+.12))
    social=_social_pack(event,genre,subject)

    explanation=[
        f"Evento: {label}",
        f"Confidenza: {round(confidence*100)}%",
    ]

    assistant_actions=[]
    if trim_start>.15 or trim_end<duration-.15:
        assistant_actions.append({
            "action":"trim",
            "label":f"Il momento forte inizia a {trim_start:.1f}s e chiude a {trim_end:.1f}s",
            "values":{"trim_start":round(trim_start,3),"trim_end":round(trim_end,3)},
        })
    if smart_reframe:
        _dir="destra" if pan_x>1.0 else ("sinistra" if pan_x<-1.0 else "centro")
        assistant_actions.append({
            "action":"reframe",
            "label":"Inquadratura "+_dir+" · HUD protetto" if hud else "Segui il soggetto automaticamente",
            "values":{
                "zoom":round(zoom,3),
                "pan_x":round(pan_x,3),
                "pan_y":round(pan_y,3),
                "hud_mode":"Smart Safe" if (hud or smart_reframe) else "Off",
            },
        })
    assistant_actions.append({
        "action":"captions",
        "label":"Sottotitoli "+("impact" if event_strength>=.78 else "clean")+" in zona sicura",
        "values":{"caption_y":round(caption_y,2)},
    })
    if slowmo_enabled:
        assistant_actions.append({
            "action":"slow_motion",
            "label":"Slow motion solo sul momento forte",
            "values":{"speed":round(slowmo_speed,2),"center":round(relative_event,3)},
        })
    if replay_enabled:
        assistant_actions.append({
            "action":"replay",
            "label":"Micro-replay sul payoff",
            "values":{"center":round(relative_event,3),"window":round(replay_window,3)},
        })
    if sound_accent!="none":
        assistant_actions.append({
            "action":"sound_design",
            "label":"Accento audio "+sound_accent.replace("-"," "),
            "values":{"accent":sound_accent},
        })
    if semantic_conf>0:
        explanation.append(f"Semantica video: {round(semantic_conf*100)}%")
    if focus_conf>0:
        explanation.append(f"Focus visivo: {round(focus_conf*100)}%")
    if hud:
        explanation.append("HUD protetto: "+", ".join(str(x).replace("_"," ") for x in hud[:4]))

    return {
        "engine":ENGINE_VERSION,
        "event":event,
        "category":category,
        "confidence":round(confidence,4),
        "edit":{
            "target_duration":round(target_duration,3),
            "trim_start":round(trim_start,3),
            "trim_end":round(trim_end,3),
            "event_offset":round(relative_event,3),
            "pace":"fast" if event_strength>=.78 else "balanced",
            "replay":{
                "enabled":bool(replay_enabled),
                "center":round(relative_event,3),
                "window":round(replay_window,3),
            },
            "slow_motion":{
                "enabled":bool(slowmo_enabled),
                "speed":round(slowmo_speed,2),
                "center":round(relative_event,3),
                "window":round(max(1.0,min(2.4,replay_window)),3),
            },
            "thumbnail_offset":round(thumbnail_offset,3),
        },
        "framing":{
            "smart_reframe":bool(smart_reframe),
            "focus_x":round(focus_x,2),
            "focus_y":round(focus_y,2),
            "focus_confidence":round(focus_conf,4),
            "zoom":round(zoom,3),
            "pan_x":round(pan_x,3),
            "pan_y":round(pan_y,3),
            "hud_mode":"Smart Safe" if (hud or smart_reframe) else "Off",
            "hud_elements":hud,
            "caption_y":round(caption_y,2),
            "frame_preset":"gameplay",
        },
        "style":{
            "look":look,
            "intensity":intensity,
            "audio_mode":audio_mode,
            "sound_accent":sound_accent,
            "normalize_audio":bool(audio_mode=="Game Boost"),
        },
        "text":{
            "hook":hook_text,
            "event_label":label,
            "caption_style":"impact" if event_strength>=.78 else "clean",
            "social":social,
        },
        "quality_rules":{
            "min_duration":5.0,
            "max_duration":60.0,
            "prefer_vertical":True,
            "protect_hud":bool(hud),
            "protect_subject":bool(focus_conf>=.35),
            "avoid_black_frames":True,
            "avoid_audio_clipping":True,
        },
        "assistant_actions":assistant_actions,
        "explanation":explanation,
    }


def attach_director_plans(selected, clip_duration=15.0, genre="Auto", profile="auto"):
    out=[]
    for row in selected or []:
        item=dict(row or {})
        item["director_plan"]=build_director_plan(
            item,clip_duration=clip_duration,genre=genre,profile=profile
        )
        out.append(item)
    return out


def build_alternates(candidates, selected, clip_duration=15.0, genre="Auto", profile="auto", limit=3):
    selected_starts=[_num(x.get("start"),-999) for x in selected or [] if isinstance(x,dict)]
    out=[]
    for row in candidates or []:
        if not isinstance(row,dict):
            continue
        start=_num(row.get("start"),-999)
        if any(abs(start-old)<max(1.5,float(clip_duration)*.18) for old in selected_starts):
            continue
        item=dict(row)
        item["director_plan"]=build_director_plan(
            item,clip_duration=clip_duration,genre=genre,profile=profile
        )
        out.append(item)
        if len(out)>=max(1,int(limit or 3)):
            break
    return out


def cloud_decision(local_events, duration_seconds=0.0, enabled=True):
    """Conservative cost/confidence router. Cloud is skipped only for obvious local consensus."""
    if not enabled:
        return {"use_cloud":False,"reason":"disabled","confidence":1.0}

    rows=[]
    for event in local_events or []:
        if not isinstance(event,dict):
            continue
        if str(event.get("kind") or "").upper()=="SILENCE":
            continue
        score=_clamp(event.get("score"),0,1)
        t=max(0.0,_num(event.get("time"),0.0))
        rows.append((score,t,str(event.get("kind") or "EVENT")))
    rows.sort(reverse=True)

    strong=[]
    for score,t,kind in rows:
        if score<.93:
            continue
        if all(abs(t-old[1])>=7.0 for old in strong):
            strong.append((score,t,kind))
        if len(strong)>=3:
            break

    if len(strong)>=3 and _num(duration_seconds,0.0)<=180.0:
        confidence=sum(x[0] for x in strong)/len(strong)
        return {
            "use_cloud":False,
            "reason":"local-consensus",
            "confidence":round(confidence,4),
            "strong_events":[{"score":round(x[0],4),"time":round(x[1],3),"kind":x[2]} for x in strong],
        }

    ambiguity=1.0
    if len(rows)>=2:
        ambiguity=max(0.0,min(1.0,1.0-abs(rows[0][0]-rows[1][0])*2.5))
    return {
        "use_cloud":True,
        "reason":"semantic-verification",
        "confidence":round(1.0-ambiguity*.35,4),
        "local_events":len(rows),
    }


def feedback_event(moment, action, editor_state=None):
    moment=dict(moment or {})
    allowed={"selected","rejected","opened_editor","published","replaced","trimmed"}
    action=str(action or "").strip().lower()
    if action not in allowed:
        action="selected"
    return {
        "engine":ENGINE_VERSION,
        "action":action,
        "rank":int(_num(moment.get("rank"),0)),
        "start":round(_num(moment.get("start"),0.0),3),
        "event":_event_name(moment.get("event")),
        "brain_score":round(_num(moment.get("brain_score"),0.0),5),
        "confidence":round(_num(moment.get("confidence"),0.0),4),
        "semantic_injected":bool(moment.get("semantic_injected")),
        "editor_state":dict(editor_state or {}) if isinstance(editor_state,dict) else {},
    }
