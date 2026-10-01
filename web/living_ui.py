"""GSF Living UI shell.

Presentation-only module. Keep application logic, AI, render, social and Editor
outside this file so visual iterations cannot mutate the production pipeline.
"""
import streamlit as st

LIVING_CSS = r"""
<style id="gsf-living-ui">
:root{
  --gsf-ink:#18243a;
  --gsf-blue:#83c8ee;
  --gsf-line:rgba(102,155,190,.24);
  --gsf-glass:rgba(255,255,255,.78);
}
html,body,[data-testid="stAppViewContainer"],.stApp{
  background:
    radial-gradient(circle at 50% -10%,rgba(140,211,247,.20),transparent 36%),
    linear-gradient(180deg,#fbfdff 0%,#f5faff 52%,#ffffff 100%) !important;
  color:var(--gsf-ink) !important;
}
[data-testid="stAppViewContainer"] .main .block-container{
  max-width:1200px !important;
  padding-top:5.3rem !important;
  padding-bottom:6rem !important;
}
.gsf-living-brand{
  position:fixed; top:18px; left:26px; z-index:9999;
  font-size:18px; font-weight:800; letter-spacing:-.35px;
  color:#17233a;
}
.gsf-living-bar{
  position:fixed; top:12px; left:50%; transform:translateX(-50%);
  z-index:9998; display:flex; align-items:center; gap:7px;
  padding:7px 9px; border:1px solid var(--gsf-line);
  border-radius:18px; background:var(--gsf-glass);
  box-shadow:0 12px 34px rgba(64,116,151,.12);
  backdrop-filter:blur(18px); -webkit-backdrop-filter:blur(18px);
}
.gsf-living-chip{
  display:flex; align-items:center; justify-content:center;
  min-width:42px; height:34px; padding:0 12px;
  border-radius:12px; font-size:12px; font-weight:750;
  color:#506177; background:rgba(245,250,255,.82);
  border:1px solid rgba(121,172,205,.14);
}
.gsf-living-chip.active{
  color:#176894; background:rgba(129,202,239,.18);
  box-shadow:inset 0 0 0 1px rgba(105,186,229,.14);
}
[data-testid="stFileUploader"]{
  max-width:720px !important; margin:1.2rem auto !important;
  filter:drop-shadow(0 18px 34px rgba(81,142,180,.10));
}
[data-testid="stFileUploaderDropzone"]{
  border:1px solid rgba(103,181,225,.34) !important;
  border-radius:28px !important;
  background:rgba(255,255,255,.84) !important;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.75),
             0 14px 42px rgba(87,153,194,.09) !important;
  animation:gsfLivingBreath 3.2s ease-in-out infinite;
}
@keyframes gsfLivingBreath{
  0%,100%{box-shadow:inset 0 0 0 1px rgba(255,255,255,.75),0 14px 42px rgba(87,153,194,.09)}
  50%{box-shadow:inset 0 0 0 1px rgba(255,255,255,.9),0 16px 48px rgba(87,169,216,.18)}
}
@media(max-width:760px){
  .gsf-living-brand{left:16px;top:15px;font-size:15px}
  .gsf-living-bar{top:auto;bottom:12px;width:calc(100% - 24px);justify-content:space-between}
  .gsf-living-chip{min-width:0;flex:1;padding:0 5px;font-size:11px}
  [data-testid="stAppViewContainer"] .main .block-container{padding-top:4.4rem !important;padding-bottom:6.4rem !important}
}
@media(prefers-reduced-motion:reduce){
  [data-testid="stFileUploaderDropzone"]{animation:none}
}
</style>
"""

SHELL_HTML = r"""
<div class="gsf-living-brand">Gaming Shorts Factory</div>
<div class="gsf-living-bar" aria-label="GSF Game Bar">
  <div class="gsf-living-chip active">Home</div>
  <div class="gsf-living-chip">AI</div>
  <div class="gsf-living-chip">Editor</div>
  <div class="gsf-living-chip">Share</div>
  <div class="gsf-living-chip">Hub</div>
</div>
"""

def render_shell() -> None:
    """Render presentation only; no session-state or pipeline mutations."""
    st.markdown(LIVING_CSS, unsafe_allow_html=True)
    st.markdown(SHELL_HTML, unsafe_allow_html=True)
