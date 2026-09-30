from pathlib import Path

src=Path("/app/GamingShortsFactory_V125_CINEMATIC_AI.py")
out=Path("/app/GamingShortsFactory_V126_CREATIVE_DIRECTOR.py")
s=src.read_text(encoding="utf-8")

# ------------------------------------------------------------------
# 1) Director hook: manual user copy always wins. Explicit OFF always wins.
#    Only an empty automatic hook is filled from the semantic Director plan.
# ------------------------------------------------------------------
helper_anchor='''def _gsf_v124_moment_for_start(start):
    try:
        _brain=st.session_state.get("gsf_v112_brain_context") or {}
        _rows=list(_brain.get("selected") or []) if isinstance(_brain,dict) else []
        if not _rows:
            return {}
        _start=float(start or 0.0)
        return dict(min(_rows,key=lambda row:abs(float((row or {}).get("start") or 0.0)-_start)) or {})
    except Exception:
        return {}
'''
helper_add=r'''
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
'''
if helper_anchor not in s:
    raise RuntimeError("V126 V124 moment helper anchor missing")
s=s.replace(helper_anchor,helper_anchor+helper_add,1)

old_hook='''manual_hook=(
                                        st.session_state.get("hook_testo","")
                                        if st.session_state.get("hook_enabled_v102",True)
                                        else _GSF_HOOK_OFF_V102
                                    )'''
new_hook='''manual_hook=_gsf_v126_hook_for_start(float(_card["start"]))'''
if s.count(old_hook)<2:
    raise RuntimeError("V126 auto hook recipe anchors missing")
s=s.replace(old_hook,new_hook,2)

# ------------------------------------------------------------------
# 2) Event-aware sound design. Video is stream-copied; only audio is filtered.
#    Cinematic output remains the fallback source if sound design fails.
# ------------------------------------------------------------------
stable_anchor='''                        __import__("shutil").copyfile(_v125_final_source,_tmp_video)
                        __import__("os").replace(_tmp_video,_gsf_stable)

                        # AI thumbnail: choose the event frame from the clean render,
'''
stable_replacement='''                        _v126_final_source=_v125_final_source
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

                        __import__("shutil").copyfile(_v126_final_source,_tmp_video)
                        __import__("os").replace(_tmp_video,_gsf_stable)
                        try:
                            _v126_audio_tmp.unlink(missing_ok=True)
                        except Exception:
                            pass

                        # AI thumbnail: choose the event frame from the clean render,
'''
if stable_anchor not in s:
    raise RuntimeError("V126 V125 stable-copy anchor missing")
s=s.replace(stable_anchor,stable_replacement,1)

s=s.replace("Gaming Shorts Factory · V125 Cinematic AI","Gaming Shorts Factory · V126 Creative Director")
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V126 Creative Director applied:",out)
