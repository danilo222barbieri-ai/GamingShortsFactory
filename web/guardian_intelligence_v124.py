from __future__ import annotations


ENGINE_VERSION="v124-guardian-intelligence"


def diagnose(guardian=None, quality=None, render_status=""):
    guardian=dict(guardian or {})
    quality=dict(quality or {})
    render_status=str(render_status or guardian.get("status") or "").lower()
    repairs=list(guardian.get("repairs") or [])
    issues=list(quality.get("issues") or [])
    warnings=list(quality.get("warnings") or [])

    diagnosis={
        "engine":ENGINE_VERSION,
        "severity":"ok",
        "class":"healthy",
        "message":"Sistema operativo.",
        "safe_action":"none",
        "repairs":repairs,
    }

    if repairs:
        diagnosis.update({
            "severity":"info",
            "class":"self_healed",
            "message":"Guardian ha ripristinato automaticamente lo stato.",
            "safe_action":"already_repaired",
        })

    if guardian.get("needs_source_restore"):
        diagnosis.update({
            "severity":"warning",
            "class":"source_missing",
            "message":"Gameplay sorgente mancante localmente; recupero storage richiesto.",
            "safe_action":"restore_source_from_bucket",
        })
    elif guardian.get("needs_final_restore"):
        diagnosis.update({
            "severity":"warning",
            "class":"final_missing",
            "message":"Short finale mancante localmente; recupero storage richiesto.",
            "safe_action":"restore_final_from_bucket",
        })
    elif render_status=="stale":
        diagnosis.update({
            "severity":"warning",
            "class":"render_stale",
            "message":"Render rimasto in esecuzione oltre la finestra prevista.",
            "safe_action":"release_stale_state_then_retry",
        })
    elif render_status in ("error","failed"):
        diagnosis.update({
            "severity":"error",
            "class":"render_failed",
            "message":"Render non riuscito.",
            "safe_action":"retry_with_safe_render_fallback",
        })

    if quality:
        qstatus=str(quality.get("status") or "")
        if qstatus=="fail":
            diagnosis.update({
                "severity":"error",
                "class":"quality_failed",
                "message":"Il file esiste ma il controllo qualità ha rilevato problemi bloccanti.",
                "safe_action":"rerender_from_recipe",
            })
        elif qstatus=="warn" and diagnosis["severity"] in ("ok","info"):
            diagnosis.update({
                "severity":"warning",
                "class":"quality_warning",
                "message":"Short valido con avvisi di qualità.",
                "safe_action":"publish_or_rerender",
            })

        if "too_many_black_frames" in issues:
            diagnosis["message"]="Troppi frame neri nel risultato."
            diagnosis["safe_action"]="rerender_or_adjust_trim"
        elif "video_stream_missing" in issues:
            diagnosis["message"]="Stream video finale non valido."
            diagnosis["safe_action"]="rerender_from_recipe"
        elif "audio_near_clipping" in warnings:
            diagnosis["message"]="Audio vicino al clipping."
            diagnosis["safe_action"]="normalize_audio_next_render"
        elif "audio_very_low" in warnings:
            diagnosis["message"]="Audio molto basso."
            diagnosis["safe_action"]="boost_audio_next_render"
        elif "not_vertical" in warnings:
            diagnosis["message"]="Il risultato non è verticale."
            diagnosis["safe_action"]="rerender_vertical"

    return diagnosis
