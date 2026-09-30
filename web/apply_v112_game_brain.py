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
        _meta["game_brain"]="v117-editor-semantic"
        _meta["candidate_pool"]=len(_pool or [])
        _meta["final_moments"]=len(_chosen or [])
    print(
        "GSF_V117_GAME_BRAIN",
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
