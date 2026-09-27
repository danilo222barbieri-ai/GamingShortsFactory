from pathlib import Path

p=Path('/app/GamingShortsFactory_V85_UPLOAD_CLEANUP.py')
s=p.read_text(encoding='utf-8')
print('=== V85 UPLOADER DIAGNOSTIC START ===')
needles=('v73-upload-shell','stFileUploader','stFileUploaderDropzone','v81_new_video')
for i,line in enumerate(s.splitlines(),1):
    if any(n in line for n in needles):
        print(f'{i}: {line}')
print('=== V85 UPLOADER DIAGNOSTIC END ===')
