from __future__ import annotations

from pathlib import Path

from creator_learning_v138 import choose_ab, learn, load_profile, save_profile
from director_orchestrator_v136 import build_director_evidence
from long_form_director_v141 import build_long_form, compile_long_form_operations
from render_director_v139 import compile_render_plan
from vision_consumers_v137 import consume_vision_evidence, content_fingerprint


def _d(v):
    return dict(v) if isinstance(v, dict) else {}


def _l(v):
    return [dict(x) for x in (v or []) if isinstance(x, dict)]


def _selected_short(one_click, selected_start=None):
    rows=_l(_d(one_click).get("shorts"))
    if not rows:
        return {}
    if selected_start is None:
        return rows[0]
    wanted=float(selected_start or 0.0)
    return min(rows,key=lambda x:abs(float(x.get("start") or 0.0)-wanted))


def _ab_candidates(short_pkg):
    s=_d(short_pkg)
    intel=_d(s.get("director_intelligence"))
    ret=_d(intel.get("retention_prediction"))
    story=_d(intel.get("story_understanding"))
    reaction=_d(intel.get("reaction"))
    payoff=float(ret.get("payoff_delay") or 0.0)
    target=float(_d(_d(s.get("mount")).get("trim")).get("target_duration") or 15.0)
    payoff_ratio=min(1.0,max(0.0,payoff/max(target,1.0)))
    dead=float(ret.get("dead_air_seconds") or 0.0)
    dead_ratio=min(1.0,max(0.0,dead/max(target,1.0)))
    stakes=float(story.get("stakes_score") or .5)
    react=float(reaction.get("strength") or .5)
    structural=float(ret.get("structural_score") or .5)
    a={
        "name":"action_first",
        "hook_strength":min(1.0,structural+.12),
        "stakes":stakes,
        "reaction":react,
        "payoff_delay_ratio":max(0.0,payoff_ratio-.12),
        "dead_air_ratio":max(0.0,dead_ratio-.08),
        "rhythm":min(1.0,.72+structural*.20),
    }
    b={
        "name":"context_first",
        "hook_strength":min(1.0,structural+.04),
        "stakes":min(1.0,stakes+.14),
        "reaction":react,
        "payoff_delay_ratio":payoff_ratio,
        "dead_air_ratio":dead_ratio,
        "rhythm":min(1.0,.58+structural*.20),
    }
    return a,b


def run_director_pipeline(
    video_path,
    duration,
    brain,
    one_click,
    runtime_dir,
    *,
    selected_start=None,
    provider_results=None,
    creator_event=None,
):
    """Execute the full V134→V141 intelligence chain for one selected Short."""
    brain=_d(brain); one_click=_d(one_click)
    root=Path(runtime_dir); root.mkdir(parents=True,exist_ok=True)
    evidence=build_director_evidence(video_path,duration,brain,one_click,out_dir=root/"vision")
    if provider_results is None:
        try:
            _visual=__import__("visual_scoring_v144",fromlist=["enrich_frame_manifest"])
            provider_results=_visual.enrich_frame_manifest(dict(evidence.get("frames") or {}))
        except Exception:
            provider_results=[]
    vision=consume_vision_evidence(evidence,provider_results=provider_results)
    short_pkg=_selected_short(one_click,selected_start)
    profile_path=root/"creator_style.json"
    profile=load_profile(profile_path)
    a,b=_ab_candidates(short_pkg)
    ab=choose_ab(a,b,profile)
    ab["variants"]={"A":a.get("name"),"B":b.get("name")}
    render=compile_render_plan(short_pkg,profile,ab,vision)
    all_moments=_l(brain.get("selected"))+_l(brain.get("alternates"))
    long_form=build_long_form(all_moments,8)
    long_form["operations"]=compile_long_form_operations(long_form)
    if creator_event:
        profile=learn(profile,_d(creator_event))
        save_profile(profile_path,profile)
    source_fp=content_fingerprint(evidence)
    try:
        _mem=__import__("content_memory_v145",fromlist=["candidate_fingerprint"])
        candidate_fp=_mem.candidate_fingerprint(source_fp,short_pkg)
    except Exception:
        candidate_fp=source_fp
    return {
        "engine":"v142-director-runtime",
        "selected_short":short_pkg,
        "evidence":evidence,
        "vision":vision,
        "creator_profile":profile,
        "ab":ab,
        "render":render,
        "long_form":long_form,
        "source_fingerprint":source_fp,
        "content_fingerprint":candidate_fp,
        "ready":bool(short_pkg and render.get("ready")),
    }


