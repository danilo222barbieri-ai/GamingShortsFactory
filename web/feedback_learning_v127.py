from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path

ENGINE_VERSION="v127-learning-ranker"

_ACTION_WEIGHTS={
    "published":2.0,
    "selected":0.70,
    "opened_editor":0.35,
    "trimmed":0.15,
    "replaced":-1.10,
    "rejected":-1.45,
}


def _num(value,default=0.0):
    try:
        value=float(value)
        return value if math.isfinite(value) else float(default)
    except Exception:
        return float(default)


def empty_model():
    return {
        "engine":ENGINE_VERSION,
        "updated_at":0.0,
        "total_feedback":0,
        "events":{},
    }


def normalize_event(value):
    text=str(value or "highlight").strip().lower().replace("-","_").replace(" ","_")
    return text[:48] or "highlight"


def update_model(model,event_row):
    current=dict(model or empty_model())
    events=dict(current.get("events") or {})
    event=normalize_event((event_row or {}).get("event"))
    action=str((event_row or {}).get("action") or "selected").strip().lower()
    weight=float(_ACTION_WEIGHTS.get(action,0.0))

    stats=dict(events.get(event) or {})
    actions=dict(stats.get("actions") or {})
    actions[action]=int(actions.get(action,0) or 0)+1
    count=int(stats.get("count",0) or 0)+1
    signal=_num(stats.get("signal"),0.0)+weight

    stats.update({
        "count":count,
        "signal":round(signal,5),
        "actions":actions,
        "updated_at":time.time(),
    })
    events[event]=stats
    current.update({
        "engine":ENGINE_VERSION,
        "updated_at":time.time(),
        "total_feedback":int(current.get("total_feedback",0) or 0)+1,
        "events":events,
    })
    return current


def event_multiplier(model,event):
    """Return a deliberately small learning multiplier in [0.96, 1.04]."""
    stats=dict(((model or {}).get("events") or {}).get(normalize_event(event)) or {})
    count=max(0,int(stats.get("count",0) or 0))
    signal=_num(stats.get("signal"),0.0)
    if count<4:
        return 1.0

    # Bayesian-like damping: early feedback barely moves the ranker, while
    # sustained preference can reach at most +/-4%.
    learned=signal/(count+12.0)
    delta=max(-0.04,min(0.04,learned*0.11))
    return round(1.0+delta,6)


def event_learning_snapshot(model,event):
    mult=event_multiplier(model,event)
    stats=dict(((model or {}).get("events") or {}).get(normalize_event(event)) or {})
    return {
        "event":normalize_event(event),
        "count":int(stats.get("count",0) or 0),
        "signal":round(_num(stats.get("signal"),0.0),5),
        "multiplier":mult,
    }


def load_model(path=None):
    if path is None:
        root=Path(os.environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime"))
        path=root/"ai_learning_v127.json"
    path=Path(path)
    if not path.is_file():
        return empty_model()
    try:
        payload=json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload,dict) else empty_model()
    except Exception:
        return empty_model()


def save_model(path,model):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(
        json.dumps(model,ensure_ascii=False,separators=(",",":"),sort_keys=True),
        encoding="utf-8",
    )
    os.replace(tmp,path)
    return path
