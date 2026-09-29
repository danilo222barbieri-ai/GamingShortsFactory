from pathlib import Path
import ast,sys
p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_render_core")
lines=s.splitlines()
print("===== V105_RENDER_CORE_AUDIO_INSPECT =====")
print("\n".join(lines[node.lineno-1:node.end_lineno]))
print("===== END_V105_RENDER_CORE_AUDIO_INSPECT =====")
