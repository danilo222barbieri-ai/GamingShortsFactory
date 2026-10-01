from pathlib import Path

src=Path("/app/GamingShortsFactory_V129_AUTO_HIGHLIGHTS.py")
out=Path("/app/GamingShortsFactory_V130_ONE_CLICK_AI.py")
s=src.read_text(encoding="utf-8")

helper_anchor="def _gsf_v126_hook_for_start(start):\n"
helper=r'''
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


'''
if helper_anchor not in s:
    raise RuntimeError("V130 helper anchor missing")
s=s.replace(helper_anchor,helper+helper_anchor,1)

# Rank overrides happen after the Game Brain returns, so rebuild the one-click
# package after replacement logic to keep previews/editor/final render aligned.
override_anchor='''    try:
        _clean_events=[]
'''
override_add=r'''    try:
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

'''
if override_anchor not in s:
    raise RuntimeError("V130 override rebuild anchor missing")
s=s.replace(override_anchor,override_add+override_anchor,1)

recipe_anchor='''                            _recipe["ai_director_plan"]=_v125_plan
                            _recipe["ai_director_event"]=str((_v125_moment or {}).get("event") or "highlight")
                            _recipe["ai_director_rank"]=int((_v125_moment or {}).get("rank") or 0)
'''
recipe_replacement=recipe_anchor+r'''

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
'''
if recipe_anchor not in s:
    raise RuntimeError("V130 final recipe anchor missing")
s=s.replace(recipe_anchor,recipe_replacement,1)

create_anchor='''            with st.container(key="gsf-major-create-short"):
'''
one_click_ui=r'''            # V130 One Click AI: the three ranked moments are already
            # mounted as edit packages. Encoding remains lazy to avoid wasting
            # CPU/cloud cost on clips the creator will not publish.
            try:
                _v130_brain=st.session_state.get("gsf_v112_brain_context") or {}
                _v130_pack=dict(_v130_brain.get("one_click") or {}) if isinstance(_v130_brain,dict) else {}
                _v130_current_start=float(st.session_state.get("auto_clip_scelta",0.0) or 0.0)
                _v130_short=_gsf_v130_short_for_start(_v130_current_start)
                if _v130_pack.get("ready") and _v130_short:
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
                        '<div><b>ONE CLICK AI</b><span>'+str(_v130_count)+' Short preparati</span></div>'
                        '<small><strong>'+_v130_escape(_v130_event.upper())+' · '+str(_v130_conf)+'%</strong>'
                        ' · '+_v130_escape(_v130_feature_text)+'</small>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
            except Exception as _v130_ui_exc:
                print("GSF_V130_UI_WARN",repr(str(_v130_ui_exc))[:220],flush=True)

'''
if create_anchor not in s:
    raise RuntimeError("V130 create-short UI anchor missing")
s=s.replace(create_anchor,one_click_ui+create_anchor,1)

s += r'''
st.markdown("""
<style id="gsf-v130-one-click-style">
.gsf-v130-oneclick{
  max-width:760px;margin:16px auto 10px;padding:12px 14px;
  border:1px solid rgba(119,157,184,.25);border-radius:17px;
  background:linear-gradient(135deg,rgba(241,250,255,.90),rgba(246,242,255,.88));
  box-shadow:0 7px 22px rgba(73,108,136,.07)
}
.gsf-v130-oneclick>div{display:flex;gap:9px;align-items:baseline;flex-wrap:wrap}
.gsf-v130-oneclick b{font-size:11px;letter-spacing:.09em;color:#55748a}
.gsf-v130-oneclick span{font-size:12px;color:#7890a2;font-weight:800}
.gsf-v130-oneclick small{display:block;margin-top:5px;color:#6f8799;line-height:1.4}
.gsf-v130-oneclick small strong{color:#355a73}
</style>
""",unsafe_allow_html=True)
'''

s=s.replace(
    "Gaming Shorts Factory · V129 Auto Highlights",
    "Gaming Shorts Factory · V130 One Click AI",
)
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V130 One Click AI applied:",out)
