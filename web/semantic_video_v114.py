from __future__ import annotations

import json
import os
import time
from pathlib import Path


_DEFAULT_MODEL="gemini-3.8-flash"


def _env_bool(name,default=True):
    value=os.environ.get(name)
    if value is None:
        return bool(default)
    return str(value).strip().lower() not in ("0","false","off","no","")


def semantic_enabled():
    return bool(os.environ.get("GEMINI_API_KEY","").strip()) and _env_bool("GSF_SEMANTIC_VIDEO_AI",True)


def _num(value,default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def _clamp(value):
    return max(0.0,min(1.0,_num(value)))


def _pct(value,default=50.0,lo=0.0,hi=100.0):
    try:
        return max(lo,min(hi,float(value)))
    except Exception:
        return max(lo,min(hi,float(default)))


def normalize_semantic_events(payload,max_events=12):
    rows=[]
    source=(payload or {}).get("events") if isinstance(payload,dict) else []
    for item in source or []:
        if not isinstance(item,dict):
            continue
        t=max(0.0,_num(item.get("timestamp_seconds"),-1.0))
        if t<0:
            continue
        event=str(item.get("event") or "highlight").strip().lower().replace(" ","_")[:48]
        category=str(item.get("category") or "balanced").strip().lower().replace(" ","_")[:32]
        confidence=_clamp(item.get("confidence"))
        excitement=_clamp(item.get("excitement"))
        reaction=_clamp(item.get("reaction"))
        score=.55*confidence+.30*excitement+.15*reaction
        hud=[]
        for label in item.get("hud_elements") or []:
            label=str(label or "").strip().lower().replace(" ","_")[:32]
            if label and label not in hud:
                hud.append(label)
            if len(hud)>=8:
                break
        rows.append({
            "time":round(t,3),
            "semantic":event,
            "category":category,
            "semantic_confidence":round(confidence,4),
            "semantic_excitement":round(excitement,4),
            "semantic_reaction":round(reaction,4),
            "semantic_reason":str(item.get("reason") or "")[:180],
            "semantic_score":round(score,4),
            "subject":str(item.get("subject") or "")[:80],
            "focus_x":round(_pct(item.get("focus_x_percent"),50.0),2),
            "focus_y":round(_pct(item.get("focus_y_percent"),43.0),2),
            "focus_confidence":round(_clamp(item.get("focus_confidence")),4),
            "hud_elements":hud,
            "caption_safe_y":round(_pct(item.get("caption_safe_y_percent"),78.0,15.0,88.0),2),
            "source":"gemini-v117",
        })
    rows.sort(key=lambda x:x["semantic_score"],reverse=True)
    kept=[]
    for row in rows:
        if any(
            abs(row["time"]-old["time"])<1.5 and
            (row["semantic"]==old["semantic"] or row["category"]==old["category"])
            for old in kept
        ):
            continue
        kept.append(row)
        if len(kept)>=max(1,int(max_events)):
            break
    kept.sort(key=lambda x:x["time"])
    return kept


def merge_semantic_events(base_events,semantic_events,max_events=24):
    merged=[dict(x) for x in (base_events or []) if isinstance(x,dict)]
    for sem in semantic_events or []:
        if not isinstance(sem,dict):
            continue
        t=_num(sem.get("time"),-1.0)
        if t<0:
            continue
        nearest=None
        for idx,event in enumerate(merged):
            if str(event.get("kind","")).upper()=="SILENCE":
                continue
            dist=abs(_num(event.get("time"),-999)-t)
            if nearest is None or dist<nearest[0]:
                nearest=(dist,idx)
        if nearest and nearest[0]<=2.5:
            target=merged[nearest[1]]
            target.update({
                "semantic":sem.get("semantic"),
                "category":sem.get("category") or target.get("category"),
                "semantic_confidence":sem.get("semantic_confidence"),
                "semantic_excitement":sem.get("semantic_excitement"),
                "semantic_reaction":sem.get("semantic_reaction"),
                "semantic_reason":sem.get("semantic_reason"),
                "semantic_score":sem.get("semantic_score"),
                "subject":sem.get("subject"),
                "focus_x":sem.get("focus_x"),
                "focus_y":sem.get("focus_y"),
                "focus_confidence":sem.get("focus_confidence"),
                "hud_elements":list(sem.get("hud_elements") or []),
                "caption_safe_y":sem.get("caption_safe_y"),
                "source":"local+gemini-v117",
            })
            target["score"]=round(max(_num(target.get("score")),_num(sem.get("semantic_score"))),4)
        else:
            row=dict(sem)
            row["kind"]=str(sem.get("semantic") or "EVENT").upper()
            row["score"]=sem.get("semantic_score",0.0)
            merged.append(row)
    merged.sort(key=lambda x:_num(x.get("score")),reverse=True)
    merged=merged[:max(1,int(max_events))]
    merged.sort(key=lambda x:_num(x.get("time")))
    return merged


def _schema(max_events):
    return {
        "type":"object",
        "properties":{
            "events":{
                "type":"array",
                "maxItems":max(3,int(max_events)),
                "items":{
                    "type":"object",
                    "properties":{
                        "timestamp_seconds":{"type":"number"},
                        "event":{"type":"string"},
                        "category":{"type":"string"},
                        "confidence":{"type":"number","minimum":0,"maximum":1},
                        "excitement":{"type":"number","minimum":0,"maximum":1},
                        "reaction":{"type":"number","minimum":0,"maximum":1},
                        "reason":{"type":"string"},
                        "subject":{"type":"string"},
                        "focus_x_percent":{"type":"number","minimum":0,"maximum":100},
                        "focus_y_percent":{"type":"number","minimum":0,"maximum":100},
                        "focus_confidence":{"type":"number","minimum":0,"maximum":1},
                        "hud_elements":{"type":"array","maxItems":8,"items":{"type":"string"}},
                        "caption_safe_y_percent":{"type":"number","minimum":15,"maximum":88},
                    },
                    "required":[
                        "timestamp_seconds","event","category","confidence","excitement","reaction","reason",
                        "subject","focus_x_percent","focus_y_percent","focus_confidence","hud_elements","caption_safe_y_percent"
                    ],
                },
            }
        },
        "required":["events"],
    }


def analyze_gameplay_video(path,game_hint="",max_events=12):
    key=os.environ.get("GEMINI_API_KEY","").strip()
    if not key or not semantic_enabled():
        return {"enabled":False,"provider":"local-only","events":[],"skipped":"not-configured"}
    source=Path(path)
    max_bytes=max(10*1024*1024,int(os.environ.get("GSF_SEMANTIC_MAX_BYTES",str(2*1024*1024*1024))))
    model=os.environ.get("GSF_GEMINI_MODEL",_DEFAULT_MODEL).strip() or _DEFAULT_MODEL
    if not source.is_file() or source.stat().st_size>max_bytes:
        return {"enabled":True,"provider":model+"-agentic-v117","events":[],"skipped":"file-too-large"}

    uploaded=None
    started=time.perf_counter()
    try:
        from google import genai
        client=genai.Client(api_key=key)
        uploaded=client.files.upload(file=str(source))
        deadline=time.time()+180
        while time.time()<deadline:
            uploaded=client.files.get(name=uploaded.name)
            state=str(getattr(getattr(uploaded,"state",None),"name",getattr(uploaded,"state","")) or "")
            if state=="ACTIVE":
                break
            if state=="FAILED":
                raise RuntimeError("Gemini file processing failed")
            time.sleep(2)
        else:
            raise TimeoutError("Gemini file processing timeout")

        prompt=(
            "Analyze this gameplay as a professional short-form gaming highlight editor. "
            "Find only genuinely strong moments that could deserve one of the three best clips. "
            "Recognize concrete events when visible or audible: kills, multi-kills, clutch, victory, goals, "
            "saves, overtakes, crashes, boss events, rare loot, deaths, strong reactions, score or HUD changes, "
            "and meaningful setup/payoff. Avoid menus, loading, repetitive action and false peaks. "
            "Return diverse candidate timestamps, not duplicates from the same event. "
            "For every event also estimate the primary visual subject center as X/Y percentages of the full frame. "
            "Use low focus_confidence if the subject position is uncertain. List visible HUD elements that should be "
            "protected from crop such as minimap, killfeed, scoreboard, facecam, health, ammo, objective, timer, "
            "speedometer or lap counter. Suggest a caption-safe Y percentage that avoids the subject and important HUD. "
            "Do not invent precision: uncertainty must lower focus_confidence. "
            "Game/title hint: "+str(game_hint or "unknown")+"."
        )
        interaction=client.interactions.create(
            model=model,
            input=[
                {"type":"video","uri":uploaded.uri,"mime_type":uploaded.mime_type,"processing":"agentic"},
                {"type":"text","text":prompt},
            ],
            response_format={
                "type":"text",
                "mime_type":"application/json",
                "schema":_schema(max_events),
            },
            background=True,
        )
        interaction_deadline=time.time()+max(
            60.0,float(os.environ.get("GSF_SEMANTIC_TIMEOUT_SECONDS","420") or 420)
        )
        while str(getattr(interaction,"status","") or "").lower() in ("in_progress","queued"):
            if time.time()>=interaction_deadline:
                raise TimeoutError("Gemini semantic interaction timeout")
            time.sleep(3)
            interaction=client.interactions.get(interaction.id)
        final_status=str(getattr(interaction,"status","") or "").lower()
        if final_status not in ("completed",""):
            raise RuntimeError("Gemini semantic interaction "+final_status)
        payload=json.loads(interaction.output_text or "{}")
        events=normalize_semantic_events(payload,max_events=max_events)
        return {
            "enabled":True,
            "provider":model+"-agentic",
            "events":events,
            "elapsed_seconds":round(time.perf_counter()-started,3),
        }
    except Exception as exc:
        return {
            "enabled":True,
            "provider":model+"-agentic",
            "events":[],
            "error":str(exc)[:240],
            "elapsed_seconds":round(time.perf_counter()-started,3),
        }
    finally:
        if uploaded is not None:
            try:
                client.files.delete(name=uploaded.name)
            except Exception:
                pass
