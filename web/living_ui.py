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
  --gsf-glass:rgba(255,255,255,.76);\n  --gsf-glow:rgba(101,190,239,.30);\n  --gsf-soft:#eef8fe;
}
html,body,[data-testid="stAppViewContainer"],.stApp{
  background:
    radial-gradient(circle at 50% -10%,rgba(140,211,247,.20),transparent 36%),
    linear-gradient(180deg,#fbfdff 0%,#f5faff 52%,#ffffff 100%) !important;
  color:var(--gsf-ink) !important;
}

/* App-shell polish: presentation only. */
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stToolbar"],#MainMenu,footer{visibility:hidden!important}
[data-testid="stDecoration"]{display:none!important}
[data-testid="stAppViewContainer"]{overflow-x:hidden!important}
.stButton>button,.stDownloadButton>button{
  border-radius:14px!important;
  border:1px solid rgba(104,176,217,.22)!important;
  box-shadow:0 8px 22px rgba(75,135,171,.07)!important;
  transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease!important;
}
.stButton>button:hover,.stDownloadButton>button:hover{
  transform:translateY(-1px);
  border-color:rgba(86,174,224,.44)!important;
  box-shadow:0 11px 28px rgba(75,145,187,.12)!important;
}
[data-testid="stVerticalBlockBorderWrapper"]{
  border-radius:22px!important;
}
[data-testid="stExpander"]{
  border-radius:18px!important;
  overflow:hidden;
  border-color:rgba(112,169,202,.18)!important;
  background:rgba(255,255,255,.66)!important;
}
[data-testid="stAlert"]{
  border-radius:16px!important;
}

[data-testid="stAppViewContainer"] .main .block-container{
  max-width:1200px !important;
  padding-top:5.3rem !important;
  padding-bottom:6rem !important;
}
.gsf-living-brand{
  position:fixed; top:18px; left:26px; z-index:9999;
  font-size:18px; font-weight:800; letter-spacing:-.35px;\n  animation:gsfBrandIn .7s cubic-bezier(.2,.8,.2,1) both;
  color:#17233a;
}
.gsf-living-bar{
  position:fixed; top:12px; left:50%; transform:translateX(-50%);
  z-index:9998; display:flex; align-items:center; gap:7px;
  padding:7px 9px; border:1px solid var(--gsf-line);
  border-radius:18px; background:var(--gsf-glass);
  box-shadow:0 12px 34px rgba(64,116,151,.12);
  backdrop-filter:blur(18px); -webkit-backdrop-filter:blur(18px);\n  animation:gsfBarIn .65s cubic-bezier(.2,.8,.2,1) both;
}
.gsf-living-chip{
  display:flex; align-items:center; justify-content:center;
  min-width:42px; height:34px; padding:0 12px;
  border-radius:12px; font-size:12px; font-weight:750;
  color:#506177; background:rgba(245,250,255,.82);
  border:1px solid rgba(121,172,205,.14);\n  transition:transform .2s ease,background .2s ease,box-shadow .2s ease;
}
.gsf-living-chip:hover{transform:translateY(-1px);background:rgba(229,245,255,.96)}\n.gsf-living-chip.active{
  color:#176894; background:rgba(129,202,239,.18);
  box-shadow:inset 0 0 0 1px rgba(105,186,229,.14);
}
@keyframes gsfBrandIn{from{opacity:0;transform:translateY(-7px)}to{opacity:1;transform:none}}\n@keyframes gsfBarIn{from{opacity:0;transform:translate(-50%,-8px) scale(.98)}to{opacity:1;transform:translate(-50%,0) scale(1)}}\n/* Living uploader: make the first action feel like the center of the product. */\n[data-testid="stFileUploader"]{
  max-width:680px !important; margin:1.8rem auto 2.4rem !important;
  filter:drop-shadow(0 18px 34px rgba(81,142,180,.10));
}
[data-testid="stFileUploaderDropzone"]{
  border:1px solid rgba(103,181,225,.34) !important;
  border-radius:32px !important;
  background:linear-gradient(180deg,rgba(255,255,255,.96),rgba(244,251,255,.88)) !important;
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.75),
             0 14px 42px rgba(87,153,194,.09) !important;
  animation:gsfLivingBreath 3.2s ease-in-out infinite;\n  min-height:156px!important;\n  transition:transform .28s ease,border-color .28s ease;
}
[data-testid="stFileUploaderDropzoneInstructions"]{font-weight:650!important;color:#4b6177!important}\n[data-testid="stFileUploaderDropzone"] button{border-radius:999px!important;padding:.62rem 1rem!important;background:rgba(226,245,255,.9)!important}\n[data-testid="stFileUploaderDropzone"]:hover{transform:translateY(-2px);border-color:rgba(82,174,226,.58)!important}\n[data-testid="stFileUploaderDropzone"]::after{\n  content:"";position:absolute;inset:-1px;border-radius:28px;pointer-events:none;\n  background:radial-gradient(circle at 50% 0,var(--gsf-glow),transparent 46%);\n  opacity:.35;animation:gsfUploaderAura 3.2s ease-in-out infinite;\n}\n@keyframes gsfUploaderAura{0%,100%{opacity:.22}50%{opacity:.62}}\n@keyframes gsfLivingBreath{
  0%,100%{box-shadow:inset 0 0 0 1px rgba(255,255,255,.75),0 14px 42px rgba(87,153,194,.09)}
  50%{box-shadow:inset 0 0 0 1px rgba(255,255,255,.9),0 16px 48px rgba(87,169,216,.18)}
}
@media(max-width:760px){\n  [data-testid="stFileUploader"]{max-width:100%!important;margin-top:1.1rem!important}\n  [data-testid="stFileUploaderDropzone"]{min-height:138px!important;border-radius:26px!important}
  .gsf-living-brand{left:16px;top:15px;font-size:15px}
  .gsf-living-bar{top:auto;bottom:12px;width:calc(100% - 24px);justify-content:space-between}
  .gsf-living-chip{min-width:0;flex:1;padding:0 5px;font-size:11px}
  [data-testid="stAppViewContainer"] .main .block-container{padding-top:4.4rem !important;padding-bottom:6.4rem !important}
}
@media(prefers-reduced-motion:reduce){
  [data-testid="stFileUploaderDropzone"],[data-testid="stFileUploaderDropzone"]::after,.gsf-living-brand,.gsf-living-bar{animation:none}
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
  <div class="gsf-living-chip">Creator Hub</div>
</div>
"""

def render_shell() -> None:
    """Render presentation only; no session-state or pipeline mutations."""
    st.markdown(LIVING_CSS, unsafe_allow_html=True)
    st.markdown(SHELL_HTML, unsafe_allow_html=True)
