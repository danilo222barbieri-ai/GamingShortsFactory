import streamlit as st
import subprocess
import sys
import os
import json
import tempfile
import re
import math
import time
import hashlib
import shutil
import io
import zipfile
import threading
import socket
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import quote, urlencode, urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import secrets
import webbrowser
import importlib.util
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit.components.v1 as components
from faster_whisper import WhisperModel

try:
    import numpy as np
except Exception:
    np = None


st.markdown("""
<style id="gsf-v80-ui-fix">
/* Elimina la fascia vuota di Streamlit sopra l'app (desktop + mobile). */
[data-testid="stHeader"],
header[data-testid="stHeader"]{
    height:0 !important;
    min-height:0 !important;
    max-height:0 !important;
    visibility:hidden !important;
    overflow:hidden !important;
    background:transparent !important;
}
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu{
    display:none !important;
}
[data-testid="stAppViewContainer"]{
    padding-top:0 !important;
}
[data-testid="stAppViewContainer"] > .main{
    padding-top:0 !important;
}
.block-container{
    padding-top:.30rem !important;
}

/* Safari/iOS non deve trasformare i controlli dell'Editor in pulsanti scuri. */
:root, html, body, .stApp, [data-testid="stAppViewContainer"]{
    color-scheme:light !important;
}

@media(max-width:750px){
    html, body, .stApp, [data-testid="stAppViewContainer"]{
        background:#F7FBFE !important;
    }
    .block-container{
        padding-top:.20rem !important;
        padding-left:.72rem !important;
        padding-right:.72rem !important;
    }

    /* Segmenti Formato / Sottotitoli: contrasto leggibile su iPhone. */
    .st-key-editor_format button,
    .st-key-editor_sub_mode_v18 button{
        background:#FFFFFF !important;
        color:#17324A !important;
        border-color:#BFD7E8 !important;
        min-height:2.65rem !important;
        font-weight:700 !important;
        box-shadow:none !important;
    }
    .st-key-editor_format button[aria-pressed="true"],
    .st-key-editor_sub_mode_v18 button[aria-pressed="true"]{
        background:#EAF5FD !important;
        color:#0E2D46 !important;
        border-color:#56AEDD !important;
    }
    .st-key-editor_format button p,
    .st-key-editor_sub_mode_v18 button p{
        color:inherit !important;
    }

    /* Popover INQUADRATURA / REGOLAZIONI / POSIZIONE. */
    [data-testid="stPopover"] > button,
    [data-testid="stPopover"] > button p{
        background:#FFFFFF !important;
        color:#17324A !important;
    }
    [data-testid="stPopover"] > button{
        border:1px solid #BFD7E8 !important;
        min-height:2.70rem !important;
        height:auto !important;
        padding:.35rem .70rem !important;
        border-radius:14px !important;
        box-shadow:none !important;
    }

    /* Bottoni Editor: compatti ma ancora comodi da toccare. */
    .st-key-reset_main_all_v29 button,
    .st-key-editor_transcribe_scene_v18 button,
    .st-key-editor_use_changes_v54 button,
    .st-key-retry_auto_sub_v80 button{
        min-height:2.75rem !important;
        height:auto !important;
        padding:.38rem .75rem !important;
        border-radius:14px !important;
    }

    /* Rimuove le frecce decorative che su mobile sembravano pulsanti "avanti". */
    .st-key-reset_main_all_v29 button::before,
    .st-key-editor_transcribe_scene_v18 button::before,
    .st-key-editor_use_changes_v54 button::before,
    .st-key-retry_auto_sub_v80 button::before,
    [data-testid="stPopover"] > button::before{
        display:none !important;
        content:none !important;
        width:0 !important;
        height:0 !important;
        margin:0 !important;
    }

    /* Mantieni leggibile anche il testo dei pulsanti custom. */
    .st-key-reset_main_all_v29 button,
    .st-key-editor_transcribe_scene_v18 button,
    .st-key-retry_auto_sub_v80 button{
        background:#FFFFFF !important;
        color:#17324A !important;
        border:1px solid #9FCDEA !important;
    }
    .st-key-reset_main_all_v29 button p,
    .st-key-editor_transcribe_scene_v18 button p,
    .st-key-retry_auto_sub_v80 button p{
        color:#17324A !important;
    }

    .st-key-editor_use_changes_v54 button{
        color:#102C45 !important;
    }
    .st-key-editor_use_changes_v54 button p{
        color:inherit !important;
    }
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style id="gsf-v81-mobile-tablet-polish">
/* Upload: il cerchio deve comunicare chiaramente che sta lavorando. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
    position:relative !important;
    overflow:visible !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::after{
    content:"";
    position:absolute;
    inset:-7px;
    border-radius:999px;
    border:5px solid transparent;
    pointer-events:none;
    opacity:0;
    box-sizing:border-box;
    z-index:4;
}
@keyframes gsfV81UploadRing{
    from{transform:rotate(0deg)}
    to{transform:rotate(360deg)}
}
/* Streamlit espone un progressbar durante l'upload: anello verde animato. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([role="progressbar"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="Progress"])
[data-testid="stFileUploaderDropzone"]::after{
    opacity:1;
    border-top-color:#22C55E;
    border-right-color:#22C55E;
    border-bottom-color:rgba(34,197,94,.22);
    border-left-color:rgba(34,197,94,.22);
    animation:gsfV81UploadRing .85s linear infinite;
    filter:drop-shadow(0 0 5px rgba(34,197,94,.28));
}
/* Upload completato: anello verde pieno. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::after{
    opacity:1;
    border-color:#22C55E;
    animation:none;
    filter:drop-shadow(0 0 5px rgba(34,197,94,.25));
}

/* Tablet/mobile: tutti i player custom devono restare centrati. */
@media(max-width:1100px){
    iframe{
        display:block !important;
        margin-left:auto !important;
        margin-right:auto !important;
    }
    .st-key-v81_new_video button{
        min-height:2.55rem !important;
        border-radius:14px !important;
    }
}
</style>
""",unsafe_allow_html=True)





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


# ============================================================
# V77 — WEB RUNTIME / SESSION ISOLATION
# ============================================================
# Ogni visitatore anonimo lavora in una cartella server separata.
# Nessun account richiesto: lo stato resta temporaneo e viene eliminato
# automaticamente dopo un periodo di inattivita.
GSF_WEB_MODE = str(os.environ.get("GSF_WEB_MODE", "0")).strip().lower() in ("1", "true", "yes", "on")
# V78 MOBILE BETA — profilo memoria prudente per hosting web/mobile.
# Sul desktop locale resta invariato. Su Railway evita che la prima analisi AI
# saturi il container da ~1 GB caricando Whisper durante lo scan iniziale.
GSF_LOW_MEMORY_WEB = str(
    os.environ.get("GSF_LOW_MEMORY_WEB", "1" if GSF_WEB_MODE else "0")
).strip().lower() in ("1", "true", "yes", "on")
GSF_AI_VOICE_TRANSCRIPTION = str(
    os.environ.get("GSF_AI_VOICE_TRANSCRIPTION", "0" if GSF_LOW_MEMORY_WEB else "1")
).strip().lower() in ("1", "true", "yes", "on")
GSF_SESSION_TTL_SECONDS = max(1800, int(os.environ.get("GSF_SESSION_TTL_SECONDS", "7200") or 7200))
GSF_RUNTIME_ROOT = Path(
    os.environ.get(
        "GSF_RUNTIME_ROOT",
        str(Path(tempfile.gettempdir()) / "gaming_shorts_factory_web")
    )
).expanduser().resolve()
GSF_SESSIONS_ROOT = GSF_RUNTIME_ROOT / "sessions"
GSF_OAUTH_STATE_ROOT = GSF_RUNTIME_ROOT / "oauth_states"
GSF_SESSIONS_ROOT.mkdir(parents=True, exist_ok=True)
GSF_OAUTH_STATE_ROOT.mkdir(parents=True, exist_ok=True)


def _gsf_query_value(name):
    try:
        value = st.query_params.get(name)
        if isinstance(value, (list, tuple)):
            value = value[0] if value else ""
        return str(value or "")
    except Exception:
        return ""


def _gsf_safe_session_id(value):
    value = re.sub(r"[^A-Za-z0-9_-]+", "", str(value or ""))
    return value[:64]


def _gsf_session_id():
    """
    V79: anonymous session recovery survives a Streamlit reconnect.
    Priority: OAuth state -> existing Streamlit state -> Nginx HttpOnly cookie
    -> optional URL fallback -> new cryptographic id.
    """
    callback_state = re.sub(r"[^A-Za-z0-9_-]+", "", _gsf_query_value("state"))[:160]
    if callback_state:
        state_file = GSF_OAUTH_STATE_ROOT / (callback_state + ".json")
        try:
            payload = json.loads(state_file.read_text(encoding="utf-8"))
            created = float(payload.get("created", 0) or 0)
            recovered = _gsf_safe_session_id(payload.get("session_id", ""))
            if recovered and created and time.time() - created <= 900:
                st.session_state["gsf_web_session_id"] = recovered
        except Exception:
            pass

    current = _gsf_safe_session_id(st.session_state.get("gsf_web_session_id", ""))

    if not current and GSF_WEB_MODE:
        try:
            current = _gsf_safe_session_id(
                st.context.headers.get("X-GSF-Session-ID", "")
            )
        except Exception:
            current = ""

    if not current and GSF_WEB_MODE:
        current = _gsf_safe_session_id(_gsf_query_value("sid"))

    if not current:
        current = secrets.token_urlsafe(24).replace("-", "_")[:36]

    st.session_state["gsf_web_session_id"] = current
    return current


GSF_SESSION_ID = _gsf_session_id()
GSF_SESSION_ROOT = GSF_SESSIONS_ROOT / GSF_SESSION_ID
GSF_PREVIEW_DIR = GSF_SESSION_ROOT / "media"
GSF_SESSION_TMP_DIR = GSF_SESSION_ROOT / "tmp"
GSF_SESSION_EXPORT_DIR = GSF_SESSION_ROOT / "export"
GSF_SESSION_SOCIAL_DIR = GSF_SESSION_ROOT / "social"
for _dir in (GSF_PREVIEW_DIR, GSF_SESSION_TMP_DIR, GSF_SESSION_EXPORT_DIR, GSF_SESSION_SOCIAL_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# V79 — small durable snapshot of JSON-safe UI state.
# This is not an account or permanent cloud project: it only lets the same
# anonymous browser recover after a websocket/process reconnect during beta.
GSF_SESSION_STATE_FILE = GSF_SESSION_ROOT / "session_state.json"
_GSF_STATE_SKIP_EXACT = {
    "upload_v73", "gsf_web_session_id",
}
_GSF_STATE_SKIP_PARTS = (
    "secret", "password", "access_token", "refresh_token", "client_secret",
    "oauth", "credential", "inline_final_bytes", "editor_output_bytes",
    "editor_quick_bytes", "source_bytes",
    "upload_v73",
)

def _gsf_persistable_state_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (list, tuple)):
        if len(value) > 5000:
            raise ValueError("list too large")
        return [_gsf_persistable_state_value(x) for x in value]
    if isinstance(value, dict):
        if len(value) > 1000:
            raise ValueError("dict too large")
        return {
            str(k): _gsf_persistable_state_value(v)
            for k, v in value.items()
            if isinstance(k, (str, int, float, bool))
        }
    raise TypeError(type(value).__name__)


_GSF_TRANSIENT_WIDGET_EXACT = ['create_final_short_v54', 'download_final_v54', 'editor_apply_subs_v26', 'editor_time_go_v22', 'editor_transcribe_scene_v18', 'editor_use_changes_v54', 'open_publish_v54', 'reset_main_all_v29', 'retry_auto_sub_v80', 'v75_cancel_engine_switch', 'v75_confirm_engine_switch']
_GSF_TRANSIENT_WIDGET_PREFIXES = ('edit_ai_', 'inline_apply_subs_v26_', 'inline_close_', 'inline_time_go_v22_', 'inline_transcribe_v18_', 'inline_use_changes_v54_', 'reset_inline_all_v29_', 'result_download_', 'result_edit_', 'use_ai_', 'v69_choose_', 'v71_choose_short_')

def _gsf_is_transient_widget_key(key):
    key=str(key or "")
    return (
        key in _GSF_TRANSIENT_WIDGET_EXACT
        or any(key.startswith(prefix) for prefix in _GSF_TRANSIENT_WIDGET_PREFIXES)
    )

