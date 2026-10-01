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


/* Reference fidelity pass: cleaner hierarchy, brighter canvas, stronger app feel. */
[data-testid="stAppViewContainer"] .main{
  position:relative;
}
[data-testid="stAppViewContainer"] .main::before{
  content:"";
  position:fixed;
  inset:64px 5% auto 5%;
  height:310px;
  pointer-events:none;
  background:
    radial-gradient(circle at 50% 20%,rgba(137,207,244,.15),transparent 42%),
    radial-gradient(circle at 25% 65%,rgba(201,239,226,.12),transparent 26%),
    radial-gradient(circle at 78% 62%,rgba(255,231,158,.10),transparent 25%);
  filter:blur(4px);
  z-index:0;
}
[data-testid="stAppViewContainer"] .main .block-container{
  position:relative;
  z-index:1;
}
[data-testid="stWidgetLabel"]{
  color:#51677d!important;
  font-weight:680!important;
  letter-spacing:-.01em!important;
}
[data-testid="stCaptionContainer"]{
  font-size:.82rem!important;
}
[data-testid="stFileUploader"]{
  isolation:isolate;
}
[data-testid="stFileUploaderDropzone"]{
  overflow:hidden!important;
}
[data-testid="stFileUploaderDropzone"] > div{
  position:relative;
  z-index:2;
}
[data-testid="stFileUploaderDropzone"] button{
  min-height:40px!important;
  padding:.55rem 1rem!important;
  box-shadow:0 8px 20px rgba(75,145,187,.09)!important;
}
[data-testid="stFileUploaderDropzone"] button:hover{
  box-shadow:0 10px 24px rgba(75,145,187,.14)!important;
}
[data-testid="stVerticalBlockBorderWrapper"]{
  border:1px solid rgba(113,170,204,.14)!important;
  background:rgba(255,255,255,.66)!important;
  box-shadow:0 12px 32px rgba(82,133,165,.06)!important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h3{
  margin-top:.15rem!important;
}
[data-testid="stExpander"] summary{
  min-height:48px!important;
  align-items:center!important;
}
[data-testid="stTabs"]{
  margin-top:.2rem!important;
}
[data-testid="stTabs"] [role="tablist"]{
  width:max-content;
  max-width:100%;
}
[data-testid="stTabs"] [role="tab"]{
  min-height:38px!important;
}
.stButton>button,
.stDownloadButton>button{
  font-weight:720!important;
  letter-spacing:-.01em!important;
}
@media(min-width:761px){
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{
    transition:transform .2s ease;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]){
    align-self:stretch;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) .stButton{
    margin-top:.25rem!important;
  }
}
@media(max-width:760px){
  [data-testid="stAppViewContainer"] .main::before{
    inset:54px 0 auto 0;
    height:240px;
  }
  [data-testid="stVerticalBlockBorderWrapper"]{
    border-radius:19px!important;
  }
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

/* V153.8 — large Living fidelity pass: hero, guidance, cards, dock, responsive. */

@media(min-width:980px){
  [data-testid="stAppViewContainer"] .main .block-container{
    max-width:1080px!important;
    padding-top:6.15rem!important;
  }
}

/* Central living uploader with side guidance. */
[data-testid="stFileUploader"]{
  position:relative!important;
  overflow:visible!important;
  margin-top:2.35rem!important;
  margin-bottom:3.4rem!important;
}
[data-testid="stFileUploader"]::before,
[data-testid="stFileUploader"]::after{
  position:absolute;
  top:50%;
  width:220px;
  transform:translateY(-50%);
  color:rgba(52,79,104,.66);
  font-size:15px;
  line-height:1.28;
  font-weight:560;
  font-style:italic;
  letter-spacing:-.02em;
  pointer-events:none;
  z-index:3;
}
[data-testid="stFileUploader"]::before{
  content:"Trasforma il tuo gameplay in Shorts  →";
  right:calc(100% + 34px);
  text-align:right;
}
[data-testid="stFileUploader"]::after{
  content:"←  Trascina qui o tocca per caricare";
  left:calc(100% + 34px);
  text-align:left;
}
[data-testid="stFileUploaderDropzone"]{
  background:
    radial-gradient(circle at 50% 42%,rgba(255,255,255,.99) 0 42%,rgba(246,252,255,.96) 58%,rgba(228,246,255,.93) 100%)!important;
  box-shadow:
    inset 0 0 0 1px rgba(255,255,255,.98),
    inset 0 0 0 19px rgba(223,244,255,.34),
    inset 0 -18px 34px rgba(133,199,234,.07),
    0 0 0 10px rgba(181,228,249,.15),
    0 0 0 21px rgba(181,228,249,.055),
    0 26px 70px rgba(78,143,182,.15)!important;
}
[data-testid="stFileUploaderDropzone"]::after{
  background:
    radial-gradient(circle at 50% 22%,rgba(113,199,244,.34),transparent 38%),
    radial-gradient(circle at 50% 78%,rgba(192,235,255,.12),transparent 48%)!important;
}
[data-testid="stFileUploaderDropzone"] button{
  border-radius:999px!important;
  padding:.58rem 1.08rem!important;
  background:linear-gradient(180deg,rgba(236,248,255,.98),rgba(218,241,253,.94))!important;
  color:#24465e!important;
  font-weight:760!important;
}
[data-testid="stFileUploaderDropzoneInstructions"]{
  text-align:center!important;
}
[data-testid="stFileUploaderDropzoneInstructions"]>div{
  justify-content:center!important;
}

/* App-card language across Home. */
[data-testid="stVerticalBlockBorderWrapper"]{
  border-radius:25px!important;
  background:
    linear-gradient(180deg,rgba(255,255,255,.92),rgba(248,252,255,.78))!important;
  border:1px solid rgba(116,174,207,.13)!important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.95),
    0 16px 38px rgba(80,130,160,.075)!important;
  backdrop-filter:blur(16px);
  -webkit-backdrop-filter:blur(16px);
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"]{
  min-height:100%;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] [data-testid="stMarkdownContainer"] p{
  line-height:1.42!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] h3{
  margin-bottom:.35rem!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] .stButton{
  margin-top:.35rem!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] .stButton>button{
  border-radius:999px!important;
  min-width:44px!important;
}

