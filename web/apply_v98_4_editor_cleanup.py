from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_3_HOME_COMPACT.py')
out=Path('/app/GamingShortsFactory_V98_4_EDITOR_CLEANUP.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.4 patch target not found: {label}')
    s=s.replace(old,new,1)

replace_once(
'''                                    st.caption("Zoom e posizione vengono applicati identici al render.")
''',
'',
'remove framing info cloud')

replace_once(
'''                                    st.caption("Audio, immagine e velocità restano sincronizzati con la preview.")
''',
'',
'remove adjustments info cloud')

s=s.replace(
    'Gaming Shorts Factory · V98.3 Home Compact',
    'Gaming Shorts Factory · V98.4 Editor Cleanup'
)

out.write_text(s,encoding='utf-8')
print(f'V98.4 patch applied: {out}')