def apply_pipeline_to_recipe(recipe,pipeline):
    """Freeze runtime AI decisions into the render recipe consumed by workers."""
    out=dict(recipe or {}); p=_d(pipeline)
    render=_d(p.get("render")); selected=_d(p.get("selected_short"))
    if selected.get("render",{}).get("plan") and not out.get("ai_director_plan"):
        out["ai_director_plan"]=_d(selected["render"].get("plan"))
    # Blend learned creator preferences back into the actual Director plan.
    _plan=_d(out.get("ai_director_plan"))
    _frame=_d(_plan.get("framing"))
    _edit=_d(_plan.get("edit"))
    _profile=_d(p.get("creator_profile"))
    if _frame and _profile:
        try:
            _zoom=float(_frame.get("zoom") or 1.0)
            _learned=1.0+0.45*float(_profile.get("zoom_aggression") or 0.0)
            _frame["zoom"]=round(max(1.0,min(1.8,_zoom*.72+_learned*.28)),3)
        except Exception:
            pass
        _plan["framing"]=_frame
    if _edit and _profile:
        _replay=_d(_edit.get("replay"))
        if _replay and float(_profile.get("replay_preference") or 0.0)<.22:
            _replay["enabled"]=False
            _edit["replay"]=_replay
        _plan["edit"]=_edit
    if _plan:
        out["ai_director_plan"]=_plan
    out["director_runtime_v142"]={
        "engine":p.get("engine"),
        "ab":p.get("ab"),
        "source_fingerprint":p.get("source_fingerprint"),
        "content_fingerprint":p.get("content_fingerprint"),
        "content_memory":_d(p.get("content_memory")),
        "publish_guard":render.get("publish_guard","clear"),
        "operation_count":render.get("operation_count",0),
    }
    out["ai_source_fingerprint"]=p.get("source_fingerprint")
    out["ai_content_fingerprint"]=p.get("content_fingerprint")
    if p.get("content_memory"):
        out["ai_content_memory"]=_d(p.get("content_memory"))
        out["ai_duplicate_guard"]=bool(_d(p.get("content_memory")).get("duplicate"))
    if p.get("content_memory_record"):
        out["ai_content_memory_record"]=_d(p.get("content_memory_record"))
    out["ai_render_operations"]=_l(render.get("operations"))
    out["ai_ab_strategy"]=_d(p.get("ab")).get("winner")
    out["ai_creator_style"]=_d(p.get("creator_profile"))
    vision=_d(p.get("vision"))
    covers=_l(vision.get("cover_candidates"))
    if covers:
        out["ai_cover"]=covers[0]
        out["ai_thumbnail_offset"]=covers[0].get("time")
        # Existing V125 thumbnail extractor consumes edit.thumbnail_offset,
        # so route the Vision-selected cover into that proven renderer path.
        try:
            _plan=_d(out.get("ai_director_plan"))
            _edit=_d(_plan.get("edit"))
            _edit["thumbnail_offset"]=round(
                max(0.0,float(covers[0].get("time") or 0.0)-float(out.get("start") or 0.0)),3
            )
            _plan["edit"]=_edit
            out["ai_director_plan"]=_plan
        except Exception:
            pass
    out["ai_visual_cleanup"]={
        "recommended":bool(vision.get("cleanup_recommended")),
        "overlays":_l(vision.get("overlay_findings")),
        "privacy":_l(vision.get("privacy_findings")),
    }
    out["ai_publish_guard"]=vision.get("publish_guard","clear")
    return out