/* Stronger primary actions, softer secondary actions. */
.stButton>button[kind="primary"],
button[data-testid="baseButton-primary"]{
  min-height:46px!important;
  padding:.62rem 1.15rem!important;
  border-radius:15px!important;
  background:
    linear-gradient(180deg,rgba(181,225,248,.98),rgba(141,205,239,.95))!important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.88),
    0 12px 26px rgba(72,153,198,.16)!important;
}
.stButton>button:not([kind="primary"]),
.stDownloadButton>button{
  background:rgba(255,255,255,.78)!important;
}

/* Cleaner section rhythm. */
[data-testid="stAppViewContainer"] h1{
  margin-top:.1rem!important;
  margin-bottom:.35rem!important;
}
[data-testid="stAppViewContainer"] h2{
  margin-top:1.45rem!important;
  margin-bottom:.55rem!important;
}
[data-testid="stAppViewContainer"] h3{
  margin-bottom:.4rem!important;
}
[data-testid="stAppViewContainer"] [data-testid="stVerticalBlock"]{
  row-gap:.66rem!important;
}
[data-testid="stHorizontalBlock"]{
  gap:.9rem!important;
}

/* Bottom dock feels like a real native app control. */
@media(max-width:760px){
  .gsf-living-bar{
    bottom:9px!important;
    border-radius:26px!important;
    padding:7px!important;
    background:rgba(255,255,255,.86)!important;
    box-shadow:
      0 16px 42px rgba(70,126,158,.17),
      inset 0 1px 0 rgba(255,255,255,.98)!important;
  }
  .gsf-living-chip{
    height:44px!important;
    border-radius:15px!important;
    font-size:10px!important;
  }
  .gsf-living-chip.active{
    background:rgba(132,203,240,.22)!important;
  }

  [data-testid="stFileUploader"]{
    width:min(82vw,340px)!important;
    margin-top:1.15rem!important;
    margin-bottom:2.15rem!important;
  }
  [data-testid="stFileUploader"]::before,
  [data-testid="stFileUploader"]::after{
    display:none!important;
  }
  [data-testid="stFileUploaderDropzone"]{
    box-shadow:
      inset 0 0 0 1px rgba(255,255,255,.98),
      inset 0 0 0 14px rgba(223,244,255,.30),
      0 0 0 8px rgba(181,228,249,.13),
      0 20px 52px rgba(78,143,182,.13)!important;
  }
  [data-testid="stHorizontalBlock"]{
    gap:.7rem!important;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"]{
    border-radius:21px!important;
  }
}

@media(min-width:761px) and (max-width:1180px){
  [data-testid="stFileUploader"]::before,
  [data-testid="stFileUploader"]::after{
    width:150px;
    font-size:13px;
  }
  [data-testid="stFileUploader"]::before{right:calc(100% + 18px)}
  [data-testid="stFileUploader"]::after{left:calc(100% + 18px)}
}

/* V153.9 — native app polish: icon dock, media, controls, compact responsive. */
.gsf-living-chip{
  min-width:58px!important;
}
.gsf-nav-icon{
  width:17px;
  height:17px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  flex:0 0 auto;
}
.gsf-nav-icon svg{
  width:100%;
  height:100%;
  fill:none;
  stroke:currentColor;
  stroke-width:1.75;
  stroke-linecap:round;
  stroke-linejoin:round;
}
.gsf-living-chip.active .gsf-nav-icon{
  filter:drop-shadow(0 2px 5px rgba(65,156,207,.22));
}
.gsf-nav-label{
  white-space:nowrap;
}

/* Rich media adopts the same soft radius as the approved reference. */
[data-testid="stImage"],
[data-testid="stImage"] img,
[data-testid="stVideo"],
[data-testid="stVideo"] video{
  border-radius:20px!important;
}
[data-testid="stImage"] img,
[data-testid="stVideo"] video{
  box-shadow:0 12px 30px rgba(61,104,132,.10)!important;
}
[data-testid="stImage"]{
  overflow:hidden!important;
}

/* Sliders, toggles and checks feel part of one product. */
[data-testid="stSlider"] [data-baseweb="slider"]{
  padding-top:.35rem!important;
  padding-bottom:.35rem!important;
}
[data-testid="stSlider"] [role="slider"]{
  box-shadow:0 0 0 4px rgba(92,183,231,.10)!important;
}
[data-testid="stCheckbox"] label,
[data-testid="stToggle"] label{
  color:#4f6478!important;
  font-weight:620!important;
}
[data-testid="stCheckbox"] input:checked + div,
[data-testid="stToggle"] input:checked + div{
  box-shadow:0 0 0 3px rgba(96,186,233,.10);
}

/* Pills and badges read lighter and more modern. */
[data-testid="stPills"] button,
[data-testid="stSegmentedControl"] button{
  border-radius:999px!important;
  min-height:38px!important;
  border-color:rgba(109,170,205,.16)!important;
}
[data-testid="stPills"] button[aria-pressed="true"],
[data-testid="stSegmentedControl"] button[aria-pressed="true"]{
  background:rgba(129,202,239,.18)!important;
}

