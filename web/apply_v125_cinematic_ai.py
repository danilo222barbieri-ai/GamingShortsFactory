from pathlib import Path

src=Path("/app/GamingShortsFactory_V124_AI_OS.py")
out=Path("/app/GamingShortsFactory_V125_CINEMATIC_AI.py")
s=src.read_text(encoding="utf-8")

# ------------------------------------------------------------------
# 1) Persist the Director plan inside the locked final-render recipe.
# ------------------------------------------------------------------
queue_anchor='''                _recipe=st.session_state.get("gsf_final_recipe")
                if isinstance(_recipe,dict) and _recipe:
                    st.session_state["gsf_v107_render_recipe_snapshot"]=dict(_recipe)
'''
queue_replacement='''                _recipe=st.session_state.get("gsf_final_recipe")
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
                            st.session_state["gsf_final_recipe"]=_recipe
                    except Exception as _v125_recipe_exc:
                        print("GSF_V125_PLAN_RECIPE_WARN",repr(str(_v125_recipe_exc))[:220],flush=True)
                    st.session_state["gsf_v107_render_recipe_snapshot"]=dict(_recipe)
'''
if queue_anchor not in s:
    raise RuntimeError("V125 final recipe queue anchor missing")
s=s.replace(queue_anchor,queue_replacement,1)

# ------------------------------------------------------------------
# 2) Real alternative replacement UI. It sets a persistent rank override;
#    the next rerun recomputes the true 3-moment ranking with that alternate.
# ------------------------------------------------------------------
create_anchor='''            with st.container(key="gsf-major-create-short"):
'''
alternatives=r'''            # V125 AI alternatives: replace the currently selected rank for real.
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
                if _v125_rank>0 and _v125_alternates:
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

'''
if create_anchor not in s:
    raise RuntimeError("V125 create-short UI anchor missing")
s=s.replace(create_anchor,alternatives+create_anchor,1)

# ------------------------------------------------------------------
# 3) Cinematic post-process only after the normal final render succeeded.
#    Fail-safe: original base render is always used if AI cinematic fails.
# ------------------------------------------------------------------
stable_anchor='''                        _tmp_video=_gsf_stable.with_suffix(".mp4.tmp")
                        __import__("shutil").copyfile(_gsf_out,_tmp_video)
                        __import__("os").replace(_tmp_video,_gsf_stable)
'''
stable_replacement='''                        _tmp_video=_gsf_stable.with_suffix(".mp4.tmp")
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
                        __import__("shutil").copyfile(_v125_final_source,_tmp_video)
                        __import__("os").replace(_tmp_video,_gsf_stable)

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
'''
if stable_anchor not in s:
    raise RuntimeError("V125 stable-final copy anchor missing")
s=s.replace(stable_anchor,stable_replacement,1)

# UI polish for alternatives.
s += r'''
st.markdown("""
<style id="gsf-v125-cinematic-ai-style">
.gsf-v125-alt-head{
  max-width:760px;margin:18px auto 10px;padding:12px 15px;
  border:1px solid rgba(123,158,183,.24);border-radius:17px;
  background:rgba(247,251,254,.82);display:flex;gap:9px;
  align-items:baseline;flex-wrap:wrap
}
.gsf-v125-alt-head b{font-size:12px;letter-spacing:.08em;color:#55778d}
.gsf-v125-alt-head span{font-size:13px;color:#7690a2}
</style>
""",unsafe_allow_html=True)
'''

s=s.replace("Gaming Shorts Factory · V124 AI OS","Gaming Shorts Factory · V125 Cinematic AI")
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V125 Cinematic AI applied:",out)

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
                st.image(str(_v125_thumb_path),use_container_width=False,width=270)
except Exception:
    pass

st.markdown("""
<style id="gsf-v125-thumb-style">
.gsf-v125-thumb-title{
  max-width:760px;margin:16px auto 8px;display:flex;align-items:baseline;
  gap:9px;flex-wrap:wrap;color:#708797
}
.gsf-v125-thumb-title b{font-size:12px;letter-spacing:.08em;color:#527389}
.gsf-v125-thumb-title span{font-size:13px}
div[data-testid="stImage"]{margin-left:auto;margin-right:auto}
</style>
""",unsafe_allow_html=True)
# ===== /V125 AI THUMBNAIL PREVIEW =====
