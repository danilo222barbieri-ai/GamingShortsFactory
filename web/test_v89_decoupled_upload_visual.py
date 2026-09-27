from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else '/app/GamingShortsFactory_V89_DECOUPLED_UPLOAD_VISUAL.py')
s=p.read_text(encoding='utf-8')

checks={
    'V89 visual function':'def _gsf_v89_upload_visual_html(loaded=False):' in s,
    'visual rendered inside uploader shell':'    st.markdown(_gsf_v89_upload_visual_html(video is not None), unsafe_allow_html=True)' in s,
    'native uploader invisible overlay':'opacity:0 !important;' in s and 'position:absolute !important;' in s,
    'persistent custom circle':'.gsf-v89-upload-visual{' in s,
    'loaded custom state':'.gsf-v89-upload-visual.is-loaded{' in s,
    'old V86 render call removed':'st.markdown(_gsf_v86_upload_css(video is not None), unsafe_allow_html=True)' not in s,
    'old V88 render call removed':'st.markdown(_gsf_v88_loaded_circle_html(), unsafe_allow_html=True)' not in s,
    'new video still present':'key="v81_new_video"' in s,
}
failed=[name for name,ok in checks.items() if not ok]
for name,ok in checks.items():
    print(('PASS' if ok else 'FAIL')+': '+name)
if failed:
    raise SystemExit('V89 regression failed: '+', '.join(failed))
print('V89 regression PASS')