/* Cleaner upload icon / instruction stack. */
[data-testid="stFileUploaderDropzone"] svg{
  color:#73bfe8!important;
  filter:drop-shadow(0 5px 12px rgba(89,174,220,.18));
}
[data-testid="stFileUploaderDropzoneInstructions"] span{
  font-weight:720!important;
  color:#405b72!important;
}
[data-testid="stFileUploaderDropzoneInstructions"] small{
  font-size:.72rem!important;
  letter-spacing:.02em;
}

/* Recent-project-like rows gain depth without changing their content. */
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] [data-testid="stImage"]{
  margin-bottom:.45rem!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] [data-testid="stImage"] img{
  aspect-ratio:16/9;
  object-fit:cover;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] [data-testid="stCaptionContainer"]{
  margin-top:-.1rem!important;
  padding-left:.1rem!important;
}

/* Desktop dock gets more air and less 'button' feeling. */
@media(min-width:761px){
  .gsf-living-bar{
    padding:7px 8px!important;
    gap:5px!important;
  }
  .gsf-living-chip{
    height:38px!important;
    padding:0 13px!important;
    background:transparent!important;
    border-color:transparent!important;
  }
  .gsf-living-chip.active{
    background:rgba(129,202,239,.18)!important;
    border-color:rgba(105,186,229,.12)!important;
  }
}

/* Mobile dock uses stacked icon + label, like a native app bar. */
@media(max-width:760px){
  .gsf-living-chip{
    flex-direction:column!important;
    gap:2px!important;
    height:50px!important;
    padding:5px 3px 4px!important;
    line-height:1!important;
  }
  .gsf-nav-icon{
    width:18px;
    height:18px;
  }
  .gsf-nav-label{
    font-size:8.5px;
    font-weight:720;
    max-width:100%;
    overflow:hidden;
    text-overflow:ellipsis;
  }
  .gsf-living-chip:nth-child(4) .gsf-nav-label{
    font-size:7.6px;
  }
  [data-testid="stImage"],
  [data-testid="stImage"] img,
  [data-testid="stVideo"],
  [data-testid="stVideo"] video{
    border-radius:17px!important;
  }
  [data-testid="stAppViewContainer"] [data-testid="stVerticalBlock"]{
    row-gap:.58rem!important;
  }
}

@media(max-width:390px){
  .gsf-living-bar{
    width:calc(100% - 14px)!important;
    bottom:7px!important;
  }
  .gsf-nav-label{font-size:7.8px}
  .gsf-living-chip:nth-child(4) .gsf-nav-label{font-size:7px}
}

/* V153.10 — large premium card/section pass aligned to approved Living reference. */

/* Three main action areas get distinct soft identities without changing behavior. */
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]){
  position:relative;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]{
  overflow:hidden!important;
  isolation:isolate;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]::before{
  content:"";
  position:absolute;
  width:120px;
  height:120px;
  border-radius:50%;
  top:-52px;
  right:-34px;
  z-index:-1;
  opacity:.5;
  filter:blur(.2px);
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:nth-child(1):has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]::before{
  background:radial-gradient(circle,rgba(117,200,244,.28),rgba(117,200,244,0) 68%);
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:nth-child(2):has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]::before{
  background:radial-gradient(circle,rgba(157,226,199,.26),rgba(157,226,199,0) 68%);
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:nth-child(3):has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]::before{
  background:radial-gradient(circle,rgba(246,220,137,.26),rgba(246,220,137,0) 68%);
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) h3{
  font-size:1.18rem!important;
  font-weight:800!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) p{
  min-height:2.4em;
  color:#6b7c8e!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) .stButton>button{
  width:100%!important;
  justify-content:center!important;
}

/* Section headers mimic the reference: title left, controls lighter and compact. */
[data-testid="stAppViewContainer"] h2{
  position:relative;
  padding-bottom:.18rem;
}
[data-testid="stAppViewContainer"] h2::after{
  content:"";
  display:block;
  width:32px;
  height:3px;
  margin-top:.42rem;
  border-radius:999px;
  background:linear-gradient(90deg,rgba(85,174,221,.68),rgba(85,174,221,.08));
}
[data-testid="stAppViewContainer"] h2 + [data-testid="stCaptionContainer"],
[data-testid="stAppViewContainer"] h2 + div [data-testid="stCaptionContainer"]{
  margin-top:-.15rem!important;
}

/* Media/project cards feel cinematic and tactile. */
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]){
  border-radius:23px;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]) [data-testid="stImage"]{
  position:relative;
  overflow:hidden!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]) [data-testid="stImage"]::after{
  content:"";
  position:absolute;
  inset:auto 0 0 0;
  height:40%;
  pointer-events:none;
  background:linear-gradient(180deg,transparent,rgba(17,31,43,.12));
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]) img{
  transition:transform .28s ease,filter .28s ease!important;
}
@media(hover:hover) and (pointer:fine){
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]):hover img{
    transform:scale(1.018);
    filter:saturate(1.025) contrast(1.01);
  }
}

/* Inputs and forms become quieter, matching the Living canvas. */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-baseweb="select"]>div{
  min-height:44px!important;
}
[data-testid="stTextArea"] textarea{
  padding:.8rem .9rem!important;
}
[data-testid="stForm"]{
  border-radius:24px!important;
  border-color:rgba(108,168,202,.14)!important;
  background:rgba(255,255,255,.62)!important;
  box-shadow:0 14px 34px rgba(82,133,165,.055)!important;
}

