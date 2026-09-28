from pathlib import Path
p=Path('/app/GamingShortsFactory_V98_10_SPEED_PASS1.py')
lines=p.read_text(encoding='utf-8').splitlines()
patterns=(
    'def _gsf_ai_scan',
    'def _gsf_ai_',
    'ThreadPoolExecutor(',
    'max_workers=',
    'scan_step',
    'step=',
    'fps=',
    'scale=',
    'shortlist',
    'candidati',
    'candidate',
    'motion',
    'audio',
    'subprocess.run(',
    'Popen(',
)
hits=set()
for i,line in enumerate(lines):
    if any(pat in line for pat in patterns):
        if 4200 <= i+1 <= 6200:
            for j in range(max(0,i-5),min(len(lines),i+18)):
                hits.add(j)
for j in sorted(hits):
    print(f'V98SPEED {j+1}: {lines[j]}')