def _gsf_restore_persistent_state():
    if not GSF_WEB_MODE or st.session_state.get("_gsf_v79_state_restored"):
        return
    st.session_state["_gsf_v79_state_restored"] = True
    try:
        payload = json.loads(GSF_SESSION_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(payload, dict):
        return
    for key, value in payload.items():
        if key in st.session_state or key in _GSF_STATE_SKIP_EXACT:
            continue
        if _gsf_is_transient_widget_key(key):
            continue
        if any(part in str(key).lower() for part in _GSF_STATE_SKIP_PARTS):
            continue
        try:
            st.session_state[key] = value
        except Exception:
            pass

def _gsf_save_persistent_state():
    if not GSF_WEB_MODE:
        return
    payload = {}
    total = 2
    for key, value in list(st.session_state.items()):
        key = str(key)
        if key.startswith("_") or key in _GSF_STATE_SKIP_EXACT:
            continue
        if _gsf_is_transient_widget_key(key):
            continue
        if any(part in key.lower() for part in _GSF_STATE_SKIP_PARTS):
            continue
        try:
            safe = _gsf_persistable_state_value(value)
            encoded = json.dumps(safe, ensure_ascii=False, separators=(",", ":"))
        except Exception:
            continue
        if len(encoded) > 180000 or total + len(encoded) > 900000:
            continue
        payload[key] = safe
        total += len(encoded)
    try:
        tmp = Path(str(GSF_SESSION_STATE_FILE) + ".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, GSF_SESSION_STATE_FILE)
    except Exception:
        pass

def _gsf_find_recovered_source():
    candidate = str(st.session_state.get("gsf_source_path", "") or "")
    if candidate and Path(candidate).is_file():
        return Path(candidate)
    try:
        files = [
            p for p in GSF_PREVIEW_DIR.glob("source_gaming_short_*")
            if p.is_file() and p.suffix.lower() in (".mp4", ".mov", ".mkv")
        ]
        if files:
            return max(files, key=lambda p: p.stat().st_mtime)
    except Exception:
        pass
    return None

class _GSFRecoveredUpload:
    """Small adapter used only when a browser reconnects after upload."""
    def __init__(self, path, display_name=""):
        self._gsf_recovered_path = str(Path(path))
        self.name = str(display_name or Path(path).name)
        self.type = {
            ".mov": "video/quicktime",
            ".mkv": "video/x-matroska",
        }.get(Path(path).suffix.lower(), "video/mp4")
        try:
            self.size = Path(path).stat().st_size
        except OSError:
            self.size = 0
        self._fh = None
    def __bool__(self):
        return bool(self._gsf_recovered_path and Path(self._gsf_recovered_path).is_file())
    def _file(self):
        if self._fh is None or self._fh.closed:
            self._fh = open(self._gsf_recovered_path, "rb")
        return self._fh
    def read(self, size=-1):
        return self._file().read(size)
    def seek(self, offset, whence=0):
        return self._file().seek(offset, whence)
    def tell(self):
        return self._file().tell()
    def getvalue(self):
        return Path(self._gsf_recovered_path).read_bytes()
    def getbuffer(self):
        return memoryview(self.getvalue())

# V81: reset sicuro della lavorazione corrente per poter caricare un nuovo
# video anche dopo il ripristino automatico della sessione.
def _gsf_start_new_video():
    old_generation=int(st.session_state.get("gsf_upload_generation",0) or 0)

    keep_exact={"gsf_web_session_id"}
    keep_parts=("youtube","tiktok","instagram","social","oauth")

    for _key in list(st.session_state.keys()):
        _ks=str(_key)
        _low=_ks.lower()
        if _ks.startswith("_") or _ks in keep_exact:
            continue
        if any(part in _low for part in keep_parts):
            continue
        try:
            st.session_state.pop(_key,None)
        except Exception:
            pass

    st.session_state["gsf_upload_generation"]=old_generation+1

    # V98.8: free AI / Whisper memory before the next Streamlit upload.
    try:
        _gsf_v93_release_analysis_memory()
    except Exception:
        try:
            import gc
            gc.collect()
        except Exception:
            pass

    try:
        GSF_SESSION_STATE_FILE.unlink(missing_ok=True)
    except Exception:
        pass

    # Pulisce solo i file della lavorazione video. I token social restano.
    for _root in (GSF_PREVIEW_DIR,GSF_SESSION_TMP_DIR,GSF_SESSION_EXPORT_DIR):
        try:
            for _p in sorted(_root.rglob("*"),key=lambda p:len(p.parts),reverse=True):
                try:
                    if _p.is_file() or _p.is_symlink():
                        _p.unlink(missing_ok=True)
                    elif _p.is_dir():
                        _p.rmdir()
                except Exception:
                    pass
            _root.mkdir(parents=True,exist_ok=True)
        except Exception:
            pass

# Questo pulsante viene aggiunto dopo V80.1, quindi lo registriamo
# esplicitamente come widget transitorio da NON persistere.
try:
    if "v81_new_video" not in _GSF_TRANSIENT_WIDGET_EXACT:
        _GSF_TRANSIENT_WIDGET_EXACT.append("v81_new_video")
except Exception:
    pass

try:
    if "v70_duration_" not in _GSF_TRANSIENT_WIDGET_PREFIXES:
        _GSF_TRANSIENT_WIDGET_PREFIXES=tuple(_GSF_TRANSIENT_WIDGET_PREFIXES)+("v70_duration_",)
except Exception:
    pass

_gsf_restore_persistent_state()


def _gsf_touch_session():
    try:
        marker = GSF_SESSION_ROOT / ".active"
        marker.touch(exist_ok=True)
    except OSError:
        pass


def _gsf_cleanup_expired_sessions():
    now = time.time()
    try:
        for folder in GSF_SESSIONS_ROOT.iterdir():
            if not folder.is_dir() or folder.name == GSF_SESSION_ID:
                continue
            marker = folder / ".active"
            try:
                last = marker.stat().st_mtime if marker.exists() else folder.stat().st_mtime
            except OSError:
                continue
            if now - last > GSF_SESSION_TTL_SECONDS:
                shutil.rmtree(folder, ignore_errors=True)
    except OSError:
        pass


def _gsf_session_mkdtemp(prefix="gsf_"):
    GSF_SESSION_TMP_DIR.mkdir(parents=True, exist_ok=True)
    return tempfile.mkdtemp(prefix=str(prefix), dir=str(GSF_SESSION_TMP_DIR))


def _gsf_session_tempdir(prefix="gsf_"):
    GSF_SESSION_TMP_DIR.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(prefix=str(prefix), dir=str(GSF_SESSION_TMP_DIR))


def _gsf_is_session_temp(path, prefix=""):
    try:
        target = Path(path).resolve()
        root = GSF_SESSION_TMP_DIR.resolve()
        inside = target == root or root in target.parents
        return bool(inside and (not prefix or target.name.startswith(prefix)))
    except Exception:
        return False


def _gsf_write_oauth_state(state, payload):
    safe_state = re.sub(r"[^A-Za-z0-9_-]+", "", str(state or ""))[:160]
    if not safe_state:
        raise ValueError("OAuth state non valido")
    body = dict(payload or {})
    body["session_id"] = GSF_SESSION_ID
    body["created"] = time.time()
    path = GSF_OAUTH_STATE_ROOT / (safe_state + ".json")
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)
    return path


def _gsf_read_oauth_state(state, consume=False):
    safe_state = re.sub(r"[^A-Za-z0-9_-]+", "", str(state or ""))[:160]
    if not safe_state:
        return {}
    path = GSF_OAUTH_STATE_ROOT / (safe_state + ".json")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if time.time() - float(payload.get("created", 0) or 0) > 900:
            payload = {}
    except Exception:
        payload = {}
    if consume:
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass
    return payload if isinstance(payload, dict) else {}


def _gsf_cleanup_oauth_states():
    now = time.time()
    try:
        for path in GSF_OAUTH_STATE_ROOT.glob("*.json"):
            try:
                if now - path.stat().st_mtime > 1800:
                    path.unlink(missing_ok=True)
            except OSError:
                pass
    except OSError:
        pass


_gsf_touch_session()
_gsf_cleanup_oauth_states()
_gsf_cleanup_expired_sessions()


@st.cache_resource
def _gsf_start_cleanup_worker(root_dir, ttl_seconds):
    root = Path(root_dir)
    ttl = max(1800, int(ttl_seconds))
    stop_event = threading.Event()

    def _loop():
        interval = max(120, min(600, ttl // 4))
        while not stop_event.wait(interval):
            now = time.time()
            try:
                for folder in root.iterdir():
                    if not folder.is_dir():
                        continue
                    marker = folder / ".active"
                    try:
                        last = marker.stat().st_mtime if marker.exists() else folder.stat().st_mtime
                    except OSError:
                        continue
                    if now - last > ttl:
                        shutil.rmtree(folder, ignore_errors=True)
            except OSError:
                pass

    threading.Thread(target=_loop, daemon=True, name="gsf-session-cleanup").start()
    return stop_event


_GSF_CLEANUP_WORKER = _gsf_start_cleanup_worker(str(GSF_SESSIONS_ROOT), GSF_SESSION_TTL_SECONDS)

GSF_MEDIA_SERVER_ROOT = GSF_SESSIONS_ROOT
GSF_MEDIA_BIND = str(os.environ.get("GSF_MEDIA_BIND", "0.0.0.0" if GSF_WEB_MODE else "127.0.0.1"))
try:
    GSF_MEDIA_PORT_CONFIG = int(os.environ.get("GSF_MEDIA_PORT", "8765" if GSF_WEB_MODE else "0") or 0)
except ValueError:
    GSF_MEDIA_PORT_CONFIG = 8765 if GSF_WEB_MODE else 0
GSF_MEDIA_BASE_URL = str(os.environ.get("GSF_MEDIA_BASE_URL", "/media" if GSF_WEB_MODE else "")).strip()


def _gsf_free_port(bind_host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((bind_host, 0))
        return s.getsockname()[1]

class _GSFQuietHandler(SimpleHTTPRequestHandler):
    """Quiet HTTP handler with proper byte-range support for HTML5 video seeking."""
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        pass

    def list_directory(self, path):
        self.send_error(403, "Directory listing disabled")
        return None

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
def _gsf_start_preview_server(bind_host, configured_port, root_dir):
    port = int(configured_port or 0)
    if port <= 0:
        port = _gsf_free_port(bind_host)
    def handler(*args, **kwargs):
        return _GSFQuietHandler(*args, directory=str(root_dir), **kwargs)
    server = ThreadingHTTPServer((bind_host, port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return port


GSF_PREVIEW_PORT = _gsf_start_preview_server(
    GSF_MEDIA_BIND, GSF_MEDIA_PORT_CONFIG, str(GSF_MEDIA_SERVER_ROOT)
)


def _gsf_media_relative(path):
    try:
        return Path(path).resolve().relative_to(GSF_MEDIA_SERVER_ROOT.resolve()).as_posix()
    except Exception:
        return Path(path).name


def _gsf_media_url(relative_path):
    relative = str(relative_path or "").lstrip("/")
    encoded = quote(relative, safe="/")
    if GSF_MEDIA_BASE_URL:
        return GSF_MEDIA_BASE_URL.rstrip("/") + "/" + encoded
    return f"http://127.0.0.1:{GSF_PREVIEW_PORT}/{encoded}"

def _gsf_probe_display_size(path):
    try:
        source=Path(path)
        stat=source.stat()
    except OSError as error:
        return None,None,None,str(error)
    return _gsf_probe_display_size_cached(
        str(source),stat.st_size,stat.st_mtime_ns,FFPROBE_PATH or shutil.which("ffprobe")
    )


@st.cache_data(show_spinner=False,max_entries=256)
def _gsf_probe_display_size_cached(path,size,mtime_ns,ffprobe):
    """The file signature invalidates metadata only when the media changes."""
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
    # Mantieni l'URL distinto per player senza duplicare i byte del video.
    if source_path == served_path:
        return _gsf_media_relative(served_path), served_path
    streamlit=globals().get("st")
    registered=(streamlit.session_state.setdefault("gsf_served_sources_v63",{})
                if streamlit is not None else {})
    source_stat=source_path.stat()
    signature=(str(source_path.resolve()),source_stat.st_size,source_stat.st_mtime_ns)
    try:
        same_inode=served_path.exists() and os.path.samefile(source_path,served_path)
    except OSError:
        same_inode=False
    same_copy=(
        served_path.exists() and registered.get(str(served_path))==signature
        and served_path.stat().st_size==source_stat.st_size
    )
    if not (same_inode or same_copy):
        if served_path.exists():
            served_path.unlink()
        try:
            os.link(source_path, served_path)
        except OSError:
            shutil.copy2(source_path, served_path)
    if streamlit is not None:
        registered[str(served_path)]=signature
        streamlit.session_state.setdefault("gsf_served_links_v63",set()).add(str(served_path))
    return _gsf_media_relative(served_path), served_path


def _gsf_v72_unique_media_key(source_path, key):
    """Give each inline editor clip a stable but unique browser URL."""
    source = Path(source_path)
    try:
        stat = source.stat()
        identity = f"{source.resolve()}|{stat.st_size}|{stat.st_mtime_ns}"
    except OSError:
        identity = str(source)
    token = hashlib.sha256(identity.encode("utf-8", "replace")).hexdigest()[:16]
    safe_key = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(key))
    return f"{safe_key}_{token}"


def _gsf_preview_cache_get(cache, key, create, max_items=3,
                           max_bytes=48*1024*1024):
    """Reuse a small number of lightweight AI previews in the current session."""
    if key in cache:
        value=cache.pop(key)
        cache[key]=value
        return value
    value=create()
    if value and len(value)<=max_bytes:
        cache[key]=value
        while (len(cache)>max_items or
               sum(len(item) for item in cache.values())>max_bytes):
            cache.pop(next(iter(cache)))
    return value

def _gsf_bytes_to_preview(data, key, suffix=".mp4"):
    digest = hashlib.sha256(data).hexdigest()[:16]
    safe_key = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(key))
    path = GSF_PREVIEW_DIR / f"{safe_key}_{digest}{suffix}"
    if not path.exists() or path.stat().st_size != len(data):
        with open(path, "wb") as f:
            f.write(data)
    streamlit=globals().get("st")
    if streamlit is not None:
        streamlit.session_state.setdefault("gsf_served_links_v63",set()).add(str(path))
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
    url = _gsf_media_url(served_name)
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

# V65 — revisione grafica ad alta leggibilità.
# Tutti gli elementi sono HTML/CSS: niente screenshot usati come interfaccia.
st.markdown("""
<style>
:root{
  --v65-bg:#f2f8fc;
  --v65-surface:#ffffff;
  --v65-surface-soft:#f7fbfe;
  --v65-text:#10243d;
  --v65-muted:#536b84;
  --v65-line:#d6e5f0;
  --v65-primary:#0b9fe8;
  --v65-primary-dark:#0678b8;
  --v65-focus:#0678b8;
  --v65-ai:#7051d6;
  --v65-warm:#e89618;
}
html,body,[class*="css"]{
  font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  -webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
}
.stApp{
  background:linear-gradient(180deg,#f4faff 0%,#ffffff 56%,#f1f8fc 100%) !important;
  color:var(--v65-text) !important;
}
.block-container{max-width:1360px !important;width:94vw !important;padding-top:.8rem !important;padding-bottom:3rem !important}
h1,h2,h3,h4,h5,h6,p,label,[data-testid="stCaptionContainer"]{color:var(--v65-text) !important}
[data-testid="stCaptionContainer"],.gsf-section-sub,.result-time,.results-head p{color:var(--v65-muted) !important}
[data-testid="stFileUploader"],[data-testid="stExpander"],.soft-card,.result-wrap,.editor-v2-head,.gsf-command{
  background:var(--v65-surface) !important;
  border:1px solid var(--v65-line) !important;
  border-radius:22px !important;
  box-shadow:0 10px 30px rgba(28,78,112,.08) !important;
}
[data-testid="stFileUploaderDropzone"]{background:var(--v65-surface-soft) !important;border:2px dashed #8fc9e8 !important;border-radius:16px !important}
.gsf-brand-name,.gsf-hero h1,.gsf-section-title,.result-title,.results-head h2{color:var(--v65-text) !important}
.gsf-brand-sub,.gsf-hero p,.gsf-section-sub,.result-time,.results-head p{color:var(--v65-muted) !important}
.gsf-logo,.gsf-orb,.ai-orb{background:linear-gradient(135deg,#0b9fe8,#6c83ef) !important;box-shadow:0 8px 20px rgba(11,159,232,.20) !important}
.gsf-step,.result-badge{background:#e9f6fd !important;border:1px solid #b9dfef !important;color:var(--v65-primary-dark) !important}
.gsf-command{color:var(--v65-muted) !important}
.stButton>button,.stDownloadButton>button{
  min-height:2.8rem !important;
  background:#ffffff !important;
  color:var(--v65-primary-dark) !important;
  border:1px solid #8fc9e8 !important;
  border-radius:14px !important;
  box-shadow:0 5px 14px rgba(28,78,112,.08) !important;
  font-weight:800 !important;
}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--v65-focus) !important;background:#f2fbff !important;color:var(--v65-focus) !important}
.stButton>button[kind="primary"]{background:var(--v65-primary) !important;color:#ffffff !important;border-color:var(--v65-primary) !important;box-shadow:0 7px 18px rgba(11,159,232,.22) !important}
.stButton>button[kind="primary"]:hover{background:var(--v65-primary-dark) !important;color:#ffffff !important}
.stTextInput input,.stNumberInput input,[data-baseweb="select"]>div,[data-testid="stRadio"] label{background:#ffffff !important;border-color:#aac9dc !important;color:var(--v65-text) !important}
.stRadio label p,.stSelectbox label,.stSlider label,.stTextInput label{color:var(--v65-text) !important;font-weight:700 !important}
.stSlider [data-baseweb="slider"] [role="slider"]{background:var(--v65-primary) !important;border-color:var(--v65-primary) !important}
.stSlider [data-baseweb="slider"] > div > div{background:var(--v65-primary) !important}
.hero-title{font-size:clamp(2.25rem,5vw,3.6rem) !important;letter-spacing:-.055em !important;color:var(--v65-text) !important}
.hero-sub{color:var(--v65-muted) !important;font-size:1rem !important}
.flow{gap:9px !important;margin:24px 0 28px !important}
.orb{width:auto !important;height:auto !important;min-width:118px !important;padding:14px 18px !important;border-radius:18px !important;font-size:.78rem !important;line-height:1.15 !important;box-shadow:0 7px 18px rgba(28,78,112,.10) !important}
.orb-blue{background:#e0f2ff !important;color:#155a98 !important;border:1px solid #9acdf2 !important}
.orb-cyan{background:#d9f7ee !important;color:#146b59 !important;border:1px solid #83d5bc !important}
.orb-yellow{background:#fff0cf !important;color:#805400 !important;border:1px solid #e6bd67 !important}
.orb-red{background:#eee6ff !important;color:#593b91 !important;border:1px solid #bca9e8 !important}
.flow-arrow{color:#7892a9 !important}
.v65-quality-note{max-width:760px;margin:0 auto 20px;text-align:center;color:var(--v65-muted);font-size:.9rem;line-height:1.45}
.flow .orb{display:flex !important;align-items:center !important;gap:11px !important;min-width:145px !important;padding:10px 16px 10px 10px !important;font-size:.84rem !important;letter-spacing:.025em !important}
.v66-step-icon{display:grid;place-items:center;flex:none;width:43px;height:43px;border-radius:50%;background:#fff;box-shadow:0 2px 9px rgba(30,61,85,.11);font-size:1.55rem;line-height:1;font-weight:750}
.gsf-icon-title{display:flex;align-items:center;gap:12px;margin:16px 0 10px;color:#203b53;font-weight:800;font-size:1.28rem;line-height:1.3}
.gsf-subtitles-title{margin-top:19px !important}
.gsf-icon-title .gsf-icon{display:grid;place-items:center;flex:none;width:43px;height:43px;border-radius:50%;font-size:1.45rem;line-height:1;color:#155a98;background:#e0f2ff;border:1px solid #9acdf2}
.gsf-icon-title.mint .gsf-icon{background:#d9f7ee;color:#146b59;border-color:#83d5bc}
.gsf-icon-title.amber .gsf-icon{background:#fff0cf;color:#805400;border-color:#e6bd67}
.gsf-icon-title.lilac .gsf-icon{background:#eee6ff;color:#593b91;border-color:#bca9e8}
[data-testid="stRadio"] label{border-radius:16px !important;padding:9px 13px !important}
[data-testid="stRadio"] label p{font-size:.96rem !important}
.stButton>button,.stDownloadButton>button{min-height:44px !important;border-radius:16px !important}
.v66-upload-intro{display:flex;align-items:center;gap:15px;margin:18px 0 10px;padding:18px 21px;border-radius:22px;background:linear-gradient(115deg,#e0f2ff 0%,#effaff 58%,#d9f7ee 100%);border:1px solid #a8d9e7;box-shadow:0 9px 22px rgba(31,105,133,.08)}
.v66-upload-intro .v66-upload-icon{display:grid;place-items:center;flex:none;width:58px;height:58px;border-radius:19px;background:#fff;color:#155a98;border:1px solid #a4cdec;font-size:2.2rem;line-height:1;box-shadow:0 5px 14px rgba(31,105,133,.11)}
.v66-upload-intro strong{display:block;color:#203b53;font-size:1.17rem;line-height:1.3}.v66-upload-intro span{display:block;color:#48657a;font-size:.92rem;line-height:1.45;margin-top:3px}
[data-testid="stFileUploader"]{padding:8px 15px 15px !important}
[data-testid="stFileUploaderDropzone"]{min-height:128px !important;background:#f8fcff !important;border:2px dashed #70b9d4 !important;border-radius:18px !important;transition:background .15s,border-color .15s}
[data-testid="stFileUploaderDropzone"]:hover{background:#eaf8fb !important;border-color:#168a94 !important}
[data-testid="stFileUploaderDropzone"] button{border-radius:14px !important;background:#e0f2ff !important;border:1px solid #9acdf2 !important;color:#155a98 !important;font-weight:800 !important}
[data-testid="stFileUploader"] label p,[data-testid="stFileUploaderDropzone"] *{color:#203b53 !important}
@media(max-width:700px){.flow{flex-wrap:wrap !important;justify-content:center !important}.flow-arrow{display:none !important}.flow .orb{min-width:43% !important}.v66-step-icon{width:38px;height:38px}}
</style>
""", unsafe_allow_html=True)


import html



GSF_ENGINE_IDS_V75 = ("🚀 AUTO TOTALE", "🎬 AI Director", "🧠 Smart Clip", "🤖 Auto Clip", "✋ Manuale")
GSF_ENGINE_NAMES_V75 = {
    "🚀 AUTO TOTALE": "Automatico",
    "🎬 AI Director": "Momento migliore",
    "🧠 Smart Clip": "Più azione",
    "🤖 Auto Clip": "Reazioni",
    "✋ Manuale": "Scegli scena",
}


def _gsf_v75_engine_work_to_protect():
    """True solo quando c'è una scelta/finale o modifiche reali nell'editor."""
    if st.session_state.get("gsf_final_recipe") or st.session_state.get("publication_ready"):
        return True
    if any(st.session_state.get(k) for k in (
        "editor_output", "editor_output_bytes", "editor_result_path",
        "editor_quick_bytes", "inline_final_bytes"
    )):
        return True

    main_defaults = {
        "editor_format": "9:16 Short",
        "editor_zoom": 1.0, "editor_x": 0, "editor_y": 0,
        "editor_volume": 100, "editor_brightness": 0.0,
        "editor_contrast": 1.0, "editor_speed": 1.0,
        "editor_sub_mode": "Automatici", "editor_sub_mode_v18": "Automatici",
        "editor_sub_font_v18": "Arial", "editor_sub_size": 92,
        "editor_sub_size_v18": 92, "subtitle_font": "Arial",
        "subtitle_text_color": "#FFFFFF", "subtitle_active_color": "#FFD400",
        "subtitle_outline_color": "#000000", "subtitle_x": 50, "subtitle_y": 78,
        "subtitle_x_v18": 50, "subtitle_y_v18": 78,
        "subtitle_text_color_v18": "#FFFFFF",
        "subtitle_active_color_v18": "#FFD400",
        "subtitle_outline_color_v18": "#000000",
    }
    for key, default in main_defaults.items():
        if key in st.session_state and st.session_state.get(key) != default:
            return True

    if st.session_state.get("editor_sub_words") or st.session_state.get("editor_sub_text"):
        return True

    # Timeline editor principale: il solo valore iniziale non conta come modifica.
    original_start = st.session_state.get("editor_original_start")
    original_end = st.session_state.get("editor_original_end")
    for key in list(st.session_state.keys()):
        skey = str(key)
        value = st.session_state.get(key)
        if skey.startswith("editor_trim_") and isinstance(value, (tuple, list)) and len(value) == 2:
            if original_start is not None and original_end is not None:
                try:
                    if abs(float(value[0]) - float(original_start)) > 0.01 or abs(float(value[1]) - float(original_end)) > 0.01:
                        return True
                except (TypeError, ValueError):
                    pass

        if skey.startswith("inline_trans_words_") and value:
            return True
        if skey.startswith("inline_trans_text_") and str(value or "").strip():
            return True
        if skey.startswith("inline_applied_text_") and str(value or "").strip():
            return True

        # Controlli dell'editor inline: confronta solo valori diversi dai default.
        inline_defaults = (
            ("inline_fmt_", "9:16 Short"),
            ("inline_zoom_", 1.0), ("inline_x_", 0), ("inline_y_", 0),
            ("inline_vol_", 100), ("inline_bri_", 0.0),
            ("inline_con_", 1.0), ("inline_spd_", 1.0),
            ("inline_submode_", "Automatici"),
            ("inline_font_", "Arial"), ("inline_subsize_", 92),
            ("inline_subx_", 50), ("inline_suby_", 78),
            ("inline_txtcol_v18_", "#FFFFFF"),
            ("inline_actcol_v18_", "#FFD400"),
            ("inline_outcol_v18_", "#000000"),
        )
        for prefix, default in inline_defaults:
            # Evita di leggere come stato principale le copie widget: anche quelle
            # vengono comunque intercettate dal rispettivo prefisso quando cambiano.
            if skey.startswith(prefix) and value != default:
                return True

        if skey.startswith("inline_trim_") and isinstance(value, (tuple, list)) and len(value) == 2:
            try:
                full_duration = float(st.session_state.get("inline_editor_duration", value[1]))
                if abs(float(value[0])) > 0.01 or abs(float(value[1]) - full_duration) > 0.05:
                    return True
            except (TypeError, ValueError):
                pass

    return False


def _gsf_v75_reset_engine_workflow():
    """Azzera solo la lavorazione del motore; conserva gameplay, durata e cache sorgente."""
    # Chiude e rimuove solo le cartelle temporanee degli editor correnti.
    for temp_key, prefix in (("editor_dir", "gsf_editor_"), ("inline_editor_dir", "gsf_inline_ai_")):
        old_temp = st.session_state.get(temp_key)
        if old_temp:
            try:
                temp_path = Path(old_temp)
                if _gsf_is_session_temp(temp_path, prefix):
                    shutil.rmtree(temp_path, ignore_errors=True)
            except OSError:
                pass

    exact = {
        "ai_director_scores", "clip_rifinite", "gsf_ai_v3_diagnostics",
        "gsf_final_recipe", "apri_editor_manuale", "apri_editor_risultato",
        "current_view", "editor_source", "manual_start_editor", "manual_duration_editor",
        "project_subtitles_enabled", "project_subtitles_mode",
        "show_social_publish_v53", "show_social_publish_v54",
        "social_final_context_v53", "social_final_context_v54",
        "social_error_v59", "social_export_v59", "social_selected_v59", "social_started_v59",
        "social_auth_url_v77", "social_auth_platform_v77",
        "risultati_batch",
    }
    prefixes = (
        "auto_clip_", "preview_", "publication_",
        "editor_", "inline_",
        "subtitle_",
    )
    for key in list(st.session_state.keys()):
        skey = str(key)
        if key in exact or any(skey.startswith(prefix) for prefix in prefixes):
            st.session_state.pop(key, None)


def _gsf_v75_apply_engine(engine_id):
    if engine_id not in GSF_ENGINE_IDS_V75:
        return
    _gsf_v75_reset_engine_workflow()
    st.session_state["modalita_gsf"] = engine_id
    st.session_state.pop("gsf_pending_engine_switch_v75", None)


def _gsf_v69_select_engine(index):
    if type(index) is not int or not 0 <= index < len(GSF_ENGINE_IDS_V75):
        raise ValueError("Invalid engine selection")
    target = GSF_ENGINE_IDS_V75[index]
    current = st.session_state.get("modalita_gsf")
    if current == target:
        st.session_state.pop("gsf_pending_engine_switch_v75", None)
        return
    if _gsf_v75_engine_work_to_protect():
        st.session_state["gsf_pending_engine_switch_v75"] = target
    else:
        _gsf_v75_apply_engine(target)


def _gsf_v75_confirm_engine_switch():
    target = st.session_state.get("gsf_pending_engine_switch_v75")
    if target in GSF_ENGINE_IDS_V75:
        _gsf_v75_apply_engine(target)


def _gsf_v75_cancel_engine_switch():
    st.session_state.pop("gsf_pending_engine_switch_v75", None)


def _gsf_v70_select_duration(value):
    """Store one of the two visible duration presets."""
    allowed = ("15s", "30s")
    if value not in allowed:
        raise ValueError("Invalid duration preset")
    st.session_state["gsf_duration_preset"] = value


def _gsf_v70_build_short_cards(risultati_ai, candidati, duration, diagnostics=None):
    """Build three lightweight candidate cards without rendering video players."""
    diagnostics = diagnostics if isinstance(diagnostics, dict) else {}
    result_rows = list(risultati_ai or [])
    candidate_rows = list(candidati or [])[:3]
    scores = []
    for row in result_rows:
        try:
            scores.append(float(row[0]))
        except (TypeError, ValueError, IndexError):
            scores.append(None)
    valid_scores = [score for score in scores if score is not None]
    maximum = max(valid_scores) if valid_scores else None
    duration = float(duration)
    labels = {
        "reaction": "Reazione",
        "action": "Azione",
        "story": "Momento forte",
    }
    cards = []
    for index, raw_start in enumerate(candidate_rows):
        start = float(raw_start)
        score = scores[index] if index < len(scores) else None
        quality = None
        if score is not None and maximum:
            quality = int(max(1, min(100, score / maximum * 100)))
        detail = diagnostics.get(round(start, 3), {}) or {}
        features = detail.get("features", {}) if isinstance(detail, dict) else {}
        category = str(features.get("moment_category", "") or "")
        label = labels.get(category, "Momento forte")
        cards.append({
            "index": index + 1,
            "start": start,
            "end": start + duration,
            "duration": duration,
            "quality": quality,
            "label": label,
        })
    return cards


def _gsf_v71_mini_player_html(url, label):
    """Return a compact lazy HTML5 player for one candidate card."""
    safe_url = (str(url).replace("&", "&amp;").replace('"', "&quot;")
                .replace("<", "&lt;").replace(">", "&gt;"))
    safe_label = (str(label).replace("&", "&amp;").replace('"', "&quot;")
                  .replace("<", "&lt;").replace(">", "&gt;"))
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;background:transparent;overflow:hidden}}
.mini{{width:100%;height:154px;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:16px;background:#101a2c}}
video{{display:block;width:100%;height:154px;object-fit:contain;background:#101a2c}}
</style></head><body><div class="mini">
<video controls preload="metadata" playsinline aria-label="{safe_label}">
<source src="{safe_url}" type="video/mp4">
</video></div></body></html>'''


def _gsf_v71_render_mini_player(source_path, key, label):
    """Serve one cached low-resolution candidate and render it inside its card."""
    source_path = Path(source_path)
    if not source_path.exists():
        st.caption("Anteprima non disponibile")
        return False
    served_name, _ = _gsf_serve_path(source_path, key)
    url = _gsf_media_url(served_name)
    components.html(
        _gsf_v71_mini_player_html(url, label),
        height=174,
        scrolling=False,
    )
    return True

def _gsf_v68_upload_css(loaded):
    """Keep the native chooser present in both states, without replacing its input."""
    label = "Video caricato" if loaded else "Carica il tuo video"
    icon = "m5%2012%204%204L19%206" if loaded else "M12%2016V4m-5%205%205-5%205%205M4%2016v4h16v-4"
    color = "#c7efdf" if loaded else "#d4eaff"
    return """<style>
[data-testid="stFileUploaderDropzone"]{display:flex !important;visibility:visible !important;align-items:center !important;justify-content:center !important}
[data-testid="stFileUploaderDropzone"]>div:has(button){display:flex !important;justify-content:center !important}
[data-testid="stFileUploaderDropzone"] button{display:flex !important;visibility:visible !important;margin:0 auto !important;gap:0 !important;background:COLOR !important}
[data-testid="stFileUploaderDropzone"] button::before{content:"";display:block;width:42px;height:42px;flex:0 0 42px;margin:0 auto 12px;background:url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='%23164b85'%20stroke-width='1.8'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='ICON'/%3E%3C/svg%3E") center/42px 42px no-repeat;transform:none !important}
[data-testid="stFileUploaderDropzone"] button{box-sizing:border-box !important;width:196px !important;height:196px !important;min-width:196px !important;max-width:196px !important;min-height:196px !important;max-height:none !important;padding:25px 24px !important;overflow:visible !important;white-space:normal !important;flex-direction:column !important;align-items:center !important;justify-content:center !important}
[data-testid="stFileUploaderDropzone"] button::after{content:"LABEL";display:block;flex:0 0 auto;width:132px;max-width:132px;white-space:normal !important;overflow:visible !important;overflow-wrap:normal;text-align:center;font-size:17px !important;line-height:1.35 !important}
[data-testid="stFileUploaderDropzone"]{overflow:visible !important;min-height:238px !important}
[data-testid="stFileUploaderDropzone"] button::before{flex-shrink:0 !important}
[data-testid="stFileUploaderDropzone"] button>div{display:none !important}
    </style>""".replace("ICON", icon).replace("COLOR", color).replace("LABEL", label)


def _gsf_v72_upload_css(loaded):
    """Keep the native uploader, but separate its circle from the file row."""
    label = "Video caricato" if loaded else "Carica il tuo video"
    icon = "m5%2012%204%204L19%206" if loaded else "M12%2016V4m-5%205%205-5%205%205M4%2016v4h16v-4"
    color = "#c7efdf" if loaded else "#d4eaff"
    return """<style>
[class*="st-key-v72-upload-shell"] [data-testid="stFileUploaderDropzone"]{
  display:block !important; min-height:320px !important; height:auto !important;
  padding:24px 18px !important; overflow:visible !important; box-sizing:border-box !important;
}
[class*="st-key-v72-upload-shell"] [data-testid="stFileUploaderDropzone"]>div:has(button){
  display:flex !important; flex-direction:column !important; align-items:center !important;
  justify-content:flex-start !important; gap:16px !important; width:100% !important;
}
[class*="st-key-v72-upload-shell"] [data-testid="stFileUploaderDropzone"] button{
  display:flex !important; visibility:visible !important; position:relative !important; z-index:2 !important;
  box-sizing:border-box !important; width:210px !important; height:210px !important;
  min-width:210px !important; max-width:210px !important; min-height:210px !important;
  padding:26px 24px !important; margin:0 auto !important; border-radius:50% !important;
  border:2px solid rgba(22,75,133,.35) !important; background:COLOR !important;
  overflow:visible !important; white-space:normal !important; flex-direction:column !important;
  align-items:center !important; justify-content:center !important; gap:0 !important;
}
[class*="st-key-v72-upload-shell"] [data-testid="stFileUploaderDropzone"] button>div{display:none !important}
[class*="st-key-v72-upload-shell"] [data-testid="stFileUploaderDropzone"] button::before{
  content:""; display:block; width:48px; height:48px; flex:0 0 48px; margin:0 auto 12px;
  background:url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='%23164b85'%20stroke-width='1.8'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='ICON'/%3E%3C/svg%3E") center/48px 48px no-repeat;
}
[class*="st-key-v72-upload-shell"] [data-testid="stFileUploaderDropzone"] button::after{
  content:"LABEL"; display:block; flex:0 0 auto; width:150px; max-width:150px;
  white-space:normal !important; overflow:visible !important; overflow-wrap:normal;
  text-align:center; font-size:18px !important; font-weight:700 !important;
  line-height:1.25 !important; color:#164b85 !important;
}
[class*="st-key-v72-upload-shell"] [data-testid="stFileUploaderFile"]{
  order:2 !important; position:relative !important; inset:auto !important; transform:none !important;
  z-index:3 !important; display:flex !important; align-self:center !important;
  width:min(100%,360px) !important; max-width:360px !important; margin:0 auto !important;
  box-sizing:border-box !important; border-radius:14px !important;
}
[class*="st-key-v72-upload-shell"] [data-testid="stFileUploaderFileName"]{
  max-width:100% !important; overflow:hidden !important; text-overflow:ellipsis !important;
}
    </style>""".replace("ICON", icon).replace("COLOR", color).replace("LABEL", label)


def _gsf_v73_upload_css(loaded):
    """Draw the status on the dropzone, never on the uploaded-file controls."""
    label = "Video caricato" if loaded else "Carica il tuo video"
    icon = "m5%2012%204%204L19%206" if loaded else "M12%2016V4m-5%205%205-5%205%205M4%2016v4h16v-4"
    color = "#c7efdf" if loaded else "#d4eaff"
    return """<style>
.st-key-v73-upload-shell{padding:24px 0 8px !important}
.st-key-v73-upload-shell [data-testid="stFileUploader"]{
  width:100% !important; max-width:300px !important; margin:0 auto !important;
  padding:0 !important; background:transparent !important; border:0 !important;
  box-shadow:none !important; overflow:visible !important;
}
[class*="st-key-v73-upload-shell"] [data-testid="stFileUploaderDropzone"]{
  position:relative !important; display:block !important; box-sizing:border-box !important;
  width:228px !important; min-width:228px !important; max-width:228px !important;
  min-height:228px !important; height:228px !important; padding:0 !important;
  margin:0 auto !important; border-radius:50% !important;
  overflow:visible !important; background:transparent !important; border:0 !important;
}
/* Streamlit uses either a Browse button or file chips plus an Add button.
   Neither wrapper is allowed to size or clip the decorative circle. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]>div:not([data-testid="stFileUploaderDropzoneInstructions"]),
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]>span,
.st-key-v73-upload-shell [data-testid="stFileChips"]{
  position:static !important; display:contents !important; overflow:visible !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzoneInstructions"],
.st-key-v73-upload-shell [data-testid="stFileChips"]>div,
.st-key-v73-upload-shell [data-testid="stFileUploaderFile"],
.st-key-v73-upload-shell [data-testid="stFileUploaderFileList"]{
  display:none !important;
}
[class*="st-key-v73-upload-shell"] [data-testid="stFileUploaderDropzone"]::before{
  content:""; position:absolute !important; z-index:1 !important; inset:0 !important;
  width:100% !important; height:100% !important; box-sizing:border-box !important;
  border-radius:50% !important;
  border:2px solid rgba(22,75,133,.35) !important; background-color:COLOR !important;
  background-image:url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='%23164b85'%20stroke-width='1.8'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='ICON'/%3E%3C/svg%3E") !important;
  background-repeat:no-repeat !important; background-size:48px 48px !important;
  background-position:center 32% !important; pointer-events:none !important;
}
[class*="st-key-v73-upload-shell"] [data-testid="stFileUploaderDropzone"]::after{
  content:"LABEL"; position:absolute !important; z-index:2 !important; top:138px !important;
  left:50% !important; width:170px !important; transform:translateX(-50%) !important;
  text-align:center !important; white-space:normal !important; color:#164b85 !important;
  font-size:18px !important; font-weight:700 !important; line-height:1.25 !important;
  pointer-events:none !important;
}
[class*="st-key-v73-upload-shell"] [data-testid="stFileUploaderDropzone"] button{
  position:absolute !important; inset:0 !important; z-index:5 !important;
  width:100% !important; max-width:none !important; min-width:0 !important;
  height:100% !important; min-height:0 !important; margin:0 !important;
  padding:0 !important; opacity:0 !important;
  cursor:pointer !important; border:0 !important; background:transparent !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button::before,
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button::after{
  content:none !important; display:none !important;
}
[class*="st-key-v73-upload-shell"] [data-testid="stFileUploaderDropzone"] input[type="file"]{
  position:absolute !important; inset:0 !important; z-index:6 !important;
  display:block !important; width:100% !important; height:100% !important;
  margin:0 !important; padding:0 !important; border:0 !important; opacity:0 !important;
  cursor:pointer !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]:focus-within::before{
  outline:3px solid #164b85; outline-offset:5px;
}
.v73-upload-meta{
  display:block; box-sizing:border-box; width:fit-content; text-align:center;
  max-width:min(360px,100%); margin:4px auto 0; padding:8px 16px; border-radius:999px;
  background:#eef6fb; color:#315c7a; font-size:.86rem; font-weight:700;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}
</style>""".replace("ICON", icon).replace("COLOR", color).replace("LABEL", label)

def _gsf_v67_badge(icon, label, tone="blue"):
    """Render a crisp decorative vector; escape labels and constrain styles."""
    paths = {
        "upload": '<path d="M12 16V4m-5 5 5-5 5 5M4 16v4h16v-4"/>',
        "choose": '<path d="m5 12 4 4L19 6"/>',
        "edit": '<path d="m4 16 12-12 4 4L8 20H4zm10-10 4 4"/>',
        "publish": '<path d="m3 11 18-8-8 18-3-8zm7 2L21 3"/>',
        "play": '<path d="m8 5 11 7-11 7z"/>',
        "intelligence": '<path d="M8 4h8M12 4v16M8 20h8"/>',
        "text": '<path d="M5 6h14M12 6v14M8 20h8"/>',
        "spark": '<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5z"/>',
    }
    tone = tone if tone in {"blue", "mint", "amber", "lilac", "rose", "peach", "indigo"} else "blue"
    path = paths.get(icon, paths["spark"])
    svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + path + '</svg>'
    return '<span class="v67-badge ' + tone + '">' + svg + '</span><span>' + html.escape(str(label)) + '</span>'

st.markdown("""
<style>

.stButton>button::before,.stDownloadButton>button::before,[data-testid="stPopover"] button::before{content:"";display:inline-block;flex-shrink:0;width:27px;height:27px;border-radius:50%;background:#dbeaff;border:1px solid #8eb3dd;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23203b53' stroke-width='2'%3E%3Cpath d='M5 12h14m-5-5 5 5-5 5'/%3E%3C/svg%3E");background-position:center;background-size:17px;background-repeat:no-repeat;margin-right:7px}
.stButton>button[kind="primary"]::before{background-color:#fff}
.stDownloadButton>button::before{transform:rotate(90deg);background-color:#d9f3e9}
[data-testid="stPopover"] button::before{background-color:#fff0cf}

.st-key-v67_engines [role="radiogroup"] label:nth-of-type(1)::before{background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23203b53%22%20stroke-width%3D%221.8%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22m12%203%202.5%206.5L21%2012l-6.5%202.5L12%2021l-2.5-6.5L3%2012l6.5-2.5z%22%2F%3E%3C%2Fsvg%3E");background-color:#badaff !important}
.st-key-v67_engines [role="radiogroup"] label:nth-of-type(2)::before{background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23203b53%22%20stroke-width%3D%221.8%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M7%203h10v7a5%205%200%200%201-10%200zM7%205H3v3a4%204%200%200%200%204%204m10-7h4v3a4%204%200%200%201-4%204m-5%203v6m-4%200h8%22%2F%3E%3C%2Fsvg%3E");background-color:#b9e9c8 !important}
.st-key-v67_engines [role="radiogroup"] label:nth-of-type(3)::before{background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23203b53%22%20stroke-width%3D%221.8%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22m13%202-9%2012h7l-1%208%2010-13h-7z%22%2F%3E%3C%2Fsvg%3E");background-color:#ffdc91 !important}
.st-key-v67_engines [role="radiogroup"] label:nth-of-type(4)::before{background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23203b53%22%20stroke-width%3D%221.8%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Crect%20x%3D%229%22%20y%3D%223%22%20width%3D%226%22%20height%3D%2212%22%20rx%3D%223%22%2F%3E%3Cpath%20d%3D%22M5%2010v2a7%207%200%200%200%2014%200v-2M12%2019v3%22%2F%3E%3C%2Fsvg%3E");background-color:#d7baff !important}
.st-key-v67_engines [role="radiogroup"] label:nth-of-type(5)::before{background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23203b53%22%20stroke-width%3D%221.8%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Ccircle%20cx%3D%2212%22%20cy%3D%2212%22%20r%3D%227%22%2F%3E%3Ccircle%20cx%3D%2212%22%20cy%3D%2212%22%20r%3D%222%22%2F%3E%3Cpath%20d%3D%22M12%202v4m0%2012v4M2%2012h4m12%200h4%22%2F%3E%3C%2Fsvg%3E");background-color:#ffc4b2 !important}
/* Native radio remains accessible; its small extra dot is visually suppressed. */
.st-key-v67_engines label>div:first-child{position:absolute !important;opacity:0 !important;width:1px !important;height:1px !important;overflow:hidden}
.stApp,.stApp p,.stApp label,.stApp button,.stApp input,.stApp select,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.hero-title,.hero-sub,.orb,.gsf-icon-title,.v67-footer{font-family:Arial,"Helvetica Neue",sans-serif !important;font-kerning:normal;text-shadow:none !important}
.stApp p,.stApp label{font-weight:400 !important;line-height:1.5}
.stApp button p,.gsf-icon-title,.orb{font-weight:600 !important}
.hero-title{font-weight:700 !important;letter-spacing:-.035em !important;line-height:1.05 !important}
.gsf-section-sub,[data-testid="stCaptionContainer"]{background:#d8edf5 !important;border:2px dashed #6295ac !important;color:#233f51 !important;opacity:1 !important}
.gsf-section-sub *,[data-testid="stCaptionContainer"] p{color:#233f51 !important}

/* V67: native text, vector icons, quiet surfaces, distinct circular controls. */
.v67-badge{display:inline-grid;place-items:center;flex:none;width:54px;height:54px;border-radius:50%;background:#cce5ff;color:#164b85;border:1px solid #83b5eb;box-shadow:0 5px 14px #203b5310}
.v67-badge svg{width:29px;height:29px}
.v67-badge.mint{background:#bcefdc;color:#115b45;border-color:#6bbb9d}
.v67-badge.amber{background:#ffe0a3;color:#714400;border-color:#d6a446}
.v67-badge.lilac{background:#decaff;color:#573584;border-color:#ac85de}
.v67-badge.rose{background:#ffd4df;color:#8a2947;border-color:#de91a7}
.flow .orb{background:transparent !important;border:0 !important;box-shadow:none !important;flex-direction:column !important;gap:12px !important;padding:8px 18px !important;min-width:140px !important;font-size:.9rem !important;color:#203b53 !important}
.flow .v67-badge{width:78px;height:78px}.flow .v67-badge svg{width:37px;height:37px}
.flow-arrow{display:none !important}
.gsf-icon-title{display:flex;gap:13px;align-items:center}
.gsf-command,.gsf-section-sub,.v65-quality-note,[data-testid="stCaptionContainer"]{border:1.5px dashed #8caab9 !important;border-radius:20px !important;background:#f3fafc !important;padding:12px 17px !important;color:#39556b !important;box-shadow:none !important;line-height:1.55 !important}
.gsf-section-sub{margin:9px 0 18px}
[data-testid="stCaptionContainer"] p{color:#39556b !important}
[data-testid="stFileUploader"]{max-width:720px;margin:auto;padding:18px !important;background:transparent !important;border:0 !important;box-shadow:none !important}
[data-testid="stFileUploaderDropzone"]{justify-content:center !important;background:transparent !important;border:0 !important;padding:16px !important;min-height:210px !important}
[data-testid="stFileUploaderDropzoneInstructions"],[data-testid="stFileUploaderDropzone"] small{display:none !important}
[data-testid="stFileUploaderDropzone"] button{display:flex !important;flex-direction:column !important;align-items:center !important;justify-content:center !important;width:184px !important;height:184px !important;min-width:184px !important;border-radius:50% !important;background:linear-gradient(145deg,#d4ecff,#b6d9ff) !important;border:2px solid #80b5e7 !important;box-shadow:0 12px 30px #155a981c !important;padding:22px !important}
[data-testid="stFileUploaderDropzone"] button p{display:none !important}
[data-testid="stFileUploaderDropzone"] button::before{content:"↑";display:block;font-size:2.5rem;color:#164b85 !important;line-height:1;margin-bottom:12px}
[data-testid="stFileUploaderDropzone"] button::after{content:"Carica il tuo video";font-size:1.05rem;line-height:1.3;color:#164b85 !important;font-weight:800}
[data-testid="stFileUploaderDropzone"] button:hover{background:#b9ddff !important;border-color:#2867a6 !important}
button:focus-visible,[role="radio"]:focus-visible{outline:3px solid #185b93 !important;outline-offset:4px}
.st-key-v67_engines [role="radiogroup"]{display:flex;flex-wrap:wrap;gap:16px;justify-content:center}
.st-key-v67_engines label{position:relative;display:flex !important;flex-direction:column !important;justify-content:center;align-items:center;gap:10px !important;width:150px;min-height:158px;border:2px solid transparent !important;background:transparent !important;padding:12px 8px !important;text-align:center}
.st-key-v67_engines label::before{content:"";width:76px;height:76px;flex:none;border-radius:50%;background-color:#cce5ff;background-position:center;background-repeat:no-repeat;background-size:34px;border:1px solid #83b5eb}
.st-key-v67_engines label:nth-of-type(2)::before{background-color:#bcefdc;border-color:#6bbb9d}
.st-key-v67_engines label:nth-of-type(3)::before{background-color:#ffe0a3;border-color:#d6a446}
.st-key-v67_engines label:nth-of-type(4)::before{background-color:#decaff;border-color:#ac85de}
.st-key-v67_engines label:nth-of-type(5)::before{background-color:#ffd4df;border-color:#de91a7}
.st-key-v67_engines label:has(input:checked){border-color:#295e85 !important;background:#f4faff !important}
.st-key-v67_engines label:has(input:checked)::after{content:"✓";position:absolute;top:9px;right:10px;color:#174e74;font-weight:900}
.st-key-v67_engines label:focus-within{outline:3px solid #185b93;outline-offset:3px}
.v67-ad{display:flex;justify-content:center;align-items:center;min-height:100px;max-width:970px;margin:32px auto;border:1px solid #d5dce3;border-radius:20px;background:#f6f7f9;color:#5e6e7b;font-size:.8rem;letter-spacing:.08em}
.v67-footer{visibility:visible !important;text-align:center;border-top:1px solid #d9e4eb;margin:28px auto 0;padding:22px 10px;color:#4f677b;font-size:.85rem;line-height:1.7}
@media(max-width:700px){.flow .orb{min-width:40% !important}.flow .v67-badge{width:66px;height:66px}.st-key-v67_engines label{width:130px}.v67-ad{min-height:90px;margin:24px 0}}
.gsf-section-sub,[data-testid="stCaptionContainer"]{background:#d8edf5 !important;border:2px dashed #6295ac !important;color:#233f51 !important;opacity:1 !important}
.gsf-section-sub *,[data-testid="stCaptionContainer"] p{color:#233f51 !important}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.v67-badge.rose{background:#ffbeac;color:#843b25;border-color:#de8f76}
.v67-badge.amber{background:#ffdf91;color:#765000;border-color:#d5ac4e}
.v67-badge.peach{background:#ffe1ce;color:#995627;border-color:#e5ae89}
.v67-badge.indigo{background:#cbd5ff;color:#36477e;border-color:#91a2dc}
.st-key-v69_engine_grid button{position:relative;display:flex !important;flex-direction:column !important;justify-content:flex-start !important;align-items:center !important;width:100% !important;min-height:208px !important;height:208px !important;padding:20px 8px 12px !important;gap:16px !important;border:2px solid transparent !important;background:#f8fbfe !important;color:#203b53 !important;box-shadow:none !important;border-radius:24px !important}
.st-key-v69_engine_grid button::before{content:"" !important;display:block !important;flex:0 0 104px !important;width:104px !important;height:104px !important;min-width:104px !important;border-radius:50% !important;margin:0 !important;background-position:center !important;background-repeat:no-repeat !important;background-size:48px !important;transform:none !important;border:1px solid #203b5326 !important}
.st-key-v69_engine_grid button p{display:flex;align-items:flex-start;justify-content:center;min-height:48px;max-width:160px;white-space:normal !important;font-size:1.05rem !important;line-height:1.35 !important;font-weight:600 !important;color:#203b53 !important;margin:0 !important}
.st-key-v69_engine_grid button[kind="primary"]{border-color:#375d80 !important;background:#eef5fb !important}
.st-key-v69_engine_grid button[kind="primary"]::after{content:"✓";position:absolute;top:10px;right:12px;font-size:18px;color:#254d6e}
.st-key-v69_engine_grid button:hover{border-color:#7094b1 !important;background:#f0f6fb !important}
.st-key-v69_engine_grid{margin:20px 0 22px !important;padding:8px 0 6px !important}
.st-key-v69_engine_grid [data-testid="stHorizontalBlock"]{gap:24px !important;align-items:stretch !important}
.st-key-v69_engine_grid button{min-height:224px !important;height:224px !important;padding-top:24px !important;gap:18px !important}
.st-key-v69_engine_grid button::before{width:110px !important;height:110px !important;min-width:110px !important;flex-basis:110px !important;background-size:52px !important}
.st-key-v70-duration,.st-key-v72-duration,.st-key-v73-duration{margin:26px 0 30px !important;padding:4px 0 !important}
.st-key-v70-duration [data-testid="stHorizontalBlock"],.st-key-v72-duration [data-testid="stHorizontalBlock"],.st-key-v73-duration [data-testid="stHorizontalBlock"]{justify-content:center !important;gap:24px !important}
.st-key-v70-duration button,.st-key-v72-duration button,.st-key-v73-duration button{width:150px !important;height:118px !important;min-height:118px !important;border-radius:60px !important;padding:12px !important;font-size:1.12rem !important;font-weight:800 !important;letter-spacing:.02em !important;background:#f7fbff !important;border:2px solid #a9c8df !important;color:#294a63 !important;box-shadow:0 8px 18px rgba(28,78,112,.08) !important}
.st-key-v70-duration button[kind="primary"],.st-key-v72-duration button[kind="primary"],.st-key-v73-duration button[kind="primary"]{background:#e9dcff !important;border-color:#8d70d2 !important;color:#50379e !important;box-shadow:0 10px 22px rgba(112,81,214,.18) !important}
.st-key-v70-duration button:hover,.st-key-v72-duration button:hover,.st-key-v73-duration button:hover{background:#eef8ff !important;border-color:#4d85ad !important}
.v70-duration-title{margin:4px 0 10px;text-align:center;color:#203b53;font-size:1.15rem;font-weight:800}
.v70-duration-sub{margin:0;text-align:center;color:#536b84;font-size:.88rem}
.v70-short-heading{margin:30px 0 7px;color:#203b53;font-size:1.25rem;font-weight:800;text-align:left}
.v70-short-sub{margin:0 0 18px;color:#536b84;font-size:.9rem}
.st-key-v70-short-grid [data-testid="stHorizontalBlock"]{gap:24px !important;align-items:stretch !important}
[class*="st-key-v70_short_card_"]{height:100% !important;padding:18px !important;border:1px solid #d4e4ef !important;border-radius:24px !important;background:#fbfdff !important;box-shadow:0 10px 24px rgba(28,78,112,.08) !important}
[class*="st-key-v70_short_card_"] .v70-short-card-preview{display:flex;align-items:center;justify-content:center;position:relative;min-height:128px;border-radius:18px;background:linear-gradient(135deg,#d9edff 0%,#e8ddff 55%,#ffe6cf 100%);overflow:hidden}
.v70-short-card-preview::after{content:"";position:absolute;inset:0;background:radial-gradient(circle at 30% 20%,#ffffffa8,transparent 40%)}
.v70-short-play{position:relative;z-index:1;display:grid;place-items:center;width:52px;height:52px;border-radius:50%;background:#ffffffd9;color:#3c5790;font-size:1.35rem;box-shadow:0 6px 14px #1c4e7030}
.v70-short-index{position:absolute;z-index:1;left:12px;top:10px;padding:5px 10px;border-radius:999px;background:#ffffffcf;color:#203b53;font-size:.75rem;font-weight:800;letter-spacing:.06em}
.v70-short-card-label{margin:15px 0 5px;color:#203b53;font-size:1.06rem;font-weight:800}
.v70-short-card-time{color:#536b84;font-size:.9rem;line-height:1.45}
.v70-short-card-score{display:inline-block;margin-top:8px;padding:4px 9px;border-radius:999px;background:#edf5fb;color:#315c7a;font-size:.75rem;font-weight:700}
[class*="st-key-v70_short_card_"] .stButton{margin-top:17px !important}
[class*="st-key-v70_short_card_"] .stButton>button{min-height:42px !important;border-radius:14px !important;font-size:.83rem !important}
[class*="st-key-v70_short_card_"]:has(button[kind="primary"]){border-color:#7191d2 !important;background:#f4f1ff !important;box-shadow:0 12px 28px rgba(112,81,214,.13) !important}
.st-key-v71-short-grid [data-testid="stHorizontalBlock"]{gap:24px !important;align-items:stretch !important}
[class*="st-key-v71_short_card_"]{height:100% !important;padding:18px !important;border:1px solid #d4e4ef !important;border-radius:24px !important;background:#fbfdff !important;box-shadow:0 10px 24px rgba(28,78,112,.08) !important}
[class*="st-key-v71_short_card_"] iframe{display:block !important;width:100% !important;height:174px !important;border:0 !important;border-radius:16px !important;background:#101a2c !important}
[class*="st-key-v71_short_card_"] .stButton{margin-top:17px !important}
[class*="st-key-v71_short_card_"] .stButton>button{min-height:42px !important;border-radius:14px !important;font-size:.83rem !important}
[class*="st-key-v71_short_card_"]:has(button[kind="primary"]){border-color:#7191d2 !important;background:#f4f1ff !important;box-shadow:0 12px 28px rgba(112,81,214,.13) !important}
.st-key-v69_engine_0 button::before{background-color:#b9dbff !important;background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23203b53%22%20stroke-width%3D%221.8%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M14%205c3-3%207-3%207-3s0%204-3%207l-7%207-5-5zM8%209H4l-2%205%205-1m8%203v4l-5%202%201-5M5%2016l-3%206%206-3%22%2F%3E%3Ccircle%20cx%3D%2216%22%20cy%3D%227%22%20r%3D%222%22%2F%3E%3C%2Fsvg%3E") !important}
.st-key-v69_engine_1 button::before{background-color:#bae7c8 !important;background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23203b53%22%20stroke-width%3D%221.8%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M7%203h10v7a5%205%200%200%201-10%200zM7%205H3v3a4%204%200%200%200%204%204m10-7h4v3a4%204%200%200%201-4%204m-5%203v6m-4%200h8%22%2F%3E%3C%2Fsvg%3E") !important}
.st-key-v69_engine_2 button::before{background-color:#ffdc88 !important;background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23203b53%22%20stroke-width%3D%221.8%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22m13%202-9%2012h7l-1%208%2010-13h-7z%22%2F%3E%3C%2Fsvg%3E") !important}
.st-key-v69_engine_3 button::before{background-color:#d8bdff !important;background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23203b53%22%20stroke-width%3D%221.8%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Crect%20x%3D%229%22%20y%3D%223%22%20width%3D%226%22%20height%3D%2212%22%20rx%3D%223%22%2F%3E%3Cpath%20d%3D%22M5%2010v2a7%207%200%200%200%2014%200v-2M12%2019v3%22%2F%3E%3C%2Fsvg%3E") !important}
.st-key-v69_engine_4 button::before{background-color:#ffbaa7 !important;background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23203b53%22%20stroke-width%3D%221.8%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Ccircle%20cx%3D%2212%22%20cy%3D%2212%22%20r%3D%227%22%2F%3E%3Ccircle%20cx%3D%2212%22%20cy%3D%2212%22%20r%3D%222%22%2F%3E%3Cpath%20d%3D%22M12%202v4m0%2012v4M2%2012h4m12%200h4%22%2F%3E%3C%2Fsvg%3E") !important}
.st-key-v69_social_youtube button,.st-key-v69_social_tiktok button,.st-key-v69_social_instagram button{min-height:100px !important;display:flex !important;justify-content:center !important;align-items:center !important;gap:15px !important;padding:18px !important;border-radius:21px !important;box-shadow:none !important}
.st-key-v69_social_youtube button p,.st-key-v69_social_tiktok button p,.st-key-v69_social_instagram button p{color:white !important;font-size:1.2rem !important;font-weight:700 !important}
.st-key-v69_social_youtube button{background:#c91425 !important;border-color:#a90e1c !important}
.st-key-v69_social_tiktok button{background:#161820 !important;border-color:#161820 !important}
.st-key-v69_social_instagram button{background:linear-gradient(120deg,#7629a4,#ac285e,#b04420) !important;border-color:#94345b !important}
.st-key-v69_social_youtube button::before,.st-key-v69_social_tiktok button::before,.st-key-v69_social_instagram button::before{content:"";width:46px !important;height:46px !important;background-color:transparent !important;border:0 !important;border-radius:0 !important;background-size:contain !important;transform:none !important;margin:0 !important}
@media(max-width:750px){
  /* V78 MOBILE BETA — layout pensato per iPhone/Android, non desktop schiacciato. */
  .block-container{width:100% !important;max-width:100% !important;padding-left:.75rem !important;padding-right:.75rem !important;padding-top:.45rem !important}
  .hero-title{font-size:clamp(2.15rem,12vw,3.15rem) !important;line-height:.92 !important}
  .hero-sub{font-size:.92rem !important;margin-top:10px !important}
  .gsf-hero{padding:16px 6px 8px !important}
  .gsf-hero h1{font-size:1.72rem !important}
  [data-testid="stFileUploader"]{padding:8px !important;border-radius:22px !important}
  [data-testid="stFileUploaderDropzone"]{min-height:116px !important;border-radius:18px !important}
  .st-key-v69_engine_grid [data-testid="stHorizontalBlock"]{display:grid !important;grid-template-columns:repeat(2,minmax(0,1fr)) !important;gap:12px !important;align-items:stretch !important}
  .st-key-v69_engine_grid [data-testid="stColumn"],
  .st-key-v69_engine_grid [data-testid="column"]{width:100% !important;min-width:0 !important;max-width:none !important;flex:none !important}
  .st-key-v69_engine_grid [data-testid="stColumn"]:nth-child(5),
  .st-key-v69_engine_grid [data-testid="column"]:nth-child(5){grid-column:1 / -1 !important}
  .st-key-v69_engine_grid button{height:154px !important;min-height:154px !important;padding:14px 7px 9px !important;gap:10px !important;border-radius:20px !important}
  .st-key-v69_engine_grid button::before{width:68px !important;height:68px !important;min-width:68px !important;flex-basis:68px !important;background-size:34px !important}
  .st-key-v69_engine_grid button p{font-size:.88rem !important;line-height:1.2 !important;min-height:34px !important}
  .st-key-v73-duration{--duration-size:clamp(104px,31vw,126px) !important}
  .st-key-v73-duration [data-testid="stHorizontalBlock"]{gap:16px !important}
  .stButton>button[kind="primary"]{min-height:3.35rem !important;font-size:1rem !important}
  iframe{max-width:100% !important}
}
.st-key-v69_social_youtube button::before{background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%3E%3Crect%20x%3D%221%22%20y%3D%225%22%20width%3D%2222%22%20height%3D%2214%22%20rx%3D%225%22%20fill%3D%22white%22%2F%3E%3Cpath%20d%3D%22m10%209%206%203-6%203z%22%20fill%3D%22%23c91425%22%2F%3E%3C%2Fsvg%3E") !important}
.st-key-v69_social_instagram button::before{background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%3E%3Crect%20x%3D%223%22%20y%3D%223%22%20width%3D%2218%22%20height%3D%2218%22%20rx%3D%225%22%20fill%3D%22none%22%20stroke%3D%22white%22%20stroke-width%3D%222%22%2F%3E%3Ccircle%20cx%3D%2212%22%20cy%3D%2212%22%20r%3D%224%22%20fill%3D%22none%22%20stroke%3D%22white%22%20stroke-width%3D%222%22%2F%3E%3Ccircle%20cx%3D%2217.5%22%20cy%3D%226.5%22%20r%3D%221.2%22%20fill%3D%22white%22%2F%3E%3C%2Fsvg%3E") !important}
.st-key-v69_social_tiktok button::before{background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%3E%3Cpath%20d%3D%22M14%203h3c0%203%202%205%205%205v3a9%209%200%200%201-5-2v8a6%206%200%201%201-6-6v3a3%203%200%201%200%203%203z%22%20fill%3D%22%2325f4ee%22%20transform%3D%22translate(-1%201)%22%2F%3E%3Cpath%20d%3D%22M14%203h3c0%203%202%205%205%205v3a9%209%200%200%201-5-2v8a6%206%200%201%201-6-6v3a3%203%200%201%200%203%203z%22%20fill%3D%22%23fe2c55%22%20transform%3D%22translate(1%200)%22%2F%3E%3Cpath%20d%3D%22M14%203h3c0%203%202%205%205%205v3a9%209%200%200%201-5-2v8a6%206%200%201%201-6-6v3a3%203%200%201%200%203%203z%22%20fill%3D%22white%22%2F%3E%3C%2Fsvg%3E") !important}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:10px;">
  <div class="hero-title">Gaming<br>Shorts Factory</div>
  <div class="hero-sub">Crea il tuo Short in quattro passaggi semplici.</div>
</div>

<div class="flow"><div class="orb"><span class="v67-badge blue"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 16V4m-5 5 5-5 5 5M4 16v4h16v-4"/></svg></span><span>CARICA</span></div><div class="orb"><span class="v67-badge mint"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg></span><span>SCEGLI</span></div><div class="orb"><span class="v67-badge amber"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m4 16 12-12 4 4L8 20H4zm10-10 4 4"/></svg></span><span>MODIFICA</span></div><div class="orb"><span class="v67-badge lilac"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 11 18-8-8 18-3-8zm7 2L21 3"/></svg></span><span>PUBBLICA</span></div></div>


""", unsafe_allow_html=True)


# Cerca FFmpeg automaticamente: prima il vecchio percorso, poi PATH di Windows.
import shutil

def _gsf_executable_name(base):
    return base + (".exe" if os.name == "nt" else "")


def _gsf_candidate_executables(base):
    """Cross-platform lookup used both locally and on a Linux web server."""
    env_name = "FFMPEG_BINARY" if base == "ffmpeg" else "FFPROBE_BINARY"
    candidates = []
    env_value = str(os.environ.get(env_name, "") or "").strip()
    if env_value:
        candidates.append(os.path.expanduser(env_value))

    in_path = shutil.which(base)
    if in_path:
        candidates.append(in_path)

    try:
        app_dir = Path(__file__).resolve().parent
    except Exception:
        app_dir = Path.cwd()
    exe = _gsf_executable_name(base)
    candidates.extend([
        str(app_dir / exe),
        str(app_dir / "bin" / exe),
        str(app_dir / "ffmpeg" / "bin" / exe),
    ])

    home = Path.home()
    if os.name == "nt":
        candidates.extend([
            str(home / "ffmpeg" / "bin" / exe),
            str(home / "Desktop" / "ffmpeg" / "bin" / exe),
            str(home / "Downloads" / "ffmpeg" / "bin" / exe),
        ])
    else:
        candidates.extend([
            f"/usr/bin/{base}",
            f"/usr/local/bin/{base}",
            f"/opt/homebrew/bin/{base}",
            f"/opt/local/bin/{base}",
        ])

    seen = set()
    for candidate in candidates:
        candidate = str(candidate or "").strip()
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def trova_ffmpeg():
    return _gsf_candidate_executables("ffmpeg")


def trova_ffprobe():
    # Prefer the sibling ffprobe from the same FFmpeg installation.
    if FFMPEG_PATH:
        sibling = os.path.join(os.path.dirname(FFMPEG_PATH), _gsf_executable_name("ffprobe"))
        if os.path.isfile(sibling):
            return sibling
    return _gsf_candidate_executables("ffprobe")


FFMPEG_PATH = trova_ffmpeg()
FFPROBE_PATH = trova_ffprobe()


def durata_video(file_path):
    if not FFMPEG_PATH:
        st.error(
            "⚠️ FFmpeg non trovato sul server/sistema. "
            "Installa FFmpeg oppure imposta FFMPEG_BINARY nel PATH dell'ambiente."
        )
        return None

    try:
        path=Path(file_path)
        stat=path.stat()
    except OSError:
        return None
    return _gsf_duration_cached(
        str(path),stat.st_size,stat.st_mtime_ns,FFMPEG_PATH
    )


@st.cache_data(show_spinner=False,max_entries=256)
def _gsf_duration_cached(file_path,size,mtime_ns,ffmpeg_path):
    """Read each unchanged media duration once across Streamlit reruns."""

    comando = [
        ffmpeg_path,
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
            norm = (db - db_min) / span
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
    """Create a lightweight preview; software encode works without Intel QSV."""
    base = [
        FFMPEG_PATH,
        "-y",
        "-ss", str(start),
        "-i", input_file,
        "-t", str(duration),
        "-vf", "scale=640:-2",
    ]
    for encoder,options in (
        ("h264_qsv",["-preset","veryfast","-global_quality","30"]),
        ("libx264",["-preset","veryfast","-crf","30"]),
    ):
        try:
            if os.path.exists(output_file):
                os.unlink(output_file)
            risultato=subprocess.run(
                base+["-c:v",encoder]+options+[
                    "-c:a","aac","-b:a","96k",
                    "-movflags","+faststart",output_file
                ],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
                timeout=max(120.0,float(duration)*15.0)
            )
            if risultato.returncode==0 and os.path.exists(output_file):
                return True
        except (OSError,subprocess.TimeoutExpired):
            continue
    return False



@st.cache_resource(show_spinner=False)
def _gsf_subtitle_whisper_model():
    """
    Modello dedicato ai sottotitoli.
    In locale resta Small; nella beta web/mobile a memoria ridotta usiamo Tiny
    per non superare il limite del container durante render e trascrizione.
    """
    if GSF_LOW_MEMORY_WEB:
        return WhisperModel("tiny", device="cpu", compute_type="int8")
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
    tmp_dir=_gsf_session_mkdtemp("gsf_render_sub_")
    wav=os.path.join(tmp_dir,"speech.wav")
    try:
        cmd=[
            FFMPEG_PATH,"-y","-ss",str(max(0.0,float(start))),"-i",str(source_path),
            "-t",str(max(.1,float(duration))),"-vn","-ac","1","-ar","16000",
            "-af","highpass=f=70,lowpass=f=7800",
            wav
        ]
        r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if r.returncode!=0 or not os.path.exists(wav):
            return [],"Estrazione audio sottotitoli non riuscita"

        model=_gsf_subtitle_whisper_model()
        segs,info=model.transcribe(
            wav,
            language="it",
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



def _gsf_render_transcribe_words_lowmem(*args, **kwargs):
    """V80.2: release cached Whisper RAM before FFmpeg rendering."""
    try:
        return _gsf_render_transcribe_words(*args, **kwargs)
    finally:
        if GSF_LOW_MEMORY_WEB:
            try:
                _gsf_subtitle_whisper_model.clear()
            except Exception:
                pass
            try:
                import gc
                gc.collect()
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
    "goal": "CHE GOL!",
    "shooter_elimination": "ELIMINATO!",
    "victory": "VITTORIA!",
    "sports_big_chance": "CHE OCCASIONE!",
    "racing": "MOMENTO GARA!",
    "achievement": "SBLOCCATO!",
    "impact_event": "ECCO IL MOMENTO!",
}

_GSF_CATEGORY_HOOKS = {
    "reaction": "CHE REAZIONE!",
    "action": "AZIONE PURA!",
    "story": "ECCO IL MOMENTO!",
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
    reaction=max(
        float(features.get("reaction",0.0)),
        float(features.get("reaction_cue",0.0)),
    )
    payoff=float(features.get("payoff_position",0.0))
    hook_score=float(features.get("hook_score",0.0))

    if event_score>=0.56 and event_type in _GSF_HOOK_TEMPLATES:
        return _GSF_HOOK_TEMPLATES[event_type]

    # A category hook is shown only when the underlying moment is strong enough.
    # This avoids stamping generic text over weak clips.
    if category=="reaction" and reaction>=0.34:
        return _GSF_CATEGORY_HOOKS["reaction"]
    if category=="action" and max(event_score,hook_score,payoff)>=0.38:
        return _GSF_CATEGORY_HOOKS["action"]
    if category=="story" and max(hook_score,payoff)>=0.42:
        return _GSF_CATEGORY_HOOKS["story"]

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


def _gsf_subtitle_groups(words,max_words=4,max_chars=25,max_gap=0.58):
    groups=[]
    current=[]
    for item in (words or []):
        tx=str((item or {}).get("text","") or "").strip()
        if not tx:
            continue
        if current:
            joined=" ".join(
                str((w or {}).get("text","") or "").strip()
                for w in current+[item]
            ).strip()
            try:
                gap=float(item.get("start",0.0))-float(current[-1].get("end",0.0))
            except Exception:
                gap=0.0
            if len(current)>=int(max_words) or len(joined)>int(max_chars) or gap>float(max_gap):
                groups.append(current)
                current=[]
        current.append(item)
        if tx.endswith((".", "!", "?", "…")):
            groups.append(current)
            current=[]
    if current:
        groups.append(current)
    return groups


def _gsf_clean_burnin_text(value):
    text=str(value or "")
    # Emoji / pictographs + variation selectors. Keep punctuation and accented text.
    text=re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF]", "", text)
    text=text.replace("\ufe0f","").replace("\u200d","")
    text=re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


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

    hook=_gsf_clean_burnin_text(hook_text)
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
        groups=_gsf_subtitle_groups(words)
        for group in groups:
            for local_idx,word in enumerate(group):
                parts=[]
                for j,item in enumerate(group):
                    tx=_gsf_ass_escape(item.get("text",""))
                    if j==local_idx:
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
                own_end=max(a+.06,float(word.get("end",a+.16)))
                if local_idx+1<len(group):
                    try:
                        next_start=float(group[local_idx+1].get("start",own_end))
                    except Exception:
                        next_start=own_end
                    b=max(own_end,min(next_start,own_end+.22))
                else:
                    b=own_end+.10
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


def _gsf_smooth_reframe_track(track):
    pts=[]
    for item in (track or []):
        try:
            pts.append({
                "t":float(item["t"]),
                "cx":max(0.10,min(0.90,float(item["cx"]))),
            })
        except Exception:
            continue
    pts=sorted(pts,key=lambda x:x["t"])
    if len(pts)<2:
        return pts

    out=[dict(pts[0])]
    prev=float(pts[0]["cx"])
    for item in pts[1:]:
        raw=float(item["cx"])
        delta=max(-0.22,min(0.22,raw-prev))
        alpha=0.64 if abs(delta)>=0.08 else 0.36
        smooth=prev+delta*alpha
        smooth=max(0.10,min(0.90,smooth))
        out.append({"t":float(item["t"]),"cx":smooth})
        prev=smooth
    return out


def _gsf_smart_reframe_cx_expression(track):
    """Smooth piecewise-linear normalized horizontal center for FFmpeg crop."""
    pts=[]
    for item in _gsf_smooth_reframe_track(track):
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
    temp_dir=_gsf_session_mkdtemp("gsf_render_core_")
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
                used_words,subtitle_error=_gsf_render_transcribe_words_lowmem(
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
                    "-global_quality","21",
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
                    "-crf","21",
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

            try:
                r=subprocess.run(
                    cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
                    timeout=max(180.0,min(3600.0,duration*15.0))
                )
            except subprocess.TimeoutExpired:
                last_error=f"Render {encoder} interrotto: tempo massimo superato."
                continue
            if r.returncode==0 and os.path.exists(output_path) and os.path.getsize(output_path)>0:
                return {
                    "ok":True,
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


def _gsf_upload_identity(video_obj):
    """
    Full-content identity; the same Streamlit upload ID reuses its fingerprint
    across reruns without reading a multi-gigabyte gameplay again.
    """
    try:
        name=str(getattr(video_obj,"name","video") or "video")
        size=int(getattr(video_obj,"size",0) or 0)
        file_id=getattr(video_obj,"file_id",None)
        cache_key=(str(file_id),name,size) if file_id is not None else None
        cached=st.session_state.get("gsf_upload_fingerprint_v63")
        if cache_key is not None and cached and cached.get("key")==cache_key:
            return cached["token"]
        old_pos=0
        try:
            old_pos=int(video_obj.tell())
        except Exception:
            old_pos=0
        h=hashlib.sha256()
        try:
            video_obj.seek(0)
            while True:
                chunk=video_obj.read(8*1024*1024)
                if not chunk:
                    break
                h.update(chunk)
        finally:
            video_obj.seek(old_pos)
        token=f"{name}|{size}|{h.hexdigest()[:24]}"
        st.session_state["gsf_upload_fingerprint_v63"]={
            "key":cache_key,"token":token
        }
        return token
    except Exception as error:
        raise RuntimeError("Impossibile verificare il gameplay caricato") from error


def _gsf_materialize_upload_once(video_obj):
    _recovered = getattr(video_obj, "_gsf_recovered_path", "")
    if _recovered and Path(_recovered).is_file():
        _p = Path(_recovered)
        _st = _p.stat()
        _token = hashlib.sha256(
            f"recovered|{_p}|{_st.st_size}|{_st.st_mtime_ns}".encode("utf-8")
        ).hexdigest()
        st.session_state["gsf_source_path"] = str(_p)
        st.session_state.setdefault("gsf_source_name", getattr(video_obj, "name", _p.name))
        return str(_p), _token, True, {
            "mode": "recovered", "bytes": int(_st.st_size),
            "hash_ms": 0.0, "write_ms": 0.0, "total_ms": 0.0,
        }
    token=_gsf_upload_identity(video_obj)
    try:
        name=Path(str(getattr(video_obj,"name","video.mp4") or "video.mp4")).name
        size=int(getattr(video_obj,"size",0) or 0)
    except Exception:
        name="video.mp4"
        size=0

    ext=Path(name).suffix or ".mp4"
    safe_base=re.sub(r"[^A-Za-z0-9_.-]+","_",Path(name).stem)[:80] or "video"
    digest=token.rsplit("|",1)[-1] if "|" in token else hashlib.md5(token.encode(), usedforsecurity=False).hexdigest()[:16]
    path=GSF_PREVIEW_DIR / f"source_{safe_base}_{digest}{ext}"

    previous_token=st.session_state.get("gsf_source_token")
    previous_path=st.session_state.get("gsf_source_path")
    same_session=(
        previous_token==token
        and previous_path
        and os.path.exists(previous_path)
        and (size<=0 or os.path.getsize(previous_path)==size)
    )

    disk_reused=False
    bytes_written=0
    write_seconds=0.0

    if same_session:
        path=Path(previous_path)
    elif path.exists() and (size<=0 or path.stat().st_size==size):
        disk_reused=True
    else:
        t0=time.perf_counter()
        tmp_path=Path(str(path)+".partial")
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass

        old_pos=0
        try:
            old_pos=int(video_obj.tell())
        except Exception:
            old_pos=0

        with open(tmp_path,"wb") as f:
            video_obj.seek(0)
            while True:
                chunk=video_obj.read(8*1024*1024)
                if not chunk:
                    break
                f.write(chunk)
                bytes_written+=len(chunk)

        try:
            video_obj.seek(old_pos)
        except Exception:
            try:
                video_obj.seek(0)
            except Exception:
                pass

        os.replace(tmp_path,path)
        write_seconds=time.perf_counter()-t0

    # New gameplay: release caches that can retain large old results/bytes.
    if previous_token and previous_token!=token:
        for temp_key,prefix in (("editor_dir","gsf_editor_"),
                                ("inline_editor_dir","gsf_inline_ai_")):
            old_temp=st.session_state.get(temp_key)
            if old_temp:
                try:
                    temp_path=Path(old_temp)
                    if _gsf_is_session_temp(temp_path, prefix):
                        shutil.rmtree(temp_path,ignore_errors=True)
                except OSError:
                    pass
        for served in st.session_state.pop("gsf_served_links_v63",set()):
            try:
                old_link=Path(served)
                if old_link.parent==GSF_PREVIEW_DIR and old_link!=path:
                    old_link.unlink(missing_ok=True)
            except OSError:
                pass
        st.session_state.pop("gsf_served_sources_v63",None)
        for key in (
            "gsf_ai_scan_cache_v40",
            "gsf_ai_scan_cache_v50",
            "gsf_ai_voice_cache_v40",
            "gsf_ai_refine_motion_cache_v50",
            "gsf_smart_reframe_cache_v42",
            "gsf_fast_ai_cache",
            "gsf_ai_preview_cache_v61",
            "gsf_final_master_cache_v44",
        ):
            try:
                st.session_state.pop(key,None)
            except Exception:
                pass

        # V54: new gameplay = genuinely new project state.
        # Social account tokens live on disk and stay connected, but every
        # clip/editor/publication state from the previous gameplay is cleared.
        _workflow_exact={
            "preview_bytes",
            "preview_key",
            "publication_ready",
            "publication_source",
            "publication_origin",
            "publication_preview_bytes",
            "publication_final_bytes",
            "publication_final_signature",
            "publication_final_encoder",
            "publication_final_seconds",
            "gsf_final_recipe",
            "auto_clip_scelta",
            "auto_clip_duration",
            "auto_clip_candidati",
            "ai_director_scores",
            "clip_rifinite",
            "inline_final_bytes",
            "inline_editor_id",
            "inline_editor_dir",
            "inline_editor_input",
            "inline_editor_original_input",
            "inline_editor_source_start",
            "inline_editor_duration",
            "editor_key",
            "editor_dir",
            "editor_input",
            "editor_output",
            "editor_output_bytes",
            "editor_output_name",
            "editor_quick_bytes",
            "editor_quick_path",
            "editor_quick_signature",
            "editor_sub_words",
            "editor_sub_live_words",
            "editor_sub_text",
            "editor_sub_applied_text",
            "editor_sub_scene_token",
            "show_social_publish_v53",
            "show_social_publish_v54",
            "social_final_context_v53",
            "social_final_context_v54",
            "social_connect_error_v54",
            "youtube_last_result",
            "tiktok_last_result",
            "instagram_last_result",
            "manual_publish_export_v56",
            "manual_publish_error_v56",
            "manual_publish_feedback_v56",
            "social_auth_url_v77",
            "social_auth_platform_v77",
            "youtube_autofill_feedback_v57",
            "youtube_autofill_install_v57",
            "risultati_batch",
        }
        _workflow_prefixes=(
            "social_title_v53_",
            "social_title_v54_",
            "social_description_v53_",
            "social_description_v54_",
            "social_hashtags_v53_",
            "social_hashtags_v54_",
            "editor_trim_",
            "inline_seek_",
            "inline_seek_feedback_",
            "inline_seek_nonce_",
        )
        for key in list(st.session_state.keys()):
            if (
                key in _workflow_exact
                or any(str(key).startswith(p) for p in _workflow_prefixes)
            ):
                try:
                    st.session_state.pop(key,None)
                except Exception:
                    pass

        # Remove only the old shared SOURCE file, never generated previews/results.
        try:
            old=Path(previous_path) if previous_path else None
            if (
                old and old.exists()
                and old.parent==GSF_PREVIEW_DIR
                and old.name.startswith("source_")
                and old!=path
            ):
                old.unlink()
        except Exception:
            pass

    st.session_state["gsf_source_token"]=token
    st.session_state["gsf_source_path"]=str(path)
    st.session_state["gsf_source_size"]=int(size or (path.stat().st_size if path.exists() else 0))
    st.session_state["gsf_source_perf"]={
        "same_session":bool(same_session),
        "disk_reused":bool(disk_reused),
        "bytes_written":int(bytes_written),
        "write_seconds":round(float(write_seconds),3),
    }

    return str(path),token,bool(same_session or disk_reused),st.session_state["gsf_source_perf"]


def _gsf_upload_master_token(video_obj):
    _recovered = getattr(video_obj, "_gsf_recovered_path", "")
    if _recovered and Path(_recovered).is_file():
        _p = Path(_recovered)
        _st = _p.stat()
        return hashlib.sha256(
            f"recovered-master|{_p}|{_st.st_size}|{_st.st_mtime_ns}".encode("utf-8")
        ).hexdigest()
    """Stable identity shared by AI, single render and batch render."""
    current=st.session_state.get("gsf_source_token")
    if current:
        return str(current)
    return _gsf_upload_identity(video_obj)


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


def _gsf_master_cache_trim(cache,max_items=6,max_bytes=128*1024*1024):
    try:
        def total_bytes():
            return sum(len(item.get("bytes",b"")) for item in cache.values())
        while cache and (len(cache)>int(max_items) or total_bytes()>int(max_bytes)):
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

    Automatic final-render paths share this function.
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
        own_temp=_gsf_session_mkdtemp("gsf_master_v44_")
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

        if len(data)<=128*1024*1024:
            cache[signature]={"bytes":data,"meta":meta}
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



GSF_AI_ENGINE_VERSION = "v52-keyframe-turbo"


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
    cache = st.session_state.setdefault("gsf_ai_scan_cache_v50", {})
    key = (
        GSF_AI_ENGINE_VERSION,
        str(cache_token or input_file)
    )

    if key in cache:
        return cache[key], True

    scan = None
    try:
        import sys as _gsf_sys
        if "/app/web" not in _gsf_sys.path:
            _gsf_sys.path.insert(0,"/app/web")
        from gsf_bucket_bridge import load_prescan_from_marker as _gsf_load_prescan
        scan = _gsf_load_prescan(
            GSF_PREVIEW_DIR,
            GSF_AI_ENGINE_VERSION
        )
    except Exception:
        scan = None

    if scan is None:
        scan = _gsf_ai_scan_base(input_file)

    cache[key] = scan
    _gsf_ai_cache_trim(cache, 2)
    return scan, False


def _gsf_ai_voice_cached(input_file, start, duration, cache_token=None, force=False):
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
        str(st.session_state.get("gioco", "") or ""),
        bool(force)
    )

    if key in cache:
        return cache[key], True

    result = _gsf_ai_voice_features(
        input_file, start, duration, force=force
    )
    cache[key] = result
    _gsf_ai_cache_trim(cache, 96)
    return result, False


def _gsf_ai_scan_profile_for_duration(total_seconds):
    """
    Adaptive full-video scan.
    Short videos keep 2 fps; long gameplay reduces full-pass cost.
    Dense detail is restored later only on shortlisted windows.
    """
    total=max(0.0,float(total_seconds or 0.0))

    if total<=3*60:
        return {
            "tier":"standard",
            "video_fps":2.0,
            "analysis_width":192,
            "adaptive":False,
            "keyframes_only":False,
        }
    if total<=20*60:
        return {
            "tier":"medium_turbo",
            "video_fps":0.5,
            "analysis_width":128,
            "adaptive":True,
            "keyframes_only":True,
        }
    if total<=60*60:
        return {
            "tier":"long_turbo",
            "video_fps":0.35,
            "analysis_width":112,
            "adaptive":True,
            "keyframes_only":True,
        }
    return {
        "tier":"very_long_turbo",
        "video_fps":0.25,
        "analysis_width":112,
        "adaptive":True,
        "keyframes_only":True,
    }


def _gsf_interpolate_motion_points(points,n):
    """Interpolate sparse adaptive visual samples onto the 0.5 s AI grid."""
    n=max(0,int(n))
    if n<=0:
        return []
    if not points:
        return [0.0]*n

    known=sorted(
        (max(0,int(k)),float(v))
        for k,v in points.items()
        if 0<=int(k)<n
    )
    if not known:
        return [0.0]*n

    out=[0.0]*n
    first_i,first_v=known[0]
    for i in range(0,min(n,first_i+1)):
        out[i]=first_v

    for idx in range(len(known)-1):
        i0,v0=known[idx]
        i1,v1=known[idx+1]
        if i1<=i0:
            continue
        span=float(i1-i0)
        for i in range(i0,min(n,i1+1)):
            alpha=(i-i0)/span
            out[i]=v0*(1.0-alpha)+v1*alpha

    last_i,last_v=known[-1]
    for i in range(max(0,last_i),n):
        out[i]=last_v
    return out


def _gsf_ai_scan_base(input_file):
    """
    V50 whole-game scan:
    - audio and video FFmpeg passes run concurrently;
    - video fps/width adapts to gameplay duration;
    - result remains on the same 0.5 s grid expected by Point 3.
    """
    scan_t0=time.perf_counter()
    total_seconds=float(durata_video(input_file) or 0.0)
    profile=_gsf_ai_scan_profile_for_duration(total_seconds)
    video_fps=float(profile["video_fps"])
    analysis_width=int(profile["analysis_width"])

    cmd_audio=[
        FFMPEG_PATH,"-hide_banner","-threads","1","-i",str(input_file),"-vn",
        "-af",
        (
            "aresample=8000,asetnsamples=n=4000:p=0,"
            "astats=metadata=1:reset=1,"
            "ametadata=print:key=lavfi.astats.Overall.RMS_level,"
            "ametadata=print:key=lavfi.astats.Overall.Peak_level"
        ),
        "-f","null","-"
    ]

    keyframes_only=bool(profile.get("keyframes_only",False))
    cmd_video=[FFMPEG_PATH,"-hide_banner","-threads","2"]
    if keyframes_only:
        cmd_video += ["-skip_frame","nokey"]
    cmd_video += ["-i",str(input_file),"-an","-vf"]
    if keyframes_only:
        cmd_video += [
            f"scale={analysis_width}:-2,"
            "select='gte(scene,0)',metadata=print"
        ]
    else:
        cmd_video += [
            f"fps={video_fps:g},scale={analysis_width}:-2,"
            "select='gte(scene,0)',metadata=print"
        ]
    cmd_video += ["-f","null","-"]

    def run_capture(cmd):
        t0=time.perf_counter()
        try:
            r=subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=max(180.0,min(7200.0,total_seconds*2.0))
            )
            return r, time.perf_counter()-t0, ""
        except Exception as e:
            return None, time.perf_counter()-t0, str(e)

    # Independent streams => parallel wall-clock scan.
    with ThreadPoolExecutor(max_workers=2) as pool:
        fa=pool.submit(run_capture,cmd_audio)
        fv=pool.submit(run_capture,cmd_video)
        ra,audio_seconds,audio_error=fa.result()
        rv,video_seconds,video_error=fv.result()

    raw_audio=""
    if ra is not None:
        raw_audio=(ra.stdout or "")+"\n"+(ra.stderr or "")

    raw_video=""
    if rv is not None:
        raw_video=(rv.stdout or "")+"\n"+(rv.stderr or "")

    audio_points={}
    current_t=None
    for line in raw_audio.splitlines():
        mt=re.search(r"pts_time:([0-9.]+)",line)
        if mt:
            try:
                current_t=float(mt.group(1))
            except Exception:
                current_t=None
        if current_t is None:
            continue

        bucket=max(0,int(round(current_t*2.0)))
        if "lavfi.astats.Overall.RMS_level=" in line:
            try:
                v=float(
                    line.split(
                        "lavfi.astats.Overall.RMS_level=",1
                    )[1].strip().split()[0]
                )
                if math.isfinite(v):
                    audio_points.setdefault(bucket,{})["rms"]=v
            except Exception:
                pass
        elif "lavfi.astats.Overall.Peak_level=" in line:
            try:
                v=float(
                    line.split(
                        "lavfi.astats.Overall.Peak_level=",1
                    )[1].strip().split()[0]
                )
                if math.isfinite(v):
                    audio_points.setdefault(bucket,{})["peak"]=v
            except Exception:
                pass

    motion_points={}
    current_t=None
    for line in raw_video.splitlines():
        mt=re.search(r"pts_time:([0-9.]+)",line)
        if mt:
            try:
                current_t=float(mt.group(1))
            except Exception:
                current_t=None

        if current_t is not None and "lavfi.scene_score=" in line:
            try:
                v=float(
                    line.split(
                        "lavfi.scene_score=",1
                    )[1].strip().split()[0]
                )
                bucket=max(0,int(round(current_t*2.0)))
                motion_points[bucket]=max(
                    motion_points.get(bucket,0.0),
                    max(0.0,v)
                )
            except Exception:
                pass

    all_buckets=set(audio_points)|set(motion_points)
    if total_seconds>0:
        all_buckets.add(max(0,int(math.ceil(total_seconds*2.0))-1))

    meta={
        "parallel":True,
        "tier":profile["tier"],
        "adaptive":bool(profile["adaptive"]),
        "video_fps":video_fps,
        "analysis_width":analysis_width,
        "keyframes_only":keyframes_only,
        "duration_seconds":round(total_seconds,2),
        "audio_seconds":round(float(audio_seconds),3),
        "video_seconds":round(float(video_seconds),3),
        "wall_seconds":round(time.perf_counter()-scan_t0,3),
        "audio_error":audio_error,
        "video_error":video_error,
    }

    if not all_buckets:
        return {
            "step":0.5,
            "audio":[],
            "peak":[],
            "motion":[],
            "meta":meta,
        }

    n=max(all_buckets)+2
    rms_raw=[]
    peak_raw=[]
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

    motion_raw=_gsf_interpolate_motion_points(
        motion_points,n
    )

    audio=_gsf_norm_series(rms_raw)
    peak=_gsf_norm_series(peak_raw)
    motion=_gsf_norm_series(motion_raw)

    return {
        "step":0.5,
        "audio":audio,
        "peak":peak,
        "motion":motion,
        "meta":meta,
    }


def _gsf_ai_refine_motion_window(input_file,start,duration):
    """
    Dense second pass only for shortlisted windows on long gameplay.
    Uses 2 fps / 144 px and returns a focused visual-support signal.
    """
    t0=time.perf_counter()
    cmd=[
        FFMPEG_PATH,"-hide_banner","-threads","1",
        "-ss",str(max(0.0,float(start))),
        "-i",str(input_file),
        "-t",str(max(.25,float(duration))),
        "-an",
        "-vf",
        "fps=2,scale=144:-2,select='gte(scene,0)',metadata=print",
        "-f","null","-"
    ]

    try:
        r=subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=max(120.0,min(600.0,float(duration)*15.0))
        )
    except Exception as e:
        return {
            "support":0.0,
            "burst":0.0,
            "peak":0.0,
            "seconds":round(time.perf_counter()-t0,3),
            "error":str(e),
        }

    raw=(r.stdout or "")+"\n"+(r.stderr or "")
    vals=[]
    for line in raw.splitlines():
        if "lavfi.scene_score=" not in line:
            continue
        try:
            v=float(
                line.split(
                    "lavfi.scene_score=",1
                )[1].strip().split()[0]
            )
            if math.isfinite(v):
                vals.append(max(0.0,v))
        except Exception:
            pass

    if not vals:
        return {
            "support":0.0,
            "burst":0.0,
            "peak":0.0,
            "seconds":round(time.perf_counter()-t0,3),
            "error":"",
        }

    ordered=sorted(vals)
    p90=ordered[max(0,int(len(ordered)*0.90)-1)]
    avg=sum(vals)/len(vals)
    peak=max(vals)
    deltas=[
        max(0.0,vals[i]-vals[i-1])
        for i in range(1,len(vals))
    ]
    burst_raw=max(deltas) if deltas else 0.0

    # Absolute scene-score mapping. Kept conservative to avoid
    # turning ordinary camera motion into a fake important event.
    support=max(
        0.0,
        min(
            1.0,
            0.50*min(1.0,avg/0.045)
            +0.50*min(1.0,p90/0.12)
        )
    )
    burst=max(0.0,min(1.0,burst_raw/0.10))
    peak_score=max(0.0,min(1.0,peak/0.20))

    return {
        "support":round(support,4),
        "burst":round(burst,4),
        "peak":round(peak_score,4),
        "samples":len(vals),
        "seconds":round(time.perf_counter()-t0,3),
        "error":"",
    }


def _gsf_ai_refine_motion_cached(
    input_file,start,duration,cache_token=None
):
    cache=st.session_state.setdefault(
        "gsf_ai_refine_motion_cache_v50",{}
    )
    key=(
        GSF_AI_ENGINE_VERSION,
        str(cache_token or input_file),
        round(float(start),2),
        round(float(duration),2),
    )
    if key in cache:
        return cache[key],True

    result=_gsf_ai_refine_motion_window(
        input_file,start,duration
    )
    cache[key]=result
    _gsf_ai_cache_trim(cache,48)
    return result,False


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
    motion=float(features.get("motion_peak",0.0))
    synergy=float(features.get("synergy",0.0))
    support=0.34*audio+0.26*burst+0.22*motion+0.18*synergy
    return max(0.0,min(1.0,semantic*(0.68+0.32*support)))

def _gsf_ai_voice_features(input_file,start,duration,force=False):
    """
    Secondo passaggio SOLO sui candidati migliori.
    Misura parlato, reazione e segnali semantici di eventi importanti.
    V92: nella beta web low-memory Whisper resta spento per i motori normali,
    ma il profilo Reazioni puo forzare Tiny SOLO sui migliori candidati.
    """
    if not GSF_AI_VOICE_TRANSCRIPTION and not bool(force):
        return 0.0,0.0,"",{"type":"","semantic":0.0,"time":None,"text":""}
    wav=None
    try:
        temp_dir=str(GSF_SESSION_TMP_DIR / "gsf_ai_voice")
        os.makedirs(temp_dir,exist_ok=True)
        token=hashlib.md5(f"{input_file}|{start:.2f}|{duration:.2f}".encode(), usedforsecurity=False).hexdigest()[:14]
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
            beam_size=(1 if GSF_LOW_MEMORY_WEB else 2),
            best_of=(1 if GSF_LOW_MEMORY_WEB else 2),
            condition_on_previous_text=False,
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
            0.24*f["motion_avg"]+
            0.12*f["motion_peak"]+
            0.10*f["motion_burst"]+
            0.10*f["active_ratio"]+
            0.06*f["audio_avg"]+
            0.07*f["synergy"]+
            0.08*hook+
            0.07*payoff+
            0.10*event_score+
            0.14*short_score-
            0.28*dead-
            0.18*dead_streak
        )
    elif profile=="reaction":
        score=(
            0.22*reaction+
            0.14*speech+
            0.14*f["audio_burst"]+
            0.12*reaction_cue+
            0.06*f["audio_peak"]+
            0.06*f["synergy"]+
            0.02*f["motion_avg"]+
            0.06*hook+
            0.06*payoff+
            0.10*event_score+
            0.14*short_score-
            0.25*dead-
            0.14*dead_streak
        )
    elif profile=="director":
        score=(
            0.20*f["arc"]+
            0.10*f["center_peak"]+
            0.08*f["activity_avg"]+
            0.07*f["synergy"]+
            0.06*f["active_ratio"]+
            0.10*hook+
            0.10*payoff+
            0.04*speech+
            0.04*reaction+
            0.02*f["motion_avg"]+
            0.12*event_score+
            0.16*short_score-
            0.27*dead-
            0.17*dead_streak
        )
    else:
        score=(
            0.12*f["activity_avg"]+
            0.08*f["activity_peak"]+
            0.08*f["motion_avg"]+
            0.06*f["audio_avg"]+
            0.07*f["synergy"]+
            0.06*f["active_ratio"]+
            0.09*hook+
            0.08*payoff+
            0.04*speech+
            0.05*reaction+
            0.05*f["arc"]+
            0.03*reaction_cue+
            0.14*event_score+
            0.15*short_score-
            0.28*dead-
            0.17*dead_streak
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
                category_bonus=0.070 if this_category not in chosen_categories else -0.020
                short_bonus=0.08*float(f.get("short_worthiness",0.0))
                false_peak_penalty=0.08*float(f.get("false_peak_penalty",0.0))

                # Similarità contenuto pesa meno dell'overlap temporale.
                return (
                    float(score)
                    -0.10*worst_similarity
                    -0.29*worst_overlap
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
    scan_meta=scan.get("meta",{}) or {}
    adaptive_scan=bool(scan_meta.get("adaptive",False))
    voice_cache_hits=0
    voice_checks=0
    forced_voice_checks=0
    refine_cache_hits=0
    refine_checks=0
    n=min(len(scan.get("audio",[])),len(scan.get("motion",[])))
    step=float(scan.get("step",0.5) or 0.5)
    total=n*step
    if n<=0 or total<5:
        return [],{}

    # Ogni 1 secondo: qualità migliore senza moltiplicare troppo il lavoro.
    candidates=[]
    last_start=max(0,int(total-max(5.0,duration)))
    candidate_stride=2 if adaptive_scan else 1
    for start in range(0,last_start+1,candidate_stride):
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
    shortlist_target=6
    coarse_target=7 if adaptive_scan else shortlist_target
    min_gap=max(3.0,duration*0.35)

    for item in candidates:
        if any(abs(item[1]-x[1])<min_gap for x in shortlist):
            continue
        shortlist.append(item)
        if len(shortlist)>=coarse_target:
            break

    # Long gameplay: restore dense visual detail ONLY on the shortlist.
    # This keeps the full-video pass cheap without throwing away local accuracy.
    if adaptive_scan and shortlist:
        refined_items=[None]*len(shortlist)

        def _refine_one(idx,item):
            prelim,start,f=item
            result,hit=_gsf_ai_refine_motion_cached(
                input_file,start,duration,
                cache_token=cache_token
            )
            return idx,item,result,hit

        workers=min(2,len(shortlist))
        with ThreadPoolExecutor(max_workers=max(1,workers)) as pool:
            futures=[
                pool.submit(_refine_one,idx,item)
                for idx,item in enumerate(shortlist)
            ]
            for future in as_completed(futures):
                idx,item,result,hit=future.result()
                prelim,start,f=item
                f=dict(f)
                support=float(result.get("support",0.0))
                burst=float(result.get("burst",0.0))
                peak_ref=float(result.get("peak",0.0))
                f["motion_refined_support"]=support
                f["motion_refined_burst"]=burst
                f["motion_refined_peak"]=peak_ref
                refine_checks+=1
                if hit:
                    refine_cache_hits+=1

                # Conservative second-pass adjustment.
                refined_prelim=float(prelim)*(0.94+0.12*support)
                refined_prelim+=0.025*burst
                refined_items[idx]=(refined_prelim,start,f)

        shortlist=[
            x for x in refined_items if x is not None
        ]
        shortlist.sort(key=lambda x:x[0],reverse=True)
        shortlist=shortlist[:shortlist_target]
    else:
        shortlist=shortlist[:shortlist_target]

    # Voice/reaction/event detection SOLO sulla shortlist.
    enriched=[]
    diagnostics={}
    for prelim,start,f in shortlist:
        f=dict(f)
        transcript=""

        # V92: Reazioni deve davvero ascoltare la voce anche sul profilo web
        # low-memory. Limitiamo Whisper Tiny ai 6 candidati migliori: il primo
        # passaggio audio/video ha gia eliminato le zone deboli, quindi otteniamo
        # semantica e reazioni senza trascrivere inutilmente tutto il gameplay.
        _force_reaction_voice=bool(
            profile=="reaction" and len(enriched)<4
        )
        _voice_result,_voice_hit=_gsf_ai_voice_cached(
            input_file,start,duration,
            cache_token=cache_token,
            force=_force_reaction_voice
        )
        if _force_reaction_voice:
            forced_voice_checks+=1
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

        if "motion_refined_support" in f:
            score*=(
                0.96+
                0.08*float(f.get("motion_refined_support",0.0))
            )
            score+=0.015*float(f.get("motion_refined_burst",0.0))

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
                "motion_refined":round(
                    float(f.get("motion_refined_support",0.0)),3
                ),
                "motion_refined_burst":round(
                    float(f.get("motion_refined_burst",0.0)),3
                ),
            }
        }

    diagnostics["__meta__"]={
        "engine":GSF_AI_ENGINE_VERSION,
        "analysis_seconds":round(time.perf_counter()-_analysis_t0,3),
        "scan_cache_hit":bool(scan_cache_hit),
        "voice_cache_hits":int(voice_cache_hits),
        "voice_checks":int(voice_checks),
        "forced_voice_checks":int(forced_voice_checks),
        "refine_cache_hits":int(refine_cache_hits),
        "refine_checks":int(refine_checks),
        "video_seconds":round(float(total),2),
        "scan_wall_seconds":float(scan_meta.get("wall_seconds",0.0) or 0.0),
        "scan_video_fps":float(scan_meta.get("video_fps",2.0) or 2.0),
        "scan_width":int(scan_meta.get("analysis_width",192) or 192),
        "scan_tier":str(scan_meta.get("tier","standard") or "standard"),
        "scan_parallel":bool(scan_meta.get("parallel",False)),
        "adaptive_scan":bool(scan_meta.get("adaptive",False)),
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




GSF_PUBLISHING_ENGINE_VERSION = "v60-youtube-normal-browser"
GSF_SOCIAL_MODE = "browser-upload-v60"

GSF_YOUTUBE_WINDOWS_WORKER_V60 = 'param(\n    [Parameter(Mandatory=$true)][string]$VideoPath,\n    [Parameter(Mandatory=$true)][string]$StatusPath\n)\n\n$ErrorActionPreference = \'Stop\'\nAdd-Type -AssemblyName UIAutomationClient\nAdd-Type -AssemblyName UIAutomationTypes\nAdd-Type -AssemblyName System.Windows.Forms\nAdd-Type -TypeDefinition @"\nusing System;\nusing System.Runtime.InteropServices;\npublic class GsfWin32 {\n    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();\n}\n"@\n\nfunction Write-Status([string]$State, [string]$Message) {\n    try {\n        $payload = @{\n            state = $State\n            message = $Message\n            updated = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()\n        } | ConvertTo-Json -Compress\n        $temp = $StatusPath + \'.tmp\'\n        [IO.File]::WriteAllText($temp, $payload, [Text.Encoding]::UTF8)\n        Move-Item -LiteralPath $temp -Destination $StatusPath -Force\n    } catch { }\n}\n\nfunction Find-Windows {\n    $root = [System.Windows.Automation.AutomationElement]::RootElement\n    $type = [System.Windows.Automation.ControlType]::Window\n    $condition = [System.Windows.Automation.PropertyCondition]::new(\n        [System.Windows.Automation.AutomationElement]::ControlTypeProperty, $type\n    )\n    return $root.FindAll([System.Windows.Automation.TreeScope]::Children, $condition)\n}\n\nfunction Invoke-Element($element) {\n    try {\n        $pattern = $element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)\n        $pattern.Invoke()\n        return $true\n    } catch {\n        try {\n            $element.SetFocus()\n            [System.Windows.Forms.SendKeys]::SendWait(\'{ENTER}\')\n            return $true\n        } catch { return $false }\n    }\n}\n\ntry {\n    if (-not [IO.File]::Exists($VideoPath)) {\n        Write-Status \'error\' \'Il video non si trova in EXPORT.\'\n        exit 2\n    }\n\n    Write-Status \'starting\' \'Apro YouTube nel browser normale...\'\n    Start-Process \'https://www.youtube.com/upload\'\n\n    $fileButton = $null\n    $deadline = [DateTime]::UtcNow.AddSeconds(75)\n    $names = @(\'SELECT FILES\', \'Select files\', \'SELEZIONA FILE\', \'Seleziona file\')\n    while ([DateTime]::UtcNow -lt $deadline -and $null -eq $fileButton) {\n        foreach ($window in (Find-Windows)) {\n            $title = $window.Current.Name\n            if ($title -notmatch \'YouTube|Studio|Carica video|Upload videos\') { continue }\n            foreach ($name in $names) {\n                $condition = [System.Windows.Automation.PropertyCondition]::new(\n                    [System.Windows.Automation.AutomationElement]::NameProperty, $name\n                )\n                $fileButton = $window.FindFirst(\n                    [System.Windows.Automation.TreeScope]::Descendants, $condition\n                )\n                if ($null -ne $fileButton) { break }\n            }\n            if ($null -ne $fileButton) {\n                break\n            }\n        }\n        if ($null -eq $fileButton) { Start-Sleep -Milliseconds 350 }\n    }\n\n    if ($null -eq $fileButton) {\n        Write-Status \'error\' \'YouTube e aperto, ma non trovo Seleziona file. Il video resta in EXPORT.\'\n        exit 3\n    }\n    if (-not (Invoke-Element $fileButton)) {\n        Write-Status \'error\' \'Non riesco ad aprire la scelta del file. Il video resta in EXPORT.\'\n        exit 4\n    }\n\n    Write-Status \'uploading\' \'Inserisco il video nella finestra di Windows...\'\n    $dialog = $null\n    $deadline = [DateTime]::UtcNow.AddSeconds(25)\n    while ([DateTime]::UtcNow -lt $deadline -and $null -eq $dialog) {\n        $foreground = [GsfWin32]::GetForegroundWindow().ToInt64()\n        $candidate = $null\n        foreach ($window in (Find-Windows)) {\n            $name = $window.Current.Name\n            $class = $window.Current.ClassName\n            if ($class -eq \'#32770\' -and $name -match \'^(Open|Apri|Choose File|Seleziona file)\') {\n                if ($window.Current.NativeWindowHandle -eq $foreground) {\n                    $dialog = $window\n                    break\n                }\n                if ($null -eq $candidate) { $candidate = $window }\n            }\n        }\n        if ($null -eq $dialog) { $dialog = $candidate }\n        if ($null -eq $dialog) { Start-Sleep -Milliseconds 250 }\n    }\n    if ($null -eq $dialog) {\n        Write-Status \'error\' \'Non trovo la finestra Apri file. Il video resta in EXPORT.\'\n        exit 5\n    }\n\n    $editType = [System.Windows.Automation.ControlType]::Edit\n    $editCondition = [System.Windows.Automation.PropertyCondition]::new(\n        [System.Windows.Automation.AutomationElement]::ControlTypeProperty, $editType\n    )\n    $edits = $dialog.FindAll([System.Windows.Automation.TreeScope]::Descendants, $editCondition)\n    $fileEdit = $null\n    foreach ($edit in $edits) {\n        if ($edit.Current.AutomationId -eq \'1148\') { $fileEdit = $edit; break }\n    }\n    if ($null -eq $fileEdit) {\n        foreach ($edit in $edits) {\n            if ($edit.Current.Name -match \'File name|Nome file\') { $fileEdit = $edit; break }\n        }\n    }\n    if ($null -eq $fileEdit) {\n        Write-Status \'error\' \'Non trovo il campo Nome file. Il video resta in EXPORT.\'\n        exit 6\n    }\n\n    $value = $fileEdit.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)\n    $value.SetValue([IO.Path]::GetFullPath($VideoPath))\n    $fileEdit.SetFocus()\n    $dialogHandle = $dialog.Current.NativeWindowHandle\n    $openButton = $null\n    $buttonCondition = [System.Windows.Automation.PropertyCondition]::new(\n        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,\n        [System.Windows.Automation.ControlType]::Button\n    )\n    foreach ($button in $dialog.FindAll([System.Windows.Automation.TreeScope]::Descendants, $buttonCondition)) {\n        if ($button.Current.Name -match \'^(Open|Apri)(\\b|$)\') {\n            $openButton = $button\n            break\n        }\n    }\n    if ($null -ne $openButton) {\n        if (-not (Invoke-Element $openButton)) {\n            [System.Windows.Forms.SendKeys]::SendWait(\'{ENTER}\')\n        }\n    } else {\n        [System.Windows.Forms.SendKeys]::SendWait(\'{ENTER}\')\n    }\n    $deadline = [DateTime]::UtcNow.AddSeconds(12)\n    $dialogOpen = $true\n    while ([DateTime]::UtcNow -lt $deadline -and $dialogOpen) {\n        $dialogOpen = $false\n        foreach ($window in (Find-Windows)) {\n            if ($window.Current.NativeWindowHandle -eq $dialogHandle) {\n                $dialogOpen = $true\n                break\n            }\n        }\n        if ($dialogOpen) { Start-Sleep -Milliseconds 250 }\n    }\n    if ($dialogOpen) {\n        Write-Status \'error\' \'La scelta file e ancora aperta: controlla il percorso in EXPORT.\'\n        exit 7\n    }\n    Write-Status \'ready\' \'Video inviato a YouTube. Completa i dettagli nel browser.\'\n    exit 0\n} catch {\n    Write-Status \'error\' (\'YouTube non completato: \' + $_.Exception.Message)\n    exit 9\n}\n'

GSF_SOCIAL_UPLOAD_WORKER_V59 = 'import json\nimport os\nimport re\nimport sys\nimport time\nfrom pathlib import Path\n\n\nUPLOAD_URLS = {\n    "YouTube": "https://www.youtube.com/upload",\n    "TikTok": "https://www.tiktok.com/tiktokstudio/upload",\n    "Instagram": "https://www.instagram.com/",\n}\n\n\ndef write_status(path, state, message=""):\n    try:\n        target = Path(path)\n        target.parent.mkdir(parents=True, exist_ok=True)\n        temp = Path(str(target) + ".tmp")\n        temp.write_text(json.dumps({\n            "state": state,\n            "message": message,\n            "updated": time.time(),\n        }, ensure_ascii=False), encoding="utf-8")\n        os.replace(temp, target)\n    except Exception:\n        pass\n\n\ndef click_any(page, selectors):\n    for selector in selectors:\n        try:\n            item = page.locator(selector).first\n            if item.count() and item.is_visible():\n                item.click(timeout=1500)\n                return True\n        except Exception:\n            continue\n    return False\n\n\ndef find_file_input(page, platform):\n    if platform == "Instagram":\n        try:\n            dialog = page.locator(\'[role="dialog"]\').first\n            if not dialog.count() or not dialog.is_visible():\n                return None\n        except Exception:\n            return None\n    selectors = (\n        [\n            \'[role="dialog"] input[type="file"][accept*="video"]\',\n            \'[role="dialog"] input[type="file"]\',\n            \'input[type="file"][accept*="video"]\',\n        ]\n        if platform == "Instagram" else [\'input[type="file"]\']\n    )\n    for selector in selectors:\n        try:\n            item = page.locator(selector).first\n            if item.count():\n                return item\n        except Exception:\n            pass\n    return None\n\n\ndef instagram_click_role(page, role, expression):\n    """Only use named create controls, never a Post in the home feed."""\n    try:\n        item = page.get_by_role(role, name=re.compile(expression, re.I)).first\n        if item.count() and item.is_visible():\n            item.click(timeout=2000)\n            return True\n    except Exception:\n        pass\n    return False\n\n\ndef instagram_open_create(page):\n    if instagram_click_role(page, "link", r"^(Crea|Create)$"):\n        return True\n    if instagram_click_role(page, "button", r"^(Crea|Create)$"):\n        return True\n    return click_any(page, [\n        \'a[aria-label="Crea"]\', \'a[aria-label="Create"]\',\n        \'a[href="/create/select/"]\',\n        \'[role="button"][aria-label="Crea"]\',\n        \'[role="button"][aria-label="Create"]\',\n    ])\n\n\ndef instagram_choose_post_type(page):\n    return instagram_click_role(\n        page, "menuitem", r"^(Post|Reel|Pubblica un post|Create post)$"\n    )\n\n\ndef instagram_file_chooser(page):\n    """Some Instagram layouts create the file input only on button click."""\n    try:\n        dialog = page.locator(\'[role="dialog"]\').first\n        if not dialog.count() or not dialog.is_visible():\n            return None\n        button = dialog.get_by_role(\n            "button",\n            name=re.compile(r"^(Seleziona dal computer|Select from computer|Select files)$", re.I),\n        ).first\n        if not button.count() or not button.is_visible():\n            return None\n        with page.expect_file_chooser(timeout=5000) as selected:\n            button.click(timeout=2000)\n        return selected.value\n    except Exception:\n        return None\n\n\ndef open_upload_flow(page, platform, status_path):\n    url = UPLOAD_URLS[platform]\n    try:\n        page.goto(url, wait_until="domcontentloaded", timeout=90000)\n    except Exception:\n        if platform == "TikTok":\n            page.goto("https://www.tiktok.com/upload", wait_until="domcontentloaded", timeout=90000)\n        elif platform == "YouTube":\n            page.goto("https://studio.youtube.com/", wait_until="domcontentloaded", timeout=90000)\n        else:\n            return None\n\n    write_status(status_path, "waiting_login", "Se richiesto, accedi nel browser aperto.")\n    deadline = time.time() + 600\n    last_navigation = 0\n    instagram_create_clicked = False\n    instagram_active_since = None\n    while time.time() < deadline:\n        try:\n            current = page.url or ""\n            if platform == "YouTube" and "youtube.com" in current:\n                item = find_file_input(page, platform)\n                if item is not None:\n                    return item\n                if time.time() - last_navigation > 8:\n                    click_any(page, [\n                        \'ytcp-button#create-icon\',\n                        \'[aria-label*="Crea"]\', \'[aria-label*="Create"]\',\n                    ])\n                    click_any(page, [\n                        \'[test-id="upload-beta"]\',\n                        \'text="Carica video"\', \'text="Upload videos"\',\n                    ])\n                    last_navigation = time.time()\n\n            elif platform == "TikTok" and "tiktok.com" in current:\n                item = find_file_input(page, platform)\n                if item is not None:\n                    return item\n                if time.time() - last_navigation > 10:\n                    click_any(page, [\'text="Upload"\', \'text="Carica"\'])\n                    last_navigation = time.time()\n\n            elif platform == "Instagram" and "instagram.com" in current:\n                if "/accounts/login" in current:\n                    write_status(status_path, "waiting_login", "Accedi a Instagram nella finestra aperta.")\n                    page.wait_for_timeout(1000)\n                    continue\n                if instagram_active_since is None:\n                    instagram_active_since = time.time()\n                if not instagram_create_clicked:\n                    write_status(status_path, "opening", "Instagram: apro il menu Crea...")\n                    instagram_create_clicked = instagram_open_create(page)\n                if instagram_create_clicked:\n                    instagram_choose_post_type(page)\n                    item = find_file_input(page, platform)\n                    if item is not None:\n                        return item\n                    chooser = instagram_file_chooser(page)\n                    if chooser is not None:\n                        return chooser\n                if time.time() - instagram_active_since > 50:\n                    return None\n\n            page.wait_for_timeout(1000)\n        except Exception:\n            time.sleep(1)\n    return None\n\n\ndef main(job_path):\n    job = json.loads(Path(job_path).read_text(encoding="utf-8"))\n    platform = job["platform"]\n    status_path = job["status_path"]\n    video_path = job["video_path"]\n    if platform not in UPLOAD_URLS or not os.path.isfile(video_path):\n        write_status(status_path, "error", "Video o destinazione non disponibile.")\n        return 2\n\n    write_status(status_path, "starting", "Apro " + platform + "...")\n    try:\n        from playwright.sync_api import sync_playwright\n    except Exception:\n        write_status(status_path, "error", "Impossibile preparare il browser.")\n        return 3\n\n    try:\n        with sync_playwright() as playwright:\n            context = None\n            for channel in ("chrome", "msedge"):\n                try:\n                    context = playwright.chromium.launch_persistent_context(\n                        job["profile_dir"], channel=channel,\n                        headless=False, no_viewport=True,\n                        args=["--start-maximized"],\n                    )\n                    break\n                except Exception:\n                    continue\n            if context is None:\n                message = (\n                    "Chiudi la vecchia finestra Instagram aperta dall\'app e riprova."\n                    if platform == "Instagram" else "Chrome o Edge non si apre."\n                )\n                write_status(status_path, "error", message)\n                return 4\n\n            page = context.pages[0] if context.pages else context.new_page()\n            file_input = open_upload_flow(page, platform, status_path)\n            if file_input is None:\n                if platform == "Instagram":\n                    write_status(status_path, "error",\n                                 "Instagram: non trovo il menu Crea o la scelta del video. "\n                                 "Pagina attuale: " + str(page.url)[:150])\n                else:\n                    write_status(status_path, "error", "Non trovo il caricamento: seleziona il video manualmente.")\n                if platform == "Instagram":\n                    # A failed persistent browser must release its profile so\n                    # the next click can retry without a Chrome profile lock.\n                    context.close()\n                    return 5\n            else:\n                if hasattr(file_input, "set_input_files"):\n                    file_input.set_input_files(video_path)\n                else:\n                    file_input.set_files(video_path)\n                if platform == "Instagram":\n                    write_status(status_path, "selected",\n                                 "Video inserito su Instagram. Attendi l\'elaborazione e completa lì.")\n                else:\n                    write_status(status_path, "ready",\n                                 "Video selezionato su " + platform + ". Completa e pubblica lì.")\n\n            # Il browser rimane aperto per tutte le scelte finali dell\'utente.\n            while context.pages:\n                try:\n                    page.wait_for_timeout(1000)\n                except Exception:\n                    break\n        return 0\n    except Exception as error:\n        write_status(status_path, "error", "Caricamento interrotto: " + str(error)[-350:])\n        return 9\n\n\nif __name__ == "__main__":\n    raise SystemExit(main(sys.argv[1]))\n'


def _gsf_playwright_available():
    try:
        return importlib.util.find_spec("playwright") is not None
    except Exception:
        return False


def _gsf_ensure_social_browser():
    if _gsf_playwright_available():
        return True, ""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "playwright"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=240,
        )
        if result.returncode == 0:
            return True, ""
        return False, (result.stderr or result.stdout or "Installazione non riuscita.")[-1000:]
    except Exception as error:
        return False, str(error)


def _gsf_social_worker_paths(platform):
    platform_slug = {"YouTube": "youtube", "TikTok": "tiktok", "Instagram": "instagram"}[platform]
    base = GSF_SESSION_SOCIAL_DIR / "social_upload"
    base.mkdir(parents=True, exist_ok=True)
    return {
        "base": base,
        "worker": base / "social_upload_worker_v59.py",
        "profile": base / (platform_slug + "_profile"),
        "status": base / (platform_slug + "_status.json"),
    }


def _gsf_read_social_status(platform):
    try:
        data = json.loads(
            _gsf_social_worker_paths(platform)["status"].read_text(encoding="utf-8")
        )
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _gsf_launch_social_upload(platform, video_path):
    if platform not in ("YouTube", "TikTok", "Instagram"):
        return False, "Social non riconosciuto."
    if not os.path.isfile(video_path):
        return False, "Video non trovato."
    paths = _gsf_social_worker_paths(platform)
    try:
        paths["worker"].write_text(GSF_SOCIAL_UPLOAD_WORKER_V59, encoding="utf-8")
        job_id = hashlib.sha256(
            (video_path + platform + str(time.time())).encode("utf-8")
        ).hexdigest()[:12]
        job_path = paths["base"] / ("job_" + job_id + ".json")
        job_path.write_text(json.dumps({
            "platform": platform,
            "video_path": video_path,
            "status_path": str(paths["status"]),
            "profile_dir": str(paths["profile"]),
        }, ensure_ascii=False), encoding="utf-8")
        paths["status"].write_text(json.dumps({
            "state": "starting",
            "message": "Apro " + platform + "...",
            "updated": time.time(),
        }, ensure_ascii=False), encoding="utf-8")
        kwargs = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
            "close_fds": True,
        }
        if os.name == "nt":
            kwargs["creationflags"] = (
                getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                | getattr(subprocess, "DETACHED_PROCESS", 0)
            )
        subprocess.Popen([sys.executable, str(paths["worker"]), str(job_path)], **kwargs)
        return True, "Apro " + platform + "."
    except Exception as error:
        try:
            paths["status"].write_text(json.dumps({
                "state": "error", "message": "Non riesco ad aprire " + platform + ".",
                "updated": time.time(),
            }, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        return False, str(error)[-500:]


def _gsf_launch_youtube_desktop(video_path):
    """Open normal Windows browser and use its native file chooser."""
    if os.name != "nt":
        return False, "Questa automazione YouTube richiede Windows."
    if not os.path.isfile(video_path):
        return False, "Video non trovato."
    paths = _gsf_social_worker_paths("YouTube")
    script_path = paths["base"] / "youtube_windows_worker_v60.ps1"
    try:
        script_path.write_text(GSF_YOUTUBE_WINDOWS_WORKER_V60, encoding="utf-8-sig")
        paths["status"].write_text(json.dumps({
            "state": "starting",
            "message": "Apro YouTube nel browser normale...",
            "updated": time.time(),
        }, ensure_ascii=False), encoding="utf-8")
        subprocess.Popen(
            [
                "powershell.exe", "-NoProfile", "-STA", "-WindowStyle", "Hidden",
                "-ExecutionPolicy", "Bypass", "-File", str(script_path),
                "-VideoPath", str(video_path),
                "-StatusPath", str(paths["status"]),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return True, "Apro YouTube nel browser normale."
    except Exception as error:
        return False, "Non riesco ad aprire YouTube: " + str(error)[-400:]


def _gsf_write_social_status(platform, state, message, **extra):
    try:
        path = _gsf_social_worker_paths(platform)["status"]
        payload = {
            "state": str(state),
            "message": str(message),
            "updated": time.time(),
        }
        payload.update(extra)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _gsf_publish_social_upload(video, platform):
    """V77: publishing is server-side and API-only; no desktop/browser automation."""
    if platform not in ("YouTube", "TikTok", "Instagram"):
        return False, "Social non riconosciuto.", ""
    if not isinstance(video, (bytes, bytearray)) or len(video) <= 1024:
        return False, "Short finale non disponibile.", ""

    exported, error = _gsf_export_final_video(
        video, platform=platform, title="GamingShort"
    )
    if error:
        return False, error, ""

    connected, connection_error = _gsf_social_connection_status(platform)
    if not connected:
        _gsf_write_social_status(platform, "error", connection_error or (platform + " non collegato"))
        return False, connection_error or (platform + " non collegato"), exported

    platform_name = {
        "YouTube": "YouTube Shorts",
        "TikTok": "TikTok",
        "Instagram": "Instagram Reels",
    }[platform]
    recipe = st.session_state.get("gsf_final_recipe", {}) or {}
    start = float(recipe.get("start", 0.0) or 0.0)
    game = st.session_state.get("gioco", "Gaming")
    tone = st.session_state.get("tono_social", "Gaming forte")
    pack = _gsf_finalize_publish_pack(
        _gsf_build_publish_pack(start, platform=platform_name, game=game, tone=tone)
    )

    try:
        _gsf_write_social_status(platform, "uploading", "Carico il video tramite API ufficiale...")
        if platform == "YouTube":
            prefs = _gsf_social_preferences()
            result = _gsf_youtube_upload(
                bytes(video),
                pack,
                privacy_status=str(prefs.get("youtube_privacy", "private") or "private"),
                made_for_kids=bool(prefs.get("youtube_made_for_kids", False)),
            )
            if not result.get("ok"):
                message = str(result.get("error", "Upload YouTube non riuscito"))
                _gsf_write_social_status(platform, "error", message)
                return False, message, exported
            message = "Video caricato su YouTube."
            _gsf_write_social_status(platform, "ready", message, url=result.get("url", ""))
            return True, message, exported

        if platform == "TikTok":
            result = _gsf_tiktok_upload_draft(bytes(video))
            if not result.get("ok"):
                message = str(result.get("error", "Upload TikTok non riuscito"))
                _gsf_write_social_status(platform, "error", message)
                return False, message, exported
            message = "Video inviato a TikTok. Completa il post dalla notifica/bozza TikTok."
            _gsf_write_social_status(platform, "ready", message, publish_id=result.get("publish_id", ""))
            return True, message, exported

        result = _gsf_instagram_publish_reel_auto(bytes(video), pack)
        if not result.get("ok"):
            message = str(result.get("error", "Pubblicazione Instagram non riuscita"))
            _gsf_write_social_status(platform, "error", message)
            return False, message, exported
        message = "Reel pubblicato su Instagram."
        _gsf_write_social_status(platform, "ready", message, url=result.get("permalink", ""))
        return True, message, exported

    except Exception as exc:
        message = str(exc)
        _gsf_write_social_status(platform, "error", message)
        return False, message, exported


def _gsf_social_progress_panel():
    platform = st.session_state.get("social_selected_v59")
    if platform not in ("YouTube", "TikTok", "Instagram"):
        return
    status = _gsf_read_social_status(platform)
    state = status.get("state", "")
    if not state or time.time() - float(status.get("updated", 0) or 0) > 3600:
        return
    progress = {"starting": 20, "waiting_login": 40, "uploading": 80,
                "selected": 80, "ready": 100, "error": 0}
    st.progress(progress.get(state, 20))
    if state == "ready":
        st.success("✅ Video pronto su " + platform + ". Completa la pubblicazione lì.")
    elif state == "error":
        st.warning(str(status.get("message", "Caricamento non completato.")))
        path = st.session_state.get("social_export_v59", "")
        if path and os.path.isfile(path):
            st.caption("Video salvato in EXPORT: " + path)
    else:
        st.caption(str(status.get("message", "Apro " + platform + "...")))


if callable(getattr(st, "fragment", None)):
    _gsf_social_progress_panel = st.fragment(run_every="2s")(
        _gsf_social_progress_panel
    )


def _gsf_safe_export_name(value, fallback="GamingShort"):
    """Windows-safe compact filename stem."""
    value=str(value or "").strip()
    value=re.sub(r'[<>:"/\\|?*\x00-\x1f]+'," ",value)
    value=re.sub(r"\s+"," ",value).strip(" .")
    if not value:
        value=fallback
    return value[:64].rstrip(" .") or fallback


def _gsf_export_final_video(video_bytes, platform="Social", title=""):
    """
    Save the final master to the anonymous session export area on the server.
    Same bytes/platform reuse the same file instead of making duplicates.
    """
    if not isinstance(video_bytes,(bytes,bytearray)) or len(video_bytes)<=1024:
        return "", "Short finale non disponibile."

    export_dir=GSF_SESSION_EXPORT_DIR
    try:
        export_dir.mkdir(parents=True,exist_ok=True)
        _gsf_touch_session()
    except Exception as e:
        return "", f"Non riesco a creare l'area export temporanea: {e}"

    digest=hashlib.sha256(bytes(video_bytes)).hexdigest()[:10]
    title_safe=_gsf_safe_export_name(title,"GamingShort").replace(" ","_")
    filename=f"{title_safe}_{digest}.mp4"
    path=export_dir/filename

    try:
        if (not path.exists()) or path.stat().st_size!=len(video_bytes):
            tmp=Path(str(path)+".tmp")
            tmp.write_bytes(bytes(video_bytes))
            os.replace(tmp,path)
        return str(path),""
    except Exception as e:
        return "", f"Non riesco a salvare lo Short: {e}"


def _gsf_reveal_export_file(path):
    """Open the local file manager with the exported MP4 selected when possible."""
    path=str(path or "").strip()
    if not path or not os.path.exists(path):
        return False

    try:
        if os.name=="nt":
            # explorer.exe accepts /select,<absolute path>
            subprocess.Popen(
                ["explorer.exe",f"/select,{os.path.normpath(path)}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True

        if sys.platform=="darwin":
            subprocess.Popen(
                ["open","-R",path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True

        subprocess.Popen(
            ["xdg-open",str(Path(path).parent)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception:
        return False


def _gsf_copy_to_clipboard(value):
    """Copy text to the desktop clipboard without extra dependencies on Windows."""
    value=str(value or "")
    try:
        if os.name=="nt":
            proc=subprocess.run(
                ["clip"],
                input=value,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=5
            )
            return proc.returncode==0
    except Exception:
        pass

    # Cross-platform fallback for development environments.
    try:
        import tkinter as tk
        root=tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(value)
        root.update()
        root.destroy()
        return True
    except Exception:
        return False


def _gsf_open_social_and_reveal_video(url, video_path):
    """
    Open the official upload page in the default browser and reveal the
    already-exported MP4 locally. No API/OAuth integration is used.
    """
    browser_ok=False
    try:
        browser_ok=bool(webbrowser.open(str(url),new=2))
    except Exception:
        browser_ok=False

    # Small delay helps Windows create the browser tab before Explorer opens.
    try:
        time.sleep(.25)
    except Exception:
        pass

    reveal_ok=_gsf_reveal_export_file(video_path)
    return browser_ok,reveal_ok



def _gsf_clean_game_name(value):
    value=str(value or "").strip()
    return value if value else "Gaming"


def _gsf_publish_event_label(diag):
    diag=diag or {}
    f=diag.get("features") or {}
    event_type=str(f.get("event_type","") or "")
    event_score=float(f.get("event_score",0.0))
    category=str(f.get("moment_category","") or "")

    if event_score>=0.56:
        return {
            "goal":"gol",
            "shooter_elimination":"eliminazione",
            "victory":"vittoria",
            "sports_big_chance":"grande occasione",
            "racing":"momento gara",
            "achievement":"traguardo",
            "impact_event":"momento forte",
        }.get(event_type,"momento forte")

    return {
        "reaction":"reazione",
        "action":"azione",
        "story":"momento",
    }.get(category,"momento")


def _gsf_publish_transcript_excerpt(diag,max_words=10):
    transcript=str((diag or {}).get("transcript","") or "").strip()
    if not transcript:
        return ""
    words=transcript.split()
    excerpt=" ".join(words[:max_words]).strip()
    if len(words)>max_words:
        excerpt+="…"
    return excerpt


def _gsf_hashtag_token(value):
    value=re.sub(r"[^A-Za-z0-9À-ÿ]+","",str(value or ""))
    return value[:32]


def _gsf_publish_hashtags(game,event_label,platform):
    tags=[]
    game_tag=_gsf_hashtag_token(game)
    if game_tag:
        tags.append(f"#{game_tag}")

    event_tag=_gsf_hashtag_token(event_label)
    if event_tag:
        tags.append(f"#{event_tag}")

    if str(platform)=="TikTok":
        tags += ["#gaming","#gamingclips","#fyp"]
    else:
        tags += ["#gaming","#shorts","#gamingShorts"]

    seen=[]
    for tag in tags:
        low=tag.lower()
        if low not in [x.lower() for x in seen]:
            seen.append(tag)
    return seen[:6]


def _gsf_slug_filename(text,max_len=55):
    text=str(text or "").strip().lower()
    text=re.sub(r"[^\w\s-]","",text,flags=re.UNICODE)
    text=re.sub(r"[\s_-]+","-",text).strip("-")
    if not text:
        text="gaming-short"
    return text[:max_len].rstrip("-")+".mp4"


def _gsf_publish_tone_profile(tone):
    tone=str(tone or "Gaming forte")
    return {
        "Gaming forte":{
            "suffixes":["🔥","😱","👀"],
            "cta_youtube":"Tu l'avresti giocata così?",
            "cta_tiktok":"Tu che avresti fatto?",
            "cta_instagram":"Che voto dai a questa giocata?",
        },
        "Pulito":{
            "suffixes":["","🎮","✨"],
            "cta_youtube":"Che ne pensi?",
            "cta_tiktok":"Che ne pensi?",
            "cta_instagram":"Che ne pensi?",
        },
        "Ironico":{
            "suffixes":["😂","💀","🙃"],
            "cta_youtube":"Direi tutto calcolato 😂",
            "cta_tiktok":"Tutto calcolato, ovviamente 😂",
            "cta_instagram":"Tutto calcolato... più o meno 😂",
        },
    }.get(tone,{
        "suffixes":["🔥","👀","🎮"],
        "cta_youtube":"Che ne pensi?",
        "cta_tiktok":"Tu che avresti fatto?",
        "cta_instagram":"Che ne pensi?",
    })


def _gsf_publish_event_score(diag):
    f=(diag or {}).get("features") or {}
    return float(f.get("event_score",0.0))


def _gsf_publish_short_score(diag):
    f=(diag or {}).get("features") or {}
    return float(f.get("short_worthiness",0.0))


def _gsf_publish_title_seeds(game,event_label,confident=True):
    game=_gsf_clean_game_name(game)

    if confident:
        mapping={
            "gol":[
                f"Che gol su {game}!",
                f"Questo gol su {game} non me l'aspettavo",
                f"GOOOL su {game}!",
            ],
            "eliminazione":[
                f"Che eliminazione su {game}!",
                f"Questa eliminazione su {game} è assurda",
                f"Uno dei momenti migliori su {game}",
            ],
            "vittoria":[
                f"Vittoria su {game}!",
                f"È finita così su {game}",
                f"Che finale su {game}!",
            ],
            "grande occasione":[
                f"Che occasione su {game}!",
                f"Per un attimo ci ho creduto su {game}",
                f"Occasione enorme su {game}",
            ],
            "momento gara":[
                f"Momento assurdo su {game}!",
                f"Qui è cambiata la gara su {game}",
                f"Che momento su {game}!",
            ],
            "traguardo":[
                f"Nuovo traguardo su {game}!",
                f"Finalmente su {game}!",
                f"Questo traguardo su {game} vale tutto",
            ],
            "reazione":[
                f"Questa reazione su {game}",
                f"Non ero pronto a questo su {game}",
                f"La mia reazione dice tutto su {game}",
            ],
            "azione":[
                f"Questa azione su {game}",
                f"Qui succede tutto su {game}",
                f"Momento puro caos su {game}",
            ],
        }
        if event_label in mapping:
            return mapping[event_label]

    return [
        f"Questo momento su {game}",
        f"Guarda cosa succede su {game}",
        f"Uno di quei momenti su {game}",
    ]


def _gsf_publish_limit(text,limit):
    text=" ".join(str(text or "").split()).strip()
    if len(text)<=int(limit):
        return text
    clipped=text[:max(1,int(limit)-1)].rstrip(" ,.!?-")
    return clipped+"…"


def _gsf_publish_platform_preset(platform):
    """
    Product presets, not claims about official platform limits.
    Conservative copy lengths chosen for readability.
    """
    if str(platform)=="TikTok":
        return {
            "title_limit":64,
            "caption_excerpt_words":14,
            "hashtag_limit":5,
            "cta_key":"cta_tiktok",
            "style":"fast",
        }
    if str(platform)=="Instagram Reels":
        return {
            "title_limit":70,
            "caption_excerpt_words":16,
            "hashtag_limit":8,
            "cta_key":"cta_instagram",
            "style":"reels",
        }
    return {
        "title_limit":70,
        "caption_excerpt_words":18,
        "hashtag_limit":6,
        "cta_key":"cta_youtube",
        "style":"searchable",
    }


def _gsf_publish_hashtags_v46(game,event_label,platform,limit=None):
    preset=_gsf_publish_platform_preset(platform)
    limit=int(limit or preset["hashtag_limit"])

    tags=[]
    game_tag=_gsf_hashtag_token(game)
    if game_tag:
        tags.append(f"#{game_tag}")

    event_map={
        "gol":"#goal",
        "eliminazione":"#gamingclips",
        "vittoria":"#win",
        "grande occasione":"#gamingmoment",
        "momento gara":"#racing",
        "traguardo":"#achievement",
        "reazione":"#reaction",
        "azione":"#gameplay",
        "momento":"#gaming",
        "momento forte":"#gaming",
    }
    if event_label in event_map:
        tags.append(event_map[event_label])

    if str(platform)=="TikTok":
        tags += ["#gaming","#gamingclips","#fyp","#videogames"]
    elif str(platform)=="Instagram Reels":
        tags += ["#gaming","#reels","#gamingreels","#videogames","#gameplay"]
    else:
        tags += ["#gaming","#shorts","#gamingShorts","#gameplay"]

    unique=[]
    seen=set()
    for tag in tags:
        low=tag.lower()
        if low not in seen:
            seen.add(low)
            unique.append(tag)
    return unique[:limit]


def _gsf_build_publish_pack(start,platform="YouTube Shorts",game="",tone="Gaming forte"):
    """
    V46 Publishing Pack.

    Uses only signals we already have:
    detected event/category, event confidence, Short-worthiness,
    transcript excerpt and selected game/tone.
    """
    game=_gsf_clean_game_name(game)
    platform=str(platform or "YouTube Shorts")
    tone=str(tone or "Gaming forte")
    diag=_gsf_diag_for_start(start)

    event_label=_gsf_publish_event_label(diag)
    event_score=_gsf_publish_event_score(diag)
    short_score=_gsf_publish_short_score(diag)
    confident=(event_score>=0.56)
    preset=_gsf_publish_platform_preset(platform)
    tone_profile=_gsf_publish_tone_profile(tone)

    # The excerpt is re-cut using the platform preset.
    transcript=str((diag or {}).get("transcript","") or "").strip()
    transcript_words=transcript.split()
    excerpt=""
    if transcript_words:
        n=int(preset["caption_excerpt_words"])
        excerpt=" ".join(transcript_words[:n])
        if len(transcript_words)>n:
            excerpt+="…"

    seeds=_gsf_publish_title_seeds(
        game,event_label,confident=confident
    )
    suffixes=tone_profile["suffixes"]

    title_variants=[]
    for i,seed in enumerate(seeds[:3]):
        suffix=suffixes[i] if i<len(suffixes) else ""
        title=_gsf_publish_limit(
            (seed+" "+suffix).strip(),
            preset["title_limit"]
        )
        if title not in title_variants:
            title_variants.append(title)

    while len(title_variants)<3:
        title_variants.append(
            _gsf_publish_limit(
                f"{game} gaming moment {len(title_variants)+1}",
                preset["title_limit"]
            )
        )

    hashtags=_gsf_publish_hashtags_v46(
        game,event_label,platform,preset["hashtag_limit"]
    )
    tags_text=" ".join(hashtags)

    cta=tone_profile[preset["cta_key"]]
    hook=_gsf_auto_hook_for_start(start)

    if platform=="TikTok":
        opening=title_variants[0]
        caption_a=opening
        if excerpt:
            caption_a+=f"\n{excerpt}"
        caption_a+=f"\n\n{cta}\n{tags_text}"

        caption_b=(
            (hook if hook else title_variants[1])
            +f"\n\n{cta}\n{tags_text}"
        )
    elif platform=="Instagram Reels":
        caption_a=title_variants[0]
        if excerpt:
            caption_a+=f"\n\n{excerpt}"
        caption_a+=f"\n\n{cta}\n\n{tags_text}"

        caption_b=(
            (hook if hook else title_variants[1])
            +f"\n\n{cta}\n\n{tags_text}"
        )
    else:
        caption_a=title_variants[0]
        if excerpt:
            caption_a+=f"\n\n{excerpt}"
        caption_a+=f"\n\n{cta}\n\n{tags_text}"

        caption_b=title_variants[1]
        if hook:
            caption_b+=f"\n\n{hook}"
        caption_b+=f"\n\n{tags_text}"

    caption_variants=[caption_a.strip(),caption_b.strip()]
    filename=_gsf_slug_filename(
        f"{game}-{event_label}-{round(float(start))}s"
    )

    confidence_label=(
        "alta" if event_score>=0.75
        else "media" if event_score>=0.56
        else "generica"
    )

    return {
        "start":round(float(start),3),
        "platform":platform,
        "game":game,
        "tone":tone,
        "event_label":event_label,
        "event_score":round(event_score,3),
        "short_score":round(short_score,3),
        "confidence":confidence_label,
        "title":title_variants[0],
        "title_variants":title_variants,
        "caption":caption_variants[0],
        "caption_variants":caption_variants,
        "hashtags":hashtags,
        "filename":filename,
        "hook":hook,
        "excerpt":excerpt,
        "preset":preset,
    }



def _gsf_finalize_publish_pack(
    pack,
    selected_title=None,
    selected_caption=None,
    title_index=0,
    caption_index=0
):
    """
    V47 single source of truth.
    The selected title/caption drive every downstream artifact.
    """
    final=dict(pack or {})
    titles=list(final.get("title_variants",[]) or [])
    captions=list(final.get("caption_variants",[]) or [])

    title_index=max(0,min(int(title_index),max(0,len(titles)-1)))
    caption_index=max(0,min(int(caption_index),max(0,len(captions)-1)))

    title=str(
        selected_title
        if selected_title is not None
        else (titles[title_index] if titles else final.get("title",""))
    ).strip()
    caption=str(
        selected_caption
        if selected_caption is not None
        else (captions[caption_index] if captions else final.get("caption",""))
    ).strip()

    start=float(final.get("start",0.0) or 0.0)
    filename=_gsf_slug_filename(
        f"{title}-{round(start)}s"
    )

    final.update({
        "selected_title":title,
        "selected_caption":caption,
        "selected_title_index":title_index,
        "selected_caption_index":caption_index,
        "selected_filename":filename,
        # Compatibility: from here on title/caption/filename ARE the selection.
        "title":title,
        "caption":caption,
        "filename":filename,
    })

    signature_payload={
        "platform":final.get("platform",""),
        "game":final.get("game",""),
        "start":round(start,3),
        "title":title,
        "caption":caption,
        "hashtags":final.get("hashtags",[]),
        "filename":filename,
    }
    final["publishing_signature"]=hashlib.sha256(
        json.dumps(
            signature_payload,
            sort_keys=True,
            ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()[:16]

    return final





GSF_SOCIAL_DIR = GSF_SESSION_SOCIAL_DIR
GSF_TIKTOK_TOKEN = GSF_SOCIAL_DIR / "tiktok_token.json"
GSF_TIKTOK_CONFIG = GSF_SOCIAL_DIR / "tiktok_config.json"
GSF_INSTAGRAM_CONFIG = GSF_SOCIAL_DIR / "instagram_config.json"
try:
    _gsf_app_dir = Path(__file__).resolve().parent
except Exception:
    _gsf_app_dir = Path.cwd()
GSF_GLOBAL_CONFIG_DIR = Path(
    os.environ.get("GSF_CONFIG_DIR", str(_gsf_app_dir / ".gsf_config"))
).expanduser().resolve()
GSF_APP_CREDENTIALS = GSF_GLOBAL_CONFIG_DIR / "app_credentials.json"
GSF_SOCIAL_PREFS = GSF_SOCIAL_DIR / "social_preferences.json"

GSF_TIKTOK_AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
GSF_TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
GSF_TIKTOK_REVOKE_URL = "https://open.tiktokapis.com/v2/oauth/revoke/"
GSF_TIKTOK_UPLOAD_INIT = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
GSF_TIKTOK_STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
GSF_TIKTOK_SCOPES = "user.info.basic,video.upload"


def _gsf_secure_write_json(path,payload):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=Path(str(path)+".tmp")
    tmp.write_text(
        json.dumps(payload,ensure_ascii=False,indent=2),
        encoding="utf-8"
    )
    os.replace(tmp,path)
    try:
        os.chmod(path,0o600)
    except Exception:
        pass


def _gsf_read_json_file(path):
    try:
        path=Path(path)
        if not path.exists():
            return {}
        data=json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data,dict) else {}
    except Exception:
        return {}


def _gsf_app_credentials():
    """
    Developer/application credentials live outside the UI.
    End users never type Client IDs, secrets, tokens or JSON files.
    The packaged app may ship a private app_credentials.json beside the
    executable/script; local overrides live in ~/.gaming_shorts_factory.
    """
    cfg={}
    try:
        _app_dir=Path(__file__).resolve().parent
    except Exception:
        _app_dir=Path.cwd()

    for _cfg_path in (
        _app_dir/"app_credentials.json",
        GSF_APP_CREDENTIALS,
    ):
        _part=_gsf_read_json_file(_cfg_path)
        if isinstance(_part,dict):
            cfg.update(_part)

    env_map={
        "youtube_client_secret_file":"GSF_YOUTUBE_CLIENT_SECRET_FILE",
        "youtube_client_secret_json":"GSF_YOUTUBE_CLIENT_SECRET_JSON",
        "tiktok_client_key":"GSF_TIKTOK_CLIENT_KEY",
        "tiktok_client_secret":"GSF_TIKTOK_CLIENT_SECRET",
        "instagram_user_id":"GSF_INSTAGRAM_USER_ID",
        "instagram_access_token":"GSF_INSTAGRAM_ACCESS_TOKEN",
        "cloudflared_path":"GSF_CLOUDFLARED",
        "public_app_url":"GSF_PUBLIC_APP_URL",
    }
    for key,env_name in env_map.items():
        value=os.environ.get(env_name)
        if value:
            cfg[key]=value

    if not str(cfg.get("youtube_client_secret_file","") or "").strip():
        for _candidate in (
            _app_dir/"youtube_client_secret.json",
            _app_dir/"client_secret.json",
            GSF_SOCIAL_DIR/"youtube_client_secret.json",
        ):
            if _candidate.exists():
                cfg["youtube_client_secret_file"]=str(_candidate)
                break

    return cfg


def _gsf_social_preferences():
    prefs=_gsf_read_json_file(GSF_SOCIAL_PREFS)
    if not isinstance(prefs,dict):
        prefs={}
    prefs.setdefault("youtube_privacy","private")
    prefs.setdefault("youtube_made_for_kids",False)
    return prefs


def _gsf_save_social_preferences(**changes):
    prefs=_gsf_social_preferences()
    prefs.update(changes)
    _gsf_secure_write_json(GSF_SOCIAL_PREFS,prefs)
    return prefs


def _gsf_hidden_app_setup(platform):
    """
    Returns whether the packaged app has what it needs to start account login.
    This is intentionally separate from user account connection state.
    """
    cfg=_gsf_app_credentials()
    platform=str(platform or "").lower()

    if platform=="youtube":
        if str(cfg.get("youtube_client_secret_json","") or "").strip():
            return True
        path=str(cfg.get("youtube_client_secret_file","") or "").strip()
        return bool(path and os.path.exists(os.path.expanduser(path)))

    if platform=="tiktok":
        return bool(
            str(cfg.get("tiktok_client_key","") or "").strip()
            and str(cfg.get("tiktok_client_secret","") or "").strip()
        )

    if platform=="instagram":
        # V54 supports a pre-provisioned Meta connection without exposing
        # technical fields in the user interface. A hosted OAuth bridge can
        # later populate these same values without changing the UI.
        return bool(
            str(cfg.get("instagram_user_id","") or "").strip()
            and str(cfg.get("instagram_access_token","") or "").strip()
        )

    return False


def _gsf_connect_social_account(platform):
    """
    One-click connection entry point used by the UI.
    App credentials are hidden in developer configuration.
    """
    platform=str(platform or "")
    cfg=_gsf_app_credentials()

    if platform=="YouTube":
        path=os.path.expanduser(
            str(cfg.get("youtube_client_secret_file","") or "").strip()
        )
        if not path or not os.path.exists(path):
            return False,(
                "YouTube non è ancora configurato nell'app. "
                "Le credenziali applicazione vanno impostate una sola volta "
                "nella build, non dall'utente."
            )
        try:
            data=Path(path).read_bytes()
        except Exception as e:
            return False,str(e)
        return _gsf_youtube_connect(data)

    if platform=="TikTok":
        client_key=str(cfg.get("tiktok_client_key","") or "").strip()
        client_secret=str(cfg.get("tiktok_client_secret","") or "").strip()
        if not client_key or not client_secret:
            return False,(
                "TikTok non è ancora configurato nell'app. "
                "Client Key e Secret restano nella configurazione della build."
            )
        return _gsf_tiktok_connect(client_key,client_secret)

    if platform=="Instagram":
        user_id=str(cfg.get("instagram_user_id","") or "").strip()
        access_token=str(cfg.get("instagram_access_token","") or "").strip()
        if not user_id or not access_token:
            return False,(
                "Instagram non è ancora configurato nell'app. "
                "Il collegamento utente resta semplice; le credenziali Meta "
                "non vengono mostrate nella schermata."
            )
        return _gsf_instagram_connect(user_id,access_token)

    return False,"Piattaforma non riconosciuta"




def _gsf_http_json(
    url,
    method="GET",
    headers=None,
    json_body=None,
    form_body=None,
    timeout=45
):
    headers=dict(headers or {})
    data=None

    if json_body is not None:
        data=json.dumps(
            json_body,
            ensure_ascii=False
        ).encode("utf-8")
        headers.setdefault(
            "Content-Type",
            "application/json; charset=UTF-8"
        )
    elif form_body is not None:
        data=urlencode(form_body).encode("utf-8")
        headers.setdefault(
            "Content-Type",
            "application/x-www-form-urlencoded"
        )

    req=Request(
        str(url),
        data=data,
        headers=headers,
        method=str(method).upper()
    )

    try:
        with urlopen(req,timeout=timeout) as resp:
            raw=resp.read()
            status=int(getattr(resp,"status",200) or 200)
            try:
                payload=json.loads(raw.decode("utf-8","replace")) if raw else {}
            except Exception:
                payload={"raw":raw.decode("utf-8","replace")}
            return {
                "ok":200<=status<300,
                "status":status,
                "data":payload,
                "error":"",
            }
    except HTTPError as e:
        raw=e.read() if hasattr(e,"read") else b""
        try:
            payload=json.loads(raw.decode("utf-8","replace")) if raw else {}
        except Exception:
            payload={"raw":raw.decode("utf-8","replace")}
        return {
            "ok":False,
            "status":int(getattr(e,"code",0) or 0),
            "data":payload,
            "error":str(e),
        }
    except Exception as e:
        return {
            "ok":False,
            "status":0,
            "data":{},
            "error":str(e),
        }


# ============================================================
# TIKTOK — Desktop OAuth + Upload Draft
# ============================================================

def _gsf_tiktok_pkce():
    verifier=secrets.token_urlsafe(64)[:96]
    challenge=hashlib.sha256(
        verifier.encode("utf-8")
    ).hexdigest()
    return verifier,challenge


class _GSFTikTokCallbackHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args,**kwargs):
        return

    def do_GET(self):
        parsed=urlparse(self.path)
        if parsed.path.rstrip("/")!="/callback":
            self.send_response(404)
            self.end_headers()
            return

        query=parse_qs(parsed.query)
        self.server.oauth_query=query
        body=(
            "<html><body style='font-family:sans-serif;padding:40px'>"
            "<h2>TikTok collegato a Gaming Shorts Factory</h2>"
            "<p>Puoi chiudere questa scheda e tornare all'app.</p>"
            "</body></html>"
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _gsf_tiktok_save_token(token_data):
    payload=dict(token_data or {})
    payload["_saved_at"]=time.time()
    _gsf_secure_write_json(GSF_TIKTOK_TOKEN,payload)


def _gsf_tiktok_save_config(client_key,client_secret):
    _gsf_secure_write_json(
        GSF_TIKTOK_CONFIG,
        {
            "client_key":str(client_key or "").strip(),
            "client_secret":str(client_secret or "").strip(),
        }
    )


def _gsf_tiktok_refresh(token_data,config):
    refresh=str((token_data or {}).get("refresh_token","") or "")
    client_key=str((config or {}).get("client_key","") or "")
    client_secret=str((config or {}).get("client_secret","") or "")
    if not (refresh and client_key and client_secret):
        return None,"Configurazione TikTok incompleta"

    res=_gsf_http_json(
        GSF_TIKTOK_TOKEN_URL,
        method="POST",
        form_body={
            "client_key":client_key,
            "client_secret":client_secret,
            "grant_type":"refresh_token",
            "refresh_token":refresh,
        }
    )
    if not res.get("ok"):
        return None,str(res.get("data") or res.get("error"))

    data=res.get("data") or {}
    if not data.get("access_token"):
        return None,str(data)

    _gsf_tiktok_save_token(data)
    return data,""


def _gsf_tiktok_credentials():
    token=_gsf_read_json_file(GSF_TIKTOK_TOKEN)
    config=_gsf_read_json_file(GSF_TIKTOK_CONFIG)

    if not token or not config:
        return None,None,"TikTok non collegato"

    expires=int(token.get("expires_in",0) or 0)
    saved=float(token.get("_saved_at",0.0) or 0.0)
    needs_refresh=(
        not token.get("access_token")
        or not saved
        or (expires and time.time()>=saved+max(60,expires-300))
    )

    if needs_refresh:
        token,error=_gsf_tiktok_refresh(token,config)
        if token is None:
            return None,config,error

    scopes=str((token or {}).get("scope","") or "")
    if "video.upload" not in scopes:
        return None,config,"Manca lo scope TikTok video.upload"

    return token,config,""


def _gsf_tiktok_connection_status():
    token,config,error=_gsf_tiktok_credentials()
    return {
        "connected":bool(token and token.get("access_token")),
        "open_id":str((token or {}).get("open_id","") or ""),
        "scope":str((token or {}).get("scope","") or ""),
        "error":error,
    }


def _gsf_tiktok_connect(client_key,client_secret,timeout_seconds=180):
    client_key=str(client_key or "").strip()
    client_secret=str(client_secret or "").strip()
    if not client_key or not client_secret:
        return False,"Inserisci Client Key e Client Secret TikTok"

    verifier,challenge=_gsf_tiktok_pkce()
    state=secrets.token_urlsafe(32)

    server=ThreadingHTTPServer(
        ("127.0.0.1",0),
        _GSFTikTokCallbackHandler
    )
    server.timeout=1
    redirect_uri=(
        f"http://127.0.0.1:{server.server_address[1]}/callback/"
    )

    params={
        "client_key":client_key,
        "response_type":"code",
        "scope":GSF_TIKTOK_SCOPES,
        "redirect_uri":redirect_uri,
        "state":state,
        "code_challenge":challenge,
        "code_challenge_method":"S256",
    }
    auth_url=GSF_TIKTOK_AUTH_URL+"?"+urlencode(params)

    try:
        webbrowser.open(auth_url,new=1,autoraise=True)
    except Exception:
        pass

    deadline=time.time()+max(30,int(timeout_seconds))
    query=None
    try:
        while time.time()<deadline:
            server.handle_request()
            query=getattr(server,"oauth_query",None)
            if query:
                break
    finally:
        try:
            server.server_close()
        except Exception:
            pass

    if not query:
        return False,(
            "Timeout OAuth TikTok. Controlla che il Redirect URI desktop "
            "consenta 127.0.0.1 con porta wildcard."
        )

    returned_state=str((query.get("state") or [""])[0])
    if returned_state!=state:
        return False,"OAuth TikTok annullato: state non valido"

    error=str((query.get("error") or [""])[0])
    if error:
        desc=str((query.get("error_description") or [""])[0])
        return False,f"{error}: {desc}"

    code=str((query.get("code") or [""])[0])
    if not code:
        return False,"TikTok non ha restituito il codice OAuth"

    res=_gsf_http_json(
        GSF_TIKTOK_TOKEN_URL,
        method="POST",
        form_body={
            "client_key":client_key,
            "client_secret":client_secret,
            "code":code,
            "grant_type":"authorization_code",
            "redirect_uri":redirect_uri,
            "code_verifier":verifier,
        }
    )

    if not res.get("ok"):
        return False,str(res.get("data") or res.get("error"))

    token=res.get("data") or {}
    if not token.get("access_token"):
        return False,str(token)

    scope=str(token.get("scope","") or "")
    if "video.upload" not in scope:
        return False,(
            "Login riuscito ma TikTok non ha concesso video.upload. "
            "Lo scope deve essere approvato e autorizzato."
        )

    _gsf_tiktok_save_config(client_key,client_secret)
    _gsf_tiktok_save_token(token)
    return True,"TikTok collegato"


def _gsf_tiktok_disconnect():
    token=_gsf_read_json_file(GSF_TIKTOK_TOKEN)
    config=_gsf_read_json_file(GSF_TIKTOK_CONFIG)

    try:
        if token.get("access_token") and config.get("client_key") and config.get("client_secret"):
            _gsf_http_json(
                GSF_TIKTOK_REVOKE_URL,
                method="POST",
                form_body={
                    "client_key":config.get("client_key"),
                    "client_secret":config.get("client_secret"),
                    "token":token.get("access_token"),
                }
            )
    except Exception:
        pass

    errors=[]
    for p in (GSF_TIKTOK_TOKEN,GSF_TIKTOK_CONFIG):
        try:
            if Path(p).exists():
                Path(p).unlink()
        except Exception as e:
            errors.append(str(e))

    return (not errors),("; ".join(errors) if errors else "TikTok scollegato")


def _gsf_tiktok_chunk_plan(video_size):
    """
    Follows TikTok media-transfer rules:
    <5MB whole; <=64MB whole; larger files use 32MB chunks with the
    trailing remainder merged into the last chunk.
    """
    size=max(0,int(video_size or 0))
    if size<=0:
        return 0,0

    if size<=64*1024*1024:
        return size,1

    chunk=32*1024*1024
    count=max(1,size//chunk)
    return chunk,count


def _gsf_tiktok_upload_draft(video_bytes,progress_callback=None):
    token,config,error=_gsf_tiktok_credentials()
    if token is None:
        return {"ok":False,"error":error or "TikTok non collegato"}

    if not isinstance(video_bytes,(bytes,bytearray)) or len(video_bytes)<1:
        return {"ok":False,"error":"Master video non disponibile"}

    access_token=str(token.get("access_token","") or "")
    size=len(video_bytes)
    chunk_size,total_count=_gsf_tiktok_chunk_plan(size)

    init=_gsf_http_json(
        GSF_TIKTOK_UPLOAD_INIT,
        method="POST",
        headers={
            "Authorization":f"Bearer {access_token}",
        },
        json_body={
            "source_info":{
                "source":"FILE_UPLOAD",
                "video_size":size,
                "chunk_size":chunk_size,
                "total_chunk_count":total_count,
            }
        }
    )

    payload=init.get("data") or {}
    err=(payload.get("error") or {})
    if not init.get("ok") or (
        isinstance(err,dict) and err.get("code") not in (None,"","ok")
    ):
        return {
            "ok":False,
            "error":str(payload or init.get("error")),
        }

    data=payload.get("data") or {}
    upload_url=str(data.get("upload_url","") or "")
    publish_id=str(data.get("publish_id","") or "")
    if not upload_url or not publish_id:
        return {
            "ok":False,
            "error":"TikTok non ha restituito upload_url/publish_id",
        }

    sent=0
    while sent<size:
        remaining=size-sent
        # For the last planned part, upload all remaining bytes.
        if total_count<=1:
            this_size=remaining
        else:
            part_index=sent//chunk_size
            if part_index>=total_count-1:
                this_size=remaining
            else:
                this_size=min(chunk_size,remaining)

        end=sent+this_size-1
        chunk=bytes(video_bytes[sent:sent+this_size])

        req=Request(
            upload_url,
            data=chunk,
            headers={
                "Content-Type":"video/mp4",
                "Content-Length":str(this_size),
                "Content-Range":f"bytes {sent}-{end}/{size}",
            },
            method="PUT"
        )

        try:
            with urlopen(req,timeout=120) as resp:
                status=int(getattr(resp,"status",0) or 0)
                if status not in (200,201,206):
                    return {
                        "ok":False,
                        "error":f"TikTok upload HTTP {status}",
                        "publish_id":publish_id,
                    }
        except HTTPError as e:
            body=e.read().decode("utf-8","replace") if hasattr(e,"read") else ""
            return {
                "ok":False,
                "error":f"TikTok upload HTTP {getattr(e,'code',0)}: {body}",
                "publish_id":publish_id,
            }
        except Exception as e:
            return {
                "ok":False,
                "error":str(e),
                "publish_id":publish_id,
            }

        sent+=this_size
        if progress_callback:
            try:
                progress_callback(int(sent/size*100))
            except Exception:
                pass

    status=_gsf_tiktok_fetch_status(publish_id)
    return {
        "ok":True,
        "publish_id":publish_id,
        "status":status.get("status",""),
        "uploaded_bytes":status.get("uploaded_bytes",size),
        "error":"",
    }


def _gsf_tiktok_fetch_status(publish_id):
    token,config,error=_gsf_tiktok_credentials()
    if token is None:
        return {"ok":False,"status":"","error":error}

    res=_gsf_http_json(
        GSF_TIKTOK_STATUS_URL,
        method="POST",
        headers={
            "Authorization":f"Bearer {token.get('access_token','')}",
        },
        json_body={"publish_id":str(publish_id or "")}
    )
    payload=res.get("data") or {}
    api_error=payload.get("error") or {}
    if not res.get("ok") or (
        isinstance(api_error,dict)
        and api_error.get("code") not in (None,"","ok")
    ):
        return {
            "ok":False,
            "status":"",
            "error":str(payload or res.get("error")),
        }

    data=payload.get("data") or {}
    return {
        "ok":True,
        "status":str(data.get("status","") or ""),
        "fail_reason":str(data.get("fail_reason","") or ""),
        "uploaded_bytes":int(data.get("uploaded_bytes",0) or 0),
        "post_ids":data.get("publicaly_available_post_id",[]) or [],
        "error":"",
    }


# ============================================================
# INSTAGRAM REELS — official Meta container -> status -> publish
# Requires a publicly reachable HTTPS video URL.
# ============================================================

def _gsf_instagram_config():
    return _gsf_read_json_file(GSF_INSTAGRAM_CONFIG)


def _gsf_instagram_validate(ig_user_id,access_token):
    ig_user_id=str(ig_user_id or "").strip()
    access_token=str(access_token or "").strip()
    if not ig_user_id or not access_token:
        return False,"","Inserisci IG User ID e access token"

    url=(
        "https://graph.facebook.com/"
        +quote(ig_user_id,safe="")
        +"?"+urlencode({
            "fields":"id,username",
            "access_token":access_token,
        })
    )
    res=_gsf_http_json(url,method="GET")
    if not res.get("ok"):
        return False,"",str(res.get("data") or res.get("error"))

    data=res.get("data") or {}
    if data.get("error"):
        return False,"",str(data.get("error"))

    username=str(data.get("username","") or "")
    return True,username,""


def _gsf_instagram_connect(ig_user_id,access_token):
    ok,username,error=_gsf_instagram_validate(
        ig_user_id,access_token
    )
    if not ok:
        return False,error

    _gsf_secure_write_json(
        GSF_INSTAGRAM_CONFIG,
        {
            "ig_user_id":str(ig_user_id).strip(),
            "access_token":str(access_token).strip(),
            "username":username,
        }
    )
    return True,username or "Instagram collegato"


def _gsf_instagram_connection_status():
    cfg=_gsf_instagram_config()
    return {
        "connected":bool(
            cfg.get("ig_user_id") and cfg.get("access_token")
        ),
        "username":str(cfg.get("username","") or ""),
        "error":"",
    }


def _gsf_instagram_disconnect():
    try:
        if GSF_INSTAGRAM_CONFIG.exists():
            GSF_INSTAGRAM_CONFIG.unlink()
        return True,"Instagram scollegato"
    except Exception as e:
        return False,str(e)


def _gsf_instagram_public_video_url_ok(value):
    try:
        u=urlparse(str(value or "").strip())
        return (
            u.scheme.lower()=="https"
            and bool(u.netloc)
            and not u.username
            and not u.password
        )
    except Exception:
        return False


class _GSFInstagramStageHandler(BaseHTTPRequestHandler):
    """Serve one MP4 with HTTP Range support while Meta fetches it."""
    server_version="GSFStage/1.0"

    def log_message(self,*args,**kwargs):
        return

    def _send_common(self,length,status=200,content_range=None):
        self.send_response(status)
        self.send_header("Content-Type","video/mp4")
        self.send_header("Accept-Ranges","bytes")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(max(0,int(length))))
        if content_range:
            self.send_header("Content-Range",content_range)
        self.end_headers()

    def do_HEAD(self):
        route=self.path.split("?",1)[0]
        if route!=getattr(self.server,"public_path",""):
            self.send_response(404)
            self.end_headers()
            return
        data=getattr(self.server,"video_bytes",b"") or b""
        self._send_common(len(data),200)

    def do_GET(self):
        route=self.path.split("?",1)[0]
        if route!=getattr(self.server,"public_path",""):
            self.send_response(404)
            self.end_headers()
            return

        data=getattr(self.server,"video_bytes",b"") or b""
        total=len(data)
        if total<=0:
            self.send_response(404)
            self.end_headers()
            return

        start=0
        end=total-1
        range_header=str(self.headers.get("Range","") or "").strip()

        if range_header.startswith("bytes="):
            raw=range_header[6:].split(",",1)[0].strip()
            try:
                left,right=(raw.split("-",1)+[""])[:2]
                if left:
                    start=max(0,int(left))
                    if right:
                        end=min(total-1,int(right))
                else:
                    suffix=max(1,int(right))
                    start=max(0,total-suffix)
                if start>=total or end<start:
                    self.send_response(416)
                    self.send_header("Content-Range",f"bytes */{total}")
                    self.end_headers()
                    return
                chunk=data[start:end+1]
                self._send_common(
                    len(chunk),
                    206,
                    f"bytes {start}-{end}/{total}"
                )
                self.wfile.write(chunk)
                return
            except Exception:
                self.send_response(416)
                self.send_header("Content-Range",f"bytes */{total}")
                self.end_headers()
                return

        self._send_common(total,200)
        self.wfile.write(data)


def _gsf_find_cloudflared():
    cfg=_gsf_app_credentials()
    candidates=[
        str(cfg.get("cloudflared_path","") or "").strip(),
        os.environ.get("GSF_CLOUDFLARED",""),
        shutil.which("cloudflared") or "",
        shutil.which("cloudflared.exe") or "",
        str(Path.cwd()/"cloudflared.exe"),
        str(GSF_SOCIAL_DIR/"bin"/"cloudflared.exe"),
    ]
    for item in candidates:
        if not item:
            continue
        path=os.path.expanduser(str(item))
        if os.path.exists(path):
            return path
    return ""


def _gsf_start_instagram_staging(video_bytes,timeout_seconds=25):
    """
    Temporary HTTPS staging for Meta using a Cloudflare Quick Tunnel.
    No URL is shown to the user. The tunnel lives only for this publish action.
    """
    if not isinstance(video_bytes,(bytes,bytearray)) or len(video_bytes)<1024:
        return None,"Video finale non disponibile"

    cloudflared=_gsf_find_cloudflared()
    if not cloudflared:
        return None,(
            "Per la pubblicazione Instagram automatica manca il componente "
            "cloudflared. Nella build finale può essere incluso accanto all'app."
        )

    token=secrets.token_urlsafe(24).replace("-","").replace("_","")
    public_path=f"/gsf-{token}.mp4"

    try:
        server=ThreadingHTTPServer(
            ("127.0.0.1",0),
            _GSFInstagramStageHandler
        )
        server.video_bytes=bytes(video_bytes)
        server.public_path=public_path
        thread=threading.Thread(
            target=server.serve_forever,
            daemon=True
        )
        thread.start()

        local_url=f"http://127.0.0.1:{server.server_address[1]}"
        proc=subprocess.Popen(
            [
                cloudflared,
                "tunnel",
                "--no-autoupdate",
                "--url",
                local_url,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=(
                getattr(subprocess,"CREATE_NO_WINDOW",0)
                if os.name=="nt" else 0
            )
        )

        deadline=time.time()+max(8,int(timeout_seconds))
        public_base=""
        log_lines=[]

        while time.time()<deadline:
            if proc.poll() is not None:
                break
            line=proc.stdout.readline() if proc.stdout else ""
            if line:
                log_lines.append(line.strip())
                match=re.search(
                    r"https://[a-z0-9-]+\.trycloudflare\.com",
                    line,
                    re.I
                )
                if match:
                    public_base=match.group(0)
                    break
            else:
                time.sleep(.1)

        if not public_base:
            try:
                proc.terminate()
            except Exception:
                pass
            try:
                server.shutdown()
                server.server_close()
            except Exception:
                pass
            return None,(
                "Non sono riuscito ad aprire lo staging HTTPS temporaneo "
                "per Instagram."
            )

        return {
            "server":server,
            "thread":thread,
            "process":proc,
            "url":public_base.rstrip("/") + public_path,
        },""

    except Exception as e:
        try:
            server.shutdown()
            server.server_close()
        except Exception:
            pass
        return None,str(e)


def _gsf_stop_instagram_staging(stage):
    if not isinstance(stage,dict):
        return
    proc=stage.get("process")
    server=stage.get("server")
    try:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=4)
            except Exception:
                proc.kill()
    except Exception:
        pass
    try:
        if server:
            server.shutdown()
            server.server_close()
    except Exception:
        pass


def _gsf_instagram_publish_reel_auto(
    video_bytes,
    pack,
    share_to_feed=True,
    progress_callback=None
):
    """Web mode serves the temporary MP4 from the site's HTTPS /media path."""
    if GSF_WEB_MODE:
        if not isinstance(video_bytes, (bytes, bytearray)) or len(video_bytes) < 1024:
            return {"ok": False, "error": "Master video non disponibile"}
        public_app = _gsf_public_app_url()
        if not public_app or not public_app.lower().startswith("https://"):
            return {"ok": False, "error": "Instagram richiede GSF_PUBLIC_APP_URL in HTTPS"}
        digest = hashlib.sha256(bytes(video_bytes)).hexdigest()[:16]
        stage_path = GSF_PREVIEW_DIR / f"instagram_stage_{digest}.mp4"
        try:
            if not stage_path.exists() or stage_path.stat().st_size != len(video_bytes):
                tmp = Path(str(stage_path) + ".tmp")
                tmp.write_bytes(bytes(video_bytes))
                os.replace(tmp, stage_path)
            rel = _gsf_media_relative(stage_path)
            media_url = _gsf_media_url(rel)
            if media_url.startswith("/"):
                parsed = urlparse(public_app)
                media_url = f"{parsed.scheme}://{parsed.netloc}{media_url}"
            return _gsf_instagram_publish_reel(
                media_url,
                pack,
                share_to_feed=share_to_feed,
                progress_callback=progress_callback
            )
        finally:
            try:
                stage_path.unlink(missing_ok=True)
            except Exception:
                pass

    stage,error=_gsf_start_instagram_staging(video_bytes)
    if stage is None:
        return {"ok":False,"error":error}

    try:
        return _gsf_instagram_publish_reel(
            stage["url"],
            pack,
            share_to_feed=share_to_feed,
            progress_callback=progress_callback
        )
    finally:
        _gsf_stop_instagram_staging(stage)



def _gsf_instagram_publish_reel(
    video_url,
    pack,
    share_to_feed=True,
    timeout_seconds=240,
    progress_callback=None
):
    cfg=_gsf_instagram_config()
    ig_user_id=str(cfg.get("ig_user_id","") or "")
    access_token=str(cfg.get("access_token","") or "")
    if not ig_user_id or not access_token:
        return {"ok":False,"error":"Instagram non collegato"}

    if not _gsf_instagram_public_video_url_ok(video_url):
        return {
            "ok":False,
            "error":"Instagram richiede un URL HTTPS pubblico del video",
        }

    caption=str(
        pack.get(
            "selected_caption",
            pack.get("caption","")
        ) or ""
    ).strip()

    create_url=(
        "https://graph.facebook.com/"
        +quote(ig_user_id,safe="")
        +"/media"
    )
    create=_gsf_http_json(
        create_url,
        method="POST",
        form_body={
            "media_type":"REELS",
            "video_url":str(video_url).strip(),
            "caption":caption,
            "share_to_feed":"true" if share_to_feed else "false",
            "access_token":access_token,
        },
        timeout=60
    )
    create_data=create.get("data") or {}
    if not create.get("ok") or create_data.get("error"):
        return {
            "ok":False,
            "error":str(create_data or create.get("error")),
        }

    container_id=str(create_data.get("id","") or "")
    if not container_id:
        return {
            "ok":False,
            "error":"Meta non ha restituito il container Reel",
        }

    if progress_callback:
        try:
            progress_callback(20)
        except Exception:
            pass

    deadline=time.time()+max(60,int(timeout_seconds))
    last_status=""
    while time.time()<deadline:
        status_url=(
            "https://graph.facebook.com/"
            +quote(container_id,safe="")
            +"?"+urlencode({
                "fields":"status_code,status",
                "access_token":access_token,
            })
        )
        status_res=_gsf_http_json(
            status_url,
            method="GET",
            timeout=45
        )
        status_data=status_res.get("data") or {}
        if not status_res.get("ok") or status_data.get("error"):
            return {
                "ok":False,
                "container_id":container_id,
                "error":str(status_data or status_res.get("error")),
            }

        last_status=str(
            status_data.get("status_code","") or ""
        ).upper()

        if last_status=="FINISHED":
            break
        if last_status in ("ERROR","EXPIRED"):
            return {
                "ok":False,
                "container_id":container_id,
                "error":str(status_data.get("status") or last_status),
            }

        if progress_callback:
            try:
                progress_callback(55)
            except Exception:
                pass
        time.sleep(3)

    if last_status!="FINISHED":
        return {
            "ok":False,
            "container_id":container_id,
            "error":"Timeout mentre Meta elaborava il Reel",
        }

    if progress_callback:
        try:
            progress_callback(80)
        except Exception:
            pass

    publish_url=(
        "https://graph.facebook.com/"
        +quote(ig_user_id,safe="")
        +"/media_publish"
    )
    publish=_gsf_http_json(
        publish_url,
        method="POST",
        form_body={
            "creation_id":container_id,
            "access_token":access_token,
        },
        timeout=60
    )
    pub_data=publish.get("data") or {}
    if not publish.get("ok") or pub_data.get("error"):
        return {
            "ok":False,
            "container_id":container_id,
            "error":str(pub_data or publish.get("error")),
        }

    media_id=str(pub_data.get("id","") or "")
    if not media_id:
        return {
            "ok":False,
            "container_id":container_id,
            "error":"Meta non ha restituito l'ID del Reel pubblicato",
        }

    permalink=""
    info_url=(
        "https://graph.facebook.com/"
        +quote(media_id,safe="")
        +"?"+urlencode({
            "fields":"permalink",
            "access_token":access_token,
        })
    )
    info=_gsf_http_json(info_url,method="GET",timeout=30)
    if info.get("ok"):
        permalink=str(
            (info.get("data") or {}).get("permalink","") or ""
        )

    if progress_callback:
        try:
            progress_callback(100)
        except Exception:
            pass

    return {
        "ok":True,
        "container_id":container_id,
        "media_id":media_id,
        "permalink":permalink,
        "error":"",
    }


GSF_YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
GSF_YOUTUBE_DIR = GSF_SESSION_SOCIAL_DIR
GSF_YOUTUBE_TOKEN = GSF_YOUTUBE_DIR / "youtube_token.json"


def _gsf_youtube_dependencies():
    """Lazy imports: the rest of the app works even without Google libraries."""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow, Flow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError
        return {
            "ok":True,
            "Credentials":Credentials,
            "Request":Request,
            "InstalledAppFlow":InstalledAppFlow,
            "Flow":Flow,
            "build":build,
            "MediaFileUpload":MediaFileUpload,
            "HttpError":HttpError,
            "error":"",
        }
    except Exception as e:
        return {
            "ok":False,
            "error":str(e),
        }


def _gsf_youtube_install_command():
    return (
        "python -m pip install --upgrade "
        "google-api-python-client google-auth-oauthlib google-auth-httplib2"
    )


def _gsf_youtube_save_credentials(creds):
    GSF_YOUTUBE_DIR.mkdir(parents=True,exist_ok=True)
    GSF_YOUTUBE_TOKEN.write_text(
        creds.to_json(),
        encoding="utf-8"
    )
    try:
        os.chmod(GSF_YOUTUBE_TOKEN,0o600)
    except Exception:
        pass


def _gsf_youtube_credentials():
    """
    Load and refresh the local OAuth token.
    Returns (credentials, error).
    """
    deps=_gsf_youtube_dependencies()
    if not deps.get("ok"):
        return None,deps.get("error","Dipendenze Google mancanti")

    if not GSF_YOUTUBE_TOKEN.exists():
        return None,"Account YouTube non collegato"

    try:
        creds=deps["Credentials"].from_authorized_user_file(
            str(GSF_YOUTUBE_TOKEN),
            [GSF_YOUTUBE_SCOPE]
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(deps["Request"]())
            _gsf_youtube_save_credentials(creds)

        if not creds.valid:
            return None,"Token OAuth non valido o scaduto"

        return creds,""
    except Exception as e:
        return None,str(e)


def _gsf_youtube_connection_status():
    deps=_gsf_youtube_dependencies()
    if not deps.get("ok"):
        return {
            "dependencies":False,
            "connected":False,
            "error":deps.get("error",""),
        }

    creds,error=_gsf_youtube_credentials()
    return {
        "dependencies":True,
        "connected":bool(creds is not None),
        "error":error,
    }


def _gsf_youtube_connect(client_secret_bytes):
    """
    Official Google installed-app OAuth flow.
    The client secret file is temporary; the reusable token remains only
    in the user's home directory.
    """
    deps=_gsf_youtube_dependencies()
    if not deps.get("ok"):
        return False,deps.get("error","Dipendenze Google mancanti")

    if not client_secret_bytes:
        return False,"Seleziona il file OAuth client_secret.json"

    tmp_dir=_gsf_session_mkdtemp("gsf_youtube_oauth_")
    secret_path=os.path.join(tmp_dir,"client_secret.json")

    try:
        if isinstance(client_secret_bytes,str):
            client_secret_bytes=client_secret_bytes.encode("utf-8")
        with open(secret_path,"wb") as f:
            f.write(bytes(client_secret_bytes))

        # Validate JSON before opening OAuth.
        with open(secret_path,"r",encoding="utf-8") as f:
            payload=json.load(f)
        if not isinstance(payload,dict) or not (
            isinstance(payload.get("installed"),dict)
            or isinstance(payload.get("web"),dict)
        ):
            return False,"Il JSON non sembra una credenziale OAuth Google valida"

        flow=deps["InstalledAppFlow"].from_client_secrets_file(
            secret_path,
            scopes=[GSF_YOUTUBE_SCOPE]
        )
        creds=flow.run_local_server(
            host="localhost",
            port=0,
            authorization_prompt_message=(
                "Apri questo indirizzo nel browser per collegare YouTube: {url}"
            ),
            success_message=(
                "YouTube collegato a Gaming Shorts Factory. "
                "Puoi chiudere questa scheda."
            ),
            open_browser=True,
            access_type="offline",
            prompt="consent",
        )

        _gsf_youtube_save_credentials(creds)
        return True,"YouTube collegato"
    except Exception as e:
        return False,str(e)
    finally:
        shutil.rmtree(tmp_dir,ignore_errors=True)


def _gsf_youtube_disconnect():
    try:
        if GSF_YOUTUBE_TOKEN.exists():
            GSF_YOUTUBE_TOKEN.unlink()
        return True,"YouTube scollegato da Gaming Shorts Factory"
    except Exception as e:
        return False,str(e)


def _gsf_youtube_upload(
    video_bytes,
    pack,
    privacy_status="private",
    made_for_kids=False,
    progress_callback=None
):
    """
    Resumable videos.insert upload using the official YouTube Data API.
    Upload occurs only after the user explicitly presses the publish button.
    """
    deps=_gsf_youtube_dependencies()
    if not deps.get("ok"):
        return {
            "ok":False,
            "error":deps.get("error","Dipendenze Google mancanti"),
        }

    creds,error=_gsf_youtube_credentials()
    if creds is None:
        return {
            "ok":False,
            "error":error or "YouTube non collegato",
        }

    if not isinstance(video_bytes,(bytes,bytearray)) or len(video_bytes)<1024:
        return {
            "ok":False,
            "error":"Master video finale non disponibile",
        }

    privacy_status=str(privacy_status or "private")
    if privacy_status not in ("private","unlisted","public"):
        privacy_status="private"

    tmp_dir=_gsf_session_mkdtemp("gsf_youtube_upload_")
    path=os.path.join(
        tmp_dir,
        pack.get("selected_filename",pack.get("filename","gaming-short.mp4"))
    )

    try:
        with open(path,"wb") as f:
            f.write(bytes(video_bytes))

        youtube=deps["build"](
            "youtube",
            "v3",
            credentials=creds,
            cache_discovery=False
        )

        title=str(
            pack.get("selected_title",pack.get("title","Gaming Short"))
            or "Gaming Short"
        ).strip()[:100]

        description=str(
            pack.get("selected_caption",pack.get("caption",""))
            or ""
        ).strip()[:5000]

        tags=[]
        for tag in pack.get("hashtags",[]) or []:
            clean=str(tag).strip().lstrip("#").strip()
            if clean and clean not in tags:
                tags.append(clean)

        body={
            "snippet":{
                "title":title,
                "description":description,
                "categoryId":"20",
                "tags":tags[:30],
            },
            "status":{
                "privacyStatus":privacy_status,
                "selfDeclaredMadeForKids":bool(made_for_kids),
            },
        }

        media=deps["MediaFileUpload"](
            path,
            chunksize=8*1024*1024,
            resumable=True,
            mimetype="video/mp4"
        )

        request=youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response=None
        retries=0
        while response is None:
            try:
                status,response=request.next_chunk()
                if status is not None and progress_callback:
                    try:
                        progress_callback(
                            max(0,min(100,int(status.progress()*100)))
                        )
                    except Exception:
                        pass
            except deps["HttpError"] as e:
                status_code=int(getattr(getattr(e,"resp",None),"status",0) or 0)
                if status_code in (500,502,503,504) and retries<4:
                    retries+=1
                    time.sleep(min(8,2**retries))
                    continue
                raise

        if progress_callback:
            try:
                progress_callback(100)
            except Exception:
                pass

        video_id=str((response or {}).get("id","") or "")
        if not video_id:
            return {
                "ok":False,
                "error":"YouTube non ha restituito l'ID del video",
                "response":response,
            }

        return {
            "ok":True,
            "video_id":video_id,
            "url":f"https://www.youtube.com/watch?v={video_id}",
            "privacy":privacy_status,
            "title":title,
            "response":response,
        }

    except Exception as e:
        return {
            "ok":False,
            "error":str(e),
        }
    finally:
        shutil.rmtree(tmp_dir,ignore_errors=True)



# ============================================================
# V77 — WEB OAUTH (anonymous session, official APIs)
# ============================================================
def _gsf_public_app_url():
    cfg = _gsf_app_credentials()
    value = str(
        os.environ.get("GSF_PUBLIC_APP_URL")
        or cfg.get("public_app_url", "")
        or ""
    ).strip()
    return value.rstrip("/") + ("/" if value else "")


def _gsf_youtube_client_config():
    cfg = _gsf_app_credentials()
    raw_json = str(cfg.get("youtube_client_secret_json", "") or "").strip()
    if raw_json:
        try:
            payload = json.loads(raw_json)
            if isinstance(payload, dict):
                return payload, ""
        except Exception as e:
            return {}, "GSF_YOUTUBE_CLIENT_SECRET_JSON non valido: " + str(e)
    secret_path = os.path.expanduser(str(cfg.get("youtube_client_secret_file", "") or "").strip())
    if not secret_path or not os.path.exists(secret_path):
        return {}, "YouTube non è configurato sul server."
    try:
        payload = json.loads(Path(secret_path).read_text(encoding="utf-8"))
        return (payload, "") if isinstance(payload, dict) else ({}, "Credenziale Google non valida")
    except Exception as e:
        return {}, str(e)


def _gsf_youtube_web_auth_url():
    deps = _gsf_youtube_dependencies()
    if not deps.get("ok"):
        return "", deps.get("error", "Dipendenze Google mancanti")
    payload, config_error = _gsf_youtube_client_config()
    redirect_uri = _gsf_public_app_url()
    if not payload:
        return "", config_error or "YouTube non è configurato sul server."
    if not redirect_uri:
        return "", "Imposta GSF_PUBLIC_APP_URL per il collegamento YouTube via browser."
    try:
        if GSF_WEB_MODE and not isinstance(payload.get("web"), dict):
            return "", "Per il sito serve una credenziale OAuth Google di tipo Web application."
        state = secrets.token_urlsafe(32)
        flow = deps["Flow"].from_client_config(
            payload,
            scopes=[GSF_YOUTUBE_SCOPE],
            state=state,
            redirect_uri=redirect_uri,
        )
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=state,
        )
        _gsf_write_oauth_state(state, {
            "platform": "YouTube",
            "redirect_uri": redirect_uri,
        })
        return auth_url, ""
    except Exception as e:
        return "", str(e)


def _gsf_youtube_web_complete(code, state, pending):
    deps = _gsf_youtube_dependencies()
    if not deps.get("ok"):
        return False, deps.get("error", "Dipendenze Google mancanti")
    payload, config_error = _gsf_youtube_client_config()
    redirect_uri = str((pending or {}).get("redirect_uri", "") or _gsf_public_app_url()).strip()
    if not payload or not redirect_uri:
        return False, config_error or "Configurazione YouTube incompleta sul server."
    try:
        flow = deps["Flow"].from_client_config(
            payload,
            scopes=[GSF_YOUTUBE_SCOPE],
            state=state,
            redirect_uri=redirect_uri,
        )
        flow.fetch_token(code=str(code))
        _gsf_youtube_save_credentials(flow.credentials)
        return True, "YouTube collegato."
    except Exception as e:
        return False, str(e)


def _gsf_tiktok_web_auth_url():
    cfg = _gsf_app_credentials()
    client_key = str(cfg.get("tiktok_client_key", "") or "").strip()
    client_secret = str(cfg.get("tiktok_client_secret", "") or "").strip()
    redirect_uri = _gsf_public_app_url()
    if not client_key or not client_secret:
        return "", "TikTok non è configurato sul server."
    if not redirect_uri:
        return "", "Imposta GSF_PUBLIC_APP_URL per il collegamento TikTok via browser."
    if GSF_WEB_MODE and not redirect_uri.lower().startswith("https://"):
        return "", "TikTok Web richiede un Redirect URI HTTPS."
    state = secrets.token_urlsafe(32)
    params = {
        "client_key": client_key,
        "response_type": "code",
        "scope": GSF_TIKTOK_SCOPES,
        "redirect_uri": redirect_uri,
        "state": state,
    }
    _gsf_write_oauth_state(state, {
        "platform": "TikTok",
        "redirect_uri": redirect_uri,
    })
    return GSF_TIKTOK_AUTH_URL + "?" + urlencode(params), ""


def _gsf_tiktok_web_complete(code, state, pending):
    cfg = _gsf_app_credentials()
    client_key = str(cfg.get("tiktok_client_key", "") or "").strip()
    client_secret = str(cfg.get("tiktok_client_secret", "") or "").strip()
    redirect_uri = str((pending or {}).get("redirect_uri", "") or _gsf_public_app_url()).strip()
    if not client_key or not client_secret or not redirect_uri:
        return False, "Configurazione TikTok incompleta sul server."
    res = _gsf_http_json(
        GSF_TIKTOK_TOKEN_URL,
        method="POST",
        form_body={
            "client_key": client_key,
            "client_secret": client_secret,
            "code": str(code),
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        },
    )
    if not res.get("ok"):
        return False, str(res.get("data") or res.get("error"))
    token = res.get("data") or {}
    if not token.get("access_token"):
        return False, str(token)
    if "video.upload" not in str(token.get("scope", "") or ""):
        return False, "TikTok non ha concesso lo scope video.upload."
    _gsf_tiktok_save_config(client_key, client_secret)
    _gsf_tiktok_save_token(token)
    return True, "TikTok collegato."


def _gsf_social_connection_status(platform):
    platform = str(platform or "")
    if platform == "YouTube":
        status = _gsf_youtube_connection_status()
        return bool(status.get("connected")), str(status.get("error", "") or "")
    if platform == "TikTok":
        status = _gsf_tiktok_connection_status()
        return bool(status.get("connected")), str(status.get("error", "") or "")
    if platform == "Instagram":
        status = _gsf_instagram_connection_status()
        return bool(status.get("connected")), str(status.get("error", "") or "")
    return False, "Piattaforma non riconosciuta"


def _gsf_social_web_auth_url(platform):
    platform = str(platform or "")
    if platform == "YouTube":
        return _gsf_youtube_web_auth_url()
    if platform == "TikTok":
        return _gsf_tiktok_web_auth_url()
    if platform == "Instagram":
        # Meta publishing is API-only here, but user OAuth requires a dedicated
        # Meta Login configuration. A server-owned connection can be provisioned
        # through GSF_INSTAGRAM_USER_ID / GSF_INSTAGRAM_ACCESS_TOKEN.
        cfg = _gsf_app_credentials()
        uid = str(cfg.get("instagram_user_id", "") or "").strip()
        token = str(cfg.get("instagram_access_token", "") or "").strip()
        if uid and token:
            ok, msg = _gsf_instagram_connect(uid, token)
            return "", "" if ok else msg
        return "", "Instagram richiede la configurazione Meta del sito."
    return "", "Piattaforma non riconosciuta"


def _gsf_handle_web_oauth_callback():
    state = _gsf_query_value("state")
    code = _gsf_query_value("code")
    error = _gsf_query_value("error")
    if not state or (not code and not error):
        return False
    pending = _gsf_read_oauth_state(state, consume=False)
    if not pending:
        st.error("Collegamento social scaduto o non valido.")
        _gsf_read_oauth_state(state, consume=True)
        return True
    if _gsf_safe_session_id(pending.get("session_id", "")) != GSF_SESSION_ID:
        st.error("Sessione social non valida.")
        _gsf_read_oauth_state(state, consume=True)
        return True
    platform = str(pending.get("platform", "") or "")
    if error:
        message = _gsf_query_value("error_description") or error
        ok = False
    elif platform == "YouTube":
        ok, message = _gsf_youtube_web_complete(code, state, pending)
    elif platform == "TikTok":
        ok, message = _gsf_tiktok_web_complete(code, state, pending)
    else:
        ok, message = False, "Callback social non riconosciuto."
    _gsf_read_oauth_state(state, consume=True)
    try:
        st.query_params.clear()
    except Exception:
        pass
    if ok:
        st.success("✅ " + message + " Puoi chiudere questa scheda e tornare al progetto.")
    else:
        st.error("Collegamento non riuscito: " + str(message))
    st.stop()
    return True


_gsf_handle_web_oauth_callback()




def _gsf_clear_final_master():
    for key in (
        "publication_final_bytes",
        "publication_final_signature",
        "publication_final_encoder",
        "publication_final_seconds",
        "show_social_publish_v53",
        "show_social_publish_v54",
        "social_final_context_v53",
        "social_final_context_v54",
    ):
        st.session_state.pop(key,None)


def _gsf_recipe_token(recipe):
    try:
        raw=json.dumps(
            recipe or {},
            sort_keys=True,
            ensure_ascii=False,
            default=str
        ).encode("utf-8")
        return hashlib.sha1(raw, usedforsecurity=False).hexdigest()[:16]
    except Exception:
        return hashlib.sha1(
            repr(recipe).encode("utf-8","ignore")
        , usedforsecurity=False).hexdigest()[:16]


def _gsf_set_final_recipe(recipe,source_label=""):
    st.session_state["gsf_final_recipe"]=dict(recipe or {})
    st.session_state["publication_ready"]=True
    st.session_state["publication_source"]=str(
        (recipe or {}).get("kind",source_label or "recipe")
    )
    st.session_state["publication_origin"]=str(source_label or "")
    _gsf_clear_final_master()


def _gsf_v93_release_analysis_memory():
    if not GSF_LOW_MEMORY_WEB:
        return
    for _key in (
        "gsf_ai_scan_cache_v40",
        "gsf_ai_scan_cache_v50",
        "gsf_ai_voice_cache_v40",
        "gsf_ai_refine_motion_cache_v50",
        "gsf_fast_ai_cache",
    ):
        try:
            st.session_state.pop(_key,None)
        except Exception:
            pass
    for _cached in (
        globals().get("_gsf_ai_whisper_tiny"),
        globals().get("_gsf_subtitle_whisper_model"),
    ):
        try:
            if _cached is not None:
                _cached.clear()
        except Exception:
            pass
    try:
        import gc
        gc.collect()
    except Exception:
        pass
    try:
        import ctypes
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass


def _gsf_render_final_recipe(recipe,output_path,video_obj=None):
    """
    The ONLY manual/editor final render path.
    Editor screens only save a recipe; this function renders once at the bottom.
    """
    recipe=dict(recipe or {})
    kind=str(recipe.get("kind","") or "")

    if kind=="auto":
        return _gsf_render_auto_master(
            str(recipe.get("source_path","")),
            float(recipe.get("start",0.0) or 0.0),
            float(recipe.get("duration",15.0) or 15.0),
            master_token=str(
                recipe.get("master_token")
                or (
                    _gsf_upload_master_token(video_obj)
                    if video_obj is not None else ""
                )
            ),
            subtitles_enabled=bool(
                recipe.get("subtitles_enabled",True)
            ),
            manual_hook=str(recipe.get("manual_hook","") or ""),
            output_path=output_path
        )

    if kind in ("main_editor","inline_editor"):
        kw=dict(recipe.get("render_kwargs") or {})
        return _gsf_render_core(
            str(recipe.get("source_path","")),
            output_path,
            float(recipe.get("start",0.0) or 0.0),
            float(recipe.get("duration",15.0) or 15.0),
            **kw
        )

    return {
        "ok":False,
        "error":"Ricetta Short finale non disponibile."
    }


def _gsf_recipe_selected(kind,start,duration,source_path,**extra):
    recipe={
        "kind":str(kind),
        "source_path":str(source_path),
        "start":float(start),
        "duration":float(duration),
    }
    recipe.update(extra)
    return recipe



def _gsf_social_clean_description(pack):
    """Keep hashtags in their own editable field."""
    value=str((pack or {}).get("caption","") or "").strip()
    for tag in (pack or {}).get("hashtags",[]) or []:
        value=value.replace(str(tag),"")
    value=re.sub(r"[ \t]+\n","\n",value)
    value=re.sub(r"\n{3,}","\n\n",value)
    return value.strip()


def _gsf_social_parse_hashtags(value):
    """Editable hashtag field -> normalized unique tags."""
    raw=re.split(r"[\s,;]+",str(value or "").strip())
    tags=[]
    seen=set()
    for item in raw:
        token=re.sub(r"[^A-Za-z0-9À-ÿ_#]+","",item.strip()).lstrip("#")
        if not token:
            continue
        tag="#"+token[:48]
        low=tag.lower()
        if low not in seen:
            seen.add(low)
            tags.append(tag)
    return tags[:30]


def _gsf_social_pack_for_upload(pack,title,description,hashtags):
    """Use the user's edited title/description/hashtags as the payload."""
    final=dict(pack or {})
    tags=_gsf_social_parse_hashtags(hashtags)
    description=str(description or "").strip()
    upload_caption=description
    if tags:
        upload_caption=(
            description
            + ("\n\n" if description else "")
            + " ".join(tags)
        ).strip()

    final=_gsf_finalize_publish_pack(
        final,
        selected_title=str(title or "").strip(),
        selected_caption=upload_caption,
        title_index=0,
        caption_index=0
    )
    final["hashtags"]=tags
    final["selected_title"]=str(title or "").strip()
    final["selected_description"]=description
    final["selected_caption"]=upload_caption
    final["caption"]=upload_caption
    return final


GSF_PUBLISH_CENTER_VERSION = "v54"


def _gsf_publish_context_token(pack):
    """
    Widget identity follows the actual publishing context.
    Changing game/platform/tone/moment no longer leaves stale edited text
    from the previous pack in Streamlit widgets.
    """
    payload={
        "engine":GSF_PUBLISHING_ENGINE_VERSION,
        "platform":pack.get("platform",""),
        "game":pack.get("game",""),
        "tone":pack.get("tone",""),
        "start":round(float(pack.get("start",0.0) or 0.0),3),
        "titles":pack.get("title_variants",[]),
        "captions":pack.get("caption_variants",[]),
    }
    return hashlib.md5(
        json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False
        ).encode("utf-8")
    , usedforsecurity=False).hexdigest()[:10]


def _gsf_publish_readiness(pack,video_bytes=None,master_signature=""):
    """
    Internal readiness check for the package we generate.
    These are product-quality checks, not claims about official platform rules.
    """
    pack=pack or {}
    title=str(pack.get("selected_title",pack.get("title","")) or "").strip()
    caption=str(pack.get("selected_caption",pack.get("caption","")) or "").strip()
    hashtags=list(pack.get("hashtags",[]) or [])
    filename=str(
        pack.get("selected_filename",pack.get("filename","")) or ""
    ).strip()
    platform=str(pack.get("platform","") or "")
    pub_sig=str(pack.get("publishing_signature","") or "")
    preset=pack.get("preset") or {}
    title_limit=int(preset.get("title_limit",70) or 70)

    video_ok=isinstance(video_bytes,(bytes,bytearray)) and len(video_bytes)>1024
    title_ok=bool(title)
    caption_ok=bool(caption)
    hashtag_ok=len(hashtags)>=2
    filename_ok=bool(filename) and filename.lower().endswith(".mp4")
    platform_ok=platform in ["YouTube Shorts","TikTok","Instagram Reels"]
    signature_ok=bool(pub_sig)
    title_length_ok=(len(title)<=title_limit) if title else False

    checks=[
        {
            "id":"video",
            "label":"Video finale",
            "ok":video_ok,
            "detail":"master presente" if video_ok else "crea prima il master finale",
            "required":True,
        },
        {
            "id":"title",
            "label":"Titolo",
            "ok":title_ok,
            "detail":"selezionato" if title_ok else "titolo mancante",
            "required":True,
        },
        {
            "id":"caption",
            "label":"Caption",
            "ok":caption_ok,
            "detail":"pronta" if caption_ok else "caption mancante",
            "required":True,
        },
        {
            "id":"hashtags",
            "label":"Hashtag",
            "ok":hashtag_ok,
            "detail":f"{len(hashtags)} tag" if hashtags else "hashtag mancanti",
            "required":True,
        },
        {
            "id":"filename",
            "label":"File",
            "ok":filename_ok,
            "detail":filename if filename_ok else "nome file non valido",
            "required":True,
        },
        {
            "id":"platform",
            "label":"Piattaforma",
            "ok":platform_ok,
            "detail":platform if platform else "non selezionata",
            "required":True,
        },
        {
            "id":"signature",
            "label":"Pack",
            "ok":signature_ok,
            "detail":pub_sig[:8] if pub_sig else "firma mancante",
            "required":True,
        },
        {
            "id":"title_length",
            "label":"Titolo compatto",
            "ok":title_length_ok,
            "detail":(
                f"{len(title)}/{title_limit} caratteri"
                if title else "nessun titolo"
            ),
            "required":True,
        },
    ]

    if master_signature:
        checks.append({
            "id":"master_signature",
            "label":"Master",
            "ok":True,
            "detail":str(master_signature)[:8],
            "required":False,
        })

    required=[c for c in checks if c.get("required")]
    ready=all(c.get("ok") for c in required)
    missing=[c for c in required if not c.get("ok")]

    return {
        "ready":bool(ready),
        "checks":checks,
        "missing":missing,
        "ready_count":sum(1 for c in required if c.get("ok")),
        "total_count":len(required),
    }


def _gsf_publish_checklist_text(pack,readiness,master_signature=""):
    lines=[
        "GAMING SHORTS FACTORY — PUBLISH CENTER",
        f"Piattaforma: {pack.get('platform','')}",
        f"Gioco: {pack.get('game','')}",
        f"File: {pack.get('selected_filename',pack.get('filename',''))}",
        f"Pack: {pack.get('publishing_signature','')}",
    ]
    if master_signature:
        lines.append(f"Master: {master_signature}")

    lines.append("")
    lines.append("CONTROLLI")
    for item in readiness.get("checks",[]):
        icon="OK" if item.get("ok") else "DA SISTEMARE"
        lines.append(
            f"[{icon}] {item.get('label','')}: {item.get('detail','')}"
        )

    lines.append("")
    lines.append(
        "STATO: PRONTO"
        if readiness.get("ready")
        else "STATO: DA COMPLETARE"
    )
    return "\n".join(lines)+"\n"


def _gsf_publish_center_json(pack,readiness,master_signature=""):
    manifest=_gsf_publish_manifest(
        pack,
        master_signature=master_signature
    )
    manifest["publish_center_version"]=GSF_PUBLISH_CENTER_VERSION
    manifest["ready"]=bool(readiness.get("ready"))
    manifest["checks"]=[
        {
            "id":c.get("id",""),
            "label":c.get("label",""),
            "ok":bool(c.get("ok")),
            "detail":c.get("detail",""),
        }
        for c in readiness.get("checks",[])
    ]
    return manifest


def _gsf_publish_selected_text(pack):
    """Copy/paste text containing ONLY the user's chosen variant."""
    return (
        f"PIATTAFORMA\n{pack.get('platform','')}\n\n"
        f"GIOCO\n{pack.get('game','')}\n\n"
        f"TITOLO\n{pack.get('selected_title',pack.get('title',''))}\n\n"
        f"CAPTION / DESCRIZIONE\n"
        f"{pack.get('selected_caption',pack.get('caption',''))}\n\n"
        f"HASHTAG\n{' '.join(pack.get('hashtags',[]))}\n\n"
        f"NOME FILE\n{pack.get('selected_filename',pack.get('filename',''))}\n\n"
        f"FIRMA PACK\n{pack.get('publishing_signature','')}\n"
    )


def _gsf_publish_manifest(pack,master_signature=""):
    """Machine-readable companion for a ready-to-publish Short."""
    return {
        "engine":GSF_PUBLISHING_ENGINE_VERSION,
        "platform":pack.get("platform",""),
        "game":pack.get("game",""),
        "tone":pack.get("tone",""),
        "start":pack.get("start",0.0),
        "event":pack.get("event_label",""),
        "event_confidence":pack.get("confidence",""),
        "short_score":pack.get("short_score",0.0),
        "title":pack.get("selected_title",pack.get("title","")),
        "caption":pack.get("selected_caption",pack.get("caption","")),
        "hashtags":pack.get("hashtags",[]),
        "filename":pack.get("selected_filename",pack.get("filename","")),
        "hook":pack.get("hook",""),
        "publishing_signature":pack.get("publishing_signature",""),
        "master_signature":str(master_signature or ""),
    }


def _gsf_build_ready_zip(video_bytes,pack,master_signature=""):
    """
    V48 one-click package:
    MP4 + selected copy + readiness checklist + machine manifest.
    """
    readiness=_gsf_publish_readiness(
        pack,
        video_bytes=video_bytes,
        master_signature=master_signature
    )

    buffer=io.BytesIO()
    video_name=pack.get(
        "selected_filename",
        pack.get("filename","gaming-short.mp4")
    )

    with zipfile.ZipFile(
        buffer,"w",zipfile.ZIP_DEFLATED
    ) as zf:
        zf.writestr(video_name,video_bytes)
        zf.writestr(
            "PUBBLICAZIONE.txt",
            _gsf_publish_selected_text(pack)
        )
        zf.writestr(
            "CHECKLIST.txt",
            _gsf_publish_checklist_text(
                pack,readiness,
                master_signature=master_signature
            )
        )
        zf.writestr(
            "manifest.json",
            json.dumps(
                _gsf_publish_center_json(
                    pack,readiness,
                    master_signature=master_signature
                ),
                ensure_ascii=False,
                indent=2
            )
        )

    return buffer.getvalue()


def _gsf_publish_pack_text(pack):
    titles=pack.get("title_variants",[]) or [pack.get("title","")]
    captions=pack.get("caption_variants",[]) or [pack.get("caption","")]

    title_block="\n".join(
        f"{i+1}. {value}" for i,value in enumerate(titles)
    )
    caption_block="\n\n".join(
        f"VERSIONE {i+1}\n{value}" for i,value in enumerate(captions)
    )

    return (
        f"PIATTAFORMA\n{pack.get('platform','')}\n\n"
        f"GIOCO\n{pack.get('game','')}\n\n"
        f"MOMENTO\n{pack.get('event_label','')} "
        f"(confidenza {pack.get('confidence','')})\n\n"
        f"TITOLI\n{title_block}\n\n"
        f"CAPTION / DESCRIZIONE\n{caption_block}\n\n"
        f"HASHTAG\n{' '.join(pack.get('hashtags',[]))}\n\n"
        f"NOME FILE\n{pack.get('filename','')}\n"
    )


def mostra_risultati_v2(items, titolo="Le tue clip sono pronte"):
    """UI semplice per preview, modifica e download delle clip generate."""
    if not items:
        return

    st.markdown(
        f"""
        <div class="results-head">
          <h2><span class="gsf-icon-title mint"><span class="gsf-icon">✓</span>{titolo}</span></h2>
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
                "MODIFICA",
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
                "SCARICA",
                data=result_bytes,
                file_name=f"GamingShort_{i}.mp4",
                mime="video/mp4",
                key=f"result_download_{i}",
                use_container_width=True
            )


    st.markdown(
        """
        <div class="gsf-hero">
          <div class="gsf-orb">✦</div>
          <h1>Cosa vuoi creare oggi?</h1>
          <p>Carica il gameplay. Al resto può pensare la tua Gaming Shorts Factory.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def _gsf_v86_upload_css(_uploaded=False):
    return """
<style id="gsf-v86-single-upload-circle">
/* One owner, one circle: the real Streamlit upload button. */
.st-key-v73-upload-shell{
    width:100% !important;
    padding:18px 0 8px !important;
    text-align:center !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]{
    width:100% !important;
    max-width:330px !important;
    margin:0 auto !important;
    padding:0 !important;
    background:transparent !important;
    border:0 !important;
    border-radius:0 !important;
    box-shadow:none !important;
    overflow:visible !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
    width:100% !important;
    min-height:236px !important;
    height:auto !important;
    margin:0 auto !important;
    padding:8px !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    background:transparent !important;
    border:0 !important;
    border-radius:0 !important;
    box-shadow:none !important;
    overflow:visible !important;
    position:relative !important;
}

/* Kill every old outer-ring/outer-label pseudo element. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::before,
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::after{
    content:none !important;
    display:none !important;
    border:0 !important;
    background:none !important;
    box-shadow:none !important;
    animation:none !important;
    filter:none !important;
}

/* Hide native helper/file rows; the control itself remains fully functional. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzoneInstructions"],
.st-key-v73-upload-shell [data-testid="stFileUploaderFile"],
.st-key-v73-upload-shell [data-testid="stFileUploaderFileList"],
.st-key-v73-upload-shell [data-testid="stFileUploaderFileName"],
.st-key-v73-upload-shell [data-testid="stFileChips"],
.st-key-v73-upload-shell [data-testid*="UploadedFile"],
.v73-upload-meta{
    display:none !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] > div:has(button){
    width:auto !important;
    margin:0 auto !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
}

/* The only visible upload circle. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button{
    all:unset !important;
    box-sizing:border-box !important;
    width:218px !important;
    height:218px !important;
    min-width:218px !important;
    min-height:218px !important;
    max-width:218px !important;
    max-height:218px !important;
    margin:0 auto !important;
    padding:26px 22px !important;
    display:flex !important;
    flex-direction:column !important;
    align-items:center !important;
    justify-content:center !important;
    border-radius:50% !important;
    background:#DCEBFC !important;
    border:2px solid #8DB4E2 !important;
    box-shadow:0 10px 26px rgba(31,78,121,.10) !important;
    cursor:pointer !important;
    color:#214F82 !important;
    text-align:center !important;
    position:relative !important;
    overflow:hidden !important;
    -webkit-tap-highlight-color:transparent !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button:hover{
    background:#D2E6FB !important;
    border-color:#6FA1D8 !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button > *{
    display:none !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button::before{
    content:"⇧" !important;
    display:block !important;
    width:auto !important;
    height:auto !important;
    margin:0 0 13px 0 !important;
    padding:0 !important;
    background:none !important;
    color:#24558B !important;
    font-size:58px !important;
    font-weight:500 !important;
    line-height:.82 !important;
    transform:none !important;
    flex:0 0 auto !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button::after{
    content:"Carica il tuo video" !important;
    display:block !important;
    width:150px !important;
    max-width:150px !important;
    margin:0 !important;
    padding:0 !important;
    color:#244B7C !important;
    font-size:17px !important;
    font-weight:800 !important;
    line-height:1.2 !important;
    white-space:normal !important;
    text-align:center !important;
    flex:0 0 auto !important;
}

/* Completed state stays inside the same circle; no filename underneath. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"] button,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"] button{
    background:#DDF5E8 !important;
    border-color:#69BE8E !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"] button::before,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"] button::before{
    content:"✓" !important;
    color:#238A50 !important;
    font-size:54px !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"] button::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"] button::after{
    content:"Video caricato" !important;
    color:#236B43 !important;
}

/* V87: after Streamlit accepts a file, its Browse button can disappear.
   In that state the dropzone itself becomes the SAME circle, so the UI does
   not collapse. This rule only activates when an uploaded-file node exists. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"],
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]{
    width:218px !important;
    height:218px !important;
    min-width:218px !important;
    min-height:218px !important;
    max-width:218px !important;
    max-height:218px !important;
    margin:0 auto !important;
    padding:0 !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    position:relative !important;
    overflow:hidden !important;
    border-radius:50% !important;
    background:#DDF5E8 !important;
    border:2px solid #69BE8E !important;
    box-shadow:0 10px 26px rgba(31,78,121,.10) !important;
}
/* If Streamlit keeps a Browse button in this state, hide it so there is still
   exactly one circle rather than a circle inside a circle. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"] button,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"] button{
    display:none !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::before,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::before{
    content:"✓" !important;
    display:block !important;
    position:absolute !important;
    left:50% !important;
    top:38% !important;
    transform:translate(-50%,-50%) !important;
    color:#238A50 !important;
    font-size:54px !important;
    font-weight:700 !important;
    line-height:1 !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::after{
    content:"Video caricato" !important;
    display:block !important;
    position:absolute !important;
    left:50% !important;
    top:66% !important;
    transform:translate(-50%,-50%) !important;
    width:150px !important;
    max-width:150px !important;
    color:#236B43 !important;
    font-size:17px !important;
    font-weight:800 !important;
    line-height:1.2 !important;
    text-align:center !important;
    white-space:normal !important;
}

/* Small, real progress bar under the circle. No animated outer ring. */
.st-key-v73-upload-shell [role="progressbar"]{
    width:154px !important;
    max-width:154px !important;
    height:6px !important;
    min-height:6px !important;
    margin:12px auto 0 !important;
    border-radius:999px !important;
    overflow:hidden !important;
    background:rgba(34,197,94,.18) !important;
}
.st-key-v73-upload-shell [role="progressbar"] > div{
    height:100% !important;
    border-radius:999px !important;
    background:#22C55E !important;
}
.st-key-v73-upload-shell progress{
    width:154px !important;
    height:6px !important;
    margin:12px auto 0 !important;
    accent-color:#22C55E !important;
}

/* New video is centered directly below the upload circle. */
.st-key-v81_new_video{
    width:100% !important;
    display:flex !important;
    justify-content:center !important;
    align-items:center !important;
    text-align:center !important;
}
.st-key-v81_new_video > div,
.st-key-v81_new_video [data-testid="stButton"]{
    width:auto !important;
    margin:0 auto !important;
}
.st-key-v81_new_video button{
    width:auto !important;
    min-width:176px !important;
    min-height:44px !important;
    margin:10px auto 0 !important;
    padding:9px 18px !important;
    display:inline-flex !important;
    align-items:center !important;
    justify-content:center !important;
    border-radius:14px !important;
    background:#FFFFFF !important;
    color:#17324A !important;
    border:1px solid #9FCDEA !important;
    box-shadow:none !important;
    font-weight:800 !important;
}
.st-key-v81_new_video button p{
    display:block !important;
    margin:0 !important;
    color:#17324A !important;
}

@media(max-width:600px){
    .st-key-v73-upload-shell [data-testid="stFileUploader"]{
        max-width:286px !important;
    }
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
        min-height:222px !important;
        padding:6px !important;
    }
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button{
        width:208px !important;
        height:208px !important;
        min-width:208px !important;
        min-height:208px !important;
        max-width:208px !important;
        max-height:208px !important;
    }
    .st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
    [data-testid="stFileUploaderDropzone"],
    .st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
    [data-testid="stFileUploaderDropzone"]{
        width:208px !important;
        height:208px !important;
        min-width:208px !important;
        min-height:208px !important;
        max-width:208px !important;
        max-height:208px !important;
    }
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button::before{
        font-size:54px !important;
        margin-bottom:12px !important;
    }
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button::after{
        width:144px !important;
        max-width:144px !important;
        font-size:16px !important;
    }
}
</style>
"""


def _gsf_v88_loaded_circle_html():
    return """
<style id="gsf-v88-persistent-loaded-circle">
/* Once Python has a video, hide Streamlit's changing post-upload uploader DOM.
   The stable completed-state circle below becomes the single visible control. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]{display:none !important;}

.gsf-v88-loaded-wrap{
    width:100%;
    padding:18px 0 8px;
    display:flex;
    align-items:center;
    justify-content:center;
    text-align:center;
}
.gsf-v88-loaded-circle{
    box-sizing:border-box;
    width:218px;
    height:218px;
    min-width:218px;
    min-height:218px;
    max-width:218px;
    max-height:218px;
    margin:0 auto;
    padding:26px 22px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    border-radius:50%;
    background:#DDF5E8;
    border:2px solid #69BE8E;
    box-shadow:0 10px 26px rgba(31,78,121,.10);
    color:#236B43;
}
.gsf-v88-loaded-check{
    display:block;
    margin:0 0 13px 0;
    color:#238A50;
    font-size:54px;
    font-weight:700;
    line-height:.82;
}
.gsf-v88-loaded-label{
    display:block;
    width:150px;
    max-width:150px;
    margin:0;
    color:#236B43;
    font-size:17px;
    font-weight:800;
    line-height:1.2;
    white-space:normal;
    text-align:center;
}
@media(max-width:600px){
    .gsf-v88-loaded-circle{
        width:208px;
        height:208px;
        min-width:208px;
        min-height:208px;
        max-width:208px;
        max-height:208px;
    }
    .gsf-v88-loaded-check{font-size:54px;margin-bottom:12px;}
    .gsf-v88-loaded-label{width:144px;max-width:144px;font-size:16px;}
}
</style>
<div class="gsf-v88-loaded-wrap" role="status" aria-label="Video caricato">
  <div class="gsf-v88-loaded-circle">
    <span class="gsf-v88-loaded-check">✓</span>
    <span class="gsf-v88-loaded-label">Video caricato</span>
  </div>
</div>
"""


def _gsf_v89_upload_visual_html(loaded=False):
    _loaded_class = " is-loaded" if loaded else ""
    _icon = "✓" if loaded else "⇧"
    _label = "Video caricato" if loaded else "Carica il tuo video"
    return f"""
<style id="gsf-v89-decoupled-upload-visual">
.st-key-v73-upload-shell{{
    width:100% !important;
    min-height:244px !important;
    padding:10px 0 8px !important;
    position:relative !important;
    box-sizing:border-box !important;
    text-align:center !important;
}}

/* Streamlit is only the invisible functional upload layer. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]{{
    position:absolute !important;
    left:50% !important;
    top:10px !important;
    transform:translateX(-50%) !important;
    width:218px !important;
    min-width:218px !important;
    max-width:218px !important;
    height:218px !important;
    min-height:218px !important;
    max-height:218px !important;
    margin:0 !important;
    padding:0 !important;
    border:0 !important;
    background:transparent !important;
    box-shadow:none !important;
    opacity:0 !important;
    z-index:20 !important;
    overflow:hidden !important;
}}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"],
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] > div,
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button{{
    position:absolute !important;
    inset:0 !important;
    width:100% !important;
    height:100% !important;
    min-width:100% !important;
    min-height:100% !important;
    max-width:100% !important;
    max-height:100% !important;
    margin:0 !important;
    padding:0 !important;
    border-radius:50% !important;
}}

/* After upload only + NUOVO VIDEO should change the source. */
.st-key-v73-upload-shell:has(.gsf-v89-upload-visual.is-loaded)
[data-testid="stFileUploader"]{{
    pointer-events:none !important;
}}

/* This is the ONLY visible circle. It is independent of Streamlit's DOM. */
.gsf-v89-upload-visual{{
    box-sizing:border-box;
    width:218px;
    height:218px;
    min-width:218px;
    min-height:218px;
    max-width:218px;
    max-height:218px;
    margin:0 auto;
    padding:26px 22px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    border-radius:50%;
    background:#DCEBFC;
    border:2px solid #8DB4E2;
    box-shadow:0 10px 26px rgba(31,78,121,.10);
    color:#214F82;
    position:relative;
    z-index:2;
    pointer-events:none;
}}
.gsf-v89-upload-visual.is-loaded{{
    background:#DDF5E8;
    border-color:#69BE8E;
    color:#236B43;
}}
.gsf-v89-upload-icon{{
    display:block;
    margin:0 0 13px 0;
    color:#24558B;
    font-size:58px;
    font-weight:500;
    line-height:.82;
}}
.gsf-v89-upload-visual.is-loaded .gsf-v89-upload-icon{{
    color:#238A50;
    font-size:54px;
    font-weight:700;
}}
.gsf-v89-upload-label{{
    display:block;
    width:150px;
    max-width:150px;
    margin:0;
    color:inherit;
    font-size:17px;
    font-weight:800;
    line-height:1.2;
    white-space:normal;
    text-align:center;
}}

/* V91 — piccolo indicatore indipendente sotto il cerchio.
   Non mostra una percentuale inventata: appare solo mentre Streamlit espone
   il vero stato di upload e comunica chiaramente che il file sta salendo. */
.gsf-v91-upload-status{{
    display:none;
    width:154px;
    margin:10px auto 0;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    gap:5px;
    color:#238A50;
    font-size:12px;
    font-weight:800;
    line-height:1;
    text-align:center;
}}
.st-key-v73-upload-shell:has([role="progressbar"]) .gsf-v91-upload-status,
.st-key-v73-upload-shell:has(progress) .gsf-v91-upload-status,
.st-key-v73-upload-shell:has([data-testid*="Progress"]) .gsf-v91-upload-status,
.st-key-v73-upload-shell:has([data-testid="stFileChipIconSpinner"]) .gsf-v91-upload-status{{
    display:flex;
}}
.gsf-v91-upload-track{{
    position:relative;
    width:132px;
    height:5px;
    overflow:hidden;
    border-radius:999px;
    background:rgba(34,197,94,.18);
    box-shadow:inset 0 0 0 1px rgba(34,197,94,.08);
}}
.gsf-v91-upload-runner{{
    position:absolute;
    top:0;
    bottom:0;
    left:-42%;
    width:42%;
    border-radius:999px;
    background:#22C55E;
    animation:gsfV91UploadMove 1.0s ease-in-out infinite;
}}
@keyframes gsfV91UploadMove{{
    0%{{left:-42%;}}
    55%{{left:42%;}}
    100%{{left:100%;}}
}}
@media (prefers-reduced-motion: reduce){{
    .gsf-v91-upload-runner{{
        animation:none;
        left:29%;
    }}
}}

@media(max-width:600px){{
    .st-key-v73-upload-shell{{min-height:234px !important;}}
    .st-key-v73-upload-shell [data-testid="stFileUploader"]{{
        width:208px !important;
        min-width:208px !important;
        max-width:208px !important;
        height:208px !important;
        min-height:208px !important;
        max-height:208px !important;
    }}
    .gsf-v89-upload-visual{{
        width:208px;
        height:208px;
        min-width:208px;
        min-height:208px;
        max-width:208px;
        max-height:208px;
    }}
    .gsf-v89-upload-icon{{font-size:54px;margin-bottom:12px;}}
    .gsf-v89-upload-visual.is-loaded .gsf-v89-upload-icon{{font-size:52px;}}
    .gsf-v89-upload-label{{width:144px;max-width:144px;font-size:16px;}}
}}
</style>
<div class="gsf-v89-upload-visual{_loaded_class}" role="status" aria-label="{_label}">
  <span class="gsf-v89-upload-icon">{_icon}</span>
  <span class="gsf-v89-upload-label">{_label}</span>
</div>
<div class="gsf-v91-upload-status" aria-live="polite">
  <span>Caricamento video…</span>
  <span class="gsf-v91-upload-track" aria-hidden="true">
    <span class="gsf-v91-upload-runner"></span>
  </span>
</div>
"""

def _gsf_v989_direct_ready():
    marker=GSF_PREVIEW_DIR / ".direct_upload_ready.json"
    try:
        if not marker.is_file():
            return None,""
        data=json.loads(marker.read_text(encoding="utf-8"))
        candidate=Path(str(data.get("path","") or ""))
        if not candidate.is_file():
            return None,""
        if candidate.parent.resolve()!=GSF_PREVIEW_DIR.resolve():
            return None,""
        return candidate,str(data.get("name","") or candidate.name)
    except Exception:
        return None,""


def _gsf_v989_direct_upload_html(loaded=False):
    if loaded:
        return r"""
<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;background:transparent;overflow:hidden;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{height:278px;display:flex;align-items:flex-start;justify-content:center;padding-top:34px;box-sizing:border-box}
.circle{box-sizing:border-box;width:218px;height:218px;border-radius:50%;display:flex;flex-direction:column;
align-items:center;justify-content:center;background:linear-gradient(145deg,#EEF9FE 0%,#F3F0FF 100%);border:2px solid #C9DFED;
box-shadow:0 10px 24px rgba(83,126,158,.10);color:#55758A}
.icon{font-size:54px;font-weight:700;line-height:.82;color:#7297CF;margin-bottom:13px}
.label{width:150px;text-align:center;font-size:17px;font-weight:800;line-height:1.2}
@media(max-width:600px){.wrap{height:260px}.circle{width:208px;height:208px}.icon{font-size:52px}.label{width:144px;font-size:16px}}
</style></head><body><div class="wrap"><div class="circle"><div class="icon">✓</div><div class="label">Video caricato</div></div></div></body></html>
"""

    return r"""
<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;background:transparent;overflow:hidden;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{height:298px;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding-top:38px;box-sizing:border-box}
input{position:absolute;width:1px;height:1px;opacity:0;pointer-events:none}
.circle{box-sizing:border-box;width:218px;height:218px;border-radius:50%;display:flex;flex-direction:column;
align-items:center;justify-content:center;background:linear-gradient(145deg,#F1FAFE 0%,#F6F2FF 100%);border:2px solid #D0E2EE;
box-shadow:0 10px 24px rgba(83,126,158,.09);color:#607B8F;cursor:pointer;user-select:none}
.circle:hover{border-color:#B9D6E7;box-shadow:0 12px 28px rgba(83,126,158,.13)}
.icon{font-size:58px;font-weight:500;line-height:.82;color:#789AD2;margin-bottom:13px}
.label{width:150px;text-align:center;font-size:17px;font-weight:800;line-height:1.2}
.status{display:none;margin-top:7px;width:174px;text-align:center;color:#668397;font-size:12px;font-weight:800}
.track{display:block;height:5px;margin-top:5px;border-radius:999px;background:rgba(116,154,197,.15);overflow:hidden}
.bar{display:block;height:100%;width:0;background:linear-gradient(90deg,#75B9DC,#978DE0);border-radius:999px;transition:width .12s linear}
.circle.busy{pointer-events:none;background:linear-gradient(145deg,#F3FAFD,#F5F2FC)}
.circle.done{background:linear-gradient(145deg,#EAF7FE,#F0ECFF);border-color:#C3DBEA;color:#55758A}
.circle.done .icon{color:#718FD0}
.error{color:#B42318}
@media(max-width:600px){.wrap{height:286px}.circle{width:208px;height:208px}.icon{font-size:54px}.label{width:144px;font-size:16px}}
</style></head><body>
<div class="wrap">
<input id="pick" type="file" accept="video/mp4,video/quicktime,video/x-matroska,.mp4,.mov,.mkv">
<label class="circle" id="circle" for="pick"><span class="icon" id="icon">⇧</span><span class="label" id="label">Carica il tuo video</span></label>
<div class="status" id="status"><span id="statusText">Caricamento video… 0%</span><span class="track"><span class="bar" id="bar"></span></span></div>
</div>
<script>
const pick=document.getElementById('pick');
const circle=document.getElementById('circle');
const icon=document.getElementById('icon');
const label=document.getElementById('label');
const status=document.getElementById('status');
const statusText=document.getElementById('statusText');
const bar=document.getElementById('bar');
const CHUNK=16*1024*1024;
const CONCURRENCY=6;

function uploadChunk(blob,meta,onProgress){
  return new Promise((resolve,reject)=>{
    const xhr=new XMLHttpRequest();
    xhr.open('PUT','/direct-upload/chunk',true);
    xhr.setRequestHeader('Content-Type','application/octet-stream');
    xhr.setRequestHeader('X-GSF-Upload-ID',meta.id);
    xhr.setRequestHeader('X-GSF-Filename',encodeURIComponent(meta.name));
    xhr.setRequestHeader('X-GSF-File-Size',String(meta.size));
    xhr.setRequestHeader('X-GSF-Chunk-Start',String(meta.start));
    xhr.setRequestHeader('X-GSF-Chunk-Index',String(meta.index));
    xhr.setRequestHeader('X-GSF-Chunk-Count',String(meta.count));
    xhr.upload.onprogress=(e)=>{if(e.lengthComputable) onProgress(e.loaded);};
    xhr.onload=()=>{
      if(xhr.status>=200 && xhr.status<300) resolve(xhr.responseText);
      else reject(new Error('HTTP '+xhr.status));
    };
    xhr.onerror=()=>reject(new Error('Errore di rete'));
    xhr.ontimeout=()=>reject(new Error('Timeout'));
    xhr.timeout=180000;
    xhr.send(blob);
  });
}


async function uploadChunkWithRetry(blob,meta,onProgress,maxAttempts=3){
  let lastError=null;
  for(let attempt=1;attempt<=maxAttempts;attempt++){
    try{
      return await uploadChunk(blob,meta,onProgress);
    }catch(err){
      lastError=err;
      onProgress(0);
      if(attempt<maxAttempts){
        await new Promise(resolve=>setTimeout(resolve,400*attempt));
      }
    }
  }
  throw lastError || new Error('Upload interrotto');
}


async function gsfUploadCapabilities(){
  try{
    const r=await fetch('/direct-upload/capabilities',{cache:'no-store'});
    if(!r.ok)return {bucket:false};
    return await r.json();
  }catch(e){
    return {bucket:false};
  }
}

function gsfPutPresigned(url,blob,onProgress){
  return new Promise((resolve,reject)=>{
    const xhr=new XMLHttpRequest();
    xhr.open('PUT',url,true);
    xhr.upload.onprogress=(e)=>{if(e.lengthComputable)onProgress(e.loaded);};
    xhr.onload=()=>{
      if(xhr.status>=200 && xhr.status<300){
        const etag=xhr.getResponseHeader('ETag')||xhr.getResponseHeader('etag');
        if(!etag)reject(new Error('ETag non disponibile'));
        else resolve(etag);
      }else reject(new Error('Bucket HTTP '+xhr.status));
    };
    xhr.onerror=()=>reject(new Error('Errore rete bucket'));
    xhr.ontimeout=()=>reject(new Error('Timeout bucket'));
    xhr.timeout=240000;
    xhr.send(blob);
  });
}

async function gsfPutPresignedRetry(url,blob,onProgress,maxAttempts=3){
  let lastError=null;
  for(let attempt=1;attempt<=maxAttempts;attempt++){
    try{
      return await gsfPutPresigned(url,blob,onProgress);
    }catch(err){
      lastError=err;
      onProgress(0);
      if(attempt<maxAttempts){
        await new Promise(resolve=>setTimeout(resolve,450*attempt));
      }
    }
  }
  throw lastError||new Error('Upload bucket interrotto');
}

async function gsfBucketUpload(file,caps){
  const initResp=await fetch('/direct-upload/bucket/init',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      name:file.name,
      size:file.size,
      type:file.type||'application/octet-stream'
    })
  });
  const init=await initResp.json();
  if(!initResp.ok||!init.ok)throw new Error(init.error||'Impossibile inizializzare bucket');

  const partSize=Number(init.part_size||caps.part_size||32*1024*1024);
  const concurrency=Math.max(1,Number(init.concurrency||caps.concurrency||6));
  const descriptors=Array.isArray(init.parts)?init.parts:[];
  let next=0;
  let completedBytes=0;
  const live=new Map();
  const results=[];

  const update=()=>{
    let inflight=0;
    for(const value of live.values())inflight+=value;
    const pct=Math.min(99,Math.round(((completedBytes+inflight)/file.size)*100));
    bar.style.width=pct+'%';
    statusText.textContent='Upload diretto… '+pct+'%';
  };

  const worker=async()=>{
    while(true){
      const idx=next++;
      if(idx>=descriptors.length)return;
      const desc=descriptors[idx];
      const start=idx*partSize;
      const end=Math.min(file.size,start+partSize);
      const blob=file.slice(start,end);
      live.set(idx,0);
      const etag=await gsfPutPresignedRetry(desc.url,blob,(sent)=>{
        live.set(idx,sent);
        update();
      });
      live.delete(idx);
      completedBytes+=end-start;
      results[idx]={PartNumber:Number(desc.number),ETag:etag};
      update();
    }
  };

  try{
    await Promise.all(
      Array.from({length:Math.min(concurrency,descriptors.length)},()=>worker())
    );
    bar.style.width='100%';
    statusText.textContent='Preparazione video…';

    const doneResp=await fetch('/direct-upload/bucket/complete',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        upload_id:init.upload_id,
        multipart_id:init.multipart_id,
        key:init.key,
        analysis_key:init.analysis_key,
        name:file.name,
        size:file.size,
        parts:results
      })
    });
    const done=await doneResp.json();
    if(!doneResp.ok||!done.ok)throw new Error(done.error||'Finalizzazione bucket fallita');

    const deadline=Date.now()+300000;
    while(Date.now()<deadline){
      const sr=await fetch('/direct-upload/bucket/status?upload_id='+encodeURIComponent(init.upload_id),{cache:'no-store'});
      const st=await sr.json();
      if(sr.ok&&st.ready)return true;
      if(!sr.ok&&st.error)throw new Error(st.error);
      await new Promise(resolve=>setTimeout(resolve,500));
    }
    throw new Error('Preparazione video troppo lunga');
  }catch(err){
    try{
      await fetch('/direct-upload/bucket/abort',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          upload_id:init.upload_id,
          multipart_id:init.multipart_id,
          key:init.key
        })
      });
    }catch(e){}
    throw err;
  }
}

pick.addEventListener('change',async()=>{
  const file=pick.files && pick.files[0];
  if(!file)return;
  const ext=(file.name.split('.').pop()||'').toLowerCase();
  if(!['mp4','mov','mkv'].includes(ext)){
    status.style.display='block';status.classList.add('error');statusText.textContent='Formato non supportato';return;
  }
  const count=Math.ceil(file.size/CHUNK);
  const id=Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,12);
  circle.classList.add('busy');
  status.classList.remove('error');
  status.style.display='block';
  label.textContent='Caricamento…';
  try{
    const caps=await gsfUploadCapabilities();
    if(caps && caps.bucket===true){
      await gsfBucketUpload(file,caps);
      bar.style.width='100%';
      statusText.textContent='Video caricato';
      circle.classList.remove('busy');
      circle.classList.add('done');
      icon.textContent='✓';
      label.textContent='Video caricato';
      return;
    }

    let nextIndex=0;
    let completedBytes=0;
    const liveBytes=new Map();

    const updateProgress=()=>{
      let inflight=0;
      for(const value of liveBytes.values()) inflight+=value;
      const pct=Math.min(99,Math.round(((completedBytes+inflight)/file.size)*100));
      bar.style.width=pct+'%';
      statusText.textContent='Caricamento video… '+pct+'%';
    };

    const worker=async()=>{
      while(true){
        const i=nextIndex++;
        if(i>=count)return;
        const start=i*CHUNK;
        const end=Math.min(file.size,start+CHUNK);
        const blob=file.slice(start,end);
        liveBytes.set(i,0);
        await uploadChunkWithRetry(blob,{id,name:file.name,size:file.size,start,index:i,count},(sent)=>{
          liveBytes.set(i,sent);
          updateProgress();
        });
        liveBytes.delete(i);
        completedBytes+=end-start;
        updateProgress();
      }
    };

    await Promise.all(
      Array.from({length:Math.min(CONCURRENCY,count)},()=>worker())
    );

    bar.style.width='100%';
    statusText.textContent='Video caricato';
    circle.classList.remove('busy');
    circle.classList.add('done');
    icon.textContent='✓';
    label.textContent='Video caricato';
    // No browser refresh: the Streamlit fragment watcher sees the disk marker
    // and reruns the app internally without reloading the page.
  }catch(err){
    circle.classList.remove('busy');
    status.classList.add('error');
    statusText.textContent='Upload interrotto — riprova';
    label.textContent='Carica il tuo video';
    bar.style.width='0';
  }
});
</script></body></html>
"""


_gsf_direct_source,_gsf_direct_name=(None,"")
if GSF_WEB_MODE:
    _gsf_direct_source,_gsf_direct_name=_gsf_v989_direct_ready()

_gsf_recovered_source=None
video=None
if _gsf_direct_source is not None:
    _gsf_recovered_source=_gsf_direct_source
    video=_GSFRecoveredUpload(_gsf_direct_source,_gsf_direct_name or _gsf_direct_source.name)
    st.session_state["gsf_source_path"]=str(_gsf_direct_source)
    st.session_state["gsf_source_name"]=_gsf_direct_name or _gsf_direct_source.name
elif GSF_WEB_MODE:
    _gsf_recovered_source=_gsf_find_recovered_source()
    if _gsf_recovered_source is not None:
        video=_GSFRecoveredUpload(
            _gsf_recovered_source,
            st.session_state.get("gsf_source_name",_gsf_recovered_source.name)
        )
        st.session_state["gsf_source_path"]=str(_gsf_recovered_source)

with st.container(key="v73-upload-shell"):
    if GSF_WEB_MODE:
        components.html(
            _gsf_v989_direct_upload_html(video is not None),
            height=288 if video is not None else 308,
            scrolling=False
        )
    else:
        video=st.file_uploader(
            "Carica il tuo video",
            type=["mp4","mov","mkv"],
            label_visibility="collapsed",
            key="upload_v73"
        )
        st.markdown(_gsf_v89_upload_visual_html(video is not None),unsafe_allow_html=True)

if GSF_WEB_MODE and video is None:
    @st.fragment(run_every="0.35s")
    def _gsf_v989_direct_upload_watch():
        _ready,_name=_gsf_v989_direct_ready()
        if _ready is not None:
            st.rerun()
    _gsf_v989_direct_upload_watch()
if video is not None:
    _gsf_has_active_video=(
        _gsf_recovered_source is not None
        or bool(st.session_state.get("gsf_source_path"))
        or (not GSF_WEB_MODE and st.session_state.get("upload_v73") is not None)
    )
    if _gsf_has_active_video:
        _nv_left,_nv_center,_nv_right=st.columns([1,1,1])
        with _nv_center:
            st.button(
                "＋ NUOVO VIDEO",
                use_container_width=True,
                key="v81_new_video",
                on_click=_gsf_start_new_video,
                help="Azzera questa lavorazione e prepara l'upload di un nuovo video."
            )
st.markdown('<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>', unsafe_allow_html=True)



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
    return hashlib.md5(raw.encode("utf-8"), usedforsecurity=False).hexdigest()[:10]


# ==========================================================
# V25 — PERSISTENT LIVE PLAYER (Streamlit Components V2)
# ==========================================================
_GSF_LIVE_V2 = None
def _gsf_pan_translate(zoom, position):
    """Match the final FFmpeg crop: no movement without zoom, positive pans right."""
    return -max(0.0,float(zoom)-1.0)*float(position)/2.0

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
          const tx = Number(d.panX ?? 0);
          const ty = Number(d.panY ?? 0);
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
        _legacy_seek=float(seek_target if seek_target is not None else start_seconds)
        return _render_gsf_editor_live_player_legacy(
            source_path,key,_legacy_seek,fmt,zoom,x_pos,y_pos,volume,brightness,contrast,speed,
            subtitles_on,subtitle_style,subtitle_size,subtitle_position,subtitle_words,subtitle_text,
            subtitle_font,subtitle_x,subtitle_y
        )

    served_name,_=_gsf_serve_path(source_path, _gsf_v72_unique_media_key(source_path, "persistent"))
    url=_gsf_media_url(served_name)
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
            "zoom":float(zoom),
            "panX":_gsf_pan_translate(zoom,x_pos),
            "panY":_gsf_pan_translate(zoom,y_pos),
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
    url=_gsf_media_url(served_name)
    start_seconds=max(0.0,float(start_seconds))
    vertical=(fmt=="9:16 Short")
    frame_w,frame_h,iframe_h=((220,391,424) if vertical else (520,293,332))
    zoom=float(zoom); x_pos=float(x_pos); y_pos=float(y_pos)
    vol=max(0.0,min(1.0,float(volume)/100.0))
    bri=max(0.0,1.0+float(brightness))
    con=max(0.0,float(contrast)); speed=float(speed)
    tx=_gsf_pan_translate(zoom,x_pos)
    ty=_gsf_pan_translate(zoom,y_pos)

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
      margin:10px auto 12px auto;overflow:hidden;border-radius:20px;background:#000;
      box-shadow:0 0 0 9px #F8FCFF,0 0 0 10px #D4E4EF,
                 0 14px 34px rgba(16,40,61,.14)}}
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
    temp_dir=str(GSF_SESSION_TMP_DIR / "gsf_editor_subs")
    os.makedirs(temp_dir,exist_ok=True)
    token=hashlib.md5(f"{source_path}|{start_seconds:.2f}|{duration_seconds:.2f}".encode(), usedforsecurity=False).hexdigest()[:12]
    wav=os.path.join(temp_dir,f"{token}.wav")
    cmd=[
        FFMPEG_PATH,"-y","-ss",str(float(start_seconds)),"-i",str(source_path),
        "-t",str(float(duration_seconds)),"-vn","-ac","1","-ar","16000",
        "-af","highpass=f=70,lowpass=f=7800,loudnorm=I=-16:LRA=11:TP=-1.5",
        wav
    ]
    try:
        run=subprocess.run(
            cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
            timeout=max(120.0,float(duration_seconds)*10.0)
        )
        if run.returncode!=0 or not os.path.exists(wav):
            return [], "Estrazione audio non riuscita"
        model=_gsf_subtitle_whisper_model()
        segs,info=model.transcribe(
            wav,
            language="it",
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
    finally:
        try:
            os.unlink(wav)
        except OSError:
            pass



def _gsf_transcribe_editor_scene_lowmem(*args, **kwargs):
    """V80.2: release cached Whisper RAM before FFmpeg rendering."""
    try:
        return _gsf_transcribe_editor_scene(*args, **kwargs)
    finally:
        if GSF_LOW_MEMORY_WEB:
            try:
                _gsf_subtitle_whisper_model.clear()
            except Exception:
                pass
            try:
                import gc
                gc.collect()
            except Exception:
                pass

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

    # V50: una sola sorgente locale per TUTTO il progetto.
    # Niente più copie integrali separate per player/AI/editor/batch/render.
    with st.spinner("Preparo il gameplay..." if not st.session_state.get("gsf_source_path") else "Carico gameplay..."):
        _source_path,_video_cache_token,_source_reused,_source_perf = (
            _gsf_materialize_upload_once(video)
        )
    _preview_path=Path(_source_path)
    _safe_name=_preview_path.name

    # PLAYER HTML5 ADATTIVO DEFINITIVO
    st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("play", "Anteprima video", "blue") + '</div>', unsafe_allow_html=True)

    _pw,_ph,_rotation,_probe_error=_gsf_probe_display_size(_preview_path)
    if _probe_error:
        st.error(f"⚠️ Impossibile leggere il formato video: {_probe_error}")
    else:
        _vertical=_ph>_pw
        if _vertical:
            _profile="PLAYER 9:16"; _target_width=300; _max_vw="300px"; _cap=680
        else:
            _profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430

        _target_height=round(_target_width*_ph/_pw)
        _video_url=_gsf_media_url(_gsf_media_relative(_preview_path))

        _html=f"""
        <!doctype html><html><head><meta charset="utf-8"><style>
        html,body{{margin:0;padding:0;background:transparent;overflow:hidden}}
        .wrap{{width:fit-content;max-width:100%;margin:0 auto;
        display:flex;justify-content:center;align-items:flex-start;
        padding:12px;box-sizing:border-box;
        border:1px solid #D4E4EF;border-radius:24px;
        background:linear-gradient(180deg,#FFFFFF 0%,#F8FCFF 100%);
        box-shadow:0 12px 28px rgba(28,78,112,.09)}}
        video{{display:block;width:{_target_width}px;max-width:min({_max_vw},100%);height:auto;
        margin-left:auto;margin-right:auto;
        object-fit:contain;border-radius:18px;background:#000;
        box-shadow:0 14px 34px rgba(16,40,61,.14)}}
        </style></head><body><div class="wrap">
        <video controls preload="metadata" playsinline><source src="{_video_url}"></video>
        </div></body></html>
        """
        components.html(_html,height=min(_target_height+30,_cap),scrolling=False)

    st.divider()
    st.markdown('<div class="gsf-icon-title">Come vuoi creare?</div>', unsafe_allow_html=True)

    _v69_engine_ids = ("🚀 AUTO TOTALE", "🎬 AI Director", "🧠 Smart Clip", "🤖 Auto Clip", "✋ Manuale")
    _v69_engine_names = ("Automatico", "Momento migliore", "Più azione", "Reazioni", "Scegli scena")
    if st.session_state.get("modalita_gsf") not in _v69_engine_ids:
        st.session_state["modalita_gsf"] = _v69_engine_ids[0]
    with st.container(key="v69_engine_grid"):
        _v69_cols = st.columns(5, gap="medium")
        for _index, (_col, _engine_id, _name) in enumerate(zip(_v69_cols, _v69_engine_ids, _v69_engine_names)):
            with _col, st.container(key=f"v69_engine_{_index}"):
                st.button(
                    _name, key=f"v69_choose_{_index}",
                    type="primary" if st.session_state["modalita_gsf"] == _engine_id else "secondary",
                    use_container_width=True, on_click=_gsf_v69_select_engine, args=(_index,),
                    help="Seleziona " + _name
                )
    _pending_engine = st.session_state.get("gsf_pending_engine_switch_v75")
    if _pending_engine in _v69_engine_ids and _pending_engine != st.session_state.get("modalita_gsf"):
        _pending_name = GSF_ENGINE_NAMES_V75.get(_pending_engine, _pending_engine)
        st.warning(f"Cambiare motore in **{_pending_name}** e scartare la lavorazione corrente?")
        _switch_yes, _switch_no = st.columns(2)
        with _switch_yes:
            st.button(
                "CAMBIA MOTORE",
                type="primary",
                use_container_width=True,
                key="v75_confirm_engine_switch",
                on_click=_gsf_v75_confirm_engine_switch,
            )
        with _switch_no:
            st.button(
                "CONTINUA QUI",
                use_container_width=True,
                key="v75_cancel_engine_switch",
                on_click=_gsf_v75_cancel_engine_switch,
            )

    modalita = st.session_state["modalita_gsf"]

    # Spiegazione compatta del motore selezionato, vicino a Durata.
    _engine_help = {
        "🚀 AUTO TOTALE": "Automatico: analizza tutto il gameplay combinando azione, movimento, audio, voce/reazioni, cambi di scena e parti morte. Alla fine propone i 3 momenti con il punteggio complessivo migliore.",
        "🎬 AI Director": "Momento migliore: cerca i picchi più interessanti e completi bilanciando evento, ritmo e audio. Alla fine propone i 3 momenti migliori secondo questo criterio.",
        "🧠 Smart Clip": "Più azione: privilegia movimento, combattimenti, cambi rapidi, eventi intensi e picchi visivi, penalizzando attese e parti statiche. Alla fine propone le 3 scene con più azione.",
        "🤖 Auto Clip": "Reazioni: privilegia voce, urla, risate, esclamazioni e picchi audio collegandoli al gameplay. Alla fine propone i 3 momenti con le reazioni più interessanti.",
        "✋ Manuale": "Scegli scena: qui l’AI non crea 3 proposte. Selezioni tu IN/OUT e lavori direttamente sulla scena nel player LIVE."
    }
    st.caption(_engine_help.get(modalita, ""))

    st.markdown('<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>', unsafe_allow_html=True)

    # Prima dell'analisi scegliamo solo la durata. I sottotitoli si decidono DOPO aver scelto una clip.
    st.session_state.setdefault("gsf_duration_preset", "15s")
    st.markdown('<div class="v70-duration-title">Scegli la durata</div>', unsafe_allow_html=True)
    st.markdown('<div class="v70-duration-sub">La stessa durata verrà applicata alle tre proposte AI.</div>', unsafe_allow_html=True)
    st.markdown("""<style>
.st-key-v73-duration{--duration-size:clamp(112px,31vw,144px)}
.st-key-v73-duration [data-testid="stHorizontalBlock"]{
  display:grid !important; grid-template-columns:repeat(2,var(--duration-size)) !important;
  justify-content:center !important; align-items:start !important;
  gap:24px !important; width:100% !important;
}
.st-key-v73-duration [data-testid="stColumn"],
.st-key-v73-duration [data-testid="column"]{
  width:var(--duration-size) !important; max-width:var(--duration-size) !important;
  min-width:0 !important;
}
.st-key-v73-duration button{
  width:var(--duration-size) !important; max-width:none !important;
  height:var(--duration-size) !important; min-height:var(--duration-size) !important;
  border-radius:50% !important;
}
.st-key-v73-duration button::before,.st-key-v73-duration button::after{
  content:none !important; display:none !important;
}
</style>""", unsafe_allow_html=True)
    with st.container(key="v73-duration"):
        _duration_cols = st.columns(2, gap="small")
        for _duration_col, _duration_label in zip(_duration_cols, ("15s", "30s")):
            with _duration_col:
                st.button(
                    _duration_label,
                    key="v70_duration_" + _duration_label,
                    type=("primary" if st.session_state["gsf_duration_preset"] == _duration_label else "secondary"),
                    use_container_width=True,
                    on_click=_gsf_v70_select_duration,
                    args=(_duration_label,),
                    help="Short da " + _duration_label,
                )
    preset_durata = st.session_state["gsf_duration_preset"]
    duration = float(preset_durata.replace("s", ""))

    # V53: nessuna UI social prima del video finale.
    st.session_state.setdefault("piattaforma","YouTube Shorts")
    st.session_state.setdefault("tono_social","Gaming forte")
    st.session_state.setdefault("gioco","ARC Raiders")


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
                editor_dir = _gsf_session_mkdtemp("gsf_editor_")
                editor_input = str(_source_path)
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
        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("edit", "Editor", "rose") + '</div>', unsafe_allow_html=True)
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
        pass  # V69: no overlapping timeline guide
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

        # V76: rimosse le 3 nuvole IN / OUT / DURATA nella modalità Scegli scena.

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
        studio_player, studio_side = st.columns(
            [.40,.60] if editor_format=="16:9 Originale" else [.22,.78],
            gap="medium"
        )

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
                st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("edit", "Strumenti", "amber") + '</div>', unsafe_allow_html=True)
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
                with st.popover("INQUADRATURA",use_container_width=True):
                    editor_zoom=st.slider("Zoom",1.0,2.0,float(st.session_state.get("editor_zoom",1.0)),.05,key="editor_zoom")
                    editor_x=st.slider("↔ X",-100,100,int(st.session_state.get("editor_x",0)),5,key="editor_x")
                    editor_y=st.slider("↕ Y",-100,100,int(st.session_state.get("editor_y",0)),5,key="editor_y")
            with _regc:
                with st.popover("REGOLAZIONI",use_container_width=True):
                    editor_extra_tool=st.selectbox("Parametro",["Volume","Velocità","Luminosità","Contrasto"],key="editor_extra_tool")
                    if editor_extra_tool=="Volume":
                        editor_volume=st.slider("Volume",0,200,int(st.session_state.get("editor_volume",100)),5,key="editor_volume")
                    elif editor_extra_tool=="Velocità":
                        editor_speed=st.select_slider("Velocità",options=[.5,.75,1.0,1.25,1.5,2.0],value=float(st.session_state.get("editor_speed",1.0)),key="editor_speed")
                    elif editor_extra_tool=="Luminosità":
                        editor_brightness=st.slider("Luminosità",-.30,.30,float(st.session_state.get("editor_brightness",0.0)),.05,key="editor_brightness")
                    else:
                        editor_contrast=st.slider("Contrasto",.70,1.50,float(st.session_state.get("editor_contrast",1.0)),.05,key="editor_contrast")

            st.markdown('<div class="gsf-icon-title gsf-subtitles-title">' + _gsf_v67_badge("text", "Sottotitoli", "lilac") + '</div>', unsafe_allow_html=True)
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

            # V80: "Automatici" significa davvero automatici.
            # La scena viene trascritta una volta per sorgente + IN/OUT e le parole
            # reali vengono mostrate subito nel player. Zoom/colori/strumenti non
            # rilanciano Whisper perché il token della scena resta invariato.
            if editor_sub_mode=="Automatici":
                _auto_sub_token=hashlib.sha256(
                    (
                        f"{editor_input}|{float(editor_start):.3f}|"
                        f"{float(editor_len):.3f}|v80-auto"
                    ).encode("utf-8")
                ).hexdigest()[:24]

                if st.session_state.get("editor_auto_sub_scene_token") != _auto_sub_token:
                    with st.spinner("Trascrizione automatica della scena..."):
                        _auto_words,_auto_err=_gsf_transcribe_editor_scene_lowmem(
                            editor_input,editor_start,editor_len
                        )

                    st.session_state["editor_auto_sub_scene_token"]=_auto_sub_token
                    st.session_state["editor_auto_sub_error"]=str(_auto_err or "")

                    if _auto_err:
                        st.session_state["editor_sub_words"]=[]
                        st.session_state["editor_sub_live_words"]=[]
                        st.session_state["editor_sub_text"]=""
                    else:
                        _auto_words=list(_auto_words or [])
                        _auto_text=" ".join(
                            str(w.get("text","")).strip()
                            for w in _auto_words
                            if str(w.get("text","")).strip()
                        )
                        st.session_state["editor_sub_words"]=_auto_words
                        st.session_state["editor_sub_live_words"]=_auto_words
                        st.session_state["editor_sub_text"]=_auto_text
                        st.session_state["editor_sub_applied_text"]=_auto_text
                        st.session_state["editor_sub_seek"]=float(editor_start)
                        st.session_state["editor_sub_seek_feedback"]=float(editor_start)
                        try:
                            _gsf_save_persistent_state()
                        except Exception:
                            pass
                        st.rerun()

                _auto_sub_error=st.session_state.get("editor_auto_sub_error","")
                if _auto_sub_error:
                    st.warning(
                        "Trascrizione automatica non riuscita: "
                        + str(_auto_sub_error)
                    )
                    if st.button(
                        "RIPROVA TRASCRIZIONE",
                        use_container_width=True,
                        key="retry_auto_sub_v80"
                    ):
                        st.session_state.pop("editor_auto_sub_scene_token",None)
                        st.session_state.pop("editor_auto_sub_error",None)
                        st.rerun()
                elif st.session_state.get("editor_sub_live_words"):
                    st.caption(
                        "Trascrizione automatica pronta · "
                        f"{len(st.session_state.get('editor_sub_live_words',[]))} parole"
                    )

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
                    with st.popover("POSIZIONE",use_container_width=True):
                        st.slider("↔ X",5,95,int(st.session_state.get("subtitle_x_v18",st.session_state.get("subtitle_x",50))),1,key="subtitle_x_v18")
                        st.slider("↕ Y",5,95,int(st.session_state.get("subtitle_y_v18",st.session_state.get("subtitle_y",78))),1,key="subtitle_y_v18")
                st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("intelligence", "Trascrizione intelligente", "mint") + '</div>', unsafe_allow_html=True, help="La trascrizione resta salvata mentre modifichi font, colori, posizione o gli strumenti.")
                if not st.session_state.get("editor_sub_words"):
                    if st.button("TRASCRIVI LA SCENA",use_container_width=True,key="editor_transcribe_scene_v18"):
                        with st.spinner("Trascrivo la scena..."):
                            words,err=_gsf_transcribe_editor_scene_lowmem(editor_input,editor_start,editor_len)
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

        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("choose", "Modifiche", "amber") + '</div>', unsafe_allow_html=True)
        _main_sub_mode=st.session_state.get(
            "editor_sub_mode","Automatici"
        )
        _main_sub_words=(
            st.session_state.get(
                "editor_sub_live_words",
                st.session_state.get("editor_sub_words",[])
            )
            if _main_sub_mode in ("Manuali","Automatici") else []
        )

        _main_recipe=_gsf_recipe_selected(
            "main_editor",
            editor_start,
            editor_len,
            editor_input,
            render_kwargs={
                "fmt":editor_format,
                "zoom":editor_zoom,
                "x_pos":editor_x,
                "y_pos":editor_y,
                "brightness":editor_brightness,
                "contrast":editor_contrast,
                "speed":editor_speed,
                "volume":editor_volume,
                "subtitles_enabled":(_main_sub_mode!="Nessuno"),
                # Automatici V80 ha già parole temporizzate: al renderer passa
                # come trascrizione pronta, evitando un secondo download/modello.
                "subtitle_mode":(
                    "Manuali"
                    if _main_sub_mode=="Automatici" and _main_sub_words
                    else _main_sub_mode
                ),
                "subtitle_words":_main_sub_words,
                "subtitle_text":st.session_state.get(
                    "editor_sub_text",""
                ),
                "subtitle_time_origin":editor_start,
                "subtitle_font":st.session_state.get(
                    "editor_sub_font_v18",
                    st.session_state.get("subtitle_font","Arial")
                ),
                "subtitle_size":st.session_state.get(
                    "editor_sub_size_v18",
                    st.session_state.get("editor_sub_size",92)
                ),
                "subtitle_x":st.session_state.get(
                    "subtitle_x_v18",
                    st.session_state.get("subtitle_x",50)
                ),
                "subtitle_y":st.session_state.get(
                    "subtitle_y_v18",
                    st.session_state.get("subtitle_y",78)
                ),
                "text_color":st.session_state.get(
                    "subtitle_text_color_v18","#FFFFFF"
                ),
                "active_color":st.session_state.get(
                    "subtitle_active_color_v18","#FFD400"
                ),
                "outline_color":st.session_state.get(
                    "subtitle_outline_color_v18","#000000"
                ),
                "normalize_audio":True,
                "smart_reframe":False,
                "hook_text":"",
                "polish_audio":True,
            }
        )
        _main_recipe_token=_gsf_recipe_token(_main_recipe)
        _saved_main_recipe=st.session_state.get(
            "gsf_final_recipe",{}
        )
        _main_recipe_selected=bool(
            _saved_main_recipe.get("kind")=="main_editor"
            and _gsf_recipe_token(_saved_main_recipe)==_main_recipe_token
        )

        if st.button(
            (
                "✅ MODIFICHE SELEZIONATE"
                if _main_recipe_selected
                else "✓ USA QUESTE MODIFICHE"
            ),
            type="primary",
            use_container_width=True,
            key="editor_use_changes_v54",
            disabled=_main_recipe_selected
        ):
            _gsf_set_final_recipe(
                _main_recipe,
                source_label="Editor"
            )
            st.session_state["auto_clip_scelta"]=float(editor_start)
            st.session_state["auto_clip_duration"]=float(editor_len)
            _main_recipe_selected=True

        if _main_recipe_selected:
            st.caption(
                "Queste modifiche verranno applicate quando premi "
                "CREA SHORT FINALE in fondo."
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

        if st.button("CREA CON AI", use_container_width=True):
            _gsf_save_persistent_state()
            with _gsf_session_tempdir("gsf_analysis_") as analisi_temp:
                analisi_input = str(_source_path)

                if modalita == "🚀 AUTO TOTALE":
                    messaggio = "✨ Scansione completa → azione, audio, voce e tempi morti..."
                elif modalita == "🎬 AI Director":
                    messaggio = "🎬 Cerco costruzione, picco e chiusura dei momenti..."
                elif modalita == "🧠 Smart Clip":
                    messaggio = "🔥 Cerco movimento, combattimenti e attività sostenuta..."
                else:
                    messaggio = "🎙️ Cerco voce, reazioni e picchi collegati al gameplay..."

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
                                nuova_durata=float(duration)
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
            risultati_ai = st.session_state.get("ai_director_scores", [])
            _short_cards = _gsf_v70_build_short_cards(
                risultati_ai,
                candidati,
                duration,
                st.session_state.get("gsf_ai_v3_diagnostics", {}),
            )
            if _short_cards:
                st.markdown('<div class="v70-short-heading">Scegli il tuo momento</div>', unsafe_allow_html=True)
                st.markdown('<div class="v70-short-sub">Riproduci le tre anteprime direttamente qui e scegli il momento migliore.</div>', unsafe_allow_html=True)

                for _card in _short_cards:
                    _card_duration = float(duration)
                    if modalita in ["🚀 AUTO TOTALE", "🎬 AI Director"]:
                        _card_duration = float(
                            st.session_state.get("clip_rifinite", {}).get(
                                round(float(_card["start"]), 3),
                                duration,
                            )
                        )
                    _card["preview_duration"] = _card_duration
                    _card["end"] = float(_card["start"]) + _card_duration

                _current_start = st.session_state.get("auto_clip_scelta")
                if _current_start is None or not any(
                    abs(float(card["start"]) - float(_current_start)) < 0.05
                    for card in _short_cards
                ):
                    _current_start = float(_short_cards[0]["start"])
                    st.session_state.auto_clip_scelta = _current_start

                _mini_preview_cache = st.session_state.setdefault(
                    "gsf_ai_preview_cache_v71", {}
                )
                _mini_preview_bytes = {}
                with st.spinner("Preparo le tre anteprime leggere..."):
                    for _card in _short_cards:
                        _mini_key = (
                            _video_cache_token,
                            round(float(_card["start"]), 2),
                            round(float(_card["preview_duration"]), 2),
                        )

                        def _make_mini_preview(
                            _card=_card,
                            _duration=float(_card["preview_duration"]),
                        ):
                            with _gsf_session_tempdir("gsf_preview_") as _preview_temp:
                                _preview_output = os.path.join(
                                    _preview_temp,
                                    f"mini_{int(_card['index'])}.mp4",
                                )
                                if crea_anteprima(
                                    str(_source_path),
                                    _preview_output,
                                    float(_card["start"]),
                                    _duration,
                                ):
                                    return Path(_preview_output).read_bytes()
                            return None

                        _mini_bytes = _gsf_preview_cache_get(
                            _mini_preview_cache,
                            _mini_key,
                            _make_mini_preview,
                            max_items=3,
                        )
                        if _mini_bytes:
                            _mini_preview_bytes[int(_card["index"])] = bytes(_mini_bytes)

                _selected_card = next(
                    (
                        card for card in _short_cards
                        if abs(float(card["start"]) - float(_current_start)) < 0.05
                    ),
                    _short_cards[0],
                )
                _selected_preview_bytes = _mini_preview_bytes.get(
                    int(_selected_card["index"])
                )
                st.session_state["preview_bytes"] = _selected_preview_bytes
                st.session_state["preview_key"] = (
                    (
                        _video_cache_token,
                        round(float(_selected_card["start"]), 2),
                        round(float(_selected_card["preview_duration"]), 2),
                    )
                    if _selected_preview_bytes else None
                )

                with st.container(key="v71-short-grid"):
                    _short_cols = st.columns(3, gap="large")
                    for _short_col, _card in zip(_short_cols, _short_cards):
                        _is_selected = abs(float(_card["start"]) - float(_current_start)) < 0.05
                        with _short_col, st.container(key=f"v71_short_card_{_card['index']}"):
                            _quality = (
                                f"Qualità {_card['quality']}%"
                                if _card.get("quality") is not None else ""
                            )
                            _card_bytes = _mini_preview_bytes.get(int(_card["index"]))
                            if _card_bytes:
                                _card_path = _gsf_bytes_to_preview(
                                    _card_bytes,
                                    f"v71_mini_{_card['index']}_{_card['start']:.2f}",
                                )
                                _gsf_v71_render_mini_player(
                                    _card_path,
                                    f"v71_mini_{_card['index']}",
                                    f"Short {_card['index']}",
                                )
                            else:
                                st.markdown(
                                    '<div class="v70-short-card-preview"><span class="v70-short-index">ANTEPRIMA NON DISPONIBILE</span></div>',
                                    unsafe_allow_html=True,
                                )
                            st.markdown(
                                f'''<div class="v70-short-card-label">{html.escape(_card["label"])}</div>
                                <div class="v70-short-card-time">{_card["start"]:.0f}s → {_card["end"]:.0f}s · {_card["preview_duration"]:.0f}s</div>
                                {f'<span class="v70-short-card-score">{_quality}</span>' if _quality else ''}''',
                                unsafe_allow_html=True,
                            )
                            if st.button(
                                "✓ SELEZIONATA" if _is_selected else "SCEGLI QUESTO",
                                key=f"v71_choose_short_{_card['index']}",
                                type="primary" if _is_selected else "secondary",
                                use_container_width=True,
                            ):
                                st.session_state.auto_clip_scelta = float(_card["start"])
                                st.session_state["auto_clip_duration"] = float(_card["preview_duration"])
                                st.session_state["preview_key"] = None
                                st.session_state.pop("preview_bytes", None)
                                st.rerun()

                start = float(st.session_state.auto_clip_scelta)

            durata_effettiva = float(duration)

            if modalita in ["🚀 AUTO TOTALE", "🎬 AI Director"]:
                durata_effettiva = float(
                    st.session_state.get(
                        "clip_rifinite",
                        {}
                    ).get(round(start, 3), duration)
                )





            if st.session_state.get("preview_bytes"):
                edit_col, keep_col = st.columns(2)
                with edit_col:
                    if st.button(
                        "MODIFICA NELL’EDITOR",
                        use_container_width=True,
                        key=f"edit_ai_{start:.2f}_{durata_effettiva:.2f}"
                    ):
                        # Apre UNA copia dell'Editor direttamente sotto questa clip.
                        _inline_id=f"{start:.2f}_{durata_effettiva:.2f}"
                        _edit_dir=_gsf_session_mkdtemp("gsf_inline_ai_")
                        _edit_input=os.path.join(_edit_dir,"ai_clip_inline_preview.mp4")
                        _edit_original=str(_source_path)
                        with open(_edit_input,"wb") as _ef:
                            _ef.write(st.session_state.preview_bytes)
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
                    _selected_recipe=st.session_state.get(
                        "gsf_final_recipe",{}
                    )
                    _is_selected_ai=bool(
                        st.session_state.get("publication_ready")
                        and _selected_recipe.get("kind")=="auto"
                        and st.session_state.get("auto_clip_scelta") is not None
                        and abs(
                            float(st.session_state.get("auto_clip_scelta",0.0))
                            -float(start)
                        )<0.05
                    )
                    if st.button(
                        (
                            "✓ SELEZIONATA"
                            if _is_selected_ai
                            else "✓ USA QUESTA"
                        ),
                        use_container_width=True,
                        key=f"use_ai_{start:.2f}_{durata_effettiva:.2f}",
                        disabled=_is_selected_ai
                    ):
                        st.session_state.auto_clip_scelta=float(start)
                        st.session_state["auto_clip_duration"]=float(
                            durata_effettiva
                        )
                        _auto_recipe=_gsf_recipe_selected(
                            "auto",
                            float(start),
                            float(durata_effettiva),
                            str(_source_path),
                            master_token=_gsf_upload_master_token(video),
                            subtitles_enabled=bool(
                                st.session_state.get(
                                    "project_subtitles_enabled",True
                                )
                            ),
                            manual_hook=st.session_state.get(
                                "hook_testo",""
                            )
                        )
                        _gsf_set_final_recipe(
                            _auto_recipe,
                            source_label="AI"
                        )
                        st.session_state[
                            "publication_preview_bytes"
                        ]=st.session_state.get("preview_bytes")
                        st.rerun()


                # ===== EDITOR INLINE DELLA CLIP AI =====
                _this_inline_id=f"{start:.2f}_{durata_effettiva:.2f}"
                if st.session_state.get("inline_editor_id")==_this_inline_id:
                    _ii=st.session_state.get("inline_editor_input")
                    _idir=st.session_state.get("inline_editor_dir")
                    _idur=float(st.session_state.get("inline_editor_duration",durata_effettiva))

                    if _ii and os.path.exists(_ii):
                        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("edit", "Editor", "rose") + '</div>', unsafe_allow_html=True)
                        # Timeline: descrizione sopra, nessuno scroll verso altri editor.
                        pass  # V69: no overlapping timeline guide
                        _trim=st.slider(
                            "IN / OUT · ritaglio scena",0.0,float(max(.5,_idur)),
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

                        _pl,_side=st.columns(
                            [.40,.60] if st.session_state[_fmt_key]=="16:9 Originale" else [.22,.78],
                            gap="medium"
                        )

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
                            _ith,_itr,_itc=st.columns([.50,.25,.25],gap="medium")
                            with _ith:
                                st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("edit", "Strumenti", "amber") + '</div>', unsafe_allow_html=True, help="Regola formato, inquadratura, audio e immagine. Le modifiche sono mostrate nel player LIVE.")
                            with _itr:
                                st.button(
                                    "↶ RESET",use_container_width=True,key=f"reset_inline_all_v29_{_this_inline_id}",
                                    on_click=_gsf_reset_inline_all,
                                    args=(_this_inline_id,_fmt_key,_zoom_key,_x_key,_y_key,_vol_key,_bri_key,_con_key,_spd_key)
                                )
                            with _itc:
                                if st.button("CHIUDI", use_container_width=True, key=f"inline_close_{_this_inline_id}"):
                                    st.session_state.pop("inline_editor_id", None)
                                    st.rerun()
                            _fc,_ic,_rc=st.columns([.34,.33,.33],gap="medium")
                            with _fc:
                                st.session_state[_fmt_key]=st.segmented_control(
                                    "Formato",["9:16 Short","16:9 Originale"],
                                    default=st.session_state[_fmt_key],key=f"inline_fmt_widget_v18_{_this_inline_id}"
                                )
                            with _ic:
                                with st.popover("INQUADRATURA",use_container_width=True):
                                    st.session_state[_zoom_key]=st.slider("Zoom",1.0,2.0,float(st.session_state[_zoom_key]),.05,key=f"inline_zoom_widget_v18_{_this_inline_id}")
                                    st.session_state[_x_key]=st.slider("↔ X",-100,100,int(st.session_state[_x_key]),5,key=f"inline_x_widget_v18_{_this_inline_id}")
                                    st.session_state[_y_key]=st.slider("↕ Y",-100,100,int(st.session_state[_y_key]),5,key=f"inline_y_widget_v18_{_this_inline_id}")
                            with _rc:
                                with st.popover("REGOLAZIONI",use_container_width=True):
                                    _reg=st.selectbox("Parametro",["Volume","Luminosità","Contrasto","Velocità"],key=f"inline_reg_v18_{_this_inline_id}")
                                    if _reg=="Volume":
                                        st.session_state[_vol_key]=st.slider("Volume",0,200,int(st.session_state[_vol_key]),5,key=f"inline_vol_widget_v18_{_this_inline_id}")
                                    elif _reg=="Luminosità":
                                        st.session_state[_bri_key]=st.slider("Luminosità",-.30,.30,float(st.session_state[_bri_key]),.05,key=f"inline_bri_widget_v18_{_this_inline_id}")
                                    elif _reg=="Contrasto":
                                        st.session_state[_con_key]=st.slider("Contrasto",.70,1.50,float(st.session_state[_con_key]),.05,key=f"inline_con_widget_v18_{_this_inline_id}")
                                    else:
                                        st.session_state[_spd_key]=st.select_slider("Velocità",options=[.5,.75,1.0,1.25,1.5,2.0],value=float(st.session_state[_spd_key]),key=f"inline_spd_widget_v18_{_this_inline_id}")

                            st.markdown('<div class="gsf-icon-title gsf-subtitles-title">' + _gsf_v67_badge("text", "Sottotitoli", "lilac") + '</div>', unsafe_allow_html=True, help="Automatici: fa tutto l'AI. Manuali: trascrive la clip e permette di correggere testo e aspetto. Nessuno: video pulito.")
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
                                    with st.popover("POSIZIONE",use_container_width=True):
                                        st.slider("↔ X",5,95,int(st.session_state.get(f"inline_subx_widget_v18_{_this_inline_id}",st.session_state[_sx])),1,key=f"inline_subx_widget_v18_{_this_inline_id}")
                                        st.slider("↕ Y",5,95,int(st.session_state.get(f"inline_suby_widget_v18_{_this_inline_id}",st.session_state[_sy])),1,key=f"inline_suby_widget_v18_{_this_inline_id}")
                                st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("intelligence", "Trascrizione intelligente", "mint") + '</div>', unsafe_allow_html=True, help="Resta salvata mentre modifichi font, colori, posizione o gli strumenti.")
                                if not st.session_state.get(_trans_words_key):
                                    if st.button("TRASCRIVI LA CLIP",use_container_width=True,key=f"inline_transcribe_v18_{_this_inline_id}"):
                                        with st.spinner("Trascrivo la clip..."):
                                            _words,_err=_gsf_transcribe_editor_scene_lowmem(_ii,_istart,_ilen)
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

                        # V54: l'Editor inline salva soltanto la ricetta.
                        # Il render pesante avviene una sola volta, in fondo.
                        _original_source=st.session_state.get(
                            "inline_editor_original_input",_ii
                        )
                        _source_base=float(
                            st.session_state.get(
                                "inline_editor_source_start",0.0
                            )
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
                                st.session_state.get(
                                    _trans_words_key,[]
                                )
                            )
                            if _inline_sub_mode=="Manuali" else []
                        )

                        _inline_recipe=_gsf_recipe_selected(
                            "inline_editor",
                            _render_start,
                            _ilen,
                            _original_source,
                            render_kwargs={
                                "fmt":st.session_state[_fmt_key],
                                "zoom":st.session_state[_zoom_key],
                                "x_pos":st.session_state[_x_key],
                                "y_pos":st.session_state[_y_key],
                                "brightness":st.session_state[_bri_key],
                                "contrast":st.session_state[_con_key],
                                "speed":st.session_state[_spd_key],
                                "volume":st.session_state[_vol_key],
                                "subtitles_enabled":(
                                    _inline_sub_mode!="Nessuno"
                                ),
                                "subtitle_mode":_inline_sub_mode,
                                "subtitle_words":_inline_sub_words,
                                "subtitle_text":st.session_state.get(
                                    _trans_text_key,""
                                ),
                                "subtitle_time_origin":_istart,
                                "subtitle_font":st.session_state.get(
                                    f"inline_font_widget_v18_{_this_inline_id}",
                                    st.session_state.get(
                                        f"inline_font_{_this_inline_id}",
                                        "Arial"
                                    )
                                ),
                                "subtitle_size":st.session_state.get(
                                    f"inline_subsize_widget_v18_{_this_inline_id}",
                                    st.session_state.get(
                                        f"inline_subsize_{_this_inline_id}",
                                        92
                                    )
                                ),
                                "subtitle_x":st.session_state.get(
                                    f"inline_subx_widget_v18_{_this_inline_id}",
                                    50
                                ),
                                "subtitle_y":st.session_state.get(
                                    f"inline_suby_widget_v18_{_this_inline_id}",
                                    78
                                ),
                                "text_color":st.session_state.get(
                                    f"inline_txtcol_v18_{_this_inline_id}",
                                    "#FFFFFF"
                                ),
                                "active_color":st.session_state.get(
                                    f"inline_actcol_v18_{_this_inline_id}",
                                    "#FFD400"
                                ),
                                "outline_color":st.session_state.get(
                                    f"inline_outcol_v18_{_this_inline_id}",
                                    "#000000"
                                ),
                                "normalize_audio":True,
                                "smart_reframe":False,
                                "hook_text":"",
                                "polish_audio":True,
                            }
                        )
                        _inline_recipe_token=_gsf_recipe_token(
                            _inline_recipe
                        )
                        _saved_inline_recipe=st.session_state.get(
                            "gsf_final_recipe",{}
                        )
                        _inline_recipe_selected=bool(
                            _saved_inline_recipe.get("kind")=="inline_editor"
                            and _gsf_recipe_token(
                                _saved_inline_recipe
                            )==_inline_recipe_token
                        )

                        if st.button(
                            (
                                "✅ MODIFICHE SELEZIONATE"
                                if _inline_recipe_selected
                                else "✓ USA QUESTE MODIFICHE"
                            ),
                            type="primary",
                            use_container_width=True,
                            key=f"inline_use_changes_v54_{_this_inline_id}",
                            disabled=_inline_recipe_selected
                        ):
                            _gsf_set_final_recipe(
                                _inline_recipe,
                                source_label="Editor AI"
                            )
                            st.session_state[
                                "auto_clip_scelta"
                            ]=float(_render_start)
                            st.session_state[
                                "auto_clip_duration"
                            ]=float(_ilen)
                            _inline_recipe_selected=True

                        if _inline_recipe_selected:
                            st.caption(
                                "Modifiche pronte. Il render avverrà "
                                "solo con CREA SHORT FINALE."
                            )

        else:
            start = 0.0

    # La clip AI selezionata si finalizza soltanto in fondo.
    _ai_selected_start = st.session_state.get("auto_clip_scelta")

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
    # V54 — BETA FLOW: ONE FINAL RENDER + MINIMAL SOCIAL
    # ==========================================================
    _final_recipe=st.session_state.get("gsf_final_recipe",{}) or {}
    _final_video=st.session_state.get("publication_final_bytes")

    _show_final_flow=bool(
        _final_recipe
        or (
            isinstance(_final_video,(bytes,bytearray))
            and len(_final_video)>1024
        )
    )

    if _show_final_flow:
        st.divider()
        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("play", "Crea lo Short finale", "peach") + '</div>', unsafe_allow_html=True)

        _has_final=bool(
            isinstance(_final_video,(bytes,bytearray))
            and len(_final_video)>1024
        )

        if not _has_final:
            if st.button(
                "CREA SHORT FINALE",
                type="primary",
                use_container_width=True,
                key="create_final_short_v54"
            ):
                _final_dir=_gsf_session_mkdtemp("gsf_final_v54_")
                _final_out=os.path.join(
                    _final_dir,
                    "gaming_short_finale.mp4"
                )

                with st.spinner("🎬 Creo lo Short finale..."):
                    _gsf_v93_release_analysis_memory()
                    _final_result=_gsf_render_final_recipe(
                        _final_recipe,
                        _final_out,
                        video_obj=video
                    )

                if (
                    _final_result.get("ok")
                    and os.path.exists(_final_out)
                    and os.path.getsize(_final_out)>0
                ):
                    if isinstance(
                        _final_result.get("bytes"),
                        (bytes,bytearray)
                    ):
                        _bytes=bytes(_final_result["bytes"])
                    else:
                        with open(_final_out,"rb") as _f:
                            _bytes=_f.read()

                    st.session_state[
                        "publication_final_bytes"
                    ]=_bytes
                    st.session_state[
                        "publication_final_signature"
                    ]=str(
                        _final_result.get("signature")
                        or _gsf_recipe_token(_final_recipe)
                    )
                    st.session_state[
                        "publication_final_encoder"
                    ]=str(_final_result.get("encoder","") or "")
                    st.session_state[
                        "publication_final_seconds"
                    ]=float(_final_result.get("seconds",0) or 0)
                    st.session_state[
                        "publication_source"
                    ]="final_master"
                    st.session_state[
                        "show_social_publish_v54"
                    ]=False
                    st.success("✅ Short finale creato.")
                    shutil.rmtree(_final_dir,ignore_errors=True)
                    st.rerun()
                else:
                    st.error("Creazione Short finale non riuscita.")
                    if _final_result.get("error"):
                        st.code(
                            str(_final_result.get("error",""))[-2500:]
                        )
                    shutil.rmtree(_final_dir,ignore_errors=True)
        else:
            st.success("✅ Short finale pronto")

            _final_sig=str(
                st.session_state.get(
                    "publication_final_signature",""
                ) or ""
            )
            _final_context=(
                f"{_gsf_recipe_token(_final_recipe)}|"
                f"{_final_sig}|{len(_final_video)}"
            )
            if (
                st.session_state.get(
                    "social_final_context_v54"
                )!=_final_context
            ):
                st.session_state[
                    "social_final_context_v54"
                ]=_final_context
                st.session_state[
                    "show_social_publish_v54"
                ]=False
                st.session_state["social_started_v59"]=False
                st.session_state.pop("social_error_v59",None)

            _pub_col,_download_col=st.columns(2,gap="small")

            with _pub_col:
                if st.button(
                    "PUBBLICA",
                    type="primary",
                    use_container_width=True,
                    key="open_publish_v54"
                ):
                    st.session_state[
                        "show_social_publish_v54"
                    ]=not bool(
                        st.session_state.get(
                            "show_social_publish_v54",False
                        )
                    )

            with _download_col:
                st.download_button(
                    "SCARICA",
                    _final_video,
                    "gaming_short_finale.mp4",
                    "video/mp4",
                    use_container_width=True,
                    key="download_final_v54"
                )

            if st.session_state.get("show_social_publish_v54", False):
                st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("publish", "Pubblicazione", "indigo") + '</div>', unsafe_allow_html=True)
                _selected_social = st.session_state.get("social_selected_v59")
                _social_columns = st.columns(3, gap="small")
                for _column, _platform in zip(
                    _social_columns, ("YouTube", "TikTok", "Instagram")
                ):
                    with _column, st.container(key="v69_social_" + _platform.lower()):
                        if st.button(
                            _platform,
                            type=("primary" if _selected_social == _platform else "secondary"),
                            use_container_width=True,
                            key="social_upload_v59_" + _platform.lower(),
                        ):
                            st.session_state["social_selected_v59"] = _platform
                            st.session_state["social_started_v59"] = False
                            st.session_state.pop("social_error_v59", None)
                            st.session_state.pop("social_auth_url_v77", None)
                            st.session_state.pop("social_auth_platform_v77", None)

                            _connected, _connect_error = _gsf_social_connection_status(_platform)
                            if not _connected:
                                if GSF_WEB_MODE:
                                    _auth_url, _auth_error = _gsf_social_web_auth_url(_platform)
                                    _connected, _connect_error = _gsf_social_connection_status(_platform)
                                    if _auth_url:
                                        st.session_state["social_auth_url_v77"] = _auth_url
                                        st.session_state["social_auth_platform_v77"] = _platform
                                        st.session_state["social_error_v59"] = (
                                            "Collega " + _platform + " per pubblicare tramite API ufficiale."
                                        )
                                    elif not _connected:
                                        st.session_state["social_error_v59"] = _auth_error or _connect_error
                                else:
                                    _connected, _connect_error = _gsf_connect_social_account(_platform)
                                    if not _connected:
                                        st.session_state["social_error_v59"] = _connect_error

                            if _connected:
                                with st.spinner("Carico il video su " + _platform + "..."):
                                    _ok, _message, _path = _gsf_publish_social_upload(
                                        _final_video, _platform
                                    )
                                st.session_state["social_started_v59"] = _ok
                                if _path:
                                    st.session_state["social_export_v59"] = _path
                                if not _ok:
                                    st.session_state["social_error_v59"] = _message

                _auth_url = st.session_state.get("social_auth_url_v77", "")
                _auth_platform = st.session_state.get("social_auth_platform_v77", "")
                if _auth_url and _auth_platform:
                    st.link_button(
                        "COLLEGA " + str(_auth_platform).upper(),
                        _auth_url,
                        use_container_width=True,
                    )
                    st.caption("Il collegamento si apre nel browser. Terminato l'accesso, torna qui e premi di nuovo il social.")

                if st.session_state.get("social_started_v59"):
                    _gsf_social_progress_panel()
                _social_error = st.session_state.get("social_error_v59", "")
                if _social_error:
                    st.warning(_social_error)
                    _saved_path = st.session_state.get("social_export_v59", "")
                    if _saved_path and os.path.isfile(_saved_path) and not GSF_WEB_MODE:
                        st.caption("Video salvato in EXPORT: " + _saved_path)


st.markdown('<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>', unsafe_allow_html=True)
st.markdown('<footer class="v67-footer">Gaming Shorts Factory · V99 FINAL Architecture<br>Beta web/mobile · Sessione persistente</footer>', unsafe_allow_html=True)


# ============================================================
# V79 — PERSIST ANONYMOUS BETA WORKSPACE
# ============================================================
try:
    _gsf_save_persistent_state()
    _gsf_touch_session()
except Exception:
    pass


st.markdown("""
<style id="gsf-v82-upload-fix">
/* Il nuovo-video resta chiaramente separato dall'upload precedente. */
.st-key-v81_new_video button{
    background:#FFFFFF !important;
    color:#17324A !important;
    border:1px solid #9FCDEA !important;
    font-weight:750 !important;
}
.st-key-v81_new_video button p{color:#17324A !important}

/* Rafforza il feedback verde dell'uploader V81. */
.st-key-v73-upload-shell [role="progressbar"]{
    accent-color:#22C55E !important;
}
.st-key-v73-upload-shell progress{
    accent-color:#22C55E !important;
}
</style>
""",unsafe_allow_html=True)





st.markdown("""
<style id="gsf-v98-3-home-compact">
/* Use the available viewport instead of leaving decorative empty space above. */
.block-container{
    padding-top:0 !important;
}

/* Hero: preserve typography, only remove vertical air. */
.gsf-hero{
    padding-top:2px !important;
    padding-bottom:4px !important;
    margin-top:-24px !important;
    margin-bottom:0 !important;
}
.hero-title{
    margin-top:0 !important;
    margin-bottom:0 !important;
    line-height:.92 !important;
}
.hero-sub{
    margin-top:6px !important;
    margin-bottom:4px !important;
}

/* Pull the approved upload circle slightly upward; do not resize it. */
.st-key-v73-upload-shell{
    margin-top:-28px !important;
}

@media(max-width:750px){
    .block-container{
        padding-top:0 !important;
    }
    .gsf-hero{
        padding-top:2px !important;
        padding-bottom:3px !important;
        margin-top:-12px !important;
    }
    .hero-sub{
        margin-top:5px !important;
        margin-bottom:3px !important;
    }
    .st-key-v73-upload-shell{
        margin-top:-18px !important;
    }
}
</style>
""",unsafe_allow_html=True)

