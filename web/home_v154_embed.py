from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

from web.ui_release import GSF_UI_RELEASE

_COMPONENT_DIR = Path(__file__).resolve().parent / "home_v154_component"
_HOME_V154_COMPONENT = components.declare_component(
    f"gsf_home_v154_live_{GSF_UI_RELEASE}",
    path=str(_COMPONENT_DIR),
)


def render_home_v154(*, loaded=False, duration=15, engine="", height=900, key="gsf_home_v155"):
    # V308: one parent shell for every viewport. The component owns the same
    # browser work area on phone, tablet and desktop; only its internal fluid
    # CSS changes scale and spacing.
    st.html(r"""
    <style id="gsf-v308-viewport-shell">
      html,body,.stApp,
      [data-testid="stAppViewContainer"],
      [data-testid="stMain"]{
        width:100vw !important;
        height:100dvh !important;
        min-height:100dvh !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
        overscroll-behavior:none !important;
      }

      [data-testid="stHeader"],
      [data-testid="stToolbar"],
      [data-testid="stDecoration"],
      [data-testid="stStatusWidget"]{
        display:none !important;
        height:0 !important;
        min-height:0 !important;
        max-height:0 !important;
        margin:0 !important;
        padding:0 !important;
      }

      [data-testid="stMainBlockContainer"],
      .main .block-container{
        position:fixed !important;
        inset:0 !important;
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        min-height:0 !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
      }

      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154"]){
        position:fixed !important;
        inset:0 !important;
        width:100vw !important;
        height:100dvh !important;
        min-height:0 !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
        z-index:1 !important;
      }

      [data-testid="stCustomComponentV1"]:has(iframe[title*="gsf_home_v154"]){
        position:absolute !important;
        inset:0 !important;
        width:100% !important;
        height:100% !important;
        min-height:0 !important;
        max-height:none !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
      }

      iframe[title*="gsf_home_v154"],
      iframe[src*="home_v154"]{
        position:absolute !important;
        inset:0 !important;
        display:block !important;
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        min-height:100dvh !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        border:0 !important;
      }

      [data-testid="stElementContainer"]:has(#gsf-creator-hub-live-v160),
      [data-testid="stElementContainer"]:has(#gsf-social-overlay-v159),
      [data-testid="stElementContainer"]:has(#gsf-editor-overlay-v220),
      [data-testid="stElementContainer"]:has(#gsf-ai-overlay-v221){
        position:relative !important;
        z-index:120 !important;
        overflow:visible !important;
      }
    </style>
    """)

    value = _HOME_V154_COMPONENT(
        loaded=bool(loaded),
        duration=int(duration or 15),
        engine=str(engine or ""),
        height=int(height),
        key=str(key),
        default=None,
    )
    return value if isinstance(value, dict) else None
