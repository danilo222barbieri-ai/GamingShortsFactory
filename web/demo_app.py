import streamlit as st

st.set_page_config(
    page_title="Gaming Shorts Factory · UI Demo",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "demo_engine" not in st.session_state:
    st.session_state.demo_engine = "🚀 Automatico"
if "demo_duration" not in st.session_state:
    st.session_state.demo_duration = "30s"
if "demo_social" not in st.session_state:
    st.session_state.demo_social = "YouTube"

st.markdown(
    """
    <style>
    :root{
        --ink:#17324A;
        --muted:#71879A;
        --line:#D9E7F1;
        --soft:#F7FBFE;
        --soft2:#EEF7FD;
        --blue:#4D9ED1;
        --shadow:0 12px 34px rgba(34,82,116,.08);
    }
    .stApp{
        background:
          radial-gradient(circle at 12% 0%, rgba(214,239,255,.72), transparent 28rem),
          linear-gradient(180deg,#FBFDFF 0%,#FFFFFF 45%,#F8FBFD 100%);
        color:var(--ink);
    }
    .block-container{
        max-width:1180px;
        padding-top:1.5rem;
        padding-bottom:5rem;
    }
    h1,h2,h3{letter-spacing:-.03em}
    .demo-top{
        padding:22px 24px;
        border:1px solid var(--line);
        border-radius:26px;
        background:rgba(255,255,255,.92);
        box-shadow:var(--shadow);
        margin-bottom:18px;
    }
    .demo-kicker{
        display:inline-flex;
        align-items:center;
        gap:7px;
        padding:6px 10px;
        border-radius:999px;
        border:1px solid #BFDFF0;
        background:#EFF9FE;
        color:#2E6F98;
        font-size:12px;
        font-weight:850;
        letter-spacing:.03em;
        text-transform:uppercase;
    }
    .demo-title{
        margin:12px 0 5px;
        font-size:clamp(2rem,4vw,3.45rem);
        line-height:.98;
        font-weight:900;
        color:#153149;
    }
    .demo-sub{
        color:var(--muted);
        font-size:15px;
        max-width:820px;
    }
    .mock-card{
        border:1px solid var(--line);
        border-radius:24px;
        background:rgba(255,255,255,.96);
        box-shadow:var(--shadow);
        padding:18px;
        margin:10px 0 16px;
    }
    .fake-video{
        aspect-ratio:16/9;
        width:100%;
        border-radius:20px;
        border:1px solid #D2E2ED;
        display:flex;
        align-items:center;
        justify-content:center;
        flex-direction:column;
        gap:7px;
        color:#DCEFFF;
        background:
          radial-gradient(circle at 68% 30%,rgba(48,167,228,.35),transparent 28%),
          radial-gradient(circle at 28% 68%,rgba(112,84,229,.28),transparent 26%),
          linear-gradient(145deg,#132A3D 0%,#1E4560 52%,#0E2232 100%);
        overflow:hidden;
    }
    .fake-video strong{font-size:20px;color:white}
    .fake-video span{font-size:12px;color:#CBE3F3}
    .fake-short{
        aspect-ratio:9/16;
        max-height:450px;
        width:100%;
        border-radius:20px;
        border:1px solid #D2E2ED;
        display:flex;
        align-items:center;
        justify-content:center;
        flex-direction:column;
        gap:7px;
        background:
          radial-gradient(circle at 30% 18%,rgba(99,176,255,.35),transparent 28%),
          radial-gradient(circle at 70% 72%,rgba(160,92,255,.25),transparent 28%),
          linear-gradient(180deg,#12293D,#183D56 60%,#0B2130);
        color:white;
    }
    .fake-short span{color:#CBE3F3;font-size:12px}
    .section-label{
        font-size:12px;
        text-transform:uppercase;
        letter-spacing:.08em;
        font-weight:850;
        color:#7891A5;
        margin:6px 0 4px;
    }
    .section-title{
        font-size:1.35rem;
        font-weight:900;
        color:#17324A;
        margin-bottom:5px;
    }
    .section-note{
        font-size:13px;
        color:#7890A2;
        margin-bottom:12px;
    }
    .ad-demo{
        position:relative;
        min-height:104px;
        width:100%;
        box-sizing:border-box;
        margin:20px auto;
        border:1.5px dashed #A9CDE4;
        border-radius:20px;
        display:flex;
        align-items:center;
        justify-content:center;
        text-align:center;
        background:
          radial-gradient(circle at 15% 12%,rgba(218,239,255,.82),transparent 35%),
          linear-gradient(180deg,#FFFFFF,#F7FBFE);
        color:#667F93;
        box-shadow:0 9px 26px rgba(31,78,112,.05);
    }
    .ad-demo b{
        display:block;
        color:#456B86;
        font-size:15px;
        margin-bottom:3px;
    }
    .ad-demo small{
        font-size:11px;
        color:#8AA0B2;
    }
    .ad-tag{
        position:absolute;
        left:13px;
        top:9px;
        font-size:9px;
        font-weight:900;
        letter-spacing:.08em;
        text-transform:uppercase;
        color:#7991A4;
    }
    .ad-num{
        position:absolute;
        right:12px;
        top:8px;
        padding:4px 7px;
        border-radius:999px;
        background:#EDF6FC;
        border:1px solid #D7E8F3;
        font-size:9px;
        font-weight:900;
        color:#678198;
    }
    .moment{
        border:1px solid var(--line);
        border-radius:20px;
        padding:10px;
        background:#FFF;
    }
    .moment .thumb{
        aspect-ratio:16/9;
        border-radius:15px;
        background:
          radial-gradient(circle at 25% 25%,rgba(82,183,243,.35),transparent 24%),
          linear-gradient(145deg,#17344A,#0C2231);
        display:flex;
        align-items:center;
        justify-content:center;
        color:white;
        font-weight:850;
    }
    .pill{
        display:inline-flex;
        padding:5px 9px;
        border-radius:999px;
        background:#EEF7FD;
        border:1px solid #D4E7F3;
        color:#53758D;
        font-size:11px;
        font-weight:800;
        margin-top:9px;
    }
    .timeline{
        height:56px;
        border-radius:14px;
        border:1px solid #D5E4EE;
        background:
          linear-gradient(90deg,transparent 0 8%,rgba(93,160,202,.18) 8% 11%,transparent 11% 20%,
          rgba(93,160,202,.18) 20% 22%,transparent 22% 36%,rgba(93,160,202,.18) 36% 40%,
          transparent 40% 62%,rgba(93,160,202,.18) 62% 67%,transparent 67% 100%),
          linear-gradient(180deg,#F9FCFE,#EFF6FA);
        position:relative;
        overflow:hidden;
    }
    .timeline:before{
        content:"";
        position:absolute;
        left:23%;
        right:31%;
        top:8px;
        bottom:8px;
        border:2px solid #62A9D4;
        border-radius:10px;
        background:rgba(98,169,212,.08);
    }
    .footer-demo{
        text-align:center;
        color:#8095A6;
        font-size:12px;
        padding:26px 0 6px;
    }
    [data-testid="stButton"] button,
    [data-testid="stDownloadButton"] button{
        border-radius:14px !important;
        font-weight:800 !important;
    }
    [data-testid="stRadio"] > div{
        gap:.45rem;
    }
    @media(max-width:750px){
        .block-container{padding-left:.8rem;padding-right:.8rem}
        .demo-top{padding:18px 16px;border-radius:21px}
        .mock-card{padding:13px;border-radius:19px}
        .ad-demo{min-height:112px;border-radius:17px}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def ad_slot(n, label):
    st.markdown(
        f'''
        <div class="ad-demo">
          <span class="ad-tag">Pubblicità</span>
          <span class="ad-num">SLOT {n}</span>
          <div><b>{label}</b><small>Anteprima responsive · nessun annuncio reale</small></div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="demo-top">
      <span class="demo-kicker">🧪 UI DEMO · V105.6</span>
      <div class="demo-title">Gaming Shorts Factory</div>
      <div class="demo-sub">
        Tutto è già aperto: nessun upload, nessuna attesa AI, nessun rendering.
        Questa pagina serve solo per sistemare grafica, spazi, pubblicità, editor e pubblicazione social.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2 = st.columns([1,1])
with c1:
    if st.button("↻ RESET DEMO", use_container_width=True):
        for k in ("demo_engine","demo_duration","demo_social"):
            st.session_state.pop(k, None)
        st.rerun()
with c2:
    st.info("Produzione separata: questa demo non pubblica, non renderizza e non modifica video reali.", icon="🔒")

st.markdown('<div class="section-label">Video caricato</div>', unsafe_allow_html=True)
st.markdown('<div class="fake-video"><strong>Gameplay demo già caricato</strong><span>1920×1080 · 00:02:14 · audio presente</span></div>', unsafe_allow_html=True)

ad_slot(1, "Banner dopo il caricamento")

st.markdown('<div class="section-label">Crea con AI</div><div class="section-title">Scegli il motore</div><div class="section-note">Tutti gli stati sono disponibili senza analisi reale.</div>', unsafe_allow_html=True)
engines = ["🚀 Automatico","✨ Momento migliore","⚡ Più azione","😮 Reazioni","✋ Manuale"]
st.radio("Motore", engines, horizontal=True, key="demo_engine", label_visibility="collapsed")

ad_slot(2, "Banner tra motore e durata")

st.markdown('<div style="height:10px"></div><div class="section-title">Scegli la durata</div>', unsafe_allow_html=True)
st.radio("Durata", ["15s","30s"], horizontal=True, key="demo_duration", label_visibility="collapsed")

st.markdown('<div class="section-label">Classifica AI</div><div class="section-title">3 momenti trovati</div>', unsafe_allow_html=True)
cols = st.columns(3)
for i, (title, score) in enumerate([("Momento 1","96%"),("Momento 2","91%"),("Momento 3","87%")]):
    with cols[i]:
        st.markdown(f'<div class="moment"><div class="thumb">{title}</div><span class="pill">Score AI {score}</span></div>', unsafe_allow_html=True)
        st.button("USA QUESTA", key=f"moment_{i}", use_container_width=True)

ad_slot(3, "Banner dopo CREA CON AI")

st.markdown('<div class="section-label">Editor</div><div class="section-title">Scena selezionata</div>', unsafe_allow_html=True)
ec1, ec2 = st.columns([1.55,1])
with ec1:
    st.markdown('<div class="fake-video"><strong>Anteprima Editor 16:9</strong><span>Scena demo · IN 00:42 · OUT 01:12</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="height:10px"></div><div class="timeline"></div>', unsafe_allow_html=True)
    a,b = st.columns(2)
    with a:
        st.number_input("IN", value=42.0, step=0.5)
    with b:
        st.number_input("OUT", value=72.0, step=0.5)
with ec2:
    st.markdown('<div class="mock-card"><div class="section-title">Strumenti</div>', unsafe_allow_html=True)
    st.slider("Zoom", 100, 180, 116)
    st.slider("Volume", 0, 200, 100)
    st.slider("Luminosità", -50, 50, 0)
    st.slider("Contrasto", -50, 50, 0)
    st.select_slider("Velocità", options=[0.5,0.75,1.0,1.25,1.5,2.0], value=1.0)
    st.radio("Sottotitoli", ["Nessuno","Automatici","Manuali"], horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

ad_slot(4, "Banner prima dello Short finale")

st.markdown('<div class="section-label">Risultato</div><div class="section-title">Short finale già pronto</div>', unsafe_allow_html=True)
fc1, fc2 = st.columns([.72,1.28])
with fc1:
    st.markdown('<div class="fake-short"><strong>SHORT 9:16</strong><span>1080×1920 · demo</span></div>', unsafe_allow_html=True)
with fc2:
    st.markdown('<div class="mock-card"><div class="section-title">Output finale</div><div class="section-note">Simulazione pronta per controllare l’ultima parte della pagina.</div>', unsafe_allow_html=True)
    st.button("CREA SHORT FINALE", type="primary", use_container_width=True)
    st.button("SCARICA", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

ad_slot(5, "Banner dopo CREA SHORT FINALE")

st.markdown('<div class="section-label">Pubblicazione diretta</div><div class="section-title">Social già aperti</div>', unsafe_allow_html=True)
socials = ["YouTube","TikTok","Instagram"]
st.radio("Social", socials, horizontal=True, key="demo_social", label_visibility="collapsed")

with st.container(border=True):
    st.markdown(f"### Dettagli {st.session_state.demo_social}")
    st.caption("Simulazione account collegato · nessuna pubblicazione reale")
    st.text_input("Gioco", placeholder="Es. Halo Infinite")
    st.text_input("Titolo", placeholder="Es. Halo Infinite · clutch all’ultimo secondo")
    st.text_area("Descrizione", placeholder="Es. Il momento decisivo della partita, pronto per lo Short.", height=100)
    st.text_input("Hashtag", placeholder="Es. #HaloInfinite #Gaming #Shorts")
    st.button("PUBBLICA", type="primary", use_container_width=True)

ad_slot(6, "Banner finale / footer")

st.markdown('<div class="footer-demo">Gaming Shorts Factory · UI DEMO separata · Nessuna azione reale viene eseguita</div>', unsafe_allow_html=True)
