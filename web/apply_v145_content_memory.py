from pathlib import Path

src=Path("/app/GamingShortsFactory_V144_VISUAL_SCORING.py")
out=Path("/app/GamingShortsFactory_V145_CONTENT_MEMORY.py")
s=src.read_text(encoding="utf-8")

helper_anchor="def _gsf_v142_source_path():\n"
helper=r'''
def _gsf_v145_memory_api(path,record):
    try:
        _u=__import__("urllib.request",fromlist=["Request","urlopen"])
        _j=__import__("json")
        _port=str(__import__("os").environ.get("GSF_DIRECT_UPLOAD_PORT","8502") or "8502")
        _raw=_j.dumps({"record":dict(record or {})},ensure_ascii=False,separators=(",",":")).encode("utf-8")
        _req=_u.Request(
            "http://127.0.0.1:"+_port+str(path),
            data=_raw,
            headers={
                "Content-Type":"application/json",
                "X-GSF-Session-ID":str(GSF_SESSION_ID),
            },
            method="POST",
        )
        _resp=_j.loads(_u.urlopen(_req,timeout=2.5).read().decode("utf-8"))
        return dict((_resp or {}).get("memory") or {})
    except Exception as _exc:
        print("GSF_V145_MEMORY_API_WARN",str(path),repr(str(_exc))[:220],flush=True)
        return {}


'''
if helper_anchor not in s:
    raise RuntimeError("V145 V142 source helper anchor missing")
s=s.replace(helper_anchor,helper+helper_anchor,1)

pipeline_anchor=r'''        _pipeline=_mod.run_director_pipeline(
            _src,_dur,_brain,_one,_root,
            selected_start=_start,
            provider_results=st.session_state.get("gsf_v142_provider_results"),
            creator_event=_event,
            performance_context=_gsf_v148_performance_context(),
        )
        st.session_state["gsf_v142_runtime"]=_pipeline
        _recipe=_mod.apply_pipeline_to_recipe(_recipe,_pipeline)
'''
pipeline_replacement=r'''        _pipeline=_mod.run_director_pipeline(
            _src,_dur,_brain,_one,_root,
            selected_start=_start,
            provider_results=st.session_state.get("gsf_v142_provider_results"),
            creator_event=_event,
            performance_context=_gsf_v148_performance_context(),
        )

        # V145: persistent candidate-level memory is checked before the render
        # recipe is frozen. It survives redeploys through the existing bucket.
        try:
            _mem=__import__("content_memory_v145",fromlist=["memory_record"])
            _recognition=dict(_one.get("game_recognition") or {})
            _record=_mem.memory_record(
                _pipeline.get("source_fingerprint"),
                _pipeline.get("selected_short"),
                {
                    "game":str(_recognition.get("game") or ""),
                    "status":"prepared",
                },
            )
            _memory=_gsf_v145_memory_api("/content-memory/check",_record)
            _pipeline["content_memory"]=_memory
            _pipeline["content_memory_record"]=_record
            print(
                "GSF_V145_MEMORY_CHECK",
                "duplicate="+str(bool(_memory.get("duplicate"))),
                "source_count="+str(_memory.get("source_count") or 0),
                flush=True,
            )
        except Exception as _v145_exc:
            print("GSF_V145_MEMORY_CHECK_WARN",repr(str(_v145_exc))[:240],flush=True)

        st.session_state["gsf_v142_runtime"]=_pipeline
        _recipe=_mod.apply_pipeline_to_recipe(_recipe,_pipeline)
'''
if pipeline_anchor not in s:
    raise RuntimeError("V145 V142 pipeline anchor missing")
s=s.replace(pipeline_anchor,pipeline_replacement,1)

s=s.replace(
    "Gaming Shorts Factory · V144 Visual Scoring",
    "Gaming Shorts Factory · V145 Content Memory",
)
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V145 Content Memory applied:",out)
