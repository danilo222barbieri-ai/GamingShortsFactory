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
    return {
        "engine":"v142-director-runtime",
        "selected_short":short_pkg,
        "evidence":evidence,
        "vision":vision,
        "creator_profile":profile,
        "ab":ab,
        "render":render,
        "long_form":long_form,
        "content_fingerprint":content_fingerprint(evidence),
        "ready":bool(short_pkg and render.get("ready")),
    }


def apply_pipeline_to_recipe(recipe,pipeline):
    """Freeze runtime AI decisions into the render recipe consumed by workers."""
    out=dict(recipe or {}); p=_d(pipeline)
    render=_d(p.get("render")); selected=_d(p.get("selected_short"))
    if selected.get("render",{}).get("plan") and not out.get("ai_director_plan"):
        out["ai_director_plan"]=_d(selected["render"].get("plan"))
    out["director_runtime_v142"]={
        "engine":p.get("engine"),
        "ab":p.get("ab"),
        "content_fingerprint":p.get("content_fingerprint"),
        "publish_guard":render.get("publish_guard","clear"),
        "operation_count":render.get("operation_count",0),
    }
    out["ai_render_operations"]=_l(render.get("operations"))
    out["ai_ab_strategy"]=_d(p.get("ab")).get("winner")
    out["ai_creator_style"]=_d(p.get("creator_profile"))
    vision=_d(p.get("vision"))
    covers=_l(vision.get("cover_candidates"))
    if covers:
        out["ai_cover"]=covers[0]
        out["ai_thumbnail_offset"]=covers[0].get("time")
    out["ai_visual_cleanup"]={
        "recommended":bool(vision.get("cleanup_recommended")),
        "overlays":_l(vision.get("overlay_findings")),
        "privacy":_l(vision.get("privacy_findings")),
    }
    out["ai_publish_guard"]=vision.get("publish_guard","clear")
    return out