/* Status/progress elements sit closer to the app language. */
[data-testid="stStatusWidget"],
[data-testid="stNotification"],
[data-testid="stToast"]{
  border-radius:18px!important;
}
[data-testid="stProgress"]{
  margin:.45rem 0!important;
}
[data-testid="stProgress"]>div{
  height:8px!important;
  border-radius:999px!important;
}

/* Desktop: stronger center composition, less web-page feel. */
@media(min-width:1000px){
  [data-testid="stAppViewContainer"] .main .block-container{
    padding-left:2.4rem!important;
    padding-right:2.4rem!important;
  }
  [data-testid="stFileUploader"]{
    width:min(40vw,445px)!important;
    max-width:445px!important;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]{
    min-height:178px!important;
  }
}

/* Tablet: preserve the reference hierarchy without crowding. */
@media(min-width:761px) and (max-width:999px){
  [data-testid="stFileUploader"]{
    width:min(50vw,390px)!important;
    max-width:390px!important;
  }
  [data-testid="stHorizontalBlock"]{
    gap:.75rem!important;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) h3{
    font-size:1.05rem!important;
  }
}

/* Mobile: cards become compact but keep hierarchy and touch comfort. */
@media(max-width:760px){
  [data-testid="stAppViewContainer"] .main .block-container{
    padding-left:.8rem!important;
    padding-right:.8rem!important;
  }
  [data-testid="stAppViewContainer"] h2{
    margin-top:1.15rem!important;
  }
  [data-testid="stAppViewContainer"] h2::after{
    width:26px;
    height:2px;
    margin-top:.32rem;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]{
    min-height:0!important;
    padding-top:.12rem!important;
    padding-bottom:.12rem!important;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) p{
    min-height:0;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]) [data-testid="stImage"] img{
    aspect-ratio:16/9;
  }
}

/* Gentle entry of primary visual regions only. */
@keyframes gsfSurfaceIn{
  from{opacity:0;transform:translateY(7px)}
  to{opacity:1;transform:none}
}
[data-testid="stFileUploader"],
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]){
  animation:gsfSurfaceIn .48s ease both;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]):nth-child(2){animation-delay:.05s}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]):nth-child(3){animation-delay:.10s}

@media(prefers-reduced-motion:reduce){
  [data-testid="stFileUploader"],
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]){
    animation:none!important;
  }
}

/* V153.11 — first-screen composition and stronger reference match. */

/* Make the first viewport read as one designed composition. */
[data-testid="stAppViewContainer"] .main .block-container{
  padding-top:5.8rem!important;
}
[data-testid="stAppViewContainer"] h1:first-of-type{
  text-align:center!important;
  max-width:760px;
  margin-left:auto!important;
  margin-right:auto!important;
}
[data-testid="stAppViewContainer"] h1:first-of-type + div,
[data-testid="stAppViewContainer"] h1:first-of-type + [data-testid="stCaptionContainer"]{
  max-width:720px;
  margin-left:auto!important;
  margin-right:auto!important;
  text-align:center!important;
}

/* The upload circle now feels like a real focal object, not a styled widget. */
[data-testid="stFileUploader"]{
  width:min(36vw,420px)!important;
  max-width:420px!important;
  min-width:340px!important;
}
[data-testid="stFileUploaderDropzone"]{
  border-width:1px!important;
  border-color:rgba(102,185,230,.32)!important;
}
[data-testid="stFileUploaderDropzone"]::before{
  top:22%!important;
  font-size:12px!important;
  letter-spacing:.75px!important;
}
[data-testid="stFileUploaderDropzoneInstructions"]{
  margin-top:2.55rem!important;
}
[data-testid="stFileUploaderDropzoneInstructions"] small{
  display:block!important;
  margin-top:.25rem!important;
}
[data-testid="stFileUploaderDropzone"] button{
  margin-top:.45rem!important;
  min-width:126px!important;
}

/* Main action cards: equal rhythm and clear visual grouping. */
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]){
  display:flex!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"])>div{
  width:100%!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]{
  height:100%!important;
  padding:1rem 1rem .9rem!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stMarkdownContainer"]{
  min-height:64px;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) .stButton{
  margin-top:auto!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) .stButton>button{
  height:44px!important;
  min-height:44px!important;
}

/* Recent-project/media groups become quieter and more premium. */
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]){
  background:rgba(255,255,255,.54);
  border:1px solid rgba(107,166,200,.10);
  border-radius:22px;
  padding:.45rem;
  box-shadow:0 12px 28px rgba(73,122,153,.055);
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]) [data-testid="stMarkdownContainer"]{
  padding:0 .25rem .15rem;
}

/* Keep headings and section controls compact and modern. */
[data-testid="stAppViewContainer"] h2{
  font-size:clamp(1.35rem,2vw,1.85rem)!important;
}
[data-testid="stAppViewContainer"] h3{
  line-height:1.15!important;
}
[data-testid="stCaptionContainer"]{
  line-height:1.35!important;
}

/* Desktop spacing tuned for one-screen hierarchy. */
@media(min-width:1100px){
  [data-testid="stAppViewContainer"] .main .block-container{
    max-width:1110px!important;
  }
  [data-testid="stFileUploader"]{
    margin-top:1.4rem!important;
    margin-bottom:2.7rem!important;
  }
  [data-testid="stHorizontalBlock"]{
    gap:1rem!important;
  }
}

