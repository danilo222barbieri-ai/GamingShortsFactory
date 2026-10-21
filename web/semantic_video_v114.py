from __future__ import annotations

import base64
import json
import os
import subprocess
import time
from pathlib import Path


_DEFAULT_MODEL="gemini-3.8-flash"
GSF_SEMANTIC_ENGINE_VERSION="v125-cinematic-ai"


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


def _interaction_status(interaction):
    value=getattr(interaction,"status","")
    value=getattr(value,"value",None) or getattr(value,"name",None) or value
    text=str(value or "").strip().lower()
    if "." in text:
        text=text.rsplit(".",1)[-1]
    return text


def choose_processing_mode(duration_seconds):
    duration=max(0.0,_num(duration_seconds))
    return "static" if 0.0<duration<300.0 else "agentic"


def choose_input_method(size_bytes):
    inline_limit=max(
        1024*1024,
        int(os.environ.get("GSF_SEMANTIC_INLINE_MAX_BYTES",str(18*1024*1024)) or 18*1024*1024),
    )
    return "inline" if max(0,int(size_bytes or 0))<=inline_limit else "files"


def semantic_model_candidates(primary=None):
    primary=str(primary or os.environ.get("GSF_GEMINI_MODEL",_DEFAULT_MODEL) or _DEFAULT_MODEL).strip()
    raw=str(os.environ.get("GSF_GEMINI_FALLBACK_MODELS","gemini-3.7-flash") or "")
    rows=[primary]+[x.strip() for x in raw.split(",") if x.strip()]
    out=[]
    for model in rows:
        if model and model not in out:
            out.append(model)
    return out


def is_quota_error(value):
    text=str(value or "").lower()
    markers=(
        "429","resource_exhausted","resource exhausted","quota exceeded",
        "exceeded your current quota","rate limit","too many requests",
    )
    return any(marker in text for marker in markers)


def is_retryable_provider_error(value):
    text=str(value or "").lower()
    if is_quota_error(text):
        return True
    markers=(
        "503","service unavailable","unavailable","high demand",
        "500 internal","internal server error","502 bad gateway","504 gateway timeout",
        "timeout","timed out","readtimeout","deadline exceeded",
        "connection reset","connection error","temporarily unavailable",
        "response empty","expecting value: line 1 column 1",
    )
    return any(marker in text for marker in markers)


