from __future__ import annotations

from pathlib import Path
from frame_vision_v135 import build_frame_manifest


def _d(v):
    return dict(v) if isinstance(v,dict) else {}


def _l(v):
    return list(v) if isinstance(v,list) else []


def build_director_evidence(video_path,duration,brain,one_click,out_dir=None):
    """Connect V131-V135 intelligence so downstream engines consume the same evidence."""
    brain=_d(brain); package=_d(one_click)
    moments=_l(brain.get("selected"))+_l(brain.get("alternates"))
    vision=build_frame_manifest(video_path,duration,moments,out_dir=out_dir)
    recognition=_d(package.get("game_recognition"))
    context=_d(package.get("game_context"))
    future=_d(package.get("director_future_stack"))
    session=_d(package.get("session_intelligence"))
    frame_paths=[x.get("path") for x in _l(vision.get("frames")) if isinstance(x,dict) and x.get("path")]
    return {
        "engine":"v136-director-orchestrator",
        "source":str(Path(video_path)),
        "game":{"recognition":recognition,"context":context},
        "session":session,
        "frames":vision,
        "cover_ai":{
            **_d(future.get("cover_ai")),
            "frame_candidates":frame_paths[:12],
            "operational":bool(frame_paths),
        },
        "privacy_visual_guard":{
            **_d(future.get("privacy_visual_guard")),
            "frame_candidates":frame_paths,
            "operational":bool(frame_paths),
        },
        "retention_lab":_d(future.get("retention_lab")),
        "creator_style_learning":_d(future.get("creator_style_learning")),
        "audio_intelligence":_d(future.get("audio_intelligence")),
        "publishing_intelligence":_d(future.get("publishing_intelligence")),
        "performance_learning":_d(future.get("performance_learning")),
        "long_form_director":_d(future.get("long_form_director")),
        "game_specific_director":_d(future.get("game_specific_director")),
        "next_consumers":["vision_provider","ocr_provider","cover_ranker","style_store","retention_ranker"],
    }


def readiness(evidence):
    e=_d(evidence); frames=_d(e.get("frames"))
    return {
        "frames_ready":bool(frames.get("sample_count")),
        "game_context_ready":bool(_d(e.get("game")).get("recognition")),
        "cover_ready":bool(_d(e.get("cover_ai")).get("operational")),
        "privacy_scan_ready":bool(_d(e.get("privacy_visual_guard")).get("operational")),
        "style_learning_ready":bool(e.get("creator_style_learning")),
        "retention_ready":bool(e.get("retention_lab")),
        "long_form_ready":bool(e.get("long_form_director")),
    }
