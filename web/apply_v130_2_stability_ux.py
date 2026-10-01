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

# 6) Cover is intentionally not a standalone gallery in V130.2.
# It will live as a compact control associated with the final player.
cover_anchor='''            with st.container(key="gsf-major-create-short"):\n'''
if cover_anchor not in s:
    raise RuntimeError("V130.2 create-short anchor missing")
create_note='''            with st.container(key="gsf-major-create-short"):\n                st.markdown('<div class="gsf-major-note gsf-v1302-create-note">L’IA crea il tuo Short, applica le modifiche e controlla automaticamente qualità e formato. Quando è pronto puoi salvarlo, condividerlo o pubblicarlo.</div>',unsafe_allow_html=True)\n'''
s=s.replace(cover_anchor,create_note,1)
# The explanatory cloud above CREA SHORT is the only create-final guidance.
s=s.replace('<div class="gsf-major-note">Genera la versione finale pronta per il download e la pubblicazione sui tuoi social collegati.</div>','',1)

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
.gsf-v1302-social-pick{margin:12px 0 8px;text-align:center;color:#53758e;font-weight:800;font-size:13px}
[class*="st-key-gsf_v1302_icon_"]{display:flex!important;justify-content:center!important}
[class*="st-key-gsf_v1302_icon_"] button{width:64px!important;min-width:64px!important;max-width:64px!important;height:64px!important;min-height:64px!important;padding:0!important;border-radius:18px!important;border:1px solid rgba(138,174,199,.48)!important;background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(241,247,252,.96))!important;color:#53758e!important;box-shadow:0 9px 20px rgba(49,92,125,.10)!important;font-size:26px!important;font-weight:850!important}
[class*="st-key-gsf_v1302_icon_"] button:hover{transform:translateY(-2px)!important;color:#4f46e5!important;border-color:rgba(99,102,241,.52)!important;box-shadow:0 12px 24px rgba(79,70,229,.12)!important}
.gsf-v1302-live-progress{margin:14px 0 12px;padding:14px 16px 15px;border:1px solid rgba(126,165,193,.34);border-radius:20px;background:linear-gradient(145deg,rgba(250,253,255,.98),rgba(238,247,252,.94));box-shadow:0 10px 28px rgba(46,94,128,.09);overflow:hidden}
.gsf-v1302-progress-steps{display:flex;align-items:center;justify-content:space-between;gap:7px;font-size:12px;font-weight:850;letter-spacing:.035em;color:#91a8b8}.gsf-v1302-progress-steps i{font-style:normal;color:#bdd0dd}.gsf-v1302-progress-steps .active{color:#397b9f;animation:gsfPulse 1.35s ease-in-out infinite}.gsf-v1302-progress-steps .done{color:#2d718f}.gsf-v1302-progress-track{position:relative;height:9px;margin-top:12px;border-radius:999px;background:rgba(173,204,222,.32);overflow:hidden}.gsf-v1302-progress-track span{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,#8ed8ee,#68bde4,#a9dfe9);background-size:180% 100%;box-shadow:0 0 16px rgba(75,174,218,.42);animation:gsfFlow 1.45s linear infinite;transition:width .55s ease}.gsf-v1302-live-progress.ready .gsf-v1302-progress-track span{animation:none}.gsf-v1302-live-progress:not(.ready) .gsf-v1302-progress-track:after{content:"";position:absolute;top:0;bottom:0;width:32%;left:-35%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.75),transparent);animation:gsfShine 1.55s ease-in-out infinite}@keyframes gsfFlow{to{background-position:-180% 0}}@keyframes gsfShine{to{left:110%}}@keyframes gsfPulse{50%{opacity:.52}}
.st-key-gsf_v1302_save button,.st-key-gsf_v1302_share_wait button,.st-key-gsf_v1302_share_fallback button{height:44px!important;border-radius:14px!important;border:1px solid rgba(138,174,199,.48)!important;background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(241,247,252,.96))!important;color:#53758e!important;font-size:24px!important;box-shadow:0 8px 18px rgba(49,92,125,.08)!important}
.gsf-v1302-create-note{border:1px dashed #bfd7e8;border-radius:16px;padding:10px 12px;background:rgba(244,250,254,.78);color:#55758c}
[class*="st-key-gsf_share_download_top"]{display:none !important;}
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
.st-key-v81_new_video{
  display:flex !important;
  justify-content:center !important;
  width:100% !important;
}
.st-key-v81_new_video > div,
.st-key-v81_new_video [data-testid="stButton"]{
  width:auto !important;
  margin-left:auto !important;
  margin-right:auto !important;
}
.gsf-footer-v4{
  margin:0 auto 2px !important;
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
  [class*="st-key-gsf_v1302_icon_"] button{width:58px!important;min-width:58px!important;max-width:58px!important;height:58px!important;min-height:58px!important;border-radius:17px!important}
  .gsf-v1302-progress-steps{font-size:10px!important;gap:4px!important;letter-spacing:.02em!important}
  .gsf-footer-v4{
    margin:-8px auto 0 !important;
    padding:2px 4px 1px !important;
    gap:2px !important;
    line-height:1.05 !important;
  }
  .gsf-footer-v4 .socials{
    margin:1px 0 !important;
    gap:5px !important;
  }
  .gsf-footer-v4 .socials a{
    width:34px !important;
    height:34px !important;
  }
  .gsf-footer-v4 .bug-report{
    margin-top:0 !important;
    line-height:1 !important;
  }
  .gsf-v1056-ad:last-of-type,
  .gsf-v1057-ad:last-of-type,
  .v67-ad:last-of-type{
    margin-bottom:4px !important;
  }
  [data-testid="stAppViewContainer"] .block-container{
    padding-left:.8rem !important;
    padding-right:.8rem !important;
    padding-bottom:0 !important;
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
