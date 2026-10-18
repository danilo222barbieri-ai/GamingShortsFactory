"""Adapt the existing mobile autosave to the existing final-render recipe.

No renderer or UI lives here. Source and clip binding prevents edits from a
previous upload/candidate leaking into another project or accumulating trims.
"""
import json
import math
from pathlib import Path


def current_source_key(session_root):
    try:
        marker = json.loads((Path(session_root)/'media/.direct_upload_ready.json').read_text())
    except (OSError, ValueError):
        return ''
    upload = str(marker.get('upload_id') or '')
    return upload if upload and upload != 'draft' else str(marker.get('path') or '')


def read_editor_snapshot(session_root):
    try:
        payload = json.loads((Path(session_root)/'editor_overlay_state.json').read_text())
    except (OSError, ValueError):
        return {}
    source = current_source_key(session_root)
    if not source or not isinstance(payload, dict) or payload.get('source_key') != source:
        return {}
    return payload if isinstance(payload.get('state'), dict) else {}


def _number(value, fallback):
    try:
        value = float(value)
        return value if math.isfinite(value) else fallback
    except (ValueError, TypeError):
        return fallback


def apply_saved_editor_recipe(recipe, session_root, render_kwargs_builder, session_state):
    recipe = dict(recipe or {})
    saved = read_editor_snapshot(session_root)
    if not saved:
        return recipe
    context = saved.get('context') or {}
    state = dict(saved['state'])
    base_start = _number(recipe.get('mobile_editor_base_start', recipe.get('start')), 0)
    clip_start = _number(context.get('clip_start'), base_start)
    if abs(base_start-clip_start) > .1:
        return recipe
    duration = max(.5, _number(context.get('clip_duration'), _number(state.get('sourceDuration'), _number(recipe.get('duration'), 15))))
    start = max(0, min(duration-.5, _number(state.get('inPoint'), 0)))
    end = max(start+.5, min(duration, _number(state.get('outPoint'), duration)))
    kwargs = render_kwargs_builder(state, session_state)
    recipe.update(kind='inline_editor', start=base_start+start, duration=end-start,
                  mobile_editor_base_start=base_start, render_kwargs=kwargs,
                  editor_2027_state=state,
                  subtitles_enabled=kwargs.get('subtitles_enabled', True))
    return recipe


def render_boundary(session_root):
    """Earliest valid render start for this upload and its saved edits."""
    root=Path(session_root)
    try:
        upload=json.loads((root/'media/.direct_upload_ready.json').read_text())
        boundary=_number(upload.get('completed_at'),0)
    except (OSError,ValueError,AttributeError):
        boundary=0
    saved=read_editor_snapshot(root)
    return max(boundary,_number(saved.get('updated_at'),0))


def local_final_is_current(session_root):
    root=Path(session_root)
    final=root/'media/gaming_short_finale_share.mp4'
    try:
        stat=final.stat()
        if stat.st_size<=1024:
            return False
        try:
            job=json.loads((root/'render_job.json').read_text())
            started=_number(job.get('started_at'),0)
        except (OSError,ValueError,AttributeError):
            started=0
        return stat.st_mtime>=started and (started or stat.st_mtime)>=render_boundary(root)
    except OSError:
        return False