/* Tablet keeps the uploader central without crushing the side guidance. */
@media(min-width:761px) and (max-width:1099px){
  [data-testid="stFileUploader"]{
    width:min(44vw,380px)!important;
    min-width:320px!important;
  }
  [data-testid="stFileUploader"]::before,
  [data-testid="stFileUploader"]::after{
    width:135px!important;
    font-size:12px!important;
  }
}

/* Mobile: native-app density, centered hero, cards readable without huge scrolling. */
@media(max-width:760px){
  [data-testid="stAppViewContainer"] .main .block-container{
    padding-top:4.05rem!important;
    padding-bottom:6.9rem!important;
  }
  [data-testid="stAppViewContainer"] h1:first-of-type{
    font-size:1.82rem!important;
    margin-bottom:.25rem!important;
  }
  [data-testid="stFileUploader"]{
    width:min(78vw,318px)!important;
    min-width:0!important;
    max-width:318px!important;
    margin-top:.85rem!important;
    margin-bottom:1.75rem!important;
  }
  [data-testid="stFileUploaderDropzone"]::before{
    top:21%!important;
    font-size:10px!important;
  }
  [data-testid="stFileUploaderDropzoneInstructions"]{
    max-width:72%!important;
    margin-top:2rem!important;
  }
  [data-testid="stFileUploaderDropzone"] button{
    min-width:112px!important;
    min-height:40px!important;
    font-size:.82rem!important;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]{
    padding:.78rem .82rem!important;
    border-radius:20px!important;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stMarkdownContainer"]{
    min-height:0;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]){
    border-radius:18px;
    padding:.35rem;
  }
}

/* V153.12 — large tactile Living pass: depth, CTA hierarchy, projects, motion, mobile. */

/* Living canvas: subtle depth without turning into a gradient-heavy website. */
[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(circle at 50% -10%,rgba(151,216,247,.23),transparent 31%),
    radial-gradient(circle at 8% 34%,rgba(204,238,226,.12),transparent 22%),
    radial-gradient(circle at 91% 38%,rgba(247,229,167,.10),transparent 20%),
    linear-gradient(180deg,#fbfdff 0%,#f6fbff 48%,#ffffff 100%)!important;
}
[data-testid="stAppViewContainer"]::before{
  content:"";
  position:fixed;
  inset:0;
  pointer-events:none;
  background-image:
    linear-gradient(rgba(115,168,199,.028) 1px,transparent 1px),
    linear-gradient(90deg,rgba(115,168,199,.028) 1px,transparent 1px);
  background-size:34px 34px;
  mask-image:linear-gradient(to bottom,rgba(0,0,0,.28),transparent 44%);
  -webkit-mask-image:linear-gradient(to bottom,rgba(0,0,0,.28),transparent 44%);
}

/* Brand + dock sit on the same visual system. */
.gsf-living-brand{
  text-shadow:0 1px 0 rgba(255,255,255,.86);
}
.gsf-living-bar{
  border-color:rgba(107,165,198,.18)!important;
  box-shadow:
    0 14px 38px rgba(66,116,148,.12),
    inset 0 1px 0 rgba(255,255,255,.96)!important;
}
.gsf-living-chip{
  position:relative;
  overflow:hidden;
}
.gsf-living-chip::after{
  content:"";
  position:absolute;
  left:22%;
  right:22%;
  bottom:3px;
  height:2px;
  border-radius:999px;
  background:currentColor;
  opacity:0;
  transform:scaleX(.5);
  transition:opacity .18s ease,transform .18s ease;
}
.gsf-living-chip.active::after{
  opacity:.34;
  transform:scaleX(1);
}

/* Upload object: stronger living pulse and cleaner center stack. */
[data-testid="stFileUploader"]{
  filter:
    drop-shadow(0 24px 46px rgba(75,137,175,.12))
    drop-shadow(0 0 28px rgba(105,190,236,.08))!important;
}
[data-testid="stFileUploaderDropzone"]{
  transform:translateZ(0);
}
[data-testid="stFileUploaderDropzone"]::after{
  animation:gsfUploaderAura 2.8s ease-in-out infinite!important;
}
[data-testid="stFileUploaderDropzoneInstructions"]{
  width:70%!important;
}
[data-testid="stFileUploaderDropzoneInstructions"]>div{
  gap:.28rem!important;
}
[data-testid="stFileUploaderDropzone"] button{
  transition:
    transform .18s ease,
    box-shadow .18s ease,
    background .18s ease!important;
}
[data-testid="stFileUploaderDropzone"] button:active{
  transform:scale(.97);
}

/* Three primary action cards behave like one deliberate control group. */
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]){
  min-width:0!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]{
  position:relative!important;
  border-radius:26px!important;
  transition:
    transform .22s ease,
    box-shadow .22s ease,
    border-color .22s ease,
    background .22s ease!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]::after{
  content:"";
  position:absolute;
  left:18px;
  top:18px;
  width:10px;
  height:10px;
  border-radius:50%;
  box-shadow:0 0 0 6px rgba(121,200,241,.08);
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:nth-child(1):has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]::after{
  background:#78c7ee;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:nth-child(2):has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]::after{
  background:#91d7bd;
  box-shadow:0 0 0 6px rgba(145,215,189,.09);
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:nth-child(3):has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]::after{
  background:#efd377;
  box-shadow:0 0 0 6px rgba(239,211,119,.10);
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) h3{
  padding-left:18px!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) p{
  padding-left:18px!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) .stButton>button{
  position:relative;
  overflow:hidden;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) .stButton>button::after{
  content:"→";
  position:absolute;
  right:14px;
  top:50%;
  transform:translateY(-52%);
  opacity:.55;
  transition:transform .18s ease,opacity .18s ease;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) .stButton>button:active{
  transform:scale(.985)!important;
}

