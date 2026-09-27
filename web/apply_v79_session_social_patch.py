from pathlib import Path
import re

src = Path('/app/GamingShortsFactory_V78_MOBILE_BETA.py')
out = Path('/app/GamingShortsFactory_V79_SESSION_SOCIAL_BETA.py')
s = src.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise RuntimeError(f'V79 patch target not found: {label}')
    s = s.replace(old, new, 1)

replace_once(
'''def _gsf_session_id():
    # OAuth callbacks may reconnect Streamlit in a fresh browser session.
    # Recover the anonymous workspace from the cryptographic OAuth state.
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
    if not current:
        current = secrets.token_urlsafe(24).replace("-", "_")[:36]
        st.session_state["gsf_web_session_id"] = current
    return current
''',
'''def _gsf_session_id():
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
''',
'session id recovery')

replace_once(
'''GSF_SESSION_ID = _gsf_session_id()
GSF_SESSION_ROOT = GSF_SESSIONS_ROOT / GSF_SESSION_ID
GSF_PREVIEW_DIR = GSF_SESSION_ROOT / "media"
GSF_SESSION_TMP_DIR = GSF_SESSION_ROOT / "tmp"
GSF_SESSION_EXPORT_DIR = GSF_SESSION_ROOT / "export"
GSF_SESSION_SOCIAL_DIR = GSF_SESSION_ROOT / "social"
for _dir in (GSF_PREVIEW_DIR, GSF_SESSION_TMP_DIR, GSF_SESSION_EXPORT_DIR, GSF_SESSION_SOCIAL_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
''',
'''GSF_SESSION_ID = _gsf_session_id()
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

_gsf_restore_persistent_state()
''',
'persistent anonymous state')

# Insert a cheap shortcut into the two upload helpers so a recovered source
# is reused from disk instead of being re-read into RAM.
def inject_after_def(func_name, body_builder):
    global s
    pattern = rf'(^def {re.escape(func_name)}\(([^)]*)\):\n)'
    m = re.search(pattern, s, flags=re.M)
    if not m:
        raise RuntimeError(f'V79 function not found: {func_name}')
    args = m.group(2).strip()
    first_arg = args.split(",", 1)[0].split("=", 1)[0].strip()
    body = body_builder(first_arg)
    s = s[:m.end()] + body + s[m.end():]

inject_after_def(
    "_gsf_materialize_upload_once",
    lambda arg: f'''    _recovered = getattr({arg}, "_gsf_recovered_path", "")\n    if _recovered and Path(_recovered).is_file():\n        _p = Path(_recovered)\n        _st = _p.stat()\n        _token = hashlib.sha256(\n            f"recovered|{{_p}}|{{_st.st_size}}|{{_st.st_mtime_ns}}".encode("utf-8")\n        ).hexdigest()\n        st.session_state["gsf_source_path"] = str(_p)\n        st.session_state.setdefault("gsf_source_name", getattr({arg}, "name", _p.name))\n        return str(_p), _token, True, {{\n            "mode": "recovered", "bytes": int(_st.st_size),\n            "hash_ms": 0.0, "write_ms": 0.0, "total_ms": 0.0,\n        }}\n'''
)

inject_after_def(
    "_gsf_upload_master_token",
    lambda arg: f'''    _recovered = getattr({arg}, "_gsf_recovered_path", "")\n    if _recovered and Path(_recovered).is_file():\n        _p = Path(_recovered)\n        _st = _p.stat()\n        return hashlib.sha256(\n            f"recovered-master|{{_p}}|{{_st.st_size}}|{{_st.st_mtime_ns}}".encode("utf-8")\n        ).hexdigest()\n'''
)

replace_once(
'''with st.container(key="v73-upload-shell"):
    video = st.file_uploader(
        "Carica il tuo video",
        type=["mp4", "mov", "mkv"],
        label_visibility="collapsed",
        key="upload_v73"
    )
st.markdown(_gsf_v73_upload_css(video is not None), unsafe_allow_html=True)
if video is not None:
    st.markdown(
        f'<div class="v73-upload-meta" role="status" title="{html.escape(video.name, quote=True)}">{html.escape(video.name)}</div>',
        unsafe_allow_html=True,
    )
''',
'''with st.container(key="v73-upload-shell"):
    video = st.file_uploader(
        "Carica il tuo video",
        type=["mp4", "mov", "mkv"],
        label_visibility="collapsed",
        key="upload_v73"
    )

_gsf_recovered_source = None
if video is None and GSF_WEB_MODE:
    _gsf_recovered_source = _gsf_find_recovered_source()
    if _gsf_recovered_source is not None:
        video = _GSFRecoveredUpload(
            _gsf_recovered_source,
            st.session_state.get("gsf_source_name", _gsf_recovered_source.name)
        )
        st.session_state["gsf_source_path"] = str(_gsf_recovered_source)

st.markdown(_gsf_v73_upload_css(video is not None), unsafe_allow_html=True)
if video is not None:
    st.markdown(
        f'<div class="v73-upload-meta" role="status" title="{html.escape(video.name, quote=True)}">{html.escape(video.name)}</div>',
        unsafe_allow_html=True,
    )
    if _gsf_recovered_source is not None:
        st.caption("Sessione beta ripristinata automaticamente.")
''',
'recover uploader after reconnect')

replace_once(
'''        if st.button("CREA CON AI", use_container_width=True):
            with _gsf_session_tempdir("gsf_analysis_") as analisi_temp:
''',
'''        if st.button("CREA CON AI", use_container_width=True):
            _gsf_save_persistent_state()
            with _gsf_session_tempdir("gsf_analysis_") as analisi_temp:
''',
'save before AI work')

# Save the latest JSON-safe UI state at the end of every normal Streamlit run.
s += '''

# ============================================================
# V79 — PERSIST ANONYMOUS BETA WORKSPACE
# ============================================================
try:
    _gsf_save_persistent_state()
    _gsf_touch_session()
except Exception:
    pass
'''

out.write_text(s, encoding='utf-8')
print(f'V79 patch applied: {out}')
