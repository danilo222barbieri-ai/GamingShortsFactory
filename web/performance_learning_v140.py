from __future__ import annotations
import json
from pathlib import Path


METRICS=("watch_time_ratio","completion_rate","rewatch_rate","share_rate","save_rate","scroll_stop_rate")


def _clamp(v):
    try:return max(0.0,min(1.0,float(v)))
    except Exception:return 0.0


def normalize_metrics(raw):
    r=dict(raw or {})
    out={k:_clamp(r.get(k,0)) for k in METRICS}
    if "scroll_away_rate" in r and "scroll_stop_rate" not in r:
        out["scroll_stop_rate"]=1-_clamp(r["scroll_away_rate"])
    return out


def performance_score(raw):
    m=normalize_metrics(raw)
    return round(.26*m["watch_time_ratio"]+.27*m["completion_rate"]+.15*m["rewatch_rate"]+
                 .11*m["share_rate"]+.08*m["save_rate"]+.13*m["scroll_stop_rate"],4)


def learning_delta(metadata,metrics):
    meta=dict(metadata or {}); m=normalize_metrics(metrics); score=performance_score(m)
    return {
      "performance_score":score,
      "hook_reward":round(.55*m["scroll_stop_rate"]+.45*m["watch_time_ratio"],4),
      "ending_reward":round(.65*m["completion_rate"]+.35*m["rewatch_rate"],4),
      "share_reward":round(.58*m["share_rate"]+.42*m["save_rate"],4),
      "strategy":meta.get("ab_strategy"),
      "cover":meta.get("cover"),
      "game":meta.get("game"),
      "platform":meta.get("platform"),
    }


def update_memory(path,content_id,metadata,metrics):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    try:data=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except Exception:data={}
    if not isinstance(data,dict): data={}
    row={"content_id":str(content_id),**learning_delta(metadata,metrics),"metrics":normalize_metrics(metrics)}
    data[str(content_id)]=row
    tmp=p.with_suffix(p.suffix+".tmp"); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8"); tmp.replace(p)
    return row


def aggregate_preferences(memory):
    rows=list((memory or {}).values()) if isinstance(memory,dict) else list(memory or [])
    rows=[x for x in rows if isinstance(x,dict)]
    if not rows:return {"samples":0}
    best=sorted(rows,key=lambda x:float(x.get("performance_score",0)),reverse=True)
    return {"samples":len(rows),"best_strategy":best[0].get("strategy"),"best_cover":best[0].get("cover"),
            "best_game":best[0].get("game"),"best_platform":best[0].get("platform"),
            "mean_score":round(sum(float(x.get("performance_score",0)) for x in rows)/len(rows),4)}
