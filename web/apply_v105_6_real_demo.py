from pathlib import Path

src=Path('/app/GamingShortsFactory_V105_6_ADS_PREVIEW.py')
out=Path('/app/GamingShortsFactory_V105_6_DEMO_REAL.py')
s=src.read_text(encoding='utf-8')

anchor='\nif video:\n'
if anchor not in s:
    raise RuntimeError('Demo real anchor not found: top-level if video')

inject=r'''
# ==========================================================
# V105.6 REAL DEMO
# Production app/controls unchanged. Only the initial source,
# 3 AI candidates and already-rendered final Short are seeded.
# ==========================================================
import io as _gsf_demo_io

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
        # Feed the normal production flow with an UploadedFile-compatible
        # object only when no actual upload is present.
        if video is None:
            video=_GSFRealDemoUpload(
                _gsf_demo_source.read_bytes(),
                "demo_gameplay.mp4",
            )

        st.session_state.setdefault("gsf_source_path",str(_gsf_demo_source))
        st.session_state.setdefault("gsf_source_name","demo_gameplay.mp4")

        # Seed exactly once per Streamlit session. After this point engine
        # changes, Editor, subtitles, resets, candidate selection, final flow
        # and social buttons are the ordinary production code.
        if not st.session_state.get("_gsf_real_demo_seeded",False):
            _gsf_demo_clip_bytes=_gsf_demo_clip.read_bytes()
            _gsf_demo_final_bytes=_gsf_demo_final.read_bytes()

            # Default engine + already-computed AI result.
            st.session_state.setdefault("modalita_gsf","🚀 AUTO TOTALE")
            st.session_state["auto_clip_modalita"]="🚀 AUTO TOTALE"
            st.session_state["auto_clip_candidati"]=[8.0,28.0,48.0]
            st.session_state["auto_clip_scelta"]=8.0
            st.session_state["auto_clip_duration"]=15.0
            st.session_state["ai_director_scores"]=[
                (96.0,8.0),
                (91.0,28.0),
                (87.0,48.0),
            ]
            st.session_state["clip_rifinite"]={
                8.0:15.0,
                28.0:15.0,
                48.0:15.0,
            }

            # The selected first candidate is already materialized; choosing
            # another candidate follows the normal V105.6 path.
            st.session_state["preview_bytes"]=_gsf_demo_clip_bytes
            st.session_state["preview_key"]=None

            # Same state consumed by the ordinary final-result UI.
            st.session_state["gsf_final_recipe"]={
                "kind":"auto",
                "start":8.0,
                "duration":15.0,
                "source_path":str(_gsf_demo_source),
                "manual_hook":"",
            }
            st.session_state["publication_ready"]=True
            st.session_state["publication_source"]="AI"
            st.session_state["publication_preview_bytes"]=_gsf_demo_clip_bytes
            st.session_state["publication_final_bytes"]=_gsf_demo_final_bytes

            # Do NOT pre-open publishing or editors: those must be exercised
            # through the real production buttons to expose real bugs.
            st.session_state.pop("show_social_publish_v53",None)
            st.session_state.pop("show_social_publish_v54",None)
            st.session_state.pop("current_view",None)
            st.session_state.pop("inline_editor_id",None)

            st.session_state["_gsf_real_demo_seeded"]=True

        st.markdown(
            '<div style="margin:8px 0 14px;padding:10px 13px;border:1px solid #B9DCEF;'
            'border-radius:16px;background:#F1F9FE;color:#376B8A;font-size:13px;font-weight:750">'
            '🧪 DEMO FUNZIONALE · video, 3 momenti AI e Short finale sono già pronti. '
            'Pulsanti, Editor, sottotitoli, cambio motore e social usano la V105.6 reale.'
            '</div>',
            unsafe_allow_html=True,
        )
'''

s=s.replace(anchor,'\n'+inject+'\nif video:\n',1)
s=s.replace(
    'Gaming Shorts Factory · V105.6 Ads Preview',
    'Gaming Shorts Factory · V105.6 Functional Demo'
)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print('V105.6 functional demo applied:',out)
