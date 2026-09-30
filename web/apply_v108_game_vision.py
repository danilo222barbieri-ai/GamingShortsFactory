from pathlib import Path
import ast

src=Path("/app/GamingShortsFactory_V107_1_STABILITY.py")
out=Path("/app/GamingShortsFactory_V108_GAME_VISION.py")
s=src.read_text(encoding="utf-8")


def _insert_after_function(source,name,block):
    tree=ast.parse(source)
    node=next(
        (n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),
        None,
    )
    if node is None:
        raise RuntimeError(f"V108 function not found: {name}")
    lines=source.splitlines(keepends=True)
    return "".join(lines[:node.end_lineno])+block.rstrip()+"\n\n"+"".join(lines[node.end_lineno:])


# ---------------------------------------------------------------------------
# One intelligence source: the existing cached prescan feeds ranking + map.
# ---------------------------------------------------------------------------
_v108_runtime=r'''
# ===== V108 GAME VISION + EVENT MAP =====
GSF_V108_GAME_VISION = True
try:
    import sys as _gsf_v108_sys
    if "/app/web" not in _gsf_v108_sys.path:
        _gsf_v108_sys.path.insert(0,"/app/web")
    from game_vision_v108 import (
        build_event_map as _gsf_v108_build_event_map,
        tag_chosen_moments as _gsf_v108_tag_chosen,
        infer_game_genre as _gsf_v108_infer_genre,
        genre_score_multiplier as _gsf_v108_genre_multiplier,
    )
except Exception as _gsf_v108_import_exc:
    raise RuntimeError("V108 Game Vision helpers unavailable: "+str(_gsf_v108_import_exc))


def _gsf_v108_game_hint():
    try:
        for _key in ("gioco","game_name","selected_game","titolo_gioco"):
            _value=st.session_state.get(_key)
            if _value:
                return str(_value)
    except Exception:
        pass
    try:
        _value=globals().get("gioco")
        if _value:
            return str(_value)
    except Exception:
        pass
    return ""


_gsf_v108_score_base=_gsf_score_ai_window
def _gsf_score_ai_window(profile,f):
    """
    V108 keeps the proven base score and only resolves close calls using the
    game profile. The multiplier is deliberately bounded to protect quality.
    """
    _base=float(_gsf_v108_score_base(profile,f))
    try:
        _genre=_gsf_v108_infer_genre(_gsf_v108_game_hint())
        _mult=float(_gsf_v108_genre_multiplier(_genre,profile,f))
        return max(0.0,_base*_mult)
    except Exception:
        return max(0.0,_base)


_gsf_v108_rank_base=_gsf_ai_rank_v3
def _gsf_ai_rank_v3(input_file, modalita, clip_duration=15, numero_clip=3, cache_token=None):
    """
    V108: expose the exact same intelligence used for the three moments.
    _gsf_ai_scan_cached is called again only after ranking, therefore it is a
    cache read, not a second media analysis.
    """
    _chosen,_diagnostics=_gsf_v108_rank_base(
        input_file,modalita,
        clip_duration=clip_duration,
        numero_clip=numero_clip,
        cache_token=cache_token,
    )
    if not isinstance(_diagnostics,dict):
        _diagnostics={}
    try:
        _scan,_scan_hit=_gsf_ai_scan_cached(input_file,cache_token=cache_token)
        _events=(_scan or {}).get("event_map_v108")
        if not isinstance(_events,list):
            _events=_gsf_v108_build_event_map(_scan,max_events=18)
            try:
                _scan["event_map_v108"]=_events
            except Exception:
                pass

        _genre=_gsf_v108_infer_genre(_gsf_v108_game_hint())
        _duration=max(10.0,float(clip_duration))
        _tagged=_gsf_v108_tag_chosen(
            _events,_chosen,_diagnostics,_duration
        )

        _diagnostics["__event_map__"]=_tagged
        _diagnostics["__game_genre__"]=_genre
        _meta=_diagnostics.setdefault("__meta__",{})
        if isinstance(_meta,dict):
            _meta["event_map"]="v108-shared-prescan"
            _meta["event_map_count"]=len(_tagged)
            _meta["event_map_cache_hit"]=bool(_scan_hit)
            _meta["game_genre"]=_genre

        st.session_state["gsf_v108_event_map"]=_tagged
        st.session_state["gsf_v108_game_genre"]=_genre
        st.session_state["gsf_v108_chosen_moments"]=[
            {"rank":_i+1,"score":float(_item[0]),"start":float(_item[1])}
            for _i,_item in enumerate(_chosen or [])
            if isinstance(_item,(list,tuple)) and len(_item)>=2
        ]
        st.session_state["gsf_v108_event_map_engine"]="shared-prescan-v1"
        print(
            "GSF_V108_EVENT_MAP",
            "events="+str(len(_tagged)),
            "chosen="+str(len(_chosen or [])),
            "genre="+str(_genre),
            "scan_cache_hit="+str(bool(_scan_hit)),
            flush=True,
        )
    except Exception as _gsf_v108_event_exc:
        print("GSF_V108_EVENT_MAP_WARN",repr(str(_gsf_v108_event_exc)),flush=True)
    return _chosen,_diagnostics
# ===== /V108 GAME VISION + EVENT MAP =====
'''

s=_insert_after_function(s,"_gsf_ai_rank_v3",_v108_runtime)

# ---------------------------------------------------------------------------
# Editor receives the absolute clip origin. The component only sees the small
# relative event window that belongs to the media it can actually play.
# ---------------------------------------------------------------------------
_inline_old='''                            _gsf_inline_state=_gsf_render_editor_2027_embed(
                                _gsf_ed27_path,
                                height=660,
                                key=_gsf_inline_component_key,
                                initial_state=_gsf_inline_saved,
                            )
'''
_inline_new='''                            _gsf_inline_state=_gsf_render_editor_2027_embed(
                                _gsf_ed27_path,
                                height=660,
                                key=_gsf_inline_component_key,
                                initial_state=_gsf_inline_saved,
                                clip_start=float(start),
                                source_duration=float(durata_effettiva),
                            )
'''
if _inline_old not in s:
    raise RuntimeError("V108 inline Editor 2027 call anchor missing")
s=s.replace(_inline_old,_inline_new,1)

_manual_old='''        _gsf_manual_editor_state=_gsf_render_manual_editor_2027(
            _gsf_manual_editor_media,height=720,key=_gsf_manual_component_key,initial_state=_gsf_manual_saved_state
        )
'''
_manual_new='''        _gsf_manual_editor_state=_gsf_render_manual_editor_2027(
            _gsf_manual_editor_media,
            height=720,
            key=_gsf_manual_component_key,
            initial_state=_gsf_manual_saved_state,
            clip_start=0.0,
            source_duration=float(_gsf_manual_duration),
        )
'''
if _manual_old not in s:
    raise RuntimeError("V108 manual Editor 2027 call anchor missing")
s=s.replace(_manual_old,_manual_new,1)

# Version marker is deliberately additive; old stability markers remain so
# regression tests and draft compatibility continue to work.
s='GSF_V108_GAME_VISION = True\n'+s

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V108 Game Vision/Event Map patch applied:",out)
