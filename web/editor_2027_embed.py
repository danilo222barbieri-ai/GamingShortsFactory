import base64
import hashlib
import mimetypes
import os
from pathlib import Path
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components

from game_vision_v108 import window_event_map, vision_zones_for_genre


_COMPONENT_DIR = Path(__file__).resolve().parent / "editor_2027_component"
# One stable component name/path for every clip. Dynamic per-video component
# folders caused intermittent asset 404s behind Railway/Streamlit.
_EDITOR_2027_COMPONENT = components.declare_component(
    "gsf_editor_2027_v1086",
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
    state["captionOn"] = state["captionMode"] != "Off"
    state["inPoint"] = _clamp(state.get("inPoint"), 0.0, 59.5, 0.0)
    state["outPoint"] = max(
        state["inPoint"] + 0.5,
        _clamp(state.get("outPoint"), 0.5, 60.0, duration),
    )
    return state


def editor_2027_clip_bounds(state, fallback_duration=15.0):
    fallback_duration = _clamp(fallback_duration, 0.5, 60.0, 15.0)
    if not isinstance(state, dict):
        return 0.0, fallback_duration
    start = _clamp(state.get("inPoint"), 0.0, 59.5, 0.0)
    out = _clamp(state.get("outPoint"), start + 0.5, 60.0, start + fallback_duration)
    return start, max(0.5, out - start)


def _editor_video_url(video_path):
    p = Path(video_path)
    if not p.is_file():
        return ""

    # Web/Railway: register the exact file for this browser session. The iframe
    # then resolves it through /editor-media/current, independent of whether
    # Streamlit delivers its first custom-component render message.
    try:
        sessions_root = (
            Path(os.environ.get("GSF_RUNTIME_ROOT", "/tmp/gsf-runtime"))
            / "sessions"
        ).resolve()
        resolved = p.resolve()
        rel = resolved.relative_to(sessions_root)
        if len(rel.parts) >= 3:
            session_root = sessions_root / rel.parts[0]
            marker = session_root / "editor2027_current.txt"
            marker.write_text(str(resolved), encoding="utf-8")
            stat = resolved.stat()
            fingerprint = f"{stat.st_size}-{int(stat.st_mtime)}"
            return "/editor-media/current?v=" + quote(fingerprint, safe="")
    except Exception:
        pass

    # Local desktop/dev fallback.
    mime = mimetypes.guess_type(str(p))[0] or "video/mp4"
    raw = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{raw}"

def _editor_component_for(video_path):
    # Frontend assets are served from the repository's static component
    # directory. The actual clip URL/state arrives through Streamlit's render
    # message, so changing clips no longer registers a brand-new component.
    video_url = _editor_video_url(Path(video_path))
    return _EDITOR_2027_COMPONENT, video_url


def render_editor_2027_embed(
    video_path,
    height=720,
    key="gsf_editor_2027",
    initial_state=None,
    clip_start=0.0,
    source_duration=None,
):
    p = Path(video_path)
    state = editor_2027_initial_state(
        (initial_state or {}).get("outPoint", 15.0)
        if isinstance(initial_state, dict)
        else 15.0,
        initial_state,
    )
    component, video_url = _editor_component_for(p)

    # V108 static intelligence metadata stays OUTSIDE mutable Editor state so
    # Undo/Redo remains tiny and global. The timeline receives only events that
    # actually belong to the currently loaded clip.
    try:
        _raw_events=st.session_state.get("gsf_v108_event_map") or []
        _genre=str(st.session_state.get("gsf_v108_game_genre") or "Auto")
    except Exception:
        _raw_events=[]
        _genre="Auto"
    _window_duration=(
        _clamp(source_duration,0.05,21600.0,state.get("outPoint",15.0))
        if source_duration is not None else
        _clamp(state.get("outPoint",15.0),0.05,21600.0,15.0)
    )
    _events=window_event_map(
        _raw_events,
        clip_start=_clamp(clip_start,0.0,21600.0,0.0),
        clip_duration=_window_duration,
        max_events=14,
    )
    _brain_hint={}
    try:
        _brain=st.session_state.get("gsf_v112_brain_context") or {}
        _selected=list(_brain.get("selected") or []) if isinstance(_brain,dict) else []
        if _selected:
            _clip_start=float(clip_start or 0.0)
            _nearest=min(_selected,key=lambda row:abs(float((row or {}).get("start") or 0.0)-_clip_start))
            _distance=abs(float((_nearest or {}).get("start") or 0.0)-_clip_start)
            if _distance<=max(1.5,min(5.0,_window_duration*0.25)):
                _brain_hint=dict(_nearest or {})
                _brain_hint["engine"]=str(_brain.get("engine") or "game-brain-v112")
                _brain_hint["genre"]=str(_brain.get("genre") or _genre)
    except Exception:
        _brain_hint={}
    value = component(
        video_url=video_url,
        initial_state=state,
        event_map=_events,
        event_duration=_window_duration,
        vision_profile=_genre,
        vision_zones=vision_zones_for_genre(_genre),
        brain_context=_brain_hint,
        height=int(height),
        key=str(key),
        default=None,
    )
    return value if isinstance(value, dict) else None


def editor_2027_render_kwargs(state, session_state=None):
    state = editor_2027_initial_state(
        (state or {}).get("outPoint", 15.0) if isinstance(state, dict) else 15.0,
        state,
    )
    ss = session_state if session_state is not None else {}

    look = str(state.get("look") or "Clean")
    filter_map = {
        "Clean": "Originale",
        "Competitive": "Gaming / Vibrante",
        "Boss Cinematic": "Cinematico",
    }
    audio_mode = str(state.get("audioMode") or "Originale")
    caption_mode = str(state.get("captionMode") or ("Auto" if state.get("captionOn", True) else "Off"))
    if caption_mode not in {"Auto", "Fixed", "Off"}:
        caption_mode = "Auto"
    caption_on = caption_mode != "Off"

    subtitle_words = None
    try:
        subtitle_words = ss.get("editor_sub_live_words") or ss.get("editor_sub_words")
    except Exception:
        subtitle_words = None
    if not isinstance(subtitle_words, list):
        subtitle_words = None

    try:
        subtitle_mode = (
            ss.get("editor_sub_mode_v18")
            or ss.get("editor_sub_mode")
            or "Automatici"
        )
        subtitle_font = ss.get("editor_sub_font_v18") or "Arial"
    except Exception:
        subtitle_mode = "Automatici"
        subtitle_font = "Arial"

    # AUTO only burns real transcribed words. FIXED deliberately ignores the
    # transcription and uses the user's text. OFF burns nothing.
    if caption_mode == "Off":
        subtitle_mode = "Nessuno"
        subtitle_words = None
        subtitle_text = ""
    elif caption_mode == "Fixed":
        subtitle_mode = "Manuale"
        subtitle_words = None
        subtitle_text = str(state.get("captionText") or "").strip()
    else:
        subtitle_text = ""

    fmt = str(state.get("format") or "9:16 Short")
    if "16:9" in fmt:
        fmt = "16:9 Originale"
    else:
        fmt = "9:16 Short"

    hud_mode = str(state.get("hudMode") or "Off")
    hud_safe = hud_mode != "Off"
    smart_reframe = bool(state.get("visionEnabled", False) or hud_safe)

    return {
        "fmt": fmt,
        "zoom": _clamp(state.get("zoom"), 0.8, 2.0, 1.0),
        "x_pos": _clamp(state.get("panX"), -25.0, 25.0, 0.0) * 4.0,
        "y_pos": _clamp(state.get("panY"), -25.0, 25.0, 0.0) * 4.0,
        "brightness": (_clamp(state.get("brightness"), 70, 130, 100) - 100.0) / 100.0,
        "contrast": _clamp(state.get("contrast"), 70, 150, 100) / 100.0,
        "speed": _clamp(state.get("speed"), 0.5, 2.0, 1.0),
        "volume": 0 if bool(state.get("muted")) else int(_clamp(state.get("volume"), 0, 100, 100)),
        "subtitles_enabled": caption_on,
        "subtitle_mode": str(subtitle_mode),
        "subtitle_words": subtitle_words,
        "subtitle_text": subtitle_text,
        "subtitle_font": str(subtitle_font),
        "subtitle_size": int(round(_clamp(state.get("captionSize"), 18, 70, 36) * 2.55)),
        "subtitle_x": 50,
        "subtitle_y": _clamp(state.get("captionY"), 15, 88, 76),
        "text_color": str(state.get("textColor") or "#ffffff"),
        "active_color": str(state.get("activeColor") or "#ffd400"),
        "outline_color": str(state.get("outlineColor") or "#000000"),
        "normalize_audio": audio_mode in {"Game Boost", "Personalizzato"},
        "smart_reframe": smart_reframe,
        "polish_audio": True,
        "filter_preset": filter_map.get(look, "Originale"),
        "filter_intensity": int(round(_clamp(state.get("intensity"), 0, 100, 64))),
        "hook_text": "",
    }
