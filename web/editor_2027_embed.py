import base64
import hashlib
import mimetypes
import os
from pathlib import Path
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components

from game_vision_v108 import window_event_map, vision_zones_for_genre
try:
    from web.ui_release import GSF_UI_RELEASE
except ModuleNotFoundError:
    # Docker build-time component tests execute this module with /app/web as
    # sys.path[0], so the package-qualified import is not always resolvable.
    from ui_release import GSF_UI_RELEASE


_COMPONENT_DIR = Path(__file__).resolve().parent / "editor_2027_component"
# One stable component name/path for every clip. Dynamic per-video component
# folders caused intermittent asset 404s behind Railway/Streamlit.
_EDITOR_2027_COMPONENT = components.declare_component(
    f"gsf_editor_2027_v{GSF_UI_RELEASE}",
    path=str(_COMPONENT_DIR),
)


def _clamp(value, low, high, fallback):
    try:
        value = float(value)
    except Exception:
        value = float(fallback)
    return max(float(low), min(float(high), value))


def editor_2027_state_key(video_path):
    raw = str(Path(video_path).resolve())
    return "editor_2027_state_" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def editor_2027_initial_state(duration=15.0, saved=None):
    duration = _clamp(duration, 0.5, 60.0, 15.0)
    state = {
        "zoom": 1.0,
        "panX": 0.0,
        "panY": 0.0,
        "framePreset": "free",
        "coverMode": "Auto",
        "coverTime": 0.0,
        "coverLocked": False,
        "look": "Clean",
        "intensity": 64,
        "brightness": 100,
        "contrast": 100,
        "hudMode": "Off",
        "captionOn": True,
        "captionMode": "Auto",
        "captionText": "",
        "captionSize": 36,
        "captionY": 76,
        "textColor": "#ffffff",
        "activeColor": "#ffd400",
        "outlineColor": "#000000",
        "muted": False,
        "volume": 100,
        "speed": 1.0,
        "audioMode": "Originale",
        "inPoint": 0.0,
        "outPoint": duration,
        "aiMode": "Auto Gaming",
        "visionEnabled": False,
    }
    if isinstance(saved, dict):
        state.update(saved)
        if "captionMode" not in saved:
            state["captionMode"] = "Off" if saved.get("captionOn") is False else "Auto"
    if state.get("look") == "Neon Arena":
        state["look"] = "Competitive"
    if state.get("look") == "Dark Raid":
        state["look"] = "Boss Cinematic"
    if str(state.get("hudMode") or "Off") not in {"Off", "Smart Safe"}:
        state["hudMode"] = "Smart Safe"
    if str(state.get("captionMode") or "Auto") not in {"Auto", "Fixed", "Off"}:
        state["captionMode"] = "Auto"
    state["duration"] = duration
    state["outPoint"] = _clamp(state.get("outPoint"), 0.5, duration, duration)
    state["inPoint"] = _clamp(state.get("inPoint"), 0.0, max(0.0, state["outPoint"] - 0.1), 0.0)
    return state


def editor_2027_clip_bounds(state, duration):
    data = editor_2027_initial_state(duration, state)
    return float(data["inPoint"]), float(data["outPoint"])


def editor_2027_render_kwargs(state, duration):
    data = editor_2027_initial_state(duration, state)
    in_point, out_point = editor_2027_clip_bounds(data, duration)
    return {
        "trim_start": in_point,
        "trim_end": out_point,
        "zoom": float(data["zoom"]),
        "pan_x": float(data["panX"]),
        "pan_y": float(data["panY"]),
        "brightness": int(data["brightness"]),
        "contrast": int(data["contrast"]),
        "muted": bool(data["muted"]),
        "volume": int(data["volume"]),
        "speed": float(data["speed"]),
        "look": str(data["look"]),
        "filter_preset": str(data["look"]),
        "filter_intensity": int(data["intensity"]),
        "caption_on": bool(data["captionOn"]),
        "caption_mode": str(data.get("captionMode") or ("Auto" if data["captionOn"] else "Off")),
        "caption_text": str(data["captionText"]),
        "caption_size": int(data["captionSize"]),
        "caption_y": int(data["captionY"]),
        "caption_color": str(data["textColor"]),
        "caption_active_color": str(data["activeColor"]),
        "caption_outline_color": str(data["outlineColor"]),
        "cover_mode": str(data["coverMode"]),
        "cover_time": float(data["coverTime"]),
        "cover_locked": bool(data["coverLocked"]),
        "audio_mode": str(data["audioMode"]),
        "frame_preset": str(data["framePreset"]),
        "ai_mode": str(data["aiMode"]),
        "vision_enabled": bool(data["visionEnabled"]),
    }


def _editor_video_url(video_path, media_url=None):
    if media_url:
        return str(media_url)
    path = Path(video_path)
    try:
        resolved = path.resolve()
    except Exception:
        resolved = path
    mime = mimetypes.guess_type(str(resolved))[0] or "video/mp4"
    try:
        raw = resolved.read_bytes()
    except Exception:
        return ""
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def editor_2027_html(video_path, state=None, duration=15.0, media_url=None, event_map=None, genre=None):
    html_path = _COMPONENT_DIR / "index.html"
    html = html_path.read_text(encoding="utf-8")
    source = _editor_video_url(video_path, media_url=media_url)
    initial = editor_2027_initial_state(duration, state)
    if event_map is None:
        event_map = window_event_map([], duration)
    if genre:
        initial["visionZones"] = vision_zones_for_genre(genre)
    initial["eventMap"] = event_map
    payload = {
        "videoUrl": source,
        "state": initial,
        "duration": float(duration),
    }
    import json
    encoded = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = html.replace("__GSF_EDITOR_BOOTSTRAP__", encoded)
    return html


def render_editor_2027(video_path, state=None, duration=15.0, media_url=None, event_map=None, genre=None, key=None):
    initial = editor_2027_initial_state(duration, state)
    payload = {
        "videoUrl": _editor_video_url(video_path, media_url=media_url),
        "state": initial,
        "duration": float(duration),
        "eventMap": event_map if event_map is not None else window_event_map([], duration),
        "visionZones": vision_zones_for_genre(genre) if genre else {},
    }
    result = _EDITOR_2027_COMPONENT(
        payload=payload,
        default=initial,
        key=key or editor_2027_state_key(video_path),
    )
    return result if isinstance(result, dict) else initial
