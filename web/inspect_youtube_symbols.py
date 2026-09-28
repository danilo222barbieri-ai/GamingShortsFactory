from pathlib import Path
import ast
p=Path('/app/GamingShortsFactory_V104_5_YOUTUBE_SOCIAL.py')
s=p.read_text(encoding='utf-8')
tree=ast.parse(s)
print("GSF_INSTAGRAM_INSPECT_BEGIN")
for n in tree.body:
    if isinstance(n,ast.FunctionDef) and "instagram" in n.name.lower():
        print("###",n.name)
        seg=ast.get_source_segment(s,n) or ""
        if len(seg)<=12000:
            print(seg)
        else:
            for line in seg.splitlines():
                if any(k in line.lower() for k in ("token","user_id","config","social","json","credential")):
                    print(line[:600])
        print("### END",n.name)
for i,line in enumerate(s.splitlines(),1):
    if "GSF_INSTAGRAM" in line or "instagram_token" in line or "instagram_config" in line:
        print(f"LINE {i}: {line[:700]}")
print("GSF_INSTAGRAM_INSPECT_END")
