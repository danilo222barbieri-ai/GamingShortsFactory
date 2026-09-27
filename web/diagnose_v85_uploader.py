from pathlib import Path

p=Path('/app/GamingShortsFactory_V85_UPLOAD_CLEANUP.py')
s=p.read_text(encoding='utf-8')
lines=s.splitlines()
print('=== V85 UPLOADER DIAGNOSTIC START ===')
for i,line in enumerate(lines,1):
    if 'st.stop(' in line or 'st.rerun(' in line:
        print(f'FLOW-CONTROL {i}: {line}')
for i,line in enumerate(lines,1):
    if 'gsf-v85-upload-cleanup' in line:
        print(f'V85 CSS marker at line {i}')
print('=== V85 UPLOADER DIAGNOSTIC END ===')
