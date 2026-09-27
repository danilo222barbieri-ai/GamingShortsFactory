from pathlib import Path

p=Path('/app/GamingShortsFactory_V88_PERSISTENT_LOADED_CIRCLE.py')
s=p.read_text(encoding='utf-8')
lines=s.splitlines()
needles=(
    'with st.container(key="v73-upload-shell"):',
    'st.markdown(_gsf_v86_upload_css',
    'st.markdown(_gsf_v88_loaded_circle_html',
    'video = st.file_uploader',
    'st.file_uploader(',
    'if video is not None:',
    'v81_new_video',
)
seen=[]
for i,line in enumerate(lines):
    if any(n in line for n in needles):
        if any(abs(i-j)<25 for j in seen):
            continue
        seen.append(i)
        a=max(0,i-35); b=min(len(lines),i+70)
        print(f'--- V88 FLOW {a+1}-{b} ---')
        for j in range(a,b):
            print(f'{j+1}: {lines[j]}')
print('--- V88 FLOW END ---')
