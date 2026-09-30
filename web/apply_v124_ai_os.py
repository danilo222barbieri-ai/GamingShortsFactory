from pathlib import Path

src=Path("/app/GamingShortsFactory_V113_GUARDIAN.py")
out=Path("/app/GamingShortsFactory_V124_AI_OS.py")
s=src.read_text(encoding="utf-8")

# V124 anonymous product-learning feedback helper.
_feedback_import_anchor="import streamlit as st\n"
_feedback_helper=r'''
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
'''
if _feedback_import_anchor not in s:
    raise RuntimeError("V124 feedback import anchor missing")
s=s.replace(_feedback_import_anchor,_feedback_import_anchor+_feedback_helper,1)

# ------------------------------------------------------------------
# V124 product-learning action signals.
# ------------------------------------------------------------------
_choice_anchor='''                                    st.session_state.auto_clip_scelta=float(_card["start"])
                                    st.session_state["auto_clip_duration"]=float(_card["preview_duration"])
'''
_choice_replacement='''                                    _gsf_v124_feedback(
                                        _gsf_v124_moment_for_start(float(_card["start"])),
                                        "selected",
                                    )
                                    st.session_state.auto_clip_scelta=float(_card["start"])
                                    st.session_state["auto_clip_duration"]=float(_card["preview_duration"])
'''
if _choice_anchor not in s:
    raise RuntimeError("V124 selected-moment feedback anchor missing")
s=s.replace(_choice_anchor,_choice_replacement,1)

_editor_anchor='''                    if _gsf_open_game_editor:
                        _selected_sub_key=f"v71_auto_sub_{int(_selected_card['index'])}"
'''
_editor_replacement='''                    if _gsf_open_game_editor:
                        _gsf_v124_feedback(
                            _gsf_v124_moment_for_start(float(start)),
                            "opened_editor",
                        )
                        _selected_sub_key=f"v71_auto_sub_{int(_selected_card['index'])}"
'''
if _editor_anchor not in s:
    raise RuntimeError("V124 Editor feedback anchor missing")
s=s.replace(_editor_anchor,_editor_replacement,1)

_publish_anchor='''                                _ok, _message, _path = _gsf_publish_social_upload(
                                    _final_video,
                                    _selected_social,
                                    pack_override=_edited_pack,
                                )
'''
_publish_replacement=_publish_anchor+'''                            if _ok:
                                try:
                                    _v124_recipe=st.session_state.get("gsf_final_recipe",{}) or {}
                                    _gsf_v124_feedback(
                                        _gsf_v124_moment_for_start(float(_v124_recipe.get("start",0.0) or 0.0)),
                                        "published",
                                    )
                                except Exception:
                                    pass
'''
if _publish_anchor not in s:
    raise RuntimeError("V124 published feedback anchor missing")
s=s.replace(_publish_anchor,_publish_replacement,1)

# ------------------------------------------------------------------
# V124 AI OS: social copy from the exact Director plan of the selected
# moment. V105.5 intentionally created an empty connected composer; V124
# seeds the Streamlit widget keys only once so manual user edits always win.
# ------------------------------------------------------------------
social_anchor='''                        _ctx = _gsf_publish_context_token(_base_pack)
                        _slug = _selected_social.lower()

                        with st.container(key=f"v1055_social_composer_{_slug}"):
'''
social_replacement='''                        _ctx = _gsf_publish_context_token(_base_pack)
                        _slug = _selected_social.lower()

                        # V124 AI Director social optimizer.
                        try:
                            _ai_platform_key=str(_selected_social or "").strip().lower()
                            _ai_social_all={}
                            _brain=st.session_state.get("gsf_v112_brain_context") or {}
                            _rows=list(_brain.get("selected") or []) if isinstance(_brain,dict) else []
                            if _rows:
                                _nearest=min(
                                    _rows,
                                    key=lambda row:abs(float((row or {}).get("start") or 0.0)-float(_start))
                                )
                                _plan=dict((_nearest or {}).get("director_plan") or {})
                                _ai_social_all=dict(((_plan.get("text") or {}).get("social") or {}))
                            if not _ai_social_all:
                                _ai_social_all=st.session_state.get("gsf_v124_social_pack") or {}
                            _ai_social=(
                                _ai_social_all.get(_ai_platform_key)
                                if isinstance(_ai_social_all,dict)
                                else None
                            ) or {}
                            if isinstance(_ai_social,dict) and _ai_social:
                                _ai_title_key=f"social_title_{_slug}_{_ctx}"
                                _ai_description_key=f"social_description_{_slug}_{_ctx}"
                                _ai_hashtags_key=f"social_hashtags_{_slug}_{_ctx}"
                                _ai_title=str(_ai_social.get("title") or "").strip()
                                _ai_description=str(_ai_social.get("description") or "").strip()
                                _ai_hashtags=" ".join(
                                    str(x) for x in (_ai_social.get("hashtags") or [])
                                    if str(x).strip()
                                )
                                if _ai_title_key not in st.session_state and _ai_title:
                                    st.session_state[_ai_title_key]=_ai_title
                                if _ai_description_key not in st.session_state and _ai_description:
                                    st.session_state[_ai_description_key]=_ai_description
                                if _ai_hashtags_key not in st.session_state and _ai_hashtags:
                                    st.session_state[_ai_hashtags_key]=_ai_hashtags
                        except Exception as _v124_social_exc:
                            print("GSF_V124_SOCIAL_WARN",repr(str(_v124_social_exc)),flush=True)

                        with st.container(key=f"v1055_social_composer_{_slug}"):
'''
if social_anchor not in s:
    raise RuntimeError("V124 V105.5 social composer anchor missing")
s=s.replace(social_anchor,social_replacement,1)

# ------------------------------------------------------------------
# V124 AI Quality status. The heavy video inspection runs in the direct
# upload sidecar; Streamlit only reads the result.
# ------------------------------------------------------------------
quality_ui=r'''
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

st.markdown("""
<style id="gsf-v124-ai-os-style">
.gsf-v124-quality{
    max-width:760px;
    margin:18px auto 12px;
    padding:14px 16px;
    border-radius:18px;
    border:1px solid rgba(132,164,186,.28);
    background:rgba(248,252,255,.92);
    box-shadow:0 8px 24px rgba(71,107,132,.08);
    display:flex;
    align-items:center;
    gap:12px;
    flex-wrap:wrap;
}
.gsf-v124-quality b{
    font-size:12px;
    letter-spacing:.08em;
    color:#547287;
}
.gsf-v124-quality span{
    font-weight:800;
    color:#23445d;
}
.gsf-v124-quality small{
    flex-basis:100%;
    color:#708797;
    line-height:1.35;
}
.gsf-v124-quality-pass{border-color:rgba(84,168,128,.28)}
.gsf-v124-quality-warn{border-color:rgba(222,171,75,.34)}
.gsf-v124-quality-fail{border-color:rgba(211,104,104,.34)}
.gsf-v124-score{margin-left:auto}
</style>
""",unsafe_allow_html=True)
# ===== /V124 AI QUALITY UI =====
'''

s=s.rstrip()+"\n\n"+quality_ui.lstrip()

# Keep the visible app generation explicit.
s=s.replace("Gaming Shorts Factory · V112","Gaming Shorts Factory · V124 AI OS")
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V124 AI OS applied:",out)
