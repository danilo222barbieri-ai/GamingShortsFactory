from pathlib import Path

src=Path("/app/GamingShortsFactory_V113_GUARDIAN.py")
out=Path("/app/GamingShortsFactory_V124_AI_OS.py")
s=src.read_text(encoding="utf-8")

# ------------------------------------------------------------------
# V124 AI OS: social copy from the exact Director plan of the selected
# moment instead of generic/stale copy.
# ------------------------------------------------------------------
social_anchor='''                    _default_title = str(_base_pack.get("selected_title",_base_pack.get("title","")) or "")
                    _default_description = _gsf_social_clean_description(_base_pack)
                    _default_hashtags = " ".join(_base_pack.get("hashtags",[]) or [])
'''
social_replacement=social_anchor+'''                    # V124 AI Director social optimizer.
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
                            _ai_title=str(_ai_social.get("title") or "").strip()
                            _ai_description=str(_ai_social.get("description") or "").strip()
                            _ai_hashtags=list(_ai_social.get("hashtags") or [])
                            if _ai_title:
                                _default_title=_ai_title
                            if _ai_description:
                                _default_description=_ai_description
                            if _ai_hashtags:
                                _default_hashtags=" ".join(str(x) for x in _ai_hashtags if str(x).strip())
                    except Exception as _v124_social_exc:
                        print("GSF_V124_SOCIAL_WARN",repr(str(_v124_social_exc)),flush=True)
'''
if social_anchor not in s:
    raise RuntimeError("V124 social default anchor missing")
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
