import streamlit as st
import subprocess
import os
import json
import tempfile
import re
import math
import time
import hashlib
import shutil
import threading
import socket
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import quote
import streamlit.components.v1 as components
from faster_whisper import WhisperModel

try:
    import numpy as np
except Exception:
    np = None



st.markdown("""
<style>
/* UI creazione più compatta */
div[data-testid="stRadio"] > div { gap: .35rem !important; }
div[data-testid="stCheckbox"] { margin-top: -.20rem !important; margin-bottom: -.20rem !important; }
div[data-testid="stSelectbox"], div[data-testid="stTextInput"] { margin-bottom: .25rem !important; }
.gsf-section-title { margin-top: .65rem !important; margin-bottom: .35rem !important; }


/* ===== LAYOUT UNICO E PULITO ===== */
.block-container {
    max-width: 1400px !important;
    width: 94vw !important;
    padding-top: 1.4rem !important;
    padding-bottom: 4rem !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ===== V10 CLEAN UI — solo interfaccia ===== */
.block-container{
  max-width:1320px!important;width:94vw!important;
  padding-top:.8rem!important;padding-bottom:2.5rem!important;
}
h1{font-size:2.15rem!important;letter-spacing:-.035em!important}
h2{font-size:1.55rem!important}
h3{font-size:1.25rem!important}
h4{font-size:1.08rem!important;margin-top:.45rem!important;margin-bottom:.45rem!important}
h5{font-size:.94rem!important;margin:.2rem 0 .45rem!important}
[data-testid="stCaptionContainer"]{font-size:.78rem!important;line-height:1.25!important}
[data-testid="stVerticalBlock"]{gap:.55rem!important}
[data-testid="column"] [data-testid="stVerticalBlock"]{gap:.38rem!important}

/* Controls più compatti */
.stButton>button,.stDownloadButton>button{
 min-height:2.65rem!important;padding:.35rem .9rem!important;
 box-shadow:none!important;border-radius:14px!important
}
.stButton>button[kind="primary"]{min-height:3.15rem!important;font-size:1rem!important}
[data-baseweb="select"]>div,[data-baseweb="input"]>div,.stTextInput input{
 border-radius:13px!important;min-height:2.55rem!important
}
[data-testid="stSlider"]{padding-top:0!important;padding-bottom:.1rem!important}
[data-testid="stTextArea"] textarea{border-radius:15px!important;min-height:130px!important}
[data-testid="stAlert"]{border-radius:14px!important;padding:.55rem .75rem!important}
[data-testid="stFileUploader"],[data-testid="stExpander"]{border-radius:18px!important;box-shadow:none!important}

/* Radio motori = tab pulite */
[data-testid="stRadio"]>div{gap:.4rem!important}
[data-testid="stRadio"] label{
 border-radius:13px!important;padding:.48rem .72rem!important;
 box-shadow:none!important
}

/* Le vecchie decorazioni diventano più discrete */
.soft-card{border-radius:18px!important;padding:14px 16px!important;margin:9px 0!important;box-shadow:none!important}
.gsf-section-title{font-size:1.2rem!important;margin:.4rem 0 .2rem!important}
.gsf-section-sub{font-size:.84rem!important;margin-bottom:.45rem!important}
.help-cloud{margin:.25rem 0!important}

/* Desktop: workspace più denso; mobile torna naturalmente in colonna */
@media (min-width: 900px){
  [data-testid="stHorizontalBlock"]{align-items:flex-start}
}
</style>
""", unsafe_allow_html=True)


GSF_PREVIEW_DIR = Path(tempfile.gettempdir()) / "gaming_shorts_factory_preview"
GSF_PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

def _gsf_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

