from pathlib import Path

p=Path('/app/GamingShortsFactory_V90_UPLOAD_VISUAL_FIX.py')
s=p.read_text(encoding='utf-8')
lines=s.splitlines()

markers=[
    'def render_gsf_editor_live_player',
    'editor_start',
    'editor_len',
    'editor_zoom',
    'editor_speed',
    'editor_volume',
    'editor_brightness',
    'editor_contrast',
    'editor_format',
    'INQUADRATURA',
    'REGOLAZIONI',
    'Momento migliore',
    'Più azione',
    'Reazioni',
    'Automatico',
    'CREA CON AI',
    'editor_use_changes_v54',
    'subtitle_mode',
]
seen=set()
for marker in markers:
    hits=[i for i,l in enumerate(lines) if marker in l]
    if not hits:
        print(f'V91DIAG MISSING {marker}')
        continue
    # cap noisy markers to 3 occurrences
    for i in hits[:3]:
        key=(marker,i)
        if key in seen: continue
        seen.add(key)
        a=max(0,i-18); b=min(len(lines),i+42)
        print(f'--- V91DIAG {marker} line {i+1} ---')
        for j in range(a,b):
            print(f'{j+1}: {lines[j]}')
        print('--- END ---')
