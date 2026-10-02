from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

_COMPONENT_DIR = Path(__file__).resolve().parent / "home_v154_component"
_HOME_V154_COMPONENT = components.declare_component(
    "gsf_home_v154_live_191",
    path=str(_COMPONENT_DIR),
)

def render_home_v154(*, loaded=False, duration=15, engine="", height=900, key="gsf_home_v155"):
    # V181 MOBILE FULL-VIEWPORT SHELL
    # On phones the Home component must own the real viewport: no Streamlit
    # spacer above it and no parent-page scroll below it.
    st.html(r"""
    <style id="gsf-mobile-full-viewport-v181">
    @media (max-width:760px){
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
        z-index:30 !important;
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
