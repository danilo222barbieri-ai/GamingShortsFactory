from pathlib import Path
import ast

src=Path("/app/GamingShortsFactory_V107_PRODUCTION_UI.py")
out=Path("/app/GamingShortsFactory_V107_1_STABILITY.py")
s=src.read_text(encoding="utf-8")


def replace_function(source,name,new_source):
    tree=ast.parse(source)
    node=next(
        (n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),
        None,
    )
    if node is None:
        raise RuntimeError(f"V107.1 function not found: {name}")
    lines=source.splitlines(keepends=True)
    return "".join(lines[:node.lineno-1]) + new_source.rstrip() + "\n\n" + "".join(lines[node.end_lineno:])


_release=r'''def _gsf_v93_release_analysis_memory():
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
'''
s=replace_function(s,"_gsf_v93_release_analysis_memory",_release)

# The automatic final master is already retained as publication_final_bytes
# after a successful render.  Keeping up to six additional final MP4s in a
# session cache can consume hundreds of MB in a 1 GB container.
_old_cache='cache=st.session_state.setdefault("gsf_final_master_cache_v44",{})'
if _old_cache not in s:
    raise RuntimeError("V107.1 master byte-cache anchor missing")
s=s.replace(_old_cache,'cache={}  # V107.1: disk/session output is the cache; do not retain final MP4s in RAM',1)

# A duplicate Streamlit rerun must not wait for minutes while retaining another
# full page worth of video/preview memory.  Two seconds is enough to detect an
# already-running render and fail safely without destabilising the service.
_old_lock='acquired=_GSF_V106_RENDER_LOCK.acquire(timeout=max(30.0,float(timeout or 600.0)))'
if _old_lock not in s:
    raise RuntimeError("V107.1 render-lock anchor missing")
s=s.replace(_old_lock,'acquired=_GSF_V106_RENDER_LOCK.acquire(timeout=2.0)',1)

# Manual/Scegli scena already has a durable source path.  Do not duplicate the
# entire uploaded source into publication_preview_bytes.  Replace only the
# unique read; leaving the surrounding try/if structure intact makes this
# resilient to indentation changes in the generated Manual branch.
_old_manual_read='_gsf_manual_preview_bytes=video.getvalue() if hasattr(video,"getvalue") else None'
if _old_manual_read not in s:
    raise RuntimeError("V107.1 manual full-source preview read missing")
s=s.replace(
    _old_manual_read,
    '_gsf_manual_preview_bytes=None  # V107.1: stream from durable source path instead',
    1,
)

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V107.1 memory/stability patch applied:",out)
