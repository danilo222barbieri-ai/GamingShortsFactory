from pathlib import Path

src=Path("/app/GamingShortsFactory_V142_DIRECTOR_RUNTIME.py")
out=Path("/app/GamingShortsFactory_V143_RENDER_EXECUTION.py")
s=src.read_text(encoding="utf-8")

anchor='''                        __import__("shutil").copyfile(_v126_final_source,_tmp_video)
                        __import__("os").replace(_tmp_video,_gsf_stable)
'''
replacement=r'''                        _v143_final_source=_v126_final_source
                        _v143_tmp=_gsf_stable.with_name(".director_v143_"+str(__import__("os").getpid())+".mp4")
                        try:
                            _v143_recipe=dict((_job.get("recipe") or {})) if isinstance(_job,dict) else {}
                            _v143_ops=list(_v143_recipe.get("ai_render_operations") or [])
                            if _v143_ops:
                                _v143_mod=__import__(
                                    "director_render_exec_v143",
                                    fromlist=["execute_director_operations"],
                                )
                                _v143_result=_v143_mod.execute_director_operations(
                                    str(_v126_final_source),
                                    str(_v143_tmp),
                                    _v143_ops,
                                    recipe_start=float(_v143_recipe.get("start") or 0.0),
                                )
                                if (
                                    isinstance(_v143_result,dict)
                                    and _v143_result.get("ok")
                                    and int(_v143_result.get("count") or 0)>0
                                    and _v143_tmp.is_file()
                                    and _v143_tmp.stat().st_size>1024
                                ):
                                    _v143_final_source=_v143_tmp
                                    _job["director_v143"]=_v143_result
                                    print(
                                        "GSF_V143_RENDER_APPLIED",
                                        "sid="+_gsf_sid,
                                        "effects="+str(_v143_result.get("applied") or []),
                                        flush=True,
                                    )
                        except Exception as _v143_exc:
                            print("GSF_V143_RENDER_FALLBACK",repr(str(_v143_exc))[:300],flush=True)

                        __import__("shutil").copyfile(_v143_final_source,_tmp_video)
                        __import__("os").replace(_tmp_video,_gsf_stable)
                        try:
                            _v143_tmp.unlink(missing_ok=True)
                        except Exception:
                            pass
'''
if anchor not in s:
    raise RuntimeError("V143 V126 final-copy anchor missing")
s=s.replace(anchor,replacement,1)

s=s.replace(
    "Gaming Shorts Factory · V142 Director Runtime",
    "Gaming Shorts Factory · V143 Render Execution",
)
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V143 Render Execution applied:",out)
