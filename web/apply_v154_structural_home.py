from pathlib import Path

src=Path("/app/GamingShortsFactory_V152_UI_RESET.py")
out=Path("/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py")
s=src.read_text(encoding="utf-8")

anchor='with st.container(key="v73-upload-shell"):\n'
if anchor not in s:
    raise RuntimeError("V154 uploader anchor missing")

block=r'''
# V154 Structural Home — real custom component, not a CSS reskin.
# The existing V98.9/V99 direct-upload backend, AI engine and Editor remain
# authoritative. This component replaces only the Home presentation layer.
if GSF_WEB_MODE:
    from web.home_v154_embed import render_home_v154 as _gsf_render_home_v154

    st.html(r"""
    <style id="gsf-v154-parent-shell">
    /* The new component owns the production Home. Keep the old uploader
       mounted only as an invisible fallback so its backend/state contracts
       remain available during migration. */
    .st-key-v73-upload-shell{
        display:none !important;
        height:0 !important;
        min-height:0 !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
    }
    .gsf-living-brand,
    .gsf-living-bar{
        display:none !important;
    }

    /* V154.1 owns these Home CTAs. Keep the real Streamlit widgets mounted
       as action targets for the component, but remove their duplicate UI. */
    .st-key-gsf-major-create-ai,
    .st-key-gsf-major-personalize,
    [class*="st-key-gsf-major-game-editor_"],
    .st-key-gsf-major-create-short,
    [class*="st-key-edit_ai_"],
    .st-key-create_final_short_v54{
        position:absolute !important;
        width:1px !important;
        height:1px !important;
        overflow:hidden !important;
        opacity:0 !important;
        pointer-events:none !important;
        margin:0 !important;
        padding:0 !important;
    }

    /* Remove only the legacy chrome that TinyFish sees under V154 Home. */
    [data-testid="sync-short-ready-button"],
    .st-sync-ready,
    .sync-short-ready,
    [data-testid="footer"],
    .st-footer,
    .gsf-footer-v4{
        display:none !important;
    }
    </style>
    """)

    _gsf_v154_duration=int(st.session_state.get("gsf_v154_duration",15) or 15)
    if _gsf_v154_duration not in (15,30):
        _gsf_v154_duration=15
    _gsf_v154_engine=str(st.session_state.get("gsf_v154_engine","") or "")

    _gsf_v154_event=_gsf_render_home_v154(
        loaded=bool(video is not None),
        duration=_gsf_v154_duration,
        engine=_gsf_v154_engine,
        height=1180 if video is not None else 1080,
        key="gsf_home_v154_live",
    )

    if isinstance(_gsf_v154_event,dict):
        _v154_event=str(_gsf_v154_event.get("event") or "")
        _v154_duration=int(_gsf_v154_event.get("duration") or _gsf_v154_duration or 15)
        _v154_engine=str(_gsf_v154_event.get("engine") or _gsf_v154_engine or "")
        if _v154_duration in (15,30):
            st.session_state["gsf_v154_duration"]=_v154_duration
        if _v154_engine in ("","auto","best","action","reaction","manual"):
            st.session_state["gsf_v154_engine"]=_v154_engine

        # Direct upload finishes in the existing upload server before the
        # component emits this event. A clean rerun lets _gsf_v989_direct_ready
        # materialize the source into the existing pipeline.
        if _v154_event=="upload_complete" and video is None:
            st.rerun()

'''
s=s.replace(anchor,block+anchor,1)

s=s.replace(
    "Gaming Shorts Factory · V152 UI Reset",
    "Gaming Shorts Factory · V154 Structural Home",
)

# Hard migration guards.
for marker in (
    "render_home_v154",
    'key="gsf_home_v154_live"',
    "gsf-v154-parent-shell",
    'with st.container(key="v73-upload-shell")',
):
    if marker not in s:
        raise RuntimeError("V154 marker missing: "+marker)

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V154 STRUCTURAL HOME applied:",out)