class _GSFQuietHandler(SimpleHTTPRequestHandler):
    """Quiet HTTP handler with proper byte-range support for HTML5 video seeking."""
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        pass

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_head(self):
        path = self.translate_path(self.path)

        # Keep normal SimpleHTTPRequestHandler behaviour for folders.
        if os.path.isdir(path):
            return super().send_head()

        ctype = self.guess_type(path)
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        try:
            fs = os.fstat(f.fileno())
            size = fs.st_size
            range_header = self.headers.get("Range")
            self._gsf_range = None

            if range_header:
                m = re.match(r"bytes=(\d*)-(\d*)$", range_header.strip())
                if not m:
                    f.close()
                    self.send_error(416, "Requested Range Not Satisfiable")
                    return None

                a, b = m.groups()

                # bytes=-N  -> final N bytes
                if a == "":
                    suffix = int(b or 0)
                    if suffix <= 0:
                        f.close()
                        self.send_error(416, "Requested Range Not Satisfiable")
                        return None
                    start = max(0, size - suffix)
                    end = size - 1
                else:
                    start = int(a)
                    end = int(b) if b else size - 1

                if start >= size or start < 0 or end < start:
                    f.close()
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return None

                end = min(end, size - 1)
                length = end - start + 1
                self._gsf_range = (start, end)

                self.send_response(206)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.send_header("Content-Length", str(length))
                self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
                self.end_headers()
                return f

            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(size))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f

        except Exception:
            f.close()
            raise

    def copyfile(self, source, outputfile):
        byte_range = getattr(self, "_gsf_range", None)
        if not byte_range:
            return super().copyfile(source, outputfile)

        start, end = byte_range
        source.seek(start)
        remaining = end - start + 1
        chunk_size = 256 * 1024

        while remaining > 0:
            chunk = source.read(min(chunk_size, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)

@st.cache_resource
def _gsf_start_preview_server():
    port = _gsf_free_port()
    def handler(*args, **kwargs):
        return _GSFQuietHandler(*args, directory=str(GSF_PREVIEW_DIR), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return port

GSF_PREVIEW_PORT = _gsf_start_preview_server()

def _gsf_probe_display_size(path):
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None, None, None, "ffprobe non trovato nel PATH"
    try:
        import json
        r = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height:stream_tags=rotate:stream_side_data=rotation",
             "-of", "json", str(path)],
            capture_output=True, text=True, timeout=15
        )
        if r.returncode != 0:
            return None, None, None, (r.stderr or "errore ffprobe").strip()
        streams=(json.loads(r.stdout or "{}").get("streams") or [])
        if not streams:
            return None,None,None,"nessuna traccia video"
        s=streams[0]
        rw,rh=int(s.get("width") or 0),int(s.get("height") or 0)
        rot=0
        try: rot=int(float((s.get("tags") or {}).get("rotate",0)))
        except Exception: pass
        for sd in s.get("side_data_list") or []:
            if "rotation" in sd:
                try: rot=int(float(sd["rotation"]))
                except Exception: pass
        if rw<=0 or rh<=0:
            return None,None,None,f"dimensioni non valide: {rw}x{rh}"
        if rot % 360 in (90,270):
            rw,rh=rh,rw
        return rw,rh,rot,None
    except Exception as e:
        return None,None,None,str(e)


def _gsf_serve_path(source_path, key):
    source_path = Path(source_path)
    ext = source_path.suffix or ".mp4"
    safe_key = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(key))
    served_name = f"{safe_key}{ext}"
    served_path = GSF_PREVIEW_DIR / served_name
    if (not served_path.exists()
        or served_path.stat().st_size != source_path.stat().st_size
        or served_path.stat().st_mtime < source_path.stat().st_mtime):
        shutil.copy2(source_path, served_path)
    return served_name, served_path

def _gsf_bytes_to_preview(data, key, suffix=".mp4"):
    digest = hashlib.md5(data[:1024*1024]).hexdigest()[:10]
    safe_key = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(key))
    path = GSF_PREVIEW_DIR / f"{safe_key}_{digest}{suffix}"
    if not path.exists() or path.stat().st_size != len(data):
        with open(path, "wb") as f:
            f.write(data)
    return path

