import base64
import hashlib
import html
import mimetypes
import os
from pathlib import Path
from urllib.parse import quote

import streamlit.components.v1 as components


_COMPONENT_DIR = Path(__file__).resolve().parent / "editor_2027_component"
_EDITOR_2027_TEMPLATE = (_COMPONENT_DIR / "index.html").read_text(encoding="utf-8")
_EDITOR_COMPONENT_CACHE = {}


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
        "look": "Clean",
        "intensity": 64,
        "brightness": 100,
        "contrast": 100,
        "hudMode": "Off",
        "captionOn": True,
        "captionText": "NO SCOPE CLUTCH!",
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

    # The Editor runs inside a Streamlit component iframe. On Safari/iOS and
    # Chromium/Android a session-protected /media URL can lose the parent
    # session context. Embed the selected clip directly so every browser gets
    # an immediately playable source independent of cookies/range routing.
    mime = mimetypes.guess_type(str(p))[0] or "video/mp4"
    raw = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{raw}"

def _editor_component_for(video_path):
    p = Path(video_path)
    video_url = _editor_video_url(p)
    digest = hashlib.sha1(
        (str(p.resolve()) + "|" + video_url).encode("utf-8")
    ).hexdigest()[:16]
    component = _EDITOR_COMPONENT_CACHE.get(digest)
    if component is not None:
        return component, video_url

    runtime_root = Path(os.environ.get("GSF_RUNTIME_ROOT", "/tmp/gsf-runtime"))
    component_dir = runtime_root / "editor2027_components" / digest
    component_dir.mkdir(parents=True, exist_ok=True)
    target = component_dir / "index.html"

    safe_url = html.escape(video_url, quote=True)
    rendered = _EDITOR_2027_TEMPLATE.replace(
        '<video id="video" playsinline muted loop preload="metadata" src=""></video>',
        f'<video id="video" playsinline muted loop preload="metadata" src="{safe_url}"></video>',
        1,
    )
    target.write_text(rendered, encoding="utf-8")

    component = components.declare_component(
        f"gsf_editor_2027_{digest}",
        path=str(component_dir),
    )
    _EDITOR_COMPONENT_CACHE[digest] = component
    return component, video_url


def render_editor_2027_embed(
    video_path,
    height=720,
    key="gsf_editor_2027",
    initial_state=None,
):
    p = Path(video_path)
    state = editor_2027_initial_state(
        (initial_state or {}).get("outPoint", 15.0)
        if isinstance(initial_state, dict)
        else 15.0,
        initial_state,
    )
    component, video_url = _editor_component_for(p)
    value = component(
        video_url=video_url,
        initial_state=state,
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
        "Neon Arena": "Gaming / Vibrante",
        "Dark Raid": "Cinematico",
        "Boss Cinematic": "Cinematico",
    }
    audio_mode = str(state.get("audioMode") or "Originale")
    caption_on = bool(state.get("captionOn", True))

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

    if not caption_on:
        subtitle_mode = "Nessuno"

    fmt = str(state.get("format") or "9:16 Short")
    if "16:9" in fmt:
        fmt = "16:9 Originale"
    else:
        fmt = "9:16 Short"

    return {
        "fmt": fmt,
        "zoom": _clamp(state.get("zoom"), 1.0, 2.0, 1.0),
        "x_pos": _clamp(state.get("panX"), -25.0, 25.0, 0.0) * 4.0,
        "y_pos": _clamp(state.get("panY"), -25.0, 25.0, 0.0) * 4.0,
        "brightness": (_clamp(state.get("brightness"), 70, 130, 100) - 100.0) / 100.0,
        "contrast": _clamp(state.get("contrast"), 70, 150, 100) / 100.0,
        "speed": _clamp(state.get("speed"), 0.5, 2.0, 1.0),
        "volume": 0 if bool(state.get("muted")) else int(_clamp(state.get("volume"), 0, 100, 100)),
        "subtitles_enabled": caption_on,
        "subtitle_mode": str(subtitle_mode),
        "subtitle_words": subtitle_words,
        "subtitle_text": str(state.get("captionText") or ""),
        "subtitle_font": str(subtitle_font),
        "subtitle_size": int(round(_clamp(state.get("captionSize"), 18, 70, 36) * 2.55)),
        "subtitle_x": 50,
        "subtitle_y": _clamp(state.get("captionY"), 15, 88, 76),
        "text_color": str(state.get("textColor") or "#ffffff"),
        "active_color": str(state.get("activeColor") or "#ffd400"),
        "outline_color": str(state.get("outlineColor") or "#000000"),
        "normalize_audio": audio_mode in {"Game Boost", "Personalizzato"},
        "smart_reframe": bool(state.get("visionEnabled", False)),
        "polish_audio": True,
        "filter_preset": filter_map.get(look, "Originale"),
        "filter_intensity": int(round(_clamp(state.get("intensity"), 0, 100, 64))),
        "hook_text": "",
    }
