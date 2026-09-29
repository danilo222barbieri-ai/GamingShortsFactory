from pathlib import Path
import ast

p=Path("/app/GamingShortsFactory_V106_BETA_RC1.py")
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)

print("=== V107 RECIPE CONTRACT INSPECT ===")
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in {
        "_gsf_recipe_selected","_gsf_render_recipe","_gsf_render_core",
        "_gsf_set_final_recipe","_gsf_render_video_filters","_gsf_render_audio_filter"
    }:
        print(f"--- FUNC {node.name} ---")
        print(ast.get_source_segment(s,node) or "")

keys=set()
for node in ast.walk(tree):
    if isinstance(node,ast.Constant) and isinstance(node.value,str):
        v=node.value
        if v.startswith("editor_") or v.startswith("subtitle_") or v in {"project_subtitles_enabled"}:
            keys.add(v)
print("--- EDITOR_KEYS ---")
print("\n".join(sorted(keys)))
print("=== END V107 RECIPE CONTRACT INSPECT ===")
