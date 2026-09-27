from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit('usage: test_v86_uploader_patch.py <generated_app.py>')

s = Path(sys.argv[1]).read_text(encoding='utf-8')

assert 'gsf-v86-single-upload-circle' in s, 'V86 uploader CSS marker missing'
assert 'gsf-v83-upload-fix' not in s, 'V83 uploader CSS still present'
assert 'gsf-v84-centered-upload' not in s, 'V84 uploader CSS still present'
assert 'gsf-v85-upload-cleanup' not in s, 'V85 uploader CSS still present'
assert 'content:"Carica il tuo video"' in s, 'single-circle label missing'
assert 'content:"✓"' in s, 'uploaded success state missing'
assert 'border:0 !important' in s, 'outer dropzone reset missing'
assert '.st-key-v81_new_video' in s and 'justify-content:center !important' in s, 'new-video centering missing'
assert 'role="progressbar"' in s and '#22C55E' in s, 'green progress bar styling missing'
assert 'Beta mobile:' not in s, 'mobile beta caption still present'

print('V86 uploader structural tests: PASS')
