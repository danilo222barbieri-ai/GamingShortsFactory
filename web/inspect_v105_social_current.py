from pathlib import Path
import ast,sys
p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
tree=ast.parse(s)
wanted=[]
for n in tree.body:
    if isinstance(n,ast.FunctionDef):
        name=n.name.lower()
        if (
            "youtube" in name and ("upload" in name or "publish" in name)
            or "tiktok_direct_post" in name
            or "instagram_publish_reel" in name
            or "publish_to_social" in name
            or "social_publish" in name
        ):
            wanted.append(n)
for n in wanted:
    print("GSF_SOCIAL_FUNC",n.name,ast.unparse(n.args))
    src=ast.get_source_segment(s,n) or ""
    if len(src)>9000:
        src=src[:9000]+"\n# ...TRUNCATED..."
    print(src)
    print("GSF_SOCIAL_FUNC_END",n.name)
