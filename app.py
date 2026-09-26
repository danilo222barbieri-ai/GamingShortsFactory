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
            idx = min(int(t), massimo_tempo)            norm = (db - db_min) / span
            audio_sec[idx] = max(audio_sec[idx], norm)

    if movimento:
        max_scene = max(score for _, score in movimento)
        max_scene = max(0.001, max_scene)

        for t, score in movimento:
            idx = min(int(t), massimo_tempo)
            norm = min(1.0, score / max_scene)
            video_sec[idx] = max(video_sec[idx], norm)

    # 60% audio + 40% movimento.
    combinato = [
        audio_sec[i] * 0.60 + video_sec[i] * 0.40
        for i in range(len(audio_sec))
    ]

    # ---------- FINESTRE ----------
    finestra = max(10, int(clip_duration))
    candidati = []

    for i in range(len(combinato)):
        fine = min(len(combinato), i + finestra)

        if fine - i < max(5, finestra // 2):
            continue

        valori = combinato[i:fine]
        media = sum(valori) / len(valori)
        picco = max(valori)

        # Preferiamo clip con attività sostenuta, non un singolo botto.
        score = media * 0.75 + picco * 0.25

        candidati.append((score, float(i)))

    candidati.sort(reverse=True)

    scelti = []

    for score, start_clip in candidati:
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


def crea_anteprima(input_file, output_file, start, duration):
    """Crea una preview leggera 640px usando QSV."""
    comando = [
        FFMPEG_PATH,
        "-y",
        "-ss", str(start),
        "-i", input_file,
        "-t", str(duration),
        "-vf", "scale=640:-2",
        "-c:v", "h264_qsv",
        "-preset", "veryfast",
        "-global_quality", "30",
        "-c:a", "aac",
        "-b:a", "96k",
        "-movflags", "+faststart",
        output_file
    ]

    risultato = subprocess.run(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return risultato.returncode == 0 and os.path.exists(output_file)



@st.cache_resource(show_spinner=False)
def _gsf_subtitle_whisper_model():
    """
    Modello dedicato ai sottotitoli.
    Small è molto più accurato di Tiny, ma viene usato solo sulle clip/scena
    selezionate, non sulla scansione AI dell'intero gameplay.
    """
    try:
        return WhisperModel("small", device="cpu", compute_type="int8")
    except Exception:
        # Fallback: l'app continua a funzionare anche se Small non è disponibile.
        return WhisperModel("tiny", device="cpu", compute_type="int8")


def _gsf_gaming_prompt(context_hint=""):
    hint = str(context_hint or "").strip()
    base = (
        "Gaming commentary. Preserve game names, player names, weapon names, "
        "gaming terms, acronyms and English words exactly when they are spoken."
    )
    if hint:
        base += f" Game: {hint}."
    return base



GSF_RENDER_ENGINE_VERSION = "v44-point4-final"


def _gsf_hex_to_ass(value, fallback="#FFFFFF"):
    """#RRGGBB -> ASS &H00BBGGRR."""
    value=str(value or fallback).strip()
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        value=fallback
    r=value[1:3]
    g=value[3:5]
    b=value[5:7]
    return f"&H00{b}{g}{r}"


def _gsf_ass_escape(text):
    return (
        str(text or "")
        .replace("\\", r"\\")
        .replace("{", "(")
        .replace("}", ")")
        .replace("\n", " ")
    )


def _gsf_ass_time(seconds):
    seconds=max(0.0,float(seconds))
    h=int(seconds//3600)
    m=int((seconds%3600)//60)
    s=seconds%60
    return f"{h}:{m:02d}:{s:05.2f}"


def _gsf_render_transcribe_words(source_path,start,duration):
    """
    Automatic subtitles for FINAL render only.
    Small stays the high-quality subtitle model; timestamps are relative
    to the selected output segment.
    """
    tmp_dir=tempfile.mkdtemp(prefix="gsf_render_sub_")
    wav=os.path.join(tmp_dir,"speech.wav")
    try:
        cmd=[
            FFMPEG_PATH,"-y","-ss",str(max(0.0,float(start))),"-i",str(source_path),
            "-t",str(max(.1,float(duration))),"-vn","-ac","1","-ar","16000",
            "-af","highpass=f=70,lowpass=f=7800,loudnorm=I=-16:LRA=11:TP=-1.5",
            wav
        ]
        r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if r.returncode!=0 or not os.path.exists(wav):
            return [],"Estrazione audio sottotitoli non riuscita"

        model=_gsf_subtitle_whisper_model()
        segs,info=model.transcribe(
            wav,
            language=None,
            task="transcribe",
            vad_filter=True,
            beam_size=5,
            best_of=5,
            word_timestamps=True,
            condition_on_previous_text=False,
            initial_prompt=_gsf_gaming_prompt(st.session_state.get("gioco","ARC Raiders")),
            vad_parameters=dict(min_silence_duration_ms=250)
        )

        words=[]
        for seg in list(segs):
            for w in (getattr(seg,"words",None) or []):
                tx=str(getattr(w,"word","") or "").strip()
                if not tx:
                    continue
                words.append({
                    "text":tx,
                    "start":max(0.0,float(w.start)),
                    "end":max(0.0,float(w.end)),
                })
        return words,None
    except Exception as e:
        return [],str(e)
    finally:
        try:
            shutil.rmtree(tmp_dir,ignore_errors=True)
        except Exception:
            pass


def _gsf_prepare_render_words(words, origin, duration):
    """
    Convert existing editor timestamps to segment-relative timestamps.
    Main editor passes origin=editor_start.
    Inline editor passes origin=its local IN because its words are relative
    to the lightweight preview.
    """
    out=[]
    origin=float(origin or 0.0)
    duration=max(.1,float(duration))
    for w in (words or []):
        try:
            tx=str(w.get("text","") or "").strip()
            if not tx:
                continue
            a=float(w.get("start",0.0))-origin
            b=float(w.get("end",a+.12))-origin
            if b<0 or a>duration:
                continue
            a=max(0.0,a)
            b=min(duration,max(a+.04,b))
            out.append({"text":tx,"start":a,"end":b})
        except Exception:
            continue
    return out



_GSF_HOOK_TEMPLATES = {
    "goal": "GOOOL! ⚽",
    "shooter_elimination": "ELIMINAZIONE! 🎯",
    "victory": "VITTORIA! 🏆",
    "sports_big_chance": "CHE OCCASIONE! 🥅",
    "racing": "MOMENTO GARA! 🏎️",
    "achievement": "NUOVO TRAGUARDO! ⭐",
    "impact_event": "MOMENTO FORTE! 💥",
}

_GSF_CATEGORY_HOOKS = {
    "reaction": "REAZIONE! 🎙️",
    "action": "AZIONE! 🔥",
    "story": "MOMENTO! 🎬",
}


def _gsf_diag_for_start(start, max_gap=12.0):
    """
    Finds the closest Point-3 diagnostic even after boundary refinement
    has shifted the actual clip start by a few seconds.
    """
    diagnostics=st.session_state.get("gsf_ai_v3_diagnostics",{}) or {}
    try:
        target=float(start)
    except Exception:
        return {}

    exact=diagnostics.get(round(target,3))
    if isinstance(exact,dict):
        return exact

    best=None
    best_gap=None
    for key,value in diagnostics.items():
        if key=="__meta__" or not isinstance(value,dict):
            continue
        try:
            k=float(key)
        except Exception:
            continue
        gap=abs(k-target)
        if best_gap is None or gap<best_gap:
            best_gap=gap
            best=value

    if best is not None and best_gap is not None and best_gap<=float(max_gap):
        return best
    return {}


def _gsf_hook_from_diag(diag, manual_hook=""):
    """
    Conservative hooks: only claims what Point 3 actually detected.
    A user supplied hook always wins.
    """
    manual=str(manual_hook or "").strip()
    if manual:
        return manual[:70]

    diag=diag or {}
    features=diag.get("features") or {}
    event_type=str(features.get("event_type","") or "")
    event_score=float(features.get("event_score",0.0))
    category=str(features.get("moment_category","") or "")

    if event_score>=0.56 and event_type in _GSF_HOOK_TEMPLATES:
        return _GSF_HOOK_TEMPLATES[event_type]

    if category in _GSF_CATEGORY_HOOKS:
        return _GSF_CATEGORY_HOOKS[category]

    return ""


def _gsf_auto_hook_for_start(start, manual_hook=""):
    return _gsf_hook_from_diag(
        _gsf_diag_for_start(start),
        manual_hook=manual_hook
    )


def _gsf_wrap_hook(text, max_chars=22):
    """At most two balanced lines for the top-of-screen hook."""
    words=str(text or "").strip().split()
    if not words:
        return ""

    lines=[""]
    for word in words:
        candidate=(lines[-1]+" "+word).strip()
        if len(candidate)<=int(max_chars) or len(lines)>=2:
            lines[-1]=candidate
        else:
            lines.append(word)

    if len(lines)>2:
        lines=lines[:2]
    return r"\N".join(x for x in lines if x)


def _gsf_write_render_ass(
    ass_file, words, fallback_text="",
    font="Arial", size=92, x_pct=50, y_pct=78,
    text_color="#FFFFFF", active_color="#FFD400",
    outline_color="#000000", fmt="9:16 Short",
    hook_text="", hook_duration=1.8, hook_y_pct=15
):
    """
    Final burn-in:
    - subtitles mirror the LIVE editor concept;
    - hook is a separate top layer and never replaces subtitles.
    """
    if fmt=="9:16 Short":
        w_res,h_res=1080,1920
    else:
        w_res,h_res=1920,1080

    x=int(max(5,min(95,float(x_pct)))/100.0*w_res)
    y=int(max(5,min(95,float(y_pct)))/100.0*h_res)
    fs=int(max(24,min(180,int(size))))
    primary=_gsf_hex_to_ass(text_color,"#FFFFFF")
    active=_gsf_hex_to_ass(active_color,"#FFD400")
    outline=_gsf_hex_to_ass(outline_color,"#000000")
    safe_font=str(font or "Arial").replace(","," ")

    hook_y=int(max(7,min(35,float(hook_y_pct)))/100.0*h_res)
    hook_size=84 if fmt=="9:16 Short" else 64

    ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w_res}
PlayResY: {h_res}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{safe_font},{fs},{primary},{active},{outline},&H78000000,-1,0,0,0,100,100,0,0,1,5,2,5,20,20,20,1
Style: Hook,Arial Black,{hook_size},&H00FFFFFF,&H0000D7FF,&H00000000,&H72000000,-1,0,0,0,100,100,0,0,1,7,3,8,40,40,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    wrote=False

    hook=str(hook_text or "").strip()
    if hook:
        hook=_gsf_wrap_hook(hook)
        hook_end=max(.65,min(2.4,float(hook_duration)))
        hook_line=(
            r"{\an8\pos("+str(w_res//2)+","+str(hook_y)+
            r")\fad(90,180)}"+_gsf_ass_escape(hook)
        )
        # _gsf_ass_escape would escape the ASS newline token; restore only ours.
        hook_line=hook_line.replace(r"\\N",r"\N")
        ass+=(
            f"Dialogue: 2,0:00:00.00,{_gsf_ass_time(hook_end)},"
            f"Hook,,0,0,0,,{hook_line}\n"
        )
        wrote=True

    words=list(words or [])
    if words:
        for idx,word in enumerate(words):
            group_start=(idx//4)*4
            group=words[group_start:group_start+4]
            parts=[]
            for j,item in enumerate(group):
                tx=_gsf_ass_escape(item.get("text",""))
                if group_start+j==idx:
                    parts.append(
                        r"{\c"+active+r"\b1}"+tx+
                        r"{\c"+primary+r"\b1}"
                    )
                else:
                    parts.append(tx)
            line=" ".join(parts).strip()
            if not line:
                continue
            a=float(word.get("start",0.0))
            b=max(a+.06,float(word.get("end",a+.16)))
            positioned=r"{\an5\pos("+str(x)+","+str(y)+r")}"+line
            ass+=(
                f"Dialogue: 0,{_gsf_ass_time(a)},{_gsf_ass_time(b)},"
                f"Default,,0,0,0,,{positioned}\n"
            )
            wrote=True

    elif str(fallback_text or "").strip():
        line=_gsf_ass_escape(fallback_text)
        positioned=r"{\an5\pos("+str(x)+","+str(y)+r")}"+line
        ass+=(
            f"Dialogue: 0,0:00:00.00,9:59:59.00,"
            f"Default,,0,0,0,,{positioned}\n"
        )
        wrote=True

    if not wrote:
        return False

    with open(ass_file,"w",encoding="utf-8") as f:
        f.write(ass)
    return True


GSF_SMART_REFRAME_VERSION = "v42-motion-track"


def _gsf_probe_video_size(path):
    """Raw video dimensions for Smart Reframe analysis."""
    try:
        probe=FFPROBE_PATH or shutil.which("ffprobe")
        if not probe:
            return None,None
        r=subprocess.run(
            [
                probe,"-v","error","-select_streams","v:0",
                "-show_entries","stream=width,height",
                "-of","csv=p=0:s=x",str(path)
            ],
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=15
        )
        if r.returncode!=0:
            return None,None
        lines=(r.stdout or "").strip().splitlines()
        if not lines:
            return None,None
        w,h=[int(float(x)) for x in lines[0].split("x")[:2]]
        if w<=0 or h<=0:
            return None,None
        return w,h
    except Exception:
        return None,None


def _gsf_smart_reframe_analyze(source_path,start,duration,sample_fps=4,analysis_width=288):
    """
    Lightweight motion tracker for 9:16 auto renders.
    FFmpeg decodes tiny grayscale frames; NumPy estimates the horizontal
    center of local motion. Conservative smoothing prevents jitter.
    """
    result={
        "enabled":False,
        "reason":"",
        "track":[],
        "confidence":0.0,
        "movement":0.0,
        "samples":0,
    }

    if np is None:
        result["reason"]="numpy non disponibile"
        return result

    w,h=_gsf_probe_video_size(source_path)
    if not w or not h:
        result["reason"]="dimensioni video non disponibili"
        return result

    source_aspect=float(w)/float(h)
    target_aspect=9.0/16.0

    if source_aspect <= target_aspect*1.08:
        result["reason"]="video già verticale"
        return result

    aw=max(160,int(analysis_width))
    ah=max(90,int(round(aw*h/w)))
    if ah%2:
        ah+=1

    fps=max(2,min(6,int(sample_fps)))
    cmd=[
        FFMPEG_PATH,"-hide_banner","-loglevel","error",
        "-ss",str(max(0.0,float(start))),
        "-i",str(source_path),
        "-t",str(max(.25,float(duration))),
        "-an",
        "-vf",f"fps={fps},scale={aw}:{ah},format=gray",
        "-pix_fmt","gray",
        "-f","rawvideo","pipe:1"
    ]
    try:
        r=subprocess.run(
            cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            timeout=max(15,int(float(duration)*2.5)+10)
        )
    except Exception as e:
        result["reason"]=f"analisi fallita: {e}"
        return result

    if r.returncode!=0 or not r.stdout:
        result["reason"]="FFmpeg non ha prodotto frame"
        return result

    frame_size=aw*ah
    frame_count=len(r.stdout)//frame_size
    if frame_count<3:
        result["reason"]="pochi frame"
        return result

    raw=np.frombuffer(r.stdout[:frame_count*frame_size],dtype=np.uint8)
    frames=raw.reshape(frame_count,ah,aw)

    crop_fraction=min(1.0,target_aspect/source_aspect)
    half_crop=crop_fraction/2.0
    min_c=max(half_crop,0.05)
    max_c=min(1.0-half_crop,0.95)

    xs=(np.arange(aw,dtype=np.float32)+0.5)/float(aw)
    center_prior=1.0-0.18*np.minimum(1.0,np.abs(xs-0.5)/0.5)

    centers=[0.5]
    confidences=[0.0]
    prev_center=0.5

    for i in range(1,frame_count):
        cur=frames[i].astype(np.int16)
        prev=frames[i-1].astype(np.int16)
        diff=np.abs(cur-prev).astype(np.float32)

        total=float(diff.sum())
        mean=float(diff.mean())
        if total<=1.0 or mean<0.15:
            centers.append(prev_center)
            confidences.append(0.0)
            continue

        threshold=float(np.percentile(diff,78.0))
        salient=np.maximum(diff-threshold,0.0)

        col=salient.sum(axis=0)
        sal_total=float(col.sum())
        if sal_total<=1.0:
            centers.append(prev_center)
            confidences.append(0.0)
            continue

        col=col*center_prior
        weighted_total=float(col.sum()) or 1.0
        desired=float((col*xs).sum()/weighted_total)

        saliency_ratio=min(1.0,sal_total/(total+1e-6)*3.0)
        p=col/weighted_total
        entropy=float(
            -(p*np.log(p+1e-9)).sum()/max(1e-9,math.log(len(p)))
        )
        concentration=max(0.0,min(1.0,1.0-entropy))
        confidence=max(
            0.0,min(1.0,0.72*saliency_ratio+0.28*concentration)
        )

        desired=max(min_c,min(max_c,desired))

        # On the first reliable motion sample, acquire the subject quickly
        # instead of spending the first seconds drifting from dead center.
        if i==1 and confidence>=0.30:
            smoothed=desired
            centers[0]=desired
        else:
            delta=desired-prev_center
            if abs(delta)<0.035:
                desired=prev_center

            max_step=0.080
            desired=max(
                prev_center-max_step,
                min(prev_center+max_step,desired)
            )
            alpha=0.16+0.34*confidence
            smoothed=prev_center*(1.0-alpha)+desired*alpha

        smoothed=max(min_c,min(max_c,smoothed))
        centers.append(smoothed)
        confidences.append(confidence)
        prev_center=smoothed

    smoothed=list(centers)
    for _ in range(2):
        next_values=list(smoothed)
        for i in range(1,len(smoothed)-1):
            next_values[i]=(
                0.20*smoothed[i-1]+
                0.60*smoothed[i]+
                0.20*smoothed[i+1]
            )
        smoothed=next_values

    stride=max(1,int(fps))
    track=[]
    for i in range(0,len(smoothed),stride):
        j=min(len(smoothed),i+stride)
        c=float(np.median(np.asarray(smoothed[i:j],dtype=np.float32)))
        conf=float(np.mean(np.asarray(confidences[i:j],dtype=np.float32)))
        track.append({
            "t":round(i/float(fps),3),
            "cx":round(max(min_c,min(max_c,c)),6),
            "confidence":round(max(0.0,min(1.0,conf)),4),
        })

    last_t=max(0.0,(len(smoothed)-1)/float(fps))
    if not track or last_t-track[-1]["t"]>0.35:
        track.append({
            "t":round(last_t,3),
            "cx":round(
                max(min_c,min(max_c,float(smoothed[-1]))),6
            ),
            "confidence":round(
                max(0.0,min(1.0,float(confidences[-1]))),4
            ),
        })

    movement=0.0
    if len(track)>1:
        movement=sum(
            abs(float(track[i]["cx"])-float(track[i-1]["cx"]))
            for i in range(1,len(track))
        )/max(1,len(track)-1)

    mean_conf=float(
        np.mean(np.asarray(confidences,dtype=np.float32))
    )

    if mean_conf<0.12 or movement<0.006:
        result.update({
            "reason":"movimento non abbastanza affidabile",
            "track":[
                {"t":0.0,"cx":0.5,"confidence":round(mean_conf,4)}
            ],
            "confidence":round(mean_conf,4),
            "movement":round(movement,5),
            "samples":frame_count,
        })
        return result

    result.update({
        "enabled":True,
        "reason":"motion tracking",
        "track":track,
        "confidence":round(mean_conf,4),
        "movement":round(movement,5),
        "samples":frame_count,
    })
    return result


def _gsf_smart_reframe_cached(source_path,start,duration,cache_token=None):
    cache=st.session_state.setdefault(
        "gsf_smart_reframe_cache_v42",{}
    )
    key=(
        GSF_SMART_REFRAME_VERSION,
        str(cache_token or source_path),
        round(float(start),2),
        round(float(duration),2),
    )
    if key in cache:
        return cache[key],True

    result=_gsf_smart_reframe_analyze(
        source_path,start,duration
    )
    cache[key]=result
    try:
        while len(cache)>24:
            first=next(iter(cache))
            cache.pop(first,None)
    except Exception:
        pass
    return result,False


def _gsf_smart_reframe_cx_expression(track):
    """Piecewise-linear normalized horizontal center for FFmpeg crop."""
    pts=[]
    for item in (track or []):
        try:
            pts.append((float(item["t"]),float(item["cx"])))
        except Exception:
            continue

    if not pts:
        return "0.5"

    pts=sorted(pts,key=lambda x:x[0])
    if len(pts)==1:
        return f"{pts[0][1]:.6f}"

    expr=f"{pts[-1][1]:.6f}"
    for i in range(len(pts)-2,-1,-1):
        t0,c0=pts[i]
        t1,c1=pts[i+1]
        dt=max(.001,t1-t0)
        segment=(
            f"({c0:.6f}+({c1-c0:.6f})*"
            f"(t-{t0:.3f})/{dt:.3f})"
        )
        expr=f"if(lt(t,{t1:.3f}),{segment},{expr})"
    return expr


def _gsf_smart_reframe_filter(track,zoom=1.0,y_pos=0):
    """
    Landscape -> 1080x1920 with continuous horizontal pan.
    Manual Y still applies if zoom creates vertical headroom.
    """
    zoom=max(1.0,float(zoom))
    y_pos=float(y_pos)
    cx=_gsf_smart_reframe_cx_expression(track)

    return (
        "setpts=PTS-STARTPTS,"
        "scale=-2:1920,"
        f"scale=iw*{zoom}:ih*{zoom},"
        "crop=1080:1920:"
        f"x='max(0,min(iw-ow,({cx})*iw-ow/2))':"
        f"y='max(0,min(ih-oh,(ih-oh)/2+({y_pos}/100)*(ih-oh)/2))'"
    )


def _gsf_render_video_filters(
    fmt,zoom,x_pos,y_pos,brightness,contrast,speed,
    ass_file=None,reframe_track=None
):
    """Single source of truth for FINAL render geometry."""
    zoom=max(1.0,float(zoom))
    x_pos=float(x_pos)
    y_pos=float(y_pos)
    brightness=float(brightness)
    contrast=float(contrast)
    speed=max(.25,float(speed))

    if fmt=="9:16 Short" and reframe_track:
        vf=(
            _gsf_smart_reframe_filter(
                reframe_track,zoom=zoom,y_pos=y_pos
            )
            +f",eq=brightness={brightness}:contrast={contrast},"
            +f"setpts=PTS/{speed}"
        )
    elif fmt=="9:16 Short":
        out_w,out_h=1080,1920
        vf=(
            f"scale={out_w}:{out_h}:force_original_aspect_ratio=increase,"
            f"crop={out_w}:{out_h},"
            f"scale=iw*{zoom}:ih*{zoom},"
            f"crop={out_w}:{out_h}:"
            f"(iw-{out_w})/2+({x_pos}/100)*(iw-{out_w})/2:"
            f"(ih-{out_h})/2+({y_pos}/100)*(ih-{out_h})/2,"
            f"eq=brightness={brightness}:contrast={contrast},"
            f"setpts=PTS/{speed}"
        )
    else:
        out_h=1080
        vf=(
            f"scale=-2:{out_h},"
            f"scale=iw*{zoom}:ih*{zoom},"
            f"crop=iw/{zoom}:ih/{zoom}:"
            f"(iw-iw/{zoom})/2+({x_pos}/100)*(iw-iw/{zoom})/2:"
            f"(ih-ih/{zoom})/2+({y_pos}/100)*(ih-ih/{zoom})/2,"
            f"scale=-2:{out_h},"
            f"eq=brightness={brightness}:contrast={contrast},"
            f"setpts=PTS/{speed}"
        )

    if ass_file and os.path.exists(ass_file):
        ass_path=str(ass_file).replace("\\","/").replace(":","\\:")
        vf+=f",ass=filename='{ass_path}'"

    return vf


def _gsf_render_audio_filter(
    speed=1.0,volume=100,normalize_audio=True,
    duration=None,polish_audio=True
):
    """
    Final audio chain:
    speed -> loudness -> user volume -> limiter -> micro fades.
    Fades are intentionally tiny: they remove hard cuts without softening
    gunshots, goals or other important impacts.
    """
    speed=max(.25,float(speed))
    volume=max(0.0,float(volume))/100.0
    parts=[]

    local_speed=speed
    while local_speed>2.0:
        parts.append("atempo=2.0")
        local_speed/=2.0
    while local_speed<0.5:
        parts.append("atempo=0.5")
        local_speed/=0.5
    parts.append(f"atempo={local_speed:.4f}")

    if normalize_audio:
        parts.append("loudnorm=I=-14:LRA=9:TP=-1.5")

    parts.append(f"volume={volume:.4f}")

    if polish_audio:
        parts.append("alimiter=limit=0.95:attack=5:release=50")

        if duration is not None:
            out_duration=max(.10,float(duration)/speed)
            fade_in=min(.045,out_duration*.15)
            fade_out=min(.085,out_duration*.20)
            fade_out_start=max(0.0,out_duration-fade_out)
            parts.append(
                f"afade=t=in:st=0:d={fade_in:.4f}"
            )
            parts.append(
                f"afade=t=out:st={fade_out_start:.4f}:d={fade_out:.4f}"
            )

    return ",".join(parts)


def _gsf_render_core(
    source_path, output_path, start, duration,
    fmt="9:16 Short", zoom=1.0, x_pos=0, y_pos=0,
    brightness=0.0, contrast=1.0, speed=1.0, volume=100,
    subtitles_enabled=False, subtitle_mode="Automatici",
    subtitle_words=None, subtitle_text="", subtitle_time_origin=None,
    subtitle_font="Arial", subtitle_size=92,
    subtitle_x=50, subtitle_y=78,
    text_color="#FFFFFF", active_color="#FFD400",
    outline_color="#000000",
    normalize_audio=True,
    smart_reframe=False,
    reframe_cache_token=None,
    hook_text="",
    hook_duration=None,
    polish_audio=True
):
    """
    V43 final render core: Smart Reframe + hook + audio polish.

    ALWAYS renders from source_path, performs one final video encode,
    burns subtitles in that same pass, prefers Intel QSV and falls back
    to libx264 automatically.
    """
    t0=time.perf_counter()
    start=max(0.0,float(start))
    duration=max(.1,float(duration))
    temp_dir=tempfile.mkdtemp(prefix="gsf_render_core_")
    ass_file=os.path.join(temp_dir,"subs.ass")
    subtitle_error=None
    used_words=[]
    reframe_meta={
        "enabled":False,
        "reason":"disattivato",
        "track":[],
        "confidence":0.0,
        "movement":0.0,
        "samples":0,
    }
    reframe_cache_hit=False

    try:
        if subtitles_enabled and str(subtitle_mode)!="Nessuno":
            if subtitle_words:
                origin=start if subtitle_time_origin is None else float(subtitle_time_origin)
                used_words=_gsf_prepare_render_words(
                    subtitle_words,origin,duration
                )
            else:
                used_words,subtitle_error=_gsf_render_transcribe_words(
                    source_path,start,duration
                )

        _hook_text=str(hook_text or "").strip()
        _hook_duration=(
            float(hook_duration)
            if hook_duration is not None
            else min(2.0,max(1.15,float(duration)*0.12))
        )

        if (
            (subtitles_enabled and str(subtitle_mode)!="Nessuno")
            or _hook_text
        ):
            _gsf_write_render_ass(
                ass_file,
                used_words,
                fallback_text=(
                    subtitle_text
                    if subtitle_words and subtitles_enabled else ""
                ),
                font=subtitle_font,
                size=subtitle_size,
                x_pct=subtitle_x,
                y_pct=subtitle_y,
                text_color=text_color,
                active_color=active_color,
                outline_color=outline_color,
                fmt=fmt,
                hook_text=_hook_text,
                hook_duration=_hook_duration,
                hook_y_pct=15
            )

        reframe_track=None
        if bool(smart_reframe) and fmt=="9:16 Short":
            reframe_meta,reframe_cache_hit=_gsf_smart_reframe_cached(
                source_path,start,duration,
                cache_token=reframe_cache_token
            )
            if reframe_meta.get("enabled"):
                reframe_track=reframe_meta.get("track") or None

        vf=_gsf_render_video_filters(
            fmt,zoom,x_pos,y_pos,brightness,contrast,speed,
            ass_file=ass_file if os.path.exists(ass_file) else None,
            reframe_track=reframe_track
        )
        af=_gsf_render_audio_filter(
            speed=speed,
            volume=volume,
            normalize_audio=normalize_audio,
            duration=duration,
            polish_audio=polish_audio
        )

        base=[
            FFMPEG_PATH,"-y",
            "-ss",str(start),
            "-i",str(source_path),
            "-t",str(duration),
            "-vf",vf,
            "-af",af
        ]

        attempts=[
            (
                "Intel QSV",
                base+[
                    "-c:v","h264_qsv",
                    "-preset","veryfast",
                    "-global_quality","23",
                    "-c:a","aac","-b:a","160k",
                    "-movflags","+faststart",
                    str(output_path)
                ]
            ),
            (
                "libx264",
                base+[
                    "-c:v","libx264",
                    "-preset","veryfast",
                    "-crf","22",
                    "-c:a","aac","-b:a","160k",
                    "-movflags","+faststart",
                    str(output_path)
                ]
            )
        ]

        last_error=""
        for encoder,cmd in attempts:
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception:
                pass

            r=subprocess.run(
                cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True
            )
            if r.returncode==0 and os.path.exists(output_path) and os.path.getsize(output_path)>0:
                return {                    "ok":True,
                    "path":str(output_path),
                    "encoder":encoder,
                    "seconds":round(time.perf_counter()-t0,2),
                    "subtitle_words":len(used_words),
                    "subtitle_error":subtitle_error,
                    "smart_reframe":reframe_meta,
                    "reframe_cache_hit":bool(reframe_cache_hit),
                    "hook_text":_hook_text,
                    "audio_polish":bool(polish_audio),
                    "error":"",
                }
            last_error=(r.stderr or "")[-3500:]

        return {
            "ok":False,"path":str(output_path),"encoder":"",
            "seconds":round(time.perf_counter()-t0,2),
            "subtitle_words":len(used_words),
            "subtitle_error":subtitle_error,
            "smart_reframe":reframe_meta,
            "reframe_cache_hit":bool(reframe_cache_hit),
            "hook_text":_hook_text,
            "audio_polish":bool(polish_audio),
            "error":last_error,
        }
    finally:
        shutil.rmtree(temp_dir,ignore_errors=True)



GSF_MASTER_ENGINE_VERSION = "v44-auto-master"


def _gsf_upload_master_token(video_obj):
    """Stable identity shared by single render and batch render."""
    try:
        name=str(getattr(video_obj,"name","video") or "video")
        size=int(getattr(video_obj,"size",len(video_obj.getbuffer())))
        return f"{name}|{size}"
    except Exception:
        return "video|unknown"


def _gsf_auto_master_profile(subtitles_enabled=True):
    """
    One automatic visual/audio profile.
    Every automatic export path uses this exact profile.
    """
    return {
        "fmt":"9:16 Short",
        "zoom":1.0,
        "x_pos":0,
        "y_pos":0,
        "brightness":0.0,
        "contrast":1.0,
        "speed":1.0,
        "volume":100,
        "subtitles_enabled":bool(subtitles_enabled),
        "subtitle_mode":"Automatici",
        "subtitle_font":"Arial",
        "subtitle_size":int(st.session_state.get("editor_sub_size",92)),
        "subtitle_x":50,
        "subtitle_y":int(st.session_state.get("subtitle_y",78)),
        "text_color":st.session_state.get("subtitle_text_color","#FFFFFF"),
        "active_color":st.session_state.get("subtitle_active_color","#FFD400"),
        "outline_color":st.session_state.get("subtitle_outline_color","#000000"),
        "normalize_audio":True,
        "smart_reframe":True,
        "polish_audio":True,
    }


def _gsf_master_signature(master_token,start,duration,profile,hook_text):
    payload={
        "engine":GSF_MASTER_ENGINE_VERSION,
        "render_engine":GSF_RENDER_ENGINE_VERSION,
        "source":str(master_token or ""),
        "start":round(float(start),3),
        "duration":round(float(duration),3),
        "profile":profile,
        "hook":str(hook_text or ""),
    }
    raw=json.dumps(payload,sort_keys=True,ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _gsf_master_cache_trim(cache,max_items=6):
    try:
        while len(cache)>int(max_items):
            first=next(iter(cache))
            cache.pop(first,None)
    except Exception:
        pass


def _gsf_render_auto_master(
    source_path,
    start,
    duration,
    master_token,
    subtitles_enabled=True,
    manual_hook="",
    output_path=None
):
    """
    THE automatic final-render entry point.

    `USA QUESTA` and `GENERA I 3 SHORTS` both call this function.
    Same source token + same moment + same project style => same cached bytes.
    """
    start=max(0.0,float(start))
    duration=max(.1,float(duration))
    profile=_gsf_auto_master_profile(subtitles_enabled=subtitles_enabled)
    hook=_gsf_auto_hook_for_start(start,manual_hook=manual_hook)
    signature=_gsf_master_signature(
        master_token,start,duration,profile,hook
    )

    cache=st.session_state.setdefault("gsf_final_master_cache_v44",{})
    cached=cache.get(signature)

    if cached and isinstance(cached.get("bytes"),(bytes,bytearray)):
        data=bytes(cached["bytes"])
        if output_path:
            with open(output_path,"wb") as f:
                f.write(data)
        meta=dict(cached.get("meta") or {})
        meta.update({
            "ok":True,
            "cache_hit":True,
            "signature":signature,
            "bytes":data,
            "path":str(output_path or ""),
        })
        return meta

    own_temp=None
    if output_path is None:
        own_temp=tempfile.mkdtemp(prefix="gsf_master_v44_")
        output_path=os.path.join(own_temp,"master.mp4")

    try:
        result=_gsf_render_core(
            source_path,
            output_path,
            start,
            duration,
            fmt=profile["fmt"],
            zoom=profile["zoom"],
            x_pos=profile["x_pos"],
            y_pos=profile["y_pos"],
            brightness=profile["brightness"],
            contrast=profile["contrast"],
            speed=profile["speed"],
            volume=profile["volume"],
            subtitles_enabled=profile["subtitles_enabled"],
            subtitle_mode=profile["subtitle_mode"],
            subtitle_words=None,
            subtitle_text="",
            subtitle_font=profile["subtitle_font"],
            subtitle_size=profile["subtitle_size"],
            subtitle_x=profile["subtitle_x"],
            subtitle_y=profile["subtitle_y"],
            text_color=profile["text_color"],
            active_color=profile["active_color"],
            outline_color=profile["outline_color"],
            normalize_audio=profile["normalize_audio"],
            smart_reframe=profile["smart_reframe"],
            reframe_cache_token=f"master|{master_token}",
            hook_text=hook,
            polish_audio=profile["polish_audio"],
        )

        if not result.get("ok") or not os.path.exists(output_path):
            result=dict(result or {})
            result.update({
                "ok":False,
                "cache_hit":False,
                "signature":signature,
                "bytes":b"",
            })
            return result

        with open(output_path,"rb") as f:
            data=f.read()

        meta=dict(result)
        # Do not store temp-path identity in the reusable metadata.
        meta["path"]=""
        meta["signature"]=signature

        cache[signature]={
            "bytes":data,
            "meta":meta,
        }
        _gsf_master_cache_trim(cache,6)

        result.update({
            "cache_hit":False,
            "signature":signature,
            "bytes":data,
        })
        return result
    finally:
        if own_temp:
            shutil.rmtree(own_temp,ignore_errors=True)


def crea_short_batch(
    input_file,
    temp_dir,
    start,
    duration,
    indice,
    sottotitoli_attivi=True,
    normalizza_audio_attivo=True,
    stile_sub_attivo="Gaming",
    dimensione_sub_attiva=92,
    posizione_sub_attiva=330,
    hook_text="",
    master_token=""
):
    """
    Compatibility wrapper.
    The actual work is delegated to _gsf_render_auto_master, exactly like
    the single selected Short.
    """
    output_file=os.path.join(temp_dir,f"short_{indice}.mp4")
    result=_gsf_render_auto_master(
        input_file,
        start,
        duration,
        master_token=(master_token or os.path.abspath(str(input_file))),
        subtitles_enabled=bool(sottotitoli_attivi),
        manual_hook=hook_text,
        output_path=output_file
    )
    return output_file if result.get("ok") else None


def deep_rank_candidati_leggero(input_file, risultati, clip_duration):
    """
    Secondo passaggio leggero SOLO sui candidati del Fast Scan.
    Non usa modelli vision pesanti.

    Per ogni candidato misura:
    - energia audio a inizio / centro / fine
    - densità dei cambi visivi
    - presenza di un picco centrale
    - penalità se la clip parte già al massimo o finisce senza chiusura

    Restituisce gli stessi candidati riordinati.
    """
    if not risultati:
        return []

    refined = []

    for fast_score, start in risultati[:3]:
        start = max(0.0, float(start))
        dur = max(5.0, float(clip_duration))

        # Analisi locale molto economica: solo questa piccola finestra.
        cmd = [
            FFMPEG_PATH, "-hide_banner",
            "-ss", str(start),
            "-t", str(dur),
            "-i", input_file,
            "-filter_complex",
            (
                "[0:a]asetnsamples=n=22050:p=0,"
                "astats=metadata=1:reset=1,"
                "ametadata=print:key=lavfi.astats.Overall.RMS_level[a];"
                "[0:v]fps=2,scale=160:-2,"
                "select='gte(scene,0)',metadata=print[v]"
            ),
            "-map", "[a]", "-map", "[v]",
            "-f", "null", "-"
        ]

        rr = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        raw = (rr.stdout or "") + "\n" + (rr.stderr or "")

        audio_points = []
        scene_points = []
        current_t = None

        for line in raw.splitlines():
            mt = re.search(r"pts_time:([0-9.]+)", line)
            if mt:
                try:
                    current_t = float(mt.group(1))
                except Exception:
                    current_t = None

            if current_t is not None and "lavfi.astats.Overall.RMS_level=" in line:
                try:
                    db = float(
                        line.split("lavfi.astats.Overall.RMS_level=", 1)[1]
                        .strip().split()[0]
                    )
                    if math.isfinite(db):
                        audio_points.append((current_t, db))
                except Exception:
                    pass

            if current_t is not None and "lavfi.scene_score=" in line:
                try:
                    val = float(
                        line.split("lavfi.scene_score=", 1)[1]
                        .strip().split()[0]
                    )
                    scene_points.append((current_t, val))
                except Exception:
                    pass

        # Audio -> 0..1 locale.
        norm_audio = []
        if audio_points:
            vals = [x[1] for x in audio_points]
            lo, hi = min(vals), max(vals)
            span = max(0.001, hi - lo)
            norm_audio = [(t, (db - lo) / span) for t, db in audio_points]

        def media_fascia(points, a, b):
            vals = [v for t, v in points if a <= t < b]
            return sum(vals) / len(vals) if vals else 0.0

        third = dur / 3.0
        a_start = media_fascia(norm_audio, 0, third)
        a_mid = media_fascia(norm_audio, third, third * 2)
        a_end = media_fascia(norm_audio, third * 2, dur)

        # Picco centrale = utile per mini arco narrativo/hook-payoff.
        center_peak = max(0.0, a_mid - ((a_start + a_end) / 2.0))

        # Densità visiva, ma limitata per non premiare il caos infinito.
        scene_density = 0.0
        if scene_points:
            scene_density = min(
                1.0,
                sum(max(0.0, v) for _, v in scene_points)
                / max(1.0, dur * 0.12)
            )

        # Preferisce una clip che cresce verso il centro e poi respira leggermente.
        arc_score = (
            0.30 * a_mid
            + 0.22 * center_peak
            + 0.20 * scene_density
            + 0.14 * max(0.0, a_mid - a_start)
            + 0.14 * max(0.0, a_mid - a_end)
        )

        # Se inizia già "esplosa", possibile taglio troppo tardi.
        late_start_penalty = 0.10 if a_start > 0.82 and a_mid <= a_start else 0.0

        deep_score = (
            float(fast_score) * 0.72
            + arc_score * 0.28
            - late_start_penalty
        )

        refined.append((deep_score, start))

    refined.sort(reverse=True)
    return refined


def ai_director_locale(input_file, clip_duration=30, numero_clip=5):
    """
    AI Director locale leggero per CPU/RAM contenute.
    Analizza l'intero video con FFmpeg:
    - energia audio
    - movimento/cambi scena
    - attività sostenuta
    - penalità per zone quasi ferme/silenziose
    Restituisce i migliori momenti senza modelli vision pesanti.
    """

    # AUDIO: RMS per circa 1 secondo.
    cmd_audio = [
        FFMPEG_PATH, "-hide_banner",
        "-i", input_file,
        "-vn",
        "-af",
        "asetnsamples=n=44100:p=0,astats=metadata=1:reset=1,"
        "ametadata=print:key=lavfi.astats.Overall.RMS_level",
        "-f", "null", "-"
    ]

    ra = subprocess.run(
        cmd_audio,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    audio_text = (ra.stdout or "") + "\n" + (ra.stderr or "")
    audio_raw = []
    t = None

    for line in audio_text.splitlines():
        mt = re.search(r"pts_time:([0-9.]+)", line)
        if mt:
            t = float(mt.group(1))

        if "lavfi.astats.Overall.RMS_level=" in line and t is not None:
            try:
                db = float(
                    line.split(
                        "lavfi.astats.Overall.RMS_level=", 1
                    )[1].strip()
                )
                if math.isfinite(db):
                    audio_raw.append((t, db))
            except:
                pass

    # VIDEO FAST: 1 fps / 192px = scansione leggera dell’intero gameplay.
    cmd_video = [
        FFMPEG_PATH, "-hide_banner",
        "-i", input_file,
        "-an",
        "-vf",
        (
            "fps=0.5,scale=128:-2,select='gte(scene,0)',metadata=print"
            if globals().get("analisi_rapida", True)
            else
            "fps=3,scale=256:-2,select='gte(scene,0)',metadata=print"
        ),
        "-f", "null", "-"
    ]

    rv = subprocess.run(
        cmd_video,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    video_text = (rv.stdout or "") + "\n" + (rv.stderr or "")
    video_raw = []
    t = None

    for line in video_text.splitlines():
        mt = re.search(r"pts_time:([0-9.]+)", line)
        if mt:
            t = float(mt.group(1))

        if "lavfi.scene_score=" in line and t is not None:
            try:
                score = float(
                    line.split("lavfi.scene_score=", 1)[1]
                    .strip().split()[0]
                )
                video_raw.append((t, score))
            except:
                pass

    if not audio_raw and not video_raw:
        return []

    max_t = 1
    if audio_raw:
        max_t = max(max_t, int(max(x[0] for x in audio_raw)) + 2)
    if video_raw:
        max_t = max(max_t, int(max(x[0] for x in video_raw)) + 2)

    audio = [0.0] * max_t
    motion = [0.0] * max_t

    # Normalizzazione audio 0..1
    if audio_raw:
        vals = [db for _, db in audio_raw]
        lo, hi = min(vals), max(vals)
        span = max(0.001, hi - lo)

        for sec, db in audio_raw:
            idx = min(int(sec), max_t - 1)
            audio[idx] = max(
                audio[idx],
                (db - lo) / span
            )

    # Normalizzazione movimento 0..1, robusta al singolo picco.
    if video_raw:
        vals = sorted(v for _, v in video_raw)
        ref = vals[max(0, int(len(vals) * 0.95) - 1)] if vals else 1.0
        ref = max(0.001, ref)

        for sec, val in video_raw:
            idx = min(int(sec), max_t - 1)
            motion[idx] = max(
                motion[idx],
                min(1.0, val / ref)
            )

    # Feature combinata per secondo.
    activity = []
    for i in range(max_t):
        a = audio[i]
        m = motion[i]

        # Bonus quando audio e azione visiva avvengono insieme.
        synergy = min(a, m)

        # Penalizza tempi morti e scene statiche/menu/loading.
        dead_penalty = 0.22 if a < 0.12 and m < 0.08 else 0.0
        static_penalty = 0.18 if m < 0.035 else 0.0

        score = (
            0.45 * a
            + 0.40 * m
            + 0.25 * synergy
            - dead_penalty
            - static_penalty
        )

        activity.append(max(0.0, score))

    win = max(10, int(clip_duration))
    candidates = []

    # Valutiamo ogni possibile finestra.
    for start in range(0, max(1, len(activity) - win + 1)):
        vals = activity[start:start + win]
        if len(vals) < max(5, win // 2):
            continue

        avg = sum(vals) / len(vals)
        peak = max(vals)

        # Quanto della clip è davvero "vivo".
        active_ratio = (
            sum(1 for x in vals if x >= 0.28)
            / len(vals)
        )

        # Premia attività nella parte centrale, utile per hook -> payoff.
        q1 = max(1, len(vals) // 4)
        center = vals[q1:-q1] if len(vals) > q1 * 2 else vals
        center_avg = sum(center) / len(center)

        score = (
            avg * 0.48
            + peak * 0.17
            + active_ratio * 0.20
            + center_avg * 0.15
        )

        candidates.append((score, float(start)))

    candidates.sort(reverse=True)

    chosen = []

    for score, start in candidates:
        # Evita 5 clip dello stesso combattimento.
        if any(
            abs(start - old_start) < clip_duration * 0.85
            for _, old_start in chosen
        ):
            continue

        chosen.append((score, start))

        if len(chosen) >= numero_clip:
            break

    # Manteniamo ordine di qualità: migliore per prima.
    return chosen



# ==========================================================
# POINT 3 — AI MOMENT ENGINE V3
# Quattro profili realmente distinti, mantenendo l'analisi locale/leggera.
# ==========================================================

_GSF_REACTION_WORDS = {
    # IT
    "wow","oddio","dio","no","sì","si","dai","vai","attenzione","merda","cazzo",
    "incredibile","pazzesco","assurdo","preso","preso!","morto","ucciso","grande",
    # EN
    "wow","oh","omg","god","no","yes","yeah","lets","let's","go","damn","shit",
    "crazy","insane","what","nice","got","him","dead","kill","killed",
    # ES / PT / FR — piccoli segnali universali, nessun modello aggiuntivo
    "vamos","dios","madre","mierda","increíble","increible","sim","não","nao",
    "allez","putain","incroyable"
}

@st.cache_resource(show_spinner=False)
def _gsf_ai_whisper_tiny():
    """Carica Tiny una volta sola per i controlli vocali dei candidati."""
    return WhisperModel("tiny", device="cpu", compute_type="int8")


def _gsf_norm_series(values):
    if not values:
        return []
    vals=[float(v) for v in values]
    ordered=sorted(vals)
    # Percentili robusti: un singolo botto non schiaccia tutto il resto.
    lo=ordered[max(0, int(len(ordered)*0.05)-1)]
    hi=ordered[min(len(ordered)-1, int(len(ordered)*0.95))]
    span=max(1e-6, hi-lo)
    return [max(0.0,min(1.0,(v-lo)/span)) for v in vals]



GSF_AI_ENGINE_VERSION = "v40-point3-final"


def _gsf_ai_cache_trim(cache, max_items):
    """Mantiene piccole le cache di sessione."""
    try:
        while len(cache) > int(max_items):
            first_key = next(iter(cache))
            cache.pop(first_key, None)
    except Exception:
        pass


def _gsf_ai_scan_cached(input_file, cache_token=None):
    """
    La scansione FFmpeg dell'intero gameplay è la parte che cresce con la durata.
    La riusiamo quando l'utente prova Automatico / Director / Azione / Reazioni
    sullo stesso video.
    """
    cache = st.session_state.setdefault("gsf_ai_scan_cache_v40", {})
    key = (
        GSF_AI_ENGINE_VERSION,
        str(cache_token or input_file)
    )

    if key in cache:
        return cache[key], True

    scan = _gsf_ai_scan_base(input_file)
    cache[key] = scan
    _gsf_ai_cache_trim(cache, 2)
    return scan, False


def _gsf_ai_voice_cached(input_file, start, duration, cache_token=None):
    """
    Riusa Whisper Tiny quando due modalità AI finiscono per controllare
    la stessa finestra temporale.
    """
    cache = st.session_state.setdefault("gsf_ai_voice_cache_v40", {})
    key = (
        GSF_AI_ENGINE_VERSION,
        str(cache_token or input_file),
        round(float(start), 2),
        round(float(duration), 2),
        str(st.session_state.get("gioco", "") or "")
    )

    if key in cache:
        return cache[key], True

    result = _gsf_ai_voice_features(input_file, start, duration)
    cache[key] = result
    _gsf_ai_cache_trim(cache, 96)
    return result, False


def _gsf_ai_scan_base(input_file):
    """
    Fast scan unico dell'intero gameplay.
    Ritorna feature ogni ~0.5s:
    audio RMS, picco audio e differenza visiva/scene score.
    """
    # AUDIO 0.5 s, normalizzato poi in modo robusto.
    cmd_audio=[
        FFMPEG_PATH,"-hide_banner","-i",input_file,"-vn",
        "-af",
        (
            "aresample=16000,asetnsamples=n=8000:p=0,"
            "astats=metadata=1:reset=1,"
            "ametadata=print:key=lavfi.astats.Overall.RMS_level,"
            "ametadata=print:key=lavfi.astats.Overall.Peak_level"
        ),
        "-f","null","-"
    ]
    ra=subprocess.run(cmd_audio,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    raw_audio=(ra.stdout or "")+"\n"+(ra.stderr or "")
    audio_points={}
    current_t=None
    for line in raw_audio.splitlines():
        mt=re.search(r"pts_time:([0-9.]+)",line)
        if mt:
            try: current_t=float(mt.group(1))
            except Exception: current_t=None
        if current_t is None:
            continue
        bucket=max(0,int(round(current_t*2.0)))
        if "lavfi.astats.Overall.RMS_level=" in line:
            try:
                v=float(line.split("lavfi.astats.Overall.RMS_level=",1)[1].strip().split()[0])
                if math.isfinite(v):
                    audio_points.setdefault(bucket,{})["rms"]=v
            except Exception:
                pass
        elif "lavfi.astats.Overall.Peak_level=" in line:
            try:
                v=float(line.split("lavfi.astats.Overall.Peak_level=",1)[1].strip().split()[0])
                if math.isfinite(v):
                    audio_points.setdefault(bucket,{})["peak"]=v
            except Exception:
                pass

    # VIDEO 2 fps: scene score come proxy economica di cambi/movimento.
    cmd_video=[
        FFMPEG_PATH,"-hide_banner","-i",input_file,"-an",
        "-vf","fps=2,scale=192:-2,select='gte(scene,0)',metadata=print",
        "-f","null","-"
    ]
    rv=subprocess.run(cmd_video,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    raw_video=(rv.stdout or "")+"\n"+(rv.stderr or "")
    motion_points={}
    current_t=None
    for line in raw_video.splitlines():
        mt=re.search(r"pts_time:([0-9.]+)",line)
        if mt:
            try: current_t=float(mt.group(1))
            except Exception: current_t=None
        if current_t is not None and "lavfi.scene_score=" in line:
            try:
                v=float(line.split("lavfi.scene_score=",1)[1].strip().split()[0])
                bucket=max(0,int(round(current_t*2.0)))
                motion_points[bucket]=max(motion_points.get(bucket,0.0),max(0.0,v))
            except Exception:
                pass

    all_buckets=set(audio_points)|set(motion_points)
    if not all_buckets:
        return {"step":0.5,"audio":[],"peak":[],"motion":[]}

    n=max(all_buckets)+2
    rms_raw=[]
    peak_raw=[]
    motion_raw=[]
    last_rms=-80.0
    last_peak=-80.0
    for i in range(n):
        ap=audio_points.get(i,{})
        r=ap.get("rms",last_rms)
        p=ap.get("peak",last_peak)
        last_rms=r
        last_peak=p
        rms_raw.append(r)
        peak_raw.append(p)
        motion_raw.append(motion_points.get(i,0.0))

    audio=_gsf_norm_series(rms_raw)
    peak=_gsf_norm_series(peak_raw)
    motion=_gsf_norm_series(motion_raw)

    return {"step":0.5,"audio":audio,"peak":peak,"motion":motion}


def _gsf_ai_window_features(scan,start,duration):
    step=float(scan.get("step",0.5) or 0.5)
    a=scan.get("audio",[])
    p=scan.get("peak",[])
    m=scan.get("motion",[])
    n=min(len(a),len(p),len(m))
    if n<=0:
        return {}

    i0=max(0,min(n-1,int(start/step)))
    i1=max(i0+1,min(n,int((start+duration)/step)))
    aa=a[i0:i1]; pp=p[i0:i1]; mm=m[i0:i1]
    if not aa:
        return {}

    def avg(xs): return sum(xs)/len(xs) if xs else 0.0
    def mx(xs): return max(xs) if xs else 0.0

    activity=[0.46*aa[i]+0.44*mm[i]+0.10*min(aa[i],mm[i]) for i in range(len(aa))]
    dead_flags=[1.0 if aa[i]<0.10 and mm[i]<0.07 else 0.0 for i in range(len(aa))]
    burst=[max(0.0,pp[i]-aa[i]) for i in range(len(aa))]
    delta_audio=[0.0]+[max(0.0,aa[i]-aa[i-1]) for i in range(1,len(aa))]
    delta_motion=[0.0]+[max(0.0,mm[i]-mm[i-1]) for i in range(1,len(mm))]

    third=max(1,len(activity)//3)
    s1=activity[:third]
    s2=activity[third:third*2] or activity
    s3=activity[third*2:] or activity[-third:]

    center_peak=mx(s2)
    build=max(0.0,avg(s2)-avg(s1))
    release=max(0.0,avg(s2)-avg(s3))
    arc=min(1.0,0.45*center_peak+0.30*build+0.25*release)

    # Hook: i primi secondi devono contenere abbastanza informazione da non sembrare "morti".
    hook_n=max(1,min(len(activity),int(round(3.0/step))))
    hook_vals=activity[:hook_n]
    hook_score=min(1.0,0.60*avg(hook_vals)+0.40*mx(hook_vals))

    # Dove cade il payoff principale nella clip.
    peak_idx=max(range(len(activity)),key=lambda i:activity[i])
    peak_pos=peak_idx/max(1,len(activity)-1)

    # Un payoff tra ~35% e ~75% della clip tende a lasciare contesto prima e respiro dopo.
    if peak_pos < 0.35:
        payoff_position=max(0.0,peak_pos/0.35)
    elif peak_pos <= 0.75:
        payoff_position=1.0
    else:
        payoff_position=max(0.0,(1.0-peak_pos)/0.25)

    # Penalità più severa per una striscia continua di silenzio/staticità.
    longest_dead=0
    current_dead=0
    for flag in dead_flags:
        if flag:
            current_dead+=1
            longest_dead=max(longest_dead,current_dead)
        else:
            current_dead=0
    dead_streak_ratio=longest_dead/max(1,len(dead_flags))

    # "Reaction cue" audio: scatto improvviso + differenza tra picco e livello medio.
    reaction_curve=[
        min(1.0,0.58*delta_audio[i]+0.42*max(0.0,pp[i]-aa[i]))
        for i in range(len(aa))
    ]

    # Struttura locale attorno al picco: distingue un vero momento
    # da un singolo flash/rumore casuale.
    radius=max(1,int(round(2.0/step)))
    left=max(0,peak_idx-radius)
    right=min(len(activity),peak_idx+radius+1)
    peak_neighborhood=activity[left:right]
    sustained_peak=avg(peak_neighborhood)

    setup_slice=activity[max(0,peak_idx-radius*2):peak_idx]
    aftermath_slice=activity[peak_idx+1:min(len(activity),peak_idx+1+radius*2)]
    setup_score=avg(setup_slice)
    aftermath_score=avg(aftermath_slice)

    # Un picco molto più alto di tutto ciò che lo circonda è spesso
    # un click, una transizione, un colpo singolo o altro falso positivo.
    isolated_spike=max(
        0.0,
        min(1.0,activity[peak_idx]-sustained_peak)
    )

    # Audio alto ma immagine quasi ferma: possibile menu/musica/loading.
    flat_audio_risk=max(
        0.0,
        min(
            1.0,
            avg(aa)
            - 0.70*avg(mm)
            - 0.25*avg([min(aa[i],mm[i]) for i in range(len(aa))])
        )
    )

    continuity=min(
        1.0,
        0.45*sustained_peak+
        0.25*setup_score+
        0.30*aftermath_score
    )

    return {
        "audio_avg":avg(aa),
        "audio_peak":mx(aa),
        "audio_burst":min(1.0,0.55*mx(burst)+0.45*mx(delta_audio)),
        "motion_avg":avg(mm),
        "motion_peak":mx(mm),
        "motion_burst":mx(delta_motion),
        "synergy":avg([min(aa[i],mm[i]) for i in range(len(aa))]),
        "activity_avg":avg(activity),
        "activity_peak":mx(activity),
        "active_ratio":sum(1 for x in activity if x>=0.30)/len(activity),
        "dead_ratio":avg(dead_flags),
        "dead_streak_ratio":dead_streak_ratio,
        "hook_score":hook_score,
        "payoff_position":payoff_position,
        "peak_pos":peak_pos,
        "reaction_cue":mx(reaction_curve),
        "arc":arc,
        "build":build,
        "release":release,
        "center_peak":center_peak,
        "sustained_peak":sustained_peak,
        "setup_score":setup_score,
        "aftermath_score":aftermath_score,
        "isolated_spike":isolated_spike,
        "flat_audio_risk":flat_audio_risk,
        "continuity":continuity,
        "speech":0.0,
        "reaction":0.0,
        "event_score":0.0,
        "event_type":"",
        "event_time":None,
    }



_GSF_IMPORTANT_EVENTS = {
    "goal": {
        "weight": 1.00,
        "patterns": [
            r"\bgo+l+\b", r"\bgoal+\b", r"\bgolazo\b",
            r"\bha segnato\b", r"\bsegna(?:to)?\b", r"\brete\b",
            r"\bequalizer\b", r"\bpareggio\b"
        ],
    },
    "shooter_elimination": {
        "weight": 0.96,
        "patterns": [
            r"\bheadshot\b", r"\bkill(?:ed)?\b", r"\beliminat(?:ed|o|a|i|e|ion)\b",
            r"\buccis[oa]\b", r"\bknock(?:ed)?\b", r"\bdowned\b",
            r"\bsquad wipe\b", r"\bteam wipe\b", r"\bace\b", r"\bclutch\b"
        ],
    },
    "victory": {
        "weight": 0.98,
        "patterns": [
            r"\bvictory\b", r"\bvittoria\b", r"\byou win\b", r"\bwe win\b",
            r"\bhai vinto\b", r"\bwinner\b", r"\bchampion\b", r"\bcampione\b",
            r"\bmission complete\b", r"\bboss defeated\b", r"\bdefeated\b",
            r"\bextraction successful\b", r"\bextracted\b"
        ],
    },
    "sports_big_chance": {
        "weight": 0.78,
        "patterns": [
            r"\brigore\b", r"\bpenalty\b", r"\bparata\b", r"\bsave\b",
            r"\bpalo\b", r"\bpost\b", r"\btraversa\b", r"\bcrossbar\b",
            r"\bvantaggio\b", r"\btakes the lead\b"
        ],
    },
    "racing": {
        "weight": 0.82,
        "patterns": [
            r"\bsorpasso\b", r"\bovertak(?:e|es|ing)\b", r"\bovertook\b",
            r"\bpole position\b", r"\bfastest lap\b", r"\bgiro veloce\b",
            r"\bphoto finish\b", r"\bfinish line\b", r"\bcrash\b", r"\bcollision\b"
        ],
    },
    "achievement": {
        "weight": 0.76,
        "patterns": [
            r"\blevel up\b", r"\brank up\b", r"\bachievement\b",
            r"\btrofeo\b", r"\btrophy\b", r"\bnew record\b",
            r"\bnuovo record\b", r"\bpromozione\b"
        ],
    },
}

def _gsf_detect_important_event(segments, duration):
    best={"type":"","semantic":0.0,"time":None,"text":""}
    for seg in segments or []:
        tx=str(getattr(seg,"text","") or "").strip().lower()
        if not tx:
            continue
        for event_type,cfg in _GSF_IMPORTANT_EVENTS.items():
            hits=0
            for pat in cfg["patterns"]:
                try:
                    if re.search(pat,tx,flags=re.I):
                        hits+=1
                except Exception:
                    pass
            if not hits:
                continue
            semantic=min(1.0,float(cfg["weight"])+0.05*max(0,hits-1))
            try:
                seg_mid=(float(seg.start)+float(seg.end))/2.0
            except Exception:
                seg_mid=float(duration)*0.55
            pos=seg_mid/max(1.0,float(duration))
            if pos<0.05 or pos>0.95:
                semantic*=0.88
            if semantic>best["semantic"]:
                best={"type":event_type,"semantic":semantic,
                      "time":max(0.0,min(float(duration),seg_mid)),
                      "text":tx[:180]}
    return best

def _gsf_event_strength(event,features):
    semantic=float((event or {}).get("semantic",0.0))
    if semantic<=0:
        return 0.0
    audio=float(features.get("audio_peak",0.0))
    burst=float(features.get("audio_burst",0.0))
    motion=float(features.get("motion_peak",0.0))    synergy=float(features.get("synergy",0.0))
    support=0.34*audio+0.26*burst+0.22*motion+0.18*synergy
    return max(0.0,min(1.0,semantic*(0.68+0.32*support)))

def _gsf_ai_voice_features(input_file,start,duration):
    """
    Secondo passaggio SOLO sui candidati migliori.
    Misura parlato, reazione e segnali semantici di eventi importanti.
    """
    wav=None
    try:
        temp_dir=os.path.join(tempfile.gettempdir(),"gsf_ai_voice")
        os.makedirs(temp_dir,exist_ok=True)
        token=hashlib.md5(f"{input_file}|{start:.2f}|{duration:.2f}".encode()).hexdigest()[:14]
        wav=os.path.join(temp_dir,f"{token}.wav")
        cmd=[
            FFMPEG_PATH,"-y","-ss",str(max(0.0,float(start))),"-i",str(input_file),
            "-t",str(max(3.0,float(duration))),"-vn","-ac","1","-ar","16000",
            "-af","highpass=f=70,lowpass=f=7800,loudnorm=I=-16:LRA=11:TP=-1.5",
            wav
        ]
        r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if r.returncode!=0 or not os.path.exists(wav):
            return 0.0,0.0,"",{"type":"","semantic":0.0,"time":None,"text":""}

        model=_gsf_ai_whisper_tiny()
        segs,_=model.transcribe(
            wav,language=None,task="transcribe",vad_filter=True,
            beam_size=2,best_of=2,condition_on_previous_text=False,
            word_timestamps=False,
            initial_prompt=_gsf_gaming_prompt(st.session_state.get("gioco","")),
            vad_parameters=dict(min_silence_duration_ms=220)
        )
        segs=list(segs)
        if not segs:
            return 0.0,0.0,"",{"type":"","semantic":0.0,"time":None,"text":""}

        texts=[]
        spoken=0.0
        for seg in segs:
            tx=str(getattr(seg,"text","") or "").strip()
            if tx:
                texts.append(tx)
            try:
                spoken+=max(0.0,float(seg.end)-float(seg.start))
            except Exception:
                pass

        joined=" ".join(texts)
        words=re.findall(r"[A-Za-zÀ-ÿ']+",joined.lower())
        density=min(1.0,spoken/max(1.0,float(duration))*1.55)
        hits=sum(1 for w in words if w in _GSF_REACTION_WORDS)
        punctuation=joined.count("!")+joined.count("?")
        short_exclamations=sum(1 for tx in texts if 0<len(tx.split())<=5)
        reaction=min(
            1.0,
            hits*0.20+punctuation*0.08+min(0.30,short_exclamations*0.045)
        )
        event=_gsf_detect_important_event(segs,duration)
        return density,reaction,joined,event

    except Exception:
        return 0.0,0.0,"",{"type":"","semantic":0.0,"time":None,"text":""}

    finally:
        if wav:
            try:
                if os.path.exists(wav):
                    os.remove(wav)
            except Exception:
                pass


def _gsf_short_worthiness(features, profile="auto"):
    """
    0..1: quanto questa finestra sembra già una clip completa e pubblicabile,
    non semplicemente un picco statistico.
    """
    f=features or {}

    event=float(f.get("event_score",0.0))
    reaction=max(
        float(f.get("reaction",0.0)),
        float(f.get("reaction_cue",0.0))
    )
    hook=float(f.get("hook_score",0.0))
    payoff=float(f.get("payoff_position",0.0))
    sustained=float(f.get("sustained_peak",0.0))
    setup=float(f.get("setup_score",0.0))
    aftermath=float(f.get("aftermath_score",0.0))
    continuity=float(f.get("continuity",0.0))
    active=float(f.get("active_ratio",0.0))
    synergy=float(f.get("synergy",0.0))
    arc=float(f.get("arc",0.0))
    isolated=float(f.get("isolated_spike",0.0))
    flat_audio=float(f.get("flat_audio_risk",0.0))
    dead=float(f.get("dead_ratio",0.0))
    dead_streak=float(f.get("dead_streak_ratio",0.0))
    motion=float(f.get("motion_avg",0.0))

    if profile=="action":
        core=(
            0.18*continuity+
            0.16*sustained+
            0.14*active+
            0.12*setup+
            0.12*aftermath+
            0.09*hook+
            0.07*payoff+
            0.07*synergy+
            0.05*event
        )
    elif profile=="reaction":
        core=(
            0.20*reaction+
            0.16*aftermath+
            0.13*hook+
            0.12*payoff+
            0.11*continuity+
            0.09*event+
            0.08*sustained+
            0.06*setup+
            0.05*synergy
        )
    elif profile=="director":
        core=(
            0.18*arc+
            0.15*setup+
            0.15*payoff+
            0.14*aftermath+
            0.12*hook+
            0.10*continuity+
            0.07*event+
            0.05*reaction+
            0.04*synergy
        )
    else:
        core=(
            0.13*hook+
            0.13*payoff+
            0.12*continuity+
            0.10*sustained+
            0.10*setup+
            0.10*aftermath+
            0.09*active+
            0.08*event+
            0.06*reaction+
            0.05*arc+
            0.04*synergy
        )

    # Un evento riconosciuto semanticamente può essere valido anche con camera stabile
    # (es. gol in un gioco calcistico), quindi la penalità viene attenuata.
    event_protection=min(0.85,event)
    reaction_protection=min(0.65,reaction)

    false_peak_penalty=isolated*max(
        0.15,
        1.0-0.75*event_protection-0.45*reaction_protection
    )

    # Musica/menu: audio continuo alto, poco movimento, nessun evento/reazione.
    flat_noise_penalty=flat_audio*max(
        0.0,
        1.0-0.80*event-0.55*reaction
    )*max(0.15,1.0-motion)

    dead_penalty=0.55*dead+0.65*dead_streak

    # Bonus se c'è una sequenza leggibile: preparazione -> picco -> conseguenza.
    sequence_bonus=min(
        0.16,
        0.07*min(setup,sustained)+
        0.09*min(sustained,aftermath)
    )

    raw=(
        core+
        sequence_bonus+
        0.10*event+
        0.05*reaction-
        0.34*false_peak_penalty-
        0.24*flat_noise_penalty-
        0.22*dead_penalty
    )

    score=max(0.0,min(1.0,raw))

    return score,{
        "false_peak":max(0.0,min(1.0,false_peak_penalty)),
        "flat_noise":max(0.0,min(1.0,flat_noise_penalty)),
        "sequence":max(0.0,min(1.0,sequence_bonus/0.16 if 0.16 else 0.0)),
    }


def _gsf_score_ai_window(profile,f):
    """Pesi distinti + hook/payoff + eventi importanti + anti-tempo-morto."""
    dead=float(f.get("dead_ratio",0.0))
    dead_streak=float(f.get("dead_streak_ratio",0.0))
    speech=float(f.get("speech",0.0))
    reaction=float(f.get("reaction",0.0))
    hook=float(f.get("hook_score",0.0))
    payoff=float(f.get("payoff_position",0.0))
    reaction_cue=float(f.get("reaction_cue",0.0))
    event_score=float(f.get("event_score",0.0))
    short_score=float(f.get("short_worthiness",0.0))

    if profile=="action":
        score=(
            0.27*f["motion_avg"]+
            0.14*f["motion_peak"]+
            0.12*f["motion_burst"]+
            0.11*f["active_ratio"]+
            0.07*f["audio_avg"]+
            0.07*f["synergy"]+
            0.06*hook+
            0.05*payoff+
            0.09*event_score+
            0.08*short_score-
            0.25*dead-
            0.16*dead_streak
        )
    elif profile=="reaction":
        score=(
            0.22*reaction+
            0.15*speech+
            0.16*f["audio_burst"]+
            0.11*reaction_cue+
            0.07*f["audio_peak"]+
            0.07*f["synergy"]+
            0.03*f["motion_avg"]+
            0.03*hook+
            0.03*payoff+
            0.10*event_score+
            0.08*short_score-
            0.22*dead-
            0.12*dead_streak
        )
    elif profile=="director":
        score=(
            0.21*f["arc"]+
            0.12*f["center_peak"]+
            0.10*f["activity_avg"]+
            0.08*f["synergy"]+
            0.08*f["active_ratio"]+
            0.08*hook+
            0.08*payoff+
            0.06*speech+
            0.04*reaction+
            0.03*f["motion_avg"]+
            0.12*event_score+
            0.10*short_score-
            0.24*dead-
            0.15*dead_streak
        )
    else:
        score=(
            0.14*f["activity_avg"]+
            0.10*f["activity_peak"]+
            0.10*f["motion_avg"]+
            0.08*f["audio_avg"]+
            0.08*f["synergy"]+
            0.07*f["active_ratio"]+
            0.07*hook+
            0.06*payoff+
            0.05*speech+
            0.05*reaction+
            0.04*f["arc"]+
            0.02*reaction_cue+
            0.14*event_score+
            0.10*short_score-
            0.25*dead-
            0.15*dead_streak
        )
    return max(0.0,float(score))


def _gsf_ai_feature_similarity(a,b):
    """
    Similarità 0..1 tra due momenti.
    Serve a non proporre tre clip tecnicamente diverse nel tempo ma identiche nel contenuto.
    """
    keys=[
        "audio_avg","audio_burst","motion_avg","motion_burst",
        "synergy","active_ratio","arc","hook_score",
        "payoff_position","speech","reaction","reaction_cue","event_score",
        "short_worthiness","continuity","sustained_peak"
    ]
    diffs=[]
    for k in keys:
        diffs.append(abs(float(a.get(k,0.0))-float(b.get(k,0.0))))
    return max(0.0,min(1.0,1.0-(sum(diffs)/max(1,len(diffs)))))



_GSF_EVENT_LABELS = {
    "goal": "⚽ GOL",
    "shooter_elimination": "🎯 ELIMINAZIONE",
    "victory": "🏆 VITTORIA",
    "sports_big_chance": "🥅 OCCASIONE",
    "racing": "🏎️ EVENTO GARA",
    "achievement": "⭐ TRAGUARDO",
    "impact_event": "💥 MOMENTO FORTE",
}



def _gsf_detect_signal_event(scan, start, duration):
    """
    Cerca un evento forte anche SENZA trascrizione:
    picco audio + movimento + salto rispetto ai secondi precedenti +
    attività che continua subito dopo.
    """
    step=float(scan.get("step",0.5) or 0.5)
    audio=scan.get("audio",[])
    peak=scan.get("peak",[])
    motion=scan.get("motion",[])
    n=min(len(audio),len(peak),len(motion))

    if n<=0:
        return {"score":0.0,"time":None}

    i0=max(0,min(n-1,int(float(start)/step)))
    i1=max(i0+1,min(n,int((float(start)+float(duration))/step)))
    if i1-i0<3:
        return {"score":0.0,"time":None}

    best_score=0.0
    best_time=None
    pre_n=max(1,int(round(2.0/step)))
    post_n=max(1,int(round(3.0/step)))

    for idx in range(i0,i1):
        local=idx-i0

        a=float(audio[idx])
        p=float(peak[idx])
        m=float(motion[idx])
        instant=0.38*a+0.34*m+0.18*p+0.10*min(a,m)

        pre0=max(i0,idx-pre_n)
        pre_vals=[
            0.50*float(audio[j])+0.50*float(motion[j])
            for j in range(pre0,idx)
        ]
        pre_avg=sum(pre_vals)/len(pre_vals) if pre_vals else 0.0

        post1=min(i1,idx+post_n+1)
        post_vals=[
            0.46*float(audio[j])+0.42*float(motion[j])+0.12*float(peak[j])
            for j in range(idx+1,post1)
        ]
        post_avg=sum(post_vals)/len(post_vals) if post_vals else 0.0

        surge=max(0.0,instant-pre_avg)
        synergy=min(a,m)

        # Un vero evento tende ad avere un picco + un cambio rispetto al prima
        # e spesso mantiene attività per qualche secondo dopo.
        score=(
            0.38*instant+
            0.24*surge+
            0.18*post_avg+
            0.12*synergy+
            0.08*m
        )

        # Evita di chiamare evento una zona semplicemente rumorosa ma piatta.
        if surge<0.10 and instant<0.70:
            score*=0.72

        if score>best_score:
            best_score=score
            best_time=local*step

    return {
        "score":max(0.0,min(1.0,best_score)),
        "time":best_time
    }


def _gsf_merge_semantic_and_signal_event(event, signal_event, features):
    """
    Combina significato (Whisper) e firma audio/video.
    Se manca la voce ma il segnale è molto forte, crea un 'impact_event'.
    """
    event=event or {"type":"","semantic":0.0,"time":None,"text":""}
    signal_event=signal_event or {"score":0.0,"time":None}

    semantic_strength=_gsf_event_strength(event,features)
    signal_strength=float(signal_event.get("score",0.0))
    semantic_time=event.get("time")
    signal_time=signal_event.get("time")

    event_type=str(event.get("type","") or "")
    final_time=semantic_time
    final_score=semantic_strength

    if semantic_strength>0 and signal_strength>0:
        close=True
        if semantic_time is not None and signal_time is not None:
            close=abs(float(semantic_time)-float(signal_time))<=4.0

        if close:
            final_score=min(1.0,semantic_strength+0.18*signal_strength)
        else:
            final_score=max(semantic_strength,signal_strength*0.78)

    elif semantic_strength<=0 and signal_strength>=0.64:
        event_type="impact_event"
        final_time=signal_time
        final_score=min(0.86,signal_strength*0.94)

    return {
        "type":event_type,
        "score":max(0.0,min(1.0,float(final_score))),
        "time":final_time,
        "signal_score":signal_strength,
        "semantic_score":semantic_strength,
    }


def _gsf_moment_category(features):
    """Categoria sintetica usata per aumentare la varietà dei 3 risultati."""
    f=features or {}

    if float(f.get("event_score",0.0))>=0.56:
        return "event"
    if (
        float(f.get("reaction",0.0))>=0.34
        or float(f.get("reaction_cue",0.0))>=0.66
        or float(f.get("audio_burst",0.0))>=0.78
    ):
        return "reaction"
    if (
        float(f.get("motion_avg",0.0))>=0.52
        or float(f.get("motion_burst",0.0))>=0.68
    ):
        return "action"
    if float(f.get("arc",0.0))>=0.52:
        return "story"
    return "balanced"


def _gsf_event_target_position(event_type, reaction=0.0, event_score=0.0):
    """
    Posizione ideale dell'evento nello Short.
    Più serve vedere la reazione dopo, più spostiamo l'evento verso il centro.
    """
    base = {
        "goal": 0.58,
        "sports_big_chance": 0.58,
        "victory": 0.54,
        "shooter_elimination": 0.64,
        "racing": 0.58,
        "achievement": 0.55,
        "impact_event": 0.60,
    }.get(str(event_type or ""), 0.60)

    # Una reazione forte merita qualche secondo in più DOPO l'evento.
    reaction_pull = min(0.07, max(0.0, float(reaction)) * 0.06)
    strength_pull = min(0.025, max(0.0, float(event_score) - 0.70) * 0.08)
    return max(0.48, min(0.68, base - reaction_pull - strength_pull))


def _gsf_smart_event_start(scan, event_abs, duration, event_type, total,
                           reaction=0.0, event_score=0.0):
    """
    Cerca il miglior IN attorno all'evento, preservando:
    - contesto prima;
    - evento chiaramente dentro la clip;
    - spazio dopo per esultanza/reazione/conseguenza;
    - hook non morto all'inizio.
    """
    duration = max(5.0, float(duration))
    total = max(duration, float(total))
    event_abs = max(0.0, min(float(total), float(event_abs)))
    target = _gsf_event_target_position(event_type, reaction, event_score)

    candidate_positions = [
        max(0.44, min(0.72, target + delta))
        for delta in (-0.08, -0.04, 0.0, 0.04, 0.08)
    ]

    best = None
    max_start = max(0.0, total - duration)

    for pos in candidate_positions:
        start = event_abs - duration * pos
        start = max(0.0, min(max_start, start))

        actual_pos = (event_abs - start) / max(1.0, duration)
        if actual_pos < 0.34 or actual_pos > 0.82:
            continue

        f = _gsf_ai_window_features(scan, start, duration)
        if not f:
            continue

        placement = max(0.0, 1.0 - abs(actual_pos - target) / 0.24)
        post_room = max(0.0, (start + duration - event_abs) / duration)
        aftermath = min(1.0, post_room / 0.34)

        context = (
            0.23 * float(f.get("hook_score", 0.0)) +
            0.18 * float(f.get("active_ratio", 0.0)) +
            0.14 * float(f.get("activity_avg", 0.0)) +
            0.12 * float(f.get("arc", 0.0)) +
            0.10 * float(f.get("synergy", 0.0)) +
            0.12 * (1.0 - float(f.get("dead_streak_ratio", 0.0))) +
            0.11 * (1.0 - float(f.get("dead_ratio", 0.0)))
        )

        utility = 0.58 * context + 0.27 * placement + 0.15 * aftermath

        if best is None or utility > best[0]:
            best = (utility, start, actual_pos)

    if best is None:
        fallback = max(0.0, min(max_start, event_abs - duration * target))
        return fallback, target

    return float(best[1]), float(best[2])


def _gsf_same_physical_event(item_a, item_b, duration):
    """Decide se due finestre descrivono probabilmente lo stesso evento reale."""
    _, _, fa, _ = item_a
    _, _, fb, _ = item_b

    ea = fa.get("event_abs")
    eb = fb.get("event_abs")
    sa = float(fa.get("event_score", 0.0))
    sb = float(fb.get("event_score", 0.0))

    if ea is None or eb is None or sa < 0.56 or sb < 0.56:
        return False

    delta = abs(float(ea) - float(eb))
    ta = str(fa.get("event_type", "") or "")
    tb = str(fb.get("event_type", "") or "")

    # Stesso tipo entro pochi secondi: quasi certamente la stessa azione
    # vista da finestre sovrapposte.
    same_type_window = max(2.5, min(6.0, float(duration) * 0.26))
    if ta and ta == tb and delta <= same_type_window:
        return True

    # Due etichette diverse ma praticamente allo stesso istante
    # (es. goal + victory) appartengono comunque allo stesso momento.
    if delta <= 1.5:
        return True

    return False


def _gsf_collapse_event_duplicates(enriched, duration):
    """
    Tiene una sola rappresentazione del medesimo gol/kill/vittoria,
    scegliendo la finestra col punteggio più alto.
    """
    ordered = sorted(enriched, key=lambda x: float(x[0]), reverse=True)
    kept = []

    for item in ordered:
        if any(_gsf_same_physical_event(item, old, duration) for old in kept):
            continue
        kept.append(item)

    return kept


def _gsf_ai_pick_diverse(enriched,duration,numero_clip):
    """
    Ranking finale tipo MMR:
    qualità prima, poi penalità se una nuova clip assomiglia troppo a una già scelta.
    """
    if not enriched:
        return []

    best_score=max(float(x[0]) for x in enriched) or 1.0
    # Non sacrifichiamo la qualità solo per essere diversi.
    quality_floor=best_score*0.55
    pool=[
        x for x in enriched
        if float(x[0])>=quality_floor
        or float((x[2] or {}).get("event_score",0.0))>=0.68
    ]
    if len(pool)<numero_clip:
        pool=list(enriched)

    chosen=[]
    remaining=list(pool)

    while remaining and len(chosen)<int(numero_clip):
        if not chosen:
            pick=max(remaining,key=lambda x:x[0])
        else:
            def utility(item):
                score,start,f,transcript=item
                worst_similarity=0.0
                worst_overlap=0.0
                for old_score,old_start,old_f,old_transcript in chosen:
                    worst_similarity=max(
                        worst_similarity,
                        _gsf_ai_feature_similarity(f,old_f)
                    )
                    gap=abs(float(start)-float(old_start))
                    overlap=max(0.0,1.0-gap/max(1.0,float(duration)))
                    worst_overlap=max(worst_overlap,overlap)

                chosen_categories={
                    _gsf_moment_category(old_f)
                    for _,_,old_f,_ in chosen
                }
                this_category=_gsf_moment_category(f)
                category_bonus=0.055 if this_category not in chosen_categories else -0.015
                short_bonus=0.08*float(f.get("short_worthiness",0.0))
                false_peak_penalty=0.08*float(f.get("false_peak_penalty",0.0))

                # Similarità contenuto pesa meno dell'overlap temporale.
                return (
                    float(score)
                    -0.10*worst_similarity
                    -0.24*worst_overlap
                    +category_bonus
                    +short_bonus
                    -false_peak_penalty
                )

            pick=max(remaining,key=utility)

        chosen.append(pick)
        remaining.remove(pick)

    return chosen


def _gsf_profile_from_mode(modalita):
    return {
        "🚀 AUTO TOTALE":"auto",
        "🎬 AI Director":"director",
        "🧠 Smart Clip":"action",
        "🤖 Auto Clip":"reaction",
    }.get(modalita,"auto")


def _gsf_ai_rank_v3(input_file, modalita, clip_duration=15, numero_clip=3, cache_token=None):
    """
    Fast Scan -> shortlist diversa per profilo -> voice check mirato -> ranking finale.
    Restituisce [(score,start), ...] + diagnostica per eventuali sviluppi futuri.
    """
    _analysis_t0=time.perf_counter()
    profile=_gsf_profile_from_mode(modalita)
    duration=max(10.0,float(clip_duration))
    scan,scan_cache_hit=_gsf_ai_scan_cached(
        input_file,cache_token=cache_token
    )
    voice_cache_hits=0
    voice_checks=0
    n=min(len(scan.get("audio",[])),len(scan.get("motion",[])))
    step=float(scan.get("step",0.5) or 0.5)
    total=n*step
    if n<=0 or total<5:
        return [],{}

    # Ogni 1 secondo: qualità migliore senza moltiplicare troppo il lavoro.
    candidates=[]
    last_start=max(0,int(total-max(5.0,duration)))
    for start in range(0,last_start+1):
        f=_gsf_ai_window_features(scan,float(start),duration)
        if not f:
            continue

        # Prima fase NON usa Whisper.
        if profile=="reaction":
            prelim=(
                0.31*f["audio_burst"]+0.18*f["audio_peak"]+
                0.16*f["reaction_cue"]+0.13*f["synergy"]+
                0.08*f["activity_peak"]+0.06*f["motion_avg"]+
                0.04*f["hook_score"]+0.04*f["payoff_position"]-
                0.22*f["dead_ratio"]-0.12*f["dead_streak_ratio"]
            )
        elif profile=="action":
            prelim=_gsf_score_ai_window("action",f)
        elif profile=="director":
            prelim=(
                0.30*f["arc"]+0.16*f["center_peak"]+
                0.14*f["activity_avg"]+0.11*f["synergy"]+
                0.10*f["active_ratio"]+0.09*f["hook_score"]+
                0.10*f["payoff_position"]-0.22*f["dead_ratio"]-
                0.14*f["dead_streak_ratio"]
            )
        else:
            prelim=(
                0.23*f["activity_avg"]+0.15*f["activity_peak"]+
                0.14*f["motion_avg"]+0.11*f["audio_avg"]+
                0.10*f["synergy"]+0.08*f["arc"]+
                0.07*f["active_ratio"]+0.06*f["hook_score"]+
                0.06*f["payoff_position"]-0.23*f["dead_ratio"]-
                0.14*f["dead_streak_ratio"]
            )
        candidates.append((float(prelim),float(start),f))

    if not candidates:
        return [],{}

    candidates.sort(key=lambda x:x[0],reverse=True)

    # Shortlist con un po' di diversità. Non aspettiamo il ranking finale per evitare
    # di mandare a Whisper dieci finestre quasi identiche dello stesso combattimento.
    shortlist=[]
    shortlist_target=10 if profile in ("auto","director","reaction") else 8
    min_gap=max(3.0,duration*0.35)
    for item in candidates:
        if any(abs(item[1]-x[1])<min_gap for x in shortlist):
            continue
        shortlist.append(item)
        if len(shortlist)>=shortlist_target:
            break

    # Voice/reaction/event detection SOLO sulla shortlist.
    enriched=[]
    diagnostics={}
    for prelim,start,f in shortlist:
        f=dict(f)
        transcript=""
        _voice_result,_voice_hit=_gsf_ai_voice_cached(
            input_file,start,duration,cache_token=cache_token
        )
        speech,reaction,transcript,event=_voice_result
        voice_checks+=1
        if _voice_hit:
            voice_cache_hits+=1
        f["speech"]=speech
        f["reaction"]=reaction
        signal_event=_gsf_detect_signal_event(
            scan,start,duration
        )
        merged_event=_gsf_merge_semantic_and_signal_event(
            event,signal_event,f
        )

        f["event_type"]=str(merged_event.get("type","") or "")
        f["event_time"]=merged_event.get("time")
        f["event_score"]=float(merged_event.get("score",0.0))
        f["event_signal_score"]=float(merged_event.get("signal_score",0.0))
        f["event_semantic_score"]=float(merged_event.get("semantic_score",0.0))
        f["event_abs"]=None
        f["event_position"]=None
        f["moment_category"]=_gsf_moment_category(f)

        short_worthiness,short_diag=_gsf_short_worthiness(f,profile)
        f["short_worthiness"]=short_worthiness
        f["false_peak_penalty"]=float(short_diag.get("false_peak",0.0))
        f["flat_noise_penalty"]=float(short_diag.get("flat_noise",0.0))
        f["sequence_score"]=float(short_diag.get("sequence",0.0))

        score=_gsf_score_ai_window(profile,f)

        # Se è soltanto un picco isolato e non è confermato da evento/reazione,
        # lo abbassiamo nettamente: è il falso positivo tipico.
        if (
            f["false_peak_penalty"]>=0.45
            and f["event_score"]<0.56
            and f["reaction"]<0.28
        ):
            score*=0.72

        # Audio piatto/forte con immagine quasi ferma: probabile menu/loading/musica.
        if (
            f["flat_noise_penalty"]>=0.45
            and f["event_score"]<0.56
        ):
            score*=0.78
        adjusted_start=start

        if f["event_score"]>=0.56 and f.get("event_time") is not None:
            event_abs=float(start)+float(f["event_time"])
            f["event_abs"]=event_abs

            adjusted_start,event_position=_gsf_smart_event_start(
                scan,
                event_abs,
                duration,
                f["event_type"],
                total,
                reaction=f.get("reaction",0.0),
                event_score=f.get("event_score",0.0)
            )
            f["event_position"]=event_position

        elif profile=="reaction" and (f["reaction"]>0.12 or f["audio_burst"]>0.55):
            adjusted_start=max(0.0,start-1.5)

        enriched.append((score,adjusted_start,f,transcript))

    enriched.sort(key=lambda x:x[0],reverse=True)

    # Prima eliminiamo le finestre duplicate dello stesso evento fisico.
    enriched=_gsf_collapse_event_duplicates(enriched,duration)

    # Poi scegliamo tre momenti realmente diversi.
    diverse=_gsf_ai_pick_diverse(enriched,duration,numero_clip)

    chosen=[]
    for score,start,f,transcript in diverse:
        chosen.append((float(score),float(start)))
        diagnostics[round(float(start),3)]={
            "profile":profile,
            "score":float(score),
            "features":f,
            "transcript":transcript,
            "why":{
                "hook":round(float(f.get("hook_score",0.0)),3),
                "payoff":round(float(f.get("payoff_position",0.0)),3),
                "dead_streak":round(float(f.get("dead_streak_ratio",0.0)),3),
                "reaction_cue":round(float(f.get("reaction_cue",0.0)),3),
                "event":str(f.get("event_type","") or ""),
                "event_score":round(float(f.get("event_score",0.0)),3),
                "event_position":(
                    round(float(f.get("event_position")),3)
                    if f.get("event_position") is not None else None
                ),
                "event_signal":round(float(f.get("event_signal_score",0.0)),3),
                "event_semantic":round(float(f.get("event_semantic_score",0.0)),3),
                "category":str(f.get("moment_category","") or ""),
                "short_worthiness":round(float(f.get("short_worthiness",0.0)),3),
                "false_peak":round(float(f.get("false_peak_penalty",0.0)),3),
                "flat_noise":round(float(f.get("flat_noise_penalty",0.0)),3),
                "sequence":round(float(f.get("sequence_score",0.0)),3),
            }
        }

    diagnostics["__meta__"]={
        "engine":GSF_AI_ENGINE_VERSION,
        "analysis_seconds":round(time.perf_counter()-_analysis_t0,3),
        "scan_cache_hit":bool(scan_cache_hit),
        "voice_cache_hits":int(voice_cache_hits),
        "voice_checks":int(voice_checks),
        "video_seconds":round(float(total),2),
    }

    return chosen,diagnostics


def rifinisci_confini_clip(input_file, centro_start, durata_target):
    """
    Rifinisce gratis inizio/fine della clip usando silenzio audio.
    Cerca un punto naturale vicino ai bordi senza allungare troppo.
    """
    margine = 8.0
    analisi_start = max(0.0, centro_start - margine)
    analisi_durata = durata_target + margine * 2

    cmd = [
        FFMPEG_PATH, "-hide_banner",
        "-ss", str(analisi_start),
        "-i", input_file,
        "-t", str(analisi_durata),
        "-vn",
        "-af", "silencedetect=noise=-36dB:d=0.35",
        "-f", "null", "-"
    ]

    r = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    log = (r.stdout or "") + "\n" + (r.stderr or "")
    silenzi = []
    current = None

    for line in log.splitlines():
        ms = re.search(r"silence_start:\s*([0-9.]+)", line)
        if ms:
            current = float(ms.group(1))

        me = re.search(r"silence_end:\s*([0-9.]+)", line)
        if me and current is not None:
            silenzi.append((current, float(me.group(1))))
            current = None

    originale_start_rel = centro_start - analisi_start
    originale_end_rel = originale_start_rel + durata_target

    nuovo_start_rel = originale_start_rel
    nuovo_end_rel = originale_end_rel

    # Cerca una fine di silenzio poco prima/dopo dell'inizio:
    # partire dopo un silenzio tende a dare un hook più pulito.
    candidati_start = []
    for s0, s1 in silenzi:
        distanza = abs(s1 - originale_start_rel)
        if distanza <= 5.0:
            candidati_start.append((distanza, s1))

    if candidati_start:
        nuovo_start_rel = min(candidati_start)[1]

    # Cerca un inizio di silenzio vicino alla fine:
    # chiudere prima del silenzio elimina code morte.
    candidati_end = []
    for s0, s1 in silenzi:
        distanza = abs(s0 - originale_end_rel)
        if distanza <= 6.0 and s0 > nuovo_start_rel + 8:
            candidati_end.append((distanza, s0))

    if candidati_end:
        nuovo_end_rel = min(candidati_end)[1]

    nuovo_start = max(0.0, analisi_start + nuovo_start_rel)
    nuovo_end = max(
        nuovo_start + 8.0,
        analisi_start + nuovo_end_rel
    )

    # Evita clip eccessivamente lunghe.
    if nuovo_end - nuovo_start > durata_target + 8:
        nuovo_end = nuovo_start + durata_target + 8

    return nuovo_start, nuovo_end - nuovo_start



def mostra_risultati_v2(items, titolo="✨ Le tue clip sono pronte"):
    """UI semplice per preview, modifica e download delle clip generate."""
    if not items:
        return

    st.markdown(
        f"""
        <div class="results-head">
          <h2>{titolo}</h2>
          <p>Guarda il risultato, scaricalo oppure mandalo all’Editor.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    for i, item in enumerate(items, start=1):
        path = item.get("path")
        if not path or not os.path.exists(path):
            continue

        start = float(item.get("start", 0.0))
        duration = float(item.get("duration", 0.0))
        end = start + duration

        st.markdown(
            f"""
            <div class="result-wrap">
              <span class="result-badge">✦ MOMENTO {i}</span>
              <div class="result-title">Short #{i}</div>
              <div class="result-time">{start:.1f}s → {end:.1f}s • {duration:.1f}s</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        render_gsf_player(path, f"result_v2_{i}")

        b1, b2 = st.columns(2)

        with b1:
            if st.button(
                "✂️ MODIFICA",
                key=f"result_edit_{i}",
                use_container_width=True
            ):
                st.session_state["editor_result_path"] = path
                st.session_state["apri_editor_risultato"] = True
                st.session_state["manual_start_editor"] = start
                st.session_state["manual_duration_editor"] = duration
                st.info(
                    "✂️ Clip inviata all’Editor. "
                    "Apri l’Editor video sopra per modificarla."
                )

        with b2:
            with open(path, "rb") as rf:
                result_bytes = rf.read()

            st.download_button(
                "⬇️ SCARICA",
                data=result_bytes,
                file_name=f"GamingShort_{i}.mp4",
                mime="video/mp4",
                key=f"result_download_{i}",
                use_container_width=True
            )


    st.markdown(
        """
        <div class="gsf-hero">
          <div class="gsf-orb">✦</div>          <h1>Cosa vuoi creare oggi?</h1>
          <p>Carica il gameplay. Al resto può pensare la tua Gaming Shorts Factory.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="gsf-step">① CARICA IL VIDEO</div>', unsafe_allow_html=True)
video = st.file_uploader(
    "🎬 Carica il gameplay",
    type=["mp4", "mov", "mkv"]
)



def _gsf_windows_fonts():
    """Font Windows disponibili; fallback sicuro se il registro non è leggibile."""
    fallback=["Arial","Arial Black","Calibri","Cambria","Candara","Comic Sans MS",
              "Consolas","Georgia","Impact","Segoe UI","Tahoma","Times New Roman",
              "Trebuchet MS","Verdana"]
    names=set(fallback)
    if os.name=="nt":
        try:
            import winreg
            key=winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
            )
            i=0
            while True:
                try:
                    name,_,_=winreg.EnumValue(key,i); i+=1
                    clean=re.sub(r"\s*\((TrueType|OpenType|All res)\)\s*$","",str(name),flags=re.I).strip()
                    if clean:
                        for part in clean.split(" & "): names.add(part.strip())
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass
    return sorted(names,key=str.casefold)

def _gsf_sync_main_subtitle_font():
    v=st.session_state.get("editor_sub_font_v18")
    if v:
        st.session_state["subtitle_font"]=v

def _gsf_sync_inline_subtitle_font(widget_key, state_key):
    v=st.session_state.get(widget_key)
    if v:
        st.session_state[state_key]=v

def _gsf_live_signature(*values):
    """Short signature used to rebuild the LIVE iframe when editor controls change."""
    raw="|".join(str(v) for v in values)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:10]


# ==========================================================
# V25 — PERSISTENT LIVE PLAYER (Streamlit Components V2)
# ==========================================================
_GSF_LIVE_V2 = None
if hasattr(st, "components") and hasattr(st.components, "v2") and hasattr(st.components.v2, "component"):
    _GSF_LIVE_V2 = st.components.v2.component(
        "gaming_shorts_factory.live_editor_v25",
        html="""
        <div class="gsf-live-stage">
          <div class="gsf-live-viewport">
            <div class="gsf-live-badge">LIVE</div>
            <video class="gsf-live-video" controls preload="metadata" playsinline></video>
            <div class="gsf-live-subs"></div>
          </div>
        </div>
        """,
        css="""
        .gsf-live-stage{width:100%;display:flex;justify-content:flex-start}
        .gsf-live-viewport{position:relative;overflow:hidden;border-radius:18px;background:#000;
          box-shadow:0 14px 34px rgba(16,40,61,.14)}
        .gsf-live-video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:center}
        .gsf-live-badge{position:absolute;z-index:4;left:10px;top:10px;padding:5px 9px;border-radius:999px;
          background:rgba(0,0,0,.62);color:#fff;font:600 12px Arial;pointer-events:none}
        .gsf-live-subs{position:absolute;z-index:5;width:88%;text-align:center;line-height:1.05;
          transform:translate(-50%,-50%);pointer-events:none;padding:2px 4px}
        .gsf-live-subs .active{display:inline-block;transform:scale(1.10)}
        """,
        js=r"""
        export default function(component) {
          const { parentElement, data } = component;
          const v = parentElement.querySelector(".gsf-live-video");
          const vp = parentElement.querySelector(".gsf-live-viewport");
          const badge = parentElement.querySelector(".gsf-live-badge");
          const box = parentElement.querySelector(".gsf-live-subs");
          if (!v || !vp || !box) return;

          const d = data || {};
          const src = d.url || "";
          const srcChanged = v.dataset.src !== src;

          if (srcChanged) {
            v.dataset.src = src;
            v.src = src;
            v.load();
            v.dataset.clipStart = "";
            v.dataset.seekNonce = "";
          }

          const vertical = d.format === "9:16 Short";
          const fw = vertical ? 220 : 480;
          const fh = vertical ? 391 : 270;
          vp.style.width = fw + "px";
          vp.style.height = fh + "px";
          vp.style.maxWidth = "96vw";
          badge.textContent = "LIVE · " + (d.format || "");

          const zoom = Number(d.zoom ?? 1);
          const tx = Number(d.x ?? 0) * .35;
          const ty = Number(d.y ?? 0) * .35;
          v.style.transform = `translate(${tx}%, ${ty}%) scale(${zoom})`;
          v.style.filter = `brightness(${Math.max(0,1+Number(d.brightness ?? 0))}) contrast(${Math.max(0,Number(d.contrast ?? 1))})`;
          v.volume = Math.max(0,Math.min(1,Number(d.volume ?? 100)/100));
          v.playbackRate = Number(d.speed ?? 1);

          const clipStart = Math.max(0,Number(d.clipStart ?? 0));
          const clipEnd = Math.max(clipStart,Number(d.clipEnd ?? clipStart));
          const timelineToken = `${clipStart.toFixed(3)}|${clipEnd.toFixed(3)}`;

          function seekTo(t) {
            if (!Number.isFinite(t)) return;
            const go = () => {
              let target = Math.max(0,t);
              if (Number.isFinite(v.duration) && v.duration > 0) {
                target = Math.min(target, Math.max(0,v.duration-.03));
              }
              try {
                v.currentTime = target;
                // Some browsers need the media to become seekable first.
                setTimeout(() => {
                  if (Math.abs(v.currentTime-target) > .25 && v.seekable && v.seekable.length) {
                    try { v.currentTime = target; } catch(e) {}
                  }
                }, 120);
              } catch(e) {}
            };
            if (v.readyState >= 1) go();
            else v.addEventListener("loadedmetadata", go, {once:true});
          }

          // Timeline is authoritative: changing IN/OUT seeks to the new IN once.
          if (v.dataset.clipStart !== timelineToken) {
            v.dataset.clipStart = timelineToken;
            seekTo(clipStart);
          }

          // RESET TUTTO: reset del componente senza ricaricare la sorgente video.
          const resetId = String(d.resetId ?? "");
          if (resetId && v.dataset.resetId !== resetId) {
            v.dataset.resetId = resetId;
            v.dataset.seekNonce = "";
            try { v.pause(); } catch(e) {}
            seekTo(clipStart);
          }

          // VAI è un evento, non uno stato: ogni nonce nuovo esegue UN seek sullo stesso <video>.
          const seekNonce = String(d.seekNonce ?? "");
          if (seekNonce && v.dataset.seekNonce !== seekNonce) {
            v.dataset.seekNonce = seekNonce;
            const requested = Number(d.seekTarget);
            if (Number.isFinite(requested)) seekTo(requested);
          }

          const words = Array.isArray(d.words) ? d.words : [];
          const fallback = String(d.subtitleText ?? "");
          box.style.display = d.subtitlesOn ? "block" : "none";
          box.style.left = `${Math.max(5,Math.min(95,Number(d.subtitleX ?? 50)))}%`;
          box.style.top = `${Math.max(5,Math.min(95,Number(d.subtitleY ?? 78)))}%`;
          box.style.color = d.textColor || "#FFFFFF";
          box.style.fontFamily = `"${String(d.font || "Arial").replaceAll('"','')}", Arial, sans-serif`;
          box.style.fontSize = `${Math.max(13,Math.min(48,Number(d.liveFont ?? 20)))}px`;
          box.style.fontWeight = "800";
          const outline = d.outlineColor || "#000000";
          box.style.textShadow = `-2px -2px 0 ${outline},2px -2px 0 ${outline},-2px 2px 0 ${outline},2px 2px 0 ${outline},0 3px 7px rgba(0,0,0,.55)`;

          function esc(s) {
            return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));
          }
          function renderSubs() {
            if (!d.subtitlesOn) { box.innerHTML=""; return; }
            const t = v.currentTime;
            if (words.length) {
              let idx = words.findIndex(w=>t>=Number(w.start)-.06 && t<=Number(w.end)+.10);
              if (idx < 0) {
                idx = words.findIndex(w=>t<Number(w.start));
                if (idx < 0) idx=words.length-1; else if (idx>0) idx-=1;
              }
              const base=Math.floor(idx/4)*4, group=words.slice(base,base+4);
              const active=d.activeColor || "#FFD400";
              box.innerHTML=group.map((w,j)=>j===idx-base
                ? `<span class="active" style="color:${active}">${esc(w.text)}</span>`
                : esc(w.text)).join(" ");
            } else {
              box.textContent=fallback || "ANTEPRIMA SOTTOTITOLI";
            }
          }

          // Bind listeners only once. They read latest config from element properties/data on each V2 render.
          if (!v.dataset.gsfBound) {
            v.dataset.gsfBound="1";
            v.addEventListener("timeupdate", () => {
              const latest = v._gsfRenderSubs;
              if (latest) latest();
              const end = Number(v._gsfClipEnd ?? 0);
              const start = Number(v._gsfClipStart ?? 0);
              if (end > start && v.currentTime >= end) {
                v.pause();
                try { v.currentTime = start; } catch(e) {}
                if (latest) latest();
              }
            });
            v.addEventListener("seeked", () => v._gsfRenderSubs && v._gsfRenderSubs());
            v.addEventListener("play", () => {
              const start = Number(v._gsfClipStart ?? 0), end=Number(v._gsfClipEnd ?? 0);
              if (end>start && (v.currentTime < start || v.currentTime >= end)) seekTo(start);
            });
          }
          v._gsfClipStart=clipStart;
          v._gsfClipEnd=clipEnd;
          v._gsfRenderSubs=renderSubs;
          renderSubs();
        }
        """
    )



def _gsf_reset_main_tools():
    defaults={
        "editor_zoom":1.0,"editor_x":0,"editor_y":0,"editor_volume":100,
        "editor_brightness":0.0,"editor_contrast":1.0,"editor_speed":1.0
    }
    for k,v in defaults.items(): st.session_state[k]=v

def _gsf_reset_main_subtitles():
    defaults={
        "subtitle_font":"Arial","editor_sub_font_v18":"Arial",
        "editor_sub_size":92,"editor_sub_size_v18":92,
        "subtitle_text_color":"#FFFFFF","subtitle_text_color_v18":"#FFFFFF",
        "subtitle_active_color":"#FFD400","subtitle_active_color_v18":"#FFD400",
        "subtitle_outline_color":"#000000","subtitle_outline_color_v18":"#000000",
        "subtitle_x":50,"subtitle_x_v18":50,"subtitle_y":78,"subtitle_y_v18":78
    }
    for k,v in defaults.items(): st.session_state[k]=v

def _gsf_reset_inline_tools(i, fmt_key, zoom_key, x_key, y_key, vol_key, bri_key, con_key, spd_key):
    for k,v in {
        zoom_key:1.0,x_key:0,y_key:0,vol_key:100,bri_key:0.0,con_key:1.0,spd_key:1.0
    }.items(): st.session_state[k]=v

def _gsf_reset_inline_subtitles(i):
    defaults={
        f"inline_font_{i}":"Arial",f"inline_font_widget_v18_{i}":"Arial",
        f"inline_subsize_{i}":92,f"inline_subsize_widget_v18_{i}":92,
        f"inline_txtcol_v18_{i}":"#FFFFFF",f"inline_actcol_v18_{i}":"#FFD400",
        f"inline_outcol_v18_{i}":"#000000",
        f"inline_subx_{i}":50,f"inline_subx_widget_v18_{i}":50,
        f"inline_suby_{i}":78,f"inline_suby_widget_v18_{i}":78
    }
    for k,v in defaults.items(): st.session_state[k]=v

def _gsf_reset_main_all():
    # Strumenti / immagine / audio
    _gsf_reset_main_tools()
    _gsf_reset_main_subtitles()

    # Timeline: torna ai limiti originali conosciuti della clip/video.
    if "editor_original_start" in st.session_state:
        st.session_state["editor_start"]=st.session_state["editor_original_start"]
    if "editor_original_end" in st.session_state:
        st.session_state["editor_end"]=st.session_state["editor_original_end"]

    # Sottotitoli / trascrizione: reset completo.
    for k in [
        "editor_sub_words","editor_sub_live_words","editor_sub_text",
        "editor_sub_applied_text","editor_sub_text_area_v18",
        "editor_sub_seek","editor_sub_seek_feedback","editor_sub_seek_nonce",
        "editor_time_nav_v22"
    ]:
        st.session_state.pop(k,None)

    # Torna alla modalità sottotitoli iniziale se il relativo widget esiste.
    for k in ["editor_sub_mode","editor_sub_mode_v18"]:
        st.session_state.pop(k,None)

    # Evento di reset per il componente persistente.
    st.session_state["editor_reset_id"]=int(st.session_state.get("editor_reset_id",0))+1

def _gsf_reset_inline_all(i, fmt_key, zoom_key, x_key, y_key, vol_key, bri_key, con_key, spd_key):
    _gsf_reset_inline_tools(i,fmt_key,zoom_key,x_key,y_key,vol_key,bri_key,con_key,spd_key)
    _gsf_reset_inline_subtitles(i)

    # Rimuove ogni modifica della trascrizione e del seek della clip AI.
    prefixes=[
        f"inline_trans_words_{i}",f"inline_trans_live_{i}",f"inline_trans_text_{i}",
        f"inline_applied_text_{i}",f"inline_seek_{i}",f"inline_seek_feedback_{i}",
        f"inline_seek_nonce_{i}",f"inline_time_nav_v22_{i}"
    ]
    for k in prefixes:
        st.session_state.pop(k,None)

    st.session_state[f"inline_reset_id_{i}"]=int(st.session_state.get(f"inline_reset_id_{i}",0))+1

def render_gsf_editor_live_player(
    source_path, key, start_seconds, fmt, zoom, x_pos, y_pos,
    volume, brightness, contrast, speed,
    subtitles_on=False, subtitle_style="Gaming",
    subtitle_size=92, subtitle_position=330,
    subtitle_words=None, subtitle_text="",
    subtitle_font="Arial", subtitle_x=50, subtitle_y=78,
    end_seconds=None, seek_target=None, seek_nonce=0, reset_id=0, clip_start_override=None,
    text_color=None, active_color=None, outline_color=None
):
    """Persistent V2 live preview. Falls back to the legacy iframe on older Streamlit."""
    source_path=Path(source_path)
    if not source_path.exists():
        st.warning("Anteprima scena non disponibile.")
        return
    if _GSF_LIVE_V2 is None:
        st.warning("Per il player LIVE persistente serve una versione recente di Streamlit con Components V2.")
        return _render_gsf_editor_live_player_legacy(
            source_path,key,start_seconds,fmt,zoom,x_pos,y_pos,volume,brightness,contrast,speed,
            subtitles_on,subtitle_style,subtitle_size,subtitle_position,subtitle_words,subtitle_text,
            subtitle_font,subtitle_x,subtitle_y
        )

    served_name,_=_gsf_serve_path(source_path,"persistent_"+str(Path(source_path).name))
    url=f"http://127.0.0.1:{GSF_PREVIEW_PORT}/{quote(served_name)}"
    vertical=(fmt=="9:16 Short")
    frame_h=391 if vertical else 270
    live_font=max(13,min(48,float(subtitle_size)*(frame_h/1920.0)*1.25))
    words=[]
    for w in (subtitle_words or []):
        try:
            words.append({"text":str(w.get("text","")),"start":float(w.get("start",0)),"end":float(w.get("end",0))})
        except Exception:
            pass

    tc=text_color or st.session_state.get("subtitle_text_color_v18",st.session_state.get("subtitle_text_color","#FFFFFF"))
    ac=active_color or st.session_state.get("subtitle_active_color_v18",st.session_state.get("subtitle_active_color","#FFD400"))
    oc=outline_color or st.session_state.get("subtitle_outline_color_v18",st.session_state.get("subtitle_outline_color","#000000"))
    clip_start=float(clip_start_override if clip_start_override is not None else start_seconds)
    end=float(end_seconds if end_seconds is not None else max(clip_start+.1,clip_start+30))
    seek=float(seek_target if seek_target is not None else clip_start)

    _GSF_LIVE_V2(
        key=key,
        data={
            "url":url,
            "format":fmt,
            "zoom":float(zoom),"x":float(x_pos),"y":float(y_pos),
            "volume":float(volume),"brightness":float(brightness),"contrast":float(contrast),"speed":float(speed),
            "clipStart":clip_start,"clipEnd":end,
            "seekTarget":seek,"seekNonce":str(seek_nonce),"resetId":str(reset_id),
            "subtitlesOn":bool(subtitles_on),
            "words":words,"subtitleText":str(subtitle_text or ""),
            "font":str(subtitle_font or "Arial"),"liveFont":live_font,
            "subtitleX":float(subtitle_x),"subtitleY":float(subtitle_y),
            "textColor":tc,"activeColor":ac,"outlineColor":oc,
        },
    )

def _render_gsf_editor_live_player_legacy(
    source_path, key, start_seconds, fmt, zoom, x_pos, y_pos,
    volume, brightness, contrast, speed,
    subtitles_on=False, subtitle_style="Gaming",
    subtitle_size=92, subtitle_position=330,
    subtitle_words=None, subtitle_text="",
    subtitle_font="Arial", subtitle_x=50, subtitle_y=78
):
    """Live editor preview in browser, including live subtitle overlay."""
    source_path=Path(source_path)
    if not source_path.exists():
        st.warning("Anteprima scena non disponibile."); return
    pw,ph,rotation,err=_gsf_probe_display_size(source_path)
    if err:
        st.warning(f"Anteprima scena non leggibile: {err}"); return

    served_name,_=_gsf_serve_path(source_path,key)
    url=f"http://127.0.0.1:{GSF_PREVIEW_PORT}/{quote(served_name)}"
    start_seconds=max(0.0,float(start_seconds))
    vertical=(fmt=="9:16 Short")
    frame_w,frame_h,iframe_h=((220,391,424) if vertical else (480,270,309))
    zoom=float(zoom); x_pos=float(x_pos); y_pos=float(y_pos)
    vol=max(0.0,min(1.0,float(volume)/100.0))
    bri=max(0.0,1.0+float(brightness))
    con=max(0.0,float(contrast)); speed=float(speed)
    tx=x_pos*0.35; ty=y_pos*0.35

    # Sottotitoli: niente preset. Aspetto controllato direttamente da font/colori/dimensione.
    ps=dict(
        color=st.session_state.get("subtitle_text_color","#FFFFFF"),
        active=st.session_state.get("subtitle_active_color","#FFD400"),
        weight=800,
        shadow=f"-2px -2px 0 {st.session_state.get('subtitle_outline_color','#000000')},2px -2px 0 {st.session_state.get('subtitle_outline_color','#000000')},-2px 2px 0 {st.session_state.get('subtitle_outline_color','#000000')},2px 2px 0 {st.session_state.get('subtitle_outline_color','#000000')},0 3px 7px rgba(0,0,0,.55)",
        transform="none", bg="transparent", radius=0, pad="2px 4px",
        family=f'"{subtitle_font}", Arial, sans-serif', scale=1.0, spacing="0px"
    )
    sx=max(5.0,min(95.0,float(subtitle_x)))
    sy=max(5.0,min(95.0,float(subtitle_y)))
    # Scale ASS-like 1080x1920 values to the small live viewport.
    live_font=max(13,min(48,float(subtitle_size)*(frame_h/1920.0)*1.25*float(ps.get("scale",1.0))))
    words=subtitle_words or []
    # Normalize subtitle timestamps to the player's source timeline.
    # Whisper returns source-absolute timestamps; this also accepts already-relative words.
    normalized_words=[]
    for _w in words:
        try:
            _ws=float(_w.get("start",0.0)); _we=float(_w.get("end",_ws))
            normalized_words.append({"text":str(_w.get("text","")), "start":_ws, "end":_we})
        except Exception:
            pass
    words_json=json.dumps(normalized_words,ensure_ascii=False)
    fallback_json=json.dumps(str(subtitle_text or ""),ensure_ascii=False)

    html=f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    html,body{{margin:0;padding:0;background:transparent;overflow:hidden}}
    .stage{{width:100%;display:flex;justify-content:center}}
    .viewport{{position:relative;width:{frame_w}px;height:{frame_h}px;max-width:96vw;
      overflow:hidden;border-radius:18px;background:#000;box-shadow:0 14px 34px rgba(16,40,61,.14)}}
    video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
      transform-origin:center;transform:translate({tx}%, {ty}%) scale({zoom});
      filter:brightness({bri}) contrast({con})}}
    .badge{{position:absolute;z-index:4;left:10px;top:10px;padding:5px 9px;border-radius:999px;
      background:rgba(0,0,0,.62);color:#fff;font:600 12px Arial;pointer-events:none}}
    #subs{{display:{'block' if subtitles_on else 'none'};position:absolute;z-index:5;
      left:{sx}%;top:{sy}%;width:88%;text-align:center;color:{ps['color']};
      transform:translate(-50%,-50%);
      font-family:{ps['family']};font-size:{live_font}px;font-weight:{ps['weight']};
      letter-spacing:{ps['spacing']};line-height:1.05;text-shadow:{ps['shadow']};text-transform:{ps['transform']};
      background:{ps['bg']};padding:{ps['pad']};border-radius:{ps['radius']}px;pointer-events:none}}
    #subs .active{{color:{ps['active']};display:inline-block;transform:scale(1.10)}}
    #subs{{transition:all .12s ease}}
    </style></head><body><div class="stage"><div class="viewport">
    <div class="badge">LIVE · {fmt}</div>
    <video id="v" controls preload="metadata" playsinline><source src="{url}"></video>
    <div id="subs"></div>
    </div></div><script>
    const v=document.getElementById("v"), box=document.getElementById("subs");
    const startAt={start_seconds:.3f}, words={words_json}, fallback={fallback_json}, style={json.dumps(subtitle_style)};
    function apply(){{v.volume={vol:.4f};v.playbackRate={speed:.4f};}}
    function esc(s){{return String(s).replace(/[&<>"']/g,m=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[m]));}}
    function renderSubs(){{
      if(!{str(bool(subtitles_on)).lower()}) return;
      const t=v.currentTime;
      if(words.length){{
        let idx=words.findIndex(w=>t>=Number(w.start)-0.06 && t<=Number(w.end)+0.10);
        if(idx<0){{
          // Between two Whisper words keep the nearest group visible instead of making subtitles disappear.
          idx=words.findIndex(w=>t<Number(w.start));
          if(idx<0) idx=words.length-1;
          else if(idx>0) idx-=1;
        }}
        const groupSize = 4;
         const base=Math.floor(idx/groupSize)*groupSize, group=words.slice(base,base+groupSize);
        box.innerHTML=group.map((w,j)=>j===idx-base?`<span class="active">${{esc(w.text)}}</span>`:esc(w.text)).join(" ");
      }} else {{
        box.textContent=fallback || "ANTEPRIMA SOTTOTITOLI";
      }}
    }}
    v.addEventListener("loadedmetadata",()=>{{
      apply();
      if(Number.isFinite(startAt) && startAt>=0 && Math.abs(v.currentTime-startAt)>.20){{
        try{{v.currentTime=Math.min(startAt,Math.max(0,v.duration-.03));}}catch(e){{}}
      }}
      renderSubs();
    }});
    v.addEventListener("timeupdate",renderSubs);
    v.addEventListener("seeked",renderSubs);
    v.addEventListener("play",renderSubs);
    v.addEventListener("pause",renderSubs);
    apply(); renderSubs();
    </script></body></html>"""
    components.html(html,height=iframe_h,scrolling=False)


def _gsf_clean_transcript_words(words):
    """Light cleanup while preserving original word timestamps."""
    import re
    out=[]; prev_norm=""
    for w in words:
        t=re.sub(r"\s+"," ",str(w.get("text","")).strip())
        t=re.sub(r"\s+([,.;:!?])",r"\1",t)
        if not t: continue
        norm=re.sub(r"[^\wÀ-ÿ']+","",t.lower())
        if out and norm and norm==prev_norm and float(w.get("start",0))-float(out[-1]["end"]) < .18:
            out[-1]["end"]=max(float(out[-1]["end"]),float(w.get("end",out[-1]["end"])))
            continue
        item={"text":t,"start":float(w["start"]),"end":float(w["end"])}
        if w.get("language"):
            item["language"]=w["language"]
        out.append(item)
        prev_norm=norm
    return out

def _gsf_subtitle_groups(words, max_words=5, max_seconds=2.8, pause_break=.55):
    """Build natural subtitle/navigation groups without changing timings."""
    groups=[]; cur=[]
    for w in words:
        if cur:
            pause=float(w["start"])-float(cur[-1]["end"])
            dur=float(w["end"])-float(cur[0]["start"])
            punct=str(cur[-1]["text"]).rstrip().endswith((".", "!", "?", ",", ";", ":"))
            if len(cur)>=max_words or pause>=pause_break or dur>=max_seconds or punct:
                groups.append(cur); cur=[]
        cur.append(w)
    if cur: groups.append(cur)
    return groups

@st.cache_data(show_spinner=False)
def _gsf_transcribe_editor_scene(source_path, start_seconds, duration_seconds):
    """Transcribe only selected editor scene; returns word timestamps on source timeline."""
    if not FFMPEG_PATH:
        return [], "FFmpeg non disponibile"
    temp_dir=os.path.join(tempfile.gettempdir(),"gsf_editor_subs")
    os.makedirs(temp_dir,exist_ok=True)
    token=hashlib.md5(f"{source_path}|{start_seconds:.2f}|{duration_seconds:.2f}".encode()).hexdigest()[:12]
    wav=os.path.join(temp_dir,f"{token}.wav")
    cmd=[
        FFMPEG_PATH,"-y","-ss",str(float(start_seconds)),"-i",str(source_path),
        "-t",str(float(duration_seconds)),"-vn","-ac","1","-ar","16000",
        "-af","highpass=f=70,lowpass=f=7800,loudnorm=I=-16:LRA=11:TP=-1.5",
        wav
    ]
    run=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if run.returncode!=0 or not os.path.exists(wav):
        return [], "Estrazione audio non riuscita"
    try:
        model=_gsf_subtitle_whisper_model()
        segs,info=model.transcribe(
            wav,
            language=None,
            task="transcribe",
            vad_filter=True,
            beam_size=5,
            best_of=5,
            word_timestamps=True,
            condition_on_previous_text=False,
            initial_prompt=_gsf_gaming_prompt(
                st.session_state.get("gioco", "ARC Raiders")
            ),
            vad_parameters=dict(min_silence_duration_ms=250)
        )
        result=[]
        for seg in list(segs):
            for w in (getattr(seg,"words",None) or []):
                t=str(w.word).strip()
                if t:
                    result.append({
                        "text":t,
                        "start":float(start_seconds)+float(w.start),
                        "end":float(start_seconds)+float(w.end),
                        "language":str(getattr(info,"language","") or "")
                    })
        return _gsf_clean_transcript_words(result), None
    except Exception as e:
        return [], str(e)


def _gsf_atempo_chain(speed):
    """FFmpeg atempo chain valid for the editor speed range."""
    speed=float(speed)
    parts=[]
    while speed > 2.0:
        parts.append("atempo=2.0"); speed/=2.0
    while speed < 0.5:
        parts.append("atempo=0.5"); speed/=0.5
    parts.append(f"atempo={speed:.4f}")
    return ",".join(parts)

def _gsf_editor_filters(fmt, zoom, x_pos, y_pos, brightness, contrast, speed, preview=False):
    """One source of truth for quick preview and final editor render."""
    zoom=float(zoom); x_pos=float(x_pos); y_pos=float(y_pos)
    brightness=float(brightness); contrast=float(contrast); speed=float(speed)

    if fmt == "9:16 Short":
        out_w,out_h=(540,960) if preview else (1080,1920)
        # First cover the vertical canvas, then zoom and pan inside it.
        vf=(
            f"scale={out_w}:{out_h}:force_original_aspect_ratio=increase,"
            f"crop={out_w}:{out_h},"
            f"scale=iw*{zoom}:ih*{zoom},"
            f"crop={out_w}:{out_h}:"
            f"(iw-{out_w})/2+({x_pos}/100)*(iw-{out_w})/2:"
            f"(ih-{out_h})/2+({y_pos}/100)*(ih-{out_h})/2,"
            f"eq=brightness={brightness}:contrast={contrast},"
            f"setpts=PTS/{speed}"
        )
    else:
        # Same geometry for preview/final; preview only lowers output resolution.
        base_h=540 if preview else 1080
        vf=(
            f"scale=-2:{base_h},"
            f"scale=iw*{zoom}:ih*{zoom},"
            f"crop=iw/{zoom}:ih/{zoom}:"
            f"(iw-iw/{zoom})/2+({x_pos}/100)*(iw-iw/{zoom})/2:"
            f"(ih-ih/{zoom})/2+({y_pos}/100)*(ih-ih/{zoom})/2,"
            f"scale=-2:{base_h},"
            f"eq=brightness={brightness}:contrast={contrast},"
            f"setpts=PTS/{speed}"
        )

    af=f"volume={float(st.session_state.get('editor_volume',100))/100.0}," + _gsf_atempo_chain(speed)
    return vf,af


if video:

    # Player pulito: solo il lettore nativo, senza etichette o controlli aggiuntivi.
    st.markdown(
        '<div class="gsf-command">✨ <b>Cosa vuoi fare con questo gameplay?</b> '
        'Puoi lasciare scegliere tutto all’AI oppure controllare la scena manualmente.</div>',
        unsafe_allow_html=True
    )

    # Player sorgente compatto, stile YouTube: riduce solo la UI,
    # non modifica risoluzione o qualità del video.
    # PLAYER PRINCIPALE: dimensione separata per formato.
    # Lettore 1 (9:16) resta com'è; Lettore 2 (16:9) diventa molto più grande.
    try:
        _main_probe_dir = tempfile.mkdtemp(prefix="gsf_main_ratio_")
        _main_probe_path = os.path.join(_main_probe_dir, "main_ratio.mp4")
        with open(_main_probe_path, "wb") as _mf:
            _mf.write(video.getvalue())

        _main_probe_cmd = [
            FFPROBE_PATH, "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0:s=x",
            _main_probe_path
        ]
        _main_probe = subprocess.run(
            _main_probe_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        _mw, _mh = [int(x) for x in _main_probe.stdout.strip().split("x")[:2]]
    except Exception:
        _mw, _mh = 16, 9

    # PLAYER HTML5 ADATTIVO DEFINITIVO
    st.markdown("### 🎬 Anteprima video")

    _safe_name = Path(getattr(video, "name", "preview.mp4")).name
    _preview_path = GSF_PREVIEW_DIR / _safe_name
    _uploaded_size = getattr(video, "size", None)
    _must_write = (not _preview_path.exists()) or (
        _uploaded_size is not None and _preview_path.exists()
        and _preview_path.stat().st_size != _uploaded_size
    )
    if _must_write:
        with st.spinner("Preparo l'anteprima locale..."):
            with open(_preview_path, "wb") as _f:
                video.seek(0)
                while True:
                    _chunk=video.read(4*1024*1024)
                    if not _chunk: break
                    _f.write(_chunk)
                video.seek(0)

    _pw,_ph,_rotation,_probe_error=_gsf_probe_display_size(_preview_path)
    if _probe_error:
        st.error(f"⚠️ Impossibile leggere il formato video: {_probe_error}")
    else:
        _vertical=_ph>_pw
        if _vertical:
            _profile="PLAYER 9:16"; _target_width=300; _max_vw="300px"; _cap=680
        else:
            _profile="PLAYER 16:9"; _target_width=800; _max_vw="800px"; _cap=540

        _target_height=round(_target_width*_ph/_pw)
        _video_url=f"http://127.0.0.1:{GSF_PREVIEW_PORT}/{quote(_safe_name)}"

        _html=f"""
        <!doctype html><html><head><meta charset="utf-8"><style>
        html,body{{margin:0;padding:0;background:transparent;overflow:hidden}}
        .wrap{{width:100%;display:flex;justify-content:center;align-items:flex-start}}
        video{{display:block;width:{_target_width}px;max-width:{_max_vw};height:auto;
        object-fit:contain;border-radius:18px;background:#000;
        box-shadow:0 14px 34px rgba(16,40,61,.14)}}
        </style></head><body><div class="wrap">
        <video controls preload="metadata" playsinline><source src="{_video_url}"></video>
        </div></body></html>
        """
        components.html(_html,height=min(_target_height+30,_cap),scrolling=False)

    st.divider()
    st.markdown('<div class="gsf-section-title">Come vuoi creare?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="gsf-section-sub">Lascia fare all’AI oppure scegli tu la scena.</div>',
        unsafe_allow_html=True
    )
    modalita = st.radio(
        "Modalità",
        ["🚀 AUTO TOTALE", "🎬 AI Director", "🧠 Smart Clip", "🤖 Auto Clip", "✋ Manuale"],
        horizontal=True,
        label_visibility="collapsed",
        key="modalita_gsf",
        format_func=lambda x: {
            "🚀 AUTO TOTALE": "✨ Automatico",
            "🎬 AI Director": "🎬 Momento migliore",
            "🧠 Smart Clip": "🔥 Più azione",
            "🤖 Auto Clip": "🎙️ Reazioni",
            "✋ Manuale": "🎯 Scegli scena"
        }.get(x, x)
    )

    # Spiegazione compatta del motore selezionato, vicino a Durata.
    _engine_help = {
        "🚀 AUTO TOTALE": "☁️ Automatico: analizza tutto il gameplay combinando azione, movimento, audio, voce/reazioni, cambi di scena e parti morte. Alla fine propone i 3 momenti con il punteggio complessivo migliore.",
        "🎬 AI Director": "☁️ Momento migliore: cerca i picchi più interessanti e completi bilanciando evento, ritmo e audio. Alla fine propone i 3 momenti migliori secondo questo criterio.",
        "🧠 Smart Clip": "☁️ Più azione: privilegia movimento, combattimenti, cambi rapidi, eventi intensi e picchi visivi, penalizzando attese e parti statiche. Alla fine propone le 3 scene con più azione.",
        "🤖 Auto Clip": "☁️ Reazioni: privilegia voce, urla, risate, esclamazioni e picchi audio collegandoli al gameplay. Alla fine propone i 3 momenti con le reazioni più interessanti.",
        "✋ Manuale": "☁️ Scegli scena: qui l’AI non crea 3 proposte. Selezioni tu IN/OUT e lavori direttamente sulla scena nel player LIVE."
    }
    st.caption(_engine_help.get(modalita, ""))

    # Prima dell'analisi scegliamo solo la durata. I sottotitoli si decidono DOPO aver scelto una clip.
    preset_durata = st.selectbox(
        "⏱️ Durata",
        ["15s", "30s"],
        index=0,
        help="Durata target di ciascuna delle 3 proposte create dall’AI."
    )
    duration = float(preset_durata.replace("s", ""))


    # Collegamento reale Scegli scena -> Editor.
    st.session_state["apri_editor_manuale"] = (modalita == "✋ Manuale")


    # ==========================================================
    # MINI VIDEO EDITOR — prima versione
    # ==========================================================
    if modalita == "✋ Manuale":
        # Salva una copia temporanea dell'upload per leggere durata e fare preview/export.
        _editor_from_ai = (st.session_state.get("current_view") == "editor" and
                           st.session_state.get("editor_source") == "ai")
        editor_key = f"{video.name}_{video.size}"
        if _editor_from_ai and st.session_state.get("editor_input") and os.path.exists(st.session_state.get("editor_input","")):
            # La clip AI è già stata materializzata: usa quella, non sovrascriverla con l'upload originale.
            editor_input = st.session_state["editor_input"]
            editor_dir = st.session_state["editor_dir"]
        else:
            if st.session_state.get("editor_key") != editor_key:
                editor_dir = tempfile.mkdtemp(prefix="gsf_editor_")
                editor_input = os.path.join(editor_dir, "editor_input.mp4")
                with open(editor_input, "wb") as ef:
                    ef.write(video.getvalue())
                st.session_state["editor_key"] = editor_key
                st.session_state["editor_dir"] = editor_dir
                st.session_state["editor_input"] = editor_input
                st.session_state.pop("editor_output", None)
                st.session_state.pop("editor_output_bytes", None)
                st.session_state.pop("editor_output_name", None)
                st.session_state.pop("editor_quick_bytes", None)
                st.session_state.pop("editor_quick_path", None)
                st.session_state.pop("editor_quick_signature", None)
            editor_input = st.session_state["editor_input"]
            editor_dir = st.session_state["editor_dir"]
        editor_duration = durata_video(editor_input) or 30.0


        # ===== EDITOR STUDIO: timeline + player + tools in one compact workspace =====
        st.markdown("#### ✂️ Editor")
        ai_edit_start = float(st.session_state.get("editor_ai_start", 0.0))
        ai_edit_duration = float(
            st.session_state.get("editor_ai_duration", min(editor_duration, 15.0))
        )
        trim_default = (
            max(0.0, min(ai_edit_start, editor_duration)),
            max(0.5, min(ai_edit_start + ai_edit_duration, editor_duration))
        )
        if trim_default[1] <= trim_default[0]:
            trim_default = (0.0, float(min(editor_duration, 15.0)))

        editor_trim_key = "editor_trim_" + str(
            st.session_state.get("editor_ai_token", "manual")
        )
        st.caption("✂️ Timeline · trascina IN/OUT per selezionare la scena")
        trim_range = st.slider(
            "Inizio / fine",
            min_value=0.0,
            max_value=float(max(1.0, editor_duration)),
            value=trim_default,
            step=0.5,
            key=editor_trim_key,
            label_visibility="collapsed"
        )
        editor_start, editor_end = trim_range
        editor_len = max(0.5, editor_end - editor_start)

        info1, info2, info3 = st.columns(3)
        info1.caption(f"IN · **{editor_start:.1f}s**")
        info2.caption(f"OUT · **{editor_end:.1f}s**")
        info3.caption(f"DURATA · **{editor_len:.1f}s**")

        if editor_len > 30:
            st.warning("☁️ Per uno Short più rapido prova a restare entro 30 secondi.")

        # ===== EDITOR V13: PLAYER UNICO + CONTROLLI LATERALI PULITI =====
        if "editor_speed" not in st.session_state: st.session_state["editor_speed"]=1.0
        if "editor_brightness" not in st.session_state: st.session_state["editor_brightness"]=0.0
        if "editor_contrast" not in st.session_state: st.session_state["editor_contrast"]=1.0
        if "editor_sub_size" not in st.session_state: st.session_state["editor_sub_size"]=92
        if "editor_sub_text" not in st.session_state: st.session_state["editor_sub_text"]=""
        if "subtitle_x" not in st.session_state: st.session_state["subtitle_x"]=50
        if "subtitle_y" not in st.session_state: st.session_state["subtitle_y"]=78
        if "subtitle_text_color" not in st.session_state: st.session_state["subtitle_text_color"]="#FFFFFF"
        if "subtitle_active_color" not in st.session_state: st.session_state["subtitle_active_color"]="#FFD400"
        if "subtitle_outline_color" not in st.session_state: st.session_state["subtitle_outline_color"]="#000000"
        if "project_subtitles_enabled" not in st.session_state: st.session_state["project_subtitles_enabled"]=True

        editor_format=st.session_state.get("editor_format","9:16 Short")
        editor_zoom=float(st.session_state.get("editor_zoom",1.0))
        editor_x=int(st.session_state.get("editor_x",0))
        editor_y=int(st.session_state.get("editor_y",0))
        editor_volume=int(st.session_state.get("editor_volume",100))
        editor_speed=float(st.session_state.get("editor_speed",1.0))
        editor_brightness=float(st.session_state.get("editor_brightness",0.0))
        editor_contrast=float(st.session_state.get("editor_contrast",1.0))

        # Conserva i limiti originali una sola volta per RESET TUTTO.
        st.session_state.setdefault("editor_original_start",editor_start)
        st.session_state.setdefault("editor_original_end",editor_end)

        # V25: leggi subito i valori dei widget già aggiornati dal rerun, prima del player.
        if "editor_sub_font_v18" in st.session_state:
            st.session_state["subtitle_font"]=st.session_state["editor_sub_font_v18"]
        if "editor_sub_size_v18" in st.session_state:
            st.session_state["editor_sub_size"]=st.session_state["editor_sub_size_v18"]
        if "subtitle_text_color_v18" in st.session_state:
            st.session_state["subtitle_text_color"]=st.session_state["subtitle_text_color_v18"]
        if "subtitle_active_color_v18" in st.session_state:
            st.session_state["subtitle_active_color"]=st.session_state["subtitle_active_color_v18"]
        if "subtitle_outline_color_v18" in st.session_state:
            st.session_state["subtitle_outline_color"]=st.session_state["subtitle_outline_color_v18"]
        if "subtitle_x_v18" in st.session_state:
            st.session_state["subtitle_x"]=st.session_state["subtitle_x_v18"]
        if "subtitle_y_v18" in st.session_state:
            st.session_state["subtitle_y"]=st.session_state["subtitle_y_v18"]

        # V18: UN SOLO PLAYER a sinistra, workspace compatto a destra.
        studio_player, studio_side = st.columns([.22,.78],gap="medium")

        # Trascrizione persistente per sorgente: i controlli grafici non la resettano.
        scene_token=f"{editor_input}"
        if st.session_state.get("editor_sub_scene_token") != scene_token:
            st.session_state["editor_sub_words"]=[]
            st.session_state["editor_sub_live_words"]=[]
            st.session_state["editor_sub_text"]=""
            st.session_state["editor_sub_scene_token"]=scene_token

        with studio_player:
            render_gsf_editor_live_player(
                editor_input,
                "editor_master_live_v32",
                editor_start,
                editor_format,editor_zoom,editor_x,editor_y,editor_volume,
                editor_brightness,editor_contrast,editor_speed,
                subtitles_on=(st.session_state.get("editor_sub_mode","Automatici")!="Nessuno"),
                subtitle_style="Base",
                subtitle_size=st.session_state.get("editor_sub_size_v18",st.session_state.get("editor_sub_size",92)),
                subtitle_position=330,
                subtitle_words=st.session_state.get("editor_sub_live_words",st.session_state.get("editor_sub_words",[])),
                subtitle_text=(st.session_state.get("editor_sub_text","") or
                               ("Anteprima sottotitoli" if st.session_state.get("editor_sub_mode","Automatici")!="Nessuno" else "")),
                subtitle_font=st.session_state.get("editor_sub_font_v18",st.session_state.get("subtitle_font","Arial")),
                subtitle_x=st.session_state.get("subtitle_x_v18",st.session_state.get("subtitle_x",50)),
                subtitle_y=st.session_state.get("subtitle_y_v18",st.session_state.get("subtitle_y",78)),
                end_seconds=editor_end,
                seek_target=st.session_state.get("editor_sub_seek",editor_start),
                seek_nonce=st.session_state.get("editor_sub_seek_nonce",0),
                text_color=st.session_state.get("subtitle_text_color_v18","#FFFFFF"),
                active_color=st.session_state.get("subtitle_active_color_v18","#FFD400"),
                outline_color=st.session_state.get("subtitle_outline_color_v18","#000000"),
                reset_id=st.session_state.get("editor_reset_id",0),
                clip_start_override=editor_start
            )

        with studio_side:
            _th,_tr=st.columns([.78,.22],gap="small")
            with _th:
                st.markdown("##### 🛠️ Strumenti",help="Regola formato, inquadratura, audio e immagine. Le modifiche sono mostrate nel player LIVE.")
            with _tr:
                st.button(
                    "↶ RESET TUTTO",use_container_width=True,key="reset_main_all_v29",
                    on_click=_gsf_reset_main_all
                )
            _fmtc,_inqc,_regc=st.columns([.30,.35,.35],gap="small")
            with _fmtc:
                editor_format=st.segmented_control(
                    "Formato",["9:16 Short","16:9 Originale"],key="editor_format"
                )
            with _inqc:
                with st.popover("🎯 INQUADRATURA",use_container_width=True):
                    editor_zoom=st.slider("Zoom",1.0,2.0,float(st.session_state.get("editor_zoom",1.0)),.05,key="editor_zoom")
                    editor_x=st.slider("↔ X",-100,100,int(st.session_state.get("editor_x",0)),5,key="editor_x")
                    editor_y=st.slider("↕ Y",-100,100,int(st.session_state.get("editor_y",0)),5,key="editor_y")
            with _regc:
                with st.popover("🎚️ REGOLAZIONI",use_container_width=True):
                    editor_extra_tool=st.selectbox("Parametro",["Volume","Velocità","Luminosità","Contrasto"],key="editor_extra_tool")
                    if editor_extra_tool=="Volume":
                        editor_volume=st.slider("Volume",0,200,int(st.session_state.get("editor_volume",100)),5,key="editor_volume")
                    elif editor_extra_tool=="Velocità":
                        editor_speed=st.select_slider("Velocità",options=[.5,.75,1.0,1.25,1.5,2.0],value=float(st.session_state.get("editor_speed",1.0)),key="editor_speed")
                    elif editor_extra_tool=="Luminosità":
                        editor_brightness=st.slider("Luminosità",-.30,.30,float(st.session_state.get("editor_brightness",0.0)),.05,key="editor_brightness")
                    else:
                        editor_contrast=st.slider("Contrasto",.70,1.50,float(st.session_state.get("editor_contrast",1.0)),.05,key="editor_contrast")

            st.markdown("##### 📝 Sottotitoli",help="Automatici: fa tutto l'AI. Manuali: trascrive la scena e permette di correggere testo e aspetto. Nessuno: video pulito.")
            _modes=["Nessuno","Automatici","Manuali"]
            _cur=st.session_state.get("editor_sub_mode","Automatici")
            if _cur not in _modes: _cur="Automatici"
            editor_sub_mode=st.segmented_control(
                "Modalità sottotitoli",_modes,default=_cur,key="editor_sub_mode_v18",
                label_visibility="collapsed"
            )
            st.session_state["editor_sub_mode"]=editor_sub_mode
            st.session_state["project_subtitles_enabled"]=(editor_sub_mode!="Nessuno")
            st.session_state["project_subtitles_mode"]=editor_sub_mode

            if editor_sub_mode=="Manuali":
                _fonts=_gsf_windows_fonts()
                _current_font=st.session_state.get("subtitle_font","Arial")
                if _current_font not in _fonts: _current_font="Arial"
                _fontc,_aspectc,_posc=st.columns([.40,.30,.30],gap="small")
                with _fontc:
                    st.selectbox(
                        "🔤 Font",_fonts,index=_fonts.index(_current_font),key="editor_sub_font_v18",
                        on_change=_gsf_sync_main_subtitle_font
                    )
                    st.session_state["subtitle_font"]=st.session_state.get("editor_sub_font_v18",_current_font)
                with _aspectc:
                    with st.popover("📐 ASPETTO",use_container_width=True):
                        st.slider(
                            "Dimensione",48,140,int(st.session_state.get("editor_sub_size_v18",st.session_state.get("editor_sub_size",92))),2,key="editor_sub_size_v18"
                        )
                        c1,c2,c3=st.columns(3,gap="small")
                        with c1:
                            st.color_picker("Testo",st.session_state.get("subtitle_text_color_v18",st.session_state.get("subtitle_text_color","#FFFFFF")),key="subtitle_text_color_v18")
                        with c2:
                            st.color_picker("Attiva",st.session_state.get("subtitle_active_color_v18",st.session_state.get("subtitle_active_color","#FFD400")),key="subtitle_active_color_v18")
                        with c3:
                            st.color_picker("Bordo",st.session_state.get("subtitle_outline_color_v18",st.session_state.get("subtitle_outline_color","#000000")),key="subtitle_outline_color_v18")
                with _posc:
                    with st.popover("📍 POSIZIONE",use_container_width=True):
                        st.slider("↔ X",5,95,int(st.session_state.get("subtitle_x_v18",st.session_state.get("subtitle_x",50))),1,key="subtitle_x_v18")
                        st.slider("↕ Y",5,95,int(st.session_state.get("subtitle_y_v18",st.session_state.get("subtitle_y",78))),1,key="subtitle_y_v18")
                st.markdown("##### ✏️ Trascrizione intelligente",help="La trascrizione resta salvata mentre modifichi font, colori, posizione o gli strumenti.")
                if not st.session_state.get("editor_sub_words"):
                    if st.button("TRASCRIVI LA SCENA",use_container_width=True,key="editor_transcribe_scene_v18"):
                        with st.spinner("Trascrivo la scena..."):
                            words,err=_gsf_transcribe_editor_scene(editor_input,editor_start,editor_len)
                        if err:
                            st.warning(f"Trascrizione non disponibile: {err}")
                        else:
                            st.session_state["editor_sub_words"]=list(words)
                            st.session_state["editor_sub_live_words"]=list(words)
                            st.session_state["editor_sub_text"]=" ".join(w["text"] for w in words)
                            st.session_state["editor_sub_applied_text"]=st.session_state["editor_sub_text"]
                            st.session_state["editor_sub_seek"]=editor_start
                            st.rerun()
                else:
                    # Navigazione temporale compatta: una sola riga.
                    _tw=st.session_state.get("editor_sub_words",[])
                    if _tw:
                        _time_opts=[]
                        for _group in _gsf_subtitle_groups(_tw):
                            _t=float(_group[0]["start"])
                            _preview=" ".join(w["text"] for w in _group)
                            _time_opts.append((_t,f"{int(_t//60):02d}:{(_t%60):05.2f} · {_preview}"))
                        _tc_col,_go_col=st.columns([.82,.18],gap="small")
                        with _tc_col:
                            _chosen_label=st.selectbox(
                                "⏱ Vai al testo", [x[1] for x in _time_opts],
                                key="editor_time_nav_v22"
                            )
                        with _go_col:
                            st.write("")
                            if st.button("VAI",use_container_width=True,key="editor_time_go_v22"):
                                _chosen_t=next(t for t,label in _time_opts if label==_chosen_label)
                                # _chosen_t è un timestamp assoluto della sorgente.
                                st.session_state["editor_sub_seek"]=float(_chosen_t)
                                st.session_state["editor_sub_seek_feedback"]=float(_chosen_t)
                                st.session_state["editor_sub_seek_nonce"]=int(st.session_state.get("editor_sub_seek_nonce",0))+1
                                st.rerun()
                    if "editor_sub_seek_feedback" in st.session_state:
                        _ft=float(st.session_state["editor_sub_seek_feedback"])                        st.caption(f"✓ Anteprima posizionata a {int(_ft//60):02d}:{(_ft%60):05.2f}")
                    edited=st.text_area(
                        "Correggi, elimina o aggiungi parole",
                        value=st.session_state.get("editor_sub_text",""),
                        height=125,key="editor_sub_text_area_v18"
                    )
                    _main_is_applied=(edited==st.session_state.get("editor_sub_applied_text",st.session_state.get("editor_sub_text","")))
                    _main_apply_label="✓ APPLICATO" if _main_is_applied else "✓ APPLICA"
                    if st.button(_main_apply_label,type="primary",use_container_width=True,key="editor_apply_subs_v26",disabled=_main_is_applied):
                        st.session_state["editor_sub_text"]=edited
                        st.session_state["editor_sub_applied_text"]=edited
                        tokens=edited.split()
                        timed=st.session_state.get("editor_sub_words",[])
                        live_words=[]
                        for i,w in enumerate(timed):
                            if i<len(tokens):
                                live_words.append({"text":tokens[i],"start":w["start"],"end":w["end"]})
                        if len(tokens)>len(timed):
                            last_end=(timed[-1]["end"] if timed else editor_start)
                            remain=max(.08,(editor_end-last_end)/max(1,len(tokens)-len(timed)))
                            for j in range(len(timed),len(tokens)):
                                a=min(editor_end-.04,last_end+(j-len(timed))*remain)
                                b=min(editor_end,a+remain*.9)
                                live_words.append({"text":tokens[j],"start":a,"end":b})
                        st.session_state["editor_sub_live_words"]=live_words
                        st.rerun()

        st.markdown("#### 🎞️ Crea video")
        if st.button(
            "🎞️ CREA VIDEO COMPLETO",
            type="primary",
            use_container_width=True,
            key="editor_preview_btn"
        ):
            editor_output = os.path.join(editor_dir, "editor_preview.mp4")

            _main_sub_mode=st.session_state.get("editor_sub_mode","Automatici")
            _main_sub_words=(
                st.session_state.get(
                    "editor_sub_live_words",
                    st.session_state.get("editor_sub_words",[])
                )
                if _main_sub_mode=="Manuali" else []
            )

            with st.spinner("🎬 Creo il video finale dal file originale..."):
                editor_run = _gsf_render_core(
                    editor_input,
                    editor_output,
                    editor_start,
                    editor_len,
                    fmt=editor_format,
                    zoom=editor_zoom,
                    x_pos=editor_x,
                    y_pos=editor_y,
                    brightness=editor_brightness,
                    contrast=editor_contrast,
                    speed=editor_speed,
                    volume=editor_volume,
                    subtitles_enabled=(_main_sub_mode!="Nessuno"),
                    subtitle_mode=_main_sub_mode,
                    subtitle_words=_main_sub_words,
                    subtitle_text=st.session_state.get("editor_sub_text",""),
                    subtitle_time_origin=editor_start,
                    subtitle_font=st.session_state.get(
                        "editor_sub_font_v18",
                        st.session_state.get("subtitle_font","Arial")
                    ),
                    subtitle_size=st.session_state.get(
                        "editor_sub_size_v18",
                        st.session_state.get("editor_sub_size",92)
                    ),
                    subtitle_x=st.session_state.get(
                        "subtitle_x_v18",
                        st.session_state.get("subtitle_x",50)
                    ),
                    subtitle_y=st.session_state.get(
                        "subtitle_y_v18",
                        st.session_state.get("subtitle_y",78)
                    ),
                    text_color=st.session_state.get(
                        "subtitle_text_color_v18","#FFFFFF"
                    ),
                    active_color=st.session_state.get(
                        "subtitle_active_color_v18","#FFD400"
                    ),
                    outline_color=st.session_state.get(
                        "subtitle_outline_color_v18","#000000"
                    ),
                    normalize_audio=True,
                    smart_reframe=False,
                    hook_text="",
                    polish_audio=True
                )

            if editor_run.get("ok") and os.path.exists(editor_output):
                # IMPORTANT: teniamo i byte in session_state.
                # Streamlit riesegue lo script quando si preme Download;
                # affidarsi solo al file temporaneo può far sparire il file.
                with open(editor_output, "rb") as edf:
                    editor_bytes = edf.read()

                st.session_state["editor_output"] = editor_output
                st.session_state["editor_output_bytes"] = editor_bytes
                st.session_state["editor_output_name"] = "gaming_short_edit.mp4"
                st.session_state["publication_final_bytes"]=editor_bytes
                st.session_state["publication_source"]="main_editor"
                st.success(
                    f"✅ Video finale pronto · {editor_run.get('encoder','')} · "
                    f"{editor_run.get('seconds',0):.1f}s"
                )
            else:
                st.error("❌ Non sono riuscito a creare l'anteprima.")
                if editor_run.get("error"):
                    st.code(editor_run.get("error","")[-3000:])

        editor_bytes = st.session_state.get("editor_output_bytes")

        if editor_bytes:
            # Il player e il download usano gli stessi byte persistenti.
            st.caption("🎬 RISULTATO EDITOR")
            _editor_result_path = st.session_state.get("editor_output")
            if _editor_result_path and os.path.exists(_editor_result_path):
                render_gsf_player(_editor_result_path, "editor_result")
            else:
                _erp = _gsf_bytes_to_preview(editor_bytes, "editor_result")
                render_gsf_player(_erp, "editor_result")

            st.download_button(
                "⬇️ SCARICA VIDEO MODIFICATO",
                data=editor_bytes,
                file_name=st.session_state.get(
                    "editor_output_name",
                    "gaming_short_edit.mp4"
                ),
                mime="video/mp4",
                use_container_width=True,
                key="editor_download_fixed"
            )


    if modalita == "✋ Manuale":
        # Nessuna barra/numero di partenza: la selezione arriva solo dall'Editor.
        start = float(st.session_state.get("manual_start_editor", 0.0))
        duration = float(
            st.session_state.get("manual_duration_editor", duration)
        )
    else:
        if "auto_clip_scelta" not in st.session_state:
            st.session_state.auto_clip_scelta = None

        if st.button("✦ CREA CON AI", use_container_width=True):
            with tempfile.TemporaryDirectory() as analisi_temp:
                analisi_input = os.path.join(analisi_temp, "input.mp4")

                with open(analisi_input, "wb") as f:
                    f.write(video.getbuffer())

                if modalita == "🚀 AUTO TOTALE":
                    messaggio = "✨ Scansione completa → azione, audio, voce e tempi morti..."
                elif modalita == "🎬 AI Director":
                    messaggio = "🎬 Cerco costruzione, picco e chiusura dei momenti..."
                elif modalita == "🧠 Smart Clip":
                    messaggio = "🔥 Cerco movimento, combattimenti e attività sostenuta..."
                else:
                    messaggio = "🎙️ Cerco voce, reazioni e picchi collegati al gameplay..."

                _video_cache_token = (
                    f"{getattr(video,'name','video')}|"
                    f"{getattr(video,'size',len(video.getbuffer()))}"
                )

                cache_key_ai = (
                    GSF_AI_ENGINE_VERSION,
                    _video_cache_token,
                    modalita,
                    float(duration)
                )
                cached_ai = st.session_state.get("gsf_fast_ai_cache", {}).get(cache_key_ai)

                with st.spinner(messaggio):
                    if cached_ai is not None:
                        candidati = cached_ai.get("candidati", [])
                        if cached_ai.get("scores") is not None:
                            st.session_state.ai_director_scores = cached_ai["scores"]
                        if cached_ai.get("clip_rifinite") is not None:
                            st.session_state.clip_rifinite = cached_ai["clip_rifinite"]
                        if cached_ai.get("diagnostics") is not None:
                            st.session_state["gsf_ai_v3_diagnostics"] = cached_ai["diagnostics"]

                    else:
                        risultati_ai, ai_diag = _gsf_ai_rank_v3(
                            analisi_input,
                            modalita,
                            clip_duration=float(duration),
                            numero_clip=3,
                            cache_token=_video_cache_token
                        )

                        candidati = [start_ai for score_ai, start_ai in risultati_ai]
                        st.session_state.ai_director_scores = risultati_ai
                        st.session_state["gsf_ai_v3_diagnostics"] = ai_diag

                        # Solo Automatico e Momento migliore rifiniscono i bordi:
                        # per Azione/Reazioni non vogliamo spostare via il picco trovato.
                        if modalita in ["🚀 AUTO TOTALE", "🎬 AI Director"]:
                            clip_rifinite = {}
                            candidati_rifiniti = []
                            for start_ai in candidati:
                                _diag=st.session_state.get("gsf_ai_v3_diagnostics",{}).get(
                                    round(float(start_ai),3),{}
                                )
                                _event_strength=float(
                                    (_diag.get("features") or {}).get("event_score",0.0)
                                )
                                if _event_strength>=0.56:
                                    nuovo_start=float(start_ai)
                                    nuova_durata=float(duration)
                                else:
                                    nuovo_start, nuova_durata = rifinisci_confini_clip(
                                        analisi_input,
                                        float(start_ai),
                                        float(duration)
                                    )
                                candidati_rifiniti.append(nuovo_start)
                                clip_rifinite[round(nuovo_start, 3)] = nuova_durata
                            candidati = candidati_rifiniti
                            st.session_state.clip_rifinite = clip_rifinite
                            risultati_ai = [
                                (risultati_ai[i][0], candidati[i])
                                for i in range(min(len(risultati_ai),len(candidati)))
                            ]
                            st.session_state.ai_director_scores = risultati_ai
                        else:
                            st.session_state.clip_rifinite = {}

                if cached_ai is None:
                    if "gsf_fast_ai_cache" not in st.session_state:
                        st.session_state["gsf_fast_ai_cache"] = {}

                    st.session_state["gsf_fast_ai_cache"][cache_key_ai] = {
                        "candidati": list(candidati),
                        "scores": st.session_state.get("ai_director_scores"),
                        "clip_rifinite": st.session_state.get("clip_rifinite"),
                        "diagnostics": st.session_state.get("gsf_ai_v3_diagnostics"),
                    }

                st.session_state.auto_clip_candidati = candidati
                st.session_state.auto_clip_modalita = modalita

                if candidati:
                    st.session_state.auto_clip_scelta = candidati[0]
                else:
                    st.warning("Non ho trovato candidati. Usa la modalità Manuale.")

        if st.session_state.get("auto_clip_modalita") != modalita:
            candidati = []
        else:
            candidati = st.session_state.get("auto_clip_candidati", [])

        if candidati:
            if modalita != "✋ Manuale":
                risultati_ai = st.session_state.get(
                    "ai_director_scores",
                    []
                )

                if risultati_ai:
                    massimo_score = max(
                        score for score, _ in risultati_ai
                    ) or 1.0

                    opzioni = {}

                    for i, (score, sec) in enumerate(risultati_ai):
                        qualita = int(
                            max(1, min(100, score / massimo_score * 100))
                        )

                        _diag = st.session_state.get(
                            "gsf_ai_v3_diagnostics", {}
                        ).get(round(float(sec), 3), {})
                        _features = _diag.get("features") or {}
                        _event_type = str(_features.get("event_type", "") or "")
                        _event_score = float(_features.get("event_score", 0.0))
                        _event_badge = (
                            _GSF_EVENT_LABELS.get(_event_type, "")
                            if _event_score >= 0.56 else ""
                        )
                        if not _event_badge:
                            _category = str(_features.get("moment_category","") or "")
                            _event_badge = {
                                "reaction":"🎙️ REAZIONE",
                                "action":"🔥 AZIONE",
                                "story":"🎬 MOMENTO",
                            }.get(_category,"")

                        _short_pct = int(
                            max(1,min(
                                100,
                                float(_features.get("short_worthiness",0.0))*100
                            ))
                        )

                        label = (
                            f"#{i + 1} • "
                            + (f"{_event_badge} • " if _event_badge else "")
                            + f"Qualità {qualita}% • Short {_short_pct}% • "
                            + f"{sec:.0f}s → {sec + duration:.0f}s"
                        )

                        opzioni[label] = sec
                else:
                    opzioni = {
                        f"Clip {i + 1} — da {sec:.0f}s a {sec + duration:.0f}s": sec
                        for i, sec in enumerate(candidati)
                    }
            else:
                opzioni = {
                    f"Clip {i + 1} — da {sec:.0f}s a {sec + duration:.0f}s": sec
                    for i, sec in enumerate(candidati)
                }

            _ai_meta = st.session_state.get(
                "gsf_ai_v3_diagnostics", {}
            ).get("__meta__", {})
            if _ai_meta:
                _sec=float(_ai_meta.get("analysis_seconds",0.0))
                _scan_txt="riusata" if _ai_meta.get("scan_cache_hit") else "nuova"
                _vh=int(_ai_meta.get("voice_cache_hits",0))
                _vc=int(_ai_meta.get("voice_checks",0))
                st.caption(
                    f"⚡ Analisi AI {_sec:.1f}s · scansione {_scan_txt}"
                    + (f" · voce cache {_vh}/{_vc}" if _vc else "")
                )

            st.markdown('<div class="mini-label" style="margin-top:18px;">CLASSIFICA AI</div>', unsafe_allow_html=True)
            for posizione, label in enumerate(opzioni.keys(), start=1):
                st.write(f"**{posizione}.** {label}")

            scelta_label = st.radio(
                "🎯 Scegli un momento da vedere",
                list(opzioni.keys())
            )

            start = float(opzioni[scelta_label])
            st.session_state.auto_clip_scelta = start

            durata_effettiva = float(duration)

            if modalita in ["🚀 AUTO TOTALE", "🎬 AI Director"]:
                durata_effettiva = float(
                    st.session_state.get(
                        "clip_rifinite",
                        {}
                    ).get(round(start, 3), duration)
                )

                st.caption(
                    f"✂️ Taglio intelligente: {durata_effettiva:.1f}s"
                )

            st.caption("👀 Anteprima")

            preview_key = (
                f"{video.name}_{start:.2f}_{durata_effettiva:.2f}"
            )

            if st.session_state.get("preview_key") != preview_key:
                with tempfile.TemporaryDirectory() as preview_temp:
                    preview_input = os.path.join(preview_temp, "input.mp4")
                    preview_output = os.path.join(preview_temp, "preview.mp4")

                    with open(preview_input, "wb") as f:
                        f.write(video.getbuffer())

                    with st.spinner("⚡ Creo anteprima..."):
                        ok_preview = crea_anteprima(
                            preview_input,
                            preview_output,
                            start,
                            durata_effettiva
                        )

                    if ok_preview:
                        with open(preview_output, "rb") as f:
                            st.session_state.preview_bytes = f.read()
                        st.session_state.preview_key = preview_key

            if st.session_state.get("preview_bytes"):
                _aip = _gsf_bytes_to_preview(
                    st.session_state.preview_bytes,
                    f"ai_preview_{start:.2f}_{durata_effettiva:.2f}"
                )
                render_gsf_player(_aip, f"ai_preview_{start:.2f}_{durata_effettiva:.2f}")

                edit_col, keep_col = st.columns(2)
                with edit_col:
                    if st.button(
                        "✂️ MODIFICA NELL’EDITOR",
                        use_container_width=True,
                        key=f"edit_ai_{start:.2f}_{durata_effettiva:.2f}"
                    ):
                        # Apre UNA copia dell'Editor direttamente sotto questa clip.
                        _inline_id=f"{start:.2f}_{durata_effettiva:.2f}"
                        _edit_dir=tempfile.mkdtemp(prefix="gsf_inline_ai_")
                        _edit_input=os.path.join(_edit_dir,"ai_clip_inline_preview.mp4")
                        _edit_original=os.path.join(_edit_dir,"source_original.mp4")
                        with open(_edit_input,"wb") as _ef:
                            _ef.write(st.session_state.preview_bytes)
                        with open(_edit_original,"wb") as _of:
                            _of.write(video.getbuffer())
                        st.session_state["inline_editor_id"]=_inline_id
                        st.session_state["inline_editor_dir"]=_edit_dir
                        st.session_state["inline_editor_input"]=_edit_input
                        st.session_state["inline_editor_original_input"]=_edit_original
                        st.session_state["inline_editor_source_start"]=float(start)
                        st.session_state["inline_editor_duration"]=float(
                            durata_video(_edit_input) or durata_effettiva
                        )
                        st.session_state.pop("inline_final_bytes",None)
                        # Un solo editor AI aperto alla volta.
                        st.rerun()

                with keep_col:
                    if st.button(
                        "✓ USA QUESTA",
                        use_container_width=True,
                        key=f"use_ai_{start:.2f}_{durata_effettiva:.2f}"
                    ):
                        st.session_state.auto_clip_scelta = float(start)
                        st.session_state["auto_clip_duration"] = float(durata_effettiva)
                        st.session_state["publication_ready"] = True
                        st.session_state["publication_source"] = "ai_clip"
                        st.session_state["publication_preview_bytes"] = st.session_state.get("preview_bytes")
                        st.session_state.pop("publication_final_bytes",None)
                        st.session_state.pop("publication_final_signature",None)
                        st.session_state["project_view"] = "publication"
                        st.rerun()


                # ===== EDITOR INLINE DELLA CLIP AI =====
                _this_inline_id=f"{start:.2f}_{durata_effettiva:.2f}"
                if st.session_state.get("inline_editor_id")==_this_inline_id:
                    _ii=st.session_state.get("inline_editor_input")
                    _idir=st.session_state.get("inline_editor_dir")
                    _idur=float(st.session_state.get("inline_editor_duration",durata_effettiva))

                    if _ii and os.path.exists(_ii):
                        st.markdown("##### ✂️ Editor")
                        _close_col,_space_col=st.columns([.24,.76])
                        with _close_col:
                            if st.button("✕ CHIUDI EDITOR",use_container_width=True,key=f"inline_close_{_this_inline_id}"):
                                st.session_state.pop("inline_editor_id",None)
                                st.rerun()

                        # Timeline: descrizione sopra, nessuno scroll verso altri editor.
                        st.caption("✂️ Timeline · trascina IN/OUT per selezionare la scena")
                        _trim=st.slider(
                            "IN / OUT",0.0,float(max(.5,_idur)),
                            (0.0,float(max(.5,_idur))),.1,
                            key=f"inline_trim_{_this_inline_id}"
                        )
                        _istart=float(_trim[0])
                        _iend=float(_trim[1])
                        _ilen=max(.1,_iend-_istart)

                        # Stato grafico indipendente dalla trascrizione.
                        _fmt_key=f"inline_fmt_{_this_inline_id}"
                        _zoom_key=f"inline_zoom_{_this_inline_id}"
                        _x_key=f"inline_x_{_this_inline_id}"
                        _y_key=f"inline_y_{_this_inline_id}"
                        _vol_key=f"inline_vol_{_this_inline_id}"
                        _bri_key=f"inline_bri_{_this_inline_id}"
                        _con_key=f"inline_con_{_this_inline_id}"
                        _spd_key=f"inline_spd_{_this_inline_id}"
                        _submode_key=f"inline_submode_{_this_inline_id}"

                        if _fmt_key not in st.session_state: st.session_state[_fmt_key]="9:16 Short"
                        if _zoom_key not in st.session_state: st.session_state[_zoom_key]=1.0
                        if _x_key not in st.session_state: st.session_state[_x_key]=0
                        if _y_key not in st.session_state: st.session_state[_y_key]=0
                        if _vol_key not in st.session_state: st.session_state[_vol_key]=100
                        if _bri_key not in st.session_state: st.session_state[_bri_key]=0.0
                        if _con_key not in st.session_state: st.session_state[_con_key]=1.0
                        if _spd_key not in st.session_state: st.session_state[_spd_key]=1.0
                        if _submode_key not in st.session_state: st.session_state[_submode_key]="Automatici"

                        _pl,_side=st.columns([.22,.78],gap="medium")

                        # Trascrizione persistente PER CLIP: non viene toccata dai controlli grafici.
                        _trans_words_key=f"inline_trans_words_{_this_inline_id}"
                        _trans_text_key=f"inline_trans_text_{_this_inline_id}"
                        _trans_live_key=f"inline_trans_live_{_this_inline_id}"

                        with _pl:
                            _sub_on=st.session_state.get(_submode_key,"Automatici")!="Nessuno"
                            render_gsf_editor_live_player(
                                _ii,
                                f"inline_live_v32_{_this_inline_id}",
                                _istart,
                                st.session_state[_fmt_key],st.session_state[_zoom_key],
                                st.session_state[_x_key],st.session_state[_y_key],
                                st.session_state[_vol_key],st.session_state[_bri_key],
                                st.session_state[_con_key],st.session_state[_spd_key],
                                subtitles_on=_sub_on,subtitle_style="Base",
                                subtitle_size=st.session_state.get(f"inline_subsize_widget_v18_{_this_inline_id}",st.session_state.get(f"inline_subsize_{_this_inline_id}",92)),
                                subtitle_position=330,
                                subtitle_words=st.session_state.get(_trans_live_key,st.session_state.get(_trans_words_key,[])),
                                subtitle_text=(st.session_state.get(_trans_text_key,"") or ("Anteprima sottotitoli" if _sub_on else "")),
                                subtitle_font=st.session_state.get(f"inline_font_widget_v18_{_this_inline_id}",st.session_state.get(f"inline_font_{_this_inline_id}","Arial")),
                                subtitle_x=st.session_state.get(f"inline_subx_widget_v18_{_this_inline_id}",st.session_state.get(f"inline_subx_{_this_inline_id}",50)),
                                subtitle_y=st.session_state.get(f"inline_suby_widget_v18_{_this_inline_id}",st.session_state.get(f"inline_suby_{_this_inline_id}",78)),
                                end_seconds=_iend,
                                seek_target=st.session_state.get(f"inline_seek_{_this_inline_id}",_istart),
                                seek_nonce=st.session_state.get(f"inline_seek_nonce_{_this_inline_id}",0),
                                text_color=st.session_state.get(f"inline_txtcol_v18_{_this_inline_id}",st.session_state.get("subtitle_text_color","#FFFFFF")),
                                active_color=st.session_state.get(f"inline_actcol_v18_{_this_inline_id}",st.session_state.get("subtitle_active_color","#FFD400")),
                                outline_color=st.session_state.get(f"inline_outcol_v18_{_this_inline_id}","#000000"),
                                reset_id=st.session_state.get(f"inline_reset_id_{_this_inline_id}",0),
                                clip_start_override=_istart
                            )

                        with _side:
                            _ith,_itr=st.columns([.78,.22],gap="small")
                            with _ith:
                                st.markdown("##### 🛠️ Strumenti",help="Regola formato, inquadratura, audio e immagine. Le modifiche sono mostrate nel player LIVE.")
                            with _itr:
                                st.button(
                                    "↶ RESET TUTTO",use_container_width=True,key=f"reset_inline_all_v29_{_this_inline_id}",
                                    on_click=_gsf_reset_inline_all,
                                    args=(_this_inline_id,_fmt_key,_zoom_key,_x_key,_y_key,_vol_key,_bri_key,_con_key,_spd_key)
                                )
                            _fc,_ic,_rc=st.columns([.30,.35,.35],gap="small")
                            with _fc:
                                st.session_state[_fmt_key]=st.segmented_control(
                                    "Formato",["9:16 Short","16:9 Originale"],
                                    default=st.session_state[_fmt_key],key=f"inline_fmt_widget_v18_{_this_inline_id}"
                                )
                            with _ic:
                                with st.popover("🎯 INQUADRATURA",use_container_width=True):
                                    st.session_state[_zoom_key]=st.slider("Zoom",1.0,2.0,float(st.session_state[_zoom_key]),.05,key=f"inline_zoom_widget_v18_{_this_inline_id}")
                                    st.session_state[_x_key]=st.slider("↔ X",-100,100,int(st.session_state[_x_key]),5,key=f"inline_x_widget_v18_{_this_inline_id}")
                                    st.session_state[_y_key]=st.slider("↕ Y",-100,100,int(st.session_state[_y_key]),5,key=f"inline_y_widget_v18_{_this_inline_id}")
                            with _rc:
                                with st.popover("🎚️ REGOLAZIONI",use_container_width=True):
                                    _reg=st.selectbox("Parametro",["Volume","Luminosità","Contrasto","Velocità"],key=f"inline_reg_v18_{_this_inline_id}")
                                    if _reg=="Volume":
                                        st.session_state[_vol_key]=st.slider("Volume",0,200,int(st.session_state[_vol_key]),5,key=f"inline_vol_widget_v18_{_this_inline_id}")
                                    elif _reg=="Luminosità":
                                        st.session_state[_bri_key]=st.slider("Luminosità",-.30,.30,float(st.session_state[_bri_key]),.05,key=f"inline_bri_widget_v18_{_this_inline_id}")
                                    elif _reg=="Contrasto":
                                        st.session_state[_con_key]=st.slider("Contrasto",.70,1.50,float(st.session_state[_con_key]),.05,key=f"inline_con_widget_v18_{_this_inline_id}")
                                    else:
                                        st.session_state[_spd_key]=st.select_slider("Velocità",options=[.5,.75,1.0,1.25,1.5,2.0],value=float(st.session_state[_spd_key]),key=f"inline_spd_widget_v18_{_this_inline_id}")

                            st.markdown("##### 📝 Sottotitoli",help="Automatici: fa tutto l'AI. Manuali: trascrive la clip e permette di correggere testo e aspetto. Nessuno: video pulito.")
                            _modes=["Nessuno","Automatici","Manuali"]
                            _cur=st.session_state.get(_submode_key,"Automatici")
                            if _cur not in _modes: _cur="Automatici"
                            st.session_state[_submode_key]=st.segmented_control(
                                "Modalità sottotitoli",_modes,default=_cur,
                                key=f"inline_submode_widget_v18_{_this_inline_id}",label_visibility="collapsed"
                            )

                            if st.session_state[_submode_key]=="Manuali":
                                _fonts=_gsf_windows_fonts()
                                _font_key=f"inline_font_{_this_inline_id}"
                                _size_key=f"inline_subsize_{_this_inline_id}"
                                _sx=f"inline_subx_{_this_inline_id}"
                                _sy=f"inline_suby_{_this_inline_id}"
                                if _font_key not in st.session_state: st.session_state[_font_key]="Arial"
                                if st.session_state[_font_key] not in _fonts: st.session_state[_font_key]="Arial"
                                if _size_key not in st.session_state: st.session_state[_size_key]=92
                                if _sx not in st.session_state: st.session_state[_sx]=50
                                if _sy not in st.session_state: st.session_state[_sy]=78

                                _fontc,_aspectc,_posc=st.columns([.40,.30,.30],gap="small")
                                with _fontc:
                                    _font_widget_key=f"inline_font_widget_v18_{_this_inline_id}"
                                    st.selectbox(
                                        "🔤 Font",_fonts,index=_fonts.index(st.session_state[_font_key]),
                                        key=_font_widget_key,
                                        on_change=_gsf_sync_inline_subtitle_font,
                                        args=(_font_widget_key,_font_key)
                                    )
                                with _aspectc:
                                    with st.popover("📐 ASPETTO",use_container_width=True):
                                        st.slider("Dimensione",48,140,int(st.session_state.get(f"inline_subsize_widget_v18_{_this_inline_id}",st.session_state[_size_key])),2,key=f"inline_subsize_widget_v18_{_this_inline_id}")
                                        c1,c2,c3=st.columns(3,gap="small")
                                        with c1:
                                            st.session_state["subtitle_text_color"]=st.color_picker("Testo",st.session_state.get("subtitle_text_color","#FFFFFF"),key=f"inline_txtcol_v18_{_this_inline_id}")
                                        with c2:
                                            st.session_state["subtitle_active_color"]=st.color_picker("Attiva",st.session_state.get("subtitle_active_color","#FFD400"),key=f"inline_actcol_v18_{_this_inline_id}")
                                        with c3:
                                            st.session_state["subtitle_outline_color"]=st.color_picker("Bordo",st.session_state.get("subtitle_outline_color","#000000"),key=f"inline_outcol_v18_{_this_inline_id}")
                                with _posc:
                                    with st.popover("📍 POSIZIONE",use_container_width=True):
                                        st.slider("↔ X",5,95,int(st.session_state.get(f"inline_subx_widget_v18_{_this_inline_id}",st.session_state[_sx])),1,key=f"inline_subx_widget_v18_{_this_inline_id}")
                                        st.slider("↕ Y",5,95,int(st.session_state.get(f"inline_suby_widget_v18_{_this_inline_id}",st.session_state[_sy])),1,key=f"inline_suby_widget_v18_{_this_inline_id}")
                                st.markdown("##### ✏️ Trascrizione intelligente",help="Resta salvata mentre modifichi font, colori, posizione o gli strumenti.")
                                if not st.session_state.get(_trans_words_key):
                                    if st.button("TRASCRIVI LA CLIP",use_container_width=True,key=f"inline_transcribe_v18_{_this_inline_id}"):
                                        with st.spinner("Trascrivo la clip..."):
                                            _words,_err=_gsf_transcribe_editor_scene(_ii,_istart,_ilen)
                                        if _err:
                                            st.warning(f"Trascrizione non disponibile: {_err}")
                                        else:
                                            st.session_state[_trans_words_key]=list(_words)
                                            st.session_state[_trans_live_key]=list(_words)
                                            st.session_state[_trans_text_key]=" ".join(w["text"] for w in _words)
                                            st.session_state[f"inline_applied_text_{_this_inline_id}"]=st.session_state[_trans_text_key]
                                            st.session_state[f"inline_seek_{_this_inline_id}"]=_istart
                                            st.rerun()
                                else:
                                    _tw=st.session_state.get(_trans_words_key,[])
                                    if _tw:
                                        _time_opts=[]
                                        for _group in _gsf_subtitle_groups(_tw):
                                            _t=float(_group[0]["start"])
                                            _preview=" ".join(w["text"] for w in _group)
                                            _time_opts.append((_t,f"{int(_t//60):02d}:{(_t%60):05.2f} · {_preview}"))
                                        _tc_col,_go_col=st.columns([.82,.18],gap="small")
                                        with _tc_col:
                                            _chosen_label=st.selectbox(
                                                "⏱ Vai al testo",[x[1] for x in _time_opts],
                                                key=f"inline_time_nav_v22_{_this_inline_id}"
                                            )
                                        with _go_col:
                                            st.write("")
                                            if st.button("VAI",use_container_width=True,key=f"inline_time_go_v22_{_this_inline_id}"):
                                                _chosen_t=next(t for t,label in _time_opts if label==_chosen_label)
                                                st.session_state[f"inline_seek_{_this_inline_id}"]=float(_chosen_t)
                                                st.session_state[f"inline_seek_feedback_{_this_inline_id}"]=float(_chosen_t)
                                                st.session_state[f"inline_seek_nonce_{_this_inline_id}"]=int(
                                                    st.session_state.get(f"inline_seek_nonce_{_this_inline_id}",0)
                                                )+1
                                                st.rerun()
                                    if f"inline_seek_feedback_{_this_inline_id}" in st.session_state:
                                        _ft=float(st.session_state[f"inline_seek_feedback_{_this_inline_id}"])
                                        st.caption(f"✓ Anteprima posizionata a {int(_ft//60):02d}:{(_ft%60):05.2f}")
                                    _edited=st.text_area(
                                        "Correggi, elimina o aggiungi parole",
                                        value=st.session_state.get(_trans_text_key,""),
                                        height=125,key=f"inline_textarea_v18_{_this_inline_id}"
                                    )
                                    _inline_applied_key=f"inline_applied_text_{_this_inline_id}"
                                    _inline_is_applied=(_edited==st.session_state.get(_inline_applied_key,st.session_state.get(_trans_text_key,"")))
                                    _inline_apply_label="✓ APPLICATO" if _inline_is_applied else "✓ APPLICA"
                                    if st.button(_inline_apply_label,type="primary",use_container_width=True,key=f"inline_apply_subs_v26_{_this_inline_id}",disabled=_inline_is_applied):
                                        st.session_state[_trans_text_key]=_edited
                                        st.session_state[_inline_applied_key]=_edited
                                        _tokens=_edited.split()
                                        _timed=st.session_state.get(_trans_words_key,[])
                                        _live=[]
                                        for _i,_w in enumerate(_timed):
                                            if _i<len(_tokens):
                                                _live.append({"text":_tokens[_i],"start":_w["start"],"end":_w["end"]})
                                        st.session_state[_trans_live_key]=_live
                                        st.rerun()

                        # Azioni dell'editor inline.
                        _ec1,_ec2=st.columns(2,gap="small")
                        with _ec1:
                            if st.button("🎞️ CREA VIDEO",type="primary",use_container_width=True,key=f"inline_create_{_this_inline_id}"):
                                _out=os.path.join(_idir,"inline_edit_final.mp4")
                                _original_source=st.session_state.get(
                                    "inline_editor_original_input",_ii
                                )
                                _source_base=float(
                                    st.session_state.get("inline_editor_source_start",0.0)
                                )
                                _render_start=(
                                    _source_base+_istart
                                    if _original_source!=_ii else _istart
                                )
                                _inline_sub_mode=st.session_state.get(
                                    _submode_key,"Automatici"
                                )
                                _inline_sub_words=(
                                    st.session_state.get(
                                        _trans_live_key,
                                        st.session_state.get(_trans_words_key,[])
                                    )
                                    if _inline_sub_mode=="Manuali" else []
                                )

                                with st.spinner("Creo il video finale dal file originale..."):
                                    _r=_gsf_render_core(
                                        _original_source,
                                        _out,
                                        _render_start,
                                        _ilen,
                                        fmt=st.session_state[_fmt_key],
                                        zoom=st.session_state[_zoom_key],
                                        x_pos=st.session_state[_x_key],
                                        y_pos=st.session_state[_y_key],
                                        brightness=st.session_state[_bri_key],
                                        contrast=st.session_state[_con_key],
                                        speed=st.session_state[_spd_key],
                                        volume=st.session_state[_vol_key],
                                        subtitles_enabled=(_inline_sub_mode!="Nessuno"),
                                        subtitle_mode=_inline_sub_mode,
                                        subtitle_words=_inline_sub_words,
                                        subtitle_text=st.session_state.get(_trans_text_key,""),
                                        subtitle_time_origin=_istart,
                                        subtitle_font=st.session_state.get(
                                            f"inline_font_widget_v18_{_this_inline_id}",
                                            st.session_state.get(
                                                f"inline_font_{_this_inline_id}","Arial"
                                            )
                                        ),
                                        subtitle_size=st.session_state.get(
                                            f"inline_subsize_widget_v18_{_this_inline_id}",
                                            st.session_state.get(
                                                f"inline_subsize_{_this_inline_id}",92
                                            )
                                        ),
                                        subtitle_x=st.session_state.get(
                                            f"inline_subx_widget_v18_{_this_inline_id}",50
                                        ),
                                        subtitle_y=st.session_state.get(
                                            f"inline_suby_widget_v18_{_this_inline_id}",78
                                        ),
                                        text_color=st.session_state.get(
                                            f"inline_txtcol_v18_{_this_inline_id}","#FFFFFF"
                                        ),
                                        active_color=st.session_state.get(
                                            f"inline_actcol_v18_{_this_inline_id}","#FFD400"
                                        ),
                                        outline_color=st.session_state.get(
                                            f"inline_outcol_v18_{_this_inline_id}","#000000"
                                        ),
                                        normalize_audio=True,
                                        smart_reframe=False,
                                        hook_text="",
                                        polish_audio=True
                                    )
                                if _r.get("ok") and os.path.exists(_out):
                                    with open(_out,"rb") as _f:
                                        st.session_state["inline_final_bytes"]=_f.read()
                                    st.session_state["publication_final_bytes"]=st.session_state["inline_final_bytes"]
                                    st.session_state["publication_ready"]=True
                                    st.session_state["publication_source"]="inline_editor"
                                    st.success(
                                        f"Video creato · {_r.get('encoder','')} · "
                                        f"{_r.get('seconds',0):.1f}s"
                                    )
                                else:
                                    st.error("Creazione video non riuscita.")
                                    if _r.get("error"):
                                        st.code(_r.get("error","")[-2500:])
                        with _ec2:
                            _inline_master_ready=bool(
                                st.session_state.get("inline_final_bytes")
                            )
                            if st.button(
                                "✓ USA QUESTA",
                                use_container_width=True,
                                key=f"inline_use_{_this_inline_id}",
                                disabled=not _inline_master_ready
                            ):
                                st.session_state["publication_ready"]=True
                                st.session_state["publication_source"]="inline_editor"
                                st.session_state["publication_preview_bytes"]=st.session_state.get(
                                    "inline_final_bytes"
                                )
                                st.session_state["publication_final_bytes"]=st.session_state.get(
                                    "inline_final_bytes"
                                )
                                st.rerun()
                            if not _inline_master_ready:
                                st.caption("Prima crea il video finale.")
        else:
            start = 0.0

    # La clip AI si modifica soltanto nell'Editor completo.
    _ai_selected_start = st.session_state.get("auto_clip_scelta")

    if st.session_state.get("publication_ready") and st.session_state.get("publication_source")=="ai_clip":
        st.markdown("#### 🎬 Esporta")
        st.caption(
            "La preview serve solo per scegliere la scena. "
            "Il file finale viene sempre creato dal gameplay originale."
        )

        if st.button(
            "🎞️ CREA SHORT FINALE",
            type="primary",
            use_container_width=True,
            key="render_ai_selected_v41"
        ):
            _pub_dir=tempfile.mkdtemp(prefix="gsf_ai_final_")
            _pub_source=os.path.join(_pub_dir,"source_original.mp4")
            _pub_out=os.path.join(_pub_dir,"gaming_short_ai_final.mp4")
            with open(_pub_source,"wb") as _pf:
                _pf.write(video.getbuffer())

            _pub_start=float(st.session_state.get("auto_clip_scelta",0.0) or 0.0)
            _pub_duration=float(
                st.session_state.get("auto_clip_duration",duration) or duration
            )
            _pub_subtitles=bool(
                st.session_state.get("project_subtitles_enabled",True)
            )
            _pub_master_token=_gsf_upload_master_token(video)

            with st.spinner("🎬 Render finale dal file originale..."):
                _pub_result=_gsf_render_auto_master(
                    _pub_source,
                    _pub_start,
                    _pub_duration,
                    master_token=_pub_master_token,
                    subtitles_enabled=_pub_subtitles,
                    manual_hook=st.session_state.get("hook_testo",""),
                    output_path=_pub_out
                )

            if _pub_result.get("ok"):
                st.session_state["publication_final_bytes"]=_pub_result.get("bytes",b"")
                st.session_state["publication_final_signature"]=_pub_result.get("signature","")
                st.session_state["publication_final_encoder"]=_pub_result.get("encoder","")
                st.session_state["publication_final_seconds"]=_pub_result.get("seconds",0)
                _rf=_pub_result.get("smart_reframe") or {}
                _rf_text=(
                    f" · Smart Reframe {int(float(_rf.get('confidence',0))*100)}%"
                    if _rf.get("enabled") else " · crop centrale"
                )
                _hook_info=(
                    f" · Hook: {_pub_result.get('hook_text','')}"
                    if _pub_result.get("hook_text") else ""
                )
                _cache_text=" · master riusato" if _pub_result.get("cache_hit") else ""
                _sig_text=(
                    f" · {_pub_result.get('signature','')[:8]}"
                    if _pub_result.get("signature") else ""
                )
                st.success(
                    f"✅ Short finale pronto · {_pub_result.get('encoder','')} · "
                    f"{_pub_result.get('seconds',0):.1f}s"
                    f"{_rf_text}{_hook_info}{_cache_text}{_sig_text}"
                )
            else:
                st.error("Render finale non riuscito.")
                if _pub_result.get("error"):
                    st.code(_pub_result.get("error","")[-2500:])

        _final_ai=st.session_state.get("publication_final_bytes")
        if _final_ai:
            _final_ai_path=_gsf_bytes_to_preview(_final_ai,"ai_final_v41")
            render_gsf_player(_final_ai_path,"ai_final_v41")
            st.download_button(
                "⬇️ SCARICA SHORT FINALE",
                _final_ai,
                "gaming_short_ai_final.mp4",
                "video/mp4",
                use_container_width=True,
                key="export_ai_selected_final_v41"
            )

        st.markdown("#### 🚀 Pubblicazione")
        st.success("Clip scelta. Il master finale usa sempre il video originale.")
        st.caption("Titolo, descrizione e pubblicazione diretta arriveranno nel punto successivo.")

    # Nelle modalità AI l'utente non deve micro-gestire i sottotitoli:
    # l'AI usa automaticamente il preset completo.
    _manual_editor_mode = (modalita == "✋ Manuale")

    _project_subtitles_enabled = bool(
        st.session_state.get("project_subtitles_enabled", False if modalita != "✋ Manuale" and _ai_selected_start is None else True)
    )
    if _manual_editor_mode:
        sottotitoli = _project_subtitles_enabled
        stile_sub = "Base"
        dimensione_sub = int(st.session_state.get("editor_sub_size", 92))
        posizione_sub = int(st.session_state.get("editor_sub_position", 330))
    else:
        # Vale anche per i motori AI: se il progetto è senza sottotitoli,
        # nessun motore deve reinserirli.
        sottotitoli = _project_subtitles_enabled
        stile_sub = "Base"
        dimensione_sub = int(st.session_state.get("editor_sub_size", 92))
        posizione_sub = int(st.session_state.get("editor_sub_position", 330))

    # Motori tecnici sempre attivi: non sono più opzioni dell'interfaccia.
    smart_reframe = True
    analisi_rapida = True
    normalizza_audio = True


    # Manteniamo valori interni compatibili con il flusso esistente.
    gioco = st.session_state.get("gioco", "ARC Raiders")
    piattaforma = st.session_state.get("piattaforma", "YouTube Shorts")
    tono_social = st.session_state.get("tono_social", "Gaming forte")
    hook_testo = st.session_state.get("hook_testo", "")


    # ==========================================================
    # BATCH — CREA TUTTI I MOMENTI TROVATI
    # ==========================================================

    candidati_batch = st.session_state.get("auto_clip_candidati", [])

    if modalita in ["🚀 AUTO TOTALE", "🎬 AI Director"]:
        # L'AI può mostrare 5 candidati, ma il batch crea i 3 migliori.
        candidati_batch = candidati_batch[:3]

    if modalita != "✋ Manuale" and candidati_batch:

        st.divider()
        st.markdown('<div class="soft-card"><div class="mini-label">SELEZIONE AI</div><h2 style="margin:.35rem 0 0;">Momenti migliori</h2></div>', unsafe_allow_html=True)

        st.write(
            f"Pronti **{len(candidati_batch)} momenti**. "
            "Puoi creare tutti gli Shorts in una volta."
        )

        if st.button(
            "✦ GENERA I 3 SHORTS",
            type="primary",
            use_container_width=True
        ):

            batch_bar = st.progress(0)
            batch_status = st.empty()

            # Conserviamo i bytes in session_state, perché la temp
            # directory viene eliminata alla fine.
            risultati_batch = []

            with tempfile.TemporaryDirectory() as batch_temp:

                batch_input = os.path.join(
                    batch_temp,
                    "batch_input.mp4"
                )

                with open(batch_input, "wb") as f:
                    f.write(video.getbuffer())

                totale_batch = len(candidati_batch)

                for indice, inizio_clip in enumerate(
                    candidati_batch,
                    start=1
                ):

                    batch_status.write(
                        f"🎬 Creo Short {indice}/{totale_batch}..."
                    )

                    durata_batch = float(duration)

                    if modalita in ["🚀 AUTO TOTALE", "🎬 AI Director"]:
                        durata_batch = float(
                            st.session_state.get(
                                "clip_rifinite",
                                {}
                            ).get(round(float(inizio_clip), 3), duration)
                        )

                    _batch_manual_hook=st.session_state.get("hook_testo","")
                    _batch_master_token=_gsf_upload_master_token(video)

                    output_batch = crea_short_batch(
                        batch_input,
                        batch_temp,
                        float(inizio_clip),
                        durata_batch,
                        indice,
                        sottotitoli,
                        normalizza_audio,
                        stile_sub,
                        dimensione_sub,
                        posizione_sub,
                        hook_text=_batch_manual_hook,
                        master_token=_batch_master_token
                    )

                    if output_batch and os.path.exists(output_batch):
                        with open(output_batch, "rb") as f:
                            risultati_batch.append(
                                (
                                    indice,
                                    float(inizio_clip),
                                    f.read()
                                )
                            )

                    batch_bar.progress(
                        int(indice / totale_batch * 100)
                    )

            st.session_state.risultati_batch = risultati_batch

            if risultati_batch:
                batch_status.write(
                    f"✅ Creati {len(risultati_batch)} Shorts."
                )
            else:                batch_status.write(
                    "❌ Non sono riuscito a creare gli Shorts."
                )

        risultati_batch = st.session_state.get(
            "risultati_batch",
            []
        )

        if risultati_batch:

            st.subheader("📦 Shorts pronti")

            for indice, inizio_clip, dati_video in risultati_batch:

                st.write(
                    f"### Short {indice} — da {inizio_clip:.0f}s"
                )

                _batch_path = _gsf_bytes_to_preview(
                    dati_video, f"batch_short_{indice}"
                )
                render_gsf_player(_batch_path, f"batch_short_{indice}")

                st.download_button(
                    f"⬇️ Scarica Short {indice}",
                    dati_video,
                    f"gaming_short_{indice}.mp4",
                    "video/mp4",
                    key=f"download_batch_{indice}"
                )

            # ZIP unico con tutti gli Shorts
            import io
            import zipfile

            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(
                zip_buffer,
                "w",
                zipfile.ZIP_DEFLATED
            ) as archivio:

                for indice, inizio_clip, dati_video in risultati_batch:
                    archivio.writestr(
                        f"gaming_short_{indice}.mp4",
                        dati_video
                    )

                _master_profile=_gsf_auto_master_profile(
                    subtitles_enabled=bool(sottotitoli)
                )
                _master_token=_gsf_upload_master_token(video)
                _manifest_lines=[
                    "Gaming Shorts Factory — MASTER V44",
                    f"Gioco: {gioco}",
                    f"Piattaforma: {piattaforma}",
                    f"Modalità: {modalita}",
                    f"Short creati: {len(risultati_batch)}",
                ]
                for _idx,_start,_bytes in risultati_batch:
                    _dur=float(duration)
                    if modalita in ["🚀 AUTO TOTALE","🎬 AI Director"]:
                        _dur=float(
                            st.session_state.get("clip_rifinite",{}).get(
                                round(float(_start),3),duration
                            )
                        )
                    _hook=_gsf_auto_hook_for_start(
                        float(_start),
                        manual_hook=st.session_state.get("hook_testo","")
                    )
                    _sig=_gsf_master_signature(
                        _master_token,float(_start),_dur,_master_profile,_hook
                    )
                    _manifest_lines.append(
                        f"Short {_idx}: {_start:.2f}s | master {_sig}"
                    )
                manifest="\n".join(_manifest_lines)+"\n"
                archivio.writestr("INFO.txt", manifest)

            st.download_button(
                "📦 SCARICA TUTTI (.ZIP)",
                zip_buffer.getvalue(),
                "gaming_shorts.zip",
                "application/zip",
                use_container_width=True
            )

        st.divider()
        st.caption(
            "Oppure crea soltanto la clip selezionata:"
        )        )        )        )