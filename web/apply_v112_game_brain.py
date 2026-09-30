from pathlib import Path

src=Path("/app/GamingShortsFactory_V111_FINAL_VISIBLE.py")
out=Path("/app/GamingShortsFactory_V112_GAME_BRAIN.py")
s=src.read_text(encoding="utf-8")

# V112 quality-first pool: eight refined candidates feed the second-stage brain.
old="""    shortlist_target=6
    coarse_target=7 if adaptive_scan else shortlist_target
"""
new="""    shortlist_target=8
    coarse_target=10 if adaptive_scan else shortlist_target
"""
if old not in s:
    raise RuntimeError("V112 shortlist anchor missing")
s=s.replace(old,new,1)

marker="# ===== /V108 GAME VISION + EVENT MAP ====="
if marker not in s:
    raise RuntimeError("V112 V108 insertion marker missing")

runtime=r'''
# ===== V112 GAME BRAIN =====
GSF_V112_GAME_BRAIN=True
try:
    import sys as _gsf_v112_sys
    if "/app/web" not in _gsf_v112_sys.path:
        _gsf_v112_sys.path.insert(0,"/app/web")
    from game_brain_v112 import rerank_moments as _gsf_v112_rerank
except Exception as _gsf_v112_import_exc:
    raise RuntimeError("V112 Game Brain unavailable: "+str(_gsf_v112_import_exc))

_gsf_v112_rank_base=_gsf_ai_rank_v3
def _gsf_ai_rank_v3(input_file, modalita, clip_duration=15, numero_clip=3, cache_token=None):
    _target=max(1,int(numero_clip or 3))
    _pool_target=max(8,_target)
    _pool,_diagnostics=_gsf_v112_rank_base(
        input_file,modalita,
        clip_duration=clip_duration,
        numero_clip=_pool_target,
        cache_token=cache_token,
    )
    if not isinstance(_diagnostics,dict):
        _diagnostics={}
    _mode=str(modalita or "").lower()
    if "reaz" in _mode or "reaction" in _mode:
        _profile="reaction"
    elif "azione" in _mode or "action" in _mode:
        _profile="action"
    elif "miglior" in _mode or "best" in _mode or "director" in _mode:
        _profile="director"
    else:
        _profile="auto"
    try:
        _genre=str(st.session_state.get("gsf_v108_game_genre") or "Auto")
    except Exception:
        _genre="Auto"
    _events=_diagnostics.get("__event_map__") or []
    _chosen,_brain=_gsf_v112_rerank(
        _pool,_diagnostics,
        clip_duration=float(clip_duration),
        numero_clip=_target,
        profile=_profile,
        genre=_genre,
        events=_events,
    )
    # V125: persistent rank override. A replacement is a real ranked moment,
    # not a cosmetic UI swap, so preview/editor/final render all receive it.
    try:
        _overrides=st.session_state.get("gsf_v125_rank_overrides") or {}
        if isinstance(_overrides,dict) and _overrides:
            _selected_rows=list((_brain or {}).get("selected") or [])
            _alternate_rows=list((_brain or {}).get("alternates") or [])
            for _rank_raw,_start_raw in list(_overrides.items()):
                try:
                    _rank=int(_rank_raw)
                    _wanted=float(_start_raw)
                except Exception:
                    continue
                _idx=_rank-1
                if _idx<0 or _idx>=len(_selected_rows) or _idx>=len(_chosen):
                    continue
                _alt=None
                for _row in _alternate_rows:
                    if not isinstance(_row,dict):
                        continue
                    if abs(float(_row.get("start") or 0.0)-_wanted)<=0.35:
                        _alt=dict(_row)
                        break
                if _alt is None:
                    # The requested moment may already be selected after a rerun.
                    for _row in _selected_rows:
                        if isinstance(_row,dict) and abs(float(_row.get("start") or 0.0)-_wanted)<=0.35:
                            _alt=dict(_row)
                            break
                if _alt is None:
                    continue
                _old=dict(_selected_rows[_idx] or {})
                _alt["rank"]=_rank
                _alt["replaced_from_start"]=float(_old.get("start") or 0.0)
                _alt["replacement_override"]=True
                _selected_rows[_idx]=_alt
                _chosen[_idx]=(
                    float(_alt.get("brain_score") or _chosen[_idx][0]),
                    float(_alt.get("start") or _wanted),
                )
                _alternate_rows=[
                    row for row in _alternate_rows
                    if not (
                        isinstance(row,dict)
                        and abs(float(row.get("start") or 0.0)-float(_alt.get("start") or _wanted))<=0.35
                    )
                ]
                if _old:
                    _old["replacement_candidate"]=True
                    _alternate_rows.insert(0,_old)
            if isinstance(_brain,dict):
                _brain["selected"]=_selected_rows
                _brain["alternates"]=_alternate_rows[:4]
                _brain["rank_overrides"]={
                    str(k):float(v) for k,v in _overrides.items()
                    if str(v).strip()
                }
    except Exception as _v125_override_exc:
        print("GSF_V125_OVERRIDE_WARN",repr(str(_v125_override_exc))[:220],flush=True)
    try:
        _clean_events=[]
        for _event in (_events or []):
            if not isinstance(_event,dict):
                continue
            _row=dict(_event)
            _row.pop("selected_rank",None)
            _row.pop("selected_start",None)
            _row.pop("selected_score",None)
            _clean_events.append(_row)
        if "_gsf_v108_tag_chosen" in globals():
            _clean_events=_gsf_v108_tag_chosen(
                _clean_events,_chosen,_diagnostics,max(1.0,float(clip_duration))
            )
        _diagnostics["__event_map__"]=_clean_events
        st.session_state["gsf_v108_event_map"]=_clean_events
        st.session_state["gsf_v112_brain_context"]=_brain
        st.session_state["gsf_v124_director_context"]={
            "engine":str(_brain.get("engine") or "game-brain-v124-ai-director"),
            "selected":list(_brain.get("selected") or []),
            "alternates":list(_brain.get("alternates") or []),
        }
        _top=(list(_brain.get("selected") or []) or [{}])[0]
        _top_plan=dict((_top or {}).get("director_plan") or {})
        st.session_state["gsf_v124_social_pack"]=dict(
            ((_top_plan.get("text") or {}).get("social") or {})
        )
        st.session_state["gsf_v108_chosen_moments"]=[
            {"rank":_i+1,"score":float(_item[0]),"start":float(_item[1])}
            for _i,_item in enumerate(_chosen or [])
            if isinstance(_item,(list,tuple)) and len(_item)>=2
        ]
    except Exception as _brain_state_exc:
        print("GSF_V112_STATE_WARN",repr(str(_brain_state_exc)),flush=True)
    _diagnostics["__brain_v112__"]=_brain
    _meta=_diagnostics.setdefault("__meta__",{})
    if isinstance(_meta,dict):
        _meta["game_brain"]="v124-ai-director"
        _meta["candidate_pool"]=len(_pool or [])
        _meta["final_moments"]=len(_chosen or [])
    print(
        "GSF_V124_AI_DIRECTOR",
        "pool="+str(len(_pool or [])),
        "chosen="+str(len(_chosen or [])),
        "profile="+_profile,
        "genre="+_genre,
        flush=True,
    )
    return _chosen,_diagnostics
# ===== /V112 GAME BRAIN =====
'''
s=s.replace(marker,marker+"\n"+runtime,1)
s=s.replace("Gaming Shorts Factory · V111","Gaming Shorts Factory · V112")
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V112 Game Brain applied:",out)
