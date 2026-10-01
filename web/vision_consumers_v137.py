from __future__ import annotations

import hashlib
import json
from pathlib import Path


SENSITIVE_TOKENS=("email","gmail","@","http","www.","discord","invite","ip","qr","notification")
OVERLAY_TOKENS=("discord","xbox","playstation","steam","notification","popup","party chat")


def _rows(v):
    return [dict(x) for x in (v or []) if isinstance(x,dict)]


def consume_vision_evidence(evidence, provider_results=None):
    """Turn frame/provider evidence into decisions used by Cover and safety engines.

    provider_results accepts future/current OCR/vision output per frame. The engine remains
    useful without a provider by ranking frame metadata and becomes richer automatically
    when labels/OCR arrive.
    """
    evidence=dict(evidence or {})
    frames=_rows(dict(evidence.get("frames") or {}).get("frames"))
    results=_rows(provider_results)
    by_path={str(x.get("path") or ""):x for x in results}
    covers=[]; privacy=[]; overlays=[]
    for i,frame in enumerate(frames):
        path=str(frame.get("path") or "")
        obs=by_path.get(path,{})
        labels=" ".join(str(x).lower() for x in obs.get("labels",[]) or [])
        ocr=" ".join(str(x) for x in obs.get("ocr",[]) or [])
        text=(labels+" "+ocr).lower()
        sensitive=[x for x in SENSITIVE_TOKENS if x in text]
        overlay=[x for x in OVERLAY_TOKENS if x in text]
        sharp=float(obs.get("sharpness",.5) or .5)
        action=float(obs.get("action_score",.5) or .5)
        face=float(obs.get("subject_score",.5) or .5)
        obstruction=min(1.0,.18*len(overlay)+.22*len(sensitive))
        score=max(0.0,min(1.0,.35*sharp+.40*action+.25*face-obstruction))
        covers.append({"path":path,"time":frame.get("time"),"score":round(score,3),
                       "safe":not sensitive,"overlay_count":len(overlay)})
        if sensitive: privacy.append({"path":path,"time":frame.get("time"),"matches":sensitive})
        if overlay: overlays.append({"path":path,"time":frame.get("time"),"matches":overlay})
    covers.sort(key=lambda x:(x["safe"],x["score"]),reverse=True)
    return {
        "engine":"v137-vision-consumers",
        "cover_candidates":covers[:3],
        "privacy_findings":privacy,
        "overlay_findings":overlays,
        "publish_guard":"review" if privacy else "clear",
        "cleanup_recommended":bool(overlays),
        "provider_enriched":bool(results),
    }


def content_fingerprint(evidence):
    """Stable fingerprint for cross-platform duplicate/content memory."""
    e=dict(evidence or {})
    game=json.dumps(e.get("game") or {},sort_keys=True,ensure_ascii=False)
    frames=_rows(dict(e.get("frames") or {}).get("frames"))
    basis=game+"|"+"|".join(f"{x.get('time')}:{x.get('bytes')}" for x in frames)
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()
