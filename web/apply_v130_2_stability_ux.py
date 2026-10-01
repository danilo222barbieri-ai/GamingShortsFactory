from pathlib import Path
import ast
import re

src=Path("/app/GamingShortsFactory_V130_1_HOTFIX.py")
out=Path("/app/GamingShortsFactory_V130_2_STABILITY_UX.py")
s=src.read_text(encoding="utf-8")

# V130.2 stability + UX closure.
# Existing visual language is preserved. No player dimensions are touched.

# 1) New video must never silently destroy current work.
# Locate the real final widget by its stable Streamlit key instead of depending
# on the historical layout/column wrapper around it.
_tree_nv=ast.parse(s)
_nv_call=None
_nv_stmt=None
for _node in ast.walk(_tree_nv):
    if not isinstance(_node,ast.Call):
        continue
    _fn=_node.func
    if not (isinstance(_fn,ast.Attribute) and _fn.attr=="button"):
        continue
    _key=None
    for _kw in _node.keywords:
        if _kw.arg=="key" and isinstance(_kw.value,ast.Constant):
            _key=str(_kw.value.value or "")
    if _key=="v81_new_video":
        _nv_call=_node
        break
if _nv_call is None:
    raise RuntimeError("V130.2 new-video widget missing")

_old_call=ast.get_source_segment(s,_nv_call) or ""
if not _old_call:
    raise RuntimeError("V130.2 new-video widget source unavailable")
_new_call=(
    'st.button("＋ NUOVO VIDEO",use_container_width=False,key="v81_new_video",'
    'help="Avvia un nuovo progetto senza perdere per errore quello attuale.")'
)
s=s.replace(_old_call,_new_call,1)

# Insert the protection flow immediately after the enclosing active-video block
# so it uses full page width rather than the small centered button column.
_tree_nv=ast.parse(s)
_active_if=None
for _node in ast.walk(_tree_nv):
    if isinstance(_node,ast.If):
        _test=ast.get_source_segment(s,_node.test) or ""
        _body=ast.get_source_segment(s,_node) or ""
        if "_gsf_has_active_video" in _test and 'key="v81_new_video"' in _body:
            _active_if=_node
            break
if _active_if is None:
    raise RuntimeError("V130.2 active-video block missing")

# Change the button expression into a click flag inside the existing block.
_lines=s.splitlines(keepends=True)
_button_line=None
for _lineno in range(_active_if.lineno,_active_if.end_lineno+1):
    if 'key="v81_new_video"' in _lines[_lineno-1]:
        _button_line=_lineno
        break
if _button_line is None:
    # Multiline call: use AST location.
    _tree_tmp=ast.parse(s)
    for _node in ast.walk(_tree_tmp):
        if isinstance(_node,ast.Call):
            _seg=ast.get_source_segment(s,_node) or ""
            if 'key="v81_new_video"' in _seg:
                _button_line=_node.lineno
                break
if _button_line is None:
    raise RuntimeError("V130.2 new-video line missing")

# Replace the standalone st.button expression statement using AST.
_tree_tmp=ast.parse(s)
_button_expr=None
for _node in ast.walk(_tree_tmp):
    if isinstance(_node,ast.Expr) and isinstance(_node.value,ast.Call):
        _seg=ast.get_source_segment(s,_node.value) or ""
        if 'key="v81_new_video"' in _seg:
            _button_expr=_node
            break
if _button_expr is None:
    raise RuntimeError("V130.2 new-video expression missing")
_old_expr=ast.get_source_segment(s,_button_expr) or ""
_indent=" "*int(_button_expr.col_offset)
_new_expr=(
    '_gsf_v1302_new_video_clicked=st.button('
    '"＋ NUOVO VIDEO",use_container_width=False,key="v81_new_video",'
    'help="Avvia un nuovo progetto senza perdere per errore quello attuale.")'
)
s=s.replace(_old_expr,_new_expr,1)