/* Recent-project cards: stronger thumbnail/meta relationship. */
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]){
  transition:
    transform .22s ease,
    box-shadow .22s ease,
    border-color .22s ease!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]) [data-testid="stMarkdownContainer"] strong{
  font-weight:790!important;
  color:#273b4c!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]) [data-testid="stCaptionContainer"]{
  color:#8492a1!important;
  font-size:.76rem!important;
}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]) [data-testid="stImage"]{
  border-radius:18px!important;
}

/* Secondary controls lose default web-app heaviness. */
.stButton>button:not([kind="primary"]),
.stDownloadButton>button{
  min-height:40px!important;
  border-radius:999px!important;
  color:#4f6477!important;
  background:rgba(255,255,255,.72)!important;
}
[data-testid="stExpander"]{
  box-shadow:0 9px 24px rgba(71,119,150,.045)!important;
}
[data-testid="stExpander"] summary{
  font-weight:680!important;
  color:#42596d!important;
}
[data-testid="stTabs"] [role="tab"]{
  font-weight:680!important;
}

/* Subtle hover affordance only on precise pointers. */
@media(hover:hover) and (pointer:fine){
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]:hover{
    transform:translateY(-4px);
    border-color:rgba(91,178,225,.24)!important;
    box-shadow:
      inset 0 1px 0 rgba(255,255,255,.96),
      0 20px 44px rgba(77,137,173,.115)!important;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) .stButton>button:hover::after{
    opacity:.88;
    transform:translate(2px,-52%);
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]):hover{
    transform:translateY(-3px);
    border-color:rgba(89,169,214,.18);
    box-shadow:0 17px 34px rgba(73,132,168,.09);
  }
}

/* Desktop composition: clear center axis and deliberate card width. */
@media(min-width:1100px){
  [data-testid="stHorizontalBlock"]:has(.stButton>button[kind="primary"]){
    max-width:960px;
    margin-left:auto!important;
    margin-right:auto!important;
  }
  [data-testid="stHorizontalBlock"]:has([data-testid="stImage"]){
    margin-top:.4rem!important;
  }
}