def render_gsf_player(source_path, key, *, scene=False, start_seconds=None):
    """Motore unico HTML5: sorgente, scena/editor e risultati."""
    source_path = Path(source_path)
    if not source_path.exists():
        st.warning("Anteprima video non disponibile.")
        return None

    pw, ph, rotation, err = _gsf_probe_display_size(source_path)
    if err:
        st.warning(f"Anteprima non leggibile: {err}")
        return None

    vertical = ph > pw

    # Profili INDIPENDENTI: cambiare un player non modifica gli altri.
    key_s = str(key)

    if scene:
        # SCENA / EDITOR
        target_width = 290 if vertical else 650
        max_vw = "290px" if vertical else "650px"
        cap = 620 if vertical else 410

    elif (
        key_s.startswith("result_v2_")
        or key_s.startswith("ai_preview_")
        or key_s.startswith("batch_short_")
    ):
        # CLIP / 3 RISULTATI
        target_width = 250 if vertical else 560
        max_vw = "250px" if vertical else "560px"
        cap = 560 if vertical else 380

    elif key_s in ("editor_result", "final_short"):
        # RISULTATO FINALE
        target_width = 260 if vertical else 580
        max_vw = "300px" if vertical else "720px"
        cap = 680 if vertical else 470

    else:
        # PRINCIPALE / VIDEO ORIGINALE
        target_width = 340 if vertical else 900
        max_vw = "340px" if vertical else "900px"
        cap = 760 if vertical else 600

    served_name, _ = _gsf_serve_path(source_path, key)
    url = f"http://127.0.0.1:{GSF_PREVIEW_PORT}/{quote(served_name)}"
    if start_seconds is not None:
        try:
            url += f"#t={max(0.0,float(start_seconds)):.3f}"
        except Exception:
            pass

    target_height = round(target_width * ph / pw)
    html_player=f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    html,body{{margin:0;padding:0;background:transparent;overflow:hidden}}
    .wrap{{width:100%;display:flex;justify-content:center;align-items:flex-start}}
    video{{display:block;width:{target_width}px;max-width:{max_vw};height:auto;
    object-fit:contain;border-radius:18px;background:#000;
    box-shadow:0 14px 34px rgba(16,40,61,.14)}}
    </style></head><body><div class="wrap">
    <video controls preload="metadata" playsinline><source src="{url}"></video>
    </div></body></html>"""
    components.html(html_player,height=min(target_height+30,cap),scrolling=False)
    return {"vertical":vertical,"width":pw,"height":ph,"rotation":rotation}

st.set_page_config(
    page_title="Gaming Shorts Factory",
    page_icon="🎮",
    layout="wide"
)
st.markdown("""
<style>
.block-container {max-width: 1500px !important; padding-left: 1.2rem !important; padding-right: 1.2rem !important;}
</style>
""", unsafe_allow_html=True)




st.markdown("""
<style>
:root {
  --bg:#f4f9ff;
  --surface:#ffffff;
  --text:#10233f;
  --muted:#60758f;
  --blue:#21a8ff;
  --blue2:#68c9ff;
  --cyan:#53e0ea;
  --yellow:#ffd84d;
  --red:#ff6673;
  --green:#5ed6a0;
  --purple:#9d82ff;
}
.stApp {
  background:
    radial-gradient(circle at 5% 8%, rgba(33,168,255,.18) 0 110px, transparent 112px),
    radial-gradient(circle at 95% 16%, rgba(83,224,234,.20) 0 145px, transparent 147px),
    radial-gradient(circle at 86% 90%, rgba(157,130,255,.12) 0 180px, transparent 182px),
    var(--bg);
  color:var(--text);
}

h1,h2,h3,p,label { color:var(--text) !important; }
[data-testid="stCaptionContainer"] { color:var(--muted) !important; }

/* Hero */
.hero-title {
  text-align:center;
  color:var(--text);
  font-size:clamp(2.6rem,7vw,5rem);
  font-weight:950;
  letter-spacing:-.065em;
  line-height:.91;
}
.hero-sub {
  text-align:center;
  color:var(--muted);
  font-size:1.08rem;
  margin:17px 0 4px;
}
.ai-orb {
  width:68px;height:68px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  margin:0 auto 20px;
  background:linear-gradient(145deg,var(--blue),var(--blue2));
  color:white;font-weight:950;font-size:1.05rem;
  box-shadow:0 15px 35px rgba(33,168,255,.28);
}

