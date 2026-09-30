from pathlib import Path
import ast

src=Path("/app/GamingShortsFactory_V108_GAME_VISION.py")
out=Path("/app/GamingShortsFactory_V109_ZOOMOUT.py")
s=src.read_text(encoding="utf-8")
tree=ast.parse(s)

node=next(
    (n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_render_video_filters"),
    None,
)
if node is None:
    raise RuntimeError("V109 _gsf_render_video_filters not found")

wrapper=r'''
# ===== V109 NATIVE ZOOM-OUT =====
GSF_V109_ZOOMOUT = True
try:
    import sys as _gsf_v109_sys
    if "/app/web" not in _gsf_v109_sys.path:
        _gsf_v109_sys.path.insert(0,"/app/web")
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
'''

lines=s.splitlines(keepends=True)
s="".join(lines[:node.end_lineno])+wrapper.rstrip()+"\n\n"+"".join(lines[node.end_lineno:])

# -----------------------------------------------------------------------
# Final Short button: deterministic queueing + stale-running recovery.
# -----------------------------------------------------------------------
old_button='''            with st.container(key="gsf-major-create-short"):
                _v1054_create_final_clicked=st.button(
                    "CREA SHORT FINALE",
                    use_container_width=True,
                    key="create_final_short_v54",
                    on_click=_gsf_v107_queue_final_render,
                    disabled=bool(st.session_state.get("gsf_v107_final_render_running",False)),
                )

            _gsf_v107_pending=bool(
'''
new_button='''            # V109: a dead/stale job must never leave CREA SHORT disabled.
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

            with st.container(key="gsf-major-create-short"):
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
'''
if old_button not in s:
    raise RuntimeError("V109 final Short button anchor missing")
s=s.replace(old_button,new_button,1)

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V109 native zoom-out + Short queue fix applied:",out)
