from pathlib import Path
import ast,sys,re
p=Path(sys.argv[1]); s=p.read_text(encoding="utf-8"); tree=ast.parse(s)
print("=== V100.1 DIAG START ===")
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in ("render_gsf_player","_gsf_render_core","_gsf_smart_reframe_filter"):
        print("\n###",node.name,"ARGS",ast.unparse(node.args))
        print((ast.get_source_segment(s,node) or "")[:30000])
for pat in ("Anteprima","ANTEPRIMA"):
    for m in list(re.finditer(pat,s,re.I))[:12]:
        print("\n### LABEL",pat,m.start())
        print(s[max(0,m.start()-1800):min(len(s),m.start()+3500)])
print("=== V100.1 DIAG END ===")
