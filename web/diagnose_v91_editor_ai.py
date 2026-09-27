from pathlib import Path

p=Path('/app/GamingShortsFactory_V90_UPLOAD_VISUAL_FIX.py')
lines=p.read_text(encoding='utf-8').splitlines()

ranges=[
    (4510,5250,'AI2'),
    (10810,11145,'FLOW'),
    (11140,11520,'INLINEEDITOR'),
]
for a,b,label in ranges:
    print(f'V91RANGE {label} {a}-{b}')
    for n in range(a,min(b,len(lines))+1):
        print(f'V91SRC {label} {n}: {lines[n-1]}')
    print(f'V91END {label}')

for n,line in enumerate(lines,1):
    low=line.lower()
    if line.lstrip().startswith('def ') and any(k in low for k in ('render','recipe','short','reframe')):
        print(f'V91FUNC {n}: {line}')
