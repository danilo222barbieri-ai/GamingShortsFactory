from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text(encoding='utf-8')

checks = {
    'v88 footer': 'Gaming Shorts Factory · V88 Persistent Loaded Circle' in s,
    'server-side loaded-state branch': 'if video is not None:\n    st.markdown(_gsf_v88_loaded_circle_html()' in s,
    'dedicated loaded circle html': 'gsf-v88-loaded-circle' in s,
    'loaded state check': '<span class="gsf-v88-loaded-check">✓</span>' in s,
    'loaded state label': '<span class="gsf-v88-loaded-label">Video caricato</span>' in s,
    'native uploader hidden only when loaded marker css is present': '.st-key-v73-upload-shell [data-testid="stFileUploader"]{display:none !important;}' in s,
    'desktop loaded diameter': 'width:218px;' in s and 'height:218px;' in s,
    'mobile loaded diameter': 'width:208px;' in s and 'height:208px;' in s,
    'new video button preserved': 'key="v81_new_video"' in s,
}

failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('V88 persistent loaded circle tests FAILED: ' + ', '.join(failed))
print('V88 persistent loaded circle tests: PASS')
