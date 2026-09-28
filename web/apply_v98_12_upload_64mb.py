from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_11_SPEED_ALL.py')
out=Path('/app/GamingShortsFactory_V98_12_UPLOAD_64MB.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.12 target not found: {label}')
    s=s.replace(old,new,1)

replace_once(
'''const CHUNK=32*1024*1024;
const CONCURRENCY=2;
''',
'''const CHUNK=64*1024*1024;
const CONCURRENCY=2;
''',
'64MB upload chunk')

s=s.replace(
    'Gaming Shorts Factory · V98.11 Speed All',
    'Gaming Shorts Factory · V98.12 Upload 64MB'
)

out.write_text(s,encoding='utf-8')
print(f'V98.12 upload-64MB patch applied: {out}')
