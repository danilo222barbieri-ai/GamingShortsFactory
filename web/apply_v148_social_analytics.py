from pathlib import Path
import ast

src=Path("/app/GamingShortsFactory_V145_CONTENT_MEMORY.py")
out=Path("/app/GamingShortsFactory_V148_ANALYTICS_LEARNING.py")
s=src.read_text(encoding="utf-8")

tree=ast.parse(s)
node=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_gsf_write_social_status"),None)
if node is None:
    raise RuntimeError("V148 social status function not found")

lines=s.splitlines(keepends=True)
start=node.lineno-1
end=node.end_lineno
block="".join(lines[start:end])
needle="def _gsf_write_social_status("
if needle not in block:
    raise RuntimeError("V148 social status definition malformed")
block=block.replace(needle,"def _gsf_write_social_status_v148_base(",1)

wrapper=r'''
def _gsf_v148_api(path,payload):
    try:
        _u=__import__("urllib.request",fromlist=["Request","urlopen"])
        _j=__import__("json")
        _os=__import__("os")
        _port=str(_os.environ.get("GSF_DIRECT_UPLOAD_PORT","8502") or "8502")
        _raw=_j.dumps(dict(payload or {}),ensure_ascii=False,separators=(",",":")).encode("utf-8")
        _req=_u.Request(
            "http://127.0.0.1:"+_port+str(path),
            data=_raw,
            headers={
                "Content-Type":"application/json",
                "X-GSF-Session-ID":str(GSF_SESSION_ID),
            },
            method="POST",
        )
        return _j.loads(_u.urlopen(_req,timeout=2.0).read().decode("utf-8"))
    except Exception as _exc:
        print("GSF_V148_API_WARN",str(path),repr(str(_exc))[:220],flush=True)
        return {}


def _gsf_write_social_status(*args,**kwargs):
    _result=_gsf_write_social_status_v148_base(*args,**kwargs)
    try:
        _platform=str(args[0] if len(args)>0 else kwargs.get("platform") or "")
        _state=str(args[1] if len(args)>1 else kwargs.get("state") or "")
        if _state.lower()=="ready":
            _content_id=""
            _id_type=""
            for _key in ("video_id","media_id","post_id","publish_id","content_id","id"):
                _value=str(kwargs.get(_key) or "").strip()
                if _value:
                    _content_id=_value
                    _id_type=_key
                    break
            if _content_id:
                _recipe=st.session_state.get("gsf_final_recipe") or {}
                _payload={
                    "platform":_platform,
                    "content_id":_content_id,
                    "id_type":_id_type,
                    "content_fingerprint":str(
                        (_recipe or {}).get("ai_content_fingerprint")
                        or ((_recipe or {}).get("director_runtime_v142") or {}).get("content_fingerprint")
                        or ""
                    ),
                    "metadata":{
                        "ab_strategy":str((_recipe or {}).get("ai_ab_strategy") or ""),
                        "start":float((_recipe or {}).get("start") or 0.0),
                        "duration":float((_recipe or {}).get("duration") or 0.0),
                        "game":str(st.session_state.get("gioco") or ""),
                    },
                }
                _registered=_gsf_v148_api("/social-analytics/register",_payload)
                if (_registered or {}).get("ok"):
                    st.session_state["gsf_v148_analytics_registered"]={
                        "platform":_platform,
                        "content_id":_content_id,
                        "id_type":_id_type,
                    }
                    print(
                        "GSF_V148_ANALYTICS_REGISTERED",
                        _platform,
                        _id_type+"="+_content_id[:48],
                        flush=True,
                    )
    except Exception as _exc:
        print("GSF_V148_REGISTER_WARN",repr(str(_exc))[:240],flush=True)
    return _result


'''
replacement=block.rstrip()+"

"+wrapper.lstrip()
s="".join(lines[:start])+replacement+"".join(lines[end:])

s=s.replace(
    "Gaming Shorts Factory · V145 Content Memory",
    "Gaming Shorts Factory · V148 Analytics Learning",
)

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V148 Analytics Learning applied:",out)
