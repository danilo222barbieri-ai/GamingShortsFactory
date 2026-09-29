from pathlib import Path
p=Path("/app/GamingShortsFactory_V106_BETA_RC1.py")
lines=p.read_text(encoding="utf-8").splitlines()
tokens=[
    'st.markdown("### Editor")',
    'render_gsf_editor_live_player(',
    'editor_format',
    'editor_start',
    'editor_end',
    'RESET CONTROLLI',
    'REGOLAZIONI',
    'Filtri video',
    'gsf-subtitles-title',
    '_ith,_itr,_itc',
    'inline_live_v32_',
    'inline_reg_v18_',
    'inline_submode_widget_v18_',
]
print("V1062_INSPECT_START")
seen=set()
for token in tokens:
    print("\n### TOKEN",token)
    n=0
    for i,line in enumerate(lines):
        if token in line:
            n+=1
            a=max(0,i-35); b=min(len(lines),i+85)
            key=(a,b)
            if key in seen: continue
            seen.add(key)
            print(f"--- HIT line {i+1} ---")
            for j in range(a,b):
                print(f"{j+1}: {lines[j]}")
            if n>=5: break
print("V1062_INSPECT_END")