/* Circular workflow */
.flow {
  display:flex;justify-content:center;align-items:center;
  gap:12px;flex-wrap:wrap;margin:30px 0 34px;
}
.orb {
  width:92px;height:92px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  text-align:center;font-size:.73rem;font-weight:900;line-height:1.08;
  color:white;
  box-shadow:0 13px 28px rgba(39,80,120,.16);
}
.orb-blue {background:linear-gradient(145deg,#159eff,#67caff);}
.orb-cyan {background:linear-gradient(145deg,#21c8dc,#76e9ed);}
.orb-yellow {background:linear-gradient(145deg,#ffc928,#ffe87b);color:#574500;}
.orb-red {background:linear-gradient(145deg,#ff596b,#ff8a94);}
.flow-arrow {font-size:1.45rem;color:#9db1c8;font-weight:900;}

/* Surfaces */
[data-testid="stFileUploader"], [data-testid="stExpander"] {
  background:rgba(255,255,255,.92);
  border:1px solid #dceaf7;
  border-radius:32px;
  box-shadow:0 16px 45px rgba(44,89,130,.09);
}
[data-testid="stFileUploader"] {padding:14px 18px 8px;}
[data-testid="stFileUploaderDropzone"] {
  background:#f8fcff !important;
  border:2px dashed #9bd8ff !important;
  border-radius:25px !important;
}
.soft-card {
  background:white;
  border:1px solid #dceaf7;
  border-radius:32px;
  padding:22px 25px;
  margin:16px 0;
  box-shadow:0 16px 45px rgba(44,89,130,.08);
}
.mini-label {
  color:#159eff !important;
  text-transform:uppercase;
  letter-spacing:.16em;
  font-size:.68rem;
  font-weight:950;
}

/* Pills / controls */
.stButton>button,.stDownloadButton>button {
  border-radius:999px !important;
  min-height:3.3rem;
  font-weight:900 !important;
  border:1px solid #bde4ff !important;
  background:white !important;
  color:#117ec5 !important;
  box-shadow:0 9px 22px rgba(33,168,255,.11);
}
.stButton>button[kind="primary"] {
  min-height:4rem;
  background:linear-gradient(90deg,#159eff,#53c8ff) !important;
  color:white !important;
  border:0 !important;
  font-size:1.08rem;
}
[data-baseweb="select"]>div,
[data-baseweb="input"]>div,
.stTextInput input {
  background:white !important;
  border-radius:999px !important;
  color:var(--text) !important;
}
[data-testid="stRadio"] label {
  background:white;
  border:1px solid #dceaf7;
  border-radius:999px;
  padding:.55rem .8rem;
  color:var(--text) !important;
}
[data-testid="stAlert"] {
  border-radius:24px !important;
}
#MainMenu,footer {visibility:hidden;}

/* Contextual help clouds */
.help-cloud{
  position:relative;
  background:#eaf7ff;
  border:1px solid #bfe7ff;
  border-radius:28px;
  padding:15px 18px;
  margin:10px 0 18px;
  color:#315b78;
  box-shadow:0 10px 26px rgba(33,168,255,.08);
  font-size:.91rem;
  line-height:1.45;
}
.help-cloud:after{
  content:"";
  position:absolute;
  left:28px;
  bottom:-9px;
  width:18px;height:18px;
  background:#eaf7ff;
  border-right:1px solid #bfe7ff;
  border-bottom:1px solid #bfe7ff;
  transform:rotate(45deg);
}
.help-cloud b{color:#117ec5}

/* ===== GSF V3 — CHAT-LIKE AZZURRO ===== */
:root{
  --gsf-blue:#27aef3;
  --gsf-blue2:#79d2ff;
  --gsf-soft:#eef9ff;
  --gsf-line:#d9effb;
  --gsf-ink:#10283d;
  --gsf-muted:#6d8497;
}
html,body,[class*="css"]{
  font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
.stApp{
  background:linear-gradient(180deg,#f8fdff 0%,#ffffff 38%,#f5fbff 100%);
}

[data-testid="stSidebar"]{display:none;}
[data-testid="collapsedControl"]{display:none;}
.stButton>button,
.stDownloadButton>button{
  border-radius:999px!important;
}
[data-testid="stFileUploader"]{
  background:#fff;
  border:1px solid var(--gsf-line);
  border-radius:34px!important;
  padding:12px;
  box-shadow:0 14px 36px rgba(39,174,243,.07);
}
[data-testid="stExpander"]{
  background:#fff;
  border:1px solid var(--gsf-line)!important;
  border-radius:28px!important;
  overflow:hidden;
}
[data-testid="stSegmentedControl"] button{
  border-radius:999px!important;
}
.gsf-brand{
  display:flex;align-items:center;gap:12px;
  padding:8px 6px 18px;
}
.gsf-logo{
  width:42px;height:42px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  background:linear-gradient(145deg,var(--gsf-blue),var(--gsf-blue2));
  color:#fff;font-size:19px;font-weight:950;
  box-shadow:0 9px 24px rgba(39,174,243,.22);
}
.gsf-brand-name{font-weight:950;color:var(--gsf-ink);letter-spacing:-.03em}
.gsf-brand-sub{font-size:.72rem;color:var(--gsf-muted);margin-top:1px}
.gsf-hero{
  text-align:center;
  padding:26px 12px 14px;
}
.gsf-orb{
  width:66px;height:66px;margin:0 auto 16px;border-radius:50%;
  background:linear-gradient(145deg,#23adf3,#8bdcff);
  display:flex;align-items:center;justify-content:center;
  color:white;font-size:29px;
  box-shadow:0 15px 35px rgba(39,174,243,.20);
}
.gsf-hero h1{
  color:var(--gsf-ink);font-size:2.05rem;letter-spacing:-.055em;
  margin:0;font-weight:950;
}
.gsf-hero p{color:var(--gsf-muted);margin:.55rem 0 0;font-size:.96rem}
.gsf-step{
  display:inline-flex;align-items:center;gap:8px;
  background:#eaf8ff;border:1px solid #ccecff;
  color:#2879a8;border-radius:999px;padding:7px 12px;
  font-size:.78rem;font-weight:850;margin:10px 0 8px;
}
.gsf-command{
  background:white;border:1px solid var(--gsf-line);
  border-radius:30px;padding:15px 18px;margin:12px 0 18px;
  box-shadow:0 12px 34px rgba(39,174,243,.07);
  color:var(--gsf-muted);
}
.gsf-section-title{
  color:var(--gsf-ink);font-size:1.15rem;font-weight:950;
  letter-spacing:-.025em;margin:18px 0 5px;
}
.gsf-section-sub{color:var(--gsf-muted);font-size:.87rem;margin-bottom:12px}


/* ===== RESULTS V2 ===== */
.result-wrap{
  background:#ffffff;
  border:1px solid #d9effb;
  border-radius:32px;
  padding:18px;
  margin:12px 0 18px;
  box-shadow:0 12px 34px rgba(39,174,243,.07);
}
.result-badge{
  display:inline-flex;align-items:center;
  padding:6px 11px;border-radius:999px;
  background:#eaf8ff;color:#2184ba;
  font-size:.75rem;font-weight:900;
}
.result-title{
  color:#10283d;font-size:1.05rem;font-weight:950;
  margin-top:10px;letter-spacing:-.02em;
}
.result-time{color:#6d8497;font-size:.83rem;margin-top:3px}
.results-head{
  text-align:center;margin:26px 0 12px;
}
.results-head h2{
  color:#10283d;font-size:1.55rem;font-weight:950;
  letter-spacing:-.04em;margin:0;
}
.results-head p{color:#6d8497;margin:.35rem 0 0}

/* ===== EDITOR V2 ===== */
.editor-v2-head{
  background:#fff;border:1px solid #d9effb;border-radius:30px;
  padding:16px 18px;margin:8px 0 14px;
  box-shadow:0 12px 30px rgba(39,174,243,.06);
}
.editor-v2-head b{color:#10283d;font-size:1.05rem}
.editor-v2-head span{color:#6d8497;font-size:.84rem}
.editor-preview-tag{
  display:inline-flex;padding:6px 11px;border-radius:999px;
  background:#eaf8ff;color:#2184ba;font-weight:900;font-size:.72rem;
  margin-bottom:8px;
}


</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:10px;">
  <div class="ai-orb">AI</div>
  <div class="hero-title">Gaming<br>Shorts Factory</div>
  <div class="hero-sub">Dal gameplay allo Short. Automaticamente.</div>
</div>

<div class="flow">
  <div class="orb orb-blue">CARICA</div>
  <div class="flow-arrow">›</div>
  <div class="orb orb-cyan">AI<br>ANALIZZA</div>
  <div class="flow-arrow">›</div>
  <div class="orb orb-yellow">SMART<br>CUT</div>
  <div class="flow-arrow">›</div>
  <div class="orb orb-red">SHORTS</div>
</div>
""", unsafe_allow_html=True)


# Cerca FFmpeg automaticamente: prima il vecchio percorso, poi PATH di Windows.
import shutil

def trova_ffmpeg():
    """Trova ffmpeg.exe senza dipendere da una singola cartella/versione."""
    candidati = []

    # 1) PATH di Windows
    trovato_path = shutil.which("ffmpeg")
    if trovato_path:
        candidati.append(trovato_path)

    # 2) Accanto all'app / sottocartelle comuni
    base_app = os.path.dirname(os.path.abspath(__file__))
    candidati += [
        os.path.join(base_app, "ffmpeg.exe"),
        os.path.join(base_app, "ffmpeg", "bin", "ffmpeg.exe"),
        os.path.join(base_app, "bin", "ffmpeg.exe"),
    ]

    # 3) Cartelle utente comuni
    home = os.path.expanduser("~")
    candidati += [
        os.path.join(home, "ffmpeg", "bin", "ffmpeg.exe"),
        os.path.join(home, "Desktop", "ffmpeg", "bin", "ffmpeg.exe"),
        os.path.join(home, "Downloads", "ffmpeg", "bin", "ffmpeg.exe"),
    ]

    for candidato in candidati:
        if candidato and os.path.isfile(candidato):
            return candidato

    # 4) Ultimo tentativo: cerca qualsiasi ffmpeg.exe nei Downloads.
    # Lo facciamo solo se i controlli rapidi sopra falliscono.
    downloads = os.path.join(home, "Downloads")
    if os.path.isdir(downloads):
        try:
            for root, dirs, files in os.walk(downloads):
                # evita cartelle enormi/nascoste non utili
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                if "ffmpeg.exe" in files:
                    return os.path.join(root, "ffmpeg.exe")
        except OSError:
            pass

    return None


FFMPEG_PATH = trova_ffmpeg()

def trova_ffprobe():
    """Trova ffprobe.exe usando la stessa installazione di FFmpeg o il PATH."""
    # 1) Se FFmpeg è stato trovato, ffprobe normalmente è nella stessa cartella.
    if FFMPEG_PATH:
        stessa_cartella = os.path.join(
            os.path.dirname(FFMPEG_PATH),
            "ffprobe.exe" if os.name == "nt" else "ffprobe"
        )
        if os.path.isfile(stessa_cartella):
            return stessa_cartella

    # 2) PATH di Windows/sistema.
    trovato_path = shutil.which("ffprobe")
    if trovato_path:
        return trovato_path

    # 3) Stesse cartelle comuni già usate per FFmpeg.
    base_app = os.path.dirname(os.path.abspath(__file__))
    home = os.path.expanduser("~")
    candidati = [
        os.path.join(base_app, "ffprobe.exe"),
        os.path.join(base_app, "ffmpeg", "bin", "ffprobe.exe"),
        os.path.join(base_app, "bin", "ffprobe.exe"),
        os.path.join(home, "ffmpeg", "bin", "ffprobe.exe"),
        os.path.join(home, "Desktop", "ffmpeg", "bin", "ffprobe.exe"),
        os.path.join(home, "Downloads", "ffmpeg", "bin", "ffprobe.exe"),
    ]

    for candidato in candidati:
        if os.path.isfile(candidato):
            return candidato

    return None


FFPROBE_PATH = trova_ffprobe()


def durata_video(file_path):
    if not FFMPEG_PATH:
        st.error(
            "⚠️ FFmpeg non trovato automaticamente. "
            "Metti la cartella FFmpeg dentro GamingShortsFactory "
            "oppure aggiungi ffmpeg al PATH di Windows."
        )
        return None

    comando = [
        FFMPEG_PATH,
        "-i", file_path
    ]
    try:
        risultato = subprocess.run(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except FileNotFoundError:
        st.error(
            "⚠️ FFmpeg non trovato. Controlla che ffmpeg.exe sia installato "
            "oppure disponibile nel PATH di Windows."
        )
        return None
    testo = risultato.stderr
    import re
    match = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", testo)
    if not match:
        return None
    ore = int(match.group(1))
    minuti = int(match.group(2))
    secondi = float(match.group(3))
    return ore * 3600 + minuti * 60 + secondi


def trova_clip_audio(input_file, temp_dir, clip_duration=30, numero_clip=3):
    """Trova rapidamente picchi audio usando solo FFmpeg."""
    comando = [
        FFMPEG_PATH,
        "-hide_banner",
        "-i", input_file,
        "-vn",
        "-af",
        "asetnsamples=n=88200:p=0,astats=metadata=1:reset=1,"
        "ametadata=print:key=lavfi.astats.Overall.RMS_level",
        "-f", "null",
        "-"
    ]

    risultato = subprocess.run(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    testo = (risultato.stdout or "") + "\\n" + (risultato.stderr or "")
    valori = []
    tempo_corrente = None

    for riga in testo.splitlines():
        match_tempo = re.search(r"pts_time:([0-9.]+)", riga)
        if match_tempo:
            tempo_corrente = float(match_tempo.group(1))

        if "lavfi.astats.Overall.RMS_level=" in riga and tempo_corrente is not None:
            try:
                valore = riga.split(
                    "lavfi.astats.Overall.RMS_level=", 1
                )[1].strip()
                db = float(valore)

                if math.isfinite(db):
                    valori.append((tempo_corrente, db))
            except:
                pass

    if not valori:
        return []

    candidati = sorted(
        valori,
        key=lambda x: x[1],
        reverse=True
    )

    scelti = []

    for tempo, db in candidati:
        start_clip = max(
            0.0,
            tempo - clip_duration / 2
        )

        troppo_vicino = any(
            abs(start_clip - precedente) < clip_duration * 0.8
            for precedente in scelti
        )

        if troppo_vicino:
            continue

        scelti.append(start_clip)

        if len(scelti) >= numero_clip:
            break

    return sorted(scelti)


def trova_clip_smart(input_file, temp_dir, clip_duration=30, numero_clip=3):
    """
    SMART CLIP:
    combina picchi audio e movimento/cambi scena.
    L'analisi video usa una copia ridotta (320px, 4 fps) per restare veloce.
    """

    # ---------- AUDIO ----------
    comando_audio = [
        FFMPEG_PATH,
        "-hide_banner",
        "-i", input_file,
        "-vn",
        "-af",
        "asetnsamples=n=44100:p=0,astats=metadata=1:reset=1,"
        "ametadata=print:key=lavfi.astats.Overall.RMS_level",
        "-f", "null",
        "-"
    ]

    risultato_audio = subprocess.run(
        comando_audio,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    testo_audio = (
        (risultato_audio.stdout or "")
        + "\n"
        + (risultato_audio.stderr or "")
    )

    audio = []
    tempo_corrente = None

    for riga in testo_audio.splitlines():
        mt = re.search(r"pts_time:([0-9.]+)", riga)

        if mt:
            tempo_corrente = float(mt.group(1))

        if (
            "lavfi.astats.Overall.RMS_level=" in riga
            and tempo_corrente is not None
        ):
            try:
                db = float(
                    riga.split(
                        "lavfi.astats.Overall.RMS_level=", 1
                    )[1].strip()
                )

                if math.isfinite(db):
                    audio.append((tempo_corrente, db))
            except:
                pass

    # ---------- VIDEO / MOVIMENTO ----------
    # scene score ad FPS ridotto: non renderizza un nuovo video.
    comando_video = [
        FFMPEG_PATH,
        "-hide_banner",
        "-i", input_file,
        "-an",
        "-vf",
        "fps=4,scale=320:-2,select='gte(scene,0)',metadata=print",
        "-f", "null",
        "-"
    ]

    risultato_video = subprocess.run(
        comando_video,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    testo_video = (
        (risultato_video.stdout or "")
        + "\n"
        + (risultato_video.stderr or "")
    )

    movimento = []
    tempo_video = None

    for riga in testo_video.splitlines():
        mt = re.search(r"pts_time:([0-9.]+)", riga)

        if mt:
            tempo_video = float(mt.group(1))

        if "lavfi.scene_score=" in riga and tempo_video is not None:
            try:
                score = float(
                    riga.split("lavfi.scene_score=", 1)[1]
                    .strip()
                    .split()[0]
                )
                movimento.append((tempo_video, score))
            except:
                pass

    if not audio and not movimento:
        return []

    # ---------- NORMALIZZAZIONE ----------
    # Creiamo punteggi per secondo.
    massimo_tempo = 0

    if audio:
        massimo_tempo = max(massimo_tempo, int(max(t for t, _ in audio)) + 1)

    if movimento:
        massimo_tempo = max(
            massimo_tempo,
            int(max(t for t, _ in movimento)) + 1
        )

    if massimo_tempo <= 0:
        return []

    audio_sec = [0.0] * (massimo_tempo + 1)
    video_sec = [0.0] * (massimo_tempo + 1)

    if audio:
        db_values = [db for _, db in audio]
        db_min = min(db_values)
        db_max = max(db_values)
        span = max(0.001, db_max - db_min)

        for t, db in audio:
            idx = min(int(t), massimo_tempo)