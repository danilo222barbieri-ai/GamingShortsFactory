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
    "CREA SHORT",
    "Creo lo Short finale",
    "_gsf_social_pack",
    "selected_caption",
    "hashtags",
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


import ast
tree=ast.parse(s)
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in {
        "_gsf_publish_social_upload","_gsf_generate_social_pack","_gsf_social_pack"
    }:
        print("\n===== FUNCTION",node.name,"=====")
        a=node.lineno-1; b=node.end_lineno
        print("\n".join(f"{j+1}: {lines[j]}" for j in range(a,b)))
