import base64
import hashlib
import mimetypes
import os
import tempfile
from pathlib import Path
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components

from ai_hidpi_v400 import adaptive_quality_profile, inject_hidpi_runtime
from game_vision_v108 import window_event_map, vision_zones_for_genre


_SOURCE_COMPONENT_DIR = Path(__file__).resolve().parent / "editor_2027_component"


def _prepare_v400_component_dir():
    """Serve the approved editor with an additive V400 Retina layer.

    The checked-in 100 KB editor remains untouched. We derive a tiny cached
    runtime copy in /tmp so V400 can add DPR-aware vector rendering without
    risking regressions in the existing markup, controls or mobile cockpit.
    """
    try:
        source = _SOURCE_COMPONENT_DIR / "index.html"
        raw = source.read_text(encoding="utf-8")
        patched = inject_hidpi_runtime(raw)
        digest = hashlib.sha256(patched.encode("utf-8")).hexdigest()[:12]
        runtime_dir = Path(tempfile.gettempdir()) / f"gsf_editor_2027_v400_{digest}"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        target = runtime_dir / "index.html"
        if not target.exists() or target.read_text(encoding="utf-8") != patched:
            target.write_text(patched, encoding="utf-8")
        return runtime_dir
    except Exception:
        return _SOURCE_COMPONENT_DIR


_COMPONENT_DIR = _prepare_v400_component_dir()
# Keep the historical stable Streamlit component identity. V400 is an additive
# runtime layer, not a new component registration: changing this name breaks
# the editor asset/session contract and the production build guard.
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
    return "editor_2027_state_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


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
        "qualityMode": "Adaptive AI",
        "visionEnabled": False,
        "zones": {},
        "eventMap": [],
    }
    if isinstance(saved, dict):
        state.update(saved)
    state["duration"] = duration
    state["inPoint"] = _clamp(state.get("inPoint"), 0.0, duration, 0.0)
    state["outPoint"] = _clamp(state.get("outPoint"), state["inPoint"] + 0.05, duration, duration)
    return state
