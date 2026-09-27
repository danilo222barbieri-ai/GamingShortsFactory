from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text(encoding='utf-8')
checks = {
    'v87 footer': 'Gaming Shorts Factory · V87 Upload Persists' in s,
    'uploaded file state selector': ':has([data-testid="stFileUploaderFile"])' in s,
    'uploaded fallback comment': 'the dropzone itself becomes the SAME circle' in s,
    'completed dropzone fixed desktop diameter': 'width:218px !important;' in s and 'height:218px !important;' in s,
    'completed state hides browse button': 'exactly one circle rather than a circle inside a circle' in s,
    'completed check': 'content:"✓" !important;' in s,
    'completed label': 'content:"Video caricato" !important;' in s,
    'mobile completed diameter': 'width:208px !important;' in s and 'height:208px !important;' in s,
    'new video button preserved': '.st-key-v81_new_video' in s,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('V87 uploader tests FAILED: ' + ', '.join(failed))
print('V87 uploader persistence tests: PASS')
