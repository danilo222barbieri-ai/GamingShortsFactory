from pathlib import Path
import ast
p=Path('/app/GamingShortsFactory_V104_4_SHARED_SOCIAL.py')
s=p.read_text(encoding='utf-8')
tree=ast.parse(s)
print("GSF_YOUTUBE_INSPECT_BEGIN")
for n in tree.body:
    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and "youtube" in n.name.lower():
        print(f"DEF {n.name} lines={n.lineno}-{n.end_lineno}")
        segment=ast.get_source_segment(s,n) or ""
        for line in segment.splitlines():
            if any(x in line.lower() for x in ("token","credential","client","oauth","social_dir","json")):
                print("  "+line[:300])
for i,line in enumerate(s.splitlines(),1):
    lo=line.lower()
    if ("youtube" in lo and any(x in lo for x in ("token","credential","client_id","client_secret","oauth"))):
        print(f"LINE {i}: {line[:500]}")
print("GSF_YOUTUBE_INSPECT_END")
