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

_preview=r'''def crea_anteprima(input_file, output_file, start, duration):
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
'''
s=replace_function(s,"crea_anteprima",_preview)

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
s=s.replace(_old_lock,'acquired=_GSF_V106_RENDER_LOCK.acquire(timeout=15.0)',1)

# 4K/60 iPhone sources can transiently push the 1 GB Railway container over
# its cgroup limit even with one x264 worker. Keep CRF/resolution intact but
# bound filter parallelism and x264 lookahead/reference buffering.
_gsf_render_tree=ast.parse(s)
_gsf_render_core=next(
    (n for n in _gsf_render_tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_render_core"),
    None,
)
if _gsf_render_core is None:
    raise RuntimeError("V107.1 final render core missing")
_gsf_lowmem_lists=[]
for _node in ast.walk(_gsf_render_core):
    if not isinstance(_node,ast.List):
        continue
    _vals=[x.value for x in _node.elts if isinstance(x,ast.Constant) and isinstance(x.value,str)]
    if "-c:v" in _vals and "libx264" in _vals and "-threads" in _vals and "1" in _vals:
        _gsf_lowmem_lists.append(_node)
if len(_gsf_lowmem_lists)!=1:
    raise RuntimeError(f"V107.1 expected one final x264 option list, found {len(_gsf_lowmem_lists)}")
_gsf_opts=_gsf_lowmem_lists[0].elts
_gsf_thread_i=None
for _i in range(len(_gsf_opts)-1):
    if (
        isinstance(_gsf_opts[_i],ast.Constant) and _gsf_opts[_i].value=="-threads"
        and isinstance(_gsf_opts[_i+1],ast.Constant) and str(_gsf_opts[_i+1].value)=="1"
    ):
        _gsf_thread_i=_i+2
        break
if _gsf_thread_i is None:
    raise RuntimeError("V107.1 final x264 thread anchor missing")
_gsf_opts[_gsf_thread_i:_gsf_thread_i]=[
    ast.Constant(value="-filter_threads"),ast.Constant(value="1"),
    ast.Constant(value="-x264-params"),ast.Constant(value="rc-lookahead=8:sync-lookahead=0:ref=2:bframes=2"),
]
ast.fix_missing_locations(_gsf_render_core)
_gsf_render_lines=s.splitlines(keepends=True)
_gsf_render_src=ast.unparse(_gsf_render_core)
s="".join(_gsf_render_lines[:_gsf_render_core.lineno-1])+_gsf_render_src.rstrip()+"\n\n"+"".join(_gsf_render_lines[_gsf_render_core.end_lineno:])

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

# Defensive cleanup: some older generated V107 sources can contain patcher
# statements at module scope.  They compile, but crash at runtime because the
# Streamlit app has no variable named `s`.  Detect the actual AST pattern
# instead of depending on one exact comment marker.
_gsf_tree=ast.parse(s)
_gsf_bad=[]
for _gsf_node in _gsf_tree.body:
    if not isinstance(_gsf_node,ast.Assign):
        continue
    if not any(isinstance(_t,ast.Name) and _t.id=="s" for _t in _gsf_node.targets):
        continue
    _v=_gsf_node.value
    if (
        isinstance(_v,ast.Call)
        and isinstance(_v.func,ast.Attribute)
        and _v.func.attr=="replace"
        and isinstance(_v.func.value,ast.Name)
        and _v.func.value.id=="s"
    ):
        _gsf_bad.append(_gsf_node)

if _gsf_bad:
    _gsf_lines=s.splitlines(keepends=True)
    _gsf_first=_gsf_bad[0].lineno-1
    if _gsf_first < int(len(_gsf_lines)*0.75):
        raise RuntimeError(f"V107.1 unexpected runtime s=s.replace at line {_gsf_first+1}")
    _gsf_cut=_gsf_first
    for _i in range(_gsf_first-1,max(-1,_gsf_first-100),-1):
        _line=_gsf_lines[_i]
        if (
            "_old_cache=" in _line
            or "_old_lock=" in _line
            or "_old_manual_read=" in _line
            or "automatic final master is already retained" in _line
            or "duplicate Streamlit rerun" in _line
            or "Manual/Scegli scena already has a durable source path" in _line
        ):
            _gsf_cut=_i
    print("V107.1 leaked runtime patch tail detected at",_gsf_first+1,"trimming from",_gsf_cut+1)
    s="".join(_gsf_lines[:_gsf_cut]).rstrip()+"\n"

# Build must fail here if any leaked patcher self-replacement survived.
if "s=s.replace(" in s:
    _remaining=[i+1 for i,l in enumerate(s.splitlines()) if "s=s.replace(" in l]
    raise RuntimeError(f"V107.1 leaked runtime patch statements remain: {_remaining[-10:]}")

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V107.1 memory/stability patch applied:",out)