# Reparse after replacement to get the enclosing active-video block end.
_tree_nv=ast.parse(s)
_active_if=None
for _node in ast.walk(_tree_nv):
    if isinstance(_node,ast.If):
        _test=ast.get_source_segment(s,_node.test) or ""
        _body=ast.get_source_segment(s,_node) or ""
        if "_gsf_has_active_video" in _test and "gsf_v1302_new_video_clicked" in _body:
            _active_if=_node
            break
if _active_if is None:
    raise RuntimeError("V130.2 protected active-video block missing")

_guard=r'''
    if bool(locals().get("_gsf_v1302_new_video_clicked",False)):
        _gsf_v1302_has_work=bool(
            st.session_state.get("gsf_final_recipe")
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
                '<div class="gsf-major-note"><b>Nuovo video</b> · salva la lavorazione attuale oppure continua senza salvarla.</div>',
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

'''
_lines=s.splitlines(keepends=True)
_insert_index=_active_if.end_lineno
s="".join(_lines[:_insert_index])+_guard+"".join(_lines[_insert_index:])

# Transient buttons must never be restored from a persisted state.
restore_anchor='''try:
    if "gsf_final_ready_sync_v111" not in _GSF_TRANSIENT_WIDGET_EXACT:
        _GSF_TRANSIENT_WIDGET_EXACT.append("gsf_final_ready_sync_v111")
except Exception:
    pass
'''
if restore_anchor in s:
    s=s.replace(restore_anchor,restore_anchor+r'''
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
''',1)

# 2) Clicking CREA SHORT opens the shared social area immediately.
queue_flag='''                st.session_state["gsf_v107_final_render_pending"]=True
                st.session_state["gsf_v107_final_render_running"]=True
'''
if queue_flag not in s:
    raise RuntimeError("V130.2 render queue flag anchor missing")
s=s.replace(queue_flag,'''                st.session_state["gsf_v107_final_render_pending"]=True
                st.session_state["gsf_v107_final_render_running"]=True
                st.session_state["gsf_v1302_social_open"]=True
''',1)

