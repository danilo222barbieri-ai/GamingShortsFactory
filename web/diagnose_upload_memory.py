from pathlib import Path
p=Path('/app/GamingShortsFactory_V98_7_NEW_VIDEO_FIX.py')
lines=p.read_text(encoding='utf-8').splitlines()
patterns=(
    'def _gsf_materialize_upload_once',
    'WhisperModel',
    'faster_whisper',
    '@st.cache_resource',
    'getvalue(',
    'getbuffer(',
    '.read(',
    'st.cache_resource.clear',
    'gc.collect',
    'model_size',
    'compute_type',
)
hits=set()
for i,line in enumerate(lines):
    if any(pat in line for pat in patterns):
        for j in range(max(0,i-8),min(len(lines),i+28)):
            hits.add(j)
for j in sorted(hits):
    print(f'V98MEM {j+1}: {lines[j]}')
