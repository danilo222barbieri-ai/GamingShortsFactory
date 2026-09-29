from pathlib import Path

p=Path("/app/GamingShortsFactory_V105_7_ADSENSE_READY.py")
s=p.read_text(encoding="utf-8")
lines=s.splitlines()

tokens=[
    "def _render_gsf_editor_live_player_legacy",
    "def _render_gsf_editor_live_player(",
    "_fmt_key",
    "16:9 Originale",
    "9:16 Short",
    "color_picker(",
    "editor_sub_",
    "_render_gsf_editor_live_player(",
    "inline_zoom_widget",
    "inline_reg_v18",
    "editor_format",
    "_gsf_render_final_recipe(",
    "publication_final_bytes",
]

print("V106_EDITOR_INSPECT_START")
for token in tokens:
    print("\n### TOKEN",token)
    found=0
    for i,line in enumerate(lines):
        if token in line:
            found+=1
            a=max(0,i-14); b=min(len(lines),i+24)
            print(f"--- hit {found} line {i+1} ---")
            for j in range(a,b):
                print(f"{j+1}: {lines[j]}")
            if found>=5:
                break
    if not found:
        print("NOT FOUND")
print("V106_EDITOR_INSPECT_END")
