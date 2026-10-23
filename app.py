# One import-path owner for the shared Streamlit interpreter. Keep the real
# package before legacy bare-helper paths on every initial run and reconnect.
import sys as _gsf_module_sys
from pathlib import Path as _GSF_ENTRY_PATH
_gsf_module_root=str(_GSF_ENTRY_PATH(__file__).resolve().parent)
_gsf_module_web=str(_GSF_ENTRY_PATH(_gsf_module_root)/"web")
_gsf_module_sys.path[:]=[_gsf_module_root,_gsf_module_web]+[
    entry for entry in _gsf_module_sys.path if entry not in (_gsf_module_root,_gsf_module_web)
]

# V293 RENDER MEMORY GUARD
from web.render_gate_v293 import render_slot as _gsf_render_slot_v293
GSF_FINAL_RENDER_SLOTS=max(1,min(2,int(__import__("os").environ.get("GSF_FINAL_RENDER_SLOTS","1") or 1)))
import streamlit as st
import streamlit.components.v1 as _gsf_components_v343
# V336_EXECUTABLE_SHELL_BRIDGE — V343 is executable; legacy parent bridges are retired.

def _gsf_v124_feedback(moment,action):
    try:
        if not GSF_WEB_MODE or not isinstance(moment,dict):
            return
        _payload={
            "engine":"v124-ai-os",
            "action":str(action or "selected"),
            "rank":int(moment.get("rank") or 0),
            "start":float(moment.get("start") or 0.0),
            "event":str(moment.get("event") or "highlight"),
            "brain_score":float(moment.get("brain_score") or 0.0),
            "confidence":float(moment.get("confidence") or 0.0),
            "semantic_injected":bool(moment.get("semantic_injected")),
        }
        _u=__import__("urllib.request",fromlist=["Request","urlopen"])
        _raw=__import__("json").dumps(_payload,separators=(",",":")).encode("utf-8")
        _req=_u.Request(
            "http://127.0.0.1:8502/ai/feedback",
            data=_raw,
            headers={
                "Content-Type":"application/json",
                "X-GSF-Session-ID":str(GSF_SESSION_ID),
            },
            method="POST",
        )
        _u.urlopen(_req,timeout=1.5).read()
    except Exception:
        pass


def _gsf_v124_moment_for_start(start):
    try:
        _brain=st.session_state.get("gsf_v112_brain_context") or {}
        _rows=list(_brain.get("selected") or []) if isinstance(_brain,dict) else []
        if not _rows:
            return {}
        _start=float(start or 0.0)
        return dict(min(_rows,key=lambda row:abs(float((row or {}).get("start") or 0.0)-_start)) or {})
    except Exception:
        return {}




def _gsf_v145_memory_api(path,record):
    try:
        _u=__import__("urllib.request",fromlist=["Request","urlopen"])
        _j=__import__("json")
        _port=str(__import__("os").environ.get("GSF_DIRECT_UPLOAD_PORT","8502") or "8502")
        _raw=_j.dumps({"record":dict(record or {})},ensure_ascii=False,separators=(",",":")).encode("utf-8")
        _req=_u.Request(
            "http://127.0.0.1:"+_port+str(path),
            data=_raw,
            headers={
                "Content-Type":"application/json",
                "X-GSF-Session-ID":str(GSF_SESSION_ID),
            },
            method="POST",
        )
        _resp=_j.loads(_u.urlopen(_req,timeout=2.5).read().decode("utf-8"))
        return dict((_resp or {}).get("memory") or {})
    except Exception as _exc:
        print("GSF_V145_MEMORY_API_WARN",str(path),repr(str(_exc))[:220],flush=True)
        return {}


def _gsf_v142_source_path():
    try:
        for _k in ("editor_input","inline_editor_input","gsf_source_path","publication_input"):
            _p=str(st.session_state.get(_k) or "").strip()
            if _p and __import__("os").path.exists(_p):
                return _p
        _raw=st.session_state.get("gsf_source_bytes")
        if isinstance(_raw,(bytes,bytearray,memoryview)) and len(_raw)>1024:
            _root=__import__("pathlib").Path(
                __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
            )/"sessions"/str(GSF_SESSION_ID)/"director"
            _root.mkdir(parents=True,exist_ok=True)
            _p=_root/"source_v142.mp4"
            if (not _p.exists()) or _p.stat().st_size!=len(_raw):
                _tmp=_p.with_suffix(".tmp")
                _tmp.write_bytes(bytes(_raw))
                __import__("os").replace(_tmp,_p)
            return str(_p)
        _video=globals().get("video")
        if _video is not None and hasattr(_video,"getvalue"):
            _raw=bytes(_video.getvalue() or b"")
            if len(_raw)>1024:
                _root=__import__("pathlib").Path(
                    __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
                )/"sessions"/str(GSF_SESSION_ID)/"director"
                _root.mkdir(parents=True,exist_ok=True)
                _p=_root/"source_v142.mp4"
                if (not _p.exists()) or _p.stat().st_size!=len(_raw):
                    _tmp=_p.with_suffix(".tmp")
                    _tmp.write_bytes(_raw)
                    __import__("os").replace(_tmp,_p)
                return str(_p)
    except Exception as _exc:
        print("GSF_V142_SOURCE_WARN",repr(str(_exc))[:220],flush=True)
    return ""


def _gsf_v148_performance_context():
    try:
        _u=__import__("urllib.request",fromlist=["Request","urlopen"])
        _j=__import__("json")
        _os=__import__("os")
        _port=str(_os.environ.get("GSF_DIRECT_UPLOAD_PORT","8502") or "8502")
        _raw=_j.dumps({},separators=(",",":")).encode("utf-8")
        _req=_u.Request(
            "http://127.0.0.1:"+_port+"/social-analytics/context",
            data=_raw,
            headers={
                "Content-Type":"application/json",
                "X-GSF-Session-ID":str(GSF_SESSION_ID),
            },
            method="POST",
        )
        _payload=_j.loads(_u.urlopen(_req,timeout=1.5).read().decode("utf-8"))
        return dict((_payload or {}).get("context") or {})
    except Exception:
        return {}


def _gsf_v142_enrich_recipe(recipe):
    _recipe=dict(recipe or {})
    try:
        _brain=st.session_state.get("gsf_v112_brain_context") or {}
        _one=dict(_brain.get("one_click") or {}) if isinstance(_brain,dict) else {}
        if not _one.get("shorts"):
            return _recipe
        _src=_gsf_v142_source_path()
        if not _src:
            print("GSF_V142_SKIP no-source",flush=True)
            return _recipe
        try:
            _dur=float(durata_video(_src) or 0.0)
        except Exception:
            _dur=0.0
        if _dur<=0:
            _dur=max(15.0,float(_recipe.get("duration") or 15.0))
        _root=__import__("pathlib").Path(
            __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
        )/"sessions"/str(GSF_SESSION_ID)/"director"
        _mod=__import__("director_pipeline_v142",fromlist=["run_director_pipeline","apply_pipeline_to_recipe"])
        _start=float(_recipe.get("start",st.session_state.get("auto_clip_scelta",0.0)) or 0.0)
        _short=_gsf_v130_short_for_start(_start)
        _mount=dict((_short or {}).get("mount") or {})
        _cine=dict(_mount.get("cinematic") or {})
        _frame=dict(_mount.get("framing") or {})
        _event={
            "signal":"selected",
            "zoom_aggression":max(0.0,min(1.0,(float(_frame.get("zoom") or 1.0)-1.0)/.8)),
            "caption_density":1.0 if _mount.get("captions") else 0.0,
            "replay_preference":1.0 if dict(_cine.get("replay") or {}).get("enabled") else 0.0,
            "cold_open":1.0 if dict(_cine.get("cold_open") or {}).get("enabled") else 0.0,
            "preserve_context":1.0 if dict(_one.get("game_context") or {}).get("context_available") else 0.0,
            "cut_density":min(1.0,len(list(_cine.get("pattern_interrupts") or []))/.4/max(float(_recipe.get("duration") or 15.0),1.0)),
        }
        _pipeline=_mod.run_director_pipeline(
            _src,_dur,_brain,_one,_root,
            selected_start=_start,
            provider_results=st.session_state.get("gsf_v142_provider_results"),
            creator_event=_event,
            performance_context=_gsf_v148_performance_context(),
        )

        # V145: persistent candidate-level memory is checked before the render
        # recipe is frozen. It survives redeploys through the existing bucket.
        try:
            _mem=__import__("content_memory_v145",fromlist=["memory_record"])
            _recognition=dict(_one.get("game_recognition") or {})
            _record=_mem.memory_record(
                _pipeline.get("source_fingerprint"),
                _pipeline.get("selected_short"),
                {
                    "game":str(_recognition.get("game") or ""),
                    "status":"prepared",
                },
            )
            _memory=_gsf_v145_memory_api("/content-memory/check",_record)
            _pipeline["content_memory"]=_memory
            _pipeline["content_memory_record"]=_record
            print(
                "GSF_V145_MEMORY_CHECK",
                "duplicate="+str(bool(_memory.get("duplicate"))),
                "source_count="+str(_memory.get("source_count") or 0),
                flush=True,
            )
        except Exception as _v145_exc:
            print("GSF_V145_MEMORY_CHECK_WARN",repr(str(_v145_exc))[:240],flush=True)

        st.session_state["gsf_v142_runtime"]=_pipeline
        _recipe=_mod.apply_pipeline_to_recipe(_recipe,_pipeline)
        print(
            "GSF_V142_READY",
            "ops="+str(dict(_pipeline.get("render") or {}).get("operation_count") or 0),
            "ab="+str(dict(_pipeline.get("ab") or {}).get("winner") or ""),
            "guard="+str(dict(_pipeline.get("render") or {}).get("publish_guard") or ""),
            flush=True,
        )
    except Exception as _exc:
        print("GSF_V142_PIPELINE_FALLBACK",repr(str(_exc))[:320],flush=True)
    return _recipe


def _gsf_v130_short_for_start(start):
    try:
        brain=st.session_state.get("gsf_v112_brain_context") or {}
        package=dict(brain.get("one_click") or {}) if isinstance(brain,dict) else {}
        shorts=list(package.get("shorts") or [])
        if not shorts:
            return {}
        wanted=float(start or 0.0)
        return dict(min(
            shorts,
            key=lambda row:abs(float((row or {}).get("start") or 0.0)-wanted)
        ) or {})
    except Exception:
        return {}


def _gsf_v126_hook_for_start(start):
    if not st.session_state.get("hook_enabled_v102",True):
        return _GSF_HOOK_OFF_V102
    manual=str(st.session_state.get("hook_testo","") or "").strip()
    if manual:
        return manual[:70]
    try:
        moment=_gsf_v124_moment_for_start(float(start))
        plan=dict((moment or {}).get("director_plan") or {})
        text_plan=dict(plan.get("text") or {})
        hook=str(text_plan.get("hook") or "").strip()
        return hook[:70]
    except Exception:
        return ""
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
from gsf_perf import perf_event as _gsf_perf_event

try:
    import numpy as np
except Exception:
    np = None


# GSF_V401_STREAM_UPLOAD_HELPER
def _gsf_v401_stream_upload_to_path(uploaded, target, chunk_size=4 * 1024 * 1024):
    try:
        chunk_size = int(chunk_size or (4 * 1024 * 1024))
    except Exception:
        chunk_size = 4 * 1024 * 1024
    chunk_size = max(1, min(4 * 1024 * 1024, chunk_size))
    original_pos = None
    try:
        original_pos = uploaded.tell()
    except Exception:
        pass
    written = 0
    try:
        try:
            uploaded.seek(0)
        except Exception:
            pass
        with open(target, "wb") as out:
            while True:
                chunk = uploaded.read(chunk_size)
                if not chunk:
                    break
                out.write(chunk)
                written += len(chunk)
    finally:
        if original_pos is not None:
            try:
                uploaded.seek(original_pos)
            except Exception:
                pass
    return written

st.markdown("", unsafe_allow_html=True)


st.markdown("", unsafe_allow_html=True)





st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)


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
    "gsf_save_draft_v107",
    "gsf_save_draft_before_engine_change_v107",
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

try:
    _gsf_draft_resume_marker=GSF_SESSION_ROOT/"draft_resume.json"
    if _gsf_draft_resume_marker.is_file():
        _gsf_draft_payload=__import__("json").loads(GSF_SESSION_STATE_FILE.read_text(encoding="utf-8"))
        if isinstance(_gsf_draft_payload,dict):
            for _k in list(st.session_state.keys()):
                if _k=="gsf_web_session_id":
                    continue
                try:
                    del st.session_state[_k]
                except Exception:
                    pass
            for _k,_v in _gsf_draft_payload.items():
                if _k in _GSF_STATE_SKIP_EXACT:
                    continue
                if any(_p in str(_k).lower() for _p in _GSF_STATE_SKIP_PARTS):
                    continue
                try:
                    st.session_state[_k]=_v
                except Exception:
                    pass
            st.session_state["_gsf_v79_state_restored"]=True
            st.session_state["gsf_v107_draft_resumed"]=True
        _gsf_draft_resume_marker.unlink(missing_ok=True)
except Exception as _gsf_draft_resume_exc:
    print("GSF_DRAFT_RESUME_WARN",repr(str(_gsf_draft_resume_exc)),flush=True)


try:
    if "gsf_final_ready_sync_v111" not in _GSF_TRANSIENT_WIDGET_EXACT:
        _GSF_TRANSIENT_WIDGET_EXACT.append("gsf_final_ready_sync_v111")
except Exception:
    pass

try:
    for _k in (
        "v81_new_video",
        "gsf_v1302_save_then_new",
        "gsf_v1302_discard_then_new",
        "gsf_v1302_cancel_new",
        "gsf_v1302_publish_all",
    ):
        if _k not in _GSF_TRANSIENT_WIDGET_EXACT:
            _GSF_TRANSIENT_WIDGET_EXACT.append(_k)
except Exception:
    pass

_gsf_restore_persistent_state()
if st.session_state.pop("gsf_v107_draft_resumed",False):
    st.toast("💾 Bozza ripristinata.")


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


st.markdown(r"""
<style id="gsf-v152-neutral-reset">
html,body,[data-testid="stAppViewContainer"],.stApp{
  background:#fff !important;
  color:#172033 !important;
}
[data-testid="stAppViewContainer"] .main .block-container{
  max-width:1200px !important;
  padding-top:1rem !important;
  padding-bottom:4rem !important;
}
.hero-title,.hero-sub,.hero-orb,.flow,
.v67-ad,.gsf-v1056-ad,.v67-footer,
.gsf-v151-brand,.gsf-v151-whisper,.gsf-v151-bar,
.gsf-account-fab{
  display:none !important;
}
.v67-badge{display:none !important}
.gsf-icon-title{
  display:block !important;
  margin:.8rem 0 !important;
  padding:0 !important;
  background:none !important;
  border:0 !important;
  box-shadow:none !important;
}
.gsf-section-sub,.gsf-command,.v65-quality-note{
  background:none !important;
  border:0 !important;
  box-shadow:none !important;
  padding:0 !important;
}
[data-testid="stFileUploader"]{
  opacity:1 !important;
  visibility:visible !important;
  pointer-events:auto !important;
  position:static !important;
  width:100% !important;
  max-width:720px !important;
  height:auto !important;
  min-height:0 !important;
  margin:1rem auto !important;
  padding:0 !important;
  border:0 !important;
  background:none !important;
  box-shadow:none !important;
  overflow:visible !important;
}
[data-testid="stFileUploaderDropzone"]{
  position:relative !important;
  inset:auto !important;
  width:100% !important;
  height:auto !important;
  min-height:120px !important;
  opacity:1 !important;
  visibility:visible !important;
  border:1px dashed #b7c2d0 !important;
  border-radius:12px !important;
  background:#fff !important;
}
[data-testid="stFileUploaderDropzone"] button{
  position:static !important;
  width:auto !important;
  height:auto !important;
  min-width:0 !important;
  min-height:0 !important;
  max-width:none !important;
  max-height:none !important;
  opacity:1 !important;
  visibility:visible !important;
  display:inline-flex !important;
  margin:0 !important;
  padding:.55rem .9rem !important;
  border-radius:8px !important;
}
[data-testid="stFileUploaderDropzone"] button::before,
[data-testid="stFileUploaderDropzone"] button::after{
  content:none !important;
  display:none !important;
}
[data-testid="stFileUploaderDropzoneInstructions"]{
  display:block !important;
}
</style>
""",unsafe_allow_html=True)


from web.living_ui import (
    render_shell as _gsf_render_living_shell,
    render_tail as _gsf_render_living_tail,
)
_gsf_render_living_shell()

st.markdown("", unsafe_allow_html=True)




st.markdown("", unsafe_allow_html=True)

# V65 — revisione grafica ad alta leggibilità.
# Tutti gli elementi sono HTML/CSS: niente screenshot usati come interfaccia.
st.markdown("", unsafe_allow_html=True)


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
        "editor_filter_preset": "Originale", "editor_filter_intensity": 70,
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

st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)


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
    # Metadata belongs to ffprobe: the encoder wrapper inserts output options
    # and cannot safely handle the output-less `ffmpeg -i file` invocation.
    if FFPROBE_PATH:
        try:
            probe=subprocess.run([FFPROBE_PATH,"-v","error","-show_entries","format=duration",
                "-of","default=noprint_wrappers=1:nokey=1",str(file_path)],
                capture_output=True,text=True,timeout=10)
            value=float((probe.stdout or "").strip())
            if probe.returncode==0 and value>0 and value<float("inf"):
                return value
        except (OSError,ValueError,subprocess.TimeoutExpired):
            pass

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
    """Create a bounded low-memory preview without probing unavailable QSV."""
    base = [
        FFMPEG_PATH,
        "-y",
        "-ss", str(start),
        "-i", input_file,
        "-t", str(duration),
        "-vf", "scale=640:-2",
    ]
    encoders=[]
    try:
        if Path("/dev/dri/renderD128").exists():
            encoders.append(("h264_qsv",["-preset","veryfast","-global_quality","30"]))
    except Exception:
        pass
    encoders.append(("libx264",["-preset","veryfast","-crf","30","-threads","1"]))

    for encoder,options in encoders:
        try:
            if os.path.exists(output_file):
                os.unlink(output_file)
            risultato=subprocess.run(
                base+["-c:v",encoder]+options+[
                    "-c:a","aac","-b:a","96k",
                    "-movflags","+faststart",output_file
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=max(120.0,float(duration)*15.0),
            )
            if risultato.returncode==0 and os.path.exists(output_file):
                return True
        except (OSError,subprocess.TimeoutExpired):
            continue
    return False



_gsf_crea_anteprima_original=crea_anteprima
def crea_anteprima(input_path,output_path,start,duration,*args,**kwargs):
    try:
        _src=Path(str(input_path));_out=Path(str(output_path))
        _root=Path(str(GSF_PREVIEW_DIR))/"preview_cache_v107";_root.mkdir(parents=True,exist_ok=True)
        _sig="|".join([str(_src.resolve()) if _src.exists() else str(_src),str(_src.stat().st_size) if _src.exists() else "0",str(int(_src.stat().st_mtime)) if _src.exists() else "0",f"{float(start or 0):.3f}",f"{float(duration or 0):.3f}",repr(args),repr(sorted(kwargs.items())),_out.suffix.lower()])
        _key=__import__("hashlib").sha1(_sig.encode("utf-8")).hexdigest()[:24]
        _cached=_root/("p_"+_key+(_out.suffix.lower() or ".mp4"))
        if _cached.is_file() and _cached.stat().st_size>4096:
            _out.parent.mkdir(parents=True,exist_ok=True);__import__("shutil").copyfile(_cached,_out);return True
        _ok=_gsf_crea_anteprima_original(input_path,output_path,start,duration,*args,**kwargs)
        if _out.is_file() and _out.stat().st_size>4096:
            _tmp=_cached.with_suffix(_cached.suffix+".tmp");__import__("shutil").copyfile(_out,_tmp);__import__("os").replace(_tmp,_cached)
        return _ok
    except Exception:
        return _gsf_crea_anteprima_original(input_path,output_path,start,duration,*args,**kwargs)




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



_GSF_HOOK_OFF_V102 = "__GSF_HOOK_OFF_V102__"

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


def _gsf_hook_transcript_excerpt(diag, max_chars=52):
    """Use only words actually spoken in the selected moment; never invent copy."""
    diag=diag or {}
    raw=diag.get("transcript","")
    if isinstance(raw,(list,tuple)):
        raw=" ".join(str(x or "") for x in raw)
    text=_gsf_clean_burnin_text(raw)
    text=re.sub(r"\s+"," ",text).strip()
    if not text:
        return ""

    features=diag.get("features") or {}
    reaction=max(
        float(features.get("reaction",0.0)),
        float(features.get("reaction_cue",0.0)),
    )
    speech=float(features.get("speech",0.0))
    hook_score=float(features.get("hook_score",0.0))

    # Spoken text becomes a hook only when voice/reaction is genuinely relevant.
    if reaction<0.40 and not (speech>=0.50 and hook_score>=0.46):
        return ""

    filler={"eh","ehm","uh","um","ok","okay","si","sì","no","allora","cioè","dai","vai"}
    pieces=re.split(r"(?<=[!?\.])\s+|\s*[|\n]+\s*",text)
    candidates=[]
    for piece in pieces:
        piece=str(piece or "").strip(" -–—")
        words=piece.split()
        if not (2<=len(words)<=9):
            continue
        if len(piece)<7:
            continue
        if all(re.sub(r"[^\wàèéìòù]","",w.lower()) in filler for w in words):
            continue
        if len(piece)>int(max_chars):
            piece=" ".join(words[:7]).strip()
        if 7<=len(piece)<=int(max_chars):
            candidates.append(piece)

    if not candidates:
        words=text.split()
        if 2<=len(words)<=7 and len(text)<=int(max_chars):
            candidates=[text]

    if not candidates:
        return ""

    # Prefer an expressive sentence, otherwise the shortest faithful excerpt.
    candidates.sort(key=lambda x:(0 if ("!" in x or "?" in x) else 1,len(x)))
    return candidates[0][:int(max_chars)].strip()


def _gsf_hook_from_diag(diag, manual_hook=""):
    """
    V102: manual text wins; OFF is explicit; automatic hooks are used only
    when the selected content provides strong semantic evidence.
    """
    manual=str(manual_hook or "").strip()
    if manual==_GSF_HOOK_OFF_V102:
        return ""
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
    hook_score=float(features.get("hook_score",0.0))
    speech=float(features.get("speech",0.0))

    # Strong recognized gameplay events are factual/content-specific.
    if event_score>=0.64 and event_type in _GSF_HOOK_TEMPLATES:
        return _GSF_HOOK_TEMPLATES[event_type]

    spoken=_gsf_hook_transcript_excerpt(diag)
    if spoken:
        if category=="reaction" and reaction>=0.40:
            return spoken
        if category=="story" and hook_score>=0.50:
            return spoken
        if speech>=0.58 and hook_score>=0.48:
            return spoken

    # No generic "AZIONE PURA / ECCO IL MOMENTO" fallback.
    return ""



def _gsf_auto_hook_for_start(start, manual_hook=""):
    return _gsf_hook_from_diag(
        _gsf_diag_for_start(start),
        manual_hook=manual_hook
    )

def _gsf_v102_hook_preview_bytes(video_bytes, hook_text, duration, fmt="9:16 Short"):
    raw=bytes(video_bytes or b"")
    if len(raw)<1024:
        return raw
    hook=_gsf_clean_burnin_text(hook_text)
    if not hook:
        return raw
    if not FFMPEG_PATH:
        return raw

    temp_dir=_gsf_session_mkdtemp("gsf_hook_preview_v102_")
    src_path=os.path.join(temp_dir,"preview_source.mp4")
    ass_path=os.path.join(temp_dir,"hook_preview.ass")
    out_path=os.path.join(temp_dir,"hook_preview.mp4")
    with open(src_path,"wb") as f:
        f.write(raw)

    hook_duration=min(2.0,max(1.15,float(duration)*0.12))
    ok=_gsf_write_render_ass(
        ass_path,[],fallback_text="",
        fmt=fmt,
        hook_text=hook,
        hook_duration=hook_duration,
        hook_y_pct=15
    )
    if not ok:
        return raw

    try:
        cmd=[
            FFMPEG_PATH,"-hide_banner","-loglevel","error","-y",
            "-i",src_path,
            "-vf",f"ass={ass_path}",
            "-c:v","libx264","-preset","ultrafast","-crf","20",
            "-threads","1","-pix_fmt","yuv420p","-fpsmax","60",
            "-c:a","aac","-b:a","128k",
            "-movflags","+faststart",out_path
        ]
        r=subprocess.run(
            cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            timeout=max(90.0,min(300.0,float(duration)*12.0))
        )
        if r.returncode==0 and os.path.exists(out_path) and os.path.getsize(out_path)>1024:
            with open(out_path,"rb") as f:
                return f.read()
    except Exception:
        pass
    return raw


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


def _gsf_refine_subtitle_words(words):
    """Normalize Whisper word timings without changing their semantic order."""
    cleaned=[]
    for raw in (words or []):
        tx=str((raw or {}).get("text","") or "").strip()
        if not tx:
            continue
        try:
            start=max(0.0,float(raw.get("start",0.0)))
        except Exception:
            start=0.0
        try:
            end=float(raw.get("end",start+.12))
        except Exception:
            end=start+.12
        if cleaned and start<cleaned[-1]["start"]:
            start=cleaned[-1]["start"]
        end=max(start+.055,end)
        item=dict(raw)
        item["text"]=tx
        item["start"]=start
        item["end"]=end
        cleaned.append(item)

    # Resolve overlapping timestamps so the active-word handoff is deterministic.
    for i in range(len(cleaned)-1):
        cur=cleaned[i]
        nxt=cleaned[i+1]
        ns=float(nxt["start"])
        if ns>float(cur["start"]) and float(cur["end"])>ns:
            cur["end"]=max(float(cur["start"])+.055,ns)
    return cleaned


def _gsf_subtitle_visual_units(text):
    units=0.0
    for ch in str(text or ""):
        if ch.isspace():
            units+=.34
        elif ch in "ilI1'.,:;!|":
            units+=.50
        elif ch in "MW@#%&":
            units+=1.16
        else:
            units+=1.0
    return max(1.0,units)


def _gsf_subtitle_auto_size(base_size,text,fmt="9:16 Short"):
    """Keep the user's chosen size as the ceiling; shrink only to prevent overflow."""
    base=int(max(24,min(180,int(base_size))))
    width=1080 if fmt=="9:16 Short" else 1920
    safe_width=width*(.76 if fmt=="9:16 Short" else .84)
    units=_gsf_subtitle_visual_units(text)
    fitted=int(safe_width/max(1.0,units*.58))
    return int(max(24,min(base,fitted)))


def _gsf_subtitle_safe_xy(fmt,x_pct,y_pct,text,font_size,w_res,h_res):
    """Clamp only when manual placement would enter common Shorts/Reels/TikTok UI zones."""
    if fmt=="9:16 Short":
        left,right,top,bottom=.08,.88,.18,.76
    else:
        left,right,top,bottom=.05,.95,.08,.90

    line_w=min((right-left)*w_res,_gsf_subtitle_visual_units(text)*float(font_size)*.58)
    half_w=max(float(font_size)*.6,line_w/2.0)
    half_h=max(float(font_size)*.65,24.0)

    requested_x=max(0.0,min(1.0,float(x_pct)/100.0))*w_res
    requested_y=max(0.0,min(1.0,float(y_pct)/100.0))*h_res

    min_x=left*w_res+half_w
    max_x=right*w_res-half_w
    if min_x>max_x:
        safe_x=(left+right)*.5*w_res
    else:
        safe_x=max(min_x,min(max_x,requested_x))

    min_y=top*h_res+half_h
    max_y=bottom*h_res-half_h
    if min_y>max_y:
        safe_y=(top+bottom)*.5*h_res
    else:
        safe_y=max(min_y,min(max_y,requested_y))
    return int(round(safe_x)),int(round(safe_y))


def _gsf_write_render_ass(
    ass_file, words, fallback_text="",
    font="Arial", size=92, x_pct=50, y_pct=78,
    text_color="#FFFFFF", active_color="#FFD400",
    outline_color="#000000", fmt="9:16 Short",
    hook_text="", hook_duration=1.8, hook_y_pct=15
):
    """
    V101 refinement only:
    - precise active-word timing;
    - current-word highlight preserved;
    - automatic shrink only when needed;
    - safe social placement while preserving manual choices when already safe.
    """
    if fmt=="9:16 Short":
        w_res,h_res=1080,1920
    else:
        w_res,h_res=1920,1080

    base_fs=int(max(24,min(180,int(size))))
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
Style: Default,{safe_font},{base_fs},{primary},{active},{outline},&H78000000,-1,0,0,0,100,100,0,0,1,5,2,5,20,20,20,1
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
        hook_line=hook_line.replace(r"\\N",r"\N")
        ass+=(
            f"Dialogue: 2,0:00:00.00,{_gsf_ass_time(hook_end)},"
            f"Hook,,0,0,0,,{hook_line}\n"
        )
        wrote=True

    words=_gsf_refine_subtitle_words(words)
    if words:
        groups=_gsf_subtitle_groups(words)
        longest_text=max(
            (" ".join(str((w or {}).get("text","") or "").strip() for w in g).strip() for g in groups),
            key=lambda t:_gsf_subtitle_visual_units(t),
            default=""
        )
        effective_fs=_gsf_subtitle_auto_size(base_fs,longest_text,fmt)

        for group in groups:
            plain_parts=[_gsf_ass_escape(item.get("text","")) for item in group]
            plain_line=" ".join(plain_parts).strip()
            if not plain_line:
                continue
            gx,gy=_gsf_subtitle_safe_xy(
                fmt,x_pct,y_pct,
                " ".join(str((w or {}).get("text","") or "").strip() for w in group),
                effective_fs,w_res,h_res
            )
            neutral_positioned=(
                r"{\an5\pos("+str(gx)+","+str(gy)+r")\fs"+str(effective_fs)+r"}"+
                plain_line
            )

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

                a=max(0.0,float(word.get("start",0.0)))
                own_end=max(a+.055,float(word.get("end",a+.12)))
                next_start=None
                if local_idx+1<len(group):
                    try:
                        next_start=max(a+.055,float(group[local_idx+1].get("start",own_end)))
                    except Exception:
                        next_start=None

                if next_start is not None:
                    active_end=max(a+.055,min(own_end,next_start))
                else:
                    active_end=own_end+.08

                positioned=(
                    r"{\an5\pos("+str(gx)+","+str(gy)+r")\fs"+str(effective_fs)+r"}"+
                    line
                )
                ass+=(
                    f"Dialogue: 0,{_gsf_ass_time(a)},{_gsf_ass_time(active_end)},"
                    f"Default,,0,0,0,,{positioned}\n"
                )
                wrote=True

                # Keep the phrase visible during a natural inter-word gap,
                # but remove the highlight when nobody is speaking.
                if next_start is not None and next_start>active_end+.015:
                    ass+=(
                        f"Dialogue: 0,{_gsf_ass_time(active_end)},{_gsf_ass_time(next_start)},"
                        f"Default,,0,0,0,,{neutral_positioned}\n"
                    )

    elif str(fallback_text or "").strip():
        raw=str(fallback_text or "").strip()
        effective_fs=_gsf_subtitle_auto_size(base_fs,raw,fmt)
        gx,gy=_gsf_subtitle_safe_xy(fmt,x_pct,y_pct,raw,effective_fs,w_res,h_res)
        line=_gsf_ass_escape(raw)
        positioned=(
            r"{\an5\pos("+str(gx)+","+str(gy)+r")\fs"+str(effective_fs)+r"}"+
            line
        )
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



GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"


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


def _gsf_smart_reframe_analyze(source_path,start,duration,sample_fps=5,analysis_width=320):
    """
    V100 gameplay-aware Smart Reframe for 9:16.
    Tracks coherent motion clusters, suppresses HUD/corner activity, protects
    hook/subtitle safe zones and uses a damped camera controller.
    """
    result={
        "enabled":False,
        "reason":"",
        "track":[],
        "confidence":0.0,
        "movement":0.0,
        "samples":0,
        "profile":"v100-gameplay-safe",
        "hud_suppression":0.0,
        "safe_zones":{"hook_top":0.17,"subtitle_bottom":0.24},
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

    aw=max(192,int(analysis_width))
    ah=max(108,int(round(aw*h/w)))
    if ah%2:
        ah+=1

    fps=max(3,min(6,int(sample_fps)))
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
    portrait_pressure=max(0.0,min(1.0,(1.0-crop_fraction)/0.70))

    xs=(np.arange(aw,dtype=np.float32)+0.5)/float(aw)

    # Gameplay prior: center remains important, but not so strong that a real
    # subject on either side gets dragged back to the middle.
    center_prior=1.0-0.12*np.minimum(1.0,np.abs(xs-0.5)/0.5)

    # HUD / overlay protection. Most game HUD lives in corners/top/bottom.
    # We do not delete those pixels; we merely reduce their ability to steer
    # the crop. This also reserves practical visual room for hook/subtitles.
    row_weight=np.ones(ah,dtype=np.float32)
    hook_rows=max(1,int(round(ah*0.17)))
    sub_rows=max(1,int(round(ah*0.24)))
    row_weight[:hook_rows]*=0.48
    row_weight[max(0,ah-sub_rows):]*=0.54

    col_weight=np.ones(aw,dtype=np.float32)
    edge=max(1,int(round(aw*0.075)))
    col_weight[:edge]*=0.68
    col_weight[max(0,aw-edge):]*=0.68

    spatial_weight=row_weight[:,None]*col_weight[None,:]
    # Extra corner suppression catches animated minimaps, counters and kill feeds.
    corner_h=max(1,int(round(ah*0.28)))
    corner_w=max(1,int(round(aw*0.19)))
    spatial_weight[:corner_h,:corner_w]*=0.68
    spatial_weight[:corner_h,-corner_w:]*=0.68
    spatial_weight[-corner_h:,:corner_w]*=0.72
    spatial_weight[-corner_h:,-corner_w:]*=0.72

    centers=[0.5]
    confidences=[0.0]
    safe_scores=[1.0]
    hud_scores=[0.0]
    prev_center=0.5
    velocity=0.0
    pending_target=0.5
    pending_count=0

    # Narrow 9:16 crops should feel like a camera operator, not a cursor.
    dead_zone=0.038+0.014*portrait_pressure
    base_max_step=0.050-0.008*portrait_pressure
    accel_limit=0.024

    for i in range(1,frame_count):
        cur=frames[i].astype(np.int16)
        prev=frames[i-1].astype(np.int16)
        diff=np.abs(cur-prev).astype(np.float32)

        total=float(diff.sum())
        mean=float(diff.mean())
        if total<=1.0 or mean<0.14:
            centers.append(prev_center)
            confidences.append(0.0)
            safe_scores.append(1.0)
            hud_scores.append(0.0)
            velocity*=0.72
            continue

        threshold=float(np.percentile(diff,76.0))
        salient=np.maximum(diff-threshold,0.0)
        raw_sal_total=float(salient.sum())
        if raw_sal_total<=1.0:
            centers.append(prev_center)
            confidences.append(0.0)
            safe_scores.append(1.0)
            hud_scores.append(0.0)
            velocity*=0.72
            continue

        weighted=salient*spatial_weight
        col=weighted.sum(axis=0)*center_prior
        weighted_total=float(col.sum())
        if weighted_total<=1.0:
            centers.append(prev_center)
            confidences.append(0.0)
            safe_scores.append(1.0)
            hud_scores.append(0.0)
            velocity*=0.72
            continue

        # Coherent-motion cluster. A global centroid often lands between two
        # unrelated moving areas; the cluster peak is a better gameplay target.
        kernel=max(5,int(round(aw*0.055)))
        if kernel%2==0:
            kernel+=1
        smooth_col=np.convolve(
            col,
            np.ones(kernel,dtype=np.float32)/float(kernel),
            mode="same"
        )
        peak_idx=int(np.argmax(smooth_col))
        cluster_half=max(kernel,int(round(aw*0.12)))
        lo=max(0,peak_idx-cluster_half)
        hi=min(aw,peak_idx+cluster_half+1)
        cluster=col[lo:hi]
        cluster_total=float(cluster.sum())
        global_c=float((col*xs).sum()/weighted_total)
        if cluster_total>1.0:
            cluster_c=float((cluster*xs[lo:hi]).sum()/cluster_total)
        else:
            cluster_c=global_c

        cluster_share=max(0.0,min(1.0,cluster_total/(weighted_total+1e-6)))
        desired=cluster_c*(0.58+0.24*cluster_share)+global_c*(0.42-0.24*cluster_share)

        # Confidence combines amount of useful motion and how concentrated it is.
        p=col/weighted_total
        entropy=float(
            -(p*np.log(p+1e-9)).sum()/max(1e-9,math.log(len(p)))
        )
        concentration=max(0.0,min(1.0,1.0-entropy))
        useful_ratio=max(0.0,min(1.0,float(weighted.sum())/(raw_sal_total+1e-6)))
        saliency_ratio=min(1.0,raw_sal_total/(total+1e-6)*3.0)
        confidence=max(
            0.0,min(
                1.0,
                0.42*saliency_ratio+
                0.30*concentration+
                0.18*cluster_share+
                0.10*useful_ratio
            )
        )

        # Quantify how much raw activity was discounted as likely HUD/overlay.
        hud_supp=max(0.0,min(1.0,1.0-useful_ratio))
        hud_scores.append(hud_supp)
        safe_scores.append(useful_ratio)

        desired=max(min_c,min(max_c,desired))

        # Low-confidence edge motion is commonly HUD animation. It may influence
        # the camera only after it persists, never in one-frame snaps.
        edge_target=(desired<0.18 or desired>0.82)
        if edge_target and confidence<0.42:
            desired=0.72*prev_center+0.28*desired
            confidence*=0.72

        delta=desired-prev_center

        # Dead-zone + hysteresis: micro-motion does not move the crop.
        if abs(delta)<=dead_zone:
            pending_count=0
            pending_target=prev_center
            target=prev_center
        else:
            if abs(desired-pending_target)<=dead_zone*0.80:
                pending_count+=1
            else:
                pending_target=desired
                pending_count=1

            urgent=confidence>=0.62 or abs(delta)>=0.18
            if pending_count<2 and not urgent:
                target=prev_center
            else:
                target=desired

        # Fast initial lock is allowed only on a genuinely reliable sample.
        if i==1 and confidence>=0.50:
            smoothed=target
            velocity=0.0
            centers[0]=smoothed
        else:
            wanted=target-prev_center
            max_step=base_max_step+(0.020 if confidence>=0.68 else 0.0)
            wanted=max(-max_step,min(max_step,wanted))

            # Acceleration clamp avoids abrupt direction reversals.
            dv=max(-accel_limit,min(accel_limit,wanted-velocity))
            velocity=(velocity+dv)*0.90
            if target==prev_center:
                velocity*=0.52

            alpha=0.54 if abs(delta)>=0.16 and confidence>=0.55 else (0.30+0.22*confidence)
            smoothed=prev_center+velocity*alpha
            if (target-prev_center)*(target-smoothed)<0:
                smoothed=target

        smoothed=max(min_c,min(max_c,smoothed))
        centers.append(smoothed)
        confidences.append(confidence)
        prev_center=smoothed

    # Symmetric low-pass pass removes residual one-frame wobble but keeps
    # sustained movement. Three taps are intentionally conservative.
    smoothed=list(centers)
    for _ in range(2):
        nxt=list(smoothed)
        for i in range(1,len(smoothed)-1):
            nxt[i]=(
                0.18*smoothed[i-1]+
                0.64*smoothed[i]+
                0.18*smoothed[i+1]
            )
        smoothed=nxt

    # Half-second control points: smoother than frame-by-frame, more responsive
    # than the old one-point-per-second path on fast gameplay.
    stride=max(1,int(round(fps*0.50)))
    track=[]
    for i in range(0,len(smoothed),stride):
        j=min(len(smoothed),i+stride)
        c=float(np.median(np.asarray(smoothed[i:j],dtype=np.float32)))
        conf=float(np.mean(np.asarray(confidences[i:j],dtype=np.float32)))
        hud=float(np.mean(np.asarray(hud_scores[i:j],dtype=np.float32)))
        safe=float(np.mean(np.asarray(safe_scores[i:j],dtype=np.float32)))
        track.append({
            "t":round(i/float(fps),3),
            "cx":round(max(min_c,min(max_c,c)),6),
            "confidence":round(max(0.0,min(1.0,conf)),4),
            "hud_guard":round(max(0.0,min(1.0,hud)),4),
            "safe_zone_score":round(max(0.0,min(1.0,safe)),4),
        })

    last_t=max(0.0,(len(smoothed)-1)/float(fps))
    if not track or last_t-track[-1]["t"]>0.30:
        track.append({
            "t":round(last_t,3),
            "cx":round(max(min_c,min(max_c,float(smoothed[-1]))),6),
            "confidence":round(max(0.0,min(1.0,float(confidences[-1]))),4),
            "hud_guard":round(max(0.0,min(1.0,float(hud_scores[-1]))),4),
            "safe_zone_score":round(max(0.0,min(1.0,float(safe_scores[-1]))),4),
        })

    movement=0.0
    if len(track)>1:
        movement=sum(
            abs(float(track[i]["cx"])-float(track[i-1]["cx"]))
            for i in range(1,len(track))
        )/max(1,len(track)-1)

    mean_conf=float(np.mean(np.asarray(confidences,dtype=np.float32)))
    mean_hud=float(np.mean(np.asarray(hud_scores,dtype=np.float32)))

    if mean_conf<0.105 or movement<0.0035:
        result.update({
            "reason":"inquadratura stabile: tracking non necessario",
            "track":[
                {
                    "t":0.0,"cx":0.5,
                    "confidence":round(mean_conf,4),
                    "hud_guard":round(mean_hud,4),
                    "safe_zone_score":1.0,
                }
            ],
            "confidence":round(mean_conf,4),
            "movement":round(movement,5),
            "samples":frame_count,
            "hud_suppression":round(mean_hud,4),
        })
        return result

    result.update({
        "enabled":True,
        "reason":"V100 gameplay-aware tracking",
        "track":track,
        "confidence":round(mean_conf,4),
        "movement":round(movement,5),
        "samples":frame_count,
        "hud_suppression":round(mean_hud,4),
    })
    return result



def _gsf_smart_reframe_cached(source_path,start,duration,cache_token=None):
    cache=st.session_state.setdefault(
        "gsf_smart_reframe_cache_v100",{}
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
    """
    V100 camera stabilizer.
    Uses confidence-aware dead-zone, velocity and acceleration limits so a
    sustained subject move is followed while HUD spikes and micro-jitter are not.
    """
    pts=[]
    for item in (track or []):
        try:
            pts.append({
                "t":float(item["t"]),
                "cx":max(0.10,min(0.90,float(item["cx"]))),
                "confidence":max(0.0,min(1.0,float(item.get("confidence",0.55)))),
                "hud_guard":max(0.0,min(1.0,float(item.get("hud_guard",0.0)))),
                "safe_zone_score":max(0.0,min(1.0,float(item.get("safe_zone_score",1.0)))),
            })
        except Exception:
            continue
    pts=sorted(pts,key=lambda x:x["t"])
    if len(pts)<2:
        return pts

    # Light look-ahead median rejects isolated wrong targets before the camera
    # controller sees them.
    desired=[]
    for i,item in enumerate(pts):
        lo=max(0,i-1)
        hi=min(len(pts),i+2)
        nearby=sorted(float(pts[j]["cx"]) for j in range(lo,hi))
        med=nearby[len(nearby)//2]
        conf=float(item["confidence"])
        hud=float(item["hud_guard"])
        blend=max(0.20,min(0.90,0.35+0.55*conf-0.30*hud))
        desired.append(float(item["cx"])*blend+med*(1.0-blend))

    out=[dict(pts[0])]
    out[0]["cx"]=desired[0]
    prev=desired[0]
    velocity=0.0

    for i,item in enumerate(pts[1:],1):
        dt=max(0.05,float(item["t"])-float(pts[i-1]["t"]))
        raw=desired[i]
        conf=float(item["confidence"])
        hud=float(item["hud_guard"])
        delta=raw-prev

        # Dead-zone grows when the signal looks HUD-like or uncertain.
        dead=0.016+0.020*(1.0-conf)+0.018*hud
        if abs(delta)<=dead:
            target=prev
        else:
            target=raw

        # Max pan speed is normalized frame-width per second. High confidence
        # permits a faster catch-up, but never an instant jump.
        max_speed=0.16+0.12*conf
        wanted_v=(target-prev)/dt
        wanted_v=max(-max_speed,min(max_speed,wanted_v))

        max_accel=0.28
        dv=wanted_v-velocity
        dv=max(-max_accel*dt,min(max_accel*dt,dv))
        velocity+=dv
        if target==prev:
            velocity*=max(0.0,1.0-3.2*dt)

        nxt=prev+velocity*dt
        if (target-prev)*(target-nxt)<0:
            nxt=target
            velocity=0.0

        # Low-confidence HUD-ish points cannot pull far from the previous crop.
        if hud>=0.35 and conf<0.45:
            max_hud_pull=0.035
            nxt=max(prev-max_hud_pull,min(prev+max_hud_pull,nxt))

        nxt=max(0.10,min(0.90,nxt))
        row=dict(item)
        row["cx"]=nxt
        out.append(row)
        prev=nxt

    # One final symmetric pass for visually continuous FFmpeg interpolation.
    if len(out)>=3:
        vals=[float(x["cx"]) for x in out]
        for i in range(1,len(out)-1):
            out[i]["cx"]=(
                0.16*vals[i-1]+
                0.68*vals[i]+
                0.16*vals[i+1]
            )
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
    V100.3 native-crop HQ Smart Reframe.

    Crop the original landscape frame FIRST, at source resolution, then upscale
    only the selected 9:16 window to 1080x1920. This avoids scaling the whole
    16:9 frame before cropping, reducing work and preventing an unnecessary
    full-frame resample during camera motion.
    """
    zoom=max(1.0,float(zoom))
    y_pos=float(y_pos)
    cx=_gsf_smart_reframe_cx_expression(track)

    # Source-space crop:
    #   crop_h = source height / zoom
    #   crop_w = crop_h * 9/16
    # force even dimensions for H.264/yuv420 compatibility.
    crop_h=f"max(2,trunc((ih/{zoom})/2)*2)"
    crop_w=f"max(2,trunc(((ih/{zoom})*9/16)/2)*2)"

    return (
        "setpts=PTS-STARTPTS,"
        f"crop=w='{crop_w}':h='{crop_h}':"
        f"x='max(0,min(iw-ow,({cx})*iw-ow/2))':"
        f"y='max(0,min(ih-oh,(ih-oh)/2+({y_pos}/100)*(ih-oh)/2))',"
        "scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int,"
        "unsharp=5:5:0.08:3:3:0.02"
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

# ===== V109 NATIVE ZOOM-OUT =====
GSF_V109_ZOOMOUT = True
try:
    from zoomout_v109 import build_zoomout_filter as _gsf_v109_zoomout_filter
except Exception as _gsf_v109_exc:
    raise RuntimeError("V109 zoom-out helper unavailable: "+str(_gsf_v109_exc))

_gsf_v109_render_video_filters_base=_gsf_render_video_filters
def _gsf_render_video_filters(
    fmt,zoom,x_pos,y_pos,brightness,contrast,speed,
    ass_file=None,reframe_track=None
):
    try:
        _zoom=float(zoom)
    except Exception:
        _zoom=1.0
    if _zoom>=0.999:
        return _gsf_v109_render_video_filters_base(
            fmt,zoom,x_pos,y_pos,brightness,contrast,speed,
            ass_file=ass_file,reframe_track=reframe_track
        )

    # Below 1x the user's explicit framing wins: preserve the complete native
    # image instead of smart-cropping it, and use a blurred duplicate to fill
    # the social canvas. Still one FFmpeg pass.
    _vf=_gsf_v109_zoomout_filter(
        fmt,_zoom,x_pos,y_pos,brightness,contrast,speed,ass_file=ass_file
    )
    print(
        "GSF_ZOOMOUT_NATIVE_RENDER",
        "fmt="+str(fmt),
        "zoom="+str(round(_zoom,3)),
        flush=True,
    )
    return _vf
# ===== /V109 NATIVE ZOOM-OUT =====



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


def _gsf_probe_social_master(path):
    import json as _json
    probe=shutil.which("ffprobe") or "ffprobe"
    cmd=[
        probe,"-v","error",
        "-show_entries",
        "stream=index,codec_type,codec_name,codec_tag_string,profile,level,pix_fmt,width,height,avg_frame_rate,r_frame_rate,sample_rate,channels:format=format_name,duration,size,bit_rate",
        "-of","json",str(path)
    ]
    try:
        r=subprocess.run(
            cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            text=True,timeout=25
        )
        if r.returncode!=0:
            return {"ok":False,"error":(r.stderr or "")[-1200:]}
        data=_json.loads(r.stdout or "{}")
        return {"ok":True,"data":data}
    except Exception as e:
        return {"ok":False,"error":str(e)}


def _gsf_ratio_float(value):
    try:
        a,b=str(value or "0/1").split("/",1)
        b=float(b)
        return float(a)/b if b else 0.0
    except Exception:
        try:
            return float(value or 0.0)
        except Exception:
            return 0.0


def _gsf_validate_social_master(path,fmt="9:16 Short"):
    """Strict post-render gate for YouTube Shorts, TikTok and Reels."""
    probed=_gsf_probe_social_master(path)
    if not probed.get("ok"):
        return {
            "ok":False,
            "errors":["ffprobe non disponibile: "+str(probed.get("error",""))],
            "probe":{}
        }

    data=probed.get("data") or {}
    streams=data.get("streams") or []
    video=next((x for x in streams if x.get("codec_type")=="video"),{})
    audio=next((x for x in streams if x.get("codec_type")=="audio"),{})
    errors=[]

    fmt=_gsf_normalize_final_fmt(fmt)
    expected=(1080,1920) if fmt=="9:16 Short" else (1920,1080)
    if str(video.get("codec_name","")).lower()!="h264":
        errors.append("video non H.264")
    if str(video.get("codec_tag_string","")).lower()!="avc1":
        errors.append("tag video non avc1")
    pix_fmt=str(video.get("pix_fmt","")).lower()
    if pix_fmt not in ("yuv420p","yuvj420p"):
        errors.append(
            "pixel format non 4:2:0 8-bit compatibile "
            f"({video.get('pix_fmt') or 'sconosciuto'})"
        )
    if (int(video.get("width") or 0),int(video.get("height") or 0))!=expected:
        errors.append(
            f"risoluzione {video.get('width')}x{video.get('height')} invece di {expected[0]}x{expected[1]}"
        )

    fps=max(
        _gsf_ratio_float(video.get("avg_frame_rate")),
        _gsf_ratio_float(video.get("r_frame_rate"))
    )
    if fps<=0.0 or fps>60.05:
        errors.append(f"fps non compatibili ({fps:.2f})")

    if str(audio.get("codec_name","")).lower()!="aac":
        errors.append("audio non AAC")
    if int(audio.get("sample_rate") or 0)!=48000:
        errors.append("audio non 48 kHz")
    if int(audio.get("channels") or 0)!=2:
        errors.append("audio non stereo")

    format_name=str((data.get("format") or {}).get("format_name","")).lower()
    if not ("mp4" in format_name or "mov" in format_name):
        errors.append("contenitore non MP4/MOV")

    return {
        "ok":not errors,
        "errors":errors,
        "video":{
            "codec":video.get("codec_name"),
            "tag":video.get("codec_tag_string"),
            "profile":video.get("profile"),
            "level":video.get("level"),
            "pix_fmt":video.get("pix_fmt"),
            "width":video.get("width"),
            "height":video.get("height"),
            "fps":round(fps,3),
        },
        "audio":{
            "codec":audio.get("codec_name"),
            "sample_rate":audio.get("sample_rate"),
            "channels":audio.get("channels"),
        },
        "format":{
            "name":format_name,
            "duration":(data.get("format") or {}).get("duration"),
            "size":(data.get("format") or {}).get("size"),
            "bit_rate":(data.get("format") or {}).get("bit_rate"),
        },
    }


def _gsf_normalize_final_fmt(fmt):
    """Canonicalize editor/UI format labels before the final render pipeline."""
    raw=str(fmt or "").strip().lower()
    compact=raw.replace(" ","")
    if "9:16" in compact or "9x16" in compact:
        return "9:16 Short"
    if "16:9" in compact or "16x9" in compact:
        return "16:9"
    return str(fmt or "9:16 Short").strip() or "9:16 Short"


def _gsf_source_has_audio(path):
    """Return True when the source exposes at least one audio stream."""
    probe=shutil.which("ffprobe") or "ffprobe"
    try:
        r=subprocess.run(
            [
                probe,"-v","error",
                "-select_streams","a:0",
                "-show_entries","stream=index",
                "-of","csv=p=0",
                str(path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
        )
        return r.returncode==0 and bool((r.stdout or "").strip())
    except Exception:
        # Preserve the historical path if probing is unavailable.
        return True


def _gsf_render_core(source_path, output_path, start, duration, fmt='9:16 Short', zoom=1.0, x_pos=0, y_pos=0, brightness=0.0, contrast=1.0, speed=1.0, volume=100, subtitles_enabled=False, subtitle_mode='Automatici', subtitle_words=None, subtitle_text='', subtitle_time_origin=None, subtitle_font='Arial', subtitle_size=92, subtitle_x=50, subtitle_y=78, text_color='#FFFFFF', active_color='#FFD400', outline_color='#000000', normalize_audio=True, smart_reframe=False, reframe_cache_token=None, hook_text='', hook_duration=None, polish_audio=True, filter_preset='Originale', filter_intensity=0):
    """
    V43 final render core: Smart Reframe + hook + audio polish.

    ALWAYS renders from source_path, performs one final video encode,
    burns subtitles in that same pass, prefers Intel QSV and falls back
    to libx264 automatically.
    """
    fmt = _gsf_normalize_final_fmt(fmt)
    t0 = time.perf_counter()
    start = max(0.0, float(start))
    duration = max(0.1, float(duration))
    temp_dir = _gsf_session_mkdtemp('gsf_render_core_')
    ass_file = os.path.join(temp_dir, 'subs.ass')
    subtitle_error = None
    used_words = []
    reframe_meta = {'enabled': False, 'reason': 'disattivato', 'track': [], 'confidence': 0.0, 'movement': 0.0, 'samples': 0}
    reframe_cache_hit = False
    try:
        if subtitles_enabled and str(subtitle_mode) not in ('Nessuno', 'Manuale'):
            if subtitle_words:
                origin = start if subtitle_time_origin is None else float(subtitle_time_origin)
                used_words = _gsf_prepare_render_words(subtitle_words, origin, duration)
            else:
                used_words, subtitle_error = _gsf_render_transcribe_words_lowmem(source_path, start, duration)
        _hook_text = str(hook_text or '').strip()
        _hook_duration = float(hook_duration) if hook_duration is not None else min(2.0, max(1.15, float(duration) * 0.12))
        if subtitles_enabled and str(subtitle_mode) != 'Nessuno' or _hook_text:
            _gsf_write_render_ass(ass_file, used_words, fallback_text=subtitle_text if subtitles_enabled and str(subtitle_mode) == 'Manuale' else '', font=subtitle_font, size=subtitle_size, x_pct=subtitle_x, y_pct=subtitle_y, text_color=text_color, active_color=active_color, outline_color=outline_color, fmt=fmt, hook_text=_hook_text, hook_duration=_hook_duration, hook_y_pct=15)
        reframe_track = None
        if bool(smart_reframe) and fmt == '9:16 Short':
            reframe_meta, reframe_cache_hit = _gsf_smart_reframe_cached(source_path, start, duration, cache_token=reframe_cache_token)
            if reframe_meta.get('enabled'):
                reframe_track = reframe_meta.get('track') or None
        vf = _gsf_render_video_filters(fmt, zoom, x_pos, y_pos, brightness, contrast, speed, ass_file=ass_file if os.path.exists(ass_file) else None, reframe_track=reframe_track)
        _v106_final_fx = _gsf_v106_ffmpeg_filter(filter_preset, filter_intensity)
        if _v106_final_fx:
            vf = f'{vf},{_v106_final_fx}'
        af = _gsf_render_audio_filter(speed=speed, volume=volume, normalize_audio=normalize_audio, duration=duration, polish_audio=polish_audio)
        _gsf_has_audio = _gsf_source_has_audio(source_path)
        base = [FFMPEG_PATH, '-y', '-ss', str(start), '-i', str(source_path)]
        if not _gsf_has_audio:
            base += ['-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=48000']
        base += ['-t', str(duration), '-vf', vf]
        if _gsf_has_audio:
            base += ['-af', af]
        else:
            base += ['-map', '0:v:0', '-map', '1:a:0', '-af', af]
        attempts = [('libx264 HQ', base + ['-c:v', 'libx264', '-preset', 'fast', '-crf', '14', '-threads', '1', '-filter_threads', '1', '-x264-params', 'rc-lookahead=8:sync-lookahead=0:ref=2:bframes=2', '-x264-params', 'rc-lookahead=16:ref=2:bframes=2', '-profile:v', 'high', '-level:v', '4.2', '-tag:v', 'avc1', '-pix_fmt', 'yuv420p', '-fpsmax', '60', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-metadata:s:v:0', 'rotate=0', '-movflags', '+faststart', str(output_path)])]
        last_error = ''
        for encoder, cmd in attempts:
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception:
                pass
            _diag_timeout = max(420.0, min(3600.0, duration * 36.0))
            _diag_started = time.perf_counter()
            _gsf_perf_event('render_start', encoder=str(encoder), fmt=str(fmt), duration_seconds=round(float(duration), 3), timeout_seconds=round(float(_diag_timeout), 3))
            print('GSF_FINAL_RENDER_START', f'encoder={encoder}', f'fmt={fmt}', f'timeout={_diag_timeout:.1f}', flush=True)
            try:
                with _gsf_render_slot_v293('final'):
                    r = _gsf_v106_run_render_locked(cmd, _diag_timeout, encoder=encoder, fmt=fmt, duration=duration)
                _diag_elapsed = time.perf_counter() - _diag_started
                print('GSF_FINAL_RENDER_EXIT', f'encoder={encoder}', f'returncode={r.returncode}', f'elapsed={_diag_elapsed:.2f}', flush=True)
                _gsf_perf_event('render_end', encoder=str(encoder), fmt=str(fmt), duration_seconds=round(float(duration), 3), elapsed_seconds=round(float(_diag_elapsed), 3), returncode=int(r.returncode))
            except (subprocess.TimeoutExpired, TimeoutError):
                _diag_elapsed = time.perf_counter() - _diag_started
                _gsf_render_error = __import__('sys').exc_info()[1]
                if isinstance(_gsf_render_error, subprocess.TimeoutExpired):
                    print('GSF_FINAL_RENDER_TIMEOUT', f'encoder={encoder}', f'elapsed={_diag_elapsed:.2f}', flush=True)
                else:
                    print('GSF_FINAL_RENDER_EXCEPTION', f'encoder={encoder}', 'error=' + repr(str(_gsf_render_error)), flush=True)
                last_error = f'Render {encoder} interrotto: tempo massimo superato.'
                continue
            if r.returncode == 0 and os.path.exists(output_path) and (os.path.getsize(output_path) > 0):
                social_master = _gsf_validate_social_master(output_path, fmt=fmt)
                if not social_master.get('ok'):
                    last_error = 'Master MP4 non compatibile: ' + '; '.join(social_master.get('errors') or ['verifica fallita'])
                    continue
                return {'ok': True, 'path': str(output_path), 'encoder': encoder, 'seconds': round(time.perf_counter() - t0, 2), 'subtitle_words': len(used_words), 'subtitle_error': subtitle_error, 'smart_reframe': reframe_meta, 'reframe_cache_hit': bool(reframe_cache_hit), 'hook_text': _hook_text, 'audio_polish': bool(polish_audio), 'social_master': social_master, 'error': ''}
            last_error = (r.stderr or '')[-3500:]
        return {'ok': False, 'path': str(output_path), 'encoder': '', 'seconds': round(time.perf_counter() - t0, 2), 'subtitle_words': len(used_words), 'subtitle_error': subtitle_error, 'smart_reframe': reframe_meta, 'reframe_cache_hit': bool(reframe_cache_hit), 'hook_text': _hook_text, 'audio_polish': bool(polish_audio), 'error': last_error}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)














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
    digest=token.rsplit("|",1)[-1] if "|" in token else hashlib.md5(token.encode()).hexdigest()[:16]
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
            "gsf_smart_reframe_cache_v100",
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
    """"""
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

    cache={}  # V107.1: disk/session output is the cache; do not retain final MP4s in RAM
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
    _prescan_t0=time.perf_counter()
    try:
        from gsf_bucket_bridge import load_prescan_from_marker as _gsf_load_prescan
        scan = _gsf_load_prescan(
            GSF_PREVIEW_DIR,
            GSF_AI_ENGINE_VERSION
        )
    except Exception:
        scan = None

    _prescan_wait=round(time.perf_counter()-_prescan_t0,3)
    _prescan_hit=isinstance(scan,dict)
    if scan is None:
        _gsf_local_scan_t0=time.perf_counter()
        _gsf_perf_event(
            "local_scan_start",
            source=str(input_file),
            engine_version=str(GSF_AI_ENGINE_VERSION),
        )
        scan = _gsf_ai_scan_base(input_file)
        _gsf_perf_event(
            "local_scan_end",
            source=str(input_file),
            engine_version=str(GSF_AI_ENGINE_VERSION),
            elapsed_seconds=round(time.perf_counter()-_gsf_local_scan_t0,3),
        )

    scan.setdefault("meta",{}).update({"prescan_wait_seconds":_prescan_wait,"prescan_hit":_prescan_hit})
    if not any((scan.get("meta") or {}).get(key) for key in ("audio_error","video_error")):
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
            error=""
            if r.returncode != 0 and (cmd is cmd_video or _gsf_source_has_audio(input_file)):
                error="Scansione " + ("video" if cmd is cmd_video else "audio") + " non riuscita"
            return r, time.perf_counter()-t0, error
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
    duration=max(0.1,float(clip_duration))
    _scan_t0=time.perf_counter()
    scan,scan_cache_hit=_gsf_ai_scan_cached(
        input_file,cache_token=cache_token
    )
    scan_request_seconds=time.perf_counter()-_scan_t0
    scan_meta=scan.get("meta",{}) or {}
    if scan_meta.get("audio_error") or scan_meta.get("video_error"):
        raise RuntimeError("Analisi del gameplay non riuscita. Riprova o apri il video nell’Editor.")
    adaptive_scan=bool(scan_meta.get("adaptive",False))
    voice_cache_hits=0
    voice_checks=0
    forced_voice_checks=0
    refine_cache_hits=0
    refine_checks=0
    n=min(len(scan.get("audio",[])),len(scan.get("motion",[])))
    step=float(scan.get("step",0.5) or 0.5)
    total=n*step
    if n<=0 or total<=0:
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
    shortlist_target=8
    coarse_target=10 if adaptive_scan else shortlist_target
    min_gap=max(3.0,duration*0.35)

    for item in candidates:
        if any(abs(item[1]-x[1])<min_gap for x in shortlist):
            continue
        shortlist.append(item)
        if len(shortlist)>=coarse_target:
            break

    _refine_t0=time.perf_counter()
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

    refine_seconds=time.perf_counter()-_refine_t0
    voice_seconds=0.0
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
        _voice_t0=time.perf_counter()
        _voice_result,_voice_hit=_gsf_ai_voice_cached(
            input_file,start,duration,
            cache_token=cache_token,
            force=_force_reaction_voice
        )
        voice_seconds+=time.perf_counter()-_voice_t0
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
        "scan_request_seconds":round(scan_request_seconds,3),
        "motion_refine_seconds":round(refine_seconds,3),
        "voice_seconds":round(voice_seconds,3),
        "scan_cache_hit":bool(scan_cache_hit),
        "prescan_wait_seconds":float(scan_meta.get("prescan_wait_seconds",0) or 0),
        "prescan_hit":bool(scan_meta.get("prescan_hit",False)),
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

# ===== V108 GAME VISION + EVENT MAP =====
GSF_V108_GAME_VISION = True
try:
    from game_vision_v108 import (
        build_event_map as _gsf_v108_build_event_map,
        tag_chosen_moments as _gsf_v108_tag_chosen,
        infer_game_genre as _gsf_v108_infer_genre,
        genre_score_multiplier as _gsf_v108_genre_multiplier,
    )
except Exception as _gsf_v108_import_exc:
    raise RuntimeError("V108 Game Vision helpers unavailable: "+str(_gsf_v108_import_exc))


def _gsf_v108_game_hint():
    try:
        for _key in ("gioco","game_name","selected_game","titolo_gioco"):
            _value=st.session_state.get(_key)
            if _value:
                return str(_value)
    except Exception:
        pass
    try:
        _value=globals().get("gioco")
        if _value:
            return str(_value)
    except Exception:
        pass
    return ""


_gsf_v108_score_base=_gsf_score_ai_window
def _gsf_score_ai_window(profile,f):
    """
    V108 keeps the proven base score and only resolves close calls using the
    game profile. The multiplier is deliberately bounded to protect quality.
    """
    _base=float(_gsf_v108_score_base(profile,f))
    try:
        _genre=_gsf_v108_infer_genre(_gsf_v108_game_hint())
        _mult=float(_gsf_v108_genre_multiplier(_genre,profile,f))
        return max(0.0,_base*_mult)
    except Exception:
        return max(0.0,_base)


_gsf_v108_rank_base=_gsf_ai_rank_v3
def _gsf_ai_rank_v3(input_file, modalita, clip_duration=15, numero_clip=3, cache_token=None):
    """
    V108: expose the exact same intelligence used for the three moments.
    _gsf_ai_scan_cached is called again only after ranking, therefore it is a
    cache read, not a second media analysis.
    """
    _chosen,_diagnostics=_gsf_v108_rank_base(
        input_file,modalita,
        clip_duration=clip_duration,
        numero_clip=numero_clip,
        cache_token=cache_token,
    )
    if not isinstance(_diagnostics,dict):
        _diagnostics={}
    try:
        _scan,_scan_hit=_gsf_ai_scan_cached(input_file,cache_token=cache_token)
        _events=(_scan or {}).get("event_map_v108")
        if not isinstance(_events,list):
            _events=_gsf_v108_build_event_map(_scan,max_events=18)
            try:
                _scan["event_map_v108"]=_events
            except Exception:
                pass

        _genre=_gsf_v108_infer_genre(_gsf_v108_game_hint())
        _duration=max(0.1,float(clip_duration))
        _tagged=_gsf_v108_tag_chosen(
            _events,_chosen,_diagnostics,_duration
        )

        _diagnostics["__event_map__"]=_tagged
        _diagnostics["__game_genre__"]=_genre
        _meta=_diagnostics.setdefault("__meta__",{})
        if isinstance(_meta,dict):
            _meta["event_map"]="v108-shared-prescan"
            _meta["event_map_count"]=len(_tagged)
            _meta["event_map_cache_hit"]=bool(_scan_hit)
            _meta["game_genre"]=_genre

        st.session_state["gsf_v108_event_map"]=_tagged
        st.session_state["gsf_v108_game_genre"]=_genre
        st.session_state["gsf_v108_chosen_moments"]=[
            {"rank":_i+1,"score":float(_item[0]),"start":float(_item[1])}
            for _i,_item in enumerate(_chosen or [])
            if isinstance(_item,(list,tuple)) and len(_item)>=2
        ]
        st.session_state["gsf_v108_event_map_engine"]="shared-prescan-v1"
        print(
            "GSF_V108_EVENT_MAP",
            "events="+str(len(_tagged)),
            "chosen="+str(len(_chosen or [])),
            "genre="+str(_genre),
            "scan_cache_hit="+str(bool(_scan_hit)),
            flush=True,
        )
    except Exception as _gsf_v108_event_exc:
        print("GSF_V108_EVENT_MAP_WARN",repr(str(_gsf_v108_event_exc)),flush=True)
    return _chosen,_diagnostics
# ===== /V108 GAME VISION + EVENT MAP =====

# ===== V112 GAME BRAIN =====
GSF_V112_GAME_BRAIN=True
try:
    from game_brain_v112 import rerank_moments as _gsf_v112_rerank
except Exception as _gsf_v112_import_exc:
    raise RuntimeError("V112 Game Brain unavailable: "+str(_gsf_v112_import_exc))

_gsf_v112_rank_base=_gsf_ai_rank_v3
def _gsf_ai_rank_v3(input_file, modalita, clip_duration=15, numero_clip=3, cache_token=None):
    _target=max(1,int(numero_clip or 3))
    _pool_target=max(8,_target)
    _pool,_diagnostics=_gsf_v112_rank_base(
        input_file,modalita,
        clip_duration=clip_duration,
        numero_clip=_pool_target,
        cache_token=cache_token,
    )
    if not isinstance(_diagnostics,dict):
        _diagnostics={}
    _mode=str(modalita or "").lower()
    _v291_forced_profile=str(
        st.session_state.get("gsf_v291_engine_profile") or ""
    ).lower()
    if _v291_forced_profile in ("auto","director","action","reaction"):
        _profile=_v291_forced_profile
    elif "reaz" in _mode or "reaction" in _mode:
        _profile="reaction"
    elif "azione" in _mode or "action" in _mode:
        _profile="action"
    elif "miglior" in _mode or "best" in _mode or "director" in _mode:
        _profile="director"
    else:
        _profile="auto"
    try:
        _genre=str(st.session_state.get("gsf_v108_game_genre") or "Auto")
    except Exception:
        _genre="Auto"
    _events=_diagnostics.get("__event_map__") or []
    _chosen,_brain=_gsf_v112_rerank(
        _pool,_diagnostics,
        clip_duration=float(clip_duration),
        numero_clip=_target,
        profile=_profile,
        genre=_genre,
        events=_events,
    )
    # V125: persistent rank override. A replacement is a real ranked moment,
    # not a cosmetic UI swap, so preview/editor/final render all receive it.
    try:
        _overrides=st.session_state.get("gsf_v125_rank_overrides") or {}
        if isinstance(_overrides,dict) and _overrides:
            _selected_rows=list((_brain or {}).get("selected") or [])
            _alternate_rows=list((_brain or {}).get("alternates") or [])
            for _rank_raw,_start_raw in list(_overrides.items()):
                try:
                    _rank=int(_rank_raw)
                    _wanted=float(_start_raw)
                except Exception:
                    continue
                _idx=_rank-1
                if _idx<0 or _idx>=len(_selected_rows) or _idx>=len(_chosen):
                    continue
                _alt=None
                for _row in _alternate_rows:
                    if not isinstance(_row,dict):
                        continue
                    if abs(float(_row.get("start") or 0.0)-_wanted)<=0.35:
                        _alt=dict(_row)
                        break
                if _alt is None:
                    # The requested moment may already be selected after a rerun.
                    for _row in _selected_rows:
                        if isinstance(_row,dict) and abs(float(_row.get("start") or 0.0)-_wanted)<=0.35:
                            _alt=dict(_row)
                            break
                if _alt is None:
                    continue
                _old=dict(_selected_rows[_idx] or {})
                _alt["rank"]=_rank
                _alt["replaced_from_start"]=float(_old.get("start") or 0.0)
                _alt["replacement_override"]=True
                _selected_rows[_idx]=_alt
                _chosen[_idx]=(
                    float(_alt.get("brain_score") or _chosen[_idx][0]),
                    float(_alt.get("start") or _wanted),
                )
                _alternate_rows=[
                    row for row in _alternate_rows
                    if not (
                        isinstance(row,dict)
                        and abs(float(row.get("start") or 0.0)-float(_alt.get("start") or _wanted))<=0.35
                    )
                ]
                if _old:
                    _old["replacement_candidate"]=True
                    _alternate_rows.insert(0,_old)
            if isinstance(_brain,dict):
                _brain["selected"]=_selected_rows
                _brain["alternates"]=_alternate_rows[:4]
                _brain["rank_overrides"]={
                    str(k):float(v) for k,v in _overrides.items()
                    if str(v).strip()
                }
    except Exception as _v125_override_exc:
        print("GSF_V125_OVERRIDE_WARN",repr(str(_v125_override_exc))[:220],flush=True)
    try:
        if isinstance(_brain,dict):
            _v130_builder=__import__(
                "one_click_v130",fromlist=["build_one_click_package"]
            ).build_one_click_package
            _brain["one_click"]=_v130_builder(
                _brain,
                clip_duration=float(clip_duration),
                genre=_genre,
                profile=_profile,
                target_count=min(3,max(1,int(_target or 3))),
            )
    except Exception as _v130_package_exc:
        print("GSF_V130_PACKAGE_WARN",repr(str(_v130_package_exc))[:220],flush=True)

    try:
        _clean_events=[]
        for _event in (_events or []):
            if not isinstance(_event,dict):
                continue
            _row=dict(_event)
            _row.pop("selected_rank",None)
            _row.pop("selected_start",None)
            _row.pop("selected_score",None)
            _clean_events.append(_row)
        if "_gsf_v108_tag_chosen" in globals():
            _clean_events=_gsf_v108_tag_chosen(
                _clean_events,_chosen,_diagnostics,max(1.0,float(clip_duration))
            )
        _diagnostics["__event_map__"]=_clean_events
        st.session_state["gsf_v108_event_map"]=_clean_events
        st.session_state["gsf_v112_brain_context"]=_brain
        st.session_state["gsf_v124_director_context"]={
            "engine":str(_brain.get("engine") or "game-brain-v124-ai-director"),
            "selected":list(_brain.get("selected") or []),
            "alternates":list(_brain.get("alternates") or []),
        }
        _top=(list(_brain.get("selected") or []) or [{}])[0]
        _top_plan=dict((_top or {}).get("director_plan") or {})
        st.session_state["gsf_v124_social_pack"]=dict(
            ((_top_plan.get("text") or {}).get("social") or {})
        )
        st.session_state["gsf_v108_chosen_moments"]=[
            {"rank":_i+1,"score":float(_item[0]),"start":float(_item[1])}
            for _i,_item in enumerate(_chosen or [])
            if isinstance(_item,(list,tuple)) and len(_item)>=2
        ]
    except Exception as _brain_state_exc:
        print("GSF_V112_STATE_WARN",repr(str(_brain_state_exc)),flush=True)
    _diagnostics["__brain_v112__"]=_brain
    _meta=_diagnostics.setdefault("__meta__",{})
    if isinstance(_meta,dict):
        _meta["game_brain"]="v124-ai-director"
        _meta["candidate_pool"]=len(_pool or [])
        _meta["final_moments"]=len(_chosen or [])
    print(
        "GSF_V124_AI_DIRECTOR",
        "pool="+str(len(_pool or [])),
        "chosen="+str(len(_chosen or [])),
        "profile="+_profile,
        "genre="+_genre,
        flush=True,
    )
    return _chosen,_diagnostics
# ===== /V112 GAME BRAIN =====




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


def _gsf_write_social_status_v148_base(platform, state, message, **extra):
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

def _gsf_v148_api(path,payload):
    try:
        _u=__import__("urllib.request",fromlist=["Request","urlopen"])
        _j=__import__("json")
        _os=__import__("os")
        _port=str(_os.environ.get("GSF_DIRECT_UPLOAD_PORT","8502") or "8502")
        _raw=_j.dumps(dict(payload or {}),ensure_ascii=False,separators=(",",":")).encode("utf-8")
        _req=_u.Request(
            "http://127.0.0.1:"+_port+str(path),
            data=_raw,
            headers={
                "Content-Type":"application/json",
                "X-GSF-Session-ID":str(GSF_SESSION_ID),
            },
            method="POST",
        )
        return _j.loads(_u.urlopen(_req,timeout=2.0).read().decode("utf-8"))
    except Exception as _exc:
        print("GSF_V148_API_WARN",str(path),repr(str(_exc))[:220],flush=True)
        return {}


def _gsf_write_social_status(*args,**kwargs):
    _result=_gsf_write_social_status_v148_base(*args,**kwargs)
    try:
        _platform=str(args[0] if len(args)>0 else kwargs.get("platform") or "")
        _state=str(args[1] if len(args)>1 else kwargs.get("state") or "")
        if _state.lower()=="ready":
            _content_id=""
            _id_type=""
            for _key in ("video_id","media_id","post_id","publish_id","content_id","id"):
                _value=str(kwargs.get(_key) or "").strip()
                if _value:
                    _content_id=_value
                    _id_type=_key
                    break
            if _content_id:
                _recipe=st.session_state.get("gsf_final_recipe") or {}
                _payload={
                    "platform":_platform,
                    "content_id":_content_id,
                    "id_type":_id_type,
                    "content_fingerprint":str(
                        (_recipe or {}).get("ai_content_fingerprint")
                        or ((_recipe or {}).get("director_runtime_v142") or {}).get("content_fingerprint")
                        or ""
                    ),
                    "metadata":{
                        "ab_strategy":str((_recipe or {}).get("ai_ab_strategy") or ""),
                        "start":float((_recipe or {}).get("start") or 0.0),
                        "duration":float((_recipe or {}).get("duration") or 0.0),
                        "game":str(st.session_state.get("gioco") or ""),
                    },
                }
                _registered=_gsf_v148_api("/social-analytics/register",_payload)
                if (_registered or {}).get("ok"):
                    st.session_state["gsf_v148_analytics_registered"]={
                        "platform":_platform,
                        "content_id":_content_id,
                        "id_type":_id_type,
                    }
                    print(
                        "GSF_V148_ANALYTICS_REGISTERED",
                        _platform,
                        _id_type+"="+_content_id[:48],
                        flush=True,
                    )
    except Exception as _exc:
        print("GSF_V148_REGISTER_WARN",repr(str(_exc))[:240],flush=True)
    return _result




def _gsf_publish_social_upload(video, platform, pack_override=None):
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
    game = _gsf_v1053_detect_game()
    tone = st.session_state.get("tono_social", "Gaming forte")
    if isinstance(pack_override,dict) and pack_override:
        pack=dict(pack_override)
    else:
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
            result = _gsf_tiktok_direct_post(bytes(video), pack)
            if not result.get("ok"):
                message = str(result.get("error", "Pubblicazione TikTok non riuscita"))
                _gsf_write_social_status(platform, "error", message)
                return False, message, exported
            _privacy=str(result.get("privacy","") or "")
            message = (
                "Video pubblicato su TikTok."
                if _privacy!="SELF_ONLY"
                else "Video pubblicato su TikTok in modalità privata (SELF_ONLY)."
            )
            _gsf_write_social_status(
                platform, "ready", message,
                publish_id=result.get("publish_id", ""),
                privacy=_privacy,
            )
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
        st.success("✅ " + str(status.get("message") or ("Pubblicato su " + platform + ".")))
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
GSF_TIKTOK_DIRECT_INIT = "https://open.tiktokapis.com/v2/post/publish/video/init/"
GSF_TIKTOK_CREATOR_INFO = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
GSF_TIKTOK_STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
GSF_TIKTOK_SCOPES = "user.info.basic,video.publish"


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
        "instagram_app_id":"GSF_INSTAGRAM_APP_ID",
        "instagram_app_secret":"GSF_INSTAGRAM_APP_SECRET",
        "meta_app_id":"GSF_META_APP_ID",
        "meta_app_secret":"GSF_META_APP_SECRET",
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
    prefs.setdefault("youtube_privacy","public")
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


def _gsf_tiktok_credentials_legacy():
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
    if "video.publish" not in scopes:
        return None,config,"Manca lo scope TikTok video.publish"

    return token,config,""

def _gsf_shared_tiktok_s3():
    import boto3
    from botocore.config import Config
    bucket=os.environ.get("GSF_S3_BUCKET","")
    access=os.environ.get("GSF_S3_ACCESS_KEY_ID","")
    secret=os.environ.get("GSF_S3_SECRET_ACCESS_KEY","")
    endpoint=os.environ.get("GSF_S3_ENDPOINT","")
    region=os.environ.get("GSF_S3_REGION","auto") or "auto"
    if not (bucket and access and secret and endpoint):
        return None,bucket
    client=boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access,
        aws_secret_access_key=secret,
        region_name=region,
        config=Config(signature_version="s3v4",s3={"addressing_style":"virtual"}),
    )
    return client,bucket


def _gsf_shared_tiktok_load():
    try:
        client,bucket=_gsf_shared_tiktok_s3()
        if client is None:
            return {}
        obj=client.get_object(Bucket=bucket,Key=f"social-connections/{GSF_SESSION_ID}/tiktok.json")
        payload=json.loads(obj["Body"].read().decode("utf-8"))
        return payload if isinstance(payload,dict) else {}
    except Exception:
        return {}


def _gsf_shared_tiktok_save(payload):
    try:
        client,bucket=_gsf_shared_tiktok_s3()
        if client is None:
            return False
        client.put_object(
            Bucket=bucket,
            Key=f"social-connections/{GSF_SESSION_ID}/tiktok.json",
            Body=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
            CacheControl="no-store",
        )
        return True
    except Exception:
        return False


def _gsf_shared_tiktok_refresh(token):
    import urllib.parse as _up
    import urllib.request as _ur
    refresh=str((token or {}).get("refresh_token","") or "")
    cfg=_gsf_app_credentials()
    client_key=str(cfg.get("tiktok_client_key","") or "")
    client_secret=str(cfg.get("tiktok_client_secret","") or "")
    if not (refresh and client_key and client_secret):
        return token
    form=_up.urlencode({
        "client_key":client_key,
        "client_secret":client_secret,
        "grant_type":"refresh_token",
        "refresh_token":refresh,
    }).encode("utf-8")
    req=_ur.Request(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data=form,
        headers={"Content-Type":"application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with _ur.urlopen(req,timeout=45) as resp:
            payload=json.loads(resp.read().decode("utf-8"))
        if not payload.get("access_token"):
            return token
        now=time.time()
        payload["saved_at"]=now
        payload["expires_at"]=now+int(payload.get("expires_in",0) or 0)
        payload["refresh_expires_at"]=now+int(payload.get("refresh_expires_in",0) or 0)
        _gsf_shared_tiktok_save(payload)
        return payload
    except Exception:
        return token


def _gsf_tiktok_credentials():
    token=_gsf_shared_tiktok_load()
    if token.get("access_token"):
        now=time.time()
        expires_at=float(token.get("expires_at",0) or 0)
        if expires_at and expires_at<=now+300 and token.get("refresh_token"):
            token=_gsf_shared_tiktok_refresh(token)
            expires_at=float(token.get("expires_at",0) or 0)
        if token.get("access_token") and (not expires_at or expires_at>now):
            return token,_gsf_app_credentials(),""
    return _gsf_tiktok_credentials_legacy()



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
    if "video.publish" not in scope:
        return False,(
            "Login riuscito ma TikTok non ha concesso video.publish. "
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


def _gsf_tiktok_creator_info():
    token,config,error=_gsf_tiktok_credentials()
    if token is None:
        return {"ok":False,"error":error or "TikTok non collegato"}

    res=_gsf_http_json(
        GSF_TIKTOK_CREATOR_INFO,
        method="POST",
        headers={
            "Authorization":f"Bearer {token.get('access_token','')}",
            "Content-Type":"application/json; charset=UTF-8",
        },
        json_body={}
    )
    payload=res.get("data") or {}
    api_error=payload.get("error") or {}
    if not res.get("ok") or (
        isinstance(api_error,dict)
        and api_error.get("code") not in (None,"","ok")
    ):
        return {"ok":False,"error":str(payload or res.get("error"))}

    data=payload.get("data") or {}
    return {
        "ok":True,
        "username":str(data.get("creator_username","") or ""),
        "nickname":str(data.get("creator_nickname","") or ""),
        "privacy_level_options":list(data.get("privacy_level_options") or []),
        "comment_disabled":bool(data.get("comment_disabled",False)),
        "duet_disabled":bool(data.get("duet_disabled",False)),
        "stitch_disabled":bool(data.get("stitch_disabled",False)),
        "max_video_post_duration_sec":int(data.get("max_video_post_duration_sec",0) or 0),
        "error":"",
    }


def _gsf_tiktok_direct_post(video_bytes,pack,progress_callback=None):
    """V104 official TikTok Direct Post. No draft hand-off."""
    token,config,error=_gsf_tiktok_credentials()
    if token is None:
        return {"ok":False,"error":error or "TikTok non collegato"}
    if not isinstance(video_bytes,(bytes,bytearray)) or len(video_bytes)<1:
        return {"ok":False,"error":"Master video non disponibile"}

    creator=_gsf_tiktok_creator_info()
    if not creator.get("ok"):
        return creator

    options=[
        str(x) for x in creator.get("privacy_level_options",[]) or []
        if str(x)
    ]
    # One explicit click on TikTok is the publish consent. Prefer public when
    # TikTok offers it; unaudited clients naturally fall back to SELF_ONLY.
    if "PUBLIC_TO_EVERYONE" in options:
        privacy="PUBLIC_TO_EVERYONE"
    elif "SELF_ONLY" in options:
        privacy="SELF_ONLY"
    elif options:
        privacy=options[0]
    else:
        return {"ok":False,"error":"TikTok non ha restituito opzioni di privacy"}

    caption=str(
        (pack or {}).get("selected_caption",(pack or {}).get("caption",""))
        or ""
    ).strip()[:2200]

    access_token=str(token.get("access_token","") or "")
    size=len(video_bytes)
    chunk_size,total_count=_gsf_tiktok_chunk_plan(size)

    init=_gsf_http_json(
        GSF_TIKTOK_DIRECT_INIT,
        method="POST",
        headers={
            "Authorization":f"Bearer {access_token}",
            "Content-Type":"application/json; charset=UTF-8",
        },
        json_body={
            "post_info":{
                "title":caption,
                "privacy_level":privacy,
                "disable_comment":bool(creator.get("comment_disabled",False)),
                "disable_duet":bool(creator.get("duet_disabled",False)),
                "disable_stitch":bool(creator.get("stitch_disabled",False)),
            },
            "source_info":{
                "source":"FILE_UPLOAD",
                "video_size":size,
                "chunk_size":chunk_size,
                "total_chunk_count":total_count,
            }
        }
    )

    payload=init.get("data") or {}
    api_error=payload.get("error") or {}
    _api_code=str(api_error.get("code","") or "") if isinstance(api_error,dict) else ""
    if (
        _api_code=="unaudited_client_can_only_post_to_private_accounts"
        and privacy!="SELF_ONLY"
        and "SELF_ONLY" in options
    ):
        privacy="SELF_ONLY"
        init=_gsf_http_json(
            GSF_TIKTOK_DIRECT_INIT,
            method="POST",
            headers={
                "Authorization":f"Bearer {access_token}",
                "Content-Type":"application/json; charset=UTF-8",
            },
            json_body={
                "post_info":{
                    "title":caption,
                    "privacy_level":privacy,
                    "disable_comment":bool(creator.get("comment_disabled",False)),
                    "disable_duet":bool(creator.get("duet_disabled",False)),
                    "disable_stitch":bool(creator.get("stitch_disabled",False)),
                },
                "source_info":{
                    "source":"FILE_UPLOAD",
                    "video_size":size,
                    "chunk_size":chunk_size,
                    "total_chunk_count":total_count,
                }
            }
        )
        payload=init.get("data") or {}
        api_error=payload.get("error") or {}

    if not init.get("ok") or (
        isinstance(api_error,dict)
        and api_error.get("code") not in (None,"","ok")
    ):
        return {"ok":False,"error":str(payload or init.get("error"))}

    data=payload.get("data") or {}
    upload_url=str(data.get("upload_url","") or "")
    publish_id=str(data.get("publish_id","") or "")
    if not upload_url or not publish_id:
        return {"ok":False,"error":"TikTok non ha restituito upload_url/publish_id"}

    sent=0
    while sent<size:
        remaining=size-sent
        if total_count<=1:
            this_size=remaining
        else:
            part_index=sent//chunk_size
            this_size=remaining if part_index>=total_count-1 else min(chunk_size,remaining)

        end=sent+this_size-1
        req=Request(
            upload_url,
            data=bytes(video_bytes[sent:sent+this_size]),
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
            return {"ok":False,"error":str(e),"publish_id":publish_id}

        sent+=this_size
        if progress_callback:
            try:
                progress_callback(int(sent/size*100))
            except Exception:
                pass

    return {
        "ok":True,
        "publish_id":publish_id,
        "privacy":privacy,
        "creator":creator.get("username") or creator.get("nickname") or "",
        "error":"",
    }


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

def _gsf_shared_instagram_load():
    try:
        client,bucket=_gsf_shared_tiktok_s3()
        if client is None:
            return {}
        obj=client.get_object(
            Bucket=bucket,
            Key=f"social-connections/{GSF_SESSION_ID}/instagram.json"
        )
        payload=json.loads(obj["Body"].read().decode("utf-8"))
        return payload if isinstance(payload,dict) else {}
    except Exception:
        return {}


def _gsf_shared_instagram_save(payload):
    try:
        client,bucket=_gsf_shared_tiktok_s3()
        if client is None:
            return False
        client.put_object(
            Bucket=bucket,
            Key=f"social-connections/{GSF_SESSION_ID}/instagram.json",
            Body=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
            CacheControl="no-store",
        )
        return True
    except Exception:
        return False


def _gsf_instagram_config():
    cfg=_gsf_read_json_file(GSF_INSTAGRAM_CONFIG)
    if cfg.get("ig_user_id") and cfg.get("access_token"):
        return cfg
    shared=_gsf_shared_instagram_load()
    if isinstance(shared,dict) and shared.get("ig_user_id") and shared.get("access_token"):
        try:
            _gsf_secure_write_json(GSF_INSTAGRAM_CONFIG,shared)
        except Exception:
            pass
        return shared
    return cfg



def _gsf_instagram_validate(ig_user_id,access_token,api_host=None):
    ig_user_id=str(ig_user_id or "").strip()
    access_token=str(access_token or "").strip()
    if not ig_user_id or not access_token:
        return False,"","Inserisci IG User ID e access token"

    if not api_host:
        cfg=_gsf_instagram_config()
        api_host=str(cfg.get("api_host","") or "").strip()
    if not api_host:
        api_host=(
            "https://graph.instagram.com"
            if access_token.upper().startswith(("IGAA","IGQV","IG"))
            else "https://graph.facebook.com"
        )
    api_host=str(api_host).rstrip("/")

    url=(
        api_host+"/"
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



def _gsf_instagram_connect(ig_user_id,access_token,api_host=None,oauth_mode=None):
    if not api_host:
        api_host=(
            "https://graph.instagram.com"
            if str(access_token or "").upper().startswith(("IGAA","IGQV","IG"))
            else "https://graph.facebook.com"
        )
    ok,username,error=_gsf_instagram_validate(
        ig_user_id,access_token,api_host=api_host
    )
    if not ok:
        return False,error

    _payload={
        "ig_user_id":str(ig_user_id).strip(),
        "access_token":str(access_token).strip(),
        "username":username,
        "api_host":str(api_host).rstrip("/"),
        "oauth_mode":str(oauth_mode or ""),
    }
    _gsf_secure_write_json(GSF_INSTAGRAM_CONFIG,_payload)
    _gsf_shared_instagram_save(_payload)
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
    """
    In Railway web mode, stage the finished MP4 in the existing private S3
    bucket and give Meta a short-lived signed GET URL. This avoids the /media
    cookie protection that external Meta fetchers cannot satisfy.
    """
    if GSF_WEB_MODE:
        if not isinstance(video_bytes,(bytes,bytearray)) or len(video_bytes)<1024:
            return {"ok":False,"error":"Master video non disponibile"}

        client,bucket=_gsf_shared_tiktok_s3()
        if client is None or not bucket:
            return {
                "ok":False,
                "error":"Storage temporaneo Instagram non disponibile sul server"
            }

        digest=hashlib.sha256(bytes(video_bytes)).hexdigest()[:20]
        key=f"social-stage/{GSF_SESSION_ID}/instagram-{digest}.mp4"

        try:
            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=bytes(video_bytes),
                ContentType="video/mp4",
                CacheControl="no-store",
            )
            media_url=client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket":bucket,
                    "Key":key,
                    "ResponseContentType":"video/mp4",
                },
                ExpiresIn=900,
            )
            return _gsf_instagram_publish_reel(
                media_url,
                pack,
                share_to_feed=share_to_feed,
                progress_callback=progress_callback
            )
        except Exception as e:
            return {"ok":False,"error":"Staging Instagram: "+str(e)}
        finally:
            try:
                client.delete_object(Bucket=bucket,Key=key)
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
    graph_base=str(cfg.get("api_host","") or "https://graph.facebook.com").rstrip("/")
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

    create_url=graph_base+"/"+quote(ig_user_id,safe="")+"/media"
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
            graph_base+"/"
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

    publish_url=graph_base+"/"+quote(ig_user_id,safe="")+"/media_publish"
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
        graph_base+"/"
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


def _gsf_shared_youtube_load():
    try:
        client,bucket=_gsf_shared_tiktok_s3()
        if client is None:
            return {}
        obj=client.get_object(
            Bucket=bucket,
            Key=f"social-connections/{GSF_SESSION_ID}/youtube.json"
        )
        payload=json.loads(obj["Body"].read().decode("utf-8"))
        return payload if isinstance(payload,dict) else {}
    except Exception:
        return {}


def _gsf_shared_youtube_save(payload):
    try:
        client,bucket=_gsf_shared_tiktok_s3()
        if client is None:
            return False
        client.put_object(
            Bucket=bucket,
            Key=f"social-connections/{GSF_SESSION_ID}/youtube.json",
            Body=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
            CacheControl="no-store",
        )
        return True
    except Exception:
        return False


def _gsf_youtube_save_credentials(creds):
    GSF_YOUTUBE_DIR.mkdir(parents=True,exist_ok=True)
    _raw=creds.to_json()
    GSF_YOUTUBE_TOKEN.write_text(
        _raw,
        encoding="utf-8"
    )
    try:
        os.chmod(GSF_YOUTUBE_TOKEN,0o600)
    except Exception:
        pass
    try:
        _payload=json.loads(_raw)
        if isinstance(_payload,dict):
            _gsf_shared_youtube_save(_payload)
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
        _shared=_gsf_shared_youtube_load()
        if isinstance(_shared,dict) and _shared.get("token"):
            try:
                GSF_YOUTUBE_DIR.mkdir(parents=True,exist_ok=True)
                GSF_YOUTUBE_TOKEN.write_text(
                    json.dumps(_shared,ensure_ascii=False),
                    encoding="utf-8"
                )
                try:
                    os.chmod(GSF_YOUTUBE_TOKEN,0o600)
                except Exception:
                    pass
            except Exception:
                pass

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
        _client_id=str(os.environ.get("GSF_YOUTUBE_CLIENT_ID","") or "").strip()
        _client_secret=str(os.environ.get("GSF_YOUTUBE_CLIENT_SECRET","") or "").strip()
        _redirect=_gsf_public_app_url()
        if _client_id and _client_secret:
            return {
                "web":{
                    "client_id":_client_id,
                    "client_secret":_client_secret,
                    "auth_uri":"https://accounts.google.com/o/oauth2/auth",
                    "token_uri":"https://oauth2.googleapis.com/token",
                    "redirect_uris":[_redirect] if _redirect else [],
                }
            },""
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
    if "video.publish" not in str(token.get("scope", "") or ""):
        return False, "TikTok non ha concesso lo scope video.upload."
    _gsf_tiktok_save_config(client_key, client_secret)
    _gsf_tiktok_save_token(token)
    return True, "TikTok collegato."


GSF_META_AUTH_URL = "https://www.facebook.com/dialog/oauth"
GSF_META_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"
GSF_META_SCOPES = "pages_show_list,instagram_basic,instagram_content_publish,pages_read_engagement"


def _gsf_instagram_web_auth_url():
    cfg=_gsf_app_credentials()
    app_id=str(cfg.get("meta_app_id","") or "").strip()
    app_secret=str(cfg.get("meta_app_secret","") or "").strip()
    redirect_uri=_gsf_public_app_url()
    if not app_id or not app_secret:
        # Preserve the existing pre-provisioned server connection path.
        uid=str(cfg.get("instagram_user_id","") or "").strip()
        token=str(cfg.get("instagram_access_token","") or "").strip()
        if uid and token:
            ok,msg=_gsf_instagram_connect(uid,token)
            return "","" if ok else msg
        return "","Instagram non è configurato sul server."
    if not redirect_uri or not redirect_uri.lower().startswith("https://"):
        return "","Instagram Web richiede GSF_PUBLIC_APP_URL in HTTPS."

    state=secrets.token_urlsafe(32)
    _gsf_write_oauth_state(state,{
        "platform":"Instagram",
        "redirect_uri":redirect_uri,
    })
    params={
        "client_id":app_id,
        "redirect_uri":redirect_uri,
        "state":state,
        "response_type":"code",
        "scope":GSF_META_SCOPES,
    }
    return GSF_META_AUTH_URL+"?"+urlencode(params),""


def _gsf_instagram_web_complete(code,state,pending):
    cfg=_gsf_app_credentials()
    app_id=str(cfg.get("meta_app_id","") or "").strip()
    app_secret=str(cfg.get("meta_app_secret","") or "").strip()
    redirect_uri=str((pending or {}).get("redirect_uri","") or _gsf_public_app_url()).strip()
    if not app_id or not app_secret or not redirect_uri:
        return False,"Configurazione Instagram/Meta incompleta sul server."

    token_url=GSF_META_TOKEN_URL+"?"+urlencode({
        "client_id":app_id,
        "client_secret":app_secret,
        "redirect_uri":redirect_uri,
        "code":str(code),
    })
    token_res=_gsf_http_json(token_url,method="GET",timeout=45)
    token_data=token_res.get("data") or {}
    user_token=str(token_data.get("access_token","") or "")
    if not token_res.get("ok") or not user_token:
        return False,str(token_data or token_res.get("error"))

    # Exchange to long-lived user token when Meta allows it.
    long_url=GSF_META_TOKEN_URL+"?"+urlencode({
        "grant_type":"fb_exchange_token",
        "client_id":app_id,
        "client_secret":app_secret,
        "fb_exchange_token":user_token,
    })
    long_res=_gsf_http_json(long_url,method="GET",timeout=45)
    long_data=long_res.get("data") or {}
    if long_res.get("ok") and long_data.get("access_token"):
        user_token=str(long_data.get("access_token"))

    accounts_url="https://graph.facebook.com/me/accounts?"+urlencode({
        "fields":"name,access_token,tasks,instagram_business_account",
        "access_token":user_token,
    })
    accounts_res=_gsf_http_json(accounts_url,method="GET",timeout=45)
    accounts_data=accounts_res.get("data") or {}
    pages=accounts_data.get("data") if isinstance(accounts_data,dict) else None
    if not accounts_res.get("ok") or not isinstance(pages,list):
        return False,str(accounts_data or accounts_res.get("error"))

    for page in pages:
        if not isinstance(page,dict):
            continue
        ig=(page.get("instagram_business_account") or {})
        ig_id=str(ig.get("id","") or "")
        page_token=str(page.get("access_token","") or "")
        if ig_id and page_token:
            ok,msg=_gsf_instagram_connect(ig_id,page_token)
            if ok:
                return True,"Instagram collegato."
            return False,msg

    return False,"Nessun account Instagram professionale collegato a una Pagina Facebook."


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
        return _gsf_instagram_web_auth_url()
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
    elif platform == "Instagram":
        ok, message = _gsf_instagram_web_complete(code, state, pending)
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
        return hashlib.sha1(raw).hexdigest()[:16]
    except Exception:
        return hashlib.sha1(
            repr(recipe).encode("utf-8","ignore")
        ).hexdigest()[:16]


def _gsf_set_final_recipe(recipe,source_label=""):
    st.session_state["gsf_final_recipe"]=dict(recipe or {})
    st.session_state["publication_ready"]=True
    st.session_state["publication_source"]=str(
        (recipe or {}).get("kind",source_label or "recipe")
    )
    st.session_state["publication_origin"]=str(source_label or "")
    _gsf_clear_final_master()


def _gsf_v93_release_analysis_memory():
    """Release analysis/preview RAM before the final FFmpeg encode."""
    if not GSF_LOW_MEMORY_WEB:
        return

    # These entries may contain model results or MP4 byte blobs.  The real
    # source and all preview files are already persisted under the session
    # directory, so keeping their byte copies during final render is wasteful.
    for _key in (
        "gsf_ai_scan_cache_v40",
        "gsf_ai_scan_cache_v50",
        "gsf_ai_voice_cache_v40",
        "gsf_ai_refine_motion_cache_v50",
        "gsf_fast_ai_cache",
        "gsf_ai_preview_cache_v71",
        "preview_bytes",
        "publication_preview_bytes",
        "inline_final_bytes",
        "v102_hook_preview_bytes",
        "v102_hook_preview_sig",
        "gsf_final_master_cache_v44",
    ):
        try:
            st.session_state.pop(_key,None)
        except Exception:
            pass

    # Streamlit executes the page at module scope.  Remove the temporary
    # top-level aliases too; otherwise they keep the same preview bytes alive
    # even after session_state has been cleaned.
    for _name in (
        "_mini_preview_bytes",
        "_selected_preview_bytes",
        "_card_bytes",
        "_mini_bytes",
        "_gsf_manual_bytes",
        "_gsf_manual_preview_bytes",
    ):
        try:
            globals().pop(_name,None)
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

    try:
        _mem_path=Path("/sys/fs/cgroup/memory.current")
        _mem_now=int(_mem_path.read_text(encoding="utf-8").strip())
        print("GSF_PRE_RENDER_MEMORY",f"bytes={_mem_now}",flush=True)
    except Exception:
        pass



def _gsf_saved_mobile_recipe(recipe):
    from web.mobile_editor_recipe import apply_saved_editor_recipe
    from editor_2027_embed import editor_2027_render_kwargs
    return apply_saved_editor_recipe(recipe,GSF_SESSION_ROOT,editor_2027_render_kwargs,st.session_state)


def _gsf_render_final_recipe(recipe,output_path,video_obj=None):
    """
    The ONLY manual/editor final render path.
    Editor screens only save a recipe; this function renders once at the bottom.
    """
    recipe=_gsf_saved_mobile_recipe(recipe)
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
        if kind=="main_editor":
            kw.setdefault(
                "filter_preset",
                st.session_state.get("editor_filter_preset","Originale")
            )
            kw.setdefault(
                "filter_intensity",
                st.session_state.get("editor_filter_intensity",70)
            )
        else:
            kw.setdefault(
                "filter_preset",
                st.session_state.get("v106_last_inline_filter_preset","Originale")
            )
            kw.setdefault(
                "filter_intensity",
                st.session_state.get("v106_last_inline_filter_intensity",70)
            )
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




def _gsf_v1053_detect_game():
    """Best-effort game name from the current upload, never a stale default."""
    corpus_parts=[
        str(st.session_state.get("gsf_source_name","") or ""),
        str(st.session_state.get("gsf_source_path","") or ""),
        str(st.session_state.get("editor_sub_text","") or ""),
        str(st.session_state.get("hook_testo","") or ""),
    ]
    try:
        _upload_obj=st.session_state.get("upload_v73")
        _upload_name=str(getattr(_upload_obj,"name","") or "")
        if _upload_name:
            corpus_parts.append(_upload_name)
    except Exception:
        pass
    try:
        corpus_parts.append(json.dumps(
            st.session_state.get("gsf_ai_v3_diagnostics",{}) or {},
            ensure_ascii=False,
        ))
    except Exception:
        pass

    corpus=" ".join(corpus_parts).lower()
    corpus=re.sub(r"[_\\.-]+"," ",corpus)

    aliases=[
        ("Halo Infinite",("halo infinite","master chief","cortana","spartan")),
        ("Halo",("halo","master chief","spartan")),
        ("ARC Raiders",("arc raiders","arcraiders")),
        ("Fortnite",("fortnite","battle royale")),
        ("Call of Duty",("call of duty","modern warfare","black ops")),
        ("Warzone",("warzone",)),
        ("EA Sports FC",("ea sports fc","fc 27","fc27","ultimate team")),
        ("Minecraft",("minecraft","creeper","enderman")),
        ("GTA V",("gta v","gta 5","grand theft auto")),
        ("Apex Legends",("apex legends","apex")),
        ("Valorant",("valorant",)),
        ("Overwatch",("overwatch",)),
        ("Rocket League",("rocket league",)),
        ("Rainbow Six Siege",("rainbow six","siege")),
        ("Battlefield",("battlefield",)),
        ("Destiny 2",("destiny 2","destiny")),
        ("Helldivers 2",("helldivers 2","helldivers")),
        ("PUBG",("pubg",)),
    ]
    for canonical,markers in aliases:
        if any(marker in corpus for marker in markers):
            return canonical

    # Never reuse a stale game from a previous upload. If this video gives us
    # no real evidence, use a neutral label instead of inventing the game.
    return "Gaming"



def _gsf_v1054_select_social(platform):
    st.session_state["social_selected_v59"]=str(platform)
    st.session_state["social_started_v59"]=False
    st.session_state.pop("social_error_v59",None)
    st.session_state.pop("social_auth_url_v77",None)
    st.session_state.pop("social_auth_platform_v77",None)


def _gsf_v1054_social_defaults(game,platform,mode):
    game=str(game or "").strip()
    known=bool(game and game.lower() not in {"gaming","gioco","game"})
    mode_text=str(mode or "").lower()

    if "director" in mode_text:
        phrase="Il momento che cambia la partita"
    elif "smart" in mode_text or "azione" in mode_text:
        phrase="Azione pura, zero tempi morti"
    elif "reaz" in mode_text:
        phrase="La reazione che vale la clip"
    elif "auto" in mode_text:
        phrase="Il momento più forte del gameplay"
    else:
        phrase="Il momento da non perdere"

    title=(f"{game} · {phrase}" if known else phrase)

    if known:
        description=(
            f"{game}: {phrase.lower()}. "
            "Clip pronta per la pubblicazione, selezionata dal gameplay."
        )
    else:
        description=(
            f"{phrase}. Clip selezionata dal gameplay. "
            "Aggiungi il nome del gioco se vuoi rendere titolo e hashtag più precisi."
        )

    tags=["#Gaming","#Gameplay"]
    if known:
        clean=re.sub(r"[^A-Za-z0-9]+","",game)
        if clean:
            tags.insert(0,"#"+clean)
    platform_l=str(platform or "").lower()
    if "youtube" in platform_l:
        tags.extend(["#Shorts","#GamingShorts"])
    elif "tiktok" in platform_l:
        tags.extend(["#GamingTok","#TikTokGaming"])
    elif "instagram" in platform_l:
        tags.extend(["#Reels","#GamingReels"])

    # Preserve order while removing duplicates.
    dedup=[]
    seen=set()
    for tag in tags:
        key=tag.lower()
        if key not in seen:
            seen.add(key)
            dedup.append(tag)

    return {
        "title":title[:100],
        "description":description[:1200],
        "hashtags":" ".join(dedup),
    }


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
    ).hexdigest()[:10]


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
    _label = "Video caricato" if loaded else "Carica il tuo gameplay"
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
.label{width:150px;min-height:42px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:17px;font-weight:800;line-height:1.2}
@media(max-width:600px){.wrap{height:260px}.circle{width:208px;height:208px}.icon{font-size:52px}.label{width:144px;min-height:40px;font-size:16px}}
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
.label{width:150px;min-height:42px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:17px;font-weight:800;line-height:1.2}
.status{display:none;margin-top:7px;width:174px;text-align:center;color:#668397;font-size:12px;font-weight:800}
.track{display:block;height:5px;margin-top:5px;border-radius:999px;background:rgba(116,154,197,.15);overflow:hidden}
.bar{display:block;height:100%;width:0;background:linear-gradient(90deg,#75B9DC,#978DE0);border-radius:999px;transition:width .12s linear}
.circle.busy{pointer-events:none;background:linear-gradient(145deg,#F3FAFD,#F5F2FC)}
.circle.done{background:linear-gradient(145deg,#EAF7FE,#F0ECFF);border-color:#C3DBEA;color:#55758A}
.circle.done .icon{color:#718FD0}
.error{color:#B42318}
@media(max-width:600px){.wrap{height:286px}.circle{width:208px;height:208px}.icon{font-size:54px}.label{width:144px;min-height:40px;font-size:16px}}
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
  const requestedConcurrency=Math.max(1,Number(init.concurrency||caps.concurrency||10));
  const mobileUpload=/Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent||'') ||
    (navigator.maxTouchPoints>1 && Math.min(screen.width,screen.height)<900);
  const concurrency=mobileUpload?Math.min(6,requestedConcurrency):Math.min(10,requestedConcurrency);
  const descriptors=Array.isArray(init.parts)?init.parts:[];
  let next=0;
  let completedBytes=0;
  const live=new Map();
  const results=[];

  const uploadStartedAt=performance.now();
  const update=()=>{
    let inflight=0;
    for(const value of live.values())inflight+=value;
    const bytesNow=completedBytes+inflight;
    const pct=Math.min(99,Math.round((bytesNow/file.size)*100));
    const elapsed=Math.max(0.25,(performance.now()-uploadStartedAt)/1000);
    const speedMBs=(bytesNow/1048576)/elapsed;
    bar.style.width=pct+'%';
    statusText.textContent='Upload diretto… '+pct+'% · '+speedMBs.toFixed(1)+' MB/s';
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
  try{
    const jr=await fetch('/job/status',{cache:'no-store'});const js=await jr.json();
    if(js&&js.render_status==='running'){
      status.style.display='block';status.classList.add('error');
      statusText.textContent='Attendi la fine dello Short in creazione';label.textContent='Short in creazione';pick.value='';return;
    }
  }catch(e){}
  try{window.parent.postMessage({type:'gsf-upload',state:'running',progress:0,name:file.name||''},'*');}catch(e){}
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
      statusText.textContent='Video caricato';try{window.parent.postMessage({type:'gsf-upload',state:'done',progress:100,name:file.name||''},'*');}catch(e){}
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
    statusText.textContent='Upload interrotto — riprova';try{window.parent.postMessage({type:'gsf-upload',state:'error',progress:0,name:file.name||''},'*');}catch(e){}
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
    _gsf_previous_source=str(st.session_state.get("gsf_source_path") or "")
    if _gsf_previous_source and _gsf_previous_source!=str(_gsf_direct_source):
        # A completed replacement upload starts a new video workflow. Reuse
        # the existing reset, retaining the newly uploaded source and drafts.
        _gsf_v75_reset_engine_workflow()
        for _key in list(st.session_state.keys()):
            if str(_key).startswith(("gsf_editor_","gsf_manual_","gsf_v107_")):
                st.session_state.pop(_key,None)
        for _artifact in ("editor2027_current.txt","render_job.json","media/gaming_short_finale_share.mp4"):
            (GSF_SESSION_ROOT/_artifact).unlink(missing_ok=True)
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


# V151 visual shell only: the V150.2 engine/state contracts stay untouched.
st.markdown("", unsafe_allow_html=True)

# V154 Structural Home — real custom component, not a CSS reskin.
# The existing V98.9/V99 direct-upload backend, AI engine and Editor remain
# authoritative. This component replaces only the Home presentation layer.
if GSF_WEB_MODE:
    from web.home_v154_embed import render_home_v154 as _gsf_render_home_v154

    st.html(r"""
    <style id="gsf-v154-parent-shell">
    /* V161 VIEWPORT CONTRACT — desktop reference 1920×1080, fit actual browser viewport. */
    @media (min-width:761px){
      html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.stApp{
        min-height:100dvh !important;
      }
      [data-testid="stMainBlockContainer"]{
        max-width:none !important;
        padding-top:0 !important;
        padding-bottom:0 !important;
        padding-left:0 !important;
        padding-right:0 !important;
      }
      iframe[title*="gsf_home_v154"],iframe[src*="web.home_v154_embed"]{
        width:100% !important;
        max-width:1920px !important;
        margin:0 auto !important;
      }
    }
    /* V161 VIEWPORT CONTRACT */
    /* V161.1 ZERO-SCROLL CONTRACT */
    @media (min-width:761px){
      html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
        height:100dvh !important;
        max-height:100dvh !important;
        overflow:hidden !important;
      }
      [data-testid="stMainBlockContainer"],.main .block-container{
        height:100dvh !important;
        max-height:100dvh !important;
        min-height:0 !important;
        overflow:hidden !important;
        margin:0 !important;
      }
      /* Streamlit execution chrome can sit below the custom shell and create
         an otherwise pointless scrollbar. It is not GSF render/upload progress. */
      [data-testid="stStatusWidget"],
      [data-testid="stToolbar"],
      [data-testid="stDecoration"],
      [data-testid="stHeader"]{
        display:none !important;
      }
      iframe[title*="gsf_home_v154_live_155"],
      iframe[title*="gsf_home_v154"],
      iframe[src*="home_v154"]{
        display:block !important;
        max-height:100dvh !important;
        border:0 !important;
      }
    }
    /* V162.1 HOME LIFT — keep the fixed desktop composition pinned to the top. */
    @media (min-width:761px){
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154"]),
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154_live_155"]){
        margin-top:-8px !important;
        margin-bottom:0 !important;
        padding-top:0 !important;
      }
    }


    /* V165 FLUID HOME SHELL — let the Home component use the complete desktop viewport. */
    @media (min-width:761px){
      iframe[title*="gsf_home_v154_live_155"],
      iframe[title*="gsf_home_v154"],
      iframe[src*="home_v154"]{
        width:100% !important;
        max-width:none !important;
        margin:0 !important;
      }
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154"]),
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154_live_155"]){
        width:100% !important;
        max-width:none !important;
        margin-top:0 !important;
        margin-bottom:0 !important;
      }
    }

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

    /* V166 CANONICAL FLUID HOME SHELL — the component owns the entire browser work area. */
    @media (min-width:761px){
      [data-testid="stMainBlockContainer"],.main .block-container{
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        min-height:0 !important;
        padding:0 !important;
        margin:0 !important;
      }
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154"]),
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154_live_155"]){
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        transform:none !important;
      }
      iframe[title*="gsf_home_v154_live_155"],
      iframe[title*="gsf_home_v154"],
      iframe[src*="home_v154"]{
        display:block !important;
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        border:0 !important;
        transform:none !important;
      }
    }

    
    /* V166.1 REAL VIEWPORT CLEANUP — reclaim the dead Streamlit band above Home. */
    @media (min-width:761px){
      html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
      }
      [data-testid="stMainBlockContainer"],.main .block-container{
        width:100vw !important;
        max-width:none !important;
        height:100dvh !important;
        max-height:100dvh !important;
        margin:0 !important;
        padding:0 !important;
        overflow:hidden !important;
      }
      body:has(iframe[title*="gsf_home_v154"]) [data-testid="stVerticalBlock"],
      body:has(iframe[title*="gsf_home_v154_live_155"]) [data-testid="stVerticalBlock"]{
        row-gap:0 !important;
        gap:0 !important;
      }
      [data-testid="stCustomComponentV1"]:has(iframe[title*="gsf_home_v154"]),
      [data-testid="stCustomComponentV1"]:has(iframe[title*="gsf_home_v154_live_155"]),
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154"]),
      [data-testid="stElementContainer"]:has(iframe[title*="gsf_home_v154_live_155"]){
        width:100% !important;
        max-width:none !important;
        min-height:0 !important;
        margin:0 !important;
        padding:0 !important;
        transform:none !important;
      }
    }
</style>
    """)

    _gsf_v154_duration=int(st.session_state.get("gsf_v154_duration",15) or 15)
    if _gsf_v154_duration not in (15,30,60):
        _gsf_v154_duration=15
    _gsf_v154_engine=str(st.session_state.get("gsf_v154_engine","") or "")

    # GSF QUEUE RUNTIME V411
    from web.queue_runtime_v411 import render_queue_runtime
    render_queue_runtime(st)

    _gsf_v154_event=_gsf_render_home_v154(
        loaded=bool(video is not None),
        duration=_gsf_v154_duration,
        engine=_gsf_v154_engine,
        height=900,
        key="gsf_home_v154_live",
    )

    if isinstance(_gsf_v154_event,dict):
        _v154_event=str(_gsf_v154_event.get("event") or "")
        _v154_duration=int(_gsf_v154_event.get("duration") or _gsf_v154_duration or 15)
        _v154_engine=str(_gsf_v154_event.get("engine") or _gsf_v154_engine or "")
        if _v154_duration in (15,30,60):
            st.session_state["gsf_v154_duration"]=_v154_duration
        if _v154_engine in ("","auto","best","action","reaction","manual"):
            st.session_state["gsf_v154_engine"]=_v154_engine

        # V291 DIRECT AI ENGINE BRIDGE
        # The custom AI surface is authoritative. Arm the real Streamlit AI
        # backend directly instead of clicking a hidden browser button.
        _gsf_v291_profile_map={
            "auto":"auto",
            "best":"director",
            "action":"action",
            "reaction":"reaction",
        }
        if _v154_event=="create_ai" and _v154_engine in _gsf_v291_profile_map:
            st.session_state["gsf_v291_engine_profile"]=_gsf_v291_profile_map[_v154_engine]
            st.session_state["gsf_v291_requested_duration"]=(
                int(_v154_duration) if int(_v154_duration) in (15,30,60) else 15
            )
            st.session_state["gsf_v291_ai_request"]={
                "engine":_v154_engine,
                "profile":_gsf_v291_profile_map[_v154_engine],
                "duration":int(_v154_duration) if int(_v154_duration) in (15,30,60) else 15,
            }
        elif _v154_engine=="manual" or (_v154_event=="open_editor" and "index" not in _gsf_v154_event):
            st.session_state.pop("gsf_v291_engine_profile",None)
            st.session_state.pop("gsf_v291_ai_request",None)

        # Home's Editor CTA selects the existing manual renderer; opening an
        # AI candidate (which carries an index) preserves its selected recipe.
        if _v154_event=="open_editor" and _v154_engine=="manual" and "index" not in _gsf_v154_event:
            st.session_state["modalita_gsf"]="✋ Manuale"
            st.session_state.pop("gsf_pending_engine_switch_v75",None)

        # V412 AI ENGINES: the AI page drives selection, editor hand-off and
        # "Cambia short" on the real AI run (same session-state keys used by
        # preview, editor and final render).
        try:
            from web.ai_engines_v412 import apply_replacement as _gsf_v412_replace
            from web.ai_engines_v412 import select_candidate as _gsf_v412_select
            if _v154_event=="create_ai":
                st.session_state["gsf_v412_request_id"]=str(_gsf_v154_event.get("request_id") or "")[:40]
                st.session_state.pop("gsf_v412_replaced",None)
            elif _v154_event in ("preview_moment","open_editor","create_short") and "index" in _gsf_v154_event:
                _gsf_v412_select(st.session_state,_gsf_v154_event.get("index"),_gsf_v154_event.get("start_time"))
            elif _v154_event=="replace_moment":
                if _gsf_v412_replace(
                    st.session_state,
                    int(_gsf_v154_event.get("index") or 0),
                    _gsf_v154_event.get("start_time"),
                    restore=bool(_gsf_v154_event.get("restore")),
                    duration=float(_v154_duration),
                ):
                    print("GSF_V412_REPLACE index="+str(_gsf_v154_event.get("index"))+" start="+str(_gsf_v154_event.get("start_time"))+" restore="+str(bool(_gsf_v154_event.get("restore"))),flush=True)
        except Exception as _gsf_v412_event_exc:
            print("GSF_V412_EVENT_WARN",repr(str(_gsf_v412_event_exc))[:220],flush=True)

        # Direct upload finishes in the existing upload server before the
        # component emits this event. A clean rerun lets _gsf_v989_direct_ready
        # materialize the source into the existing pipeline.
        if _v154_event=="upload_complete" and video is None:
            st.rerun()

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
        st.markdown("", unsafe_allow_html=True)

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
            _gsf_v1302_new_video_clicked=st.button("＋ NUOVO VIDEO",use_container_width=False,key="v81_new_video",help="Avvia un nuovo progetto senza perdere per errore quello attuale.")

    if bool(locals().get("_gsf_v1302_new_video_clicked",False)):
        _gsf_v1302_has_work=bool(
            st.session_state.get("gsf_source_name")
            or st.session_state.get("gsf_source_bytes")
            or st.session_state.get("gsf_upload_id")
            or st.session_state.get("gsf_final_recipe")
            or st.session_state.get("publication_ready")
            or st.session_state.get("publication_final_bytes")
            or st.session_state.get("auto_clip_scelta") is not None
            or st.session_state.get("gsf_editor_2027_inline_open")
        )
        if _gsf_v1302_has_work:
            st.session_state["gsf_v1302_new_video_confirm"]=True
        else:
            _gsf_start_new_video()
            st.rerun()

    if st.session_state.get("gsf_v1302_new_video_confirm",False):
        with st.container(key="gsf_v1302_new_video_guard"):
            st.markdown(
                '<div class="gsf-major-note"><b>Hai già un progetto in corso.</b><br>Iniziando un nuovo video perderai le modifiche non salvate.</div>',
                unsafe_allow_html=True,
            )
            _v1302_g1,_v1302_g2,_v1302_g3=st.columns(3,gap="small")
            with _v1302_g1:
                _v1302_save=st.button(
                    "SALVA BOZZA",
                    key="gsf_v1302_save_then_new",
                    use_container_width=True,
                )
            with _v1302_g2:
                _v1302_discard=st.button(
                    "CONTINUA",
                    key="gsf_v1302_discard_then_new",
                    use_container_width=True,
                )
            with _v1302_g3:
                _v1302_cancel=st.button(
                    "ANNULLA",
                    key="gsf_v1302_cancel_new",
                    use_container_width=True,
                )

            if _v1302_save:
                try:
                    _gsf_save_persistent_state()
                    _draft_state={}
                    if GSF_SESSION_STATE_FILE.is_file():
                        _draft_state=__import__("json").loads(
                            GSF_SESSION_STATE_FILE.read_text(encoding="utf-8")
                        )
                    if not isinstance(_draft_state,dict):
                        _draft_state={}
                    _draft_payload={
                        "title":"Bozza · "+str(st.session_state.get("gsf_source_name") or "Gameplay"),
                        "source_name":str(st.session_state.get("gsf_source_name") or "Gameplay"),
                        "state":_draft_state,
                    }
                    _u=__import__("urllib.request",fromlist=["Request","urlopen"])
                    _body=__import__("json").dumps(
                        _draft_payload,ensure_ascii=False,default=str
                    ).encode("utf-8")
                    _req=_u.Request(
                        "http://127.0.0.1:8502/drafts/save",
                        data=_body,
                        headers={
                            "Content-Type":"application/json",
                            "X-GSF-Session-ID":str(GSF_SESSION_ID),
                        },
                        method="POST",
                    )
                    _u.urlopen(_req,timeout=15).read()
                    st.session_state.pop("gsf_v1302_new_video_confirm",None)
                    _gsf_start_new_video()
                    st.toast("Bozza salvata nel Creator Hub.")
                    st.rerun()
                except Exception as _exc:
                    print("GSF_V1302_NEW_VIDEO_DRAFT_WARN",repr(str(_exc))[:220],flush=True)
                    st.warning("La bozza non è stata salvata: il progetto resta aperto.")

            if _v1302_discard:
                st.session_state.pop("gsf_v1302_new_video_confirm",None)
                _gsf_start_new_video()
                st.rerun()

            if _v1302_cancel:
                st.session_state.pop("gsf_v1302_new_video_confirm",None)
                st.rerun()


_GSF_V1057_ADS_MODE=str(os.environ.get("GSF_ADS_MODE","off") or "off").strip().lower()
if _GSF_V1057_ADS_MODE not in {"preview","live","off"}:
    _GSF_V1057_ADS_MODE="off"

_GSF_V1057_ADSENSE_CLIENT=str(os.environ.get("GSF_ADSENSE_CLIENT","") or "").strip()
_GSF_V1057_ADSENSE_SLOTS=[
    str(os.environ.get(f"GSF_ADSENSE_SLOT_{i}","") or "").strip()
    for i in range(1,7)
]
_GSF_V1057_CLIENT_RE=re.compile(r"^ca-pub-\d{10,20}$")
_GSF_V1057_SLOT_RE=re.compile(r"^\d{5,20}$")


def _gsf_v1057_ad_markup(index):
    idx=int(index)
    base=(
        f'<aside class="v67-ad gsf-v1056-ad gsf-v1057-ad gsf-v1057-slot-{idx}" '
        'aria-label="Pubblicità">'
    )

    if _GSF_V1057_ADS_MODE=="off":
        return base.replace('">','" style="display:none!important">',1)+'</aside>'

    if _GSF_V1057_ADS_MODE=="preview":
        return (
            base
            +'<span class="gsf-v1056-ad-kicker">Pubblicità</span>'
            +'<span class="gsf-v1056-ad-preview">Anteprima</span>'
            +'<span class="gsf-v1056-ad-copy">Spazio annuncio responsive</span>'
            +'</aside>'
        )

    slot=(
        _GSF_V1057_ADSENSE_SLOTS[idx-1]
        if 1 <= idx <= len(_GSF_V1057_ADSENSE_SLOTS)
        else ""
    )
    valid=bool(
        _GSF_V1057_CLIENT_RE.fullmatch(_GSF_V1057_ADSENSE_CLIENT)
        and _GSF_V1057_SLOT_RE.fullmatch(slot)
    )
    if not valid:
        return (
            base
            +'<span class="gsf-v1056-ad-kicker">Pubblicità</span>'
            +'<span class="gsf-v1056-ad-copy">Spazio annuncio responsive</span>'
            +'</aside>'
        )

    return (
        f'<aside class="v67-ad gsf-v1056-ad gsf-v1057-ad gsf-v1057-slot-{idx} gsf-v1057-live" '
        +'aria-label="Pubblicità" '
        +f'data-ad-client="{html.escape(_GSF_V1057_ADSENSE_CLIENT,quote=True)}" '
        +f'data-ad-slot="{html.escape(slot,quote=True)}" data-gsf-placement="{idx}">'
        +'<span class="gsf-v1056-ad-kicker">Pubblicità</span>'
        +'<div class="gsf-v1057-ad-mount" aria-label="Annuncio Google"></div>'
        +'</aside>'
    )


st.markdown(_gsf_v1057_ad_markup(1), unsafe_allow_html=True)



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
    text_color=None, active_color=None, outline_color=None,
    filter_preset="Originale", filter_intensity=0
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
            subtitle_font,subtitle_x,subtitle_y,
            filter_preset,filter_intensity
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
            "filterPreset":str(filter_preset or "Originale"),
            "filterIntensity":float(filter_intensity or 0),
            "filterCss":_gsf_v106_css_filter(filter_preset,filter_intensity),
        },
    )


import threading as _gsf_v106_threading

_GSF_V106_FILTER_PRESETS=(
    "Originale",
    "Gaming / Vibrante",
    "Cinematico",
    "Caldo",
    "Freddo",
    "Bianco e Nero",
)
_GSF_V106_RENDER_LOCK=_gsf_v106_threading.Lock()
_GSF_V106_PROBE_CACHE={}


def _gsf_v106_filter_strength(value):
    try:
        return max(0.0,min(1.0,float(value)/100.0))
    except Exception:
        return 0.0


def _gsf_v106_css_filter(preset,intensity):
    p=str(preset or "Originale")
    t=_gsf_v106_filter_strength(intensity)
    if p=="Gaming / Vibrante":
        return f"saturate({1.0+0.45*t:.4f}) contrast({1.0+0.08*t:.4f})"
    if p=="Cinematico":
        return f"saturate({1.0-0.18*t:.4f}) contrast({1.0+0.12*t:.4f}) sepia({0.08*t:.4f})"
    if p=="Caldo":
        return f"sepia({0.20*t:.4f}) saturate({1.0+0.08*t:.4f}) hue-rotate({-6.0*t:.3f}deg)"
    if p=="Freddo":
        return f"saturate({1.0+0.05*t:.4f}) hue-rotate({7.0*t:.3f}deg)"
    if p=="Bianco e Nero":
        return f"grayscale({t:.4f})"
    return ""


def _gsf_v106_ffmpeg_filter(preset,intensity):
    p=str(preset or "Originale")
    t=_gsf_v106_filter_strength(intensity)
    if t<=0.0001 or p=="Originale":
        return ""
    if p=="Gaming / Vibrante":
        return f"eq=saturation={1.0+0.45*t:.5f}:contrast={1.0+0.08*t:.5f}"
    if p=="Cinematico":
        return (
            f"eq=saturation={1.0-0.18*t:.5f}:contrast={1.0+0.12*t:.5f},"
            f"colorbalance=rs={0.025*t:.5f}:bs={-0.020*t:.5f}"
        )
    if p=="Caldo":
        return (
            f"eq=saturation={1.0+0.08*t:.5f},"
            f"colorbalance=rs={0.080*t:.5f}:bs={-0.060*t:.5f}"
        )
    if p=="Freddo":
        return (
            f"eq=saturation={1.0+0.05*t:.5f},"
            f"colorbalance=rs={-0.040*t:.5f}:bs={0.075*t:.5f}"
        )
    if p=="Bianco e Nero":
        return f"eq=saturation={1.0-t:.5f}"
    return ""


def _gsf_v106_probe_display_size_cached(source_path):
    p=Path(source_path)
    try:
        stt=p.stat()
        key=(str(p),int(stt.st_mtime_ns),int(stt.st_size))
    except Exception:
        return _gsf_probe_display_size(p)
    hit=_GSF_V106_PROBE_CACHE.get(key)
    if hit is not None:
        return hit
    result=_gsf_probe_display_size(p)
    if len(_GSF_V106_PROBE_CACHE)>=24:
        _GSF_V106_PROBE_CACHE.clear()
    _GSF_V106_PROBE_CACHE[key]=result
    return result


def _gsf_v106_run_render_locked(cmd,timeout,encoder="",fmt="",duration=0.0):
    wait_started=time.perf_counter()
    acquired=_GSF_V106_RENDER_LOCK.acquire(timeout=15.0)
    waited=time.perf_counter()-wait_started
    print(
        "GSF_EDITOR_RENDER_LOCK_WAIT",
        f"waited={waited:.3f}",
        f"encoder={encoder}",
        f"fmt={fmt}",
        flush=True,
    )
    if not acquired:
        raise subprocess.TimeoutExpired(cmd,float(timeout or 600.0))
    try:
        try:
            _gsf_v93_release_analysis_memory()
        except Exception:
            try:
                import gc
                gc.collect()
            except Exception:
                pass
        print(
            "GSF_EDITOR_RENDER_LOCK_START",
            f"encoder={encoder}",
            f"fmt={fmt}",
            f"duration={float(duration or 0.0):.3f}",
            flush=True,
        )
        _gsf_out=__import__("pathlib").Path(str(cmd[-1])).resolve()
        _gsf_is_final=("gsf_final_v54_" in str(_gsf_out.parent))
        _gsf_lock_handle=None
        _gsf_sid=""
        _gsf_root=None
        _gsf_stable=None
        _job_file=None
        try:
            if _gsf_is_final:
                _gsf_os=__import__("os")
                _gsf_root=(__import__("pathlib").Path(_gsf_os.environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime"))/"sessions").resolve()
                _gsf_rel=_gsf_out.relative_to(_gsf_root)
                _gsf_sid=str(_gsf_rel.parts[0]) if _gsf_rel.parts else ""
                if _gsf_sid:
                    _gsf_media=_gsf_root/_gsf_sid/"media"
                    _gsf_media.mkdir(parents=True,exist_ok=True)
                    _gsf_stable=_gsf_media/"gaming_short_finale_share.mp4"
                    _job_file=_gsf_root/_gsf_sid/"render_job.json"
                    _gsf_lock_handle=open(_gsf_root/_gsf_sid/"final_render.lock","a+")
                    __import__("fcntl").flock(_gsf_lock_handle.fileno(),__import__("fcntl").LOCK_EX)
                    _job={}
                    if _job_file.is_file():
                        try:_job=__import__("json").loads(_job_file.read_text(encoding="utf-8"))
                        except Exception:_job={}
                    if not isinstance(_job,dict):_job={}
                    if str(_job.get("status") or "")=="cancelled":
                        return subprocess.CompletedProcess(cmd,130,"","render cancelled")
                    _started=float(_job.get("started_at") or 0.0)
                    if _gsf_stable.is_file() and _gsf_stable.stat().st_size>1024 and (_started<=0.0 or _gsf_stable.stat().st_mtime>=_started-1.0):
                        __import__("shutil").copyfile(_gsf_stable,_gsf_out)
                        print("GSF_FINAL_RENDER_REUSED","sid="+_gsf_sid,flush=True)
                        return subprocess.CompletedProcess(cmd,0,"","")
            if _gsf_is_final and _job_file is not None:
                _proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                try:
                    _job={}
                    if _job_file.is_file():
                        try:_job=__import__("json").loads(_job_file.read_text(encoding="utf-8"))
                        except Exception:_job={}
                    if not isinstance(_job,dict):_job={}
                    _job.update({"status":"running","pid":int(_proc.pid)})
                    _tmp=_job_file.with_suffix(".tmp")
                    _tmp.write_text(__import__("json").dumps(_job,ensure_ascii=False,default=str),encoding="utf-8")
                    __import__("os").replace(_tmp,_job_file)
                except Exception:pass
                try:_stdout,_stderr=_proc.communicate(timeout=timeout)
                except subprocess.TimeoutExpired:
                    _proc.kill();_stdout,_stderr=_proc.communicate();raise
                _gsf_locked_result=subprocess.CompletedProcess(cmd,int(_proc.returncode or 0),_stdout,_stderr)
            else:
                _gsf_locked_result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)
            _job={}
            if _job_file is not None and _job_file.is_file():
                try:_job=__import__("json").loads(_job_file.read_text(encoding="utf-8"))
                except Exception:_job={}
            if not isinstance(_job,dict):_job={}
            _was_cancelled=(str(_job.get("status") or "")=="cancelled")
            if _gsf_locked_result.returncode==0 and _gsf_is_final and not _was_cancelled:
                try:
                    if _gsf_sid and _gsf_out.is_file() and _gsf_out.stat().st_size>1024:
                        _tmp_video=_gsf_stable.with_suffix(".mp4.tmp")
                        _v125_final_source=_gsf_out
                        _v125_cinematic_tmp=_gsf_stable.with_name(".cinematic_v125_"+str(__import__("os").getpid())+".mp4")
                        try:
                            _v125_recipe=dict((_job.get("recipe") or {})) if isinstance(_job,dict) else {}
                            _v125_plan=dict(_v125_recipe.get("ai_director_plan") or {})
                            _v125_edit=dict(_v125_plan.get("edit") or {}) if isinstance(_v125_plan,dict) else {}
                            _v125_wants_cinematic=bool(
                                ((_v125_edit.get("slow_motion") or {}).get("enabled"))
                                or ((_v125_edit.get("replay") or {}).get("enabled"))
                            )
                            if _v125_plan and _v125_wants_cinematic:
                                _v125_mod=__import__("cinematic_render_v125",fromlist=["apply_cinematic_plan"])
                                _v125_result=_v125_mod.apply_cinematic_plan(
                                    str(_gsf_out),str(_v125_cinematic_tmp),_v125_plan
                                )
                                if (
                                    isinstance(_v125_result,dict)
                                    and _v125_result.get("ok")
                                    and _v125_cinematic_tmp.is_file()
                                    and _v125_cinematic_tmp.stat().st_size>1024
                                ):
                                    _v125_final_source=_v125_cinematic_tmp
                                    _job["cinematic_v125"]=_v125_result
                                    print(
                                        "GSF_V125_CINEMATIC_APPLIED",
                                        "sid="+_gsf_sid,
                                        "effects="+str([
                                            x.get("effect") for x in (_v125_result.get("effects") or [])
                                            if isinstance(x,dict) and x.get("applied")
                                        ]),
                                        flush=True,
                                    )
                        except Exception as _v125_cinematic_exc:
                            print("GSF_V125_CINEMATIC_FALLBACK",repr(str(_v125_cinematic_exc))[:260],flush=True)
                        _v126_final_source=_v125_final_source
                        _v126_audio_tmp=_gsf_stable.with_name(".creative_v126_"+str(__import__("os").getpid())+".mp4")
                        try:
                            _v126_style=dict((_v125_plan or {}).get("style") or {}) if isinstance(_v125_plan,dict) else {}
                            _v126_accent=str(_v126_style.get("sound_accent") or "none")
                            if _v125_plan and _v126_accent!="none":
                                _v126_mod=__import__("creative_render_v126",fromlist=["apply_sound_design"])
                                _v126_result=_v126_mod.apply_sound_design(
                                    str(_v125_final_source),str(_v126_audio_tmp),_v125_plan
                                )
                                if (
                                    isinstance(_v126_result,dict)
                                    and _v126_result.get("ok")
                                    and _v126_result.get("applied")
                                    and _v126_audio_tmp.is_file()
                                    and _v126_audio_tmp.stat().st_size>1024
                                ):
                                    _v126_final_source=_v126_audio_tmp
                                    _job["creative_v126"]=_v126_result
                                    print(
                                        "GSF_V126_SOUND_APPLIED",
                                        "sid="+_gsf_sid,
                                        "accent="+str(_v126_result.get("accent") or ""),
                                        flush=True,
                                    )
                        except Exception as _v126_audio_exc:
                            print("GSF_V126_SOUND_FALLBACK",repr(str(_v126_audio_exc))[:240],flush=True)

                        _v143_final_source=_v126_final_source
                        _v143_tmp=_gsf_stable.with_name(".director_v143_"+str(__import__("os").getpid())+".mp4")
                        try:
                            _v143_recipe=dict((_job.get("recipe") or {})) if isinstance(_job,dict) else {}
                            _v143_ops=list(_v143_recipe.get("ai_render_operations") or [])
                            if _v143_ops:
                                _v143_mod=__import__(
                                    "director_render_exec_v143",
                                    fromlist=["execute_director_operations"],
                                )
                                _v143_result=_v143_mod.execute_director_operations(
                                    str(_v126_final_source),
                                    str(_v143_tmp),
                                    _v143_ops,
                                    recipe_start=float(_v143_recipe.get("start") or 0.0),
                                )
                                if (
                                    isinstance(_v143_result,dict)
                                    and _v143_result.get("ok")
                                    and int(_v143_result.get("count") or 0)>0
                                    and _v143_tmp.is_file()
                                    and _v143_tmp.stat().st_size>1024
                                ):
                                    _v143_final_source=_v143_tmp
                                    _job["director_v143"]=_v143_result
                                    print(
                                        "GSF_V143_RENDER_APPLIED",
                                        "sid="+_gsf_sid,
                                        "effects="+str(_v143_result.get("applied") or []),
                                        flush=True,
                                    )
                        except Exception as _v143_exc:
                            print("GSF_V143_RENDER_FALLBACK",repr(str(_v143_exc))[:300],flush=True)

                        _v149_final_source=_v143_final_source
                        _v149_tmp=_gsf_stable.with_name(".privacy_v149_"+str(__import__("os").getpid())+".mp4")
                        try:
                            _v149_mod=__import__(
                                "privacy_cleanup_v149",
                                fromlist=["cleanup_video"],
                            )
                            _v149_result=_v149_mod.cleanup_video(
                                str(_v143_final_source),
                                str(_v149_tmp),
                            )
                            _job["privacy_cleanup_v149"]=_v149_result
                            try:
                                _v149_root=__import__("pathlib").Path(
                                    __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
                                )/"sessions"/str(GSF_SESSION_ID)
                                _v149_root.mkdir(parents=True,exist_ok=True)
                                (_v149_root/"privacy_cleanup_v149.json").write_text(
                                    __import__("json").dumps(
                                        {
                                            "engine":"v149-privacy-cleanup",
                                            "applied":bool((_v149_result or {}).get("applied")),
                                            "mask_count":int((_v149_result or {}).get("mask_count") or 0),
                                            "publish_guard":str((_v149_result or {}).get("publish_guard") or "clear"),
                                            "report":dict((_v149_result or {}).get("report") or {}),
                                        },
                                        ensure_ascii=False,
                                        separators=(",",":"),
                                    ),
                                    encoding="utf-8",
                                )
                            except Exception:
                                pass
                            if (
                                isinstance(_v149_result,dict)
                                and _v149_result.get("ok")
                                and _v149_tmp.is_file()
                                and _v149_tmp.stat().st_size>1024
                                and bool(_v149_result.get("applied"))
                            ):
                                _v149_final_source=_v149_tmp
                            print(
                                "GSF_V149_PRIVACY",
                                "sid="+_gsf_sid,
                                "masked="+str(int((_v149_result or {}).get("mask_count") or 0)),
                                "guard="+str((_v149_result or {}).get("publish_guard") or "clear"),
                                flush=True,
                            )
                        except Exception as _v149_exc:
                            print("GSF_V149_PRIVACY_FALLBACK",repr(str(_v149_exc))[:300],flush=True)

                        __import__("shutil").copyfile(_v149_final_source,_tmp_video)
                        __import__("os").replace(_tmp_video,_gsf_stable)

                        # V145 finalizes persistent content memory only after a
                        # real final file exists, avoiding brittle UI hooks.
                        try:
                            _v145_record=dict(_v143_recipe.get("ai_content_memory_record") or {})
                            _v145_fp=str(_v145_record.get("fingerprint") or "")
                            if _v145_fp and _gsf_stable.is_file() and _gsf_stable.stat().st_size>1024:
                                _v145_record["status"]="rendered"
                                _v145_json=__import__("json")
                                _v145_url=__import__("urllib.request",fromlist=["Request","urlopen"])
                                _v145_req=_v145_url.Request(
                                    "http://127.0.0.1:8502/content-memory/record",
                                    data=_v145_json.dumps(
                                        {"record":_v145_record},
                                        ensure_ascii=False,
                                        separators=(",",":"),
                                    ).encode("utf-8"),
                                    headers={
                                        "Content-Type":"application/json",
                                        "X-GSF-Session-ID":str(GSF_SESSION_ID),
                                    },
                                    method="POST",
                                )
                                _v145_resp=_v145_json.loads(
                                    _v145_url.urlopen(_v145_req,timeout=2.5).read().decode("utf-8")
                                )
                                print(
                                    "GSF_V145_MEMORY_FINAL",
                                    "fp="+_v145_fp[:12],
                                    "ok="+str(bool((_v145_resp or {}).get("ok"))),
                                    flush=True,
                                )
                        except Exception as _v145_exc:
                            print("GSF_V145_MEMORY_FINAL_WARN",repr(str(_v145_exc))[:220],flush=True)

                        try:
                            _v143_tmp.unlink(missing_ok=True)
                        except Exception:
                            pass
                        try:
                            _v149_tmp.unlink(missing_ok=True)
                        except Exception:
                            pass
                        try:
                            _v126_audio_tmp.unlink(missing_ok=True)
                        except Exception:
                            pass

                        # AI thumbnail: choose the event frame from the clean render,
                        # before any appended replay changes final timing.
                        try:
                            _v125_thumb=_gsf_stable.with_name("ai_thumbnail_v125.jpg")
                            _v125_thumb_offset=float(((_v125_edit or {}).get("thumbnail_offset") or 0.0))
                            if _v125_plan and _v125_thumb_offset>=0:
                                _v125_mod=__import__("cinematic_render_v125",fromlist=["extract_thumbnail"])
                                _v125_thumb_result=_v125_mod.extract_thumbnail(
                                    str(_gsf_out),str(_v125_thumb),_v125_thumb_offset,width=720
                                )
                                _job["thumbnail_v125"]={
                                    "path":str(_v125_thumb),
                                    "offset":_v125_thumb_result.get("offset"),
                                    "bytes":_v125_thumb_result.get("bytes"),
                                }
                                print(
                                    "GSF_V125_THUMBNAIL_READY",
                                    "sid="+_gsf_sid,
                                    "bytes="+str(_v125_thumb.stat().st_size if _v125_thumb.is_file() else 0),
                                    flush=True,
                                )
                        except Exception as _v125_thumb_exc:
                            print("GSF_V125_THUMBNAIL_WARN",repr(str(_v125_thumb_exc))[:220],flush=True)

                        try:
                            _v125_cinematic_tmp.unlink(missing_ok=True)
                        except Exception:
                            pass
                        print("GSF_FINAL_STABLE_READY","sid="+_gsf_sid,"bytes="+str(_gsf_stable.stat().st_size),flush=True)
                        try:
                            _job.update({"status":"ready","completed_at":__import__("time").time(),"final_path":str(_gsf_stable),"final_bytes":int(_gsf_stable.stat().st_size),"pid":0})
                            _job_tmp=_job_file.with_suffix(".tmp")
                            _job_tmp.write_text(__import__("json").dumps(_job,ensure_ascii=False,default=str),encoding="utf-8")
                            __import__("os").replace(_job_tmp,_job_file)
                        except Exception as _job_exc:
                            print("GSF_FINAL_JOB_READY_WARN",repr(str(_job_exc)),flush=True)
                        try:
                            _u=__import__("urllib.request",fromlist=["Request","urlopen"])
                            _persist_payload=__import__("json").dumps({
                                "path":str(_gsf_stable),
                                "started_at":float(_job.get("started_at") or 0.0),
                            },ensure_ascii=False).encode("utf-8")
                            _persist_req=_u.Request(
                                "http://127.0.0.1:8502/final/persist",
                                data=_persist_payload,
                                headers={"Content-Type":"application/json","X-GSF-Session-ID":_gsf_sid},
                                method="POST",
                            )
                            _u.urlopen(_persist_req,timeout=90).read()
                            print("GSF_FINAL_BUCKET_PERSISTED","sid="+_gsf_sid,flush=True)
                        except Exception as _persist_exc:
                            print("GSF_FINAL_BUCKET_PERSIST_WARN",repr(str(_persist_exc)),flush=True)
                        try:
                            _u=__import__("urllib.request",fromlist=["Request","urlopen"])
                            _payload=__import__("json").dumps({"title":"Short pronto","body":"Il tuo Short è pronto. Tocca per aprire lo Share Hub.","url":"/#share-hub","tag":"gsf-short-ready"}).encode("utf-8")
                            _req=_u.Request("http://127.0.0.1:8502/push/notify",data=_payload,headers={"Content-Type":"application/json","X-GSF-Session-ID":_gsf_sid},method="POST")
                            _u.urlopen(_req,timeout=4).read()
                        except Exception as _push_exc:print("GSF_FINAL_PUSH_WARN",repr(str(_push_exc)),flush=True)
                except Exception as _stable_exc:print("GSF_FINAL_STABLE_WARN",repr(str(_stable_exc)),flush=True)
            if _gsf_locked_result.returncode!=0 and _gsf_is_final and not _was_cancelled:
                try:
                    _job.update({"status":"failed","failed_at":__import__("time").time(),"returncode":int(_gsf_locked_result.returncode),"pid":0})
                    _tmp=_job_file.with_suffix(".tmp")
                    _tmp.write_text(__import__("json").dumps(_job,ensure_ascii=False,default=str),encoding="utf-8")
                    __import__("os").replace(_tmp,_job_file)
                except Exception:pass
            return _gsf_locked_result
        finally:
            if _gsf_lock_handle is not None:
                try:
                    __import__("fcntl").flock(_gsf_lock_handle.fileno(),__import__("fcntl").LOCK_UN)
                    _gsf_lock_handle.close()
                except Exception:pass
    finally:
        print(
            "GSF_EDITOR_RENDER_LOCK_END",
            f"encoder={encoder}",
            f"fmt={fmt}",
            flush=True,
        )
        _GSF_V106_RENDER_LOCK.release()


def _render_gsf_editor_live_player_legacy(
    source_path, key, start_seconds, fmt, zoom, x_pos, y_pos,
    volume, brightness, contrast, speed,
    subtitles_on=False, subtitle_style="Gaming",
    subtitle_size=92, subtitle_position=330,
    subtitle_words=None, subtitle_text="",
    subtitle_font="Arial", subtitle_x=50, subtitle_y=78,
    filter_preset="Originale", filter_intensity=0
):
    """Live editor preview in browser, including live subtitle overlay."""
    source_path=Path(source_path)
    if not source_path.exists():
        st.warning("Anteprima scena non disponibile."); return
    _v106_probe_t0=time.perf_counter()
    pw,ph,rotation,err=_gsf_v106_probe_display_size_cached(source_path)
    print(
        "GSF_EDITOR_PROBE",
        f"fmt={fmt}",
        f"elapsed={time.perf_counter()-_v106_probe_t0:.4f}",
        flush=True,
    )
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
    _v106_fx=_gsf_v106_css_filter(filter_preset,filter_intensity)
    _v106_css_filter=(
        f"brightness({bri}) contrast({con})"
        + (f" {_v106_fx}" if _v106_fx else "")
    )
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
    words=_gsf_refine_subtitle_words(subtitle_words or [])
    _preview_groups=_gsf_subtitle_groups(words) if words else []
    _preview_longest=max(
        (" ".join(str((w or {}).get("text","") or "").strip() for w in g).strip() for g in _preview_groups),
        key=lambda t:_gsf_subtitle_visual_units(t),
        default=str(subtitle_text or "")
    )
    _preview_fmt="9:16 Short" if frame_h>=frame_w else "16:9"
    _preview_w,_preview_h=((1080,1920) if _preview_fmt=="9:16 Short" else (1920,1080))
    _preview_fs=_gsf_subtitle_auto_size(subtitle_size,_preview_longest,_preview_fmt)
    _px,_py=_gsf_subtitle_safe_xy(
        _preview_fmt,subtitle_x,subtitle_y,_preview_longest,_preview_fs,_preview_w,_preview_h
    )
    sx=100.0*_px/_preview_w
    sy=100.0*_py/_preview_h
    # Scale ASS-like values to the small live viewport.
    live_font=max(13,min(48,float(_preview_fs)*(frame_h/_preview_h)*1.25*float(ps.get("scale",1.0))))
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
      filter:{_v106_css_filter}}}
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
    token=hashlib.md5(f"{source_path}|{start_seconds:.2f}|{duration_seconds:.2f}".encode()).hexdigest()[:12]
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

    # Anteprima sorgente caricata nascosta per UX; il file resta disponibile internamente.
    st.markdown('<div style="height:6px" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="gsf-icon-title" style="display:flex;justify-content:center;text-align:center;width:100%;">Scegli il tuo motore IA o crea il tuo gameplay</div>', unsafe_allow_html=True)
    st.markdown('\n<style id="gsf-major-actions">\n.gsf-major-note{\n    position:relative;\n    max-width:620px;\n    margin:9px auto 18px;\n    padding:10px 14px;\n    border-radius:16px;\n    border:1px solid #D6E7F2;\n    background:linear-gradient(135deg,rgba(239,250,255,.97),rgba(244,241,255,.96));\n    box-shadow:0 7px 18px rgba(91,126,170,.08);\n    color:#60798E;\n    text-align:center;\n    font-size:12px;\n    font-weight:700;\n    line-height:1.35;\n}\n.gsf-major-note:before{\n    content:"";\n    position:absolute;\n    left:50%;\n    top:-6px;\n    width:11px;\n    height:11px;\n    transform:translateX(-50%) rotate(45deg);\n    background:#F1F8FE;\n    border-left:1px solid #D6E7F2;\n    border-top:1px solid #D6E7F2;\n}\n.st-key-gsf-major-personalize button,\n[class*="st-key-gsf-major-personalize"] button,\n[class*="st-key-gsf-major-create-ai"] button,\n[class*="st-key-gsf-major-game-editor_"] button,\n[class*="st-key-gsf-major-create-short"] button{\n    min-height:56px !important;\n    border-radius:17px !important;\n    border:1px solid rgba(255,255,255,.34) !important;\n    color:#FFFFFF !important;\n    font-size:15px !important;\n    font-weight:900 !important;\n    letter-spacing:.045em !important;\n    transition:transform .16s ease,box-shadow .16s ease,filter .16s ease !important;\n}\n.st-key-gsf-major-personalize button,\n[class*="st-key-gsf-major-personalize"] button,\n[class*="st-key-gsf-major-create-ai"] button,\n[class*="st-key-gsf-major-game-editor_"] button,\n[class*="st-key-gsf-major-create-short"] button{\n    background:linear-gradient(135deg,#8B67E8 0%,#6557D9 100%) !important;\n    box-shadow:0 12px 28px rgba(104,84,205,.28) !important;\n}\n[class*="st-key-gsf-major-create-ai"] button:hover,\n[class*="st-key-gsf-major-game-editor_"] button:hover,\n[class*="st-key-gsf-major-create-short"] button:hover{\n    transform:translateY(-2px) !important;\n    filter:brightness(1.035) !important;\n    box-shadow:0 15px 34px rgba(104,84,205,.36) !important;\n}\n@media(max-width:750px){\n    .gsf-major-note{font-size:11px;padding:9px 12px;margin-bottom:15px}\n    .st-key-gsf-major-personalize button,\n    [class*="st-key-gsf-major-personalize"] button,\n    [class*="st-key-gsf-major-create-ai"] button,\n    [class*="st-key-gsf-major-game-editor_"] button,\n    [class*="st-key-gsf-major-create-short"] button{\n        min-height:52px !important;\n        font-size:13px !important;\n    }\n}\n</style>\n', unsafe_allow_html=True)

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
    st.markdown(
        '<div class="gsf-major-note">'+html.escape(str(_engine_help.get(modalita,"") or ""))+'</div>',
        unsafe_allow_html=True,
    )
    _gsf_engine_now=str(modalita)
    _gsf_engine_prev=str(st.session_state.get("gsf_v107_last_engine") or "")
    _gsf_engine_changed=bool(_gsf_engine_prev and _gsf_engine_prev!=_gsf_engine_now)
    _gsf_render_active=bool(st.session_state.get("gsf_v107_final_render_running",False))

    # Keep a snapshot from the PREVIOUS engine. Streamlit reruns on selector
    # changes, so the save action must survive the next rerun too.
    _gsf_prev_recipe=st.session_state.get("gsf_v107_engine_snapshot_recipe")
    _gsf_prev_source=str(st.session_state.get("gsf_v107_engine_snapshot_source") or "")
    if _gsf_render_active:
        _render_recipe=st.session_state.get("gsf_v107_render_recipe_snapshot")
        _render_source=str(st.session_state.get("gsf_v107_render_source_snapshot") or "")
        if isinstance(_render_recipe,dict) and _render_recipe:
            _gsf_prev_recipe=dict(_render_recipe)
        if _render_source:
            _gsf_prev_source=_render_source

    _gsf_has_meaningful_work=bool(
        _gsf_render_active
        or (isinstance(_gsf_prev_recipe,dict) and bool(_gsf_prev_recipe))
    )

    if _gsf_engine_changed and _gsf_has_meaningful_work:
        _pending_state={}
        try:
            _gsf_save_persistent_state()
            if GSF_SESSION_STATE_FILE.is_file():
                _pending_state=__import__("json").loads(GSF_SESSION_STATE_FILE.read_text(encoding="utf-8"))
            if not isinstance(_pending_state,dict):
                _pending_state={}
        except Exception:
            _pending_state={}
        if isinstance(_gsf_prev_recipe,dict) and _gsf_prev_recipe:
            _pending_state["gsf_final_recipe"]=dict(_gsf_prev_recipe)
        if _gsf_prev_source:
            _pending_state["gsf_source_path"]=_gsf_prev_source
            _pending_state["gsf_editor_source_path"]=_gsf_prev_source
        st.session_state["gsf_v107_engine_change_draft_pending"]={
            "from_engine":_gsf_engine_prev,
            "to_engine":_gsf_engine_now,
            "source":_gsf_prev_source,
            "recipe":dict(_gsf_prev_recipe) if isinstance(_gsf_prev_recipe,dict) else {},
            "state":_pending_state,
        }

        if _gsf_render_active:
            try:
                _job_path=GSF_SESSION_ROOT/"render_job.json"
                _job={}
                if _job_path.is_file():
                    _job=__import__("json").loads(_job_path.read_text(encoding="utf-8"))
                if not isinstance(_job,dict):
                    _job={}
                _pid=int(_job.get("pid") or 0)
                if _pid>0:
                    try:
                        __import__("os").kill(_pid,__import__("signal").SIGTERM)
                    except Exception:
                        pass
                _job.update({"status":"cancelled","cancelled_at":__import__("time").time(),"reason":"engine_changed","pid":0})
                _tmp=_job_path.with_suffix(".tmp")
                _tmp.write_text(__import__("json").dumps(_job,ensure_ascii=False,default=str),encoding="utf-8")
                __import__("os").replace(_tmp,_job_path)
            except Exception:
                pass
            st.session_state["gsf_v107_final_render_running"]=False
            st.session_state["gsf_v107_final_render_pending"]=False
    elif _gsf_engine_changed:
        # A fresh upload / first engine choice is not a draft. The source file
        # alone is never enough to trigger the save-warning.
        st.session_state.pop("gsf_v107_engine_change_draft_pending",None)

    _gsf_engine_pending=st.session_state.get("gsf_v107_engine_change_draft_pending")
    if isinstance(_gsf_engine_pending,dict) and _gsf_engine_pending:
        st.warning(
            "⚠️ Hai cambiato motore: il lavoro precedente è ancora disponibile. "
            "Puoi salvarlo come bozza prima di continuare."
        )
        if st.button(
            "SALVA BOZZA DELLO SHORT INTERROTTO",
            use_container_width=True,
            key="gsf_save_draft_before_engine_change_v107",
        ):
            try:
                _draft_state=_gsf_engine_pending.get("state") or {}
                if not isinstance(_draft_state,dict):
                    _draft_state={}
                _snap_recipe=_gsf_engine_pending.get("recipe")
                _snap_source=str(_gsf_engine_pending.get("source") or "")
                if isinstance(_snap_recipe,dict) and _snap_recipe:
                    _draft_state["gsf_final_recipe"]=dict(_snap_recipe)
                if _snap_source:
                    _draft_state["gsf_source_path"]=_snap_source
                    _draft_state["gsf_editor_source_path"]=_snap_source
                _draft_payload={
                    "title":"Bozza · "+str(st.session_state.get("gsf_source_name") or "Gameplay"),
                    "source_name":str(st.session_state.get("gsf_source_name") or "Gameplay"),
                    "state":_draft_state,
                }
                _u=__import__("urllib.request",fromlist=["Request","urlopen"])
                _body=__import__("json").dumps(_draft_payload,ensure_ascii=False,default=str).encode("utf-8")
                _req=_u.Request(
                    "http://127.0.0.1:8502/drafts/save",
                    data=_body,
                    headers={"Content-Type":"application/json","X-GSF-Session-ID":str(GSF_SESSION_ID)},
                    method="POST",
                )
                _u.urlopen(_req,timeout=8).read()
                st.session_state.pop("gsf_v107_engine_change_draft_pending",None)
                st.toast("💾 Bozza salvata nel Creator Hub.")
            except Exception as _draft_exc:
                print("GSF_ENGINE_DRAFT_SAVE_WARN",repr(str(_draft_exc)),flush=True)
                st.warning("Non sono riuscito a salvare la bozza. Riprova.")

    st.session_state["gsf_v107_last_engine"]=_gsf_engine_now
    _gsf_current_recipe=st.session_state.get("gsf_final_recipe")
    _gsf_current_source=str(st.session_state.get("gsf_source_path") or st.session_state.get("gsf_editor_source_path") or "")
    _gsf_snapshot_source_before=str(st.session_state.get("gsf_v107_engine_snapshot_source") or "")
    if (
        _gsf_current_source
        and _gsf_snapshot_source_before
        and _gsf_snapshot_source_before!=_gsf_current_source
        and not (isinstance(_gsf_current_recipe,dict) and _gsf_current_recipe)
    ):
        st.session_state.pop("gsf_v107_engine_snapshot_recipe",None)
        st.session_state.pop("gsf_v107_engine_change_draft_pending",None)
    if isinstance(_gsf_current_recipe,dict) and _gsf_current_recipe:
        st.session_state["gsf_v107_engine_snapshot_recipe"]=dict(_gsf_current_recipe)
    if _gsf_current_source:
        st.session_state["gsf_v107_engine_snapshot_source"]=_gsf_current_source

    if modalita != "✋ Manuale":
        with st.container(key="v1055_ad_engine"):
            st.markdown(
                _gsf_v1057_ad_markup(2),
                unsafe_allow_html=True,
            )


    # Prima dell'analisi scegliamo solo la durata. I sottotitoli si decidono DOPO aver scelto una clip.
    st.markdown('<div style="height:20px" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.session_state.setdefault("gsf_duration_preset", "15s")
    st.markdown('<div class="v70-duration-title">Scegli la durata</div>', unsafe_allow_html=True)
    st.markdown('<div class="v70-duration-sub">La stessa durata verrà applicata alle tre proposte AI.</div>', unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
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
        try:
            with st.container(key="v1055_ad_manual_before_editor"):
                st.markdown(_gsf_v1057_ad_markup(2),unsafe_allow_html=True)
        except Exception as _gsf_manual_ad_exc:
            print("GSF_MANUAL_AD_SKIP",repr(str(_gsf_manual_ad_exc)),flush=True)
        st.markdown('<div style="height:26px" aria-hidden="true"></div>',unsafe_allow_html=True)
        with st.container(key="gsf-major-personalize"):
            st.button("PERSONALIZZA IL TUO GAMEPLAY",use_container_width=True)
        st.markdown('<div class="gsf-major-note gsf-editor-note">Modifica scena, look, sottotitoli e audio prima di continuare.</div>',unsafe_allow_html=True)
        try:
            import os as _gsf_manual_os
            from editor_2027_embed import (
                render_editor_2027_embed as _gsf_render_manual_editor_2027,
                editor_2027_state_key as _gsf_editor_2027_state_key,
                editor_2027_initial_state as _gsf_editor_2027_initial_state,
                editor_2027_clip_bounds as _gsf_editor_2027_clip_bounds,
                editor_2027_render_kwargs as _gsf_editor_2027_render_kwargs,
            )
            _gsf_manual_path=str(st.session_state.get("gsf_editor_source_path") or st.session_state.get("gsf_source_path") or "")
            if _gsf_manual_path and not _gsf_manual_os.path.isfile(_gsf_manual_path) and GSF_WEB_MODE:
                try:
                    import urllib.parse as _gsf_restore_parse
                    import urllib.request as _gsf_restore_request
                    _gsf_restore_url="http://127.0.0.1:8502/source/restore?"+_gsf_restore_parse.urlencode({"path":_gsf_manual_path})
                    _gsf_restore_req=_gsf_restore_request.Request(_gsf_restore_url,headers={"X-GSF-Session-ID":str(GSF_SESSION_ID)})
                    with st.spinner("Recupero Game Editor..."):
                        _gsf_restore_payload=__import__("json").loads(_gsf_restore_request.urlopen(_gsf_restore_req,timeout=180).read().decode("utf-8"))
                    _gsf_restored_path=str(_gsf_restore_payload.get("path") or "") if isinstance(_gsf_restore_payload,dict) else ""
                    if _gsf_restored_path and _gsf_manual_os.path.isfile(_gsf_restored_path):
                        _gsf_manual_path=_gsf_restored_path
                        st.session_state["gsf_source_path"]=_gsf_manual_path
                        st.session_state["gsf_editor_source_path"]=_gsf_manual_path
                        print("GSF_MANUAL_EDITOR_SOURCE_RESTORED",_gsf_manual_path,flush=True)
                except Exception as _gsf_restore_exc:
                    print("GSF_MANUAL_EDITOR_SOURCE_RESTORE_WARN",repr(str(_gsf_restore_exc)),flush=True)
            if (not _gsf_manual_path or not _gsf_manual_os.path.isfile(_gsf_manual_path)) and not GSF_WEB_MODE:
                try:
                    _gsf_manual_bytes=video.getvalue() if hasattr(video,"getvalue") else b""
                    _gsf_manual_path=_gsf_bytes_to_preview(_gsf_manual_bytes,"manual_scene_source") if _gsf_manual_bytes else ""
                except Exception:
                    _gsf_manual_path=""
            if _gsf_manual_path and _gsf_manual_os.path.isfile(_gsf_manual_path):
                print("GSF_MANUAL_EDITOR_OPEN",_gsf_manual_path,"exists="+str(_gsf_manual_os.path.isfile(_gsf_manual_path)),flush=True)
                st.session_state["gsf_manual_editor_open"]=True
                # Persist the exact Editor source across component/button reruns.
                st.session_state["gsf_source_path"]=str(_gsf_manual_path)
                st.session_state["gsf_editor_source_path"]=str(_gsf_manual_path)
                try:
                    _gsf_manual_source_duration=float(durata_video(_gsf_manual_path) or 15.0)
                except Exception:
                    _gsf_manual_source_duration=15.0
                _gsf_manual_duration=max(0.5,min(60.0,_gsf_manual_source_duration))
                _gsf_proxy_sig=__import__("hashlib").sha1((str(_gsf_manual_path)+"|"+str(_gsf_manual_os.path.getsize(_gsf_manual_path))+"|"+str(int(_gsf_manual_os.path.getmtime(_gsf_manual_path)))+"|editor2027-h264-v1").encode("utf-8")).hexdigest()[:16]
                _gsf_manual_proxy=_gsf_manual_os.path.join(str(GSF_PREVIEW_DIR),"editor2027_manual_"+_gsf_proxy_sig+".mp4")
                _gsf_proxy_ok=_gsf_manual_os.path.isfile(_gsf_manual_proxy) and _gsf_manual_os.path.getsize(_gsf_manual_proxy)>4096
                if not _gsf_proxy_ok:
                    with st.spinner("Preparazione Game Editor..."):
                        _gsf_proxy_ok=bool(crea_anteprima(_gsf_manual_path,_gsf_manual_proxy,0.0,_gsf_manual_duration))
                _gsf_manual_editor_media=_gsf_manual_proxy if _gsf_proxy_ok else _gsf_manual_path
                print("GSF_MANUAL_EDITOR_PROXY","source="+str(_gsf_manual_path),"editor="+str(_gsf_manual_editor_media),"proxy_ok="+str(bool(_gsf_proxy_ok)),"duration="+str(round(_gsf_manual_duration,3)),flush=True)
                _gsf_manual_state_slot=_gsf_editor_2027_state_key(_gsf_manual_path)
                _gsf_manual_component_key=_gsf_manual_state_slot+"_component"
                _gsf_manual_saved_state=st.session_state.get(_gsf_manual_state_slot)
                if not isinstance(_gsf_manual_saved_state,dict):
                    _gsf_manual_saved_state=_gsf_editor_2027_initial_state(_gsf_manual_duration)
                _gsf_manual_editor_state=_gsf_render_manual_editor_2027(
                    _gsf_manual_editor_media,height=720,key=_gsf_manual_component_key,initial_state=_gsf_manual_saved_state,clip_start=0.0,source_duration=float(_gsf_manual_duration)
                )
                if isinstance(_gsf_manual_editor_state,dict):
                    st.session_state[_gsf_manual_state_slot]=dict(_gsf_manual_editor_state)
                else:
                    _gsf_manual_editor_state=dict(_gsf_manual_saved_state)
                try:
                    _gsf_manual_start,_gsf_manual_render_duration=_gsf_editor_2027_clip_bounds(
                        _gsf_manual_editor_state,_gsf_manual_duration
                    )
                    _gsf_manual_render_kwargs=_gsf_editor_2027_render_kwargs(
                        _gsf_manual_editor_state,st.session_state
                    )
                    _gsf_manual_recipe=_gsf_recipe_selected(
                        "main_editor",_gsf_manual_start,_gsf_manual_render_duration,str(_gsf_manual_path),
                        master_token=(str(_gsf_manual_os.path.getsize(_gsf_manual_path))+":"+str(int(_gsf_manual_os.path.getmtime(_gsf_manual_path)))) if _gsf_manual_os.path.isfile(_gsf_manual_path) else "",
                        subtitles_enabled=bool(_gsf_manual_render_kwargs.get("subtitles_enabled",True)),
                        render_kwargs=_gsf_manual_render_kwargs,
                        editor_2027_state=dict(_gsf_manual_editor_state),
                        manual_hook=_GSF_HOOK_OFF_V102,
                    )
                    if st.session_state.get("gsf_final_recipe")!=_gsf_manual_recipe:
                        _gsf_set_final_recipe(_gsf_manual_recipe,source_label="Editor 2027")
                    try:
                        _gsf_manual_preview_bytes=None  # V107.1: stream from durable source path instead
                        if _gsf_manual_preview_bytes:
                            st.session_state["publication_preview_bytes"]=_gsf_manual_preview_bytes
                    except Exception:
                        pass
                except Exception as _gsf_manual_recipe_exc:
                    _gsf_manual_fallback_state=_gsf_editor_2027_initial_state(_gsf_manual_duration)
                    st.session_state["gsf_final_recipe"]={
                        "kind":"main_editor","start":0.0,"duration":_gsf_manual_duration,
                        "source_path":str(_gsf_manual_path),
                        "render_kwargs":_gsf_editor_2027_render_kwargs(_gsf_manual_fallback_state,st.session_state),
                    }
            else:
                st.warning("Video non disponibile nel Game Editor.")
        except Exception as _gsf_manual_editor_exc:
            print("GSF_MANUAL_EDITOR_ERROR",repr(str(_gsf_manual_editor_exc)),flush=True)
            st.session_state["gsf_manual_editor_recover_once"]=False
            st.warning("Game Editor non disponibile: recupero del video non riuscito.")
        try:
            with st.container(key="v1055_ad_manual_after_editor"):
                st.markdown(_gsf_v1057_ad_markup(3),unsafe_allow_html=True)
        except Exception as _gsf_manual_ad2_exc:
            print("GSF_MANUAL_AD2_SKIP",repr(str(_gsf_manual_ad2_exc)),flush=True)



    if modalita == "✋ Manuale":
        # Nessuna barra/numero di partenza: la selezione arriva solo dall'Editor.
        start = float(st.session_state.get("manual_start_editor", 0.0))
        duration = float(
            st.session_state.get("manual_duration_editor", duration)
        )
    else:
        if "auto_clip_scelta" not in st.session_state:
            st.session_state.auto_clip_scelta = None

        with st.container(key="gsf-major-create-ai"):
            _gsf_v291_ai_request=st.session_state.pop("gsf_v291_ai_request",None)
            _gsf_v291_direct_create=isinstance(_gsf_v291_ai_request,dict)
            _gsf_v291_profile=str(st.session_state.get("gsf_v291_engine_profile") or "")
            if _gsf_v291_profile in ("auto","director","action","reaction"):
                # Always enter the richest whole-video AI path. The V112+
                # ranker profile override below decides HOW candidates rank.
                modalita="🚀 AUTO TOTALE"
                _gsf_v291_duration=int(
                    st.session_state.get("gsf_v291_requested_duration",15) or 15
                )
                duration=float(_gsf_v291_duration if _gsf_v291_duration in (15,30,60) else 15)
            _gsf_create_ai_clicked=(
                st.button("CREA CON IA",use_container_width=True)
                or _gsf_v291_direct_create
            )
            st.markdown(
                '<div class="gsf-major-note">L’IA analizza il gameplay e ti propone i momenti migliori già pronti da scegliere.</div>',
                unsafe_allow_html=True,
            )
        from web.ai_engines_v412 import whole_source_meta, run_duration_analysis, write_results_meta, effective_analysis_duration
        try:
            _gsf_analysis_source_duration=float(durata_video(str(_source_path)) or 0)
        except Exception:
            _gsf_analysis_source_duration=0.0
        _gsf_requested_duration=float(duration)
        _gsf_effective_analysis_duration=effective_analysis_duration(_gsf_analysis_source_duration,_gsf_requested_duration)
        duration=_gsf_effective_analysis_duration
        _gsf_whole_meta=whole_source_meta(_gsf_analysis_source_duration,_gsf_requested_duration,
            request_id=str(st.session_state.get("gsf_v412_request_id") or ""),
            video_url=_gsf_media_url(_gsf_media_relative(_source_path)))
        _gsf_whole_source=_gsf_whole_meta is not None
        if _gsf_whole_source:
            duration=_gsf_analysis_source_duration
        if _gsf_create_ai_clicked and _gsf_whole_source:
            # The candidate is ready independently of AI completion. Never crop it.
            (GSF_SESSION_ROOT/"editor2027_current.txt").write_text(str(Path(_source_path).resolve()),encoding="utf-8")
            write_results_meta(GSF_PREVIEW_DIR,_gsf_whole_meta)
            st.session_state["auto_clip_candidati"]=[0.0]
            st.session_state["auto_clip_scelta"]=0.0
            st.session_state["clip_rifinite"]={0.0:duration}
            st.session_state["gsf_v112_brain_context"]={}
        elif _gsf_create_ai_clicked:
            write_results_meta(GSF_PREVIEW_DIR,{"items":[],"status":"analyzing","updated_at":time.time(),
                "request_id":str(st.session_state.get("gsf_v412_request_id") or "")})
        if _gsf_create_ai_clicked:
            _gsf_ai_run_error=""
            _gsf_save_persistent_state()
            st.session_state["gsf_ai_timing_start"]=time.perf_counter()
            st.session_state.pop("gsf_ai_result_timings",None)
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
                    float(duration),
                    # V412: each engine profile ranks differently, so it gets its own slot.
                    __import__("web.ai_engines_v412",fromlist=["cache_profile"]).cache_profile(_gsf_v291_profile),
                )
                cached_ai = st.session_state.get("gsf_fast_ai_cache", {}).get(cache_key_ai)
                if cached_ai is not None and not cached_ai.get("candidati"):
                    cached_ai = None
                st.session_state["gsf_ai_ranking_cache_hit"]=cached_ai is not None

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
                        try:
                            risultati_ai, ai_diag = run_duration_analysis(
                                analisi_input, modalita, _gsf_requested_duration,
                                source_duration=_gsf_analysis_source_duration,
                                rank=_gsf_ai_rank_v3, scan=_gsf_ai_scan_cached,
                                voice=_gsf_ai_voice_cached, cache_token=_video_cache_token
                            )
                        except Exception as _gsf_ai_rank_failure:
                            print("GSF_AI_RANK_FAILURE",type(_gsf_ai_rank_failure).__name__,flush=True)
                            risultati_ai, ai_diag = [], {}
                            _gsf_ai_run_error="L’analisi non è riuscita. Il gameplay è conservato: puoi riprovare o aprirlo nell’Editor dalla Home."

                        candidati = [start_ai for score_ai, start_ai in risultati_ai]
                        st.session_state.ai_director_scores = risultati_ai
                        st.session_state["gsf_ai_v3_diagnostics"] = ai_diag

                        # Solo Automatico e Momento migliore rifiniscono i bordi:
                        # per Azione/Reazioni non vogliamo spostare via il picco trovato.
                        if not _gsf_whole_source and __import__("web.ai_engines_v412",fromlist=["should_refine"]).should_refine(_gsf_v291_profile, modalita):
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
                            st.session_state.clip_rifinite = {0.0:duration} if _gsf_whole_source else {}

                if _gsf_whole_source:
                    _gsf_whole_meta["status"]="failed" if _gsf_ai_run_error else "success"
                    _gsf_whole_meta["error"]=_gsf_ai_run_error
                    write_results_meta(GSF_PREVIEW_DIR,_gsf_whole_meta)
                    if _gsf_ai_run_error:
                        candidati=[0.0]
                        st.session_state.ai_director_scores=[(0.0,0.0)]
                        st.session_state.clip_rifinite={0.0:duration}

                if cached_ai is None and candidati and not _gsf_ai_run_error:
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
                    _gsf_ai_empty_message=_gsf_ai_run_error or "Non ho trovato momenti validi. Il gameplay è conservato: puoi cambiare motore o aprirlo nell’Editor dalla Home."
                    from web.ai_engines_v412 import write_results_meta as _gsf_ai_write_failure
                    _gsf_ai_write_failure(GSF_PREVIEW_DIR,{"items":[],"status":"failed","error_code":"analysis_failed" if _gsf_ai_run_error else "no_moments",
                        "request_id":str(st.session_state.get("gsf_v412_request_id") or ""),"error":_gsf_ai_empty_message})
                    st.warning(_gsf_ai_empty_message)

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
                st.markdown('<div class="v70-short-heading"></div>', unsafe_allow_html=True)
                st.markdown('<div class="v70-short-sub"></div>', unsafe_allow_html=True)

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
                _gsf_preview_t0=time.perf_counter()
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

                # V412 AI ENGINES: results sheet read by /ai/results for the AI page.
                try:
                    from web.ai_engines_v412 import build_results_meta as _gsf_v412_meta
                    from web.ai_engines_v412 import write_results_meta as _gsf_v412_write
                    if "gsf_ai_result_timings" not in st.session_state:
                        st.session_state["gsf_ai_result_timings"]={**(st.session_state.get("gsf_ai_v3_diagnostics",{}).get("__meta__",{})),
                            "preview_seconds":round(time.perf_counter()-_gsf_preview_t0,3),
                            "request_seconds":round(time.perf_counter()-float(st.session_state.get("gsf_ai_timing_start",time.perf_counter())),3),
                            "ranking_cache_hit":bool(st.session_state.get("gsf_ai_ranking_cache_hit",False))}
                    if not _gsf_whole_source:
                        _gsf_v412_write(GSF_PREVIEW_DIR,_gsf_v412_meta(
                            [float(_c["start"]) for _c in _short_cards],
                            st.session_state.get("gsf_v112_brain_context") or {},
                            duration=float(duration),
                            profile=str(st.session_state.get("gsf_v291_engine_profile") or ""),
                            request_id=str(st.session_state.get("gsf_v412_request_id") or ""),
                            durations={round(float(_c["start"]),3):float(_c["preview_duration"]) for _c in _short_cards},
                            timings=st.session_state.get("gsf_ai_result_timings",{}),
                        ))
                except Exception as _gsf_v412_meta_exc:
                    print("GSF_V412_META_WARN",repr(str(_gsf_v412_meta_exc))[:220],flush=True)

                # V412 AUTOSAVE: every AI result, selection or "Cambia short"
                # updates ONE automatic draft in the Creator Hub (stable id, no
                # duplicates). Posted in the background so the UI never waits.
                try:
                    _gsf_v412_sig=repr((
                        st.session_state.get("gsf_v412_request_id"),
                        [round(float(_c["start"]),2) for _c in _short_cards],
                        round(float(st.session_state.get("auto_clip_scelta") or 0.0),2),
                    ))
                    if GSF_WEB_MODE and st.session_state.get("gsf_v412_autosaved")!=_gsf_v412_sig:
                        st.session_state["gsf_v412_autosaved"]=_gsf_v412_sig
                        _gsf_save_persistent_state()
                        _gsf_v412_state=json.loads(GSF_SESSION_STATE_FILE.read_text(encoding="utf-8")) if GSF_SESSION_STATE_FILE.is_file() else {}
                        _gsf_v412_src=str(st.session_state.get("gsf_source_name") or "Gameplay")[:120]
                        _gsf_v412_owner=re.sub(r"[^A-Za-z0-9_-]+","",str(st.session_state.get("gsf_upload_id") or ""))[:40] or hashlib.sha256(_gsf_v412_src.encode("utf-8")).hexdigest()[:16]
                        _gsf_v412_body=json.dumps({
                            "id":"draft_ai_"+_gsf_v412_owner,
                            "title":"Bozza IA · "+_gsf_v412_src,
                            "source_name":_gsf_v412_src,
                            "state":_gsf_v412_state if isinstance(_gsf_v412_state,dict) else {},
                        },ensure_ascii=False,default=str).encode("utf-8")
                        def _gsf_v412_post(_body=_gsf_v412_body,_sid=str(GSF_SESSION_ID)):
                            try:
                                import urllib.request as _gsf_v412_url
                                _gsf_v412_url.urlopen(_gsf_v412_url.Request(
                                    "http://127.0.0.1:8502/drafts/save",data=_body,method="POST",
                                    headers={"Content-Type":"application/json","X-GSF-Session-ID":_sid},
                                ),timeout=15).read()
                            except Exception as _gsf_v412_post_exc:
                                print("GSF_V412_AUTOSAVE_WARN",repr(str(_gsf_v412_post_exc))[:200],flush=True)
                        __import__("threading").Thread(target=_gsf_v412_post,daemon=True).start()
                except Exception as _gsf_v412_save_exc:
                    print("GSF_V412_AUTOSAVE_WARN",repr(str(_gsf_v412_save_exc))[:200],flush=True)

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

                st.markdown("", unsafe_allow_html=True)
                st.markdown(
                    '<div class="gsf-moment-head">'
                    '<div class="gsf-moment-title">Scegli il tuo momento</div>'
                    '<div class="gsf-moment-subtitle">Riproduci le tre anteprime direttamente qui e scegli il momento migliore.</div>'
                    '</div>',
                    unsafe_allow_html=True,
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
                                f'''<div class="v71-card-meta">
                                <div class="v70-short-card-label">{html.escape(_card["label"])}</div>
                                <div class="v70-short-card-time">{_card["start"]:.0f}s → {_card["end"]:.0f}s · {_card["preview_duration"]:.0f}s</div>
                                {f'<span class="v70-short-card-score">{_quality}</span>' if _quality else ''}
                                </div>''',
                                unsafe_allow_html=True,
                            )
                            _sub_key=f"v71_auto_sub_{_card['index']}"
                            if _sub_key not in st.session_state:
                                st.session_state[_sub_key]=bool(
                                    st.session_state.get("project_subtitles_enabled",True)
                                )
                            _sub_enabled=st.toggle(
                                "Sottotitoli automatici",
                                key=_sub_key,
                            )

                            if _is_selected:
                                st.session_state["project_subtitles_enabled"]=bool(_sub_enabled)
                                st.markdown(
                                    '<div class="v71-selected-pill">✓ CLIP SCELTA</div>',
                                    unsafe_allow_html=True,
                                )
                                _auto_recipe=_gsf_recipe_selected(
                                    "auto",
                                    float(_card["start"]),
                                    float(_card["preview_duration"]),
                                    str(_source_path),
                                    master_token=_gsf_upload_master_token(video),
                                    subtitles_enabled=bool(_sub_enabled),
                                    manual_hook=(
                                        st.session_state.get("hook_testo","")
                                        if st.session_state.get("hook_enabled_v102",True)
                                        else _GSF_HOOK_OFF_V102
                                    )
                                )
                                _gsf_set_final_recipe(_auto_recipe,source_label="AI")
                                st.session_state["publication_preview_bytes"]=_card_bytes
                            else:
                                if st.button(
                                    "SCEGLI QUESTO",
                                    key=f"v71_choose_short_{_card['index']}",
                                    type="secondary",
                                    use_container_width=True,
                                ):
                                    _gsf_v124_feedback(
                                        _gsf_v124_moment_for_start(float(_card["start"])),
                                        "selected",
                                    )
                                    st.session_state.auto_clip_scelta=float(_card["start"])
                                    st.session_state["auto_clip_duration"]=float(_card["preview_duration"])
                                    st.session_state["project_subtitles_enabled"]=bool(_sub_enabled)
                                    _auto_recipe=_gsf_recipe_selected(
                                        "auto",
                                        float(_card["start"]),
                                        float(_card["preview_duration"]),
                                        str(_source_path),
                                        master_token=_gsf_upload_master_token(video),
                                        subtitles_enabled=bool(_sub_enabled),
                                        manual_hook=(
                                            st.session_state.get("hook_testo","")
                                            if st.session_state.get("hook_enabled_v102",True)
                                            else _GSF_HOOK_OFF_V102
                                        )
                                    )
                                    _gsf_set_final_recipe(_auto_recipe,source_label="AI")
                                    st.session_state["publication_preview_bytes"]=_card_bytes
                                    st.session_state["preview_key"]=None
                                    st.session_state.pop("preview_bytes",None)
                                    st.session_state["gsf_editor_2027_inline_open"]=False
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
                edit_col = st.container()
                with edit_col:
                    with st.container(key=f"gsf-major-game-editor_{start:.2f}_{durata_effettiva:.2f}"):
                        _gsf_open_game_editor=st.button(
                            "APRI GAME EDITOR",
                            use_container_width=True,
                            key=f"edit_ai_{start:.2f}_{durata_effettiva:.2f}"
                        )
                        st.markdown(
                            '<div class="gsf-major-note">Ritocca il gameplay nel Game Editor oppure, se ti piace già così, prosegui verso lo Short finale.</div>',
                            unsafe_allow_html=True,
                        )
                    if _gsf_open_game_editor:
                        _gsf_v124_feedback(
                            _gsf_v124_moment_for_start(float(start)),
                            "opened_editor",
                        )
                        _selected_sub_key=f"v71_auto_sub_{int(_selected_card['index'])}"
                        _selected_sub_enabled=bool(
                            st.session_state.get(
                                _selected_sub_key,
                                st.session_state.get("project_subtitles_enabled",True)
                            )
                        )
                        st.session_state["project_subtitles_enabled"]=_selected_sub_enabled
                        _auto_recipe=_gsf_recipe_selected(
                            "auto",
                            float(start),
                            float(durata_effettiva),
                            str(_source_path),
                            master_token=_gsf_upload_master_token(video),
                            subtitles_enabled=_selected_sub_enabled,
                            manual_hook=(
                                st.session_state.get("hook_testo","")
                                if st.session_state.get("hook_enabled_v102",True)
                                else _GSF_HOOK_OFF_V102
                            )
                        )
                        _gsf_set_final_recipe(_auto_recipe,source_label="AI")
                        st.session_state["publication_preview_bytes"]=st.session_state.get("preview_bytes")
                        st.session_state["gsf_editor_2027_inline_open"]=True
                        st.session_state["gsf_editor_2027_start"]=float(start)
                        st.session_state.pop("inline_editor_id",None)
                        st.rerun()

                # ===== GAME EDITOR INLINE DELLA CLIP AI =====
                _this_inline_id=f"{start:.2f}_{durata_effettiva:.2f}"
                if (
                    st.session_state.get("gsf_editor_2027_inline_open",False)
                    and abs(float(st.session_state.get("gsf_editor_2027_start",start))-float(start))<0.05
                ):
                    try:
                        from editor_2027_embed import (
                            render_editor_2027_embed as _gsf_render_editor_2027_embed,
                            editor_2027_state_key as _gsf_inline_state_key,
                            editor_2027_initial_state as _gsf_inline_initial_state,
                            editor_2027_clip_bounds as _gsf_inline_clip_bounds,
                            editor_2027_render_kwargs as _gsf_inline_render_kwargs,
                        )
                        _gsf_ed27_path=_gsf_bytes_to_preview(
                            st.session_state.get("preview_bytes") or b"",
                            f"editor2027_{start:.2f}"
                        )
                        if _gsf_ed27_path:
                            _gsf_inline_slot=_gsf_inline_state_key(_gsf_ed27_path)
                            _gsf_inline_component_key=_gsf_inline_slot+"_component"
                            _gsf_inline_saved=st.session_state.get(_gsf_inline_slot)
                            if not isinstance(_gsf_inline_saved,dict):
                                _gsf_inline_saved=_gsf_inline_initial_state(float(durata_effettiva))
                            _gsf_inline_state=_gsf_render_editor_2027_embed(
                                _gsf_ed27_path,
                                height=660,
                                key=_gsf_inline_component_key,
                                initial_state=_gsf_inline_saved,
                                clip_start=float(start),
                                source_duration=float(durata_effettiva),
                            )
                            if isinstance(_gsf_inline_state,dict):
                                st.session_state[_gsf_inline_slot]=dict(_gsf_inline_state)
                            else:
                                _gsf_inline_state=dict(_gsf_inline_saved)
                            _gsf_inline_rel_start,_gsf_inline_duration=_gsf_inline_clip_bounds(
                                _gsf_inline_state,float(durata_effettiva)
                            )
                            _gsf_inline_kwargs=_gsf_inline_render_kwargs(
                                _gsf_inline_state,st.session_state
                            )
                            _gsf_inline_recipe=_gsf_recipe_selected(
                                "inline_editor",
                                float(start)+float(_gsf_inline_rel_start),
                                float(_gsf_inline_duration),
                                str(_source_path),
                                master_token=_gsf_upload_master_token(video),
                                subtitles_enabled=bool(_gsf_inline_kwargs.get("subtitles_enabled",True)),
                                render_kwargs=_gsf_inline_kwargs,
                                editor_2027_state=dict(_gsf_inline_state),
                                manual_hook=_GSF_HOOK_OFF_V102,
                            )
                            if st.session_state.get("gsf_final_recipe")!=_gsf_inline_recipe:
                                _gsf_set_final_recipe(
                                    _gsf_inline_recipe,source_label="Editor 2027"
                                )
                    except Exception as _gsf_ed27_exc:
                        st.error("Game Editor non disponibile: "+str(_gsf_ed27_exc))

                # Vecchio Editor disattivato: il Game Editor 2027 è l'unico editor inline.
                if False and st.session_state.get("inline_editor_id")==_this_inline_id:
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
                        _filter_key=f"inline_filter_{_this_inline_id}"
                        _filter_strength_key=f"inline_filter_strength_{_this_inline_id}"
                        _submode_key=f"inline_submode_{_this_inline_id}"

                        if _fmt_key not in st.session_state: st.session_state[_fmt_key]="9:16 Short"
                        if _zoom_key not in st.session_state: st.session_state[_zoom_key]=1.0
                        if _x_key not in st.session_state: st.session_state[_x_key]=0
                        if _y_key not in st.session_state: st.session_state[_y_key]=0
                        if _vol_key not in st.session_state: st.session_state[_vol_key]=100
                        if _bri_key not in st.session_state: st.session_state[_bri_key]=0.0
                        if _con_key not in st.session_state: st.session_state[_con_key]=1.0
                        if _spd_key not in st.session_state: st.session_state[_spd_key]=1.0
                        if _filter_key not in st.session_state: st.session_state[_filter_key]="Originale"
                        if _filter_strength_key not in st.session_state: st.session_state[_filter_strength_key]=70
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
                                filter_preset=st.session_state.get(_filter_key,"Originale"),
                                filter_intensity=st.session_state.get(_filter_strength_key,70),
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
                                    _reg=st.selectbox(
                                        "Parametro",
                                        ["Volume","Luminosità","Contrasto","Velocità"],
                                        key=f"inline_reg_v18_{_this_inline_id}"
                                    )
                                    if _reg=="Volume":
                                        st.session_state[_vol_key]=st.slider("Volume",0,200,int(st.session_state[_vol_key]),5,key=f"inline_vol_widget_v18_{_this_inline_id}")
                                    elif _reg=="Luminosità":
                                        st.session_state[_bri_key]=st.slider("Luminosità",-.30,.30,float(st.session_state[_bri_key]),.05,key=f"inline_bri_widget_v18_{_this_inline_id}")
                                    elif _reg=="Contrasto":
                                        st.session_state[_con_key]=st.slider("Contrasto",.70,1.50,float(st.session_state[_con_key]),.05,key=f"inline_con_widget_v18_{_this_inline_id}")
                                    else:
                                        st.session_state[_spd_key]=st.select_slider("Velocità",options=[.5,.75,1.0,1.25,1.5,2.0],value=float(st.session_state[_spd_key]),key=f"inline_spd_widget_v18_{_this_inline_id}")

                            st.markdown(
                                '<div class="gsf-icon-title gsf-v1061-filters-title">' +
                                _gsf_v67_badge("edit", "Filtri video", "indigo") +
                                '</div>',
                                unsafe_allow_html=True,
                                help="Modifica importante dell'immagine: visibile subito e inclusa nello Short finale."
                            )
                            st.segmented_control(
                                "Filtro video",
                                list(_GSF_V106_FILTER_PRESETS),
                                key=_filter_key,
                                label_visibility="collapsed"
                            )
                            st.slider(
                                "Intensità filtro",0,100,
                                int(st.session_state.get(_filter_strength_key,70)),
                                5,key=_filter_strength_key,
                                disabled=(st.session_state.get(_filter_key,"Originale")=="Originale")
                            )
                            st.session_state["v106_last_inline_filter_preset"]=st.session_state.get(_filter_key,"Originale")
                            st.session_state["v106_last_inline_filter_intensity"]=st.session_state.get(_filter_strength_key,70)

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
                                        _txt_actual=f"inline_txtcol_v18_{_this_inline_id}"
                                        _act_actual=f"inline_actcol_v18_{_this_inline_id}"
                                        _out_actual=f"inline_outcol_v18_{_this_inline_id}"
                                        _txt_draft=f"inline_txtcol_draft_v1061_{_this_inline_id}"
                                        _act_draft=f"inline_actcol_draft_v1061_{_this_inline_id}"
                                        _out_draft=f"inline_outcol_draft_v1061_{_this_inline_id}"
                                        for _draft,_actual,_base,_fallback in (
                                            (_txt_draft,_txt_actual,"subtitle_text_color","#FFFFFF"),
                                            (_act_draft,_act_actual,"subtitle_active_color","#FFD400"),
                                            (_out_draft,_out_actual,"subtitle_outline_color","#000000"),
                                        ):
                                            _actual_value=st.session_state.get(_actual,st.session_state.get(_base,_fallback))
                                            _snap=_draft+"_applied"
                                            if _draft not in st.session_state or st.session_state.get(_snap)!=_actual_value:
                                                st.session_state[_draft]=_actual_value
                                                st.session_state[_snap]=_actual_value
                                        c1,c2,c3=st.columns(3,gap="small")
                                        with c1:
                                            st.color_picker("Testo",key=_txt_draft)
                                            if st.button("Applica",key=f"inline_apply_txt_v1061_{_this_inline_id}",use_container_width=True):
                                                _c=st.session_state[_txt_draft]
                                                st.session_state[_txt_actual]=_c
                                                st.session_state["subtitle_text_color"]=_c
                                                st.session_state[_txt_draft+"_applied"]=_c
                                                st.rerun()
                                        with c2:
                                            st.color_picker("Attiva",key=_act_draft)
                                            if st.button("Applica",key=f"inline_apply_act_v1061_{_this_inline_id}",use_container_width=True):
                                                _c=st.session_state[_act_draft]
                                                st.session_state[_act_actual]=_c
                                                st.session_state["subtitle_active_color"]=_c
                                                st.session_state[_act_draft+"_applied"]=_c
                                                st.rerun()
                                        with c3:
                                            st.color_picker("Bordo",key=_out_draft)
                                            if st.button("Applica",key=f"inline_apply_out_v1061_{_this_inline_id}",use_container_width=True):
                                                _c=st.session_state[_out_draft]
                                                st.session_state[_out_actual]=_c
                                                st.session_state["subtitle_outline_color"]=_c
                                                st.session_state[_out_draft+"_applied"]=_c
                                                st.rerun()
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

    if modalita != "✋ Manuale":
        with st.container(key="v1055_ad_after_ai"):
            st.markdown(
                _gsf_v1057_ad_markup(3),
                unsafe_allow_html=True,
            )

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
    gioco = _gsf_v1053_detect_game()
    piattaforma = st.session_state.get("piattaforma", "YouTube Shorts")
    tono_social = st.session_state.get("tono_social", "Gaming forte")
    hook_testo = st.session_state.get("hook_testo", "")


    # ==========================================================
    # V54 — BETA FLOW: ONE FINAL RENDER + MINIMAL SOCIAL
    # ==========================================================
    _final_recipe=st.session_state.get("gsf_final_recipe",{}) or {}
    if GSF_WEB_MODE:
        from web.mobile_editor_recipe import local_final_is_current as _gsf_final_is_current
        if not _gsf_final_is_current(GSF_SESSION_ROOT):
            for _key in ("publication_final_bytes","publication_ready","social_final_context_v53","social_final_context_v54"):
                st.session_state.pop(_key,None)
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
        st.markdown('<div style="height:22px" aria-hidden="true"></div>', unsafe_allow_html=True)

        # V103.1 — Hook temporarily disabled.
        # Keep the engine code available, but do not show Hook UI/player and
        # do not burn an automatic/manual hook into the final export.
        _v103_hook_kind=str(_final_recipe.get("kind","") or "")
        _v103_hook_changed=False
        if _v103_hook_kind=="auto":
            if str(_final_recipe.get("manual_hook","") or "")!=_GSF_HOOK_OFF_V102:
                _final_recipe=dict(_final_recipe)
                _final_recipe["manual_hook"]=_GSF_HOOK_OFF_V102
                _v103_hook_changed=True
        elif _v103_hook_kind in ("main_editor","inline_editor"):
            _v103_kw=dict(_final_recipe.get("render_kwargs") or {})
            if str(_v103_kw.get("hook_text","") or ""):
                _v103_kw["hook_text"]=""
                _final_recipe=dict(_final_recipe)
                _final_recipe["render_kwargs"]=_v103_kw
                _v103_hook_changed=True

        st.session_state["hook_enabled_v102"]=False
        st.session_state["hook_testo"]=""
        st.session_state.pop("v102_hook_preview_bytes",None)
        st.session_state.pop("v102_hook_preview_sig",None)

        if _v103_hook_changed:
            st.session_state["gsf_final_recipe"]=_final_recipe
            for _k in (
                "publication_final_bytes","publication_ready",
                "social_final_context_v53","social_final_context_v54"
            ):
                st.session_state.pop(_k,None)

        _has_final=bool(
            isinstance(_final_video,(bytes,bytearray))
            and len(_final_video)>1024
        )

        if not _has_final:
            def _gsf_v107_queue_final_render():
                print("GSF_FINAL_QUEUE phase=enter",flush=True)
                if st.session_state.get("gsf_v107_final_render_pending") or st.session_state.get("gsf_v107_final_render_running"):
                    return
                print("GSF_FINAL_QUEUE phase=freeze",flush=True)
                _recipe=st.session_state.get("gsf_final_recipe")
                if isinstance(_recipe,dict) and _recipe:
                    _recipe=dict(_recipe)
                    try:
                        _v125_moment=_gsf_v124_moment_for_start(
                            float(_recipe.get("start",st.session_state.get("auto_clip_scelta",0.0)) or 0.0)
                        )
                        _v125_plan=dict((_v125_moment or {}).get("director_plan") or {})
                        if _v125_plan:
                            _recipe["ai_director_plan"]=_v125_plan
                            _recipe["ai_director_event"]=str((_v125_moment or {}).get("event") or "highlight")
                            _recipe["ai_director_rank"]=int((_v125_moment or {}).get("rank") or 0)


                            # V130 freezes the complete one-click package into
                            # the render recipe. Existing V125/V126 renderers
                            # execute cinematic/audio/thumbnail/hook decisions.
                            _v130_short=_gsf_v130_short_for_start(
                                float(_recipe.get("start",0.0) or 0.0)
                            )
                            if _v130_short:
                                _recipe["one_click_engine"]="v130-one-click-ai"
                                _recipe["one_click_v130"]=_v130_short
                                _recipe["ai_second_opinion"]=dict(
                                    _v130_short.get("second_opinion") or {}
                                )
                                _recipe["ai_editor_actions"]=list(
                                    _v130_short.get("editor_actions") or []
                                )

                                # V142 executes the full Director chain and freezes
                                # its decisions into the same render recipe.
                                _recipe=_gsf_v142_enrich_recipe(_recipe)
                                st.session_state["gsf_final_recipe"]=_recipe

                            # Manual hook and explicit OFF always win. Only an
                            # empty automatic AI recipe receives Director copy.
                            if str(_recipe.get("kind") or "")=="auto":
                                _v126_existing_hook=str(_recipe.get("manual_hook","") or "")
                                if not _v126_existing_hook:
                                    _v126_director_hook=_gsf_v126_hook_for_start(
                                        float(_recipe.get("start",0.0) or 0.0)
                                    )
                                    if _v126_director_hook:
                                        _recipe["manual_hook"]=_v126_director_hook
                            st.session_state["gsf_final_recipe"]=_recipe
                    except Exception as _v125_recipe_exc:
                        print("GSF_V125_PLAN_RECIPE_WARN",repr(str(_v125_recipe_exc))[:220],flush=True)
                    print("GSF_FINAL_QUEUE phase=mobile",flush=True)
                    _recipe=_gsf_saved_mobile_recipe(_recipe)
                    print("GSF_FINAL_QUEUE phase=job",flush=True)
                    st.session_state["gsf_final_recipe"]=_recipe
                    st.session_state["gsf_v107_render_recipe_snapshot"]=dict(_recipe)
                _src=""
                if isinstance(_recipe,dict):
                    _src=str(_recipe.get("source_path") or "")
                if not _src:
                    _src=str(st.session_state.get("gsf_source_path") or "")
                if _src:
                    st.session_state["gsf_v107_render_source_snapshot"]=_src
                st.session_state["gsf_v107_final_render_pending"]=True
                st.session_state["gsf_v107_final_render_running"]=True
                st.session_state["gsf_v1302_social_open"]=True
                st.session_state["gsf_v107_render_started_at"]=__import__("time").time()
                st.session_state["gsf_v107_render_toast_shown"]=False
                st.session_state["gsf_v107_render_complete_notified"]=True
                try:
                    _job_path=GSF_SESSION_ROOT/"render_job.json"
                    _job_tmp=GSF_SESSION_ROOT/"render_job.json.tmp"
                    _job_tmp.write_text(__import__("json").dumps({
                        "status":"running",
                        "started_at":st.session_state["gsf_v107_render_started_at"],
                        "source_path":_src,
                        "recipe":dict(_recipe) if isinstance(_recipe,dict) else {},
                    },ensure_ascii=False,default=str),encoding="utf-8")
                    __import__("os").replace(_job_tmp,_job_path)
                except Exception as _job_exc:
                    print("GSF_FINAL_JOB_WRITE_WARN",repr(str(_job_exc)),flush=True)
                print("GSF_FINAL_QUEUE phase=queued",flush=True)

            try:
                _job_path=GSF_SESSION_ROOT/"render_job.json"
                if _job_path.is_file():
                    _job=__import__("json").loads(_job_path.read_text(encoding="utf-8"))
                    if isinstance(_job,dict) and str(_job.get("status") or "")=="running":
                        _started=float(_job.get("started_at") or 0.0)
                        _age=__import__("time").time()-_started if _started else 999999.0
                        if _age>900.0:
                            _job["status"]="stale"
                            _job["stale_at"]=__import__("time").time()
                            _tmp=_job_path.with_suffix(".tmp")
                            _tmp.write_text(__import__("json").dumps(_job,ensure_ascii=False,default=str),encoding="utf-8")
                            __import__("os").replace(_tmp,_job_path)
                            st.session_state["gsf_v107_final_render_running"]=False
                            st.session_state["gsf_v107_final_render_pending"]=False
                        else:
                            st.session_state["gsf_v107_final_render_running"]=True
                        st.session_state["gsf_v107_render_started_at"]=_started
                        _job_recipe=_job.get("recipe")
                        _job_src=str(_job.get("source_path") or "")
                        if isinstance(_job_recipe,dict) and _job_recipe:
                            st.session_state["gsf_v107_render_recipe_snapshot"]=dict(_job_recipe)
                        if _job_src:
                            st.session_state["gsf_v107_render_source_snapshot"]=_job_src
            except Exception:
                pass

            try:
                _gsf_restore_src=str(
                    st.session_state.get("gsf_v107_render_source_snapshot")
                    or st.session_state.get("gsf_source_path")
                    or ""
                )
                _gsf_restore_root=(__import__("pathlib").Path(
                    __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
                )/"sessions").resolve()
                _gsf_restore_rel=__import__("pathlib").Path(_gsf_restore_src).resolve().relative_to(_gsf_restore_root)
                _gsf_restore_sid=str(_gsf_restore_rel.parts[0]) if _gsf_restore_rel.parts else ""
                _gsf_restore_final=_gsf_restore_root/_gsf_restore_sid/"media"/"gaming_short_finale_share.mp4"
                _gsf_restore_started=float(st.session_state.get("gsf_v107_render_started_at",0.0) or 0.0)
                if (
                    _gsf_restore_sid
                    and _gsf_restore_final.is_file()
                    and _gsf_restore_final.stat().st_size>1024
                    and (not GSF_WEB_MODE or _gsf_final_is_current(GSF_SESSION_ROOT))
                    and (_gsf_restore_started<=0.0 or _gsf_restore_final.stat().st_mtime>=_gsf_restore_started-1.0)
                ):
                    _gsf_restored_bytes=_gsf_restore_final.read_bytes()
                    st.session_state["publication_final_bytes"]=_gsf_restored_bytes
                    st.session_state["publication_ready"]=True
                    if st.session_state.get("gsf_v107_final_render_running",False):
                        st.session_state["gsf_v107_render_done_toast"]=True
                    st.session_state["gsf_v107_final_render_running"]=False
                    st.session_state["gsf_v107_final_render_pending"]=False
            except Exception:
                pass

            # V109: a dead/stale job must never leave CREA SHORT disabled.
            try:
                _gsf_v109_job_path=GSF_SESSION_ROOT/"render_job.json"
                if st.session_state.get("gsf_v107_final_render_running",False):
                    _gsf_v109_job={}
                    if _gsf_v109_job_path.is_file():
                        try:
                            _gsf_v109_job=__import__("json").loads(
                                _gsf_v109_job_path.read_text(encoding="utf-8")
                            )
                        except Exception:
                            _gsf_v109_job={}
                    if not isinstance(_gsf_v109_job,dict):
                        _gsf_v109_job={}
                    _gsf_v109_status=str(_gsf_v109_job.get("status") or "")
                    _gsf_v109_pid=int(_gsf_v109_job.get("pid") or 0)
                    _gsf_v109_started=float(
                        _gsf_v109_job.get("started_at")
                        or st.session_state.get("gsf_v107_render_started_at")
                        or 0.0
                    )
                    _gsf_v109_age=(
                        __import__("time").time()-_gsf_v109_started
                        if _gsf_v109_started else 999999.0
                    )
                    _gsf_v109_alive=False
                    if _gsf_v109_pid>1:
                        try:
                            __import__("os").kill(_gsf_v109_pid,0)
                            _gsf_v109_alive=True
                        except Exception:
                            _gsf_v109_alive=False
                    _gsf_v109_dead=(
                        _gsf_v109_status not in ("","running")
                        or (_gsf_v109_pid>1 and not _gsf_v109_alive and _gsf_v109_age>20.0)
                        or (_gsf_v109_pid<=1 and _gsf_v109_age>45.0)
                    )
                    if _gsf_v109_dead:
                        st.session_state["gsf_v107_final_render_running"]=False
                        st.session_state["gsf_v107_final_render_pending"]=False
                        if _gsf_v109_status=="running":
                            _gsf_v109_job["status"]="stale"
                            _gsf_v109_job["stale_at"]=__import__("time").time()
                            try:
                                _gsf_v109_tmp=_gsf_v109_job_path.with_suffix(".tmp")
                                _gsf_v109_tmp.write_text(
                                    __import__("json").dumps(
                                        _gsf_v109_job,ensure_ascii=False,default=str
                                    ),
                                    encoding="utf-8",
                                )
                                __import__("os").replace(_gsf_v109_tmp,_gsf_v109_job_path)
                            except Exception:
                                pass
                        print(
                            "GSF_FINAL_STALE_RELEASED",
                            "status="+_gsf_v109_status,
                            "pid="+str(_gsf_v109_pid),
                            "age="+str(round(_gsf_v109_age,1)),
                            flush=True,
                        )
            except Exception as _gsf_v109_reconcile_exc:
                print("GSF_FINAL_RECONCILE_WARN",repr(str(_gsf_v109_reconcile_exc)),flush=True)

            # V125 AI alternatives: replace the currently selected rank for real.
            try:
                _v125_brain=st.session_state.get("gsf_v112_brain_context") or {}
                _v125_selected=list(_v125_brain.get("selected") or []) if isinstance(_v125_brain,dict) else []
                _v125_alternates=list(_v125_brain.get("alternates") or []) if isinstance(_v125_brain,dict) else []
                _v125_current_start=float(st.session_state.get("auto_clip_scelta",0.0) or 0.0)
                _v125_current=min(
                    _v125_selected,
                    key=lambda row:abs(float((row or {}).get("start") or 0.0)-_v125_current_start)
                ) if _v125_selected else {}
                _v125_rank=int((_v125_current or {}).get("rank") or 0)
                _v125_overrides=st.session_state.get("gsf_v125_rank_overrides") or {}
                if False and _v125_rank>0 and _v125_alternates:
                    st.markdown(
                        '<div class="gsf-v125-alt-head"><b>ALTERNATIVE AI</b>'
                        '<span>Non ti convince? Sostituisci solo questa scena senza rifare l’analisi.</span></div>',
                        unsafe_allow_html=True,
                    )
                    _v125_cols=st.columns(min(3,len(_v125_alternates)),gap="small")
                    for _v125_i,_v125_alt in enumerate(_v125_alternates[:3]):
                        if not isinstance(_v125_alt,dict):
                            continue
                        _v125_alt_start=float(_v125_alt.get("start") or 0.0)
                        _v125_alt_event=str(_v125_alt.get("event") or "highlight").replace("_"," ").upper()
                        _v125_alt_conf=int(round(float(_v125_alt.get("confidence") or 0.0)*100))
                        with _v125_cols[_v125_i % len(_v125_cols)]:
                            if st.button(
                                _v125_alt_event+" · "+str(_v125_alt_conf)+"%",
                                key=f"gsf_v125_alt_{_v125_rank}_{_v125_i}_{_v125_alt_start:.2f}",
                                use_container_width=True,
                            ):
                                _new_overrides=dict(_v125_overrides) if isinstance(_v125_overrides,dict) else {}
                                _new_overrides[str(_v125_rank)]=_v125_alt_start
                                st.session_state["gsf_v125_rank_overrides"]=_new_overrides
                                _gsf_v124_feedback(dict(_v125_current or {}),"replaced")
                                st.session_state["auto_clip_scelta"]=_v125_alt_start
                                st.session_state["preview_key"]=None
                                st.session_state.pop("preview_bytes",None)
                                st.session_state["gsf_editor_2027_inline_open"]=False
                                st.rerun()
                    if isinstance(_v125_overrides,dict) and str(_v125_rank) in _v125_overrides:
                        if st.button(
                            "RIPRISTINA SCELTA AI",
                            key=f"gsf_v125_restore_{_v125_rank}",
                            use_container_width=True,
                        ):
                            _new_overrides=dict(_v125_overrides)
                            _new_overrides.pop(str(_v125_rank),None)
                            st.session_state["gsf_v125_rank_overrides"]=_new_overrides
                            _restore_start=float((_v125_current or {}).get("replaced_from_start") or 0.0)
                            if _restore_start>0:
                                st.session_state["auto_clip_scelta"]=_restore_start
                            st.session_state["preview_key"]=None
                            st.session_state.pop("preview_bytes",None)
                            st.session_state["gsf_editor_2027_inline_open"]=False
                            st.rerun()
            except Exception as _v125_alt_exc:
                print("GSF_V125_ALT_UI_WARN",repr(str(_v125_alt_exc))[:220],flush=True)

            # V130 One Click AI: the three ranked moments are already
            # mounted as edit packages. Encoding remains lazy to avoid wasting
            # CPU/cloud cost on clips the creator will not publish.
            try:
                _v130_brain=st.session_state.get("gsf_v112_brain_context") or {}
                _v130_pack=dict(_v130_brain.get("one_click") or {}) if isinstance(_v130_brain,dict) else {}
                _v130_current_start=float(st.session_state.get("auto_clip_scelta",0.0) or 0.0)
                _v130_short=_gsf_v130_short_for_start(_v130_current_start)
                if False and _v130_pack.get("ready") and _v130_short:
                    _v130_escape=__import__("html").escape
                    _v130_event=str(_v130_short.get("reason") or _v130_short.get("event") or "HIGHLIGHT")
                    _v130_conf=int(round(float(_v130_short.get("confidence") or 0.0)*100))
                    _v130_count=int(_v130_pack.get("prepared_count") or 0)
                    _v130_mount=dict(_v130_short.get("mount") or {})
                    _v130_frame=dict(_v130_mount.get("framing") or {})
                    _v130_cine=dict(_v130_mount.get("cinematic") or {})
                    _v130_audio=dict(_v130_mount.get("audio") or {})
                    _v130_bits=[]
                    if _v130_frame.get("smart_reframe"):
                        _v130_bits.append("reframe")
                    if ((_v130_cine.get("replay") or {}).get("enabled")):
                        _v130_bits.append("replay")
                    if ((_v130_cine.get("slow_motion") or {}).get("enabled")):
                        _v130_bits.append("slow motion")
                    if str(_v130_audio.get("accent") or "none")!="none":
                        _v130_bits.append("sound design")
                    _v130_caption=dict(_v130_mount.get("captions") or {})
                    if _v130_caption:
                        _v130_bits.append("caption semantiche")
                    _v130_feature_text=" · ".join(_v130_bits[:5]) or "montaggio AI"
                    st.markdown(
                        '<div class="gsf-v130-oneclick">'
                        '<div><b>ONE CLICK AI</b><span>AI SECOND OPINION · '+str(_v130_count)+' Short preparati</span></div>'
                        '<small><strong>'+_v130_escape(_v130_event.upper())+' · '+str(_v130_conf)+'%</strong>'
                        ' · '+_v130_escape(_v130_feature_text)+'</small>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
            except Exception as _v130_ui_exc:
                print("GSF_V130_UI_WARN",repr(str(_v130_ui_exc))[:220],flush=True)

            with st.container(key="gsf-major-create-short"):
                st.markdown('<div class="gsf-major-note gsf-v1302-create-note">L’IA crea il tuo Short, applica le modifiche e controlla automaticamente qualità e formato. Quando è pronto puoi salvarlo, condividerlo o pubblicarlo.</div>',unsafe_allow_html=True)
                _v1054_create_final_clicked=st.button(
                    "CREA SHORT FINALE",
                    use_container_width=True,
                    key="create_final_short_v54",
                    disabled=bool(st.session_state.get("gsf_v107_final_render_running",False)),
                )

            if _v1054_create_final_clicked:
                print("GSF_FINAL_BUTTON_CLICK",flush=True)
                _gsf_v107_queue_final_render()

            _gsf_v107_pending=bool(
                st.session_state.pop("gsf_v107_final_render_pending",False)
            )
            if st.session_state.pop("gsf_v107_render_done_toast",False):
                st.toast("✅ Short completato.")
            if _gsf_v107_pending and not st.session_state.get("gsf_v107_render_toast_shown",False):
                st.toast("🎬 Short in lavorazione · puoi continuare a usare l’app.")
                st.session_state["gsf_v107_render_toast_shown"]=True
            if _gsf_v107_pending:
                _snap=st.session_state.get("gsf_v107_render_recipe_snapshot")
                if isinstance(_snap,dict) and _snap:
                    _final_recipe=dict(_snap)
                    st.session_state["gsf_final_recipe"]=_final_recipe
                _src_snap=str(st.session_state.get("gsf_v107_render_source_snapshot") or "")
                if _src_snap:
                    st.session_state["gsf_source_path"]=_src_snap
                    st.session_state["gsf_editor_source_path"]=_src_snap

            _v1054_create_final_clicked=bool(
                _v1054_create_final_clicked or _gsf_v107_pending
            )
            if _v1054_create_final_clicked:
                try:
                    print(
                        "GSF_FINAL_CREATE_CLICK",
                        "recipe="+str(bool(st.session_state.get("gsf_final_recipe"))),
                        "source="+str(bool(st.session_state.get("gsf_source_path"))),
                        flush=True,
                    )
                except Exception:
                    pass
            st.markdown(
                '',
                unsafe_allow_html=True,
            )
            with st.container(key="v1054_ad_after_final_action"):
                st.markdown(
                    _gsf_v1057_ad_markup(4),
                    unsafe_allow_html=True,
                )
            if _v1054_create_final_clicked:
                try:
                    print(
                        "GSF_FINAL_RENDER_ENTER",
                        "recipe="+str(bool(st.session_state.get("gsf_final_recipe"))),
                        "source="+str(bool(st.session_state.get("gsf_source_path"))),
                        flush=True,
                    )
                except Exception:
                    pass
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
            if _v1054_create_final_clicked:
                _gsf_completed_final=locals().get("_final_video")
                if isinstance(_gsf_completed_final,(bytes,bytearray)) and len(_gsf_completed_final)>1024:
                    st.session_state["publication_final_bytes"]=bytes(_gsf_completed_final)
                    st.session_state["publication_ready"]=True
                    st.session_state["gsf_v107_final_render_running"]=False
                    st.session_state["gsf_v107_render_done_toast"]=True
                    print("GSF_FINAL_RENDER_READY",len(_gsf_completed_final),flush=True)
                    st.rerun()
        else:
            st.empty()

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
                if st.button('PUBBLICA', type='primary', use_container_width=True, key='gsf_share_download_top'):
                    st.session_state[
                        "show_social_publish_v54"
                    ]=not bool(
                        st.session_state.get(
                            "show_social_publish_v54",False
                        )
                    )

            def _gsf_v1302_youtube_short_bytes(video_bytes):
                raw=bytes(video_bytes or b"")
                if not raw:
                    return raw
                _tmp=None
                try:
                    _tempfile=__import__("tempfile")
                    _subprocess=__import__("subprocess")
                    _json=__import__("json")
                    _shutil=__import__("shutil")
                    _tmp=Path(_tempfile.mkdtemp(prefix="gsf_youtube_short_"))
                    _src=_tmp/"input.mp4"
                    _out=_tmp/"short.mp4"
                    _src.write_bytes(raw)
                    _probe=_subprocess.run(
                        [
                            "/usr/bin/ffprobe","-v","error",
                            "-select_streams","v:0",
                            "-show_entries","stream=width,height:format=duration",
                            "-of","json",str(_src),
                        ],
                        stdout=_subprocess.PIPE,stderr=_subprocess.PIPE,text=True,timeout=25,
                    )
                    _data=_json.loads(_probe.stdout or "{}")
                    _streams=list(_data.get("streams") or [])
                    _stream=_streams[0] if _streams else {}
                    _w=int(_stream.get("width") or 0)
                    _h=int(_stream.get("height") or 0)
                    _dur=float((_data.get("format") or {}).get("duration") or 0.0)
                    if _w>0 and _h>0 and _w<=_h and (_dur<=0 or _dur<=180.0):
                        return raw

                    _vf=(
                        "[0:v]split=2[bg][fg];"
                        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
                        "crop=1080:1920,boxblur=20:1[bg2];"
                        "[fg]scale=1080:1920:force_original_aspect_ratio=decrease[fg2];"
                        "[bg2][fg2]overlay=(W-w)/2:(H-h)/2,setsar=1[v]"
                    )
                    _cmd=[
                        "/usr/bin/ffmpeg","-hide_banner","-loglevel","error","-y",
                        "-i",str(_src),
                        "-filter_complex",_vf,
                        "-map","[v]","-map","0:a?",
                        "-t","179.8",
                        "-c:v","libx264","-preset","veryfast","-crf","18",
                        "-pix_fmt","yuv420p",
                        "-c:a","aac","-b:a","128k",
                        "-movflags","+faststart",
                        str(_out),
                    ]
                    _run=_subprocess.run(
                        _cmd,stdout=_subprocess.PIPE,stderr=_subprocess.PIPE,text=True,timeout=240
                    )
                    if _run.returncode==0 and _out.is_file() and _out.stat().st_size>1024:
                        print("GSF_V1302_YOUTUBE_SHORT_NORMALIZED",_w,_h,_dur,flush=True)
                        return _out.read_bytes()
                    print("GSF_V1302_YOUTUBE_SHORT_NORMALIZE_WARN",_run.stderr[-220:],flush=True)
                    return raw
                except Exception as _exc:
                    print("GSF_V1302_YOUTUBE_SHORT_WARN",repr(str(_exc))[:220],flush=True)
                    return raw
                finally:
                    if _tmp is not None:
                        try:
                            __import__("shutil").rmtree(_tmp,ignore_errors=True)
                        except Exception:
                            pass


            if (
                st.session_state.get("gsf_v1302_social_open",False)
                or _has_final
                or st.session_state.get("gsf_v107_final_render_running",False)
            ):
                _v1302_status={}
                if GSF_WEB_MODE:
                    try:
                        _u=__import__("urllib.request",fromlist=["Request","urlopen"])
                        _req=_u.Request(
                            "http://127.0.0.1:8502/job/status",
                            headers={"X-GSF-Session-ID":str(GSF_SESSION_ID)},
                            method="GET",
                        )
                        _v1302_status=__import__("json").loads(
                            _u.urlopen(_req,timeout=2.0).read().decode("utf-8")
                        )
                    except Exception:
                        _v1302_status={}

                _v1302_final_ready=bool(
                    st.session_state.get("publication_ready",False)
                    or st.session_state.get("publication_final_bytes")
                    or (_v1302_status or {}).get("download_ready")
                )
                _v1302_quality=str((_v1302_status or {}).get("quality_status") or "")
                _v1302_qscore=(_v1302_status or {}).get("quality_score")
                _v1302_rendering=bool(
                    st.session_state.get("gsf_v107_final_render_running",False)
                    or str((_v1302_status or {}).get("render_status") or "")=="running"
                )

                if not _v1302_final_ready:
                    _v1302_progress=34
                    _v1302_phase="render"
                elif _v1302_quality in ("","analyzing"):
                    _v1302_progress=74
                    _v1302_phase="quality"
                else:
                    _v1302_progress=100
                    _v1302_phase=("ready" if _v1302_quality in ("pass","warn") else "check")
                _v1302_steps=(
                    '<span class="'+('done' if _v1302_progress>34 else 'active')+'">CREO SHORT'+(' ✓' if _v1302_progress>34 else '')+'</span>'
                    '<i>›</i><span class="'+('done' if _v1302_progress>=100 else ('active' if _v1302_progress>34 else ''))+'">QUALITY CHECK'+(' ✓' if _v1302_progress>=100 and _v1302_phase=="ready" else '')+'</span>'
                    '<i>›</i><span class="'+('done' if _v1302_phase=="ready" else '')+'">PRONTO'+(' ✓' if _v1302_phase=="ready" else '')+'</span>'
                )
                st.markdown(
                    '<div class="gsf-v1302-live-progress '+_v1302_phase+'">'
                    '<div class="gsf-v1302-progress-steps">'+_v1302_steps+'</div>'
                    '<div class="gsf-v1302-progress-track"><span style="width:'+str(_v1302_progress)+'%"></span></div>'
                    '</div>',unsafe_allow_html=True
                )
                _v1302_recipe=st.session_state.get("gsf_final_recipe",{}) or {}
                _v1302_start=float(_v1302_recipe.get("start",0.0) or 0.0)
                _v1302_game=_gsf_v1053_detect_game()
                _v1302_tone=st.session_state.get("tono_social","Gaming forte")
                _v1302_base=_gsf_finalize_publish_pack(
                    _gsf_build_publish_pack(
                        _v1302_start,
                        platform="YouTube Shorts",
                        game=_v1302_game,
                        tone=_v1302_tone,
                    )
                )
                # Keep V124/V130 Director social intelligence as the default copy even
                # though V130.2 exposes only one shared form.
                _v1302_ai_social={}
                try:
                    _v1302_brain=st.session_state.get("gsf_v112_brain_context") or {}
                    _v1302_rows=list(_v1302_brain.get("selected") or []) if isinstance(_v1302_brain,dict) else []
                    if _v1302_rows:
                        _v1302_nearest=min(
                            _v1302_rows,
                            key=lambda row:abs(float((row or {}).get("start") or 0.0)-_v1302_start)
                        )
                        _v1302_plan=dict((_v1302_nearest or {}).get("director_plan") or {})
                        _v1302_social_all=dict(((_v1302_plan.get("text") or {}).get("social") or {}))
                        _v1302_ai_social=dict(_v1302_social_all.get("youtube") or {})
                    if not _v1302_ai_social:
                        _v1302_social_all=st.session_state.get("gsf_v124_social_pack") or {}
                        if isinstance(_v1302_social_all,dict):
                            _v1302_ai_social=dict(_v1302_social_all.get("youtube") or {})
                except Exception as _v1302_social_seed_exc:
                    print("GSF_V1302_SOCIAL_SEED_WARN",repr(str(_v1302_social_seed_exc))[:220],flush=True)
                    _v1302_ai_social={}

                _v1302_ctx=_gsf_publish_context_token(_v1302_base)
                _v1302_title_key="gsf_v1302_shared_title_"+_v1302_ctx
                _v1302_desc_key="gsf_v1302_shared_description_"+_v1302_ctx
                _v1302_tags_key="gsf_v1302_shared_hashtags_"+_v1302_ctx
                _v1302_default_title=str(
                    _v1302_ai_social.get("title")
                    or _v1302_base.get("selected_title",_v1302_base.get("title",""))
                    or ""
                )
                _v1302_default_description=str(
                    _v1302_ai_social.get("description")
                    or _gsf_social_clean_description(_v1302_base)
                    or ""
                )
                _v1302_default_tags=" ".join(
                    str(x) for x in (_v1302_ai_social.get("hashtags") or [])
                    if str(x).strip()
                ) or " ".join(_v1302_base.get("hashtags",[]) or [])
                if _v1302_title_key not in st.session_state:
                    st.session_state[_v1302_title_key]=_v1302_default_title
                if _v1302_desc_key not in st.session_state:
                    st.session_state[_v1302_desc_key]=_v1302_default_description
                if _v1302_tags_key not in st.session_state:
                    st.session_state[_v1302_tags_key]=_v1302_default_tags

                with st.container(key="v1055_social_composer_shared"):
                    _v1302_save_bytes=st.session_state.get("publication_final_bytes") or b""
                    _v1302_title=st.text_input("Titolo",key=_v1302_title_key)
                    _v1302_description=st.text_area(
                        "Descrizione",key=_v1302_desc_key,height=120
                    )
                    _v1302_hashtags=st.text_input("Hashtag",key=_v1302_tags_key)

                    st.markdown('<div class="gsf-v1302-social-pick">Scegli dove pubblicare</div>',unsafe_allow_html=True)
                    for _v1302_key in ("youtube","tiktok","instagram"):
                        st.session_state.setdefault("gsf_v1302_target_"+_v1302_key,False)
                    _v1302_c1,_v1302_c2,_v1302_c3,_v1302_c4=st.columns(4,gap="small")
                    _v1302_defs=[
                        ("youtube","▶","YouTube",_v1302_c1),
                        ("tiktok","♪","TikTok",_v1302_c2),
                        ("instagram","◎","Instagram",_v1302_c3),
                        ("facebook","f","Facebook",_v1302_c4),
                    ]
                    for _v1302_key,_v1302_icon,_v1302_name,_v1302_col in _v1302_defs:
                        with _v1302_col:
                            _v1302_state=bool(st.session_state.get("gsf_v1302_target_"+_v1302_key,False))
                            if st.button(
                                _v1302_icon,
                                key="gsf_v1302_icon_"+_v1302_key,
                                width="stretch",
                                disabled=(_v1302_key=="facebook"),
                                help=(("Selezionato · " if _v1302_state else "")+_v1302_name if _v1302_key!="facebook" else "Facebook · pubblicazione diretta in attesa dei permessi Meta Page."),
                            ):
                                st.session_state["gsf_v1302_target_"+_v1302_key]=not _v1302_state
                                st.rerun()

                    _v1302_youtube=bool(st.session_state.get("gsf_v1302_target_youtube",False))
                    _v1302_tiktok=bool(st.session_state.get("gsf_v1302_target_tiktok",False))
                    _v1302_instagram=bool(st.session_state.get("gsf_v1302_target_instagram",False))
                    _v1302_targets=[]
                    if _v1302_youtube:_v1302_targets.append("YouTube")
                    if _v1302_tiktok:_v1302_targets.append("TikTok")
                    if _v1302_instagram:_v1302_targets.append("Instagram")

                    _v1302_a1,_v1302_a2=st.columns(2,gap="small")
                    with _v1302_a1:
                        st.download_button(
                            "⇩",data=bytes(_v1302_save_bytes),file_name="gaming_short_finale.mp4",
                            mime="video/mp4",width="stretch",key="gsf_v1302_save",
                            disabled=not bool(_v1302_final_ready and _v1302_save_bytes),
                        )
                    with _v1302_a2:
                        if _v1302_final_ready and _v1302_save_bytes:
                            try:
                                _v1302_b64=__import__("base64").b64encode(bytes(_v1302_save_bytes)).decode("ascii")
                                __import__("streamlit.components.v1",fromlist=["html"]).html(
                                    """<button id="gsfShare" class="gsfShare">↗</button><script>
            const b=document.getElementById('gsfShare');b.onclick=async()=>{try{const raw=atob('"""+_v1302_b64+"""');const a=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)a[i]=raw.charCodeAt(i);const f=new File([a],'gaming_short_finale.mp4',{type:'video/mp4'});if(navigator.share&&(!navigator.canShare||navigator.canShare({files:[f]}))){await navigator.share({files:[f],title:'Gaming Short'});}else{alert('Condivisione non disponibile su questo browser. Usa Salva.');}}catch(e){if(e.name!=='AbortError')alert('Condivisione non disponibile. Usa Salva.');}};</script><style>body{margin:0;background:transparent}.gsfShare{width:100%;height:44px;border-radius:14px;border:1px solid rgba(138,174,199,.48);background:linear-gradient(145deg,rgba(255,255,255,.96),rgba(241,247,252,.95));color:#365c76;font:800 15px system-ui;box-shadow:0 8px 18px rgba(49,92,125,.08)}</style>""",
                                    height=48,
                                )
                            except Exception:
                                st.button("↗",disabled=True,width="stretch",key="gsf_v1302_share_fallback")
                        else:
                            st.button("↗",disabled=True,width="stretch",key="gsf_v1302_share_wait")

                    _v1302_missing=[]
                    for _v1302_platform in _v1302_targets:
                        try:
                            _ok,_msg=_gsf_social_connection_status(_v1302_platform)
                        except Exception:
                            _ok,_msg=False,""
                        if not _ok:
                            _v1302_missing.append(_v1302_platform)

                    if _v1302_missing:
                        st.caption("Da collegare: "+", ".join(_v1302_missing))
                        st.link_button(
                            "COLLEGA SOCIAL",
                            "/social-connect",
                            use_container_width=True,
                        )

                    _v1302_quality_done=_v1302_quality in ("pass","warn")
                    _v1302_can_publish=bool(
                        _v1302_final_ready
                        and _v1302_quality_done
                        and _v1302_targets
                        and not _v1302_missing
                    )
                    if st.button(
                        "PUBBLICA",
                        type="primary",
                        use_container_width=True,
                        key="gsf_v1302_publish_all",
                        disabled=not _v1302_can_publish,
                    ):
                        _v1302_video=st.session_state.get("publication_final_bytes")
                        if not _v1302_video:
                            try:
                                _v1302_root=Path(
                                    __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
                                )/"sessions"/str(GSF_SESSION_ID)/"media"/"gaming_short_finale_share.mp4"
                                if _v1302_root.is_file():
                                    _v1302_video=_v1302_root.read_bytes()
                            except Exception:
                                _v1302_video=None

                        _v1302_results=[]
                        if _v1302_video:
                            for _v1302_platform in _v1302_targets:
                                _v1302_platform_name={
                                    "YouTube":"YouTube Shorts",
                                    "TikTok":"TikTok",
                                    "Instagram":"Instagram Reels",
                                }[_v1302_platform]
                                _v1302_pack=_gsf_finalize_publish_pack(
                                    _gsf_build_publish_pack(
                                        _v1302_start,
                                        platform=_v1302_platform_name,
                                        game=_v1302_game,
                                        tone=_v1302_tone,
                                    )
                                )
                                _v1302_tags=str(_v1302_hashtags or "").strip()
                                if _v1302_platform=="YouTube" and "#shorts" not in _v1302_tags.lower():
                                    _v1302_tags=(_v1302_tags+" #Shorts").strip()
                                elif _v1302_platform=="Instagram" and "#reels" not in _v1302_tags.lower():
                                    _v1302_tags=(_v1302_tags+" #Reels").strip()
                                _v1302_edited=_gsf_social_pack_for_upload(
                                    _v1302_pack,
                                    _v1302_title,
                                    _v1302_description,
                                    _v1302_tags,
                                )
                                _v1302_publish_video=(
                                    _gsf_v1302_youtube_short_bytes(_v1302_video)
                                    if _v1302_platform=="YouTube"
                                    else _v1302_video
                                )
                                with st.spinner("Pubblico su "+_v1302_platform+"…"):
                                    _ok,_msg,_path=_gsf_publish_social_upload(
                                        _v1302_publish_video,
                                        _v1302_platform,
                                        pack_override=_v1302_edited,
                                    )
                                if _ok:
                                    try:
                                        _gsf_v124_feedback(
                                            _gsf_v124_moment_for_start(_v1302_start),
                                            "published",
                                        )
                                    except Exception:
                                        pass
                                _v1302_results.append((_v1302_platform,_ok,_msg))
                            for _platform,_ok,_msg in _v1302_results:
                                if _ok:
                                    st.success(_platform+" · "+str(_msg or "Pubblicato"))
                                else:
                                    st.error(_platform+" · "+str(_msg or "Pubblicazione non riuscita"))
                        else:
                            st.error("Short finale non disponibile.")


with st.container(key="v1053_ad_footer"):
    st.markdown(_gsf_v1057_ad_markup(6), unsafe_allow_html=True)
st.empty()


# ============================================================
# V79 — PERSIST ANONYMOUS BETA WORKSPACE
# ============================================================
try:
    _gsf_save_persistent_state()
    _gsf_touch_session()
except Exception:
    pass


st.markdown("", unsafe_allow_html=True)





st.markdown("", unsafe_allow_html=True)

st.empty()


st.markdown("""
<style id="gsf-v1053-spacing">
/* A little breathing room between "Sottotitoli" and Nessuno/Automatici/Manuali. */
.st-key-editor_sub_mode_v18{
    margin-top:12px !important;
}
/* Social cards should not touch the Pubblicazione diretta heading. */
.st-key-v69_social_youtube,
.st-key-v69_social_tiktok,
.st-key-v69_social_instagram{
    margin-top:2px !important;
}
</style>
""",unsafe_allow_html=True)


st.markdown("", unsafe_allow_html=True)

_GSF_V1056_ADS_MODE=str(os.environ.get("GSF_ADS_MODE","off") or "off").strip().lower()
if _GSF_V1056_ADS_MODE not in {"preview","live","off"}:
    _GSF_V1056_ADS_MODE="off"

if _GSF_V1056_ADS_MODE=="off":
    st.markdown("", unsafe_allow_html=True)
else:
    st.markdown("", unsafe_allow_html=True)

    if _GSF_V1056_ADS_MODE=="live":
        st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.empty()

st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("""
<style id="gsf-v107-footer-compact">
/* Remove the redundant first footer link while preserving Privacy, Termini and Contatti. */
a[href*="social"]:not(.gsf-account-fab),
a[href*="connect"]:not(.gsf-account-fab){
  display:none !important;
}
/* Pull the legal/version/social footer into a single compact visual block. */
.v67-footer{
  margin:4px auto 2px !important;
  padding:2px 0 !important;
  text-align:center !important;
  font-size:.70rem !important;
  line-height:1.2 !important;
  color:#74899A !important;
}
.gsf-legal-footer{
  margin:2px auto 1px !important;
  padding:1px 0 !important;
  font-size:.70rem !important;
  line-height:1.15 !important;
}
.gsf-legal-footer a{font-weight:700 !important}
.gsf-social-footer{
  margin:1px auto 0 !important;
  padding:1px 6px 0 !important;
}
.gsf-social-footer-title{display:none !important}
.gsf-social-row{gap:6px !important}
.gsf-social-icon{
  width:26px !important;height:26px !important;flex-basis:26px !important;
  border-radius:8px !important;box-shadow:0 3px 8px rgba(74,110,142,.06) !important;
}
.gsf-social-icon svg{width:13px !important;height:13px !important}
@media(max-width:600px){
  .v67-footer{margin:3px auto 1px !important;font-size:.66rem !important}
  .gsf-legal-footer{margin:1px auto !important;font-size:.67rem !important}
  .gsf-social-footer{margin:0 auto !important;padding:0 4px !important}
  .gsf-social-row{gap:5px !important}
  .gsf-social-icon{width:24px !important;height:24px !important;flex-basis:24px !important;border-radius:7px !important}
  .gsf-social-icon svg{width:12px !important;height:12px !important}
  [data-testid="stAppViewContainer"] hr{
    margin-top:.24rem !important;
    margin-bottom:.24rem !important;
  }
  [data-testid="stAppViewContainer"] footer,
  [data-testid="stAppViewContainer"] footer > div{
    margin-top:0 !important;
    padding-top:0 !important;
    padding-bottom:0 !important;
  }
}
</style>
<script>
(()=>{
  const clean=()=>{
    document.querySelectorAll('a').forEach(a=>{
      const txt=(a.textContent||'').trim().toLowerCase();
      if(txt==='collega social') a.style.display='none';
      if(txt==='privacy'){
        /* Privacy is the first legal item: remove every leftover separator before it. */
        let n=a.previousSibling;
        while(n){
          const prev=n.previousSibling;
          const t=(n.textContent||'').trim();
          if(t==='' || t==='·' || t==='•' || t==='|' || t==='.' || t==='-') n.remove();
          else break;
          n=prev;
        }
        const parent=a.parentElement;
        if(parent){
          parent.childNodes.forEach(node=>{
            if(node===a)return;
            if(node.compareDocumentPosition && (node.compareDocumentPosition(a)&Node.DOCUMENT_POSITION_FOLLOWING)){
              const t=(node.textContent||'').trim();
              if(t==='·' || t==='•' || t==='|' || t==='.') node.remove();
            }
          });
        }
      }
    });
    /* Keep the version line compact: one line instead of two. */
    document.querySelectorAll('.v67-footer br').forEach(br=>{
      br.replaceWith(document.createTextNode(' · '));
    });
  };
  clean();
  new MutationObserver(clean).observe(document.body,{childList:true,subtree:true});
})();
</script>
""", unsafe_allow_html=True)

st.markdown("""
<style id="gsf-v107-footer-mobile-v2">
/* Footer: remove the large dead zones visible on phones. */
.gsf-social-footer{
  margin:2px auto 0 !important;
  padding:2px 8px 0 !important;
}
.gsf-social-footer-title{margin:4px 0 6px !important}
@media(max-width:600px){
  [data-testid="stAppViewContainer"] hr{margin:.28rem 0 !important}
  [data-testid="stAppViewContainer"] footer,
  [data-testid="stAppViewContainer"] footer > div{
    margin:0 !important;padding:0 !important;
  }
  .gsf-social-footer{margin:0 auto !important;padding:0 6px !important}
  .gsf-social-footer-title{margin:2px 0 4px !important}
  .gsf-social-footer-icons{gap:7px !important;margin:0 !important}
  .gsf-social-footer-icons a{width:46px !important;height:46px !important}
  /* Publication buttons: icons were washed out on the light mobile background. */
  [class*="st-key-"] button svg{opacity:1 !important}
  .gsf-publish-grid button,.gsf-social-publish button{
    color:#355a73 !important;
    font-weight:800 !important;
  }
  .gsf-publish-grid button svg,.gsf-social-publish button svg{
    stroke:#355a73 !important;fill:none !important;opacity:1 !important;
  }
}
</style>
<script>
(()=>{
 const enhance=()=>{
   const heading=[...document.querySelectorAll('div,p,h1,h2,h3,h4')].find(x=>(x.textContent||'').trim()==='Pubblicazione diretta');
   if(!heading)return;
   const root=heading.parentElement?.parentElement?.parentElement || heading.parentElement;
   if(root) root.classList.add('gsf-publish-grid');
   const buttons=root?[...root.querySelectorAll('button')]:[];
   const names=['YouTube','TikTok','Instagram'];
   buttons.forEach((b,i)=>{ if(i<3 && !(b.textContent||'').trim()) b.setAttribute('aria-label',names[i]); });
   /* Facebook is a visual destination placeholder until its publishing connector is implemented. */
   if(root && !root.querySelector('[data-gsf-facebook]')){
     const row=buttons[0]?.parentElement?.parentElement;
     if(row){
       const fb=document.createElement('div');
       fb.dataset.gsfFacebook='1';
       fb.title='Facebook';
       fb.setAttribute('aria-label','Facebook');
       fb.innerHTML='<div style="width:100%;height:100%;min-height:58px;border:1px solid #c9dbe8;border-radius:16px;display:flex;align-items:center;justify-content:center;font:900 26px Arial;color:#355a73;background:rgba(255,255,255,.58)">f</div>';
       row.insertBefore(fb,row.firstChild);
     }
   }
 };
 enhance(); new MutationObserver(enhance).observe(document.body,{childList:true,subtree:true});
})();
</script>
""", unsafe_allow_html=True)

st.markdown("""
<script>
(()=>{
 const clean=()=>{
   document.querySelectorAll('div,p,h1,h2,h3,h4').forEach(el=>{
     if((el.textContent||'').trim()==='Pubblicazione diretta'){
       const block=el.closest('[data-testid="stMarkdownContainer"]') || el;
       block.style.display='none';
       block.style.margin='0';
       block.style.padding='0';
     }
   });
 };
 clean(); new MutationObserver(clean).observe(document.body,{childList:true,subtree:true});
})();
</script>
""", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("""
<style id="gsf-layout-hygiene">
.st-key-gsf-major-create-ai,
.st-key-gsf-major-create-short,
[class*="st-key-gsf-major-game-editor_"],
.st-key-gsf-major-personalize{
  margin-top:10px !important;
  margin-bottom:10px !important;
}
[class*="st-key-gsf-major-game-editor_"]{
  margin-top:18px !important;
}
.gsf-major-note{
  margin:7px auto 13px !important;
}
.gsf-moment-head{
  margin:8px auto 13px !important;
}
.v67-ad{
  margin-top:12px !important;
  margin-bottom:12px !important;
}
.st-key-v1055_ad_manual_after_editor{
  margin-top:-24px !important;
}
[data-testid="stAppViewContainer"] hr{
  margin-top:.55rem !important;
  margin-bottom:.55rem !important;
}
@media(max-width:600px){
  .st-key-gsf-major-create-ai,
  .st-key-gsf-major-create-short,
  [class*="st-key-gsf-major-game-editor_"],
  .st-key-gsf-major-personalize{
    margin-top:8px !important;
    margin-bottom:8px !important;
  }
  [class*="st-key-gsf-major-game-editor_"]{margin-top:14px !important}
  .gsf-major-note{margin:6px auto 10px !important}
  .gsf-moment-head{margin:6px auto 10px !important}
  .v67-ad{margin-top:9px !important;margin-bottom:9px !important}
  .st-key-v1055_ad_manual_after_editor{margin-top:-52px !important}
  [data-testid="stAppViewContainer"] hr{margin:.38rem 0 !important}
}
</style>
<script>
(()=>{
 const slashN=String.fromCharCode(92)+'n';
 const isOnlyNewlineMarker=(value)=>{
   let t=String(value||'').replace(/\\s/g,'');
   if(!t || !t.includes(slashN)) return false;
   while(t.includes(slashN)) t=t.split(slashN).join('');
   return t==='';
 };
 const cleanArtifacts=()=>{
   /* Some legacy markers are not inside stMarkdownContainer.
      Remove the exact visible backslash-n text wherever Streamlit mounts it. */
   const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
   const doomed=[];
   let node;
   while((node=walker.nextNode())){
     const parent=node.parentElement;
     if(!parent || ['SCRIPT','STYLE','TEXTAREA','INPUT'].includes(parent.tagName)) continue;
     if(isOnlyNewlineMarker(node.nodeValue)) doomed.push(node);
   }
   doomed.forEach(node=>{
     const parent=node.parentElement;
     node.nodeValue='';
     const host=parent?.closest('[data-testid="stElementContainer"]')
       || parent?.closest('[data-testid="stMarkdownContainer"]')
       || parent;
     if(host && !(host.textContent||'').trim()){
       host.style.display='none';
       host.style.height='0';
       host.style.minHeight='0';
       host.style.margin='0';
       host.style.padding='0';
       host.style.overflow='hidden';
     }
   });
 };
 cleanArtifacts();
 new MutationObserver(cleanArtifacts).observe(document.body,{childList:true,subtree:true,characterData:true});
})();
</script>
""", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("""
<style id="gsf-footer-override-v4">
.v67-footer,.gsf-legal-footer,.gsf-social-footer{
  display:none !important;
  height:0 !important;
  min-height:0 !important;
  margin:0 !important;
  padding:0 !important;
  overflow:hidden !important;
}
.gsf-footer-v4{
  position:relative;
  width:min(720px,calc(100% - 20px));
  margin:4px auto 7px;
  padding:7px 8px 6px;
  border-top:1px solid rgba(195,214,227,.65);
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  gap:9px;
  color:#6d8496;
  text-align:center;
}
.gsf-footer-v4 .version{
  font-size:10px;
  line-height:1.1;
  font-weight:750;
}
.gsf-footer-v4 .legal{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:6px;
  font-size:10px;
  line-height:1.1;
}
.gsf-footer-v4 a{
  color:#647f92 !important;
  text-decoration:none !important;
  font-weight:750;
}
.gsf-footer-v4 .socials{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:8px;
}
.gsf-footer-v4 .social{
  width:30px;
  height:30px;
  border-radius:10px;
  border:1px solid rgba(192,213,227,.92);
  background:
    linear-gradient(145deg,rgba(255,255,255,.98),rgba(235,244,250,.94));
  display:grid;
  place-items:center;
  color:#5d778b !important;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.96),
    0 4px 10px rgba(65,96,121,.08);
  transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease,background .16s ease;
}
.gsf-footer-v4 .social:hover{
  transform:translateY(-2px);
  border-color:#b8d5e7;
  background:linear-gradient(145deg,#f9fdff,#e8f3fa);
  box-shadow:
    inset 0 1px 0 #fff,
    0 7px 14px rgba(65,96,121,.13);
}
.gsf-footer-v4 .social svg{
  width:15px;
  height:15px;
  display:block;
  fill:currentColor;
}
.gsf-footer-v4 .social.ig svg{width:16px;height:16px}
.gsf-footer-v4 .social.tw svg{width:16px;height:16px}
.gsf-footer-v4 .bug-report{
  position:absolute;
  right:8px;
  bottom:7px;
  font-size:9px;
  line-height:1;
  font-weight:800;
  letter-spacing:.015em;
  color:#6b8498 !important;
  opacity:.88;
}
.gsf-footer-v4 .bug-report:hover{opacity:1;color:#466b85 !important}
[data-testid="stAppViewContainer"] .block-container{padding-bottom:.55rem !important}
@media(max-width:600px){
  .gsf-footer-v4{
    margin:3px auto 5px;
    padding:6px 6px 5px;
    gap:7px;
  }
  .gsf-footer-v4 .version,
  .gsf-footer-v4 .legal{font-size:9px}
  .gsf-footer-v4 .socials{gap:7px}
  .gsf-footer-v4 .social{
    width:28px;
    height:28px;
    border-radius:9px;
  }
  .gsf-footer-v4 .social svg{width:14px;height:14px}
  .gsf-footer-v4 .social.ig svg,
  .gsf-footer-v4 .social.tw svg{width:15px;height:15px}
  .gsf-footer-v4 .bug-report{right:4px;bottom:5px;font-size:8px}
  [data-testid="stAppViewContainer"] .block-container{padding-bottom:.35rem !important}
}
</style>
<div class="gsf-footer-v4">
  <div class="version">Gaming Shorts Factory · Beta</div>
  <div class="legal">
    <a href="/privacy" target="_blank">Privacy</a>
    <span>·</span>
    <a href="/terms" target="_blank">Termini</a>
    <span>·</span>
    <a href="/contact" target="_blank">Contatti</a>
  </div>
  <div class="socials" aria-label="Social">
    <a class="social fb" href="https://www.facebook.com/profile.php?id=61595124112318&amp;locale=it_IT" target="_blank" rel="noopener noreferrer" aria-label="Facebook" title="Facebook">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.7 22v-9h3l.5-3.5h-3.5V7.3c0-1 .3-1.7 1.8-1.7h1.9V2.5c-.3 0-1.5-.1-2.8-.1-2.8 0-4.7 1.7-4.7 4.8v2.7H7v3.5h2.9v9h3.8z"/></svg>
    </a>
    <a class="social ig" href="https://www.instagram.com/gamingshortsfactory/" target="_blank" rel="noopener noreferrer" aria-label="Instagram" title="Instagram">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.4 2h9.2A5.4 5.4 0 0 1 22 7.4v9.2a5.4 5.4 0 0 1-5.4 5.4H7.4A5.4 5.4 0 0 1 2 16.6V7.4A5.4 5.4 0 0 1 7.4 2Zm0 2A3.4 3.4 0 0 0 4 7.4v9.2A3.4 3.4 0 0 0 7.4 20h9.2a3.4 3.4 0 0 0 3.4-3.4V7.4A3.4 3.4 0 0 0 16.6 4H7.4Zm9.6 1.5a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5ZM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"/></svg>
    </a>
    <a class="social yt" href="https://www.youtube.com/@Dans222nrg" target="_blank" rel="noopener noreferrer" aria-label="YouTube" title="YouTube">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M23 12s0-3.7-.5-5.4a3 3 0 0 0-2.1-2.1C18.7 4 12 4 12 4s-6.7 0-8.4.5a3 3 0 0 0-2.1 2.1C1 8.3 1 12 1 12s0 3.7.5 5.4a3 3 0 0 0 2.1 2.1C5.3 20 12 20 12 20s6.7 0 8.4-.5a3 3 0 0 0 2.1-2.1C23 15.7 23 12 23 12Zm-13.2 3.4V8.6l6 3.4-6 3.4Z"/></svg>
    </a>
    <a class="social tt" href="https://www.tiktok.com/@gamingshortsfactory" target="_blank" rel="noopener noreferrer" aria-label="TikTok" title="TikTok">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.6 2c.4 2.3 1.8 3.7 4.1 3.9v3.3a9.1 9.1 0 0 1-4.1-1v6.4a6.6 6.6 0 1 1-5.7-6.5v3.4a3.2 3.2 0 1 0 2.4 3.1V2h3.3Z"/></svg>
    </a>
    <a class="social tw" href="https://www.twitch.tv/dan222s86" target="_blank" rel="noopener noreferrer" aria-label="Twitch" title="Twitch">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.3 2 2 6.1v14h5.1V24l3.8-3.9h3.1L20 14V2H4.3Zm13.6 11-3.4 3.4H11l-2.9 2.9v-2.9H4V4.1h13.9V13ZM15.2 6.5h-2v5.2h2V6.5Zm-4.7 0h-2v5.2h2V6.5Z"/></svg>
    </a>
  </div>
  <a class="bug-report" href="mailto:danilo222barbieri@gmail.com?subject=Segnalazione%20bug%20Gaming%20Shorts%20Factory&body=Descrivi%20il%20bug%20e%20i%20passaggi%20per%20riprodurlo%3A%0A%0A" aria-label="Segnala bug">Segnala bug</a>
</div>
<script>
(()=>{
  const clean=()=>{
    const slashN=String.fromCharCode(92)+'n';
    document.querySelectorAll('[data-testid="stMarkdownContainer"]').forEach(el=>{
      const t=(el.textContent||'').replace(/\\s/g,'');
      if(t && t.split(slashN).join('')===''){
        const host=el.parentElement||el;
        host.style.display='none';
        host.style.height='0';
        host.style.minHeight='0';
        host.style.margin='0';
        host.style.padding='0';
        host.style.overflow='hidden';
      }
    });
  };
  clean();
  new MutationObserver(clean).observe(document.body,{childList:true,subtree:true});
})();
</script>
""", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("""
<style id="gsf-major-actions-final-override">
.st-key-gsf_share_download_top button,
[class*="st-key-gsf_share_download_top"] button,
.st-key-gsf-final-top-action-row button,
[class*="st-key-gsf-final-top-action-row"] button,
.st-key-gsf-major-create-ai button,
.st-key-gsf-major-personalize button,
[class*="st-key-gsf-major-personalize"] button,
[class*="st-key-gsf-major-create-ai"] button,
.st-key-gsf-major-personalize button,
[class*="st-key-gsf-major-personalize"] button,
[class*="st-key-gsf-major-game-editor_"] button,
.st-key-gsf-major-create-short button,
[class*="st-key-gsf-major-create-short"] button,
[class*="st-key-edit_ai_"] button,
.st-key-create_final_short_v54 button,
[class*="st-key-create_final_short_v54"] button,
.st-key-gsf_demo_social_publish_preview button,
[class*="st-key-gsf_demo_social_publish_preview"] button,
[class*="st-key-social_publish_confirm_"] button{
    width:100% !important;
    height:56px !important;
    min-height:56px !important;
    max-height:56px !important;
    padding:0 18px !important;
    border-radius:17px !important;
    border:1px solid rgba(255,255,255,.34) !important;
    background:linear-gradient(135deg,#8B67E8 0%,#6557D9 100%) !important;
    color:#FFFFFF !important;
    font-size:15px !important;
    font-weight:900 !important;
    line-height:1 !important;
    letter-spacing:.045em !important;
    box-shadow:0 12px 28px rgba(104,84,205,.28) !important;
}
.st-key-gsf_share_download_top button:hover,
[class*="st-key-gsf_share_download_top"] button:hover,
.st-key-gsf-final-top-action-row button:hover,
[class*="st-key-gsf-final-top-action-row"] button:hover,
.st-key-gsf-major-create-ai button:hover,
[class*="st-key-gsf-major-create-ai"] button:hover,
.st-key-gsf-major-personalize button:hover,
[class*="st-key-gsf-major-personalize"] button:hover,
[class*="st-key-gsf-major-game-editor_"] button:hover,
.st-key-gsf-major-create-short button:hover,
[class*="st-key-gsf-major-create-short"] button:hover,
[class*="st-key-edit_ai_"] button:hover,
.st-key-create_final_short_v54 button:hover,
[class*="st-key-create_final_short_v54"] button:hover,
.st-key-gsf_demo_social_publish_preview button:hover,
[class*="st-key-gsf_demo_social_publish_preview"] button:hover,
[class*="st-key-social_publish_confirm_"] button:hover{
    transform:translateY(-2px) !important;
    filter:brightness(1.035) !important;
    box-shadow:0 15px 34px rgba(104,84,205,.36) !important;
}
@media(max-width:750px){
    .st-key-gsf_share_download_top button,
    [class*="st-key-gsf_share_download_top"] button,
    .st-key-gsf-final-top-action-row button,
    [class*="st-key-gsf-final-top-action-row"] button,
    .st-key-gsf-major-create-ai button,
    .st-key-gsf-major-personalize button,
    [class*="st-key-gsf-major-personalize"] button,
    [class*="st-key-gsf-major-create-ai"] button,
    [class*="st-key-gsf-major-game-editor_"] button,
    .st-key-gsf-major-create-short button,
    [class*="st-key-gsf-major-create-short"] button,
    [class*="st-key-edit_ai_"] button,
    .st-key-create_final_short_v54 button,
    [class*="st-key-create_final_short_v54"] button,
    .st-key-gsf_demo_social_publish_preview button,
    [class*="st-key-gsf_demo_social_publish_preview"] button,
    [class*="st-key-social_publish_confirm_"] button{
        height:52px !important;
        min-height:52px !important;
        max-height:52px !important;
        font-size:13px !important;
    }
}

</style>
""", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("""
<style id="gsf-final-harmony-v107">
/* PUBBLICA: centered, same visual language and proportions as CREA CON IA. */
div[data-testid="stHorizontalBlock"]:has(.st-key-gsf_share_download_top){
  display:flex !important;
  width:100% !important;
  max-width:100% !important;
  margin:8px auto 14px !important;
  justify-content:center !important;
}
div[data-testid="stHorizontalBlock"]:has(.st-key-gsf_share_download_top) > div[data-testid="column"]{
  display:none !important;
}
div[data-testid="stHorizontalBlock"]:has(.st-key-gsf_share_download_top) > div[data-testid="column"]:has(.st-key-gsf_share_download_top){
  display:block !important;
  flex:1 1 100% !important;
  width:100% !important;
  max-width:100% !important;
}
.st-key-gsf_share_download_top,
[class*="st-key-gsf_share_download_top"]{
  width:100% !important;
  max-width:100% !important;
  margin:0 auto !important;
}
.st-key-gsf_share_download_top button,
[class*="st-key-gsf_share_download_top"] button{
  width:100% !important;
  height:56px !important;
  min-height:56px !important;
  max-height:56px !important;
  border-radius:17px !important;
  border:1px solid rgba(255,255,255,.34) !important;
  background:linear-gradient(135deg,#8B67E8 0%,#6557D9 100%) !important;
  color:#fff !important;
  font-family:var(--gsf-ui-font,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif) !important;
  font-size:15px !important;
  font-weight:900 !important;
  letter-spacing:.045em !important;
  box-shadow:0 12px 28px rgba(104,84,205,.28) !important;
}

/* Share destinations: smaller, lighter and aligned with the rest of GSF. */
div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_facebook){
  width:min(620px,100%) !important;
  max-width:620px !important;
  margin:0 auto 12px !important;
  padding:10px 12px !important;
  gap:10px !important;
  border:1px solid #D3E3ED !important;
  border-radius:20px !important;
  background:linear-gradient(145deg,#F8FCFF 0%,#EEF5FA 62%,#F3F1FA 100%) !important;
  box-shadow:0 10px 24px rgba(65,96,121,.10),inset 0 1px 0 rgba(255,255,255,.92) !important;
  -webkit-backdrop-filter:none !important;
  backdrop-filter:none !important;
  overflow:visible !important;
}
div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_facebook) > div[data-testid="column"]{
  min-width:0 !important;
  width:25% !important;
  flex:1 1 25% !important;
}
.st-key-v69_social_facebook button,
.st-key-v69_social_instagram button,
.st-key-v69_social_youtube button,
.st-key-v69_social_tiktok button{
  width:76px !important;
  max-width:76px !important;
  height:76px !important;
  min-height:76px !important;
  aspect-ratio:1 / 1 !important;
  border-radius:17px !important;
  padding:0 !important;
  margin:0 auto !important;
  border:0 !important;
  overflow:hidden !important;
  box-shadow:0 7px 17px rgba(42,69,88,.15),inset 0 1px 0 rgba(255,255,255,.20) !important;
  font-size:0 !important;
  color:transparent !important;
}
.st-key-v69_social_facebook button p,
.st-key-v69_social_instagram button p,
.st-key-v69_social_youtube button p,
.st-key-v69_social_tiktok button p{display:none !important}
.st-key-v69_social_facebook button:before,
.st-key-v69_social_instagram button:before,
.st-key-v69_social_youtube button:before,
.st-key-v69_social_tiktok button:before{
  content:"" !important;
  display:block !important;
  width:54% !important;
  height:54% !important;
  min-width:0 !important;
  min-height:0 !important;
  flex:0 0 auto !important;
  margin:0 !important;
  padding:0 !important;
  border-radius:0 !important;
  background-color:transparent !important;
  background-repeat:no-repeat !important;
  background-position:50% 50% !important;
  background-size:contain !important;
  box-shadow:none !important;
  text-shadow:none !important;
}
.st-key-v69_social_facebook button{background:#1877F2 !important}
.st-key-v69_social_facebook button:before{
  width:48% !important;
  height:48% !important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M13.25 21v-8h2.75l.42-3.12h-3.17V7.9c0-.9.25-1.52 1.58-1.52h1.7V3.58c-.3-.04-1.3-.13-2.47-.13-2.45 0-4.13 1.5-4.13 4.24v2.19H7.2V13h2.73v8h3.32Z'/%3E%3C/svg%3E") !important;
}
.st-key-v69_social_instagram button{
  background:radial-gradient(circle at 30% 105%,#FDF497 0 5%,#FD5949 35%,#D6249F 62%,#285AEB 100%) !important;
}
.st-key-v69_social_instagram button:before{
  width:55% !important;height:55% !important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect x='3.3' y='3.3' width='17.4' height='17.4' rx='5.1' fill='none' stroke='white' stroke-width='2.05'/%3E%3Ccircle cx='12' cy='12' r='4.15' fill='none' stroke='white' stroke-width='2.05'/%3E%3Ccircle cx='17.35' cy='6.75' r='1.15' fill='white'/%3E%3C/svg%3E") !important;
}
.st-key-v69_social_youtube button{background:#FF0000 !important}
.st-key-v69_social_youtube button:before{
  width:57% !important;height:57% !important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M9.2 7.5 16.7 12l-7.5 4.5v-9Z'/%3E%3C/svg%3E") !important;
}
.st-key-v69_social_tiktok button{background:#101010 !important}
.st-key-v69_social_tiktok button:before{
  width:52% !important;height:52% !important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M14.2 3v9.35a4.15 4.15 0 1 1-3.48-4.1v2.7a1.63 1.63 0 1 0 .82 1.4V3h2.66c.34 1.92 1.62 3.27 3.65 3.7v2.66a6.7 6.7 0 0 1-3.65-1.3V3Z'/%3E%3C/svg%3E") !important;
}
.st-key-v69_social_facebook button[kind="primary"],
.st-key-v69_social_instagram button[kind="primary"],
.st-key-v69_social_youtube button[kind="primary"],
.st-key-v69_social_tiktok button[kind="primary"],
.st-key-v69_social_facebook [data-testid="stBaseButton-primary"],
.st-key-v69_social_instagram [data-testid="stBaseButton-primary"],
.st-key-v69_social_youtube [data-testid="stBaseButton-primary"],
.st-key-v69_social_tiktok [data-testid="stBaseButton-primary"]{
  outline:2px solid rgba(101,87,217,.48) !important;
  outline-offset:3px !important;
}

/* Selected-social details: same light metallic card language as the rest of the app. */
[class*="st-key-v1055_social_composer_"]{
  width:min(760px,100%) !important;
  max-width:760px !important;
  margin:12px auto 14px !important;
  padding:15px 16px 14px !important;
  border:1px solid #D3E3ED !important;
  border-radius:20px !important;
  background:linear-gradient(145deg,#FBFDFF 0%,#EEF5FA 68%,#F4F1FA 100%) !important;
  box-shadow:0 10px 24px rgba(65,96,121,.09) !important;
  color:#2F526A !important;
  -webkit-backdrop-filter:none !important;
  backdrop-filter:none !important;
}
[class*="st-key-v1055_social_composer_"] .v1055-social-head,
[class*="st-key-v1055_social_composer_"] .v1055-social-head *{
  color:#2F526A !important;
}

/* Creator Hub: opaque, persistent and always reachable even during render/toasts. */
.gsf-account-fab{
  z-index:2147483150 !important;
  opacity:1 !important;
  visibility:visible !important;
  filter:none !important;
  pointer-events:auto !important;
}
.gsf-creator-hub-overlay.is-open{
  opacity:1 !important;
  visibility:visible !important;
  pointer-events:auto !important;
}
.gsf-creator-hub-backdrop{
  background:#EAF2F7 !important;
  -webkit-backdrop-filter:none !important;
  backdrop-filter:none !important;
}
.gsf-creator-hub-shell{
  opacity:1 !important;
  background:#F5FAFE !important;
  border-color:#D3E3ED !important;
  box-shadow:0 30px 86px rgba(19,45,65,.34) !important;
  isolation:isolate !important;
}
.gsf-creator-hub-head{
  background:#FFFFFF !important;
  opacity:1 !important;
}
.gsf-creator-hub-frame{
  background:#F5FAFE !important;
  opacity:1 !important;
}

/* Three AI preview players: larger footprint without breaking the 3-column grid. */
.st-key-v71-short-grid,
[class*="st-key-v71-short-grid"]{
  width:100% !important;
  max-width:100% !important;
}
[class*="st-key-v71_short_card_"]{
  padding:4px 4px 8px !important;
}
[class*="st-key-v71_short_card_"] [data-testid="stVideo"]{
  width:100% !important;
  max-width:100% !important;
}
[class*="st-key-v71_short_card_"] video{
  width:100% !important;
  max-width:100% !important;
  min-height:220px !important;
  max-height:300px !important;
  object-fit:contain !important;
  border-radius:15px !important;
  background:#1E2C42 !important;
}
@media(max-width:900px){
  [class*="st-key-v71_short_card_"] video{
    min-height:190px !important;
    max-height:260px !important;
  }
}
@media(max-width:600px){
  .st-key-gsf_share_download_top button,
  [class*="st-key-gsf_share_download_top"] button{
    height:52px !important;
    min-height:52px !important;
    max-height:52px !important;
    font-size:13px !important;
  }
  div[data-testid="stHorizontalBlock"]:has(.st-key-v69_social_facebook){
    width:min(340px,100%) !important;
    max-width:340px !important;
    padding:9px !important;
    gap:7px !important;
    border-radius:18px !important;
  }
  .st-key-v69_social_facebook button,
  .st-key-v69_social_instagram button,
  .st-key-v69_social_youtube button,
  .st-key-v69_social_tiktok button{
    width:64px !important;
    max-width:64px !important;
    height:64px !important;
    min-height:64px !important;
    border-radius:15px !important;
  }
  [class*="st-key-v1055_social_composer_"]{
    padding:12px !important;
    border-radius:18px !important;
  }
  [class*="st-key-v71_short_card_"] video{
    min-height:210px !important;
    max-height:300px !important;
  }
}
</style>
<script>
(()=>{
  const KEY='gsf_creator_hub_open_v107';
  let raf=0;
  const bind=()=>{
    const panel=document.getElementById('gsf-creator-hub-panel');
    const fab=document.querySelector('.gsf-account-fab');
    if(!panel||!fab)return;

    if(fab.dataset.gsfPersistBound!=='1'){
      fab.dataset.gsfPersistBound='1';
      fab.addEventListener('click',()=>{
        try{sessionStorage.setItem(KEY,'1')}catch(e){}
        panel.classList.add('is-open');
      });
    }

    panel.querySelectorAll('.gsf-creator-hub-backdrop,.gsf-creator-hub-close').forEach(el=>{
      if(el.dataset.gsfPersistBound==='1')return;
      el.dataset.gsfPersistBound='1';
      el.addEventListener('click',()=>{
        try{sessionStorage.setItem(KEY,'0')}catch(e){}
        panel.classList.remove('is-open');
      });
    });

    let keep=false;
    try{keep=sessionStorage.getItem(KEY)==='1'}catch(e){}
    if(location.hash==='#gsf-creator-hub-panel') keep=true;
    panel.classList.toggle('is-open',keep);
  };
  const schedule=()=>{
    if(raf)return;
    raf=requestAnimationFrame(()=>{raf=0;bind()});
  };
  bind();
  new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});
  window.addEventListener('hashchange',schedule);
})();
</script>
""", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)

st.markdown("""
<style id="gsf-final-social-metallic-v107">
.st-key-v69_social_facebook button,
.st-key-v69_social_instagram button,
.st-key-v69_social_youtube button,
.st-key-v69_social_tiktok button,
.st-key-v69_social_facebook button[kind="primary"],
.st-key-v69_social_instagram button[kind="primary"],
.st-key-v69_social_youtube button[kind="primary"],
.st-key-v69_social_tiktok button[kind="primary"],
.st-key-v69_social_facebook button[kind="secondary"],
.st-key-v69_social_instagram button[kind="secondary"],
.st-key-v69_social_youtube button[kind="secondary"],
.st-key-v69_social_tiktok button[kind="secondary"]{
  background:linear-gradient(145deg,#FFFFFF 0%,#F5F9FC 32%,#EAF2F7 68%,#F1EEF8 100%) !important;
  border:1px solid #C9DBE7 !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.98),inset 0 -1px 0 rgba(157,181,197,.20),0 8px 20px rgba(65,96,121,.12) !important;
  opacity:1 !important;
  filter:none !important;
}
.st-key-v69_social_facebook button:hover,
.st-key-v69_social_instagram button:hover,
.st-key-v69_social_youtube button:hover,
.st-key-v69_social_tiktok button:hover{
  background:linear-gradient(145deg,#FFFFFF 0%,#EEF6FB 42%,#E5EFF5 70%,#EEEAF7 100%) !important;
  border-color:#B9D0DE !important;
  transform:translateY(-1px) !important;
}
.st-key-v69_social_facebook button:before,
.st-key-v69_social_instagram button:before,
.st-key-v69_social_youtube button:before,
.st-key-v69_social_tiktok button:before{
  width:52% !important;
  height:52% !important;
  background-color:transparent !important;
  background-repeat:no-repeat !important;
  background-position:center !important;
  background-size:contain !important;
  border:0 !important;
  border-radius:0 !important;
  box-shadow:none !important;
  filter:drop-shadow(0 1px 0 rgba(255,255,255,.96)) drop-shadow(0 2px 3px rgba(59,88,109,.18)) !important;
  opacity:1 !important;
}
.st-key-v69_social_facebook button:before{
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%235D778B' d='M13.25 21v-8h2.75l.42-3.12h-3.17V7.9c0-.9.25-1.52 1.58-1.52h1.7V3.58c-.3-.04-1.3-.13-2.47-.13-2.45 0-4.13 1.5-4.13 4.24v2.19H7.2V13h2.73v8h3.32Z'/%3E%3C/svg%3E") !important;
}
.st-key-v69_social_instagram button:before{
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect x='3.3' y='3.3' width='17.4' height='17.4' rx='5.1' fill='none' stroke='%235D778B' stroke-width='2.05'/%3E%3Ccircle cx='12' cy='12' r='4.15' fill='none' stroke='%235D778B' stroke-width='2.05'/%3E%3Ccircle cx='17.35' cy='6.75' r='1.15' fill='%235D778B'/%3E%3C/svg%3E") !important;
}
.st-key-v69_social_youtube button:before{
  width:56% !important;
  height:56% !important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%235D778B' d='M21.3 7.1a2.8 2.8 0 0 0-2-2C17.7 4.7 12 4.7 12 4.7s-5.7 0-7.3.4a2.8 2.8 0 0 0-2 2C2.3 8.7 2.3 12 2.3 12s0 3.3.4 4.9a2.8 2.8 0 0 0 2 2c1.6.4 7.3.4 7.3.4s5.7 0 7.3-.4a2.8 2.8 0 0 0 2-2c.4-1.6.4-4.9.4-4.9s0-3.3-.4-4.9ZM10.1 15.8V8.2l6.3 3.8-6.3 3.8Z'/%3E%3C/svg%3E") !important;
}
.st-key-v69_social_tiktok button:before{
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%235D778B' d='M15.6 2c.4 2.3 1.8 3.7 4.1 3.9v3.3a9.1 9.1 0 0 1-4.1-1v6.4a6.6 6.6 0 1 1-5.7-6.5v3.4a3.2 3.2 0 1 0 2.4 3.1V2h3.3Z'/%3E%3C/svg%3E") !important;
}
.st-key-v69_social_facebook button[kind="primary"],
.st-key-v69_social_instagram button[kind="primary"],
.st-key-v69_social_youtube button[kind="primary"],
.st-key-v69_social_tiktok button[kind="primary"],
.st-key-v69_social_facebook [data-testid="stBaseButton-primary"],
.st-key-v69_social_instagram [data-testid="stBaseButton-primary"],
.st-key-v69_social_youtube [data-testid="stBaseButton-primary"],
.st-key-v69_social_tiktok [data-testid="stBaseButton-primary"]{
  outline:2px solid rgba(126,155,177,.62) !important;
  outline-offset:3px !important;
}
</style>
<!-- GSFNavigation owns Creator Hub; obsolete React-node portal retired. -->
""", unsafe_allow_html=True)

# ===== V110 CREATOR HUB SOLID LOCK =====
st.markdown("", unsafe_allow_html=True)
# ===== /V110 CREATOR HUB SOLID LOCK =====

# ===== V111 FINAL READY SYNC =====
st.markdown("", unsafe_allow_html=True)
try:
    st.session_state.pop("gsf_final_ready_sync_v111",None)
except Exception:
    pass
st.button("SYNC SHORT READY",key="gsf_final_ready_sync_v111")
# ===== /V111 FINAL READY SYNC =====

# ===== V113 GSF GUARDIAN =====
GSF_V113_GUARDIAN=True
# Operational self-healing runs in direct_upload_server.py.
# ===== /V113 GSF GUARDIAN =====

# ===== V124 AI QUALITY UI =====
try:
    _v124_ready=bool(
        st.session_state.get("publication_ready",False)
        or st.session_state.get("publication_final_bytes")
    )
except Exception:
    _v124_ready=False

if _v124_ready and GSF_WEB_MODE:
    try:
        _v124_u=__import__("urllib.request",fromlist=["Request","urlopen"])
        _v124_req=_v124_u.Request(
            "http://127.0.0.1:8502/quality/status",
            headers={"X-GSF-Session-ID":str(GSF_SESSION_ID)},
            method="GET",
        )
        _v124_raw=_v124_u.urlopen(_v124_req,timeout=2.0).read()
        _v124_payload=__import__("json").loads(_v124_raw.decode("utf-8"))
        _v124_quality=(_v124_payload or {}).get("quality") or {}
    except Exception:
        _v124_quality={}

    if isinstance(_v124_quality,dict) and _v124_quality:
        _v124_status=str(_v124_quality.get("status") or "")
        _v124_score=_v124_quality.get("score")
        _v124_issues=list(_v124_quality.get("issues") or [])
        _v124_warnings=list(_v124_quality.get("warnings") or [])
        if _v124_status=="analyzing":
            st.markdown(
                '<div class="gsf-v124-quality"><b>AI QUALITY CHECK</b>'
                '<span>Analisi finale in corso…</span></div>',
                unsafe_allow_html=True,
            )
        elif _v124_status in ("pass","warn","fail"):
            _v124_icon="✓" if _v124_status=="pass" else ("!" if _v124_status=="warn" else "×")
            _v124_detail=[]
            if _v124_issues:
                _v124_detail.append("Problemi: "+", ".join(str(x).replace("_"," ") for x in _v124_issues[:3]))
            if _v124_warnings:
                _v124_detail.append("Avvisi: "+", ".join(str(x).replace("_"," ") for x in _v124_warnings[:3]))
            _v124_detail_text=" · ".join(_v124_detail) if _v124_detail else "Video pronto per la pubblicazione."
            st.markdown(
                '<div class="gsf-v124-quality gsf-v124-quality-'+_v124_status+'">'
                '<b>AI QUALITY CHECK</b>'
                '<span class="gsf-v124-score">'+_v124_icon+' '+str(_v124_score if _v124_score is not None else "—")+'/100</span>'
                '<small>'+html.escape(_v124_detail_text)+'</small>'
                '</div>',
                unsafe_allow_html=True,
            )

st.markdown("", unsafe_allow_html=True)
# ===== /V124 AI QUALITY UI =====

st.markdown("", unsafe_allow_html=True)

# ===== V125 AI THUMBNAIL PREVIEW =====
try:
    _v125_thumb_ready=bool(
        st.session_state.get("publication_ready",False)
        or st.session_state.get("publication_final_bytes")
    )
    if _v125_thumb_ready:
        _v125_runtime_root=Path(__import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime"))
        _v125_thumb_path=_v125_runtime_root/"sessions"/str(GSF_SESSION_ID)/"media"/"ai_thumbnail_v125.jpg"
        if _v125_thumb_path.is_file() and _v125_thumb_path.stat().st_size>512:
            with st.container(key="gsf-v125-ai-thumbnail"):
                st.markdown(
                    '<div class="gsf-v125-thumb-title"><b>THUMBNAIL AI</b>'
                    '<span>Frame scelto sul momento chiave dal Director.</span></div>',
                    unsafe_allow_html=True,
                )
                st.image(str(_v125_thumb_path),width=270)
except Exception:
    pass

st.markdown("", unsafe_allow_html=True)
# ===== /V125 AI THUMBNAIL PREVIEW =====

st.markdown("", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)


st.markdown("", unsafe_allow_html=True)


# V153 Living tail override
_gsf_render_living_tail()
# V157: persist lightweight project/UI state at the end of every successful rerun.
# Video/render payloads stay on disk and are referenced by path, never serialized here.
if 'GSF_WEB_MODE' in globals() and GSF_WEB_MODE:
    try:
        from web.project_state_v157 import save_project as _gsf_save_project_v157
        _gsf_save_project_v157(st.session_state, GSF_SESSION_ROOT)
    except Exception:
        pass

if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v158-shell-bridge">
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-overlay{
      background:transparent !important;
      transition:opacity .22s ease,visibility .22s ease !important;
    }
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-backdrop{
      background:rgba(219,235,244,.52) !important;
      -webkit-backdrop-filter:blur(4px) saturate(.96) !important;
      backdrop-filter:blur(4px) saturate(.96) !important;
      transition:opacity .22s ease !important;
    }
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-shell{
      width:min(1920px,calc(100vw - 20px)) !important;
      height:calc(100dvh - 20px) !important;
      border-radius:30px !important;
      background:#F7FBFF !important;
      transform:scale(.985) !important;
      transition:transform .26s cubic-bezier(.2,.8,.2,1),opacity .22s ease !important;
      opacity:0 !important;
      overflow:hidden !important;
    }
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-overlay.is-open .gsf-creator-hub-shell,
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-overlay:target .gsf-creator-hub-shell{
      transform:scale(1) !important;
      opacity:1 !important;
    }
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-head{display:none !important}
    #gsf-creator-hub-portal-v107 .gsf-creator-hub-frame{
      width:100% !important;height:100% !important;background:#F7FBFF !important;
    }
    @media(max-width:760px){
      #gsf-creator-hub-portal-v107 .gsf-creator-hub-shell{
        width:calc(100vw - 10px) !important;height:calc(100vh - 10px) !important;border-radius:22px !important;
      }
    }
    </style>
    <!-- V158 router retired; GSFNavigation owns all destinations. -->
    """, unsafe_allow_html=True)

_GSF_SURFACE_SOCIAL = r"""<div id="gsf-social-overlay-v159" aria-hidden="true">
      <section class="gsf-social-shell" role="dialog" aria-modal="false" aria-label="Condividi o scarica">
        <button class="gsf-social-close" type="button" aria-label="Chiudi">×</button>
        <iframe src="about:blank" data-src="/share-v156/" data-loaded="0" title="Condividi o scarica"></iframe>
      </section>
    </div>"""

if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v159-social-shell">
    #gsf-social-overlay-v159{
      position:fixed;
      left:0;right:0;top:0;bottom:78px;
      z-index:2147483650;
      display:flex;align-items:center;justify-content:center;
      padding:34px clamp(16px,3vw,46px) 14px;
      background:rgba(222,238,247,.48);
      -webkit-backdrop-filter:blur(5px) saturate(.98);
      backdrop-filter:blur(5px) saturate(.98);
      opacity:0;visibility:hidden;pointer-events:none;
      transition:opacity .24s ease,visibility .24s ease;
    }
    #gsf-social-overlay-v159.is-open{opacity:1;visibility:visible;pointer-events:auto}
    #gsf-social-overlay-v159 .gsf-social-shell{
      position:relative;
      width:min(1180px,calc(100vw - 34px));
      height:min(690px,calc(100dvh - 132px));
      border:1px solid rgba(159,193,218,.34);
      border-radius:30px;
      overflow:hidden;
      background:#050D16;
      box-shadow:0 30px 86px rgba(19,45,65,.22),inset 0 1px 0 rgba(255,255,255,.92);
      transform:translateY(10px) scale(.975);
      opacity:0;
      transition:transform .32s cubic-bezier(.16,.84,.24,1),opacity .24s ease;
    }
    #gsf-social-overlay-v159.is-open .gsf-social-shell{transform:translateY(0) scale(1);opacity:1}
    #gsf-social-overlay-v159 iframe{width:100%;height:100%;border:0;background:#050D16}
    #gsf-social-overlay-v159 .gsf-social-close{
      position:absolute;z-index:5;right:13px;top:12px;width:34px;height:34px;
      border:1px solid rgba(158,190,216,.34);border-radius:12px;
      background:rgba(255,255,255,.94);color:#617B9D;font-size:20px;cursor:pointer;
      box-shadow:0 7px 18px rgba(64,104,143,.09)
    }
    @media(max-width:760px){
      #gsf-social-overlay-v159{
        bottom:70px;
        padding:12px 6px 8px;
        align-items:flex-start;
        background:rgba(225,240,248,.44);
      }
      #gsf-social-overlay-v159 .gsf-social-shell{
        width:calc(100vw - 12px);
        height:calc(100dvh - 92px);
        border-radius:22px;
      }
      #gsf-social-overlay-v159 .gsf-social-close{right:9px;top:8px;width:31px;height:31px}
    }
    </style>
        <!-- gsf-social-overlay-v159: mounted once by the parent app. -->
    <div class="gsf-script-guard" style="display:none!important"></div>

    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    _GSF_PARENT_SOCIAL = r"""<!doctype html><html><body style="margin:0;display:none">
    <script>
    ((P)=>{
      const window=P;
      const document=P.document;
      const location=P.location;
    (()=>{
      const o=document.getElementById('gsf-social-overlay-v159');
      if(!o)return;
      const bridge=P.GSFNavigation.bridge('social',globalThis.frameElement);
      const frame=o.querySelector('iframe');
      const ensureFrame=()=>{
        if(frame.dataset.loaded==='1')return;
        frame.contentWindow.location.replace(frame.dataset.src||'/share-v156/');
        frame.dataset.loaded='1';
      };
      const open=(platform='')=>{
        ensureFrame();
        o.classList.add('is-open');
        o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';
        o.setAttribute('aria-hidden','false');
        if(platform)setTimeout(()=>{try{frame.contentWindow.postMessage({type:'GSF_SHARE_FOCUS',platform},location.origin)}catch(e){}},90);
      };
      const close=()=>{
        o.classList.remove('is-open');
        o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';
        o.setAttribute('aria-hidden','true');
      };
      o.querySelector('.gsf-social-close').onclick=()=>P.GSFNavigation.navigate({target:'home'});
      o.addEventListener('click',e=>{if(e.target===o)P.GSFNavigation.navigate({target:'home'})},{signal:bridge.signal});

      // Old Streamlit share controls route into the same app layer instead of causing a page change/rerun.
      document.addEventListener('click',e=>{
        const target=e.target&&e.target.closest?e.target.closest('button,a,[role=button]'):null;
        if(!target||target.closest('#gsf-social-overlay-v159'))return;
        const label=(target.innerText||target.textContent||'').trim().toLowerCase();
        if(label.includes('condividi o scarica')||label.includes('apri share hub')){
          e.preventDefault();e.stopPropagation();P.GSFNavigation.navigate({target:'social'});
        }
      },{capture:true,signal:bridge.signal});

      // Crea Short: the canonical page starts the render when no final Short exists yet.
      let lastShortRequest=0;
      const notice=text=>{try{frame.contentWindow.postMessage({type:'GSF_SHARE_NOTICE',text:String(text||'')},location.origin)}catch(e){}};
      const startShortIfNeeded=async requestedAt=>{
        if(!requestedAt||requestedAt===lastShortRequest)return;
        lastShortRequest=requestedAt;
        const routeEpoch=P.GSFNavigation.snapshot().epoch;
        const active=()=>!bridge.signal.aborted&&lastShortRequest===requestedAt&&P.GSFNavigation.snapshot().target==='social'&&P.GSFNavigation.snapshot().epoch===routeEpoch;
        try{const r=await P.fetch('/share/state',{cache:'no-store',credentials:'same-origin'});const j=await r.json();if(r.ok&&j&&j.ready)return}catch(e){}
        const renderButton=()=>document.querySelector('.st-key-gsf-major-create-short button,.st-key-create_final_short_v54 button')||[...document.querySelectorAll('button,[role="button"]')].find(x=>{if(x.closest('#gsf-social-overlay-v159,#gsf-global-gamebar,#gsf-global-header'))return false;const t=String(x.innerText||x.textContent||'').trim().toLowerCase();return t==='crea short'||t.includes('crea short finale')||t.includes('crea il tuo short')});
        let b=renderButton();
        if(!b){
          // An edit can invalidate an already completed export without a
          // Streamlit event. Reuse its existing sync widget to mount render.
          const sync=document.querySelector('.st-key-gsf_final_ready_sync_v111 button');
          if(sync&&!sync.disabled)sync.click();
        }
        const deadline=Date.now()+15000;
        // Preparing the manual recipe and mounting its widget complete on a
        // Streamlit rerun. Wait for that existing button; leaving cancels it.
        while(!b&&active()&&Date.now()<deadline){await new Promise(resolve=>setTimeout(resolve,100));b=renderButton();}
        if(!active())return;
        if(!b){setTimeout(()=>notice('Carica un gameplay prima di creare lo Short.'),400);return}
        if(b.disabled||b.getAttribute('aria-disabled')==='true'){setTimeout(()=>notice('Il gameplay non è ancora pronto per il render.'),400);return}
        b.click();setTimeout(()=>notice('Creazione Short avviata…'),400);
      };
      P.GSFNavigation.registerSurface('social',{open:data=>{open(String(data.platform||''));if(data.createShort)startShortIfNeeded(Number(data.requestedAt)||0)},close});
    })();

    })(window.parent);
    </script>
    </body></html>"""

_GSF_SURFACE_HUB = r"""<div id="gsf-creator-hub-live-v160" aria-hidden="true">
      <section class="gsf-hub-shell-v160" role="dialog" aria-modal="false" aria-label="Creator Hub">
        <button class="gsf-hub-close-v160" type="button" aria-label="Chiudi">×</button>
        <iframe src="about:blank" data-src="/creator-hub-v156/" data-loaded="0" title="Creator Hub"></iframe>
      </section>
    </div>
<style id="gsf-v160-hub-shell">
    #gsf-creator-hub-live-v160{
      position:fixed;left:0;right:0;top:0;bottom:78px;
      z-index:2147483660;display:flex;align-items:center;justify-content:center;
      padding:24px clamp(14px,2.5vw,38px) 12px;
      background:rgba(222,238,247,.46);
      -webkit-backdrop-filter:blur(5px) saturate(.98);
      backdrop-filter:blur(5px) saturate(.98);
      opacity:0;visibility:hidden;pointer-events:none;
      transition:opacity .24s ease,visibility .24s ease
    }
    #gsf-creator-hub-live-v160.is-open{opacity:1;visibility:visible;pointer-events:auto}
    #gsf-creator-hub-live-v160 .gsf-hub-shell-v160{
      position:relative;width:min(1220px,calc(100vw - 30px));height:min(720px,calc(100dvh - 118px));
      border:1px solid rgba(157,193,219,.35);border-radius:30px;overflow:hidden;background:#050D16;
      box-shadow:0 30px 86px rgba(19,45,65,.22),inset 0 1px 0 rgba(255,255,255,.94);
      transform:scale(.985);opacity:0;
      transition:transform .30s cubic-bezier(.16,.84,.24,1),opacity .24s ease
    }
    #gsf-creator-hub-live-v160.is-open .gsf-hub-shell-v160{transform:scale(1);opacity:1}
    #gsf-creator-hub-live-v160 iframe{width:100%;height:100%;border:0;background:#050D16}
    #gsf-creator-hub-live-v160 .gsf-hub-close-v160{
      position:absolute;z-index:7;right:13px;top:11px;width:34px;height:34px;
      border:1px solid rgba(158,190,216,.34);border-radius:12px;background:rgba(255,255,255,.94);
      color:#617B9D;font-size:20px;cursor:pointer;box-shadow:0 7px 18px rgba(64,104,143,.09)
    }
    @media(max-width:760px){
      #gsf-creator-hub-live-v160{bottom:70px;padding:8px 5px}
      #gsf-creator-hub-live-v160 .gsf-hub-shell-v160{
        width:calc(100vw - 10px);height:calc(100dvh - 84px);border-radius:22px
      }
      #gsf-creator-hub-live-v160 .gsf-hub-close-v160{right:8px;top:7px;width:31px;height:31px}
    }
    </style>
"""

if GSF_WEB_MODE:
    st.markdown(r"""

        <!-- gsf-creator-hub-live-v160: mounted once by the parent app. -->
    <div class="gsf-script-guard" style="display:none!important"></div>

    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html('<!-- Surface navigation is owned by GSFNavigation. -->', height=0, scrolling=False)

_GSF_SURFACE_EDITOR = r"""<div id="gsf-editor-overlay-v220" aria-hidden="true">
  <section class="gsf-editor-shell" role="dialog" aria-modal="false" aria-label="Game Editor">
    <button class="gsf-editor-close" type="button" aria-label="Chiudi">×</button>
    <div class="gsf-editor-head"><div>Game Editor<small>Il tuo gameplay resta nel progetto mentre modifichi.</small></div><button class="v326HeaderFull" type="button" aria-label="Schermo intero"><span>↗</span> FULL</button></div>
    <div class="gsf-editor-body">
      <div class="editor-note left"><span id="gsf-editor-note-left">Qui modelli<br>la tua giocata</span></div>
      <iframe class="gsf-editor-frame" src="about:blank" data-src="/editor-live/" data-loaded="0" title="Game Editor"></iframe>
      <div class="editor-note right"><span id="gsf-editor-note-right">Tocca uno strumento<br>e guarda cosa cambia</span></div>
    </div>
  </section>
</div>
<!-- Persistent Editor shell styles: mounted with the surface before React. -->
<style id="v326EditorHeaderFullStyle">
@media(max-width:760px){#gsf-editor-overlay-v220 .gsf-editor-head{padding-right:106px!important}#gsf-editor-overlay-v220 .v326HeaderFull{position:absolute;right:48px;top:7px;height:34px;min-width:66px;padding:0 10px;border-radius:13px;border:1px solid rgba(158,190,216,.30);background:rgba(255,255,255,.92);color:#48688d;font-size:10px;font-weight:950;letter-spacing:.035em;box-shadow:0 6px 16px rgba(64,104,143,.08)}}
</style>
<style id="v389EditorParentBounded">@media(max-width:760px){#gsf-editor-overlay-v220.is-open{overflow:hidden!important}#gsf-editor-overlay-v220 .gsf-editor-head{display:none!important}#gsf-editor-overlay-v220 iframe.gsf-editor-frame,#gsf-editor-overlay-v220 iframe[title="Game Editor"]{display:block!important;flex:1 1 auto!important;width:100%!important;height:100%!important;min-height:0!important;max-height:none!important;border:0!important;background:transparent!important;transform:translateZ(0)!important;transition:none!important;animation:none!important}}</style>
<style id="v392EditorParentPremium">@media(max-width:760px){#gsf-editor-overlay-v220 .v392EditorCloseGone{display:none!important}}</style>
<style id="v393EditorShellCleanup">
@media(max-width:760px){
  #gsf-editor-overlay-v220.is-open{overflow:hidden!important;background:#050D16!important}
  #gsf-editor-overlay-v220.is-open [class*="close" i],
  #gsf-editor-overlay-v220.is-open [id*="close" i],
  .v393EditorChromeGone{display:none!important}
}
</style>
<style id="gsf-v220-editor-shell">
    #gsf-editor-overlay-v220{position:fixed;left:0;right:0;top:0;bottom:78px;z-index:2147483655;display:flex;align-items:center;justify-content:center;padding:24px clamp(14px,2.5vw,38px) 12px;background:rgba(222,238,247,.46);-webkit-backdrop-filter:blur(5px) saturate(.98);backdrop-filter:blur(5px) saturate(.98);opacity:0;visibility:hidden;pointer-events:none;transition:opacity .24s ease,visibility .24s ease}
    #gsf-editor-overlay-v220.is-open{opacity:1;visibility:visible;pointer-events:auto}
    #gsf-editor-overlay-v220 .gsf-editor-shell{position:relative;width:min(1260px,calc(100vw - 30px));height:min(760px,calc(100dvh - 118px));border:1px solid rgba(157,193,219,.35);border-radius:30px;overflow:hidden;background:radial-gradient(circle at 8% 6%,rgba(126,214,255,.20),transparent 25%),radial-gradient(circle at 92% 7%,rgba(127,236,197,.18),transparent 26%),linear-gradient(180deg,#FCFEFF,#F6FBFF);box-shadow:0 30px 86px rgba(19,45,65,.22),inset 0 1px 0 rgba(255,255,255,.94);transform:translateY(10px) scale(.975);opacity:0;transition:transform .32s cubic-bezier(.16,.84,.24,1),opacity .24s ease}
    #gsf-editor-overlay-v220.is-open .gsf-editor-shell{transform:translateY(0) scale(1);opacity:1}
    #gsf-editor-overlay-v220 .gsf-editor-head{height:54px;display:flex;align-items:center;justify-content:space-between;padding:0 54px 0 20px;border-bottom:1px solid rgba(148,183,213,.20);color:#0D2A66;font-size:14px;font-weight:900}
    #gsf-editor-overlay-v220 .gsf-editor-head small{display:block;color:#7185A6;font-size:9px;font-weight:700;margin-top:2px}
    #gsf-editor-overlay-v220 .gsf-editor-close{position:absolute;z-index:6;right:13px;top:10px;width:34px;height:34px;border-radius:12px;border:1px solid rgba(158,190,216,.34);background:rgba(255,255,255,.94);color:#617B9D;font-size:20px;cursor:pointer;box-shadow:0 7px 18px rgba(64,104,143,.09)}
    #gsf-editor-overlay-v220 .gsf-editor-body{position:absolute;left:0;right:0;top:54px;bottom:0;display:grid;grid-template-columns:180px 1fr 180px;align-items:center}
    #gsf-editor-overlay-v220 .gsf-editor-frame{width:100%;height:100%;border:0;background:transparent}
    #gsf-editor-overlay-v220 .editor-note{color:#637DA8;font-family:"Segoe Print","Bradley Hand","Comic Sans MS",cursive;font-size:16px;font-weight:600;line-height:1.08;text-align:center;padding:14px;pointer-events:none}
    #gsf-editor-overlay-v220 .editor-note.left{transform:rotate(-4deg)}
    #gsf-editor-overlay-v220 .editor-note.right{transform:rotate(4deg)}
    #gsf-editor-overlay-v220 .editor-note span{display:block;transition:opacity .42s ease,filter .42s ease,transform .42s ease}
    #gsf-editor-overlay-v220 .editor-note span.out{opacity:0;filter:blur(7px);transform:translateY(-8px) scale(.93)}
    @keyframes gsfEditorWrite{0%{opacity:0;filter:blur(8px);transform:translateY(10px) scale(.91)}70%{opacity:1;filter:blur(.5px);transform:translateY(-2px) scale(1.02)}100%{opacity:1;filter:none;transform:none}}
    #gsf-editor-overlay-v220 .editor-note span.in{animation:gsfEditorWrite 1.05s cubic-bezier(.18,.72,.2,1) 1}
    @media(max-width:900px){#gsf-editor-overlay-v220{bottom:70px;padding:8px 5px}#gsf-editor-overlay-v220 .gsf-editor-shell{width:calc(100vw - 10px);height:calc(100dvh - 84px);border-radius:22px}#gsf-editor-overlay-v220 .gsf-editor-body{grid-template-columns:1fr;top:48px}#gsf-editor-overlay-v220 .editor-note{display:none}#gsf-editor-overlay-v220 .gsf-editor-head{height:48px;padding-left:14px}#gsf-editor-overlay-v220 .gsf-editor-close{top:7px;right:8px;width:31px;height:31px}}
    </style>
"""

if GSF_WEB_MODE:
    st.markdown(r"""

<script id="V389_HIDE_OUTER_EDITOR_CTA">(()=>{const host=document.getElementById('gsf-editor-overlay-v220');if(!host)return;const clean=()=>host.querySelectorAll('button,a,[role="button"],div').forEach(el=>{const t=String(el.textContent||'').replace(/\s+/g,' ').trim().toUpperCase();if(t.length<90&&t.includes('HAI FINITO')&&t.includes('CREA IL TUO SHORT')){const x=el.closest('button,a,[role="button"]')||el;x.style.setProperty('display','none','important')}});clean();try{new MutationObserver(clean).observe(host,{childList:true,subtree:true})}catch(_e){}})();</script>

<script id="v392EditorCloseCleanup">(()=>{const host=document.getElementById('gsf-editor-overlay-v220');if(!host)return;const norm=v=>String(v||'').trim().toLowerCase();const mark=()=>{host.querySelectorAll('button,[role="button"],a').forEach(el=>{const vals=[norm(el.textContent),norm(el.getAttribute('aria-label')),norm(el.getAttribute('title')),norm(el.className),norm(el.id)];const close=vals.some(v=>v==='×'||v==='✕'||v==='✖'||v==='x'||v==='close'||v==='chiudi'||v.includes('close')||v.includes('chiudi'));if(close)el.classList.add('v392EditorCloseGone')})};mark();try{new MutationObserver(mark).observe(host,{childList:true,subtree:true})}catch(_e){}})();</script>

<!-- v393EditorParentCleanup: lifecycle owned by GSFNavigation -->

<!-- V394_MOBILE_EDITOR_FOOTER_RESTORE retired: the global shell owns footer visibility on every route. -->

<!-- GSF_EDITOR_OVERLAY_HTML: kept at column 0; 4-space indentation turns this markup into a Markdown code block. -->
    <!-- gsf-editor-overlay-v220: mounted once by the parent app. -->
<div class="gsf-script-guard" style="display:none!important"></div>

    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    _GSF_PARENT_EDITOR = r"""<!doctype html><html><body style="margin:0;display:none">
    <script>
    ((P)=>{
      const window=P;
      const document=P.document;
      const location=P.location;

    (()=>{
      const o=document.getElementById('gsf-editor-overlay-v220'); if(!o)return;
      const bridge=P.GSFNavigation.bridge('editor',globalThis.frameElement);
      let openEpoch=0;
      const frame=o.querySelector('.gsf-editor-frame'),left=document.getElementById('gsf-editor-note-left'),right=document.getElementById('gsf-editor-note-right');
      let metadataReady=frame.dataset.loaded==='1';
      let mobileReady=frame.dataset.ready==='1';
      let seq=0;
      const copies={idle:['Qui modelli<br>la tua giocata','Tocca uno strumento<br>e guarda cosa cambia'],frame:['Trova il punto<br>giusto','Inquadra l’azione<br>senza perdere il gameplay'],cover:['Scegli il frame<br>che racconta tutto','La cover deve<br>fermarsi negli occhi'],look:['Dagli il tuo<br>look','Più pulito, più gaming<br>o più cinematico'],caption:['Fai parlare<br>il momento','Le parole entrano<br>dove serve'],audio:['Fallo sentire','Voce, gioco e impatto<br>devono respirare insieme'],ai:['Lascia leggere<br>la scena alla Game AI','Ti aiuta a seguire<br>ciò che conta davvero'],play:['Guardalo vivere','Controlla il risultato<br>prima di chiudere'],done:['Ci siamo','Quando ti convince<br>torna al tuo Short']};
      const morph=(el,html,s)=>{if(!el||el.innerHTML===html)return;el.classList.remove('in');el.classList.add('out');setTimeout(()=>{if(s!==seq)return;el.innerHTML=html;el.classList.remove('out');void el.offsetWidth;el.classList.add('in');setTimeout(()=>el.classList.remove('in'),1100)},420)};
      const guide=(key)=>{const c=copies[key]||copies.idle,s=++seq;morph(left,c[0],s);morph(right,c[1],s)};
      const wire=()=>{try{const d=frame.contentDocument;if(!d)return;d.addEventListener('click',ev=>{const b=ev.target.closest&&ev.target.closest('button');if(!b)return;const t=(b.innerText||b.textContent||'').trim().toUpperCase();if(t.includes('FRAME'))guide('frame');else if(t.includes('COVER'))guide('cover');else if(t.includes('LOOK'))guide('look');else if(t.includes('CAPTION'))guide('caption');else if(t.includes('AUDIO'))guide('audio');else if(t.includes('GAME AI'))guide('ai');else if(t.includes('PLAY')||t.includes('PAUSE'))guide('play');else if(t.includes('DONE'))guide('done')},true)}catch(e){}};
      const KEY='gsf_editor_overlay_open_v223';
      const editorMeta=P.GSFNavigation.surfaceState('editor',()=>({video_url:'',initial_state:{}}));
      let pendingSelection=null;
      /* GSF_MOBILE_EDITOR_2026_BRIDGE */
      const MOBILE_EDITOR_SRC='/game-editor-mobile/';
      const DESKTOP_EDITOR_SRC='/editor-live/';
      const selectedEditorSource=()=>window.matchMedia('(max-width: 760px)').matches?MOBILE_EDITOR_SRC:DESKTOP_EDITOR_SRC;
      const isMobileEditor=()=>String(frame.dataset.editorSource||'')===MOBILE_EDITOR_SRC;
      const ensureMobileEditorFullscreenStyle=()=>{
        let style=document.getElementById('gsf-mobile-editor-fullscreen-style');
        if(style)return style;
        style=document.createElement('style');style.id='gsf-mobile-editor-fullscreen-style';
        style.append(document.createTextNode(`html.gsf-mobile-editor-fullscreen #gsf-global-gamebar,html.gsf-mobile-editor-fullscreen #gsf-global-header,html.gsf-mobile-editor-fullscreen #gsf-global-footer{display:none!important;visibility:hidden!important;pointer-events:none!important}html.gsf-mobile-editor-fullscreen #gsf-editor-overlay-v220{inset:0!important;top:0!important;bottom:0!important;width:100vw!important;height:100dvh!important;padding:0!important;z-index:2147483646!important}html.gsf-mobile-editor-fullscreen #gsf-editor-overlay-v220 .gsf-editor-shell,html.gsf-mobile-editor-fullscreen #gsf-editor-overlay-v220 .gsf-editor-body{inset:0!important;top:0!important;width:100%!important;height:100%!important;max-width:none!important;max-height:none!important;border:0!important;border-radius:0!important}`));
        document.head.appendChild(style);return style;
      };
      const sendMobileEditorInit=()=>{
        if(!isMobileEditor()||!metadataReady||!mobileReady||bridge.signal.aborted)return;
        const initial=(editorMeta.initial_state&&typeof editorMeta.initial_state==='object')?editorMeta.initial_state:{};
        const payload={
          type:'GSF_GAME_EDITOR_INIT',
          binding:{source_key:String(editorMeta.source_key||''),clip_start:Number(editorMeta.clip_start)||0,clip_duration:Number(editorMeta.clip_duration)||15},
          session:(editorMeta.session&&typeof editorMeta.session==='object')?editorMeta.session:{},
          project:(editorMeta.project&&typeof editorMeta.project==='object')?editorMeta.project:{},
          media:{url:editorMeta.ready===false?'':String(editorMeta.video_url||'/editor-media/current')},
          initial_state:initial,
          event_map:Array.isArray(editorMeta.event_map)?editorMeta.event_map:[],
          brain_context:(editorMeta.brain_context&&typeof editorMeta.brain_context==='object')?editorMeta.brain_context:{},
          ai_suggestions:Array.isArray(editorMeta.ai_suggestions)?editorMeta.ai_suggestions:[]
        };
        const fingerprint=JSON.stringify(payload),child=frame.contentDocument;
        if(frame.__gsfInitDocument===child&&frame.__gsfInitFingerprint===fingerprint)return;
        frame.__gsfInitDocument=child;frame.__gsfInitFingerprint=fingerprint;frame.__gsfEditorInitialized=true;
        frame.contentWindow.postMessage(payload,location.origin);
      };
      let mobileSaveChain=Promise.resolve();
      const postMobileEditorStatus=(message,ok,error='',extra={})=>{
        try{frame.contentWindow.postMessage({type:'GSF_GAME_EDITOR_SAVE_STATUS',sequence:Number(message.sequence)||0,ok:!!ok,error:String(error||''),...extra},location.origin)}catch(_e){}
      };
      const resetMobileEditorFullscreen=()=>{
        o.classList.remove('gsf-mobile-editor-fullscreen');
        document.documentElement.classList.remove('gsf-mobile-editor-fullscreen');
        try{frame.contentWindow.postMessage({type:'GSF_GAME_EDITOR_SHELL_CLOSE'},location.origin)}catch(_e){}
      };
      const persistMobileEditorState=(message)=>{
        if(!metadataReady)return Promise.reject(new Error('Progetto ancora in caricamento. Riprova.'));
        const binding=message.binding;
        if(!binding||String(binding.source_key||'')!==String(editorMeta.source_key||'')||Math.abs((Number(binding.clip_start)||0)-(Number(editorMeta.clip_start)||0))>.1||Math.abs((Number(binding.clip_duration)||15)-(Number(editorMeta.clip_duration)||15))>.1)return Promise.reject(new Error('Il progetto Editor è cambiato. Riaprilo prima di salvare.'));
        const state={...((message.state&&typeof message.state==='object')?message.state:{})};
        const context={clip_start:Number(editorMeta.clip_start)||0,clip_duration:Number(editorMeta.clip_duration)||Number(state.sourceDuration)||15};
        const source_key=String(editorMeta.source_key||'');
        editorMeta.initial_state={...state};
        const operation=mobileSaveChain.then(async()=>{
          const response=await fetch('/editor/state/save',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({state,context,source_key})});
          const payload=await response.json().catch(()=>({}));
          if(!response.ok||!payload.ok)throw new Error(payload.error||'Stato Editor non salvato');
          return payload;
        });
        mobileSaveChain=operation.catch(()=>{});
        return operation;
      };
      const navigateMobileEditorToShort=()=>P.postMessage({type:'GSF_SHELL_NAV',target:'short'},location.origin);
      const saveMobileDraft=(message)=>persistMobileEditorState(message).then(async()=>{
        const response=await fetch('/creator-hub/project/save-draft',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({})});
        const payload=await response.json().catch(()=>({}));
        if(!response.ok||!payload.ok)throw new Error(payload.error||'Bozza non salvata');
        postMobileEditorStatus(message,true,'',{draft:true});
      });
      const currentAction=epoch=>!bridge.signal.aborted&&P.GSFNavigation.snapshot().target==='editor'&&P.GSFNavigation.snapshot().epoch===epoch;
      const handleMobileEditorMessage=(event)=>{
        if(event.origin!==location.origin||event.source!==frame.contentWindow||!event.data)return false;
        if(event.data.type==='GSF_GAME_EDITOR_READY'){mobileReady=true;sendMobileEditorInit();return true}
        if(event.data.type!=='GSF_GAME_EDITOR_UI')return false;
        const message=event.data;
        const action=String(message.action||'');
        const actionEpoch=P.GSFNavigation.snapshot().epoch;
        if(action==='autosave'){
          persistMobileEditorState(message).then(()=>postMobileEditorStatus(message,true)).catch(error=>postMobileEditorStatus(message,false,error&&error.message||error));
          return true;
        }
        if(action==='save_draft'){
          saveMobileDraft(message).catch(error=>postMobileEditorStatus(message,false,error&&error.message||error));
          return true;
        }
        if(action==='continue_to_short'){
          persistMobileEditorState(message).then(()=>{postMobileEditorStatus(message,true);if(currentAction(actionEpoch))navigateMobileEditorToShort()}).catch(error=>postMobileEditorStatus(message,false,error&&error.message||error));
          return true;
        }
        if(action==='close'){
          persistMobileEditorState(message).then(()=>{postMobileEditorStatus(message,true);if(currentAction(actionEpoch))P.GSFNavigation.navigate({target:'home'})}).catch(error=>postMobileEditorStatus(message,false,error&&error.message||error));
          return true;
        }
        if(action==='fullscreen_changed'){
          const active=message.active===true&&P.GSFNavigation.snapshot().target==='editor';
          ensureMobileEditorFullscreenStyle();
          o.classList.toggle('gsf-mobile-editor-fullscreen',active);
          document.documentElement.classList.toggle('gsf-mobile-editor-fullscreen',active);
          return true;
        }
        return true;
      };
      /* GSF_MOBILE_EDITOR_2026_BRIDGE_END */
      /* V326_HEADER_FULL_WIRE */
setTimeout(()=>{const b=document.querySelector('#gsf-editor-overlay-v220 .v326HeaderFull');if(b&&!b.dataset.wired){b.dataset.wired='1';b.addEventListener('click',()=>{try{frame.contentWindow.postMessage({type:'GSF_EDITOR_FULLSCREEN_V326'},location.origin)}catch(_e){}})}},0);
      const sendRender=()=>{
        if(bridge.signal.aborted||!metadataReady||frame.dataset.ready!=='1')return;
        if(isMobileEditor()){sendMobileEditorInit();return}
        try{
          frame.contentWindow.postMessage({
            type:'streamlit:render',
            args:{
              video_url:editorMeta.ready===false?'':String(editorMeta.video_url||'/editor-media/current'),
              initial_state:(editorMeta.initial_state&&typeof editorMeta.initial_state==='object')?editorMeta.initial_state:{},
              event_map:[],
              event_duration:Number((editorMeta.initial_state||{}).sourceDuration)||15,
              vision_profile:'Auto',vision_zones:[],brain_context:{},height:720
            }
          },location.origin);
          frame.__gsfEditorInitialized=true;
        }catch(e){}
      };
      const scheduleRender=delay=>{const expected=openEpoch;bridge.timeout(()=>{if(expected===openEpoch&&P.GSFNavigation.snapshot().target==='editor')sendRender();},delay);};
      frame.addEventListener('load',()=>{frame.dataset.ready='1';if(!isMobileEditor())wire();scheduleRender(0)},{signal:bridge.signal});
      const open=(remember=true)=>{
        const requestEpoch=++openEpoch;
        const routeEpoch=P.GSFNavigation.snapshot().epoch;

        const selection=pendingSelection;pendingSelection=null;
        const forceReload=!!(editorMeta.needsReload||selection?.resume||selection?.draft_id||selection?.project_id);
        editorMeta.needsReload=false;
        if(forceReload){metadataReady=false;frame.__gsfInitFingerprint='';frame.__gsfEditorInitialized=false;}
        // V249: switch page immediately; refresh editor state after the surface is visible.
        o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';o.setAttribute('aria-hidden','false');
        if(remember)try{sessionStorage.setItem(KEY,'1')}catch(e){}
        guide('idle');

        const editorSource=selectedEditorSource();
        const reused=frame.dataset.loaded==='1'&&frame.dataset.editorSource===editorSource;
        if(!reused){
          metadataReady=false;mobileReady=false;frame.dataset.ready='0';frame.__gsfEditorInitialized=false;
          frame.dataset.editorSource=editorSource;
          // Surface documents must not add entries to the root router history.
          frame.contentWindow.location.replace(editorSource+'?v=2026');
          frame.dataset.loaded='1';
        }


        if(selection&&selection.video_url)metadataReady=false;
        fetch('/editor/state',{cache:'no-store',credentials:'same-origin'})
          .then(r=>r.json().then(j=>({ok:r.ok,j})))
          .then(({ok,j})=>{
            if(ok&&j&&j.ok&&!bridge.signal.aborted&&requestEpoch===openEpoch&&routeEpoch===P.GSFNavigation.snapshot().epoch&&P.GSFNavigation.snapshot().target==='editor'){
              if(reused&&!forceReload&&metadataReady&&frame.__gsfEditorInitialized&&String(j.video_url||'')===String(editorMeta.video_url||'')&&j.ready===editorMeta.ready)return;
              Object.assign(editorMeta,j,{video_url:String(j.video_url||'')});
              if(selection&&selection.video_url){
                const selectedDuration=Math.max(.5,Number(selection.duration)||15);
                Object.assign(editorMeta,{video_url:String(selection.video_url),clip_start:Number(selection.start_time)||0,clip_duration:selectedDuration,ready:true});
                editorMeta.initial_state=Object.assign({},editorMeta.initial_state||{},{inPoint:0,outPoint:selectedDuration,sourceDuration:selectedDuration,momentIndex:Number(selection.momentIndex)||0});
              }
              metadataReady=true;
              scheduleRender(0);
            }
          })
          .catch(()=>{});
      };
      const close=()=>{++openEpoch;resetMobileEditorFullscreen();o.classList.remove('is-open');o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';o.setAttribute('aria-hidden','true');try{sessionStorage.setItem(KEY,'0')}catch(e){}};

      /* V288 EDITOR JOURNEY BRIDGE */
      const triggerCreateShort=()=>{
        const nodes=[...document.querySelectorAll('button,a,[role=button]')].filter(x=>!x.closest('#gsf-editor-overlay-v220'));
        const wanted=['crea short finale','crea il tuo short','crea short'];
        const el=nodes.find(x=>wanted.some(w=>(x.innerText||x.textContent||'').trim().toLowerCase().includes(w)));
        if(el){close();el.click();return true}
        return false;
      };
      o.querySelector('.gsf-editor-close').onclick=()=>P.GSFNavigation.navigate({target:'home'});o.addEventListener('click',e=>{if(e.target===o)P.GSFNavigation.navigate({target:'home'})},{signal:bridge.signal});
      window.addEventListener('message',e=>{
        if(e.origin===location.origin&&e.data?.type==='gsf-upload'&&e.data.state==='done'){editorMeta.needsReload=true;return;}
        if(handleMobileEditorMessage(e))return;
        if(e.source===frame.contentWindow&&e.data&&e.data.type==='streamlit:setComponentValue'){
          /* V323_EDITOR_ACTION_BRIDGE */
          const state=e.data.value;
          if(state&&typeof state==='object'){
            const action=String(state.editorAction||'');
            const actionEpoch=P.GSFNavigation.snapshot().epoch;
            const cleanState={...state};
            delete cleanState.editorAction;delete cleanState.editorActionNonce;
            editorMeta.initial_state=cleanState;
            const notify=(title,msg='',kind='success')=>{try{window.GSFNotify&&window.GSFNotify.show(title,msg,kind)}catch(_e){}};
            const saveState=fetch('/editor/state/save',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({state:cleanState,source_key:String(editorMeta.source_key||''),context:{clip_start:Number(editorMeta.clip_start)||0,clip_duration:Number(editorMeta.clip_duration)||15}})}).then(r=>{if(!r.ok)throw new Error('Stato Editor non salvato');return r});
            if(action==='save_draft'){
              saveState.then(()=>fetch('/creator-hub/project/save-draft',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({})}))
                .then(async r=>{let j={};try{j=await r.json()}catch(_e){};if(!r.ok||!j.ok)throw new Error(j.error||'Bozza non salvata');notify('Bozza salvata',String((j.draft||{}).title||''),'success')})
                .catch(err=>notify('Bozza non salvata',String(err&&err.message||err),'error'));
              guide('done');
              return;
            }
            if(action==='create_short'){
              saveState.then(()=>{
                if(!currentAction(actionEpoch))return;
                P.GSFNavigation.navigate({target:'home'});
                try{sessionStorage.setItem(KEY,'0')}catch(_e){}
                const target=document.querySelector('.st-key-gsf-major-create-short button,.st-key-create_final_short_v54 button');
                if(target){target.click();return;}
                const fallback=[...document.querySelectorAll('button')].find(b=>/crea\s+short/i.test(String(b.innerText||b.textContent||'')));
                if(fallback){fallback.click();return;}
                notify('Crea Short non disponibile','Riapri il progetto e riprova.','error');
              }).catch(err=>notify('Crea Short non avviato',String(err&&err.message||err),'error'));
              guide('done');
              return;
            }
            saveState.catch(()=>{});
            guide('done');
          }
          return;
        }
      },{signal:bridge.signal});
      P.GSFNavigation.registerSurface('editor',{adopt:()=>frame.dataset.loaded==='1',open:data=>{pendingSelection={video_url:String(data.video_url||''),duration:Number(data.duration)||15,start_time:Number(data.start_time)||0,momentIndex:Number(data.momentIndex)||0,resume:data.resume===true,draft_id:String(data.draft_id||''),project_id:String(data.project_id||'')};open()},close});
    })();
    
    })(window.parent);
    </script>
    </body></html>"""

_GSF_SURFACE_AI = r"""<div id="gsf-ai-overlay-v221" aria-hidden="true">
      <section class="gsf-ai-shell" role="dialog" aria-modal="false" aria-label="Motori IA">
        <button class="gsf-ai-close" type="button" aria-label="Chiudi">×</button>
        <iframe src="about:blank" data-src="/ai-v221/" data-loaded="0" title="Motori IA"></iframe>
      </section>
    </div>"""

if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v221-ai-shell">
    #gsf-ai-overlay-v221{position:fixed;left:0;right:0;top:0;bottom:78px;z-index:2147483654;display:flex;align-items:center;justify-content:center;padding:24px clamp(14px,2.5vw,38px) 12px;background:rgba(222,238,247,.46);-webkit-backdrop-filter:blur(5px) saturate(.98);backdrop-filter:blur(5px) saturate(.98);opacity:0;visibility:hidden;pointer-events:none;transition:opacity .24s ease,visibility .24s ease}
    #gsf-ai-overlay-v221.is-open{opacity:1;visibility:visible;pointer-events:auto}
    #gsf-ai-overlay-v221 .gsf-ai-shell{position:relative;width:min(1240px,calc(100vw - 30px));height:min(730px,calc(100dvh - 118px));border:1px solid rgba(157,193,219,.35);border-radius:30px;overflow:hidden;background:#050D16;box-shadow:0 30px 86px rgba(19,45,65,.22),inset 0 1px 0 rgba(255,255,255,.94);transform:translateY(10px) scale(.975);opacity:0;transition:transform .32s cubic-bezier(.16,.84,.24,1),opacity .24s ease}
    #gsf-ai-overlay-v221.is-open .gsf-ai-shell{transform:translateY(0) scale(1);opacity:1}
    #gsf-ai-overlay-v221 iframe{width:100%;height:100%;border:0;background:#050D16}
    #gsf-ai-overlay-v221 .gsf-ai-close{position:absolute;z-index:7;right:13px;top:11px;width:34px;height:34px;border-radius:12px;border:1px solid rgba(158,190,216,.34);background:rgba(255,255,255,.94);color:#617B9D;font-size:20px;cursor:pointer;box-shadow:0 7px 18px rgba(64,104,143,.09)}
    @media(max-width:760px){#gsf-ai-overlay-v221{bottom:70px;padding:8px 5px}#gsf-ai-overlay-v221 .gsf-ai-shell{width:calc(100vw - 10px);height:calc(100dvh - 84px);border-radius:22px}#gsf-ai-overlay-v221 .gsf-ai-close{right:8px;top:7px;width:31px;height:31px}}
    </style>
        <!-- gsf-ai-overlay-v221: mounted once by the parent app. -->
    <div class="gsf-script-guard" style="display:none!important"></div>

    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    _GSF_PARENT_AI = r"""<!doctype html><html><body style="margin:0;display:none">
    <script>
    ((P)=>{
      const window=P;
      const document=P.document;
      const location=P.location;

    (()=>{
      const KEY='gsf_ai_overlay_open_v221';
      const o=document.getElementById('gsf-ai-overlay-v221');if(!o)return;
      const bridge=P.GSFNavigation.bridge('ai',globalThis.frameElement);
      const frame=o.querySelector('iframe');
      const broadcastHome=(payload)=>{
        document.querySelectorAll('iframe').forEach(f=>{
          try{if(f!==frame&&f.contentWindow)f.contentWindow.postMessage(payload,location.origin)}catch(e){}
        });
      };
      const forwardState=(data)=>{
        try{frame.contentWindow.postMessage({type:'GSF_AI_STATE',state:{loaded:!!data.loaded,duration:Number(data.duration)||15,engine:String(data.engine||''),previews:Array.isArray(data.previews)?data.previews:[]}},location.origin)}catch(e){}
      };
      const ensureFrame=()=>{
        if(frame.dataset.loaded==='1')return;
        frame.contentWindow.location.replace(frame.dataset.src||'/ai-v221/');
        frame.dataset.loaded='1';
      };
      const open=(remember=true)=>{
        ensureFrame();
        const so=document.getElementById('gsf-social-overlay-v159');if(so){so.classList.remove('is-open');so.style.opacity='0';so.style.visibility='hidden';so.style.pointerEvents='none'}
        const ed=document.getElementById('gsf-editor-overlay-v220');if(ed){ed.classList.remove('is-open');ed.style.opacity='0';ed.style.visibility='hidden';ed.style.pointerEvents='none'}
        o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';o.setAttribute('aria-hidden','false');
        if(remember)try{sessionStorage.setItem(KEY,'1')}catch(e){}
        setTimeout(()=>broadcastHome({type:'GSF_AI_COMMAND',action:'get_state'}),80);
      };
      const close=()=>{o.classList.remove('is-open');o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';o.setAttribute('aria-hidden','true');try{sessionStorage.setItem(KEY,'0')}catch(e){}};
      o.querySelector('.gsf-ai-close').onclick=()=>P.GSFNavigation.navigate({target:'home'});o.addEventListener('click',e=>{if(e.target===o)P.GSFNavigation.navigate({target:'home'})},{signal:bridge.signal});
      window.addEventListener('message',e=>{
        if(e.origin!==location.origin||!e.data)return;
        if(e.data.type==='GSF_AI_UI'){
          const action=String(e.data.action||'');
          if(action==='ready'){broadcastHome({type:'GSF_AI_COMMAND',action:'get_state'});return}
          const selection={action,candidate_id:e.data.candidate_id,video:e.data.video,start_time:e.data.start_time,end_time:e.data.end_time,duration:e.data.duration,engine:e.data.engine,index:e.data.index,request_id:e.data.request_id,restore:e.data.restore===true};
          if(action==='create_short'){
            broadcastHome({...selection,type:'GSF_AI_COMMAND',action:'select_moment'});
            close();
            P.postMessage({type:'GSF_SHELL_NAV',target:'short',candidate_id:selection.candidate_id,video:selection.video,start_time:selection.start_time,end_time:selection.end_time,index:selection.index},location.origin);
            return;
          }
          broadcastHome({type:'GSF_AI_COMMAND',...selection});
          return;
        }
        if(e.data.type==='GSF_SHELL_NAV'&&e.data.target==='ai-state')forwardState(e.data);
      },{signal:bridge.signal});
      P.GSFNavigation.registerSurface('ai',{open:()=>open(),close});
    })();
    
    })(window.parent);
    </script>
    </body></html>"""

if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v223-account-shell">
    #gsf-account-overlay-v223{position:fixed;left:0;right:0;top:0;bottom:78px;z-index:2147483662;display:flex;align-items:center;justify-content:center;padding:24px clamp(14px,2.5vw,38px) 12px;background:rgba(222,238,247,.46);-webkit-backdrop-filter:blur(5px) saturate(.98);backdrop-filter:blur(5px) saturate(.98);opacity:0;visibility:hidden;pointer-events:none;transition:opacity .24s ease,visibility .24s ease}
    #gsf-account-overlay-v223.is-open{opacity:1;visibility:visible;pointer-events:auto}
    #gsf-account-overlay-v223 .gsf-account-shell{position:relative;width:min(980px,calc(100vw - 30px));height:min(680px,calc(100dvh - 118px));border:1px solid rgba(157,193,219,.35);border-radius:30px;overflow:hidden;background:#050D16;box-shadow:0 30px 86px rgba(19,45,65,.22),inset 0 1px 0 rgba(255,255,255,.94);transform:translateY(10px) scale(.975);opacity:0;transition:transform .30s cubic-bezier(.16,.84,.24,1),opacity .24s ease}
    #gsf-account-overlay-v223.is-open .gsf-account-shell{transform:translateY(0) scale(1);opacity:1}
    #gsf-account-overlay-v223 iframe{width:100%;height:100%;border:0;background:#050D16}
    #gsf-account-overlay-v223 .gsf-account-close{position:absolute;z-index:7;right:13px;top:11px;width:34px;height:34px;border:1px solid rgba(158,190,216,.34);border-radius:12px;background:rgba(255,255,255,.94);color:#617B9D;font-size:20px;cursor:pointer}
    @media(max-width:760px){#gsf-account-overlay-v223{bottom:70px;padding:8px 5px}#gsf-account-overlay-v223 .gsf-account-shell{width:calc(100vw - 10px);height:calc(100dvh - 84px);border-radius:22px}#gsf-account-overlay-v223 .gsf-account-close{right:8px;top:7px;width:31px;height:31px}}
    </style>
    <div id="gsf-account-overlay-v223" aria-hidden="true">
      <section class="gsf-account-shell" role="dialog" aria-modal="false" aria-label="Account">
        <button class="gsf-account-close" type="button" aria-label="Chiudi">×</button>
        <iframe src="about:blank" data-src="/account/" data-loaded="0" title="Account"></iframe>
      </section>
    </div>
    <div class="gsf-script-guard" style="display:none!important"></div>

    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html('<!-- Surface navigation is owned by GSFNavigation. -->', height=0, scrolling=False)

if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v249-full-page-shell">
    :root{--gsf-pagebar-h:78px}

    #gsf-social-overlay-v159,
    #gsf-creator-hub-live-v160,
    #gsf-editor-overlay-v220,
    #gsf-ai-overlay-v221,
    #gsf-account-overlay-v223{
      position:fixed!important;
      inset:0!important;
      bottom:0!important;
      padding:0 0 var(--gsf-pagebar-h)!important;
      display:flex!important;
      align-items:stretch!important;
      justify-content:stretch!important;
      background:#050D16!important;
      -webkit-backdrop-filter:none!important;
      backdrop-filter:none!important;
      opacity:0;
      visibility:hidden;
      pointer-events:none;
      transition:none!important;
      overflow:hidden!important;
    }

    #gsf-social-overlay-v159.is-open,
    #gsf-creator-hub-live-v160.is-open,
    #gsf-editor-overlay-v220.is-open,
    #gsf-ai-overlay-v221.is-open,
    #gsf-account-overlay-v223.is-open{
      opacity:1!important;
      visibility:visible!important;
      pointer-events:auto!important;
    }

    #gsf-social-overlay-v159 .gsf-social-shell,
    #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
    #gsf-editor-overlay-v220 .gsf-editor-shell,
    #gsf-ai-overlay-v221 .gsf-ai-shell,
    #gsf-account-overlay-v223 .gsf-account-shell{
      position:relative!important;
      width:100%!important;
      max-width:none!important;
      height:calc(100dvh - var(--gsf-pagebar-h))!important;
      max-height:none!important;
      margin:0!important;
      border:0!important;
      border-radius:0!important;
      background:#050D16!important;
      box-shadow:none!important;
      opacity:1!important;
      transform:translateX(10px)!important;
      transition:transform .11s cubic-bezier(.2,.82,.25,1)!important;
      overflow:hidden!important;
    }

    #gsf-social-overlay-v159.is-open .gsf-social-shell,
    #gsf-creator-hub-live-v160.is-open .gsf-hub-shell-v160,
    #gsf-editor-overlay-v220.is-open .gsf-editor-shell,
    #gsf-ai-overlay-v221.is-open .gsf-ai-shell,
    #gsf-account-overlay-v223.is-open .gsf-account-shell{
      transform:translateX(0)!important;
      opacity:1!important;
    }

    #gsf-social-overlay-v159 iframe,
    #gsf-creator-hub-live-v160 iframe,
    #gsf-editor-overlay-v220 iframe,
    #gsf-ai-overlay-v221 iframe,
    #gsf-account-overlay-v223 iframe{
      background:#050D16!important;
    }

    /* One Game Bar owned by the active page, never the Home underneath. */
    #gsf-page-nav-v249{
      position:fixed;
      left:50%;
      bottom:10px;
      transform:translateX(-50%);
      z-index:2147483647;
      width:min(760px,72vw);
      height:58px;
      min-height:58px;
      padding:4px 10px;
      display:grid;
      grid-template-columns:repeat(4,1fr);
      gap:4px;
      border:1px solid rgba(139,181,218,.30);
      border-radius:999px;
      background:rgba(255,255,255,.96);
      box-shadow:0 10px 28px rgba(59,104,148,.11),0 0 0 4px rgba(226,243,255,.30),inset 0 1px 0 #fff;
      -webkit-backdrop-filter:blur(22px);
      backdrop-filter:blur(22px);
      opacity:0;
      visibility:hidden;
      pointer-events:none;
      transition:none;
    }
    #gsf-page-nav-v249.is-open{
      opacity:1;
      visibility:visible;
      pointer-events:auto;
    }
    #gsf-page-nav-v249 .gsf-page-nav-item{
      border:0;
      background:transparent;
      border-radius:21px;
      padding:2px 3px;
      color:#8192AA;
      display:flex;
      flex-direction:column;
      align-items:center;
      justify-content:center;
      gap:2px;
      font-size:8px;
      font-weight:800;
      cursor:pointer;
    }
    #gsf-page-nav-v249 .gsf-page-nav-item svg{
      width:19px;
      height:19px;
      padding:5px;
      box-sizing:content-box;
      border-radius:50%;
      color:currentColor;
      fill:none;
      stroke:currentColor;
      stroke-width:2;
      stroke-linecap:round;
      stroke-linejoin:round;
      background:linear-gradient(145deg,#F9FCFF,#EDF5FC);
      border:1px solid rgba(150,184,215,.24);
    }
    #gsf-page-nav-v249 .gsf-page-nav-item.active{
      color:#4F93D7;
      background:rgba(219,241,255,.70);
    }
    #gsf-page-nav-v249 .gsf-page-nav-item.active svg{
      color:#4F93D7;
      background:linear-gradient(145deg,#E8F5FF,#D8EBFF);
    }

    @media(max-width:760px){
      :root{--gsf-pagebar-h:70px}
      #gsf-page-nav-v249{
        width:calc(100vw - 24px);
        height:58px;
        min-height:58px;
        bottom:6px;
        padding:4px 8px;
      }
      #gsf-page-nav-v249 .gsf-page-nav-item{font-size:7px}
      #gsf-page-nav-v249 .gsf-page-nav-item svg{width:18px;height:18px;padding:5px}
    }

    @media(prefers-reduced-motion:reduce){
      #gsf-social-overlay-v159 .gsf-social-shell,
      #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
      #gsf-editor-overlay-v220 .gsf-editor-shell,
      #gsf-ai-overlay-v221 .gsf-ai-shell,
      #gsf-account-overlay-v223 .gsf-account-shell{
        transition:none!important;
        transform:none!important;
      }
    }
    </style>


    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html(r"""<!-- V343 chrome and GSFNavigation replace the V249/V250 controllers. -->""", height=0, scrolling=False)

if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v250-page-visual-system">
    :root{
      --gsf-page-top:44px;
      --gsf-page-bottom:108px;
      --gsf-page-side:clamp(118px,9.5vw,160px);
      --gsf-page-gap:clamp(12px,1.4vw,24px);
      --gsf-page-bg:#FAFDFF;
      --gsf-page-ink:#0D2A66;
      --gsf-page-soft:#7185A6;
    }

    #gsf-social-overlay-v159,
    #gsf-creator-hub-live-v160,
    #gsf-editor-overlay-v220,
    #gsf-ai-overlay-v221,
    #gsf-account-overlay-v223{
      background:
        #050D16!important;
      overflow:hidden!important;
    }

    .gsf-page-top-v250{
      position:absolute;
      left:0;right:0;top:0;
      height:var(--gsf-page-top);
      display:flex;
      align-items:center;
      justify-content:space-between;
      padding:0 clamp(16px,2vw,34px);
      z-index:20;
      color:#6C81A1;
      pointer-events:none;
    }
    .gsf-page-brand-v250{
      font-size:clamp(10px,.8vw,13px);
      line-height:1;
      font-weight:800;
      letter-spacing:.28em;
      white-space:nowrap;
    }
    .gsf-page-title-v250{
      position:absolute;
      left:50%;
      transform:translateX(-50%);
      color:var(--gsf-page-ink);
      font-size:clamp(11px,.9vw,14px);
      font-weight:900;
      letter-spacing:.03em;
      white-space:nowrap;
    }
    .gsf-page-state-v250{
      min-width:64px;
      text-align:right;
      font-size:8px;
      font-weight:800;
      letter-spacing:.08em;
      opacity:.78;
    }

    .gsf-page-ad-v250{
      position:absolute;
      top:calc(var(--gsf-page-top) + 12px);
      bottom:calc(var(--gsf-page-bottom) + 12px);
      width:var(--gsf-page-side);
      z-index:16;
      display:flex;
      align-items:center;
      justify-content:center;
      padding:10px;
      border:1px solid rgba(150,184,214,.22);
      border-radius:20px;
      background:rgba(255,255,255,.72);
      box-shadow:0 12px 34px rgba(59,104,148,.07),inset 0 1px 0 rgba(255,255,255,.94);
      color:#7D90AD;
      font-size:clamp(8px,.65vw,10px);
      font-weight:700;
      letter-spacing:.03em;
      text-align:center;
      pointer-events:auto;
      overflow:hidden;
    }
    .gsf-page-ad-v250.left{left:clamp(12px,1.4vw,24px)}
    .gsf-page-ad-v250.right{right:clamp(12px,1.4vw,24px)}

    .gsf-page-footer-v250{
      position:absolute;
      left:0;right:0;
      bottom:72px;
      height:30px;
      z-index:20;
      display:grid;
      grid-template-columns:1fr auto 1fr;
      align-items:center;
      gap:12px;
      padding:0 clamp(16px,2vw,34px);
      border-top:1px solid rgba(150,184,214,.18);
      color:#7D90AD;
      pointer-events:none;
    }
    .gsf-page-footer-brand-v250{
      justify-self:start;
      font-size:7px;
      font-weight:700;
    }
    .gsf-page-footer-social-v250{
      justify-self:center;
      display:flex;
      align-items:center;
      gap:6px;
      pointer-events:auto;
    }
    .gsf-page-footer-social-v250 a{
      width:22px;height:22px;
      display:grid;
      place-items:center;
      border-radius:50%;
      background:rgba(255,255,255,.90);
      border:1px solid rgba(150,183,213,.24);
      box-shadow:0 5px 13px rgba(65,105,145,.08);
      text-decoration:none;
      font-size:8px;
      font-weight:900;
    }
    .gsf-page-footer-social-v250 a:nth-child(1){color:#1877F2}
    .gsf-page-footer-social-v250 a:nth-child(2){color:#C13584}
    .gsf-page-footer-social-v250 a:nth-child(3){color:#FF0033}
    .gsf-page-footer-social-v250 a:nth-child(4){color:#111827}
    .gsf-page-footer-social-v250 a:nth-child(5){color:#9146FF}
    .gsf-page-footer-meta-v250{
      justify-self:end;
      font-size:7px;
      font-weight:700;
    }

    /* Each page owns its content area; Home is completely covered. */
    #gsf-social-overlay-v159 .gsf-social-shell,
    #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
    #gsf-editor-overlay-v220 .gsf-editor-shell,
    #gsf-ai-overlay-v221 .gsf-ai-shell,
    #gsf-account-overlay-v223 .gsf-account-shell{
      position:absolute!important;
      top:var(--gsf-page-top)!important;
      bottom:var(--gsf-page-bottom)!important;
      left:calc(var(--gsf-page-side) + var(--gsf-page-gap) + 12px)!important;
      right:calc(var(--gsf-page-side) + var(--gsf-page-gap) + 12px)!important;
      width:auto!important;
      height:auto!important;
      max-width:none!important;
      max-height:none!important;
      margin:0!important;
      border:1px solid rgba(157,193,219,.22)!important;
      border-radius:24px!important;
      background:rgba(255,255,255,.82)!important;
      box-shadow:0 18px 54px rgba(42,86,126,.09),inset 0 1px 0 rgba(255,255,255,.96)!important;
      transform:none!important;
      transition:none!important;
      opacity:1!important;
      overflow:hidden!important;
    }

    #gsf-editor-overlay-v220 .gsf-editor-head{
      background:rgba(255,255,255,.88)!important;
      border-bottom:1px solid rgba(148,183,213,.18)!important;
    }

    #gsf-social-overlay-v159 iframe,
    #gsf-creator-hub-live-v160 iframe,
    #gsf-editor-overlay-v220 iframe,
    #gsf-ai-overlay-v221 iframe,
    #gsf-account-overlay-v223 iframe{
      width:100%!important;
      height:100%!important;
      border:0!important;
      background:#050D16!important;
    }

    #gsf-page-nav-v249{
      bottom:10px!important;
      height:54px!important;
      min-height:54px!important;
      width:min(760px,72vw)!important;
      padding:3px 10px!important;
      z-index:30!important;
    }

    #gsf-social-overlay-v159 .gsf-social-close,
    #gsf-creator-hub-live-v160 .gsf-hub-close-v160,
    #gsf-editor-overlay-v220 .gsf-editor-close,
    #gsf-ai-overlay-v221 .gsf-ai-close,
    #gsf-account-overlay-v223 .gsf-account-close{
      top:7px!important;
      right:9px!important;
      width:30px!important;
      height:30px!important;
      border-radius:10px!important;
      z-index:24!important;
      box-shadow:0 5px 14px rgba(64,104,143,.07)!important;
    }

    /* Responsive scaling: no giant fixed desktop and no cramped small screen. */
    @media(min-width:1600px) and (min-height:850px){
      :root{
        --gsf-page-top:48px;
        --gsf-page-bottom:114px;
        --gsf-page-side:clamp(145px,9vw,180px);
        --gsf-page-gap:clamp(18px,1.6vw,28px);
      }
      .gsf-page-footer-v250{bottom:76px;height:32px}
      #gsf-page-nav-v249{height:58px!important;min-height:58px!important}
    }

    @media(min-width:761px) and (max-height:720px){
      :root{
        --gsf-page-top:38px;
        --gsf-page-bottom:96px;
        --gsf-page-side:clamp(102px,8.4vw,132px);
        --gsf-page-gap:10px;
      }
      .gsf-page-footer-v250{bottom:65px;height:24px}
      #gsf-page-nav-v249{
        bottom:7px!important;
        height:48px!important;
        min-height:48px!important;
      }
      .gsf-page-ad-v250{
        top:calc(var(--gsf-page-top) + 8px);
        bottom:calc(var(--gsf-page-bottom) + 8px);
      }
    }

    @media(max-width:1000px) and (min-width:761px){
      :root{
        --gsf-page-side:86px;
        --gsf-page-gap:8px;
      }
      .gsf-page-ad-v250{
        width:86px;
        border-radius:16px;
        font-size:8px;
      }
    }

    @media(max-width:760px){
      :root{
        --gsf-page-top:32px;
        --gsf-page-bottom:88px;
        --gsf-page-side:0px;
        --gsf-page-gap:0px;
      }

      .gsf-page-top-v250{
        height:32px;
        padding:0 10px;
      }
      .gsf-page-brand-v250{
        font-size:7.5px;
        letter-spacing:.22em;
      }
      .gsf-page-title-v250{
        font-size:9px;
      }
      .gsf-page-state-v250{font-size:7px}

      .gsf-page-ad-v250{
        display:none!important;
      }

      #gsf-social-overlay-v159 .gsf-social-shell,
      #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
      #gsf-editor-overlay-v220 .gsf-editor-shell,
      #gsf-ai-overlay-v221 .gsf-ai-shell,
      #gsf-account-overlay-v223 .gsf-account-shell{
        top:var(--gsf-page-top)!important;
        bottom:var(--gsf-page-bottom)!important;
        left:5px!important;
        right:5px!important;
        border-radius:18px!important;
      }

      .gsf-page-footer-v250{
        display:none!important;
      }

      #gsf-page-nav-v249{
        width:calc(100vw - 20px)!important;
        bottom:5px!important;
        height:56px!important;
        min-height:56px!important;
      }
    }
    </style>
    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html(r"""<!doctype html><html><body style="margin:0;display:none"><script>
    ((P)=>{
      const d=P.document;
      const pages=[
        ['gsf-social-overlay-v159','Social'],
        ['gsf-creator-hub-live-v160','Creator Hub'],
        ['gsf-editor-overlay-v220','Game Editor'],
        ['gsf-ai-overlay-v221','Crea con IA'],
        ['gsf-account-overlay-v223','Account']
      ];

      const chrome=(title)=>`
        <div class="gsf-page-top-v250">
          <div class="gsf-page-brand-v250">GAMING SHORTS FACTORY</div>
          <div class="gsf-page-title-v250">${title}</div>
          <div class="gsf-page-state-v250">GSF</div>
        </div>
        <aside class="gsf-page-ad-v250 left"><span>Spazio pubblicitario</span></aside>
        <aside class="gsf-page-ad-v250 right"><span>Spazio pubblicitario</span></aside>
        <footer class="gsf-page-footer-v250">
          <span class="gsf-page-footer-brand-v250">Gaming Shorts Factory</span>
          <div class="gsf-page-footer-social-v250" aria-label="Canali social">
            <a href="https://www.facebook.com/profile.php?id=61595124112318&amp;locale=it_IT" target="_blank" rel="noopener noreferrer" aria-label="Facebook">f</a>
            <a href="https://www.instagram.com/gamingshortsfactory/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">◎</a>
            <a href="https://www.youtube.com/@Dans222nrg" target="_blank" rel="noopener noreferrer" aria-label="YouTube">▶</a>
            <a href="https://www.tiktok.com/@gamingshortsfactory" target="_blank" rel="noopener noreferrer" aria-label="TikTok">♪</a>
            <a href="https://www.twitch.tv/dan222s86" target="_blank" rel="noopener noreferrer" aria-label="Twitch">◈</a>
          </div>
          <span class="gsf-page-footer-meta-v250">© 2026</span>
        </footer>`;

      pages.forEach(([id,title])=>{
        const el=d.getElementById(id);
        if(!el||el.querySelector('.gsf-page-top-v250'))return;
        el.insertAdjacentHTML('afterbegin',chrome(title));
      });

      // Fast-open policy: keep all route frames warm. They are already mounted,
      // so page switches only toggle the active surface; no iframe reload.
      const warm=()=>{
        pages.forEach(([id])=>{
          const el=d.getElementById(id);
          if(!el)return;
          const f=el.querySelector('iframe');
          if(!f)return;
          f.loading='eager';
          try{f.contentWindow&&f.contentWindow.document}catch(_e){}
        });
      };

      if('requestIdleCallback' in P) P.requestIdleCallback(warm,{timeout:450});
      else P.setTimeout(warm,180);
    })(window.parent);
    </script></body></html>""",height=0,scrolling=False)

if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v250-shared-page-chrome">
    :root{
      --gsf-shell-top:46px;
      --gsf-shell-bottom:78px;
      --gsf-shell-ad-w:clamp(118px,9.5vw,164px);
      --gsf-shell-side:calc(var(--gsf-shell-ad-w) + clamp(18px,2vw,30px));
    }

    /* Same approved Home canvas. */
    #gsf-social-overlay-v159,
    #gsf-creator-hub-live-v160,
    #gsf-editor-overlay-v220,
    #gsf-ai-overlay-v221,
    #gsf-account-overlay-v223{
      padding:
        var(--gsf-shell-top)
        var(--gsf-shell-side)
        var(--gsf-shell-bottom)!important;
      background:
        radial-gradient(120% 55% at 50% 100%,rgba(122,200,255,.10),transparent 72%),linear-gradient(180deg,#FAFDFF 0%,#F7FBFF 60%,#F2F8FE 100%)!important;
    }

    /* Content is a page, never a floating translucent modal. */
    #gsf-social-overlay-v159 .gsf-social-shell,
    #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
    #gsf-editor-overlay-v220 .gsf-editor-shell,
    #gsf-ai-overlay-v221 .gsf-ai-shell,
    #gsf-account-overlay-v223 .gsf-account-shell{
      width:100%!important;
      height:100%!important;
      max-width:none!important;
      max-height:none!important;
      border:0!important;
      border-radius:0!important;
      background:transparent!important;
      box-shadow:none!important;
      transform:translateX(7px)!important;
      transition:transform .075s cubic-bezier(.22,.78,.22,1)!important;
    }
    #gsf-social-overlay-v159.is-open .gsf-social-shell,
    #gsf-creator-hub-live-v160.is-open .gsf-hub-shell-v160,
    #gsf-editor-overlay-v220.is-open .gsf-editor-shell,
    #gsf-ai-overlay-v221.is-open .gsf-ai-shell,
    #gsf-account-overlay-v223.is-open .gsf-account-shell{
      transform:translateX(0)!important;
    }

    #gsf-social-overlay-v159 iframe,
    #gsf-creator-hub-live-v160 iframe,
    #gsf-editor-overlay-v220 iframe,
    #gsf-ai-overlay-v221 iframe,
    #gsf-account-overlay-v223 iframe{
      width:100%!important;
      height:100%!important;
      border:0!important;
      border-radius:0!important;
      background:transparent!important;
    }

    /* Old modal close buttons are redundant: Home in the page Game Bar handles exit. */
    #gsf-social-overlay-v159 .gsf-social-close,
    #gsf-creator-hub-live-v160 .gsf-hub-close-v160,
    #gsf-editor-overlay-v220 .gsf-editor-close,
    #gsf-ai-overlay-v221 .gsf-ai-close,
    #gsf-account-overlay-v223 .gsf-account-close{
      display:none!important;
    }

    #gsf-page-chrome-v250{
      position:fixed;
      inset:0;
      z-index:2147483590;
      pointer-events:none;
      opacity:0;
      visibility:hidden;
      transition:none;
      color:#637DA8;
      font-family:"Avenir Next","SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    }
    #gsf-page-chrome-v250.is-open{
      opacity:1;
      visibility:visible;
    }
    #gsf-page-chrome-v250.is-open .gsf-page-head{
      z-index:3;
      background:linear-gradient(180deg,rgba(254,255,255,.98),rgba(249,253,255,.94));
    }

    #gsf-page-chrome-v250 .gsf-page-head{
      position:absolute;
      left:clamp(14px,2vw,30px);
      right:clamp(14px,2vw,30px);
      top:0;
      height:var(--gsf-shell-top);
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:12px;
      pointer-events:none;
    }
    #gsf-page-chrome-v250 .gsf-page-brand{
      color:#6C81A1;
      font-size:clamp(9px,.75vw,12px);
      line-height:1;
      font-weight:850;
      letter-spacing:.25em;
      white-space:nowrap;
    }
    #gsf-page-chrome-v250 .gsf-page-account{
      pointer-events:auto;
      min-height:28px;
      max-width:190px;
      padding:4px 10px;
      display:flex;
      align-items:center;
      justify-content:center;
      gap:6px;
      border:1px solid rgba(145,181,214,.28);
      border-radius:999px;
      background:rgba(255,255,255,.88);
      color:#637DA8;
      box-shadow:0 7px 20px rgba(63,108,151,.08);
      font-size:9px;
      font-weight:800;
      cursor:pointer;
    }

    #gsf-page-chrome-v250 .gsf-page-ad{
      position:absolute;
      top:50%;
      transform:translateY(-50%);
      width:var(--gsf-shell-ad-w);
      height:clamp(300px,43vh,430px);
      box-sizing:border-box;
      display:flex;
      align-items:center;
      justify-content:center;
      padding:10px;
      border:1px solid rgba(150,184,214,.22);
      border-radius:20px;
      background:rgba(255,255,255,.72);
      box-shadow:0 12px 34px rgba(59,104,148,.07),inset 0 1px 0 rgba(255,255,255,.94);
      color:#7D90AD;
      font-size:clamp(8px,.65vw,10px);
      font-weight:750;
      letter-spacing:.04em;
      text-align:center;
    }
    #gsf-page-chrome-v250 .gsf-page-ad.left{left:clamp(12px,1.35vw,24px)}
    #gsf-page-chrome-v250 .gsf-page-ad.right{right:clamp(12px,1.35vw,24px)}

    /* V249 page Game Bar, rescaled to match Home across desktop sizes. */
    #gsf-page-nav-v249{
      width:min(760px,72vw)!important;
      height:clamp(52px,6.8vh,60px)!important;
      min-height:clamp(52px,6.8vh,60px)!important;
      bottom:clamp(7px,1vh,10px)!important;
      padding:4px 10px!important;
      background:rgba(255,255,255,.93)!important;
      border:1px solid rgba(139,181,218,.30)!important;
      box-shadow:0 10px 28px rgba(59,104,148,.11),0 0 0 4px rgba(226,243,255,.30),inset 0 1px 0 #fff!important;
    }
    #gsf-page-nav-v249 .gsf-page-nav-item{
      font-size:clamp(7.5px,.62vw,8.5px)!important;
    }
    #gsf-page-nav-v249 .gsf-page-nav-item svg{
      width:clamp(17px,2.35vh,21px)!important;
      height:clamp(17px,2.35vh,21px)!important;
    }

    /* Short laptops: keep ad rails useful without squeezing the content. */
    @media(min-width:1000px) and (max-height:720px){
      :root{
        --gsf-shell-top:40px;
        --gsf-shell-bottom:68px;
        --gsf-shell-ad-w:clamp(104px,8.5vw,134px);
        --gsf-shell-side:calc(var(--gsf-shell-ad-w) + 16px);
      }
      #gsf-page-chrome-v250 .gsf-page-ad{
        height:clamp(240px,38vh,320px);
      }
      #gsf-page-nav-v249{
        height:48px!important;
        min-height:48px!important;
      }
    }

    /* Compact landscape/tablet: preserve page space; ad rails collapse first. */
    @media(min-width:761px) and (max-width:999px){
      :root{
        --gsf-shell-top:40px;
        --gsf-shell-bottom:70px;
        --gsf-shell-side:14px;
      }
      #gsf-page-chrome-v250 .gsf-page-ad{display:none}
      #gsf-page-nav-v249{width:calc(100vw - 28px)!important}
    }

    /* Mobile pages keep the same approved Home language, without side rails. */
    @media(max-width:760px){
      :root{
        --gsf-shell-top:34px;
        --gsf-shell-bottom:70px;
        --gsf-shell-side:8px;
      }
      #gsf-social-overlay-v159,
      #gsf-creator-hub-live-v160,
      #gsf-editor-overlay-v220,
      #gsf-ai-overlay-v221,
      #gsf-account-overlay-v223{
        padding:
          var(--gsf-shell-top)
          var(--gsf-shell-side)
          var(--gsf-shell-bottom)!important;
      }
      #gsf-page-chrome-v250 .gsf-page-head{
        left:10px;right:10px;height:34px;
      }
      #gsf-page-chrome-v250 .gsf-page-brand{
        font-size:8px;
        letter-spacing:.22em;
      }
      #gsf-page-chrome-v250 .gsf-page-account{
        min-height:25px;
        padding:3px 8px;
        font-size:8px;
      }
      #gsf-page-chrome-v250 .gsf-page-ad{display:none}
      /* GSF_MOBILE_SURFACE_FIT: the V343 shell owns the header, Game Bar and footer on phones.
         The V250 per-page top bar showed through the shell header, and every surface was
         viewport-tall but started 32px down, so its last 32px fell below the screen. */
      .gsf-page-top-v250,.gsf-page-footer-v250,.gsf-page-ad-v250,#gsf-page-chrome-v250{display:none!important}
      #gsf-social-overlay-v159 .gsf-social-shell,
      #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
      #gsf-ai-overlay-v221 .gsf-ai-shell,
      #gsf-account-overlay-v223 .gsf-account-shell{
        left:0!important;right:0!important;width:auto!important;
        bottom:0!important;height:auto!important;
      }
      /* The Game Editor has no bottom reserve of its own: it sits between the header and the Game Bar. */
      #gsf-editor-overlay-v220 .gsf-editor-shell{
        left:0!important;right:0!important;width:auto!important;
        top:var(--gsf-shell-content-top,44px)!important;
        bottom:var(--gsf-shell-content-bottom,112px)!important;height:auto!important;
      }
      #gsf-editor-overlay-v220 .gsf-editor-body{top:0!important}
      #gsf-page-nav-v249{
        width:calc(100vw - 24px)!important;
        height:58px!important;
        min-height:58px!important;
        bottom:6px!important;
        padding:4px 8px!important;
      }
      #gsf-page-nav-v249 .gsf-page-nav-item{font-size:7px!important}
      #gsf-page-nav-v249 .gsf-page-nav-item svg{width:18px!important;height:18px!important}
    }

    @media(prefers-reduced-motion:reduce){
      #gsf-social-overlay-v159 .gsf-social-shell,
      #gsf-creator-hub-live-v160 .gsf-hub-shell-v160,
      #gsf-editor-overlay-v220 .gsf-editor-shell,
      #gsf-ai-overlay-v221 .gsf-ai-shell,
      #gsf-account-overlay-v223 .gsf-account-shell{
        transition:none!important;
        transform:none!important;
      }
    }
    </style>

    <div id="gsf-page-chrome-v250" aria-hidden="true">
      <header class="gsf-page-head">
        <div class="gsf-page-brand">GAMING SHORTS FACTORY</div>
        <button class="gsf-page-account" type="button" aria-label="Apri account">Accedi</button>
      </header>
      <aside class="gsf-page-ad left"><span>Spazio pubblicitario</span></aside>
      <aside class="gsf-page-ad right"><span>Spazio pubblicitario</span></aside>
    </div>
    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    components.html(r"""<!-- V343 chrome and GSFNavigation replace the V249/V250 controllers. -->""", height=0, scrolling=False)

if GSF_WEB_MODE:
    import streamlit.components.v1 as components
    components.html('<!-- Retired competing surface router: GSFNavigation owns transitions. -->',height=0,scrolling=False)

if GSF_WEB_MODE:
    import streamlit.components.v1 as components
    _GSF_PARENT_NOTIFICATIONS = r"""<!doctype html><html><body style="margin:0;display:none"><script>
    ((P)=>{
      const d=P.document;
      const bridge=P.GSFNavigation.bridge('notifications',null);
      const _gsfLifecycleCompat=['Upload completato']; // legacy build token; never rendered

      const ensurePush=()=>{
        if(P.GSFNotify)return Promise.resolve(true);
        return new Promise((resolve)=>{
          let s=d.getElementById('gsf-global-push-client-v258');
          if(s){
            if(P.GSFNotify)return resolve(true);
            s.addEventListener('load',()=>resolve(!!P.GSFNotify),{once:true});
            setTimeout(()=>resolve(!!P.GSFNotify),900);
            return;
          }
          s=d.createElement('script');
          s.id='gsf-global-push-client-v258';
          s.src='/gsf-push.js?v=258';
          s.async=true;
          s.onload=()=>resolve(!!P.GSFNotify);
          s.onerror=()=>resolve(false);
          d.head.appendChild(s);
        });
      };

      let startupReady=false;
      const homeReady=()=>[...d.querySelectorAll('iframe')].some(f=>{try{return !!f.contentWindow.__GSF_V333_CTA_TOUCH&&!!f.contentDocument.querySelector('#home154')}catch(_e){return false}});
      const finishStartup=()=>{startupReady=true;P.GSFNotify?.dismiss('alive:startup')};
      P.addEventListener('message',e=>{
        if(e.origin!==P.location.origin||e.data?.type!=='GSF_HOME_READY')return;
        const home=[...d.querySelectorAll('iframe')].find(f=>f.contentWindow===e.source);
        try{if(home?.contentWindow.__GSF_V333_CTA_TOUCH&&home.contentDocument.querySelector('#home154'))finishStartup()}catch(_e){}
      },{signal:bridge.signal});
      P.addEventListener('gsf:surfacechange',()=>{if(P.GSFNavigation.snapshot().target!=='home')finishStartup()},{signal:bridge.signal});

      // V258: replacement upload is owned by the Home uploader itself.
      // Existing global notifications remain available from every page.
      P.addEventListener('message',(e)=>{
        const data=e.data||{};
        if(data.type==='GSF_NOTIFY'&&P.GSFNotify){
          P.GSFNotify.show(
            String(data.title||'Gaming Shorts Factory'),
            String(data.body||''),
            String(data.kind||'success')
          );
        }
      },{signal:bridge.signal});

      // Re-enable silent Web Push when permission already exists.
      ensurePush().then(()=>{
        if(P.GSFNavigation.snapshot().target==='home'&&!startupReady&&!homeReady()){
          P.GSFNotify?.upsert('alive:startup',{title:'Avvio GSF',body:'Preparo il tuo spazio.',kind:'working',ttl:0});
          bridge.timeout(()=>{if(!startupReady&&!homeReady()&&P.GSFNavigation.snapshot().target==='home')P.GSFNotify?.upsert('alive:startup',{title:'Avvio non completato',body:'La Home non ha ancora risposto.',kind:'warning',ttl:0,actionLabel:'Riprova',onClick:()=>P.location.reload()})},60000);
        }

        try{P.GSFPush&&P.GSFPush.ensure&&P.GSFPush.ensure().catch(()=>{})}catch(_e){}
      });
    })(window.parent);
    </script></body></html>"""

if GSF_WEB_MODE:
    st.markdown(r"""
    <style id="gsf-v281-gamebar-return-type">
      #gsf-social-overlay-v159,
      #gsf-creator-hub-live-v160,
      #gsf-editor-overlay-v220,
      #gsf-ai-overlay-v221,
      #gsf-account-overlay-v223{
        z-index:2147483500!important;
      }
      #gsf-page-chrome-v250{
        z-index:2147483550!important;
      }
      #gsf-page-nav-v249{
        z-index:2147483646!important;
      }
      #gsf-page-nav-v249.is-open{
        opacity:1!important;
        visibility:visible!important;
        pointer-events:auto!important;
      }
      #gsf-page-nav-v249 .gsf-page-nav-item{
        font-size:clamp(11px,.78vw,13px)!important;
      }
      @media(max-width:760px){
        #gsf-page-nav-v249 .gsf-page-nav-item{
          font-size:9.5px!important;
        }
      }
    </style>
    """, unsafe_allow_html=True)


# GSF_GLOBAL_SHELL_V343 — the only parent-owned header, Game Bar, footer and shell router.
if GSF_WEB_MODE:
    _GSF_PARENT_SHELL = r"""    <div style="display:none!important"><script>
    ((P)=>{
      const D=P.document;
      const SHELL_Z=2147483600;
      const OVERLAY_Z=2147483400;
      const SURFACES=['gsf-social-overlay-v159','gsf-creator-hub-live-v160','gsf-editor-overlay-v220','gsf-ai-overlay-v221','gsf-account-overlay-v223','gsf-short-overlay-v343'];

      const ensureStyle=()=>{
        // iOS must extend the shared dark document canvas into the safe areas.
        // Preserve Streamlit's viewport settings and update the TOP document,
        // since viewport-fit on the Editor iframe cannot affect the device.
        let viewport=D.querySelector('meta[name="viewport"]');
        if(!viewport){viewport=D.createElement('meta');viewport.name='viewport';viewport.content='width=device-width,initial-scale=1';D.head.appendChild(viewport)}
        if(!/(?:^|,)\s*viewport-fit\s*=\s*cover\s*(?:,|$)/i.test(viewport.content)){
          viewport.content=viewport.content.replace(/(?:^|,)\s*viewport-fit\s*=[^,]*/ig,'')+',viewport-fit=cover';
        }
        let s=D.getElementById('gsf-global-shell-v343-style');
        if(s)return s;
        s=D.createElement('style');s.id='gsf-global-shell-v343-style';
        s.textContent=`
          /* Streamlit mounts its chrome after this shell; never flash it above GSF. */
          html body [data-testid="stHeader"],html body [data-testid="stToolbar"],
          html body [data-testid="stStatusWidget"],html body [data-testid="stDecoration"]{display:none!important}
          :root{
            --gsf-shell-header-h:44px;
            --gsf-shell-gamebar-h:62px;
            --gsf-shell-footer-h:30px;
            --gsf-shell-safe-top:max(0px,env(safe-area-inset-top));
            --gsf-shell-safe-bottom:max(8px,env(safe-area-inset-bottom));
            --gsf-shell-content-top:calc(var(--gsf-shell-header-h) + var(--gsf-shell-safe-top));
            --gsf-shell-content-bottom:calc(var(--gsf-shell-gamebar-h) + var(--gsf-shell-footer-h) + var(--gsf-shell-safe-bottom) + 12px);
            --gsf-shell-z:2147483600;
            --gsf-shell-overlay-z:2147483400;
          }
          #gsf-v328-global-footer,#gsf-v330-global-brand,#gsf-v330-global-footer,#gsf-page-nav-v249,[id^="gsf-page-nav"],#gsf-v334-header,#gsf-v334-gamebar,#gsf-v334-footer{display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important}
          #gsf-global-header{position:fixed!important;left:0!important;right:0!important;top:0!important;height:var(--gsf-shell-content-top)!important;z-index:var(--gsf-shell-z)!important;display:flex!important;align-items:flex-end!important;justify-content:space-between!important;padding:var(--gsf-shell-safe-top) max(16px,env(safe-area-inset-right)) 7px max(16px,env(safe-area-inset-left))!important;box-sizing:border-box!important;background:linear-gradient(180deg,rgba(250,253,255,.99),rgba(250,253,255,.91))!important;border-bottom:1px solid rgba(150,184,214,.16)!important;-webkit-backdrop-filter:blur(18px)!important;backdrop-filter:blur(18px)!important;color:#617b9f!important}
          #gsf-global-header .v343Brand{display:flex;align-items:center;gap:7px;min-width:0;font:800 10px/1 "Avenir Next","SF Pro Display",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:.22em;text-transform:uppercase;white-space:nowrap}
          #gsf-global-header .v343Logo{width:18px;height:22px;object-fit:contain;display:block;flex:0 0 18px}
          #gsf-global-header .v343Account{height:30px;min-width:64px;display:flex;align-items:center;gap:6px;padding:2px 9px 2px 4px;border:1px solid rgba(150,184,214,.28);border-radius:999px;background:rgba(255,255,255,.95);color:#60789c;font:800 9px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;box-shadow:0 7px 19px rgba(68,104,142,.08)}
          #gsf-global-header .v343Avatar{width:24px;height:24px;border-radius:50%;display:grid;place-items:center;overflow:hidden;background:linear-gradient(145deg,#e7f4ff,#e9f8f2);font-size:9px}
          #gsf-global-header .v343Avatar img{width:100%;height:100%;display:block;object-fit:cover}
          #gsf-global-gamebar{position:fixed!important;left:max(18px,env(safe-area-inset-left))!important;right:max(18px,env(safe-area-inset-right))!important;bottom:calc(var(--gsf-shell-footer-h) + var(--gsf-shell-safe-bottom) + 6px)!important;height:var(--gsf-shell-gamebar-h)!important;z-index:var(--gsf-shell-z)!important;display:grid!important;grid-template-columns:repeat(4,1fr)!important;gap:3px!important;padding:6px 8px!important;border:1px solid rgba(145,181,213,.28)!important;border-radius:999px!important;background:rgba(255,255,255,.96)!important;-webkit-backdrop-filter:blur(22px)!important;backdrop-filter:blur(22px)!important;box-shadow:0 12px 34px rgba(59,104,148,.12),inset 0 1px 0 #fff!important;box-sizing:border-box!important}
          #gsf-global-gamebar button{border:0;background:transparent;border-radius:999px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;color:#7f8fa8;font:800 7px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:2px;min-width:0}
          #gsf-global-gamebar button.active{color:#4f93d7;background:rgba(219,241,255,.72)}
          #gsf-global-gamebar .v343Icon{width:29px;height:29px;border-radius:50%;display:grid;place-items:center;background:linear-gradient(145deg,#F9FCFF,#EDF5FC);border:1px solid rgba(150,184,215,.24);font-size:14px}
          #gsf-global-footer{position:fixed!important;left:0!important;right:0!important;bottom:0!important;height:calc(var(--gsf-shell-footer-h) + var(--gsf-shell-safe-bottom))!important;z-index:var(--gsf-shell-z)!important;display:grid!important;grid-template-columns:1fr auto 1fr!important;align-items:start!important;padding:5px max(12px,env(safe-area-inset-right)) var(--gsf-shell-safe-bottom) max(12px,env(safe-area-inset-left))!important;box-sizing:border-box!important;border-top:1px solid rgba(150,184,214,.20)!important;background:rgba(250,253,255,.97)!important;-webkit-backdrop-filter:blur(18px)!important;backdrop-filter:blur(18px)!important;color:#6e88aa!important}
          #gsf-global-footer .v343Socials{grid-column:2;display:flex;align-items:center;justify-content:center;gap:7px}
          #gsf-global-footer .v343Socials a,#gsf-global-footer .v343Socials span{width:17px;height:17px;display:grid;place-items:center;border-radius:50%;text-decoration:none;border:1px solid rgba(150,183,213,.22);background:#fff;color:#7388a7;font:900 7px/1 sans-serif;overflow:hidden;box-sizing:border-box}
          #gsf-global-footer .v343Bug{grid-column:3;justify-self:end;border:0;background:transparent;color:#6983a4;font:800 7px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:3px 0;white-space:nowrap}
          #gsf-editor-overlay-v220,#gsf-short-overlay-v343,#gsf-creator-hub-live-v160,#gsf-ai-overlay-v221,#gsf-social-overlay-v159,#gsf-account-overlay-v223{position:fixed!important;left:0!important;right:0!important;top:var(--gsf-shell-content-top)!important;bottom:var(--gsf-shell-content-bottom)!important;height:auto!important;max-height:none!important;z-index:var(--gsf-shell-overlay-z)!important;box-sizing:border-box!important}
          #gsf-editor-overlay-v220 .gsf-editor-shell,#gsf-creator-hub-live-v160 .gsf-hub-shell-v160,#gsf-ai-overlay-v221 .gsf-ai-shell,#gsf-social-overlay-v159 .gsf-social-shell,#gsf-account-overlay-v223 .gsf-account-shell{position:absolute!important;inset:0!important;min-height:0!important;max-height:none!important}
          /* Canonical frame geometry exists before transient Streamlit styles/bootstrap. */
          #gsf-social-overlay-v159 iframe,#gsf-creator-hub-live-v160 iframe,#gsf-editor-overlay-v220 iframe,#gsf-ai-overlay-v221 iframe,#gsf-account-overlay-v223 iframe{display:block!important;width:100%!important;height:100%!important;min-width:0!important;max-width:100%!important;min-height:0!important;border:0!important;box-sizing:border-box!important;background:#050D16!important}
          #gsf-social-overlay-v159 .gsf-social-shell,#gsf-creator-hub-live-v160 .gsf-hub-shell-v160,#gsf-editor-overlay-v220 .gsf-editor-shell,#gsf-ai-overlay-v221 .gsf-ai-shell,#gsf-account-overlay-v223 .gsf-account-shell{width:100%!important;height:100%!important;max-width:none!important;box-sizing:border-box!important}
          #gsf-short-overlay-v343{display:flex;align-items:center;justify-content:center;padding:8px;background:#050D16;opacity:0;visibility:hidden;pointer-events:none;transition:opacity .18s ease,visibility .18s ease}
          #gsf-short-overlay-v343.is-open{opacity:1;visibility:visible;pointer-events:auto}
          #gsf-short-overlay-v343 .v343ShortShell{position:relative;width:min(680px,calc(100vw - 20px));height:100%;min-height:0;display:grid;grid-template-rows:auto 1fr auto;gap:9px;border:1px solid rgba(150,184,214,.24);border-radius:22px;background:rgba(255,255,255,.90);box-shadow:0 22px 58px rgba(49,94,135,.12);overflow:hidden;padding:12px;box-sizing:border-box}
          #gsf-short-overlay-v343 .v343ShortHead{display:flex;align-items:flex-start;justify-content:space-between;gap:10px} #gsf-short-overlay-v343 h2{margin:0;color:#0D2A66;font:900 21px/1.05 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif} #gsf-short-overlay-v343 p{margin:4px 0 0;color:#7185A6;font:700 10px/1.25 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
          #gsf-short-overlay-v343 .v343ShortStage{min-height:0;display:flex;align-items:center;justify-content:center;overflow:hidden}.v343Preview{position:relative;height:min(100%,450px);aspect-ratio:9/16;max-width:76%;border-radius:20px;border:1px solid rgba(112,187,230,.30);overflow:hidden;background:linear-gradient(155deg,#EFF8FF,#F7FFFC);display:grid;place-items:center;color:#6F88A8;text-align:center;padding:18px}.v343Preview video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;background:#000}.v343PreviewText{font:800 11px/1.25 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.v343Actions{display:grid;grid-template-columns:1.15fr 1fr 1fr;gap:7px}.v343Actions button,.v343ShortClose{min-height:42px;border-radius:13px;border:1px solid rgba(146,182,213,.26);background:#F7FBFF;color:#56718F;font:900 9px/1.1 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.v343Actions .primary{background:#DDEFFF;color:#136FCF}.v343ShortClose{width:32px;min-height:32px;height:32px;font-size:20px}.v343Status{position:absolute;left:14px;right:14px;bottom:60px;text-align:center;color:#6E86A5;font:800 9px/1.2 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;pointer-events:none}
          @media(min-width:761px){#gsf-global-gamebar{left:50%!important;right:auto!important;width:min(560px,52vw)!important;transform:translateX(-50%)!important}}
        `;
        (D.head||D.documentElement).appendChild(s);return s;
      };

      const markup={
        header:`<header id="gsf-global-header" aria-label="Gaming Shorts Factory"><div class="v343Brand"><span class="naWordmark">GAMING <b>SHORTS</b> FACTORY</span></div><button class="v343Account" type="button"><span class="v343Avatar"><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg></span><span class="v343AccountName">Accedi</span></button></header>`,
        gamebar:`<nav id="gsf-global-gamebar" aria-label="Game Bar"><button data-page="home" class="active" type="button"><span class="v343Icon"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M4 14 16 4l12 10"/><path d="M7 13v14h18V13"/><path d="M13 27v-8h6v8"/></svg></span><span>Home</span></button><button data-page="hub" type="button"><span class="v343Icon"><svg viewBox="0 0 32 32" aria-hidden="true"><rect x="5" y="5" width="8" height="8" rx="2"/><rect x="19" y="5" width="8" height="8" rx="2"/><rect x="5" y="19" width="8" height="8" rx="2"/><rect x="19" y="19" width="8" height="8" rx="2"/></svg></span><span>Hub</span></button><button data-page="projects" type="button"><span class="v343Icon"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M4 10h9l3 3h12v14H4Z"/><path d="M4 10V7h10l3 3"/></svg></span><span>Progetti</span></button><button data-page="live" type="button"><span class="v343Icon"><svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="3"/><path d="M10.5 10.5a8 8 0 0 0 0 11M21.5 10.5a8 8 0 0 1 0 11"/><path d="M6.5 6.5a13.5 13.5 0 0 0 0 19M25.5 6.5a13.5 13.5 0 0 1 0 19"/></svg></span><span>Live</span></button></nav>`,
        footer:`<footer id="gsf-global-footer" aria-label="Footer"><div class="v343Socials"><a href="https://www.facebook.com/profile.php?id=61595124112318&locale=it_IT" target="_blank" rel="noopener noreferrer" aria-label="Facebook">f</a><a href="https://www.instagram.com/gamingshortsfactory/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">◎</a><a href="https://www.youtube.com/@Dans222nrg" target="_blank" rel="noopener noreferrer" aria-label="YouTube">▶</a><span aria-label="TikTok">♪</span><span aria-label="Twitch">◫</span></div><button class="v343Bug" type="button">Segnala bug</button></footer>`
      };
      const mount=(id,html)=>{let n=D.getElementById(id);if(n)return n;D.body.insertAdjacentHTML('beforeend',html);return D.getElementById(id)};
      const hide=(o)=>{if(!o)return;o.classList.remove('is-open');o.style.opacity='0';o.style.visibility='hidden';o.style.pointerEvents='none';o.setAttribute('aria-hidden','true')};
      const show=(o)=>{if(!o)return false;o.classList.add('is-open');o.style.opacity='1';o.style.visibility='visible';o.style.pointerEvents='auto';o.setAttribute('aria-hidden','false');return true};
      const closeCompeting=(keep='')=>SURFACES.forEach(id=>{if(id!==keep)hide(D.getElementById(id))});
      const active=(page)=>{const b=D.getElementById('gsf-global-gamebar');if(!b)return;b.querySelectorAll('button').forEach(x=>x.classList.toggle('active',x.dataset.page===page))};

      const ensureHubSurface=()=>{
        let o=D.getElementById('gsf-creator-hub-live-v160');
        if(!o){o=D.createElement('section');o.id='gsf-creator-hub-live-v160';o.setAttribute('aria-hidden','true');o.innerHTML=`<div class="gsf-hub-shell-v160"><iframe class="gsf-hub-frame" title="Creator Hub" data-src="/creator-hub-v156/" style="width:100%;height:100%;display:block;border:0;background:#F8FCFF"></iframe></div>`;D.body.appendChild(o)}
        const f=o.querySelector('iframe');if(f&&f.dataset.loaded!=='1'){f.contentWindow.location.replace('/creator-hub-v156/?v=343');f.dataset.loaded='1'}return o;
      };
      const focusHub=(section)=>{const o=ensureHubSurface();show(o);const f=o.querySelector('iframe');f.dataset.gsfSection=section;const send=()=>{try{f?.contentWindow?.postMessage({type:'GSF_HUB_FOCUS',section:f.dataset.gsfSection||'dashboard',epoch:P.GSFNavigation.snapshot().epoch},P.location.origin)}catch(_e){}};send();if(f&&f.dataset.v343Focus!=='1'){f.dataset.v343Focus='1';f.addEventListener('load',send)}return true};

      const ensureShortSurface=()=>{
        let o=D.getElementById('gsf-short-overlay-v343');if(o)return o;
        o=D.createElement('section');o.id='gsf-short-overlay-v343';o.setAttribute('aria-hidden','true');o.innerHTML=`<div class="v343ShortShell" role="dialog" aria-modal="false" aria-label="Crea Short"><div class="v343ShortHead"><div><h2>Crea Short</h2><p>La tua scelta finale resta nel progetto finché non decidi di crearla.</p></div><button class="v343ShortClose" type="button" aria-label="Chiudi">×</button></div><div class="v343ShortStage"><div class="v343Preview"><div class="v343PreviewText">ANTEPRIMA 9:16</div><video playsinline controls preload="metadata" hidden></video></div></div><div class="v343Actions"><button class="primary v343Create" type="button">CREA SHORT</button><button class="v343Editor" type="button">GAME EDITOR</button><button class="v343Draft" type="button">SALVA BOZZA</button></div><div class="v343Status" aria-live="polite"></div></div>`;D.body.appendChild(o);
        const status=o.querySelector('.v343Status');const say=t=>{if(status)status.textContent=String(t||'')};
        o.querySelector('.v343ShortClose')?.addEventListener('click',()=>route({target:'home'}));
        o.querySelector('.v343Editor')?.addEventListener('click',()=>route({target:'editor'}));
        o.querySelector('.v343Create')?.addEventListener('click',()=>{let b=D.querySelector('.st-key-gsf-major-create-short button,.st-key-create_final_short_v54 button');if(!b)b=[...D.querySelectorAll('button,[role="button"]')].find(x=>{const t=String(x.innerText||x.textContent||'').trim().toLowerCase();return t==='crea short'||t.includes('crea short finale')||t.includes('crea il tuo short')});if(!b){say('Carica un gameplay prima di creare lo Short.');return}if(b.disabled||b.getAttribute('aria-disabled')==='true'){say('Il gameplay non è ancora pronto per il render.');return}say('Creazione Short…');b.click()});
        o.querySelector('.v343Draft')?.addEventListener('click',async()=>{say('Salvataggio…');try{const state=await P.fetch('/creator-hub/state?scope=header',{credentials:'same-origin'}).then(r=>r.json());const r=await P.fetch('/drafts/save-current',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-GSF-CSRF':String(state.csrf_token||'')},body:'{}'});const j=await r.json().catch(()=>({}));say(r.ok&&j&&j.ok?'Bozza salvata.':(j&&j.error)||'Nessuna modifica da salvare.')}catch(_e){say('Salvataggio non riuscito. Riprova.')}});
        const v=o.querySelector('video');if(v){v.src='/editor-media/current?v=343';v.addEventListener('loadedmetadata',()=>{v.hidden=false;const t=o.querySelector('.v343PreviewText');if(t)t.style.display='none'},{once:true});v.addEventListener('error',()=>{v.hidden=true},{once:true})}
        return o;
      };
      const openShort=()=>{const o=ensureShortSurface();show(o);return true};

      const openExisting=(id)=>{const o=D.getElementById(id);if(!o)return false;closeCompeting(id);return show(o)};
      const route=data=>P.GSFNavigation.navigate(data);

      const syncAccount=()=>P.fetch('/creator-hub/state?scope=header',{cache:'no-store',credentials:'same-origin'}).then(r=>r.json()).then(j=>{const a=(j&&j.account)||{};const name=String(a.display_name||a.nickname||a.name||a.username||String(a.email||'').split('@')[0]||'Accedi');const photo=String(a.photo||a.avatar||a.image||a.picture||'');const h=D.getElementById('gsf-global-header');if(!h)return;h.querySelector('.v343AccountName').textContent=name;const av=h.querySelector('.v343Avatar');if(photo)av.innerHTML='<img alt="" src="'+photo.replace(/"/g,'&quot;')+'">';else name==='Accedi'?(av.innerHTML='<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg>'):(av.textContent=name.slice(0,1).toUpperCase()||'G')}).catch(()=>{});
      const syncSocials=()=>{const f=D.getElementById('gsf-global-footer');const dst=f?.querySelector('.v343Socials');if(!dst)return;try{const hf=[...D.querySelectorAll('iframe')].find(x=>String(x.title||x.src||'').includes('home_v154'));const src=hf?.contentDocument?.querySelector('.footerSocial');if(src&&src.children.length)dst.innerHTML=src.innerHTML}catch(_e){}};
      const suppressChildChrome=(doc)=>{try{if(!doc||!doc.documentElement)return;if(doc.getElementById('home154')){doc.documentElement.classList.add('gsf-v343-parent-ready');return}let s=doc.getElementById('gsf-v343-child-chrome-lock');if(!s){s=doc.createElement('style');s.id='gsf-v343-child-chrome-lock';s.textContent=`.bottomNav,.siteFooter,[id^="gsf-page-nav"],[data-global-gamebar],.footerBrand{display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important}.brandOnly,.brandText{display:none!important}`;(doc.head||doc.documentElement).appendChild(s)}}catch(_e){}};
      const syncChildren=()=>D.querySelectorAll('iframe').forEach(f=>{const apply=()=>{try{suppressChildChrome(f.contentDocument)}catch(_e){}};apply();if(f.dataset.v343Chrome!=='1'){f.dataset.v343Chrome='1';f.addEventListener('load',apply,{passive:true})}});

      const NA_SHELL_CSS='/* GSF_NIGHT_ARENA_SHELL — header, Game Bar and surfaces on the single Night Arena look.\n   The old footer is gone (its links live in Creator Hub › Impostazioni › Info). */\nhtml:root{--gsf-shell-footer-h:0px;--gsf-shell-gamebar-h:66px;color-scheme:dark}\nhtml:root,html:root body{background:#050D16!important}\nhtml body .stApp,html body [data-testid="stAppViewContainer"],html body [data-testid="stHeader"],html body [data-testid="stMain"],html body [data-testid="stMainBlockContainer"],html body [data-testid="stBottom"],html body [data-testid="stBottomBlockContainer"]{background:#050D16!important}\nhtml body #gsf-global-footer{display:none!important}\nhtml body #gsf-global-header{\n background:linear-gradient(180deg,rgba(5,13,22,.92),rgba(5,13,22,.72))!important;\n border-bottom:1px solid rgba(121,210,255,.14)!important;color:#EAF6FF!important;\n}\nhtml body #gsf-global-header .v343Brand{color:#FFFFFF!important;letter-spacing:.2em!important}\nhtml body #gsf-global-header .v343Account{background:rgba(255,255,255,.06)!important;border:1px solid rgba(121,210,255,.25)!important;color:#EAF6FF!important}\nhtml body #gsf-global-header .v343Avatar{background:linear-gradient(135deg,#27AEF3,#9D82FF)!important;color:#fff!important}\nhtml body #gsf-global-gamebar{\n bottom:calc(var(--gsf-shell-safe-bottom) + 10px)!important;\n border:1px solid rgba(121,210,255,.22)!important;border-radius:30px!important;\n background:rgba(16,40,61,.66)!important;\n box-shadow:0 18px 40px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.08)!important;\n -webkit-backdrop-filter:blur(22px) saturate(1.2)!important;backdrop-filter:blur(22px) saturate(1.2)!important;\n}\nhtml body #gsf-global-gamebar button{color:#9FB7CA!important;background:transparent!important;border:0!important;border-radius:22px!important;font-weight:700!important;font-size:11px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:3px!important}\nhtml body #gsf-global-gamebar button.active{color:#FFFFFF!important;background:rgba(39,174,243,.2)!important;box-shadow:0 0 22px rgba(39,174,243,.35)!important;font-weight:800!important}\nhtml body #gsf-global-gamebar .v343Icon{display:grid!important;place-items:center!important;width:24px!important;height:24px!important;background:none!important;border:0!important;box-shadow:none!important}\nhtml body #gsf-global-gamebar .v343Icon svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}\nhtml body #gsf-global-gamebar button.active .v343Icon{color:#79D2FF!important}\nhtml body #gsf-social-overlay-v159,html body #gsf-creator-hub-live-v160,html body #gsf-editor-overlay-v220,html body #gsf-ai-overlay-v221,html body #gsf-account-overlay-v223{background:#050D16!important}\nhtml body #gsf-social-overlay-v159 iframe,html body #gsf-creator-hub-live-v160 iframe,html body #gsf-editor-overlay-v220 iframe,html body #gsf-ai-overlay-v221 iframe{background:#050D16!important}\nhtml body #gsf-global-header .v343Brand img{display:none!important}\nhtml body #gsf-global-header .naWordmark{font-weight:800!important;font-size:12px!important;letter-spacing:.24em!important;color:#FFFFFF!important;white-space:nowrap}\nhtml body #gsf-global-header .naWordmark b{font-weight:800;color:#79D2FF}\n@keyframes naReveal{from{clip-path:circle(0 at var(--na-ox,50%) var(--na-oy,50%))}to{clip-path:circle(150% at var(--na-ox,50%) var(--na-oy,50%))}}\n@keyframes naRevealRing{0%{opacity:.9;box-shadow:inset 0 0 0 2px var(--na-oc,#27AEF3)}100%{opacity:0;box-shadow:inset 0 0 0 0 transparent}}\nhtml body .na-reveal{animation:naReveal .55s cubic-bezier(.22,1.2,.36,1) both!important}';
      const ensureNightArena=()=>{let n=D.getElementById('gsf-night-arena-shell');if(!n){n=D.createElement('style');n.id='gsf-night-arena-shell';n.textContent=NA_SHELL_CSS}if(D.head.lastElementChild!==n)D.head.appendChild(n);D.documentElement.style.colorScheme='dark';return n};
      function keepGlobalShellMounted(){
        ensureStyle();ensureNightArena();
        const header=mount('gsf-global-header',markup.header);const bar=mount('gsf-global-gamebar',markup.gamebar);const footer=mount('gsf-global-footer',markup.footer);
        if(header&&header.dataset.v343Bound!=='1'){header.dataset.v343Bound='1';header.querySelector('.v343Account')?.addEventListener('click',()=>route({target:'hub',section:'profile'}))}
        if(bar&&bar.dataset.v343Bound!=='1'){bar.dataset.v343Bound='1';bar.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>route({target:b.dataset.page,section:b.dataset.page==='hub'?'dashboard':''})))}
        if(footer&&footer.dataset.v343Bound!=='1'){footer.dataset.v343Bound='1';footer.querySelector('.v343Bug')?.addEventListener('click',()=>{const hit=[...D.querySelectorAll('button,a,[role="button"]')].find(x=>x!==footer.querySelector('.v343Bug')&&String(x.textContent||'').trim().toLowerCase().includes('segnala bug'));if(hit)hit.click()})}
        syncChildren();P.GSFNavigation.reconcile();return !!(header&&bar&&footer);
      }

      if(!P.__GSF_GLOBAL_SHELL_V343){
        P.__GSF_GLOBAL_SHELL_V343=true;
        keepGlobalShellMounted();syncAccount();syncSocials();
        P.addEventListener('gsf:profile-updated',syncAccount);
        P.GSFNavigation.registerSurface('hub',{open:data=>focusHub(data.section||'dashboard'),close:()=>hide(D.getElementById('gsf-creator-hub-live-v160'))});
        P.GSFNavigation.registerSurface('short',{open:openShort,close:()=>hide(D.getElementById('gsf-short-overlay-v343'))});
        const observer=new P.MutationObserver(()=>keepGlobalShellMounted());observer.observe(D.documentElement,{childList:true,subtree:true});

      }else keepGlobalShellMounted();
      try{P.postMessage({type:'GSF_V343_SHELL_READY'},P.location.origin)}catch(_e){}
    })(window.parent);
    </script></div>
"""



# GSF_V348_TRANSPARENT_LOGO_FOOTER
import streamlit.components.v1 as _gsf_components_v348
_GSF_PARENT_FOOTER348 = r"""
<script id="gsf-v348-logo-footer">
(() => {
  const P=window.parent, D=P.document;
  const lifecycle=P.GSFNavigation.bridge('footer348',globalThis.frameElement);
  const LOGO='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAATUUlEQVR42u1de3SV1ZX/7X3O992EBPBRUCAkQSmOsdLaDJIANa3YorzEsddp7dTWR7Vd7czqtNWZ1a7V9M7qqGPbpc60aK1ata1tvW0VUAQfU9IioJBqsU3BQSUJCigizzzud87e88e9Nw9AEpJ7A4Scte5iQS7fPfn9zn79zj7nAkNjaAyNoTE0TtRBeX1ubS2hoYFOWHSTSQGgA/RptYyaGovaWh5a1wNpAfG4QUWFIpGQzn+sCM+YfsbpqXZ3mg0Lxyh5c0KhKqQmsOxadr3UtO7Z1zI4a24JiMcNkkmf/ev4aQvONIwLSfVCEJ0L4rFQOZlteOIta1FwEKBt985/bV637I4Dseo6bJ+sJh7n7APHV82dZ01wDZhmsrHDAUBFoCoACBKl/AnoWTwAA0J7T2+0fXBZimTSl06ZO5NjwXfYmBlEDHFRV7AJRJT505xw8KsCBKPas4exRww+wOUXXP5dVvw7MZO4SBRQEPEJCXY/hz0S8M+ovGikFg7/NbOdJVFKVbwfAr1/g3sFfm0toaIilLDoUQ7CWd61R6AT1L0MPAG1hERCykdMvMMWFH7MR+0RgYIh6AaCgNpaBhJSOuXimRyGX/JRyg2BP5AEJBLpN4WFXyNiQIWGIBu4IMwAZMKUSyaB8FERBxD1VWbQjsLgBCnFoEpEPetA9jCVLiGZhGecGxg7TFwkfSWA2BARm4HTpY56HcBsAxA06I8FpM3AFpyXyf/7gp4SEXnvNkJlB4ARACmlrWFQV8KiYp3HNgBARYX2mQATBsOhfXQdqgpjiLyr37dvZ2LH+pWvdHFvBGCwEqHoKsB1EyqPMA11LS2NUO2b7yBi9U5NELty+MjRfyqfvuD+8hnzp2aA9wA0Ho9zl0kPlhd66zF6JECZXlJV6mXRdkgWxEUCoMgE4dVEds2E6f/w5ITpl84DYJJpUU9ramosUJu1jMEQrKm/byIAWlL1iVOsKXqJDZeoiPadCKiqChEZNhaqgKp/XkXuat27/zfb1z+9PxP8DZIVCiQGe5zoBUsZHbu8ev5/mljhN33U7ojI9t9DqgdAZAMmEMRHr4pz9zmJfvbGC8u2dHz2QRs9h5h/PM54661j02Lq6qSnOEe9IWjMpJpTY+87qZ5tUKre5U6AS2dDSsYYYgvxqbdV9SFtdfc21j++IfMewhVX8HttaAx+P5WxgtKqOReZILYcAEFE+1GUHYoJUYUysyFjIT5qVS+POdW7t6xe/IcD5pJdUXp6xYyKsKh4JttYTMXtV9VUZl5H2yKUmIK2/Xv/sH193V/Q7y3JDAnjz59zVRAr+CkAVhEHgs31xDvihA0g3kPFL4PKXZtXLX68w5xraizq6uS0yZMLCwpLLyAbXkOMT9qwECoeKu7ocqAKDkK07dr5teb6Zbcfbkuy97PMPKRsysWXccGw+9nYkyRKpdsuci9Lp6ULImZjKV3ZuHp4/bHu12Tjnxft6nBPRAoAZVNnlZOJXQU2nzXGTFRViPgICgWICTqQjHg2gUm17vtK89on7z4cAb13I8mkRzxuGtcue7StZV+1T7U/zjZgtoHJrFyP3GkN2b0GEhd5cZEwmUoThvfwcH5xwrRLv1lSNWdcFvzKyuuDxueXb968avF/7H17+4e9S31ORVcx28AEYUgEq6DOXbt8v9L7wUZVe8T3yFZuQ4MiHjf7nlny9q7mjb8cMWbieoWWMJtStpZVlKDqO/aDc0IFMYgIIqLihYw5hW0wk4k/e/L4s8cXjyvfsnHtr7dmiXj15cfadjVv/POupr89MGLMmWtUtZiIJpogsFAlVfWUfi7lNwYY9lFq6Z43N63FOecwGhpy2ZZSy8B3FEivwDOmL5ghhC+S8uUc2ALxDhB1IGWAOPdhApIN2N5FKVL8VqX97s2rl/6hw11mrRbAhKnzJsMG1yrhU8ba0SoC9S5f7hNQ9WwD075/75e3rFu28HAuqI8fXqdAIv2LNjTg3eYNTbuaNvyueFz5Yig5At7PQVAEEEHEI6crjojSmY6KF0+EgG1wLpG5emTpWTNGlExs2b28+RU0POPSOlg8/L+XHn1zV/PfloUjxvwsCO1WQMezCUYTG1YV5Nxqj8AC+sd+9qHxuME55/CepxZt29284cnisWf+gsDbCVrGNhgFTrsQAJLD9JWIwOlqwgsANiY4w5jgipNKiueOHD+JcMrpm7b8Zel+AKiIx8PNK57Ys6tpw+pYe/ggjyj+C6CnADyBg4A1655yQ0S+XdBhXFO8gbLmdupZ04aPOHXUPxLT9WA7hYgg3mVXXO7z9WyFbSwTM8S511Xl/lR7y4NvrnuqOUtEwyOPRNkAXlo9e5qxBdcBejmbcISKg3jvKZ0IcL5dUP66o2tqDOrqXNbSJky/dDYR3aDgS9haFuegqo4IJg9EdKuw1UW7ROXhyLX9+I3nl63P1hI1AOoycxxfefGZtiB2lRJ/3tigVDUTJxR6xIsl/zGgF6OxUTJajUFDg9/VvPGVd5s2PFx0etlTBDJEmGSCoACazZzSXiVnzomIoSLqxRPTMGODKUTmmlNK/+7skeMm7di18qnXGxsbBajlivjo4NVnFu/Y1bxxxbDTxv3MUvCaqJzGxpawsawiXd1T12xb03XGQS8hYhKXWrrnzU3rBtAF9VTIdaqc5dPmn0VE14LMZ9jasZnMJBuwc17Yda2w09WyrPDeL2zavWkRGhpSADDx4otjm5Yt6+jnLJu+4BImugFEs9nYQL1L77Skc4A0fPQelbAN0b5n51eb1y2/82i4oF7HiTGVNe+LhSM/Q8bcwMaeDQDiIu0SsHM5xwMqbIV4/6LA/cS0tj78Wv0zuzviREWFyyqxpVVzP8zGXEdk4oCwim9Np9fUBsJ+qBpiSgEcZVD1xDZ0rS23NL3wRPIYI6ALETUrOBsnTps8uShWXL6Aib/Exk4nJmTihKcBCNjeRU2q8kB7S3T/theXNmZT2FGjKqSuLuEAoPQjl40JWsXueHvz3qLC0Ph329u2b1/flpmby48aOhCKbJd29/SKm3MRm/CLxDSfjQ3EO6hIvojoErANxEU7VfAwi9zz2ppFL2fdZ8VfYRoakqkjwFOPFwIOJKLjXFXp1DmVxtrrlPjTxoYjc5IivvcQKARMlk0AcVG7qixRlYWNqxb/PjvHysrrbX39GA8k9CD3dpxawKEDdpfdsPLq2WUw4ecIfDVbW55nKeEQAdv/rzj5YeOaxUs6XE3n3oT2b9Ud06N7wB47ZeapsbDoU1D+AgfBBwFAvMsClv+ALf4lUfmJ7n7nl00vr3y3c2/io9LXPWzqt9vI89ZGVjavqanhbNFUUVER7jvp/fOY6QYm83FiA/ERVJHPwg6dFXbU6FXv9VHbAx172NnToYkjI4L6tCprVjDqVvisGno0A3ZJ9fwLrDE3ALjc2DCmPoKIeCJQzpXYgwK22wHoLyLXdt+WNU++3EFEQ6fV5pKAg355VFYGp27eV5AvtN95Z2ML0g1ch57LI49IVtMpqbrk3MCG14LMp9kEo1Uc1HuPvARsVSiEmA2ZAN5F7Qz8xrnorqY1S547AF/NBQEdDyo57xMTbVHR5aT0UUDOUpUgP66HONW6L/7mi8+uPlwhc6Dpl1bOGmMKij4P0mvYBBMVCvVRVtPJQ8CGJ4JlG0C9E1V9WsUv7LaH3U8CCICeNvnjRcNGDP8ugOvYBsVQ6XPHYm85b9+9+8I3/vzU7w9LwHsUdqecf/6IYh59BRt7PZu8K7HZgG3YWKQDtqxxbXv+uXntM/U4TB+s7Q1Bp3/o4lEFxYWLTBBWe9cOH7VntvXyFoQ1vfEiRxDQEoI6ZAVA3plM7tkJ3Avg3rJpl842hr8E4BIOQiPOASq5JKLjvJy4yAMQEyusci32IwDWZVz3If9jT0eUCDU1pmBYeI8NYtUu1RZBodSx+Uyc31cfyUtbC2W3JhtXLVr62h8fnScpN8O51EME3c9BaIiY0s0EOWyXTxPB6iIBU2tPb+fDFkOJhJTuGzaVbLDAp9o8EQU4fhpntcNtxeMGqOXGF5asaVz52Oci0Q/6KHWzqr5hgtCQCXJ/wQgR96YroucDGgWxjzEbFX8cdwZ2xI90YdecTL4K4Fvjz7voRzys8AqG/RSAKRmXOqALrOcDGjZ8HwbN2a6EIAlUVlYGxcVzta4u8SaAO8qmzk2ZMJysqgUDPSPbsx2rp8GCf0a/qa+vj4B6lFVdeiUHfCOz/ZB4d1Sm1HNvZ7r9b1AAn3VFZdVzFxDbbxgbTAcU/TmA+B4BQJGuD7T/BBzXo5ZRCyCR8GlV9dJZxHwjWztTs8BnAmYOKzNPALENjOTilGQehLVcv/cwKmrCIwGUTJl9gY0V3MTMc4goL8BnCzxjQyM+8qnU/gdV9VEA1KWl/ugQkGkmOBJXRgBBlbnPwCeBsvPnVVFobmLiy9KKqRNVza0kkVFK2QZGVSA++p0Tf0vzqsXrchMD+jk5spYV+CZSbc84tjFW9DqfbbHSkEkjeyqUOH2wPAP8lNkfojB2ExFdwdYacZFq2s+bnMWzrDJqrQEIXvyz4lK3NK1+/NlucacHa7YDsPzBYv766urH1+bBfXUqtMkkyqbOPptM8A1mcyVZW9Bxi1dn23jOdB8y1qRvCkv9Cepu3rzq8d8eIA76o28BnaulELW1jK1bDcaM6X1Fl0i81wn9zs67ZNKXnj9vAofm6wT+PNugSFwKEqXSm/g5BF4VnpktWWPE+w3q2773+nOLH0J6mzK9GHoJ/MDGAIYgkRDE44R77umP7tK54uvq3Ni//8T4WMGwf1HQ9daGI7xLpYVCIqacA0+WrbXiozc0cre37G25u/vR2qTvy0HC4yUN7epq/KgpNacX2ZO+QpavZxOOUh/B5QH4rMRsgsCKj3a6qP2u9r0t/719/dNvHaq+yE8hdgwBP3bKzFMDW/QFNvbLxtoS710+Vnw2pTQchEZ81Oqj1E9bXev3tj+/fHOugD/WCei+4itqiotOPvlaYv4qG1uu3sNlfDzlOqUkIAO8eBf9Kopa/6ujozqHwB+7BHT1p2VlBeVjz7sKlr9ujJ2k4iFR5EBqKPe5vKZzeYWPUk8I+VuaVmb2d9Nz0nwcFrfHJPAVFWH5yWd+GhR8w1jzARXJpJNgENkcniQSKDSdUhK8939UF93cuGbJss45VSiSibxp8fbYAP4RQZI8AJpQPf+TsPbfmE2lqkKiyOfhikxVVeFse4mPXvKRu61x9ZJfAdAjzeWPTwI62w89QBhfNXdeEIQ3gc0MUs3ureYHeDaGrTXio1e9S/2gcfO2B7BlTWvHvAYA+KNHwAGrq6xq3sVsgxuZ+UJkhDJNV9B5AJ4N28CIc9t8qvWHunfnwo4Ww37k8scJAbVcgQbTkEikAKC8am4NjL2RjZmTufw79wolkD1fYEwQGvFur0bR3XvbWm7fUb98K4DsvRP+aN3GMiAEKIGBhDQkkSqfOn8qrLmRmC5nthCXUoWXnDdNpc+dcQb4lETRg1HL/tu2vPjUpm7Adx4kxKAkgEAQxf6xUy6ZFMYKv02EK9lYEhepuJR03K2Q25QSbEMj4iAuShrvb9m0evGL3XL5owx8rwlQIu5z0kfE4p1C5VuxWMEH2AbF4lKaB4WymzxMAMRFy8XJrY3PL1qR71w+rwSIS+3mINYfYIjYVqlKVjbILfDZuyOyubyL1qrozY2rFz12qKB/rI2eCWhr24p+fg+MeifpKx5yndnAszGW2RjxrkG83Lb5ucd+DsADSohfwccq8L2PAUz9v2A1t5lNF3k4sN6lmiHR99tb37h3a319S6e7IY8kjvlusp4JEBQQMwNIIZ8n63ud2bAxgbXq3Tvetf9Pe+u7P9paX7fjaOby+SEgWaEASEO7Urxr5CAsE5fKWALxwAOfkYed2+dS7ffBt93RmAd5eKBHb66t1NLKWWO4oOA2NsE/pXvlBui7YzK5PJuQxEcegp97529remFxQ7dc/ji+lr03GSZnY0Bp9fy4tcHtZMy4TCqZnysiO1s9WFWg4heL+lsan1uypltKOQgu/+79EaXMBklJ1Zxx1gR3GhtcruIzB+JyfZFrOqUU71Ygcje//vySpzuBH1zXGh/Z6u1yVKhs6tyrOYzdysaMzoE1dJeHnfsTvLvl9dWLf9ORyyeAwXifdF8AY9TWAomEpNtB7J3G2HmZK2CONDZ0qJRkLHwUvSKk32/a1vYQNi1rx6FOZg4RcLA1lFfNvYGC8GZme4p3qd5cqtENeHFuq4q7fc9b2368c9MLew58/mAe/QygHd3HMmHGgklKtNCYYKZmbjc5lDVk5eH01cTRHvWycH8U3fn22qXbuqWUJ8gXzuQmg0mngw4Al1bP/pqxhd9m5uHeuc6rAzLdw2wDEufaVXGfUPsPmlY+8dpgSSmPHgFZa0hf4aIl1XM+ENjYD9nYGnERoCpsQxZxUNFfRq711oNaPU4w4PM3srfWAqZs2vxvTZhxWdsZF3xSJ0xf8GR59fwLDnjf0Nef52d0fq982ZRZ1WXVcxd0/qiWu/58aAyMNSAtD8eHvn114I2hloeAHxpDY2gMjaExNA4e/w9qldjBEtmD6gAAAABJRU5ErkJggg==';

  function ensureStyle(){
    let s=D.getElementById('gsf-v348-logo-footer-style');
    if(!s){
      s=D.createElement('style');
      s.id='gsf-v348-logo-footer-style';
      s.textContent=`
        #gsf-global-header img.gsf-v348-transparent-logo{
          background:transparent!important;
          border:0!important;
          box-shadow:none!important;
          object-fit:contain!important;
        }
        #gsf-global-header .gsf-v348-transparent-logo-wrap{
          background:transparent!important;
          border:0!important;
          box-shadow:none!important;
        }
        #gsf-global-footer{
          display:flex!important;
          visibility:visible!important;
          opacity:1!important;
          pointer-events:auto!important;
        }
        
      `;
      D.head.appendChild(s);
    }
  }

  function apply(){
    ensureStyle();
    const h=D.getElementById('gsf-global-header');
    if(h){
      const imgs=[...h.querySelectorAll('.v343Brand img')];
      let logo=imgs.find(img=>{
        const r=img.getBoundingClientRect();
        return r.left < (P.innerWidth||1000)*0.5 && r.width<=90 && r.height<=90;
      }) || imgs[0];
      if(logo){
        if(logo.src!==LOGO) logo.src=LOGO;
        logo.classList.add('gsf-v348-transparent-logo');
        logo.style.background='transparent';
        logo.style.boxShadow='none';
        logo.style.objectFit='contain';
        const w=logo.parentElement;
        if(w){
          w.classList.add('gsf-v348-transparent-logo-wrap');
          w.style.background='transparent';
          w.style.boxShadow='none';
          w.style.border='0';
        }
      }
    }
    const f=D.getElementById('gsf-global-footer');
    if(f){
      f.style.display='flex';
      f.style.visibility='visible';
      f.style.opacity='1';
      f.style.pointerEvents='auto';
    }
  }

  apply();
  lifecycle.timeout(apply,80);
  lifecycle.timeout(apply,300);
  lifecycle.timeout(apply,900);
  try{
    lifecycle.observe(D.documentElement,{childList:true,subtree:true},apply);
  }catch(_e){}
})();
</script>
"""


# GSF_V349_FOOTER_CONTRACT — V343 owns geometry; V348 only keeps footer visible.


# GSF_V350_FOOTER_MOBILE_CENTER
import streamlit.components.v1 as _gsf_components_v350
_GSF_PARENT_FOOTER350 = r"""
<script id="gsf-v350-footer-mobile-center">
(() => {
  const P = window.parent;
  const D = P.document;
  const lifecycle=P.GSFNavigation.bridge('footer350',globalThis.frameElement);

  function ensureStyle(){
    let s = D.getElementById('gsf-v350-footer-style');
    if (s) return;
    s = D.createElement('style');
    s.id = 'gsf-v350-footer-style';
    s.textContent = `
      #gsf-global-footer{
        display:flex!important;
        align-items:center!important;
        justify-content:center!important;
        box-sizing:border-box!important;
        padding-left:12px!important;
        padding-right:12px!important;
      }
      #gsf-global-footer .gsf-v350-socials{
        position:absolute!important;
        left:50%!important;
        top:50%!important;
        transform:translate(-50%,-50%)!important;
        display:flex!important;
        align-items:center!important;
        justify-content:center!important;
        gap:10px!important;
        white-space:nowrap!important;
      }
      #gsf-global-footer .gsf-v350-socials > *{
        flex:0 0 auto!important;
        margin:0!important;
      }
      #gsf-global-footer .gsf-v350-legal{
        position:absolute!important;
        right:12px!important;
        top:50%!important;
        transform:translateY(-50%)!important;
        display:flex!important;
        align-items:center!important;
        justify-content:flex-end!important;
        gap:8px!important;
        white-space:nowrap!important;
      }
      #gsf-global-footer .gsf-v350-legal a{
        color:#6f829e!important;
        text-decoration:none!important;
        font-size:10px!important;
        line-height:1!important;
        font-weight:700!important;
        letter-spacing:.01em!important;
        opacity:.92!important;
      }
      #gsf-global-footer .gsf-v350-legal a:active{
        opacity:.58!important;
      }
      @media (max-width:430px){
        #gsf-global-footer .gsf-v350-socials{gap:8px!important;}
        #gsf-global-footer .gsf-v350-legal{right:8px!important;gap:6px!important;}
        #gsf-global-footer .gsf-v350-legal a{font-size:9px!important;}
      }
    `;
    D.head.appendChild(s);
  }

  function labelFor(el){
    return [
      el.textContent || '',
      el.getAttribute && el.getAttribute('aria-label') || '',
      el.getAttribute && el.getAttribute('title') || '',
      el.getAttribute && el.getAttribute('href') || ''
    ].join(' ').toLowerCase();
  }

  function isLegalOrBug(el){
    const v = labelFor(el);
    return /segnala|bug|privacy|term|contatt|contact/.test(v);
  }

  function isKnownSocial(el){
    const v = labelFor(el);
    return /facebook|instagram|youtube|youtu\.be|tiktok|twitch|twitter|x\.com/.test(v);
  }

  function apply(){
    ensureStyle();
    const f = D.getElementById('gsf-global-footer');
    if (!f) return;

    if (f.dataset.gsfV350 === '1') return;

    const clickable = [...f.querySelectorAll('a,button,[role="button"]')]
      .filter(el => !isLegalOrBug(el));

    let socials = clickable.filter(isKnownSocial);
    if (!socials.length) socials = clickable.slice(0, 4);

    // Keep only outermost unique clickable nodes so icon handlers/links survive.
    socials = socials.filter((el, i, arr) => !arr.some((other, j) => j !== i && other.contains(el)));

    const socialWrap = D.createElement('div');
    socialWrap.className = 'gsf-v350-socials';
    socials.forEach(el => socialWrap.appendChild(el));

    const legal = D.createElement('nav');
    legal.className = 'gsf-v350-legal';
    legal.setAttribute('aria-label', 'Informazioni legali');
    [
      ['Termini','/terms'],
      ['Privacy','/privacy'],
      ['Contatti','/contact']
    ].forEach(([label, href]) => {
      const a = D.createElement('a');
      a.textContent = label;
      a.href = href;
      a.target = '_self';
      legal.appendChild(a);
    });

    f.replaceChildren(socialWrap, legal);
    f.dataset.gsfV350 = '1';
  }

  apply();
  lifecycle.timeout(apply, 120);
  lifecycle.timeout(apply, 500);
  lifecycle.timeout(apply, 1200);
  try {
    lifecycle.observe(D.documentElement,{childList:true,subtree:true},() => {
      const f = D.getElementById('gsf-global-footer');
      if (f && f.dataset.gsfV350 !== '1') apply();
    }).observe(D.documentElement, {childList:true, subtree:true});
  } catch(_e) {}
})();
</script>
"""



# GSF_V351_FOOTER_BRAND_GLASS
# GSF_V353_FOOTER_BALANCE_HIRES
# GSF_V354_FOOTER_TRUE_CENTER_SAFE_SIDES
# GSF_V355_FOOTER_BOTTOM_LOCK
# GSF_V356_FOOTER_SIDE_INSET
# GSF_V358_FOOTER_VERSION_LABEL
# GSF_V361_VISIBLE_VERSION
# GSF_V395_FOOTER_STACK_CONTRACT
import streamlit.components.v1 as _gsf_components_v351
_GSF_PARENT_FOOTER351 = r"""
<script id="gsf-v351-footer-brand-glass">
(() => {
  const P = window.parent;
  const D = P.document;
  const lifecycle=P.GSFNavigation.bridge('footer351',globalThis.frameElement);

  function ensureStyle(){
    let s = D.getElementById('gsf-v351-footer-style');
    if (s) s.remove();
    s = D.createElement('style');
    s.id = 'gsf-v351-footer-style';
    s.textContent = `
      #gsf-global-footer{
        position:fixed!important;
        left:0!important;
        right:0!important;
        bottom:0!important;
        top:auto!important;
        width:100%!important;
        z-index:var(--gsf-shell-z,2147483600)!important;
        display:block!important;
        box-sizing:border-box!important;
        padding:3px 24px!important;
        background:linear-gradient(180deg,rgba(255,255,255,.94),rgba(245,251,255,.90))!important;
        border-top:1px solid rgba(139,185,218,.20)!important;
        box-shadow:0 -8px 24px rgba(66,112,154,.05),inset 0 1px 0 rgba(255,255,255,.98)!important;
        backdrop-filter:blur(18px)!important;
        -webkit-backdrop-filter:blur(18px)!important;
        overflow:visible!important;
      }
      #gsf-global-footer .gsf-v351-brand{
        position:absolute!important;
        left:max(24px,env(safe-area-inset-left))!important;
        top:50%!important;
        transform:translateY(-50%)!important;
        z-index:2!important;
        color:#6e86a5!important;
        font-size:9px!important;
        line-height:1!important;
        font-weight:950!important;
        letter-spacing:.12em!important;
        white-space:nowrap!important;
        opacity:.94!important;
      }
      #gsf-global-footer .gsf-v351-socials{
        position:absolute!important;
        left:50%!important;
        top:50%!important;
        transform:translate(-50%,-50%)!important;
        z-index:3!important;
        display:flex!important;
        align-items:center!important;
        justify-content:center!important;
        gap:6px!important;
        white-space:nowrap!important;
      }
      #gsf-global-footer .gsf-v351-social{
        width:23px!important;
        height:23px!important;
        min-width:23px!important;
        min-height:23px!important;
        border-radius:8px!important;
        display:grid!important;
        place-items:center!important;
        overflow:hidden!important;
        border:1px solid rgba(255,255,255,.92)!important;
        box-shadow:0 2px 8px rgba(55,91,127,.10),inset 0 1px 0 rgba(255,255,255,.38)!important;
        line-height:1!important;
        user-select:none!important;
        -webkit-user-select:none!important;
      }
      #gsf-global-footer .gsf-v351-social svg{
        display:block!important;
        width:15px!important;
        height:15px!important;
        shape-rendering:geometricPrecision!important;
        text-rendering:geometricPrecision!important;
      }
      #gsf-global-footer .gsf-v351-youtube{background:#ff1744!important;color:#fff!important}
      #gsf-global-footer .gsf-v351-tiktok{background:#101820!important;color:#fff!important}
      #gsf-global-footer .gsf-v351-instagram{background:linear-gradient(145deg,#6f55d8 0%,#d84f94 49%,#f4a044 100%)!important;color:#fff!important}
      #gsf-global-footer .gsf-v351-facebook{background:#1877f2!important;color:#fff!important}
      #gsf-global-footer .gsf-v351-twitch{background:#9146ff!important;color:#fff!important}
      #gsf-global-footer .gsf-v351-legal{
        position:absolute!important;
        right:max(24px,env(safe-area-inset-right))!important;
        top:50%!important;
        transform:translateY(-50%)!important;
        z-index:2!important;
        display:flex!important;
        align-items:center!important;
        justify-content:flex-end!important;
        gap:4px!important;
        white-space:nowrap!important;
        overflow:visible!important;
      }
      #gsf-global-footer .gsf-v351-legal a{
        color:#6e86a5!important;
        text-decoration:none!important;
        font-size:7.2px!important;
        line-height:1!important;
        font-weight:820!important;
        letter-spacing:-.01em!important;
        opacity:.97!important;
      }
      #gsf-global-footer .gsf-v351-legal a:active{opacity:.55!important}
      #gsf-global-footer .gsf-v351-dot{
        width:2px!important;height:2px!important;border-radius:50%!important;background:#b5c7d7!important;display:block!important;flex:0 0 auto!important;
      }
      @media (max-width:390px){
        #gsf-global-footer{padding-left:20px!important;padding-right:20px!important}
        #gsf-global-footer .gsf-v351-brand{left:max(20px,env(safe-area-inset-left))!important;font-size:8px!important;letter-spacing:.08em!important}
        #gsf-global-footer .gsf-v351-socials{gap:5px!important}
        #gsf-global-footer .gsf-v351-social{width:22px!important;height:22px!important;min-width:22px!important;min-height:22px!important}
        #gsf-global-footer .gsf-v351-social svg{width:14px!important;height:14px!important}
        #gsf-global-footer .gsf-v351-legal{right:max(20px,env(safe-area-inset-right))!important;gap:3px!important}
        #gsf-global-footer .gsf-v351-legal a{font-size:6.65px!important}
      }
      @media (max-width:350px){
        #gsf-global-footer .gsf-v351-brand{left:max(16px,env(safe-area-inset-left))!important;font-size:7px!important}
        #gsf-global-footer .gsf-v351-social{width:20px!important;height:20px!important;min-width:20px!important;min-height:20px!important}
        #gsf-global-footer .gsf-v351-socials{gap:4px!important}
        #gsf-global-footer .gsf-v351-legal{right:max(16px,env(safe-area-inset-right))!important}
        #gsf-global-footer .gsf-v351-legal a{font-size:6px!important}
      }
    `;
    D.head.appendChild(s);
  }

  const SOCIAL_HTML = `
    <span class="gsf-v351-social gsf-v351-youtube" data-social="youtube" role="img" aria-label="YouTube" title="YouTube">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M19.8 7.1a2.6 2.6 0 0 0-1.8-1.8C16.4 4.9 12 4.9 12 4.9s-4.4 0-6 .4a2.6 2.6 0 0 0-1.8 1.8A27 27 0 0 0 3.8 12a27 27 0 0 0 .4 4.9A2.6 2.6 0 0 0 6 18.7c1.6.4 6 .4 6 .4s4.4 0 6-.4a2.6 2.6 0 0 0 1.8-1.8 27 27 0 0 0 .4-4.9 27 27 0 0 0-.4-4.9ZM10.3 15.1V8.9l5.4 3.1-5.4 3.1Z"/></svg>
    </span>
    <span class="gsf-v351-social gsf-v351-tiktok" data-social="tiktok" role="img" aria-label="TikTok" title="TikTok">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M15.3 3.5c.4 2.3 1.7 3.7 4.1 3.9v3.1a8.2 8.2 0 0 1-4.1-1.2v6.2a5.4 5.4 0 1 1-4.7-5.4v3.1a2.3 2.3 0 1 0 1.5 2.2V3.5h3.2Z"/></svg>
    </span>
    <span class="gsf-v351-social gsf-v351-instagram" data-social="instagram" role="img" aria-label="Instagram" title="Instagram">
      <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4.4" y="4.4" width="15.2" height="15.2" rx="4.2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="3.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.4" cy="6.8" r="1.05" fill="currentColor"/></svg>
    </span>
    <span class="gsf-v351-social gsf-v351-facebook" data-social="facebook" role="img" aria-label="Facebook" title="Facebook">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.8 20v-7h2.4l.4-2.8h-2.8V8.4c0-.8.2-1.4 1.4-1.4h1.5V4.5c-.3 0-1.2-.1-2.3-.1-2.3 0-3.8 1.4-3.8 4v1.8H8V13h2.6v7h3.2Z"/></svg>
    </span>
    <span class="gsf-v351-social gsf-v351-twitch" data-social="twitch" role="img" aria-label="Twitch" title="Twitch">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M5 3h16v10.8l-4.5 4.5h-3.3L11 20.5H8.8v-2.2H5V3Zm2.2 2.2v10.9h3.7v2l2-2h3l2.9-2.9v-8H7.2Zm4 2h2v5h-2v-5Zm4.2 0h2v5h-2v-5Z"/></svg>
    </span>
  `;

  function build(){
    ensureStyle();
    const f = D.getElementById('gsf-global-footer');
    if (!f) return;

    const brand = D.createElement('div');
    brand.className = 'gsf-v351-brand gsf-v351-footer-shell';
    brand.innerHTML = '';  // GSF_NIGHT_ARENA: version lives in Creator Hub › Info

    const socials = D.createElement('div');
    socials.className = 'gsf-v351-socials';
    socials.setAttribute('aria-label','Social Gaming Shorts Factory');
    socials.innerHTML = SOCIAL_HTML;

    const legal = D.createElement('nav');
    legal.className = 'gsf-v351-legal';
    legal.setAttribute('aria-label','Informazioni legali');
    [
      ['Termini','/terms'],
      ['Privacy','/privacy'],
      ['Contatti','/contact']
    ].forEach(([label, href], idx, all) => {
      const a = D.createElement('a');
      a.textContent = label;
      a.href = href;
      a.target = '_self';
      legal.appendChild(a);
      if (idx < all.length - 1) {
        const dot = D.createElement('span');
        dot.className = 'gsf-v351-dot';
        dot.setAttribute('aria-hidden','true');
        legal.appendChild(dot);
      }
    });

    f.replaceChildren(brand, socials, legal);
    f.dataset.gsfV351 = '1';
    f.dataset.gsfV353 = '1';
    f.dataset.gsfV354 = '1';
    f.dataset.gsfV355 = '1';
    f.dataset.gsfV356 = '1';
    f.dataset.gsfV358 = '1';
    f.dataset.gsfV361 = '1';
  }

  build();
  lifecycle.timeout(build, 80);
  lifecycle.timeout(build, 300);
  lifecycle.timeout(build, 900);
  lifecycle.timeout(build, 1800);
  try {
    lifecycle.observe(D.documentElement,{childList:true,subtree:true},() => {
      const f = D.getElementById('gsf-global-footer');
      if (!f || f.dataset.gsfV361 !== '1' || !f.querySelector('.gsf-v351-socials')) build();
    });
  } catch(_e) {}
})();
</script>
"""


# GSF_V362_VISIBLE_VERSION
