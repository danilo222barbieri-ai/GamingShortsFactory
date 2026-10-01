from __future__ import annotations
import json
from pathlib import Path


DEFAULTS={"cut_density":.5,"zoom_aggression":.45,"caption_density":.6,"replay_preference":.35,
          "cold_open_preference":.5,"context_preference":.5}


def _clamp(v):
    try:return max(0.0,min(1.0,float(v)))
    except Exception:return .5


def load_profile(path):
    p=Path(path)
    if not p.exists(): return {"version":1,"samples":0,**DEFAULTS}
    try:
        data=json.loads(p.read_text(encoding="utf-8"))
        return {"version":1,**DEFAULTS,**(data if isinstance(data,dict) else {})}
    except Exception:return {"version":1,"samples":0,**DEFAULTS}


def learn(profile,event,alpha=.18):
    """Online creator preference learning from actual editor/publish choices."""
    out=dict(profile or {}); out.setdefault("samples",0)
    mapping={
      "cut_density":"cut_density","zoom_aggression":"zoom_aggression",
      "caption_density":"caption_density","replay_preference":"replay_preference",
      "cold_open":"cold_open_preference","preserve_context":"context_preference",
    }
    for source,target in mapping.items():
        if source in event:
            old=_clamp(out.get(target,DEFAULTS[target]))
            out[target]=round(old*(1-alpha)+_clamp(event[source])*alpha,4)
    out["samples"]=int(out.get("samples",0))+1
    out["last_signal"]=str(event.get("signal") or "editor")
    return out


def save_profile(path,profile):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+".tmp")
    tmp.write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding="utf-8")
    tmp.replace(p)


def retention_score(candidate,profile=None):
    """Structural pre-render score; later telemetry can calibrate its weights."""
    c=dict(candidate or {}); p={**DEFAULTS,**dict(profile or {})}
    hook=_clamp(c.get("hook_strength",.5)); stakes=_clamp(c.get("stakes",.5))
    reaction=_clamp(c.get("reaction",.5)); payoff=_clamp(1-_clamp(c.get("payoff_delay_ratio",.5)))
    dead=_clamp(c.get("dead_air_ratio",0)); rhythm=_clamp(c.get("rhythm",p["cut_density"]))
    score=.23*hook+.20*stakes+.16*reaction+.22*payoff+.19*rhythm-.28*dead
    return round(_clamp(score),4)


def choose_ab(a,b,profile=None):
    sa=retention_score(a,profile); sb=retention_score(b,profile)
    return {"winner":"A" if sa>=sb else "B","scores":{"A":sa,"B":sb},
            "strategy":"pre_render_structural","margin":round(abs(sa-sb),4)}
