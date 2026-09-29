from pathlib import Path
p=Path('/app/GamingShortsFactory_V105_6_ADS_PREVIEW.py')
lines=p.read_text(encoding='utf-8').splitlines()
hits=[i for i,l in enumerate(lines) if 'gsf-v1056-ad' in l and '<aside' in l]
print('ADS_CONTEXT_COUNT',len(hits))
for n,i in enumerate(hits,1):
    print(f'\n=== AD_SLOT_{n} line {i+1} ===')
    a=max(0,i-8); b=min(len(lines),i+9)
    for j in range(a,b):
        print(f'{j+1}: {lines[j]}')
