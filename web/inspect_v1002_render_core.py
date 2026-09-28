from pathlib import Path
import ast,sys
p=Path(sys.argv[1]); s=p.read_text(encoding="utf-8"); tree=ast.parse(s)
print("=== V100.2 RENDER CORE START ===")
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in ("_gsf_render_core","_gsf_render_final_recipe"):
        print("\n###",node.name,"ARGS",ast.unparse(node.args))
        print((ast.get_source_segment(s,node) or "")[:45000])
print("=== V100.2 RENDER CORE END ===")
