from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.2 Upload Recovery' in s,'V98.2 marker')

# Upload must stay on the proven stable widget and flow.
need('key="upload_v73"' in s,'stable uploader key preserved')
need('video = st.file_uploader(' in s,'native Streamlit uploader preserved')
need('if _gsf_recovered_source is not None:' in s,'new-video action is conditional again')
need('_nv_left,_nv_center,_nv_right=st.columns([1,1,1])' in s,'new-video button centered without touching uploader')
need('gsf-v98-1-new-video-center' not in s,'unconditional V98.1 uploader-area CSS removed')
need('Sessione beta ripristinata automaticamente.' not in s,'session bubble stays removed')
need('gsf-v89-upload-visual' in s,'approved upload circle preserved')
need('gsf-v91-upload-status' in s,'upload status preserved')

# All editor hotfixes must survive.
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'subtitle VAI fallback fix preserved')
need('_main_recipe_selected=True' in s,'main editor apply fix preserved')
need('_inline_recipe_selected=True' in s,'inline editor apply fix preserved')
need('Per il player LIVE persistente serve una versione recente di Streamlit con Components V2.' not in s,'technical warning stays removed')
need('IN {_istart:.1f}s · OUT {_iend:.1f}s · DURATA {_ilen:.1f}s' not in s,'trim cloud stays removed')
need('ANTEPRIMA LIVE · queste regolazioni sono le stesse usate dal render finale.' not in s,'preview cloud stays removed')

# Production guardrails.
need('numero_clip=3' in s,'three AI clips preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final render quality preserved')
print('V98.2 upload recovery regression: PASS')
