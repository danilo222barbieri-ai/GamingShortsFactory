from pathlib import Path
import re,sys

p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
lines=s.splitlines()
terms=[
    "_show_final_flow",
    "Crea lo Short finale",
    "Clicca su",
    "Pubblicazione diretta",
    "social_error_v59",
    "download_button",
    "SCARICA",
    "Pubblicità",
    "pubblicità",
    "gsf-ad",
    "editor_auto_sub_error",
]
seen=set()
for term in terms:
    print("\n===== PROBE",term,"=====")
    found=False
    for i,line in enumerate(lines):
        if term.lower() in line.lower():
            a=max(0,i-14); b=min(len(lines),i+28)
            key=(a,b)
            if key in seen:
                continue
            seen.add(key); found=True
            print(f"--- lines {a+1}-{b} ---")
            print("\n".join(f"{j+1}: {lines[j]}" for j in range(a,b)))
    if not found:
        print("NOT FOUND")
