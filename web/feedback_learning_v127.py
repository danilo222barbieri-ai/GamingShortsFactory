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


# ============================================================================
# BLOCCO 4 — IA PERSONALIZZATA ISOLATA PER UTENTE
# ============================================================================

def empty_user_model() -> dict:
    return {
        "engine": "v3.0-user-preferences",
        "updated_at": 0.0,
        "total_feedback": 0,
        "events": {},
        "genres": {},
        "recent_choices": [],
    }


def user_preferences_path(
    sid: str = "",
    account_id: str | None = None,
    runtime_root: Path | str | None = None
) -> Path:
    from pathlib import Path
    import os
    if runtime_root:
        base = Path(runtime_root)
    else:
        env_root = os.environ.get("GSF_RUNTIME_ROOT")
        base = Path(env_root) if env_root else Path("/tmp/gsf-runtime")

    acc = str(account_id or "").strip()
    if acc:
        return base / "users" / acc / "ai_user_preferences.json"

    clean_sid = str(sid or "").strip()
    if clean_sid:
        # Check if sid has a linked creator account
        try:
            sess_file = base / "sessions" / clean_sid / "session.json"
            if sess_file.is_file():
                sdata = json.loads(sess_file.read_text(encoding="utf-8"))
                found_acc = str(sdata.get("account_id") or "").strip()
                if found_acc:
                    return base / "users" / found_acc / "ai_user_preferences.json"
        except Exception:
            pass
        return base / "sessions" / clean_sid / "ai_user_preferences.json"

    return base / "users" / "default" / "ai_user_preferences.json"


def load_user_model(
    sid: str = "",
    account_id: str | None = None,
    runtime_root: Path | str | None = None
) -> dict:
    acc = str(account_id or "").strip()
    clean_sid = str(sid or "").strip()
    if not acc and not clean_sid:
        return empty_user_model()

    path = user_preferences_path(clean_sid, account_id=acc, runtime_root=runtime_root)
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    # Seamless migration: if authenticated account has no saved preferences yet,
    # but the guest session does, migrate guest preferences to the account.
    if acc and clean_sid:
        guest_path = user_preferences_path(clean_sid, account_id=None, runtime_root=runtime_root)
        if guest_path.is_file() and guest_path != path:
            try:
                guest_data = json.loads(guest_path.read_text(encoding="utf-8"))
                if isinstance(guest_data, dict) and guest_data.get("total_feedback", 0) > 0:
                    save_user_model(clean_sid, guest_data, account_id=acc, runtime_root=runtime_root)
                    return guest_data
            except Exception:
                pass

    return empty_user_model()


def save_user_model(
    sid: str = "",
    model: dict | None = None,
    account_id: str | None = None,
    runtime_root: Path | str | None = None
) -> Path:
    payload = model if isinstance(model, dict) else empty_user_model()
    path = user_preferences_path(sid, account_id=account_id, runtime_root=runtime_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
        encoding="utf-8",
    )
    os.replace(tmp, path)
    return path


def reset_user_model(
    sid: str = "",
    account_id: str | None = None,
    runtime_root: Path | str | None = None
) -> dict:
    model = empty_user_model()
    save_user_model(sid, model, account_id=account_id, runtime_root=runtime_root)
    return model


def update_user_preferences(
    sid: str = "",
    event_row: dict | None = None,
    account_id: str | None = None,
    runtime_root: Path | str | None = None
) -> dict:
    """Incrementally update user preferences with interpretable bounded shifts."""
    current = load_user_model(sid, account_id=account_id, runtime_root=runtime_root)
    events = dict(current.get("events") or {})
    genres = dict(current.get("genres") or {})
    recent = list(current.get("recent_choices") or [])

    event = normalize_event((event_row or {}).get("event"))
    action = str((event_row or {}).get("action") or "selected").strip().lower()
    genre = str((event_row or {}).get("genre") or "Auto").strip()
    score = _num((event_row or {}).get("brain_score") or (event_row or {}).get("score"), 0.0)
    weight = float(_ACTION_WEIGHTS.get(action, 0.5))

    # 1. Update event statistics
    st = dict(events.get(event) or {})
    actions = dict(st.get("actions") or {})
    actions[action] = int(actions.get(action, 0) or 0) + 1
    cnt = int(st.get("count", 0) or 0) + 1
    sig = _num(st.get("signal"), 0.0) + weight
    st.update({
        "count": cnt,
        "signal": round(sig, 4),
        "actions": actions,
        "updated_at": time.time(),
    })
    events[event] = st

    # 2. Update genre statistics if provided
    if genre and genre != "Auto":
        gst = dict(genres.get(genre) or {})
        g_actions = dict(gst.get("actions") or {})
        g_actions[action] = int(g_actions.get(action, 0) or 0) + 1
        g_cnt = int(gst.get("count", 0) or 0) + 1
        g_sig = _num(gst.get("signal"), 0.0) + weight
        preferred = list(gst.get("preferred_events") or [])
        if action in ("selected", "published") and event not in preferred:
            preferred.append(event)
        gst.update({
            "count": g_cnt,
            "signal": round(g_sig, 4),
            "actions": g_actions,
            "preferred_events": preferred[:5],
            "updated_at": time.time(),
        })
        genres[genre] = gst

    # 3. Add to recent choices (cap at 30 entries)
    recent.append({
        "timestamp": round(time.time(), 2),
        "event": event,
        "genre": genre,
        "action": action,
        "score": round(score, 3),
    })
    recent = recent[-30:]

    current.update({
        "engine": "v3.0-user-preferences",
        "updated_at": time.time(),
        "total_feedback": int(current.get("total_feedback", 0) or 0) + 1,
        "events": events,
        "genres": genres,
        "recent_choices": recent,
    })
    save_user_model(sid, current, account_id=account_id, runtime_root=runtime_root)
    return current


def user_learning_multiplier(model: dict, event: str, genre: str = "Auto") -> float:
    """Interpretable combined user preference multiplier, safely bounded in [0.88, 1.14]."""
    evt = normalize_event(event)
    events = (model or {}).get("events") or {}
    est = events.get(evt) or {}
    e_cnt = max(0, int(est.get("count", 0) or 0))
    e_sig = _num(est.get("signal"), 0.0)

    e_delta = 0.0
    if e_cnt >= 2:
        e_learned = e_sig / (e_cnt + 8.0)
        e_delta = max(-0.08, min(0.08, e_learned * 0.12))

    g_delta = 0.0
    g = str(genre or "Auto")
    if g != "Auto":
        genres = (model or {}).get("genres") or {}
        gst = genres.get(g) or {}
        g_cnt = max(0, int(gst.get("count", 0) or 0))
        g_sig = _num(gst.get("signal"), 0.0)
        if g_cnt >= 2:
            g_learned = g_sig / (g_cnt + 8.0)
            g_delta = max(-0.05, min(0.05, g_learned * 0.10))

    mult = 1.0 + e_delta + g_delta
    return round(max(0.88, min(1.14, mult)), 4)
