from pathlib import Path
import ast

src=Path("/app/GamingShortsFactory_V148_ANALYTICS_LEARNING.py")
out=Path("/app/GamingShortsFactory_V150_AI_COMPLETE.py")
s=src.read_text(encoding="utf-8")

tree=ast.parse(s)
node=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_publish_social_upload"),None)
if node is None:
    raise RuntimeError("V150 social publish function not found")

lines=s.splitlines(keepends=True)
start=node.lineno-1
end=node.end_lineno
block="".join(lines[start:end])
needle="def _gsf_publish_social_upload("
if needle not in block:
    raise RuntimeError("V150 social publish definition malformed")
block=block.replace(needle,"def _gsf_publish_social_upload_v150_base(",1)

wrapper=r'''
def _gsf_v150_privacy_state():
    try:
        _p=globals().get("GSF_SESSION_ROOT")
        if _p is None:
            _p=__import__("pathlib").Path(
                __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
            )/"sessions"/str(GSF_SESSION_ID)
        _path=__import__("pathlib").Path(_p)/"privacy_cleanup_v149.json"
        if _path.is_file():
            _data=__import__("json").loads(_path.read_text(encoding="utf-8"))
            if isinstance(_data,dict):
                return _data
    except Exception:
        pass
    return {}


def _gsf_publish_social_upload(*args,**kwargs):
    _privacy=_gsf_v150_privacy_state()
    _recipe=st.session_state.get("gsf_final_recipe") or {}
    _guard=str(_privacy.get("publish_guard") or "").lower()
    if not _guard:
        _guard=str((_recipe or {}).get("ai_publish_guard") or "").lower()
    if _guard=="review":
        return (
            False,
            "Privacy AI: ho rilevato un elemento che richiede verifica prima della pubblicazione.",
            "",
        )
    return _gsf_publish_social_upload_v150_base(*args,**kwargs)


'''
replacement=block.rstrip()+"

"+wrapper.lstrip()
s="".join(lines[:start])+replacement+"".join(lines[end:])

s=s.replace(
    "Gaming Shorts Factory · V148 Analytics Learning",
    "Gaming Shorts Factory · V150 AI Complete",
)

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V150 AI Complete applied:",out)
