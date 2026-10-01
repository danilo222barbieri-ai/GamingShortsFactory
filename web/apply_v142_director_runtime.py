from pathlib import Path

src=Path("/app/GamingShortsFactory_V130_2_STABILITY_UX.py")
out=Path("/app/GamingShortsFactory_V142_DIRECTOR_RUNTIME.py")
s=src.read_text(encoding="utf-8")

helper_anchor="def _gsf_v130_short_for_start(start):\n"
helper=r'''
def _gsf_v142_source_path():
    try:
        for _k in ("editor_input","inline_editor_input","gsf_source_path","publication_input"):
            _p=str(st.session_state.get(_k) or "").strip()
            if _p and __import__("os").path.exists(_p):
                return _p
        _raw=st.session_state.get("gsf_source_bytes")
        if isinstance(_raw,(bytes,bytearray,memoryview)) and len(_raw)>1024:
            _root=__import__("pathlib").Path(
                __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
            )/"sessions"/str(GSF_SESSION_ID)/"director"
            _root.mkdir(parents=True,exist_ok=True)
            _p=_root/"source_v142.mp4"
            if (not _p.exists()) or _p.stat().st_size!=len(_raw):
                _tmp=_p.with_suffix(".tmp")
                _tmp.write_bytes(bytes(_raw))
                __import__("os").replace(_tmp,_p)
            return str(_p)
        _video=globals().get("video")
        if _video is not None and hasattr(_video,"getvalue"):
            _raw=bytes(_video.getvalue() or b"")
            if len(_raw)>1024:
                _root=__import__("pathlib").Path(
                    __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
                )/"sessions"/str(GSF_SESSION_ID)/"director"
                _root.mkdir(parents=True,exist_ok=True)
                _p=_root/"source_v142.mp4"
                if (not _p.exists()) or _p.stat().st_size!=len(_raw):
                    _tmp=_p.with_suffix(".tmp")
                    _tmp.write_bytes(_raw)
                    __import__("os").replace(_tmp,_p)
                return str(_p)
    except Exception as _exc:
        print("GSF_V142_SOURCE_WARN",repr(str(_exc))[:220],flush=True)
    return ""


def _gsf_v148_performance_context():
    try:
        _u=__import__("urllib.request",fromlist=["Request","urlopen"])
        _j=__import__("json")
        _os=__import__("os")
        _port=str(_os.environ.get("GSF_DIRECT_UPLOAD_PORT","8502") or "8502")
        _raw=_j.dumps({},separators=(",",":")).encode("utf-8")
        _req=_u.Request(
            "http://127.0.0.1:"+_port+"/social-analytics/context",
            data=_raw,
            headers={
                "Content-Type":"application/json",
                "X-GSF-Session-ID":str(GSF_SESSION_ID),
            },
            method="POST",
        )
        _payload=_j.loads(_u.urlopen(_req,timeout=1.5).read().decode("utf-8"))
        return dict((_payload or {}).get("context") or {})
    except Exception:
        return {}


def _gsf_v142_enrich_recipe(recipe):
    _recipe=dict(recipe or {})
    try:
        _brain=st.session_state.get("gsf_v112_brain_context") or {}
        _one=dict(_brain.get("one_click") or {}) if isinstance(_brain,dict) else {}
        if not _one.get("shorts"):
            return _recipe
        _src=_gsf_v142_source_path()
        if not _src:
            print("GSF_V142_SKIP no-source",flush=True)
            return _recipe
        try:
            _dur=float(durata_video(_src) or 0.0)
        except Exception:
            _dur=0.0
        if _dur<=0:
            _dur=max(15.0,float(_recipe.get("duration") or 15.0))
        _root=__import__("pathlib").Path(
            __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
        )/"sessions"/str(GSF_SESSION_ID)/"director"
        _mod=__import__("director_pipeline_v142",fromlist=["run_director_pipeline","apply_pipeline_to_recipe"])
        _start=float(_recipe.get("start",st.session_state.get("auto_clip_scelta",0.0)) or 0.0)
        _short=_gsf_v130_short_for_start(_start)
        _mount=dict((_short or {}).get("mount") or {})
        _cine=dict(_mount.get("cinematic") or {})
        _frame=dict(_mount.get("framing") or {})
        _event={
            "signal":"selected",
            "zoom_aggression":max(0.0,min(1.0,(float(_frame.get("zoom") or 1.0)-1.0)/.8)),
            "caption_density":1.0 if _mount.get("captions") else 0.0,
            "replay_preference":1.0 if dict(_cine.get("replay") or {}).get("enabled") else 0.0,
            "cold_open":1.0 if dict(_cine.get("cold_open") or {}).get("enabled") else 0.0,
            "preserve_context":1.0 if dict(_one.get("game_context") or {}).get("context_available") else 0.0,
            "cut_density":min(1.0,len(list(_cine.get("pattern_interrupts") or []))/.4/max(float(_recipe.get("duration") or 15.0),1.0)),
        }
        _pipeline=_mod.run_director_pipeline(
            _src,_dur,_brain,_one,_root,
            selected_start=_start,
            provider_results=st.session_state.get("gsf_v142_provider_results"),
            creator_event=_event,
            performance_context=_gsf_v148_performance_context(),
        )
        st.session_state["gsf_v142_runtime"]=_pipeline
        _recipe=_mod.apply_pipeline_to_recipe(_recipe,_pipeline)
        print(
            "GSF_V142_READY",
            "ops="+str(dict(_pipeline.get("render") or {}).get("operation_count") or 0),
            "ab="+str(dict(_pipeline.get("ab") or {}).get("winner") or ""),
            "guard="+str(dict(_pipeline.get("render") or {}).get("publish_guard") or ""),
            flush=True,
        )
    except Exception as _exc:
        print("GSF_V142_PIPELINE_FALLBACK",repr(str(_exc))[:320],flush=True)
    return _recipe


'''
if helper_anchor not in s:
    raise RuntimeError("V142 helper anchor missing")
s=s.replace(helper_anchor,helper+helper_anchor,1)

recipe_anchor='''                                _recipe["ai_editor_actions"]=list(
                                    _v130_short.get("editor_actions") or []
                                )
'''
recipe_replacement=recipe_anchor+r'''
                                # V142 executes the full Director chain and freezes
                                # its decisions into the same render recipe.
                                _recipe=_gsf_v142_enrich_recipe(_recipe)
                                st.session_state["gsf_final_recipe"]=_recipe
'''
if recipe_anchor not in s:
    raise RuntimeError("V142 V130 recipe anchor missing")
s=s.replace(recipe_anchor,recipe_replacement,1)

s=s.replace(
    "Gaming Shorts Factory · V130.2",
    "Gaming Shorts Factory · V142 Director Runtime",
)
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V142 Director Runtime applied:",out)
