from pathlib import Path
import re, sys

p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
lines=s.splitlines()

patterns=[
    "gsf_source_path","gsf_source_name","upload_v73",
    "auto_clip","candidat","momenti","scelte","clip_scelta",
    "editor_start","editor_end","editor_","show_editor",
    "gsf_final_recipe","final_video","final_path","final_",
    "show_social_publish_v54","social_selected_v59"
]

seen=set()
for i,line in enumerate(lines):
    low=line.lower()
    if any(x.lower() in low for x in patterns):
        a=max(0,i-2); b=min(len(lines),i+3)
        block="\n".join(f"{j+1}: {lines[j]}" for j in range(a,b))
        if block not in seen:
            seen.add(block)
            print("\n---\n"+block)

print("\n=== SESSION STATE KEYS ===")
keys=set()
for m in re.finditer(r'st\.session_state(?:\.get\(|\[)[\"\']([^\"\']+)',s):
    keys.add(m.group(1))
for k in sorted(keys):
    if any(x in k.lower() for x in ("source","upload","clip","auto","candidate","moment","editor","final","social","short","scene","duration","durata")):
        print(k)
