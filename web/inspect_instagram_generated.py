from pathlib import Path
import ast,sys
p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)
lines=s.splitlines()
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and ("instagram" in node.name.lower() or node.name in {"_gsf_app_credentials","_gsf_social_connection_status"}):
        print(f"===== {node.name} =====")
        start=node.lineno-1
        end=getattr(node,"end_lineno",node.lineno)
        print("\n".join(lines[start:end]))
