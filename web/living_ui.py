"""GSF Living UI shell.

Presentation-only module. Keep application logic, AI, render, social and Editor
outside this file so visual iterations cannot mutate the production pipeline.
"""
import streamlit as st

LIVING_CSS = r"""
<style id="gsf-living-ui">
:root{
  --gsf-ink:#18243a;
  --gsf-muted:#65778d;
  --gsf-blue:#83c8ee;
  --gsf-blue-strong:#55aedd;
  --gsf-line:rgba(102,155,190,.24);
  --gsf-glass:rgba(255,255,255,.78);
  --gsf-glow:rgba(101,190,239,.30);
  --gsf-soft:#eef8fe;
}
html,body,[data-testid="stAppViewContainer"],.stApp{
  background:
    radial-gradient(circle at 50% -12%,rgba(140,211,247,.24),transparent 34%),
    radial-gradient(circle at 12% 24%,rgba(190,229,248,.13),transparent 24%),
    linear-gradient(180deg,#fbfdff 0%,#f5faff 52%,#ffffff 100%) !important;
  color:var(--gsf-ink) !important;
}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stToolbar"],#MainMenu,footer{visibility:hidden!important}
[data-testid="stDecoration"]{display:none!important}
[data-testid="stAppViewContainer"]{overflow-x:hidden!important}
[data-testid="stAppViewContainer"] .main .block-container{
  max-width:1160px!important;
  padding-top:5.55rem!important;
  padding-bottom:6.2rem!important;
}

/* Native Streamlit surfaces inherit the Living language without touching logic. */
.stButton>button,.stDownloadButton>button{
  min-height:42px;
  border-radius:14px!important;
  border:1px solid rgba(104,176,217,.22)!important;
  background:rgba(255,255,255,.84)!important;
  box-shadow:0 8px 22px rgba(75,135,171,.07)!important;
  transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease,background .18s ease!important;
}
.stButton>button:hover,.stDownloadButton>button:hover{
  transform:translateY(-1px);
  background:rgba(244,251,255,.98)!important;
  border-color:rgba(86,174,224,.44)!important;
  box-shadow:0 11px 28px rgba(75,145,187,.12)!important;
}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:22px!important}
[data-testid="stExpander"]{
  border-radius:18px!important;
  overflow:hidden;
  border-color:rgba(112,169,202,.18)!important;
  background:rgba(255,255,255,.68)!important;
}
[data-testid="stAlert"]{border-radius:16px!important}

/* Brand: text only, no legacy logo. */
.gsf-living-brand{
  position:fixed;top:18px;left:26px;z-index:9999;
  display:flex;align-items:center;gap:8px;
  font-size:18px;font-weight:800;letter-spacing:-.35px;
  color:#17233a;
  animation:gsfBrandIn .7s cubic-bezier(.2,.8,.2,1) both;
}
.gsf-living-brand::after{
  content:"";
  width:7px;height:7px;border-radius:50%;
  background:var(--gsf-blue-strong);
  box-shadow:0 0 0 5px rgba(85,174,221,.10),0 0 16px rgba(85,174,221,.38);
  animation:gsfStatusPulse 2.6s ease-in-out infinite;
}

/* Game Bar: persistent app navigation shell. */
.gsf-living-bar{
  position:fixed;top:11px;left:50%;transform:translateX(-50%);
  z-index:9998;display:flex;align-items:center;gap:6px;
  padding:7px;border:1px solid var(--gsf-line);
  border-radius:19px;background:var(--gsf-glass);
  box-shadow:0 12px 34px rgba(64,116,151,.12),inset 0 1px 0 rgba(255,255,255,.92);
  backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  animation:gsfBarIn .65s cubic-bezier(.2,.8,.2,1) both;
}
.gsf-living-chip{
  display:flex;align-items:center;justify-content:center;gap:6px;
  min-width:46px;height:36px;padding:0 12px;
  border-radius:13px;font-size:12px;font-weight:760;
  color:#506177;background:rgba(245,250,255,.72);
  border:1px solid rgba(121,172,205,.12);
  transition:transform .2s ease,background .2s ease,box-shadow .2s ease,color .2s ease;
}
.gsf-living-chip .gsf-nav-dot{
  width:5px;height:5px;border-radius:50%;
  background:rgba(92,125,151,.42);
}
.gsf-living-chip.active{
  color:#176894;background:rgba(129,202,239,.20);
  box-shadow:inset 0 0 0 1px rgba(105,186,229,.14),0 5px 14px rgba(78,155,198,.08);
}
.gsf-living-chip.active .gsf-nav-dot{
  background:var(--gsf-blue-strong);
  box-shadow:0 0 9px rgba(85,174,221,.44);
}
@media(hover:hover) and (pointer:fine){
  .gsf-living-chip:hover{transform:translateY(-1px);background:rgba(229,245,255,.96);color:#29465c}
}

/* Uploader is the visual heart of Home. */
[data-testid="stFileUploader"]{
  width:min(62vw,430px)!important;
  max-width:430px!important;
  aspect-ratio:1/1!important;
  margin:1.35rem auto 2.2rem!important;
  filter:drop-shadow(0 22px 44px rgba(81,142,180,.13));
}
[data-testid="stFileUploader"]>section{
  height:100%!important;
}
[data-testid="stFileUploaderDropzone"]{
  position:relative;
  height:100%!important;
  min-height:0!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  text-align:center!important;
  border:1px solid rgba(103,181,225,.36)!important;
  border-radius:50%!important;
  background:
    radial-gradient(circle at 50% 0,rgba(137,207,244,.13),transparent 42%),
    linear-gradient(180deg,rgba(255,255,255,.97),rgba(244,251,255,.89))!important;
  box-shadow:
    inset 0 0 0 1px rgba(255,255,255,.92),
    inset 0 0 0 22px rgba(231,247,255,.38),
    0 0 0 12px rgba(184,230,250,.16),
    0 22px 58px rgba(87,153,194,.14)!important;
  animation:gsfLivingBreath 3.1s ease-in-out infinite;
  transition:transform .28s ease,border-color .28s ease,box-shadow .28s ease;
}
[data-testid="stFileUploaderDropzone"]::before{
  content:"CARICA IL TUO GAMEPLAY";
  position:absolute;top:24%;left:50%;transform:translateX(-50%);
  width:78%;
  text-align:center;
  font-size:13px;font-weight:820;letter-spacing:.7px;color:#16395a;
}
[data-testid="stFileUploaderDropzone"]::after{
  content:"";
  position:absolute;inset:-1px;border-radius:50%;pointer-events:none;
  background:radial-gradient(circle at 50% 0,var(--gsf-glow),transparent 47%);
  opacity:.28;animation:gsfUploaderAura 3.1s ease-in-out infinite;
}
[data-testid="stFileUploaderDropzoneInstructions"]{
  max-width:68%!important;
  margin:2.2rem auto 0!important;
  font-weight:650!important;
  color:#61758a!important;
}
[data-testid="stFileUploaderDropzoneInstructions"] small{
  color:#7d8fa2!important;
}
[data-testid="stFileUploaderDropzone"] button{
  border-radius:999px!important;
  padding:.62rem 1.05rem!important;
  background:rgba(226,245,255,.94)!important;
  border-color:rgba(86,174,224,.26)!important;
}
@media(hover:hover) and (pointer:fine){
  [data-testid="stFileUploaderDropzone"]:hover{
    transform:translateY(-2px);
    border-color:rgba(82,174,226,.60)!important;
    box-shadow:
      inset 0 0 0 1px rgba(255,255,255,.9),
      0 18px 50px rgba(87,169,216,.16)!important;
  }
}

/* Home hierarchy and controls: visual-only Living pass. */
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3{
  color:#17233a!important;
  letter-spacing:-.035em!important;
  line-height:1.04!important;
}
[data-testid="stAppViewContainer"] h1{
  font-size:clamp(2rem,4.2vw,3.35rem)!important;
  font-weight:820!important;
  margin-bottom:.45rem!important;
}
[data-testid="stAppViewContainer"] h2{
  font-size:clamp(1.45rem,2.4vw,2.1rem)!important;
  font-weight:790!important;
}
[data-testid="stAppViewContainer"] h3{
  font-size:clamp(1.08rem,1.8vw,1.4rem)!important;
  font-weight:760!important;
}
[data-testid="stAppViewContainer"] p,
[data-testid="stCaptionContainer"]{
  color:var(--gsf-muted)!important;
}
[data-testid="stMarkdownContainer"] strong{
  color:#26384b;
}

/* Inputs feel integrated instead of default widgets. */
[data-baseweb="select"]>div,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea{
  border-radius:14px!important;
  border-color:rgba(105,166,201,.22)!important;
  background:rgba(255,255,255,.82)!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.86)!important;
}
[data-baseweb="select"]>div:focus-within,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus{
  border-color:rgba(80,170,220,.56)!important;
  box-shadow:0 0 0 3px rgba(102,190,238,.10)!important;
}

/* Choice controls and tabs become lighter app controls. */
[data-testid="stRadio"] [role="radiogroup"],
[data-testid="stSegmentedControl"]{
  gap:8px!important;
}
[data-testid="stTabs"] [role="tablist"]{
  gap:7px!important;
  background:rgba(245,250,255,.68);
  padding:5px;
  border-radius:16px;
  border:1px solid rgba(110,169,203,.14);
}
[data-testid="stTabs"] [role="tab"]{
  border-radius:11px!important;
  padding:.42rem .8rem!important;
}
[data-testid="stTabs"] [aria-selected="true"]{
  background:rgba(132,203,240,.16)!important;
}

/* Progress and status surfaces look alive but calm. */
[data-testid="stProgress"]>div>div{
  border-radius:999px!important;
  overflow:hidden!important;
  background:rgba(137,197,231,.15)!important;
}
[data-testid="stProgress"]>div>div>div{
  border-radius:999px!important;
  box-shadow:0 0 14px rgba(85,174,221,.18);
}
[data-testid="stMetric"]{
  padding:.85rem 1rem!important;
  border-radius:18px!important;
  background:rgba(255,255,255,.64)!important;
  border:1px solid rgba(108,166,199,.13)!important;
}

/* Main CTA buttons get a more product-like visual weight. */
.stButton>button[kind="primary"],
button[data-testid="baseButton-primary"]{
  color:#15364a!important;
  font-weight:790!important;
  background:
    linear-gradient(180deg,rgba(176,222,247,.96),rgba(139,205,239,.92))!important;
  border-color:rgba(77,164,212,.30)!important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.82),
    0 10px 25px rgba(72,153,198,.15)!important;
}
@media(hover:hover) and (pointer:fine){
  .stButton>button[kind="primary"]:hover,
  button[data-testid="baseButton-primary"]:hover{
    background:
      linear-gradient(180deg,rgba(187,228,249,.98),rgba(148,211,243,.96))!important;
    transform:translateY(-1px) scale(1.006);
  }
}

/* Keep vertical rhythm compact and intentional. */
[data-testid="stAppViewContainer"] [data-testid="stVerticalBlock"]{
  row-gap:.72rem;
}
[data-testid="stHorizontalBlock"]{
  gap:1rem!important;
}
hr{
  border-color:rgba(104,160,194,.13)!important;
  margin:1.3rem 0!important;
}


/* Living cards: soft app-like surfaces inspired by the approved Home direction. */
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{
  min-width:0!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"]{
  background:linear-gradient(180deg,rgba(255,255,255,.90),rgba(249,252,255,.78))!important;
  border:1px solid rgba(113,170,204,.14)!important;
  box-shadow:0 14px 32px rgba(82,133,165,.08)!important;
  backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] .stButton>button{
  border-radius:999px!important;
}
@media(hover:hover) and (pointer:fine){
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"]{
    transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"]:hover{
    transform:translateY(-2px);
    border-color:rgba(91,178,225,.24)!important;
    box-shadow:0 18px 38px rgba(82,144,180,.12)!important;
  }
}

/* Key motion is soft and bounded. */
@keyframes gsfBrandIn{
  from{opacity:0;transform:translateY(-7px)}
  to{opacity:1;transform:none}
}
@keyframes gsfBarIn{
  from{opacity:0;transform:translate(-50%,-8px) scale(.98)}
  to{opacity:1;transform:translate(-50%,0) scale(1)}
}
@keyframes gsfStatusPulse{
  0%,100%{opacity:.62;transform:scale(.92)}
  50%{opacity:1;transform:scale(1.08)}
}
@keyframes gsfUploaderAura{
  0%,100%{opacity:.20}
  50%{opacity:.56}
}
@keyframes gsfLivingBreath{
  0%,100%{box-shadow:inset 0 0 0 1px rgba(255,255,255,.75),0 14px 42px rgba(87,153,194,.09)}
  50%{box-shadow:inset 0 0 0 1px rgba(255,255,255,.92),0 17px 50px rgba(87,169,216,.17)}
}

/* Mobile is a native bottom navigation, not a shrunk desktop header. */
@media(max-width:760px){
  [data-testid="stAppViewContainer"] .main .block-container{
    padding-top:4.35rem!important;
    padding-bottom:6.8rem!important;
  }
  .gsf-living-brand{
    left:16px;top:15px;font-size:15px;
  }
  .gsf-living-brand::after{width:6px;height:6px}
  .gsf-living-bar{
    top:auto;bottom:10px;
    width:calc(100% - 20px);
    justify-content:space-between;
    gap:4px;padding:7px;
    border-radius:24px;
    box-shadow:0 14px 38px rgba(74,126,158,.16),inset 0 1px 0 rgba(255,255,255,.95);
  }
  .gsf-living-chip{
    min-width:0;flex:1;height:42px;padding:0 4px;
    font-size:10px;gap:4px;border-radius:12px;
  }
  .gsf-living-chip .gsf-nav-dot{width:4px;height:4px}
  [data-testid="stFileUploader"]{
    width:min(82vw,350px)!important;
    max-width:350px!important;
    margin:1rem auto 1.8rem!important;
  }
  [data-testid="stFileUploaderDropzone"]{
    border-radius:50%!important;
  }
  [data-testid="stFileUploaderDropzone"]::before{
    top:23%;font-size:11px;letter-spacing:.55px;
  }
  [data-testid="stFileUploaderDropzone"]::after{border-radius:50%}
}
@media(max-width:760px){
  [data-testid="stHorizontalBlock"]{gap:.65rem!important}
  [data-testid="stAppViewContainer"] h1{font-size:2rem!important}
  [data-testid="stAppViewContainer"] h2{font-size:1.45rem!important}
  .stButton>button,.stDownloadButton>button{min-height:44px!important}
}
@media(max-width:420px){
  .gsf-living-chip{font-size:9px}
  .gsf-living-chip .gsf-nav-dot{display:none}
}
@media(prefers-reduced-motion:reduce){
  [data-testid="stFileUploaderDropzone"],
  [data-testid="stFileUploaderDropzone"]::after,
  .gsf-living-brand,
  .gsf-living-brand::after,
  .gsf-living-bar{animation:none!important}
}
</style>
"""

SHELL_HTML = r"""
<div class="gsf-living-brand">Gaming Shorts Factory</div>
<nav class="gsf-living-bar" aria-label="GSF Game Bar">
  <div class="gsf-living-chip active"><span class="gsf-nav-dot"></span>Home</div>
  <div class="gsf-living-chip"><span class="gsf-nav-dot"></span>AI</div>
  <div class="gsf-living-chip"><span class="gsf-nav-dot"></span>Editor</div>
  <div class="gsf-living-chip"><span class="gsf-nav-dot"></span>Share</div>
  <div class="gsf-living-chip"><span class="gsf-nav-dot"></span>Creator Hub</div>
</nav>
"""

def render_shell() -> None:
    """Render presentation only; no session-state or pipeline mutations."""
    st.markdown(LIVING_CSS, unsafe_allow_html=True)
    st.markdown(SHELL_HTML, unsafe_allow_html=True)
