from __future__ import annotations


def _f(v,d=0.0):
    try:return float(v)
    except Exception:return float(d)


def compile_render_plan(package, creator_profile=None, ab_result=None, vision=None):
    """Compile Director intelligence into concrete render operations.

    Renderer adapters consume this list in order; this is the bridge from AI decisions
    to actual trim/reframe/speed/replay/caption/audio/cover behavior.
    """
    p=dict(package or {}); mount=dict(p.get("mount") or {}); ops=[]
    trim=dict(mount.get("trim") or {})
    ops.append({"op":"trim","start":max(0,_f(trim.get("start"))),"end":max(0,_f(trim.get("end"),15))})
    frame=dict(mount.get("framing") or {})
    if frame.get("smart_reframe"):
        ops.append({"op":"reframe","zoom":_f(frame.get("zoom"),1),"pan_x":_f(frame.get("pan_x")),
                    "pan_y":_f(frame.get("pan_y")),"hud_mode":frame.get("hud_mode","Smart Safe"),
                    "protect":frame.get("hud_elements") or []})
    cine=dict(mount.get("cinematic") or {})
    cold=dict(cine.get("cold_open") or {})
    if cold.get("enabled"): ops.append({"op":"cold_open","duration":_f(cold.get("duration"),.7),"source":"payoff"})
    for x in cine.get("pattern_interrupts") or []:
        if isinstance(x,dict): ops.append({"op":"pattern_interrupt","start":_f(x.get("start")),"duration":_f(x.get("duration")),"mode":x.get("action","micro_cut")})
    slow=dict(cine.get("slow_motion") or {})
    if slow.get("enabled"): ops.append({"op":"slow_motion",**slow})
    replay=dict(cine.get("replay") or {})
    if replay.get("enabled"): ops.append({"op":"replay",**replay})
    captions=dict(mount.get("captions") or {})
    ops.append({"op":"captions",**captions})
    audio=dict(mount.get("audio") or {})
    ops.append({"op":"audio",**audio})
    if mount.get("hook"): ops.append({"op":"hook","text":mount["hook"]})
    ending=dict(cine.get("smart_ending") or {})
    if ending: ops.append({"op":"smart_ending",**ending})
    profile=dict(creator_profile or {})
    if profile:
        ops.append({"op":"creator_style","cut_density":profile.get("cut_density"),"zoom_aggression":profile.get("zoom_aggression"),
                    "caption_density":profile.get("caption_density"),"replay_preference":profile.get("replay_preference")})
    if ab_result: ops.append({"op":"ab_strategy","choice":dict(ab_result).get("winner"),"scores":dict(ab_result).get("scores")})
    vr=dict(vision or {})
    covers=vr.get("cover_candidates") or []
    if covers: ops.append({"op":"cover","path":covers[0].get("path"),"time":covers[0].get("time"),"score":covers[0].get("score")})
    if vr.get("cleanup_recommended"): ops.append({"op":"visual_cleanup","findings":vr.get("overlay_findings") or []})
    return {"engine":"v139-render-director","operations":ops,"operation_count":len(ops),
            "publish_guard":vr.get("publish_guard","clear"),"ready":bool(ops)}
