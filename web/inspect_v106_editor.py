from pathlib import Path
import ast
p=Path("/app/GamingShortsFactory_V105_7_ADSENSE_READY.py")
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)
for name in ("_gsf_render_core","_gsf_render_final_recipe","render_gsf_editor_live_player"):
    node=next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)
    print("V106_FUNC_"+name+"_START")
    if node is None:
        print("NOT_FOUND")
    else:
        print(ast.get_source_segment(s,node) or "")
    print("V106_FUNC_"+name+"_END")
