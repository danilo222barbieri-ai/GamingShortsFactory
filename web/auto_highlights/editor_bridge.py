"""Bridge between an Auto Highlights item and Editor 2027.

The VOD/media resolver is injected: Twitch/YouTube URLs are not handed directly
to the editor. The caller resolves/materializes only the selected highlight.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping

@dataclass(frozen=True)
class EditorLaunch:
    video_path: str
    initial_state: dict
    source: dict

def highlight_editor_state(item: Mapping) -> dict:
    start=max(0.0,float(item.get("start_seconds") or 0.0))
    end=max(start+.5,float(item.get("end_seconds") or start+30.0))
    # Editor 2027 works on the materialized highlight clip, so its local
    # timeline begins at zero while source timestamps remain as metadata.
    return {
        "inPoint":0.0,
        "outPoint":min(60.0,max(.5,end-start)),
        "aiMode":"Auto Gaming",
        "autoHighlightSourceStart":start,
        "autoHighlightSourceEnd":end,
        "autoHighlightId":str(item.get("id") or ""),
    }

def prepare_editor_launch(*, folder: Mapping, item: Mapping,
                          materialize_clip: Callable[[Mapping,Mapping],str]) -> EditorLaunch:
    path=str(materialize_clip(folder,item) or "")
    if not path:
        raise ValueError("Auto Highlight clip is not available for Editor 2027")
    return EditorLaunch(
        video_path=path,
        initial_state=highlight_editor_state(item),
        source={
            "kind":"auto_highlight",
            "provider":str(folder.get("provider") or ""),
            "broadcast_id":str(folder.get("broadcast_id") or ""),
            "highlight_id":str(item.get("id") or ""),
            "source_start_seconds":float(item.get("start_seconds") or 0.0),
            "source_end_seconds":float(item.get("end_seconds") or 0.0),
        },
    )

def stash_editor_launch(session_state, launch: EditorLaunch) -> None:
    session_state["gsf_source_path"]=launch.video_path
    session_state["gsf_editor_source_path"]=launch.video_path
    session_state["gsf_auto_highlight_launch"]={
        "video_path":launch.video_path,
        "initial_state":dict(launch.initial_state),
        "source":dict(launch.source),
    }
