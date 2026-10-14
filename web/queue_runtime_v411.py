"""Observe real production references using the prepared Alive/ProjectState APIs."""
import uuid
import os
from pathlib import Path
from gsf_alive import AliveEventType, emit_alive, render_alive, sync_alive_from_session
from gsf_alive_notifications import render_alive_notification
from gsf_project_state import (ProjectEvent, ProjectEventType, load_project_session,
                               new_project, reduce_project, save_project_session)


def first_ref(session, names):
    for name in names:
        value = session.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def sync_project(session):
    project_id = first_ref(session, ('gsf_active_project_id', 'gsf_v157_project_id', 'project_id'))
    project_id = project_id or session.setdefault('_gsf_queue_project_id', uuid.uuid4().hex)
    state = load_project_session(session, project_id=project_id)
    previous_final = state.final_ref
    if state.project_id != project_id:
        state = new_project(project_id)
    source = first_ref(session, ('gsf_source_path', 'gsf_editor_source_path', 'video_path', 'input_video'))
    final = first_ref(session, ('gsf_final_short_path', 'final_short_path', 'short_path', 'output_video'))
    revision = str(session.get('publication_final_signature') or '')
    if source and session.get('publication_ready'):
        try:
            sessions = (Path(os.environ.get('GSF_RUNTIME_ROOT','/tmp/gsf-runtime'))/'sessions').resolve()
            sid = Path(source).resolve().relative_to(sessions).parts[0]
            stable = sessions/sid/'media'/'gaming_short_finale_share.mp4'
            stat = stable.stat()
            started = float(session.get('gsf_v107_render_started_at') or 0)
            if stat.st_size > 1024 and stat.st_mtime >= started-1:
                final = str(stable)
                revision += ':'+str(stat.st_mtime_ns)+':'+str(stat.st_size)
        except (OSError, ValueError, IndexError):
            pass
    if source and source != state.source_ref:
        if final and final == previous_final:
            session['gsf_queue_invalid_final_ref'] = final
        state = reduce_project(state, ProjectEvent(ProjectEventType.SOURCE_ATTACHED, {'source_ref': source}))
        emit_alive(session, AliveEventType.UPLOAD_COMPLETED)
    changed_revision = revision and revision != session.get('gsf_queue_final_revision')
    if final and (final != session.get('gsf_queue_invalid_final_ref') or changed_revision) and state.source_ref and (final != state.final_ref or changed_revision):
        session.pop('gsf_queue_invalid_final_ref', None)
        state = reduce_project(state, ProjectEvent(ProjectEventType.RENDER_COMPLETED, {'final_ref': final}))
        emit_alive(session, AliveEventType.RENDER_COMPLETED)
        session['gsf_queue_final_revision'] = revision
    save_project_session(session, state)
    return state


def render_queue_runtime(st_module):
    sync_project(st_module.session_state)
    state = sync_alive_from_session(st_module.session_state)
    render_alive(st_module, state, show_status=state.mode.value in {'working', 'celebrate', 'error'})
    render_alive_notification(st_module, st_module.session_state, state)