# 3) Faster final encode while preserving CRF/profile/current render layout.
# The real final encoder lives in _gsf_render_core. Update that function by AST
# so the optimization survives formatting/unparse changes from older patches.
_tree_speed=ast.parse(s)
_core_speed=next(
    (n for n in _tree_speed.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_render_core"),
    None,
)
if _core_speed is None:
    raise RuntimeError("V130.2 final render core missing")
_speed_changes=0
for _node in ast.walk(_core_speed):
    if not isinstance(_node,ast.List):
        continue
    _elts=_node.elts
    for _i in range(len(_elts)-1):
        _a,_b=_elts[_i],_elts[_i+1]
        if (
            isinstance(_a,ast.Constant) and _a.value=="-preset"
            and isinstance(_b,ast.Constant) and str(_b.value)=="medium"
        ):
            _b.value="fast"
            _speed_changes+=1
if _speed_changes!=1:
    raise RuntimeError(
        "V130.2 expected one final medium preset, found "+str(_speed_changes)
    )
ast.fix_missing_locations(_core_speed)
_new_core_speed=ast.unparse(_core_speed)
_lines_speed=s.splitlines(keepends=True)
s=(
    "".join(_lines_speed[:_core_speed.lineno-1])
    +_new_core_speed.rstrip()+"\n\n"
    +"".join(_lines_speed[_core_speed.end_lineno:])
)

# 4) Restore visible ad placeholders if live AdSense lacks explicit slot IDs.
ads_hidden='''    if not valid:
        # Never show a fake/empty ad in live mode if credentials are incomplete.
        return base.replace('">','" style="display:none!important">',1)+'</aside>'
'''
ads_fallback='''    if not valid:
        return (
            base
            +'<span class="gsf-v1056-ad-kicker">Pubblicità</span>'
            +'<span class="gsf-v1056-ad-copy">Spazio annuncio responsive</span>'
            +'</aside>'
        )
'''
if ads_hidden in s:
    s=s.replace(ads_hidden,ads_fallback,1)

# 5) Standalone QC card is replaced by the unified progress flow.
s=s.replace(
    '.gsf-v124-quality{',
    '.gsf-v124-quality{display:none !important;',
    1,
)

# 6) Three cover-frame candidates in the space freed by Alternative AI / One Click AI.
cover_anchor='''            with st.container(key="gsf-major-create-short"):
'''
cover_ui=r'''            try:
                _v1302_source=Path(str(
                    st.session_state.get("gsf_source_path")
                    or st.session_state.get("gsf_editor_source_path")
                    or ""
                ))
                _v1302_start=float(st.session_state.get("auto_clip_scelta",0.0) or 0.0)
                _v1302_moment=_gsf_v124_moment_for_start(_v1302_start)
                _v1302_plan=dict((_v1302_moment or {}).get("director_plan") or {})
                _v1302_edit=dict(_v1302_plan.get("edit") or {})
                _v1302_rel=float(_v1302_edit.get("thumbnail_offset") or 0.0)
                _v1302_base=max(0.0,_v1302_start+_v1302_rel)
                _v1302_offsets=[
                    max(0.0,_v1302_base),
                    max(0.0,_v1302_base-1.15),
                    max(0.0,_v1302_base+1.15),
                ]
                if _v1302_source.is_file() and _v1302_source.stat().st_size>1024:
                    _v1302_thumb_root=Path(
                        __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
                    )/"sessions"/str(GSF_SESSION_ID)/"media"/"covers_v1302"
                    _v1302_thumb_root.mkdir(parents=True,exist_ok=True)
                    _v1302_paths=[]
                    _v1302_mod=__import__("cinematic_render_v125",fromlist=["extract_thumbnail"])
                    for _v1302_i,_v1302_off in enumerate(_v1302_offsets):
                        _v1302_p=_v1302_thumb_root/(
                            "cover_"+str(int(round(_v1302_start*1000)))+"_"+str(_v1302_i)+".jpg"
                        )
                        if not _v1302_p.is_file() or _v1302_p.stat().st_size<512:
                            try:
                                _v1302_mod.extract_thumbnail(
                                    str(_v1302_source),str(_v1302_p),
                                    offset_seconds=_v1302_off,width=520,
                                )
                            except Exception:
                                pass
                        if _v1302_p.is_file() and _v1302_p.stat().st_size>512:
                            _v1302_paths.append((_v1302_i,_v1302_p,_v1302_off))
                    if _v1302_paths:
                        st.markdown(
                            '<div class="gsf-icon-title">Scegli copertina</div>',
                            unsafe_allow_html=True,
                        )
                        _v1302_cols=st.columns(len(_v1302_paths),gap="small")
                        _v1302_selected=int(st.session_state.get("gsf_v1302_thumbnail_index",0) or 0)
                        for (_v1302_i,_v1302_p,_v1302_off),_v1302_col in zip(_v1302_paths,_v1302_cols):
                            with _v1302_col:
                                st.image(str(_v1302_p),use_container_width=True)
                                _v1302_label="SELEZIONATO" if _v1302_selected==_v1302_i else "SELEZIONA"
                                if st.button(
                                    _v1302_label,
                                    key=f"gsf_v1302_thumb_{_v1302_i}_{int(round(_v1302_start*1000))}",
                                    use_container_width=True,
                                    disabled=(_v1302_selected==_v1302_i),
                                ):
                                    st.session_state["gsf_v1302_thumbnail_index"]=_v1302_i
                                    st.session_state["gsf_v1302_thumbnail_offset"]=_v1302_off
                                    st.session_state["gsf_v1302_thumbnail_path"]=str(_v1302_p)
                                    st.rerun()
            except Exception as _v1302_thumb_exc:
                print("GSF_V1302_COVER_WARN",repr(str(_v1302_thumb_exc))[:220],flush=True)

'''
if cover_anchor not in s:
    raise RuntimeError("V130.2 create-short anchor missing")
s=s.replace(cover_anchor,cover_ui+cover_anchor,1)

# 7) Replace the old per-platform composer with one shared form + multi-select.
tree=ast.parse(s)
target=None
for node in ast.walk(tree):
    if not isinstance(node,ast.If):
        continue
    test=(ast.get_source_segment(s,node.test) or "").strip()
    body=ast.get_source_segment(s,node) or ""
    if test=="_has_final" and "social_selected_v59" in body and "_social_columns" in body:
        target=node
        break
if target is None:
    raise RuntimeError("V130.2 final social block not found")

indent=" "*(target.col_offset)
social_block=r'''def _gsf_v1302_youtube_short_bytes(video_bytes):
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
        _v1302_progress=32
        _v1302_progress_text="CREO SHORT · IA Quality Check · Pronto"
    elif _v1302_quality in ("","analyzing"):
        _v1302_progress=72
        _v1302_progress_text="Creo Short ✓ · IA QUALITY CHECK · Pronto"
    else:
        _v1302_progress=100
        _v1302_progress_text=(
            "Creo Short ✓ · IA Quality Check ✓ · SHORT PRONTO"
            if _v1302_quality in ("pass","warn")
            else "Creo Short ✓ · IA Quality Check ! · Controlla"
        )
    st.progress(_v1302_progress,text=_v1302_progress_text)
    if _v1302_quality in ("pass","warn") and _v1302_qscore is not None:
        st.caption("IA Quality Check · "+str(_v1302_qscore)+"/100")

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
        _v1302_title=st.text_input("Titolo",key=_v1302_title_key)
        _v1302_description=st.text_area(
            "Descrizione",key=_v1302_desc_key,height=120
        )
        _v1302_hashtags=st.text_input("Hashtag",key=_v1302_tags_key)

        _v1302_c1,_v1302_c2,_v1302_c3,_v1302_c4=st.columns(4,gap="small")
        with _v1302_c1:
            _v1302_youtube=st.checkbox("YouTube",key="gsf_v1302_target_youtube")
        with _v1302_c2:
            _v1302_tiktok=st.checkbox("TikTok",key="gsf_v1302_target_tiktok")
        with _v1302_c3:
            _v1302_instagram=st.checkbox("Instagram",key="gsf_v1302_target_instagram")
        with _v1302_c4:
            st.checkbox(
                "Facebook",
                key="gsf_v1302_target_facebook",
                value=False,
                disabled=True,
                help="Pubblicazione diretta Facebook in attesa dei permessi Meta Page.",
            )

        _v1302_targets=[]
        if _v1302_youtube:_v1302_targets.append("YouTube")
        if _v1302_tiktok:_v1302_targets.append("TikTok")
        if _v1302_instagram:_v1302_targets.append("Instagram")

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
'''
social_lines=social_block.splitlines()
social_block="\n".join(indent+line if line else "" for line in social_lines)+"\n"

lines=s.splitlines(keepends=True)
start=target.lineno-1
end=target.end_lineno
s="".join(lines[:start])+social_block+"".join(lines[end:])

# 8) Existing graphics only: normalize spacing, footer, hub opacity, upload centering.
layout_css=r'''
st.markdown("""
<style id="gsf-v1302-stability-layout">
.st-key-gsf-v125-ai-thumbnail,
[class*="st-key-gsf-v125-ai-thumbnail"]{
  display:none !important;
}
.gsf-icon-title{
  margin-top:20px !important;
  margin-bottom:10px !important;
}
.gsf-major-note{
  margin-top:7px !important;
  margin-bottom:15px !important;
}
.v67-ad,.gsf-v1056-ad,.gsf-v1057-ad{
  margin-top:24px !important;
  margin-bottom:24px !important;
}
.st-key-v73-upload-shell{
  margin-bottom:10px !important;
}
.st-key-v81_new_video{
  margin-top:2px !important;
  margin-bottom:16px !important;
}
.st-key-v73-upload-shell iframe{
  display:block !important;
  margin-left:auto !important;
  margin-right:auto !important;
}
.st-key-gsf_v1302_new_video_guard{
  width:min(760px,100%) !important;
  margin:8px auto 18px !important;
}
.st-key-v1055_social_composer_shared{
  margin-top:14px !important;
  padding:18px 18px 16px !important;
  border:1px solid rgba(116,154,184,.24) !important;
  border-radius:22px !important;
  background:linear-gradient(180deg,rgba(247,252,255,.96),rgba(255,255,255,.98)) !important;
  box-shadow:0 10px 28px rgba(36,85,125,.07) !important;
}
.st-key-v1055_social_composer_shared input,
.st-key-v1055_social_composer_shared textarea{
  border-radius:14px !important;
  border-color:#C7DCEB !important;
  background:#FFFFFF !important;
}
.st-key-v1055_social_composer_shared label{
  color:#29485F !important;
  font-weight:750 !important;
}
#gsf-creator-hub-portal-v107:has(.gsf-creator-hub-overlay.is-open){
  position:fixed !important;
  inset:0 !important;
  z-index:2147483600 !important;
  isolation:isolate !important;
}
#gsf-creator-hub-portal-v107 .gsf-creator-hub-overlay.is-open,
#gsf-creator-hub-portal-v107 .gsf-creator-hub-overlay:target{
  background:#EAF2F7 !important;
  opacity:1 !important;
  visibility:visible !important;
}
#gsf-creator-hub-portal-v107 .gsf-creator-hub-shell,
#gsf-creator-hub-portal-v107 .gsf-creator-hub-frame{
  opacity:1 !important;
  visibility:visible !important;
  filter:none !important;
}
.gsf-footer-v4{
  margin:2px auto 4px !important;
  padding:5px 6px 4px !important;
  gap:5px !important;
  min-height:0 !important;
}
.gsf-footer-v4 .bug-report{
  position:static !important;
  right:auto !important;
  bottom:auto !important;
  margin-top:1px !important;
}
[data-testid="stAppViewContainer"] .block-container{
  padding-bottom:.3rem !important;
}
@media(max-width:750px){
  .gsf-icon-title{
    margin-top:17px !important;
    margin-bottom:8px !important;
  }
  .gsf-major-note{
    margin-top:6px !important;
    margin-bottom:12px !important;
  }
  .v67-ad,.gsf-v1056-ad,.gsf-v1057-ad{
    margin-top:18px !important;
    margin-bottom:18px !important;
  }
  .st-key-v1055_social_composer_shared{
    padding:15px 13px 14px !important;
    border-radius:18px !important;
  }
  .gsf-footer-v4{
    margin:1px auto 3px !important;
    padding:4px 5px 3px !important;
    gap:4px !important;
  }
  [data-testid="stAppViewContainer"] .block-container{
    padding-left:.8rem !important;
    padding-right:.8rem !important;
    padding-bottom:.2rem !important;
  }
}
</style>
""",unsafe_allow_html=True)
'''

# Center upload-circle text inside the existing iframe without changing size.
s=s.replace(
    '.label{width:150px;text-align:center;font-size:17px;font-weight:800;line-height:1.2}',
    '.label{width:150px;min-height:42px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:17px;font-weight:800;line-height:1.2}',
)
s=s.replace(
    '.label{width:144px;font-size:16px}',
    '.label{width:144px;min-height:40px;font-size:16px}',
)

s=s.rstrip()+"\n\n"+layout_css.lstrip()
s=s.replace(
    "Gaming Shorts Factory · V130.1 Stability Hotfix",
    "Gaming Shorts Factory · V130.2 Stability UX",
)

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V130.2 Stability UX applied:",out)