def _probe_duration_seconds(path):
    try:
        proc=subprocess.run(
            [
                "/usr/bin/ffprobe","-v","error",
                "-show_entries","format=duration",
                "-of","default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,text=True,timeout=20,check=False,
        )
        if proc.returncode==0:
            return max(0.0,float((proc.stdout or "0").strip() or 0.0))
    except Exception:
        pass
    return 0.0


def _video_mime(path):
    ext=Path(path).suffix.lower()
    return {
        ".mp4":"video/mp4",
        ".mov":"video/quicktime",
        ".m4v":"video/x-m4v",
        ".webm":"video/webm",
        ".mkv":"video/x-matroska",
        ".avi":"video/x-msvideo",
        ".mpeg":"video/mpeg",
        ".mpg":"video/mpeg",
    }.get(ext,"video/mp4")


def _inline_video_content(source,processing_mode):
    encoded=base64.b64encode(Path(source).read_bytes()).decode("ascii")
    payload={
        "type":"video",
        "data":encoded,
        "mime_type":_video_mime(source),
    }
    # Static is Gemini's default for video. Omitting the field exactly matches
    # the documented inline-video request and avoids unnecessary validation.
    if processing_mode=="agentic":
        payload["processing"]="agentic"
    return payload


def _response_format(max_events):
    return [{
        "type":"text",
        "mime_type":"application/json",
        "schema":_schema(max_events),
    }]


def _direct_semantic_interaction(client,model,video_content,prompt,max_events,semantic_timeout,structured=True):
    kwargs={
        "model":model,
        "input":[video_content,{"type":"text","text":prompt}],
        "timeout":semantic_timeout,
    }
    if structured:
        kwargs["response_format"]=_response_format(max_events)
    interaction=client.interactions.create(**kwargs)
    raw=str(getattr(interaction,"output_text","") or "").strip()
    if not raw:
        raise RuntimeError("Gemini semantic direct response empty")
    return json.loads(raw)


def _stream_semantic_interaction(client,model,video_content,prompt,max_events,semantic_timeout,structured=True):
    kwargs={
        "model":model,
        "input":[video_content,{"type":"text","text":prompt}],
        "stream":True,
        "timeout":semantic_timeout,
    }
    if structured:
        kwargs["response_format"]=_response_format(max_events)
    stream=client.interactions.create(**kwargs)
    json_parts=[]
    completed=False
    for event in stream:
        event_type=str(getattr(event,"event_type","") or "")
        if event_type=="step.delta" and getattr(event,"delta",None) is not None:
            if getattr(event.delta,"type",None)=="text":
                chunk=getattr(event.delta,"text",None)
                if chunk:
                    json_parts.append(str(chunk))
        elif event_type=="interaction.completed":
            completed=True
        elif event_type in ("interaction.failed","interaction.cancelled","error"):
            detail=str(getattr(event,"error",None) or event_type)
            raise RuntimeError("Gemini semantic stream "+detail[:180])
    if not completed and not json_parts:
        raise RuntimeError("Gemini semantic stream ended without output")
    return json.loads("".join(json_parts) or "{}")


def _generate_content_semantic(
    client,model,source,uploaded,prompt,max_events,semantic_timeout,structured=True,duration_seconds=0.0
):
    from google.genai import types
    if uploaded is not None:
        contents=[uploaded,prompt]
    else:
        gameplay_fps=max(
            1.0,
            min(6.0,float(os.environ.get("GSF_SEMANTIC_GAMEPLAY_FPS","3") or 3.0)),
        )
        contents=types.Content(
            parts=[
                types.Part(
                    inline_data=types.Blob(
                        data=Path(source).read_bytes(),
                        mime_type=_video_mime(source),
                    ),
                    video_metadata=types.VideoMetadata(fps=gameplay_fps),
                ),
                types.Part(text=prompt),
            ]
        )
    config=types.GenerateContentConfig(
        http_options=types.HttpOptions(timeout=int(max(1.0,float(semantic_timeout))*1000),retry_options=types.HttpRetryOptions(attempts=1)),
    )
    if structured:
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=_schema(max_events),
            http_options=types.HttpOptions(timeout=int(max(1.0,float(semantic_timeout))*1000),retry_options=types.HttpRetryOptions(attempts=1)),
        )
    response=client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )
    raw=str(getattr(response,"text","") or "").strip()
    if not raw:
        raise RuntimeError("Gemini Generate Content video response empty")
    return json.loads(raw)


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
    max_bytes=max(
        10*1024*1024,
        int(os.environ.get("GSF_SEMANTIC_MAX_BYTES",str(2*1024*1024*1024))),
    )
    models=semantic_model_candidates()
    primary_model=models[0] if models else _DEFAULT_MODEL
    if not source.is_file() or source.stat().st_size>max_bytes:
        return {
            "enabled":True,
            "provider":primary_model+"-local-fallback-v123",
            "events":[],
            "skipped":"file-too-large",
            "model_attempts":[],
            "model_fallback":False,
        }

    uploaded=None
    client=None
    started=time.perf_counter()
    base_processing_mode=choose_processing_mode(_probe_duration_seconds(source))
    input_method=choose_input_method(source.stat().st_size)
    duration_seconds=_probe_duration_seconds(source)
    semantic_timeout=max(
        60.0,float(os.environ.get("GSF_SEMANTIC_TIMEOUT_SECONDS","420") or 420)
    )
    static_timeout=max(
        20.0,
        min(
            semantic_timeout,
            float(os.environ.get("GSF_SEMANTIC_STATIC_TIMEOUT_SECONDS","90") or 90),
        ),
    )
    # One budget covers provider/model/format fallbacks; a retry must not
    # restart another full timeout after the UI has already been waiting.
    provider_deadline=started+(static_timeout if base_processing_mode=="static" else semantic_timeout)
    def remaining_timeout(limit):
        remaining=provider_deadline-time.perf_counter()
        if remaining<=0:raise TimeoutError("Gemini analysis deadline exceeded")
        return min(float(limit),remaining)

    model_attempts=[]
    selected_model=primary_model
    selected_mode=base_processing_mode
    selected_generate=(base_processing_mode=="static")

    try:
        from google import genai
        client=genai.Client(api_key=key,http_options={"timeout":int(remaining_timeout(semantic_timeout)*1000),"retry_options":{"attempts":1}})

        video_content=None
        if input_method=="inline":
            video_content=_inline_video_content(source,base_processing_mode)
        else:
            uploaded=client.files.upload(file=str(source),config={"http_options":{"timeout":max(1,int(remaining_timeout(semantic_timeout)*1000)),"retry_options":{"attempts":1}}})
            deadline=time.time()+180
            while time.time()<deadline and time.perf_counter()<provider_deadline:
                uploaded=client.files.get(name=uploaded.name,config={"http_options":{"timeout":max(1,int(remaining_timeout(semantic_timeout)*1000)),"retry_options":{"attempts":1}}})
                state=str(
                    getattr(getattr(uploaded,"state",None),"name",getattr(uploaded,"state",""))
                    or ""
                )
                if state=="ACTIVE":
                    break
                if state=="FAILED":
                    raise RuntimeError("Gemini file processing failed")
                time.sleep(2)
            else:
                raise TimeoutError("Gemini file processing timeout")
            video_content={
                "type":"video",
                "uri":uploaded.uri,
                "mime_type":uploaded.mime_type,
                "processing":base_processing_mode,
            }

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
        prompt_json=prompt+(
            " Return ONLY valid JSON matching the requested events schema. "
            "If there are no meaningful highlights, return {\"events\":[]}."
        )

        payload=None
        last_exc=None
        for index,candidate_model in enumerate(models):
            attempt_mode=base_processing_mode if index==0 else "static"
            attempt_generate=(attempt_mode=="static")
            try:
                try:
                    if attempt_mode=="static":
                        payload=_generate_content_semantic(
                            client,candidate_model,source,uploaded,prompt_json,max_events,
                            remaining_timeout(static_timeout),structured=True,duration_seconds=duration_seconds,
                        )
                    else:
                        candidate_video=dict(video_content or {})
                        if input_method=="inline":
                            candidate_video=_inline_video_content(source,attempt_mode)
                        else:
                            candidate_video["processing"]=attempt_mode
                        payload=_stream_semantic_interaction(
                            client,candidate_model,candidate_video,prompt_json,max_events,
                            remaining_timeout(semantic_timeout),structured=True,
                        )
                except Exception as first_exc:
                    message=str(first_exc).lower()
                    invalid=(
                        "invalid_request" in message
                        or "invalid argument" in message
                        or "unsupported file uri" in message
                    )
                    if not invalid:
                        raise
                    attempt_mode="static"
                    attempt_generate=True
                    try:
                        payload=_generate_content_semantic(
                            client,candidate_model,source,uploaded,prompt_json,max_events,
                            remaining_timeout(static_timeout),structured=True,duration_seconds=duration_seconds,
                        )
                    except Exception as structured_exc:
                        structured_message=str(structured_exc).lower()
                        structured_invalid=(
                            "invalid_request" in structured_message
                            or "invalid argument" in structured_message
                        )
                        if not structured_invalid:
                            raise
                        payload=_generate_content_semantic(
                            client,candidate_model,source,uploaded,prompt_json,max_events,
                            remaining_timeout(static_timeout),structured=False,duration_seconds=duration_seconds,
                        )

                selected_model=candidate_model
                selected_mode=attempt_mode
                selected_generate=attempt_generate
                model_attempts.append({
                    "model":candidate_model,
                    "status":"ok",
                    "fallback":bool(index>0),
                })
                break
            except Exception as exc:
                last_exc=exc
                quota=is_quota_error(exc)
                retryable=is_retryable_provider_error(exc)
                selected_model=candidate_model
                selected_mode=attempt_mode
                selected_generate=attempt_generate
                model_attempts.append({
                    "model":candidate_model,
                    "status":"quota" if quota else ("retryable" if retryable else "error"),
                    "fallback":bool(index>0),
                    "reason":str(exc)[:120],
                })
                if retryable and index+1<len(models):
                    continue
                raise

        if payload is None:
            raise last_exc or RuntimeError("Gemini semantic analysis produced no payload")

        events=normalize_semantic_events(payload,max_events=max_events)
        return {
            "enabled":True,
            "provider":selected_model+"-"+selected_mode+"-"+input_method+
                ("-generate-v123" if selected_generate else "-agentic-stream-v123"),
            "events":events,
            "processing_mode":selected_mode,
            "input_method":input_method,
            "model":selected_model,
            "model_attempts":model_attempts,
            "model_fallback":bool(selected_model!=primary_model),
            "elapsed_seconds":round(time.perf_counter()-started,3),
        }
    except Exception as exc:
        return {
            "enabled":True,
            "provider":selected_model+"-"+selected_mode+"-"+input_method+
                ("-generate-v123" if selected_generate else "-agentic-stream-v123"),
            "events":[],
            "processing_mode":selected_mode,
            "input_method":input_method,
            "model":selected_model,
            "model_attempts":model_attempts,
            "model_fallback":bool(selected_model!=primary_model),
            "error":str(exc)[:240],
            "elapsed_seconds":round(time.perf_counter()-started,3),
        }
    finally:
        if uploaded is not None and client is not None:
            try:
                client.files.delete(name=uploaded.name,config={"http_options":{"timeout":2000,"retry_options":{"attempts":1}}})
            except Exception:
                pass
