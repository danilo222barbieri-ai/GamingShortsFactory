from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V105_SOCIAL_STREAM.py')
out=Path('/app/GamingShortsFactory_V105_ISOLATED.py')
s=src.read_text(encoding='utf-8')
tree=ast.parse(s)

targets={
    "_gsf_shared_tiktok_load",
    "_gsf_shared_tiktok_save",
    "_gsf_shared_youtube_load",
    "_gsf_shared_youtube_save",
    "_gsf_shared_instagram_load",
    "_gsf_shared_instagram_save",
    "_gsf_v105_remote_render",
    "_gsf_instagram_publish_reel_file",
}

anchor=next(
    n for n in tree.body
    if isinstance(n,ast.FunctionDef) and n.name=="_gsf_shared_tiktok_s3"
)
helper=r'''
def _gsf_v105_storage_key(key):
    prefix=str(os.environ.get("GSF_STORAGE_PREFIX","") or "").strip("/")
    key=str(key or "").lstrip("/")
    if prefix and key.startswith(prefix+"/"):
        return key
    return f"{prefix}/{key}" if prefix else key


'''
lines=s.splitlines(keepends=True)
s=''.join(lines[:anchor.lineno-1])+helper+''.join(lines[anchor.lineno-1:])

def first_literal(joined):
    if not isinstance(joined,ast.JoinedStr) or not joined.values:
        return ""
    v=joined.values[0]
    return str(v.value) if isinstance(v,ast.Constant) and isinstance(v.value,str) else ""

class WrapKeys(ast.NodeTransformer):
    PREFIXES=("social-connections/","render-stage/","render-results/","social-stage/")

    def _needs(self,node):
        if isinstance(node,ast.JoinedStr):
            return first_literal(node).startswith(self.PREFIXES)
        if isinstance(node,ast.Constant) and isinstance(node.value,str):
            return node.value.startswith(self.PREFIXES)
        return False

    def _wrap(self,node):
        return ast.Call(
            func=ast.Name(id="_gsf_v105_storage_key",ctx=ast.Load()),
            args=[node],
            keywords=[],
        )

    def visit_Assign(self,node):
        self.generic_visit(node)
        if self._needs(node.value):
            node.value=self._wrap(node.value)
        return node

    def visit_AnnAssign(self,node):
        self.generic_visit(node)
        if node.value is not None and self._needs(node.value):
            node.value=self._wrap(node.value)
        return node

    def visit_Call(self,node):
        self.generic_visit(node)
        for kw in node.keywords:
            if kw.arg=="Key" and self._needs(kw.value):
                kw.value=self._wrap(kw.value)
            elif kw.arg=="Params" and isinstance(kw.value,ast.Dict):
                for i,k in enumerate(kw.value.keys):
                    if isinstance(k,ast.Constant) and k.value=="Key" and self._needs(kw.value.values[i]):
                        kw.value.values[i]=self._wrap(kw.value.values[i])
        return node

tree=ast.parse(s)
nodes=[
    n for n in tree.body
    if isinstance(n,ast.FunctionDef) and n.name in targets
]
missing=targets-{n.name for n in nodes}
if missing:
    raise RuntimeError("V105 storage namespace functions missing: "+", ".join(sorted(missing)))

replacements=[]
for node in nodes:
    transformed=WrapKeys().visit(node)
    ast.fix_missing_locations(transformed)
    replacements.append((node.lineno,node.end_lineno,ast.unparse(transformed).rstrip()+"\n"))

lines=s.splitlines(keepends=True)
for start,end,new_text in sorted(replacements,reverse=True):
    lines[start-1:end]=[new_text+"\n"]
s=''.join(lines)

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V105 storage namespace applied:",out)
