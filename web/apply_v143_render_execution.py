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
                                    render_policy=dict(_v143_recipe.get("ai_render_policy") or {}),
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

                        _v149_final_source=_v143_final_source
                        _v149_tmp=_gsf_stable.with_name(".privacy_v149_"+str(__import__("os").getpid())+".mp4")
                        try:
                            _v149_mod=__import__(
                                "privacy_cleanup_v149",
                                fromlist=["cleanup_video"],
                            )
                            _v149_result=_v149_mod.cleanup_video(
                                str(_v143_final_source),
                                str(_v149_tmp),
                            )
                            _job["privacy_cleanup_v149"]=_v149_result
                            try:
                                _v149_root=__import__("pathlib").Path(
                                    __import__("os").environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime")
                                )/"sessions"/str(GSF_SESSION_ID)
                                _v149_root.mkdir(parents=True,exist_ok=True)
                                (_v149_root/"privacy_cleanup_v149.json").write_text(
                                    __import__("json").dumps(
                                        {
                                            "engine":"v149-privacy-cleanup",
                                            "applied":bool((_v149_result or {}).get("applied")),
                                            "mask_count":int((_v149_result or {}).get("mask_count") or 0),
                                            "publish_guard":str((_v149_result or {}).get("publish_guard") or "clear"),
                                            "report":dict((_v149_result or {}).get("report") or {}),
                                        },
                                        ensure_ascii=False,
                                        separators=(",",":"),
                                    ),
                                    encoding="utf-8",
                                )
                            except Exception:
                                pass
                            if (
                                isinstance(_v149_result,dict)
                                and _v149_result.get("ok")
                                and _v149_tmp.is_file()
                                and _v149_tmp.stat().st_size>1024
                                and bool(_v149_result.get("applied"))
                            ):
                                _v149_final_source=_v149_tmp
                            print(
                                "GSF_V149_PRIVACY",
                                "sid="+_gsf_sid,
                                "masked="+str(int((_v149_result or {}).get("mask_count") or 0)),
                                "guard="+str((_v149_result or {}).get("publish_guard") or "clear"),
                                flush=True,
                            )
                        except Exception as _v149_exc:
                            print("GSF_V149_PRIVACY_FALLBACK",repr(str(_v149_exc))[:300],flush=True)

                        __import__("shutil").copyfile(_v149_final_source,_tmp_video)
                        __import__("os").replace(_tmp_video,_gsf_stable)

                        # V145 finalizes persistent content memory only after a
                        # real final file exists, avoiding brittle UI hooks.
                        try:
                            _v145_record=dict(_v143_recipe.get("ai_content_memory_record") or {})
                            _v145_fp=str(_v145_record.get("fingerprint") or "")
                            if _v145_fp and _gsf_stable.is_file() and _gsf_stable.stat().st_size>1024:
                                _v145_record["status"]="rendered"
                                _v145_json=__import__("json")
                                _v145_url=__import__("urllib.request",fromlist=["Request","urlopen"])
                                _v145_req=_v145_url.Request(
                                    "http://127.0.0.1:8502/content-memory/record",
                                    data=_v145_json.dumps(
                                        {"record":_v145_record},
                                        ensure_ascii=False,
                                        separators=(",",":"),
                                    ).encode("utf-8"),
                                    headers={
                                        "Content-Type":"application/json",
                                        "X-GSF-Session-ID":str(GSF_SESSION_ID),
                                    },
                                    method="POST",
                                )
                                _v145_resp=_v145_json.loads(
                                    _v145_url.urlopen(_v145_req,timeout=2.5).read().decode("utf-8")
                                )
                                print(
                                    "GSF_V145_MEMORY_FINAL",
                                    "fp="+_v145_fp[:12],
                                    "ok="+str(bool((_v145_resp or {}).get("ok"))),
                                    flush=True,
                                )
                        except Exception as _v145_exc:
                            print("GSF_V145_MEMORY_FINAL_WARN",repr(str(_v145_exc))[:220],flush=True)

                        try:
                            _v143_tmp.unlink(missing_ok=True)
                        except Exception:
                            pass
                        try:
                            _v149_tmp.unlink(missing_ok=True)
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
