from pathlib import Path
import streamlit.components.v1 as components

_COMPONENT_DIR = Path(__file__).resolve().parent / "home_v154_component"
_HOME_V154_COMPONENT = components.declare_component(
    "gsf_home_v154_live_178",
    path=str(_COMPONENT_DIR),
)

def render_home_v154(*, loaded=False, duration=15, engine="", height=900, key="gsf_home_v155"):
    value = _HOME_V154_COMPONENT(
        loaded=bool(loaded),
        duration=int(duration or 15),
        engine=str(engine or ""),
        height=int(height),
        key=str(key),
        default=None,
    )
    return value if isinstance(value, dict) else None
