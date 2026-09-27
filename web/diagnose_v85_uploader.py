from pathlib import Path

p=Path('/app/GamingShortsFactory_V85_UPLOAD_CLEANUP.py')
s=p.read_text(encoding='utf-8')
lines=s.splitlines()
print('=== V85 UPLOADER DIAGNOSTIC START ===')
needles=('v73-upload-shell','stFileUploader','stFileUploaderDropzone','v81_new_video')
for i,line in enumerate(lines,1):
    if any(n in line for n in needles):
        print(f'{i}: {line}')
print('=== V85 UPLOAD FLOW 8975-9045 ===')
for i in range(8975, min(9046,len(lines)+1)):
    print(f'{i}: {lines[i-1]}')
print('=== V85 APPENDED CSS POSITION ===')
for i,line in enumerate(lines,1):
    if 'gsf-v85-upload-cleanup' in line:
        print(f'V85 CSS marker at line {i}')
print('=== V85 UPLOADER DIAGNOSTIC END ===')
