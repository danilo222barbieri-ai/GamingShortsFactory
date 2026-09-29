from pathlib import Path
import re

src=Path('/app/GamingShortsFactory_V105_6_ADS_PREVIEW.py')
out=Path('/app/GamingShortsFactory_V105_6_DEMO_REAL.py')
s=src.read_text(encoding='utf-8')

anchor='\nif video:\n'
if anchor not in s:
    raise RuntimeError('Demo real anchor not found: top-level if video')

inject=r'''
# ==========================================================
# V105.6 REAL DEMO
# Same production app and controls; only initial media/results
# are preloaded so UI/functional bugs can be tested quickly.
# ==========================================================
_GSF_REAL_DEMO = str(os.environ.get("GSF_REAL_DEMO","0") or "0").strip().lower() in {"1","true","yes","on"}

class _GSFRealDemoUpload(_gsf_demo_io.BytesIO):
    def __init__(self, data, name):
        super().__init__(data)
        self.name=str(name)
        self.size=len(data)

if _GSF_REAL_DEMO:
    _gsf_demo_source=Path("/app/demo_assets/demo_gameplay.mp4")
    _gsf_demo_clip=Path("/app/demo_assets/demo_clip.mp4")
    _gsf_demo_final=Path("/app/demo_assets/demo_final.mp4")

    if not (_gsf_demo_source.is_file() and _gsf_demo_clip.is_file() and _gsf_demo_final.is_file()):
        st.error("Demo media non disponibili.")
    else:
        # Keep every ordinary production control/function. We only provide an
        # UploadedFile-compatible source when the session has no user upload.
        _gsf_demo_source_bytes=_gsf_demo_source.read_bytes()
        if video is None:
            video=_GSFRealDemoUpload(_gsf_demo_source_bytes,"demo_gameplay.mp4")

        st.session_state.setdefault("gsf_source_path",str(_gsf_demo_source))
        st.session_state.setdefault("gsf_source_name","demo_gameplay.mp4")

        # Seed once. After that, buttons and reset logic are fully production code.
        if not st.session_state.get("_gsf_real_demo_seeded",False):
            _gsf_demo_clip_bytes=_gsf_demo_clip.read_bytes()
            _gsf_demo_final_bytes=_gsf_demo_final.read_bytes()

            st.session_state["modalita_gsf"]="🚀 AUTO TOTALE"
            st.session_state["auto_clip_modalita"]="🚀 AUTO TOTALE"
            st.session_state["auto_clip_candidati"]=[8.0,28.0,48.0]
            st.session_state["auto_clip_scelta"]=8.0
            st.session_state["auto_clip_duration"]=15.0
            st.session_state["ai_director_scores"]=[
                (96.0,8.0),(91.0,28.0),(87.0,48.0)
            ]
            st.session_state["clip_rifinite"]={
                8.0:15.0,28.0:15.0,48.0:15.0
            }

            # First selected AI preview is already ready.
            st.session_state["preview_bytes"]=_gsf_demo_clip_bytes
            st.session_state["preview_key"]="demo_gameplay.mp4_8.00_15.00"

            # Seed the same final-flow state used by the real app.
            st.session_state["publication_ready"]=True
            st.session_state["publication_source"]="ai_clip"
            st.session_state["publication_preview_bytes"]=_gsf_demo_clip_bytes
            st.session_state["gsf_final_recipe"]={
                "kind":"auto",
                "start":8.0,
                "duration":15.0,
                "source_path":str(_gsf_demo_source),
                "manual_hook":"",
            }
            st.session_state["publication_final_bytes"]=_gsf_demo_final_bytes
            st.session_state["final_video_bytes"]=_gsf_demo_final_bytes
            st.session_state["gsf_final_bytes"]=_gsf_demo_final_bytes
            st.session_state["show_social_publish_v54"]=True
            st.session_state["social_selected_v59"]="YouTube"
            st.session_state["_gsf_real_demo_seeded"]=True

        st.markdown(
            '<div style="margin:8px 0 14px;padding:10px 13px;border:1px solid #B9DCEF;'
            'border-radius:16px;background:#F1F9FE;color:#376B8A;font-size:13px;font-weight:750">'
            '🧪 DEMO REALE · video, 3 momenti AI e Short finale sono già pronti. '
            'Tutti gli altri controlli usano il codice della V105.6.'
            '</div>',
            unsafe_allow_html=True,
        )

'''

s=s.replace(anchor,'\n'+inject+'\nif video:\n',1)
s=s.replace(
    'Gaming Shorts Factory · V105.6 Ads Preview',
    'Gaming Shorts Factory · V105.6 Real Demo'
)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print('V105.6 real demo applied:',out)
