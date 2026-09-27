from pathlib import Path

src=Path('/app/GamingShortsFactory_V83_UPLOAD_FIX.py')
s=src.read_text(encoding='utf-8')
lines=s.splitlines()
needles=('127.0.0.1','_gsf_serve_path','_video_url','GSF_PREVIEW_PORT','components.html','<video','video_url','served_name')
seen=set()
for i,line in enumerate(lines):
    if any(n in line for n in needles):
        a=max(0,i-4); b=min(len(lines),i+7)
        key=(a,b)
        if key in seen:
            continue
        seen.add(key)
        print(f'--- V84 DIAG lines {a+1}-{b} ---')
        for j in range(a,b):
            print(f'{j+1}: {lines[j]}')
print('--- V84 DIAG END ---')
raise RuntimeError('V84_DIAGNOSTIC_COMPLETE')
