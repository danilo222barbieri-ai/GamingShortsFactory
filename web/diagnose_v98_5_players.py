from pathlib import Path
p=Path('/app/GamingShortsFactory_V98_4_EDITOR_CLEANUP.py')
lines=p.read_text(encoding='utf-8').splitlines()
patterns=('anteprima','preview','_target_width','_max_vw','render_gsf','components.html','st.video','video_html')
hits=set()
for i,line in enumerate(lines):
    low=line.lower()
    if any(x.lower() in low for x in patterns):
        for j in range(max(0,i-4),min(len(lines),i+8)):
            hits.add(j)
for j in sorted(hits):
    print(f'V985DIAG {j+1}: {lines[j]}')
