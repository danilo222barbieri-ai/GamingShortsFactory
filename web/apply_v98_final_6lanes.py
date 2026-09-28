from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_FINAL.py')
out=Path('/app/GamingShortsFactory_V98_FINAL_6LANES.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98 FINAL 6LANES target not found: {label}')
    s=s.replace(old,new,1)

replace_once(
'''const CHUNK=32*1024*1024;
const CONCURRENCY=4;
''',
'''const CHUNK=16*1024*1024;
const CONCURRENCY=6;
''',
'16MB x6 upload lanes')

s=s.replace(
    'Gaming Shorts Factory · V98 FINAL',
    'Gaming Shorts Factory · V98 FINAL 6LANES'
)

out.write_text(s,encoding='utf-8')
print(f'V98 FINAL 6LANES patch applied: {out}')
