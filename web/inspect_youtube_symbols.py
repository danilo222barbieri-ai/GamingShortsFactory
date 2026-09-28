from pathlib import Path
import ast
p=Path('/app/GamingShortsFactory_V104_5_YOUTUBE_SOCIAL.py')
s=p.read_text(encoding='utf-8')
tree=ast.parse(s)
print("GSF_SOCIAL_UI_INSPECT_BEGIN")
for n in tree.body:
    if isinstance(n,ast.FunctionDef):
        name=n.name.lower()
        if ("social" in name or "oauth" in name) and any(x in name for x in ("auth","connect","render","publish","platform","callback","status")):
            print("###",n.name)
            seg=ast.get_source_segment(s,n) or ""
            if len(seg)<12000:
                print(seg)
            else:
                for line in seg.splitlines():
                    if any(k in line for k in ("st.", "href", "auth_url", "Collega", "platform", "link_button", "button")):
                        print(line[:500])
            print("### END",n.name)
for i,line in enumerate(s.splitlines(),1):
    if any(k in line for k in ("Collega TikTok","Collega YouTube","Collega Instagram","_gsf_social_auth","link_button","target=\"_blank\"")):
        print(f"LINE {i}: {line[:700]}")
print("GSF_SOCIAL_UI_INSPECT_END")
