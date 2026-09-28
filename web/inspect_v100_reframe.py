from pathlib import Path
import ast,sys
p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)
print("=== V100 REFRAME DIAGNOSTIC START ===")
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and any(k in node.name.lower() for k in ("reframe","crop_track","saliency")):
        print("\n###",node.name,"ARGS",ast.unparse(node.args))
        seg=ast.get_source_segment(s,node) or ""
        print(seg[:24000])
print("=== V100 REFRAME DIAGNOSTIC END ===")
