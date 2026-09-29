from pathlib import Path
import ast

p=Path("/app/GamingShortsFactory_V107_PRODUCTION_UI.py")
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)

print("=== V107 MEMORY INSPECT ===",flush=True)
wanted={
    "_gsf_v71_render_mini_player",
    "_gsf_bytes_to_preview",
    "_gsf_v93_release_analysis_memory",
    "_gsf_v106_run_render_locked",
    "_gsf_render_final_recipe",
}
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in wanted:
        print(f"--- FUNC {node.name} ---",flush=True)
        print(ast.get_source_segment(s,node) or "",flush=True)

for needle in (
    "_card_bytes",
    "publication_preview_bytes",
    "preview_bytes",
    "Creo lo Short finale",
    "Crea Short finale",
):
    print(f"--- AROUND {needle} ---",flush=True)
    start=0
    count=0
    while True:
        i=s.find(needle,start)
        if i<0 or count>=12:
            break
        print(s[max(0,i-1800):min(len(s),i+4200)],flush=True)
        print("---",flush=True)
        start=i+len(needle)
        count+=1

print("=== END V107 MEMORY INSPECT ===",flush=True)
