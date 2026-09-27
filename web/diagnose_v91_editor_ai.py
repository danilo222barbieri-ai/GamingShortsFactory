from pathlib import Path

p=Path('/app/GamingShortsFactory_V90_UPLOAD_VISUAL_FIX.py')
lines=p.read_text(encoding='utf-8').splitlines()

ranges=[
    (4200,4520,'AI'),
    (9480,10080,'PLAYER'),
    (10370,10820,'MAINEDITOR'),
    (11140,11520,'INLINEEDITOR'),
]
for a,b,label in ranges:
    print(f'V91RANGE {label} {a}-{b}')
    for n in range(a,min(b,len(lines))+1):
        print(f'V91SRC {label} {n}: {lines[n-1]}')
    print(f'V91END {label}')