/* Mobile: tighter cards, stronger bottom dock, no accidental web chrome. */
@media(max-width:760px){
  [data-testid="stAppViewContainer"]{
    background:
      radial-gradient(circle at 50% -4%,rgba(151,216,247,.22),transparent 29%),
      linear-gradient(180deg,#fbfdff 0%,#f7fbff 48%,#ffffff 100%)!important;
  }
  [data-testid="stAppViewContainer"]::before{
    background-size:28px 28px;
    opacity:.7;
  }
  .gsf-living-bar{
    width:calc(100% - 16px)!important;
  }
  .gsf-living-chip.active::after{
    bottom:2px;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]{
    border-radius:19px!important;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) [data-testid="stVerticalBlockBorderWrapper"]::after{
    left:14px;
    top:14px;
    width:8px;
    height:8px;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) h3,
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) p{
    padding-left:14px!important;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has([data-testid="stImage"]){
    padding:.32rem;
    border-radius:17px;
  }
  .stButton>button,
  .stDownloadButton>button{
    min-height:44px!important;
  }
}

@media(prefers-reduced-motion:reduce){
  .gsf-living-chip,
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"],
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"],
  [data-testid="stFileUploaderDropzone"] button{
    transition:none!important;
  }
}

/* V153.13 — native mobile rails, iOS safe areas, stronger desktop card alignment. */

/* Desktop/tablet grids stay balanced. */
@media(min-width:761px){
  [data-testid="stHorizontalBlock"]:has(.stButton>button[kind="primary"]){
    align-items:stretch!important;
  }
  [data-testid="stHorizontalBlock"]:has(.stButton>button[kind="primary"])>[data-testid="stColumn"]{
    flex:1 1 0!important;
    width:0!important;
  }
  [data-testid="stHorizontalBlock"]:has([data-testid="stImage"]){
    align-items:stretch!important;
  }
  [data-testid="stHorizontalBlock"]:has([data-testid="stImage"])>[data-testid="stColumn"]{
    min-width:0!important;
  }
}

/* Mobile cards become swipeable native rails instead of a long stacked page. */
@media(max-width:760px){
  html,body{
    overscroll-behavior-y:none;
  }

  [data-testid="stAppViewContainer"] .main .block-container{
    padding-bottom:calc(7.4rem + env(safe-area-inset-bottom))!important;
  }

  .gsf-living-brand{
    top:calc(13px + env(safe-area-inset-top))!important;
  }

  .gsf-living-bar{
    bottom:calc(8px + env(safe-area-inset-bottom))!important;
  }

  /* Main action rail */
  [data-testid="stHorizontalBlock"]:has(.stButton>button[kind="primary"]){
    display:flex!important;
    flex-wrap:nowrap!important;
    overflow-x:auto!important;
    overflow-y:visible!important;
    scroll-snap-type:x mandatory;
    scroll-padding-left:2px;
    -webkit-overflow-scrolling:touch;
    gap:.72rem!important;
    padding:.2rem .02rem .5rem!important;
    scrollbar-width:none;
  }
  [data-testid="stHorizontalBlock"]:has(.stButton>button[kind="primary"])::-webkit-scrollbar{
    display:none;
  }
  [data-testid="stHorizontalBlock"]:has(.stButton>button[kind="primary"])>[data-testid="stColumn"]{
    flex:0 0 78%!important;
    width:78%!important;
    min-width:78%!important;
    scroll-snap-align:start;
  }
  [data-testid="stHorizontalBlock"]:has(.stButton>button[kind="primary"])>[data-testid="stColumn"]:last-child{
    margin-right:8%;
  }

  /* Recent project/media rail */
  [data-testid="stHorizontalBlock"]:has([data-testid="stImage"]){
    display:flex!important;
    flex-wrap:nowrap!important;
    overflow-x:auto!important;
    overflow-y:visible!important;
    scroll-snap-type:x mandatory;
    scroll-padding-left:2px;
    -webkit-overflow-scrolling:touch;
    gap:.72rem!important;
    padding:.15rem .02rem .55rem!important;
    scrollbar-width:none;
  }
  [data-testid="stHorizontalBlock"]:has([data-testid="stImage"])::-webkit-scrollbar{
    display:none;
  }
  [data-testid="stHorizontalBlock"]:has([data-testid="stImage"])>[data-testid="stColumn"]{
    flex:0 0 72%!important;
    width:72%!important;
    min-width:72%!important;
    scroll-snap-align:start;
  }
  [data-testid="stHorizontalBlock"]:has([data-testid="stImage"])>[data-testid="stColumn"]:last-child{
    margin-right:10%;
  }

  /* Slight visual hint that rails continue horizontally. */
  [data-testid="stHorizontalBlock"]:has(.stButton>button[kind="primary"]),
  [data-testid="stHorizontalBlock"]:has([data-testid="stImage"]){
    mask-image:linear-gradient(
      90deg,
      #000 0,
      #000 calc(100% - 22px),
      rgba(0,0,0,.38) calc(100% - 7px),
      transparent 100%
    );
    -webkit-mask-image:linear-gradient(
      90deg,
      #000 0,
      #000 calc(100% - 22px),
      rgba(0,0,0,.38) calc(100% - 7px),
      transparent 100%
    );
  }

  [data-testid="stHorizontalBlock"]:has(.stButton>button[kind="primary"]):focus-within,
  [data-testid="stHorizontalBlock"]:has([data-testid="stImage"]):focus-within{
    mask-image:none;
    -webkit-mask-image:none;
  }

  /* Keep CTA text readable inside narrow cards. */
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) h3{
    font-size:1.08rem!important;
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:has(.stButton>button[kind="primary"]) p{
    font-size:.88rem!important;
    line-height:1.38!important;
  }

  /* Native press feedback. */
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:active{
    transform:scale(.992);
  }
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{
    transition:transform .12s ease;
  }
}

/* Smaller phones: reveal a little more of the next card as a swipe cue. */
@media(max-width:420px){
  [data-testid="stHorizontalBlock"]:has(.stButton>button[kind="primary"])>[data-testid="stColumn"]{
    flex-basis:82%!important;
    width:82%!important;
    min-width:82%!important;
  }
  [data-testid="stHorizontalBlock"]:has([data-testid="stImage"])>[data-testid="stColumn"]{
    flex-basis:77%!important;
    width:77%!important;
    min-width:77%!important;
  }
}

/* Wider phones/tablets in portrait show more content per swipe. */
@media(min-width:560px) and (max-width:760px){
  [data-testid="stHorizontalBlock"]:has(.stButton>button[kind="primary"])>[data-testid="stColumn"]{
    flex-basis:58%!important;
    width:58%!important;
    min-width:58%!important;
  }
  [data-testid="stHorizontalBlock"]:has([data-testid="stImage"])>[data-testid="stColumn"]{
    flex-basis:52%!important;
    width:52%!important;
    min-width:52%!important;
  }
}

@media(prefers-reduced-motion:reduce){
  [data-testid="stHorizontalBlock"]{
    scroll-behavior:auto!important;
  }
}

/* V153.14 — living states: loading, progress, feedback, disabled, focus. */

/* Progress looks like an active system, not a generic widget. */
[data-testid="stProgress"]>div{
  position:relative;
  overflow:hidden!important;
  background:rgba(130,190,225,.12)!important;
  border:1px solid rgba(112,180,218,.10)!important;
  box-shadow:inset 0 1px 2px rgba(58,108,137,.04)!important;
}
[data-testid="stProgress"]>div::after{
  content:"";
  position:absolute;
  inset:0;
  background:linear-gradient(
    100deg,
    transparent 0 34%,
    rgba(255,255,255,.72) 44%,
    transparent 55% 100%
  );
  transform:translateX(-100%);
  animation:gsfProgressSheen 2.15s ease-in-out infinite;
  pointer-events:none;
}
[data-testid="stProgress"]>div>div{
  background:linear-gradient(90deg,#8fd0f2,#67b9e5)!important;
  box-shadow:0 0 18px rgba(84,174,223,.20)!important;
}

/* Streamlit spinner/status gains a polished presence. */
[data-testid="stSpinner"]{
  color:#4c8fb7!important;
}
[data-testid="stSpinner"] svg{
  filter:drop-shadow(0 2px 6px rgba(74,157,203,.20));
}
[data-testid="stStatusWidget"]{
  border:1px solid rgba(112,172,207,.14)!important;
  background:rgba(255,255,255,.78)!important;
  box-shadow:0 12px 30px rgba(72,123,155,.07)!important;
  backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);
}

/* Alerts and confirmations feel like part of the visual system. */
[data-testid="stAlert"]{
  border:1px solid rgba(111,169,203,.14)!important;
  background:rgba(255,255,255,.76)!important;
  box-shadow:0 10px 26px rgba(71,120,150,.055)!important;
}
[data-testid="stAlert"] svg{
  opacity:.74;
}
[data-testid="stToast"]{
  background:rgba(255,255,255,.88)!important;
  border:1px solid rgba(108,168,202,.16)!important;
  box-shadow:0 14px 38px rgba(66,115,147,.13)!important;
  backdrop-filter:blur(18px);
  -webkit-backdrop-filter:blur(18px);
}

/* Disabled states stay elegant and readable. */
.stButton>button:disabled,
.stDownloadButton>button:disabled{
  opacity:.50!important;
  filter:saturate(.65)!important;
  transform:none!important;
  box-shadow:none!important;
}
[data-baseweb="select"] [aria-disabled="true"],
[data-testid="stTextInput"] input:disabled,
[data-testid="stTextArea"] textarea:disabled{
  opacity:.62!important;
}

/* Unified keyboard focus is visible without harsh browser rings. */
.stButton>button:focus-visible,
.stDownloadButton>button:focus-visible,
[data-testid="stFileUploaderDropzone"] button:focus-visible,
[data-testid="stTabs"] [role="tab"]:focus-visible,
.gsf-living-chip:focus-visible{
  outline:none!important;
  box-shadow:
    0 0 0 3px rgba(103,190,237,.18),
    0 10px 26px rgba(71,144,184,.10)!important;
}

/* Active Living navigation has a very subtle breathing state. */
.gsf-living-chip.active{
  animation:gsfActiveChip 3.2s ease-in-out infinite;
}

/* Uploader communicates readiness even before interaction. */
[data-testid="stFileUploaderDropzone"]{
  background-size:100% 100%!important;
}
[data-testid="stFileUploaderDropzone"] svg{
  animation:gsfUploadIconFloat 2.8s ease-in-out infinite;
}

/* Native press response across core visual controls. */
.stButton>button:active,
.stDownloadButton>button:active,
.gsf-living-chip:active{
  transform:scale(.975)!important;
  transition-duration:.07s!important;
}

/* Smooth visual entry when Streamlit reveals later sections. */
[data-testid="stExpander"],
[data-testid="stAlert"],
[data-testid="stStatusWidget"],
[data-testid="stImage"],
[data-testid="stVideo"]{
  animation:gsfReveal .34s ease both;
}

/* Motion definitions. */
@keyframes gsfProgressSheen{
  0%,34%{transform:translateX(-110%)}
  68%,100%{transform:translateX(110%)}
}
@keyframes gsfActiveChip{
  0%,100%{box-shadow:inset 0 0 0 1px rgba(105,186,229,.14),0 5px 14px rgba(78,155,198,.07)}
  50%{box-shadow:inset 0 0 0 1px rgba(105,186,229,.20),0 6px 18px rgba(78,155,198,.12)}
}
@keyframes gsfUploadIconFloat{
  0%,100%{transform:translateY(0)}
  50%{transform:translateY(-3px)}
}
@keyframes gsfReveal{
  from{opacity:.01;transform:translateY(4px)}
  to{opacity:1;transform:none}
}

/* Mobile feedback remains lighter to preserve speed and visual calm. */
@media(max-width:760px){
  [data-testid="stProgress"]>div::after{
    animation-duration:2.5s;
  }
  .gsf-living-chip.active{
    animation-duration:3.8s;
  }
  [data-testid="stExpander"],
  [data-testid="stAlert"],
  [data-testid="stStatusWidget"],
  [data-testid="stImage"],
  [data-testid="stVideo"]{
    animation-duration:.25s;
  }
}

@media(prefers-reduced-motion:reduce){
  [data-testid="stProgress"]>div::after,
  .gsf-living-chip.active,
  [data-testid="stFileUploaderDropzone"] svg,
  [data-testid="stExpander"],
  [data-testid="stAlert"],
  [data-testid="stStatusWidget"],
  [data-testid="stImage"],
  [data-testid="stVideo"]{
    animation:none!important;
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
  <div class="gsf-living-chip active">
    <span class="gsf-nav-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24"><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5"/><path d="M9.5 20v-5h5v5"/></svg>
    </span>
    <span class="gsf-nav-label">Home</span>
  </div>
  <div class="gsf-living-chip">
    <span class="gsf-nav-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24"><path d="m12 3 1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6Z"/><path d="m18.5 15 .8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8Z"/></svg>
    </span>
    <span class="gsf-nav-label">AI</span>
  </div>
  <div class="gsf-living-chip">
    <span class="gsf-nav-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="14" rx="3"/><path d="M8 9h8M8 13h5"/></svg>
    </span>
    <span class="gsf-nav-label">Editor</span>
  </div>
  <div class="gsf-living-chip">
    <span class="gsf-nav-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24"><rect x="4" y="4" width="6" height="6" rx="1.5"/><rect x="14" y="4" width="6" height="6" rx="1.5"/><rect x="4" y="14" width="6" height="6" rx="1.5"/><rect x="14" y="14" width="6" height="6" rx="1.5"/></svg>
    </span>
    <span class="gsf-nav-label">Creator Hub</span>
  </div>
  <div class="gsf-living-chip">
    <span class="gsf-nav-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24"><circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="m8.3 10.8 7.4-4.4M8.3 13.2l7.4 4.4"/></svg>
    </span>
    <span class="gsf-nav-label">Social</span>
  </div>
</nav>
"""

def render_shell() -> None:
    """Render presentation only; no session-state or pipeline mutations."""
    st.markdown(LIVING_CSS, unsafe_allow_html=True)
    st.markdown(SHELL_HTML, unsafe_allow_html=True)
