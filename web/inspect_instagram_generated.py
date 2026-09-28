from pathlib import Path
import ast,sys
p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)
names={
    "_gsf_instagram_validate",
    "_gsf_instagram_config",
    "_gsf_instagram_connect",
    "_gsf_instagram_publish",
    "_gsf_social_connection_status",
    "_gsf_app_credentials",
}
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in names:
        print(f"===== {node.name} =====")
        start=node.lineno-1
        end=getattr(node,"end_lineno",node.lineno)
        print("\n".join(s.splitlines()[start:end]))
