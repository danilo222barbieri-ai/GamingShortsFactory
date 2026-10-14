from pathlib import Path
import importlib.util
from web.queue_runtime_v411 import sync_project
from web.fix_v411_queue_runtime import patch_app_source, patch_csrf_hub, patch_csrf_server, patch_draft_delete_semantics
from gsf_project_state import PROJECT_SESSION_KEY


def test_real_render_file_updates_project_without_raw_bytes(tmp_path, monkeypatch):
    monkeypatch.setenv('GSF_RUNTIME_ROOT',str(tmp_path))
    media=tmp_path/'sessions'/'browser'/'media'
    media.mkdir(parents=True)
    source=media/'source.mp4'
    final=media/'gaming_short_finale_share.mp4'
    final.write_bytes(b'x'*2048)
    session={'gsf_source_path':str(source),'publication_ready':True,'publication_final_signature':'render1'}
    assert sync_project(session).final_ref==str(final)
    assert len(str(session[PROJECT_SESSION_KEY]))<3000


def test_desktop_access_keeps_media_authorization():
    from web.fix_v411_queue_runtime import patch_desktop_access
    config='error_page 424 = /__gsf_mobile_gate;\nif ($gsf_mobile_client = 0) {\n return 424;\n}\nif ($gsf_media_sid = "") { return 403; }\n'
    changed=patch_desktop_access(config)
    assert 'return 424' not in changed
    assert 'return 403' in changed
    assert patch_desktop_access(changed)==changed


def test_signature_reset_does_not_resurrect_previous_source_render(tmp_path,monkeypatch):
    monkeypatch.setenv('GSF_RUNTIME_ROOT',str(tmp_path))
    media=tmp_path/'sessions'/'browser'/'media';media.mkdir(parents=True)
    final=media/'gaming_short_finale_share.mp4';final.write_bytes(b'x'*2048)
    session={'gsf_source_path':str(media/'one.mp4'),'publication_ready':True,'publication_final_signature':'old'}
    assert sync_project(session).final_ref
    session.update(gsf_source_path=str(media/'two.mp4'),publication_final_signature='')
    assert sync_project(session).final_ref is None
    assert sync_project(session).final_ref is None
    final.write_bytes(b'y'*3072)
    assert sync_project(session).final_ref==str(final)


def test_project_switch_does_not_keep_previous_identity():
    session={'gsf_active_project_id':'one','gsf_source_path':'/one.mp4'}
    assert sync_project(session).project_id=='one'
    session.update(gsf_active_project_id='two',gsf_source_path='/two.mp4')
    state=sync_project(session)
    assert state.project_id=='two'
    assert state.source_ref=='/two.mp4'


def test_new_source_invalidates_previous_final():
    session={'gsf_active_project_id':'one','gsf_source_path':'/one.mp4','final_short_path':'/final-one.mp4'}
    assert sync_project(session).final_ref=='/final-one.mp4'
    session['gsf_source_path']='/two.mp4'
    assert sync_project(session).final_ref is None
    assert sync_project(session).final_ref is None


def test_raw_media_never_enters_project_state():
    session={'gsf_active_project_id':'one','gsf_source_path':b'x'*1000000}
    state=sync_project(session)
    assert state.source_ref is None
    assert len(str(session[PROJECT_SESSION_KEY]))<2000


def test_bootstrap_is_single_and_preserves_existing_home():
    source='import streamlit as st\nif True:\n    _gsf_v154_event=_gsf_render_home_v154()\n'
    patched=patch_app_source(source)
    compile(patched,'test','exec')
    assert patch_app_source(patched)==patched
    assert patched.count('render_queue_runtime(st)')==1
    assert '_gsf_v154_event=_gsf_render_home_v154()' in patched


def test_csrf_bridge_only_changes_own_session_response():
    source='GSF_SECURITY_V410\nif clean=="/creator-hub/state":\n    _json(self,200,{"ok":True,})\nif clean=="/account":\n    pass\n'
    changed=patch_csrf_server(source)
    assert '"csrf_token":_security_csrf_token(sid)' in changed
    assert patch_csrf_server(changed)==changed
    hub="await fetch('/drafts/delete?id='+encodeURIComponent(id),{credentials:'same-origin',redirect:'follow',cache:'no-store'});"
    changed=patch_csrf_hub(hub)
    assert "method:'POST'" in changed and "'X-GSF-CSRF':identity.csrf_token" in changed
    assert 'if(!response.ok||!result.ok)throw' in changed
    assert patch_csrf_hub(changed)==changed


def test_csrf_bridge_targets_full_state_after_v366_header_response():
    source='''GSF_SECURITY_V410
if clean=="/creator-hub/state":
    sid=_social_sid(self)
    scope=str((parse_qs(path.query).get("scope") or [""])[0] or "")
    if scope=="header":
        _json(self,200,{
            "ok":True,
            "account":{"connected":False},
        })
        return
    profile=_creator_account_load(sid) or {}
    _json(self,200,{
        "ok":True,
        "account":{"connected":False},
        "project":{},
    })
    return
if clean=="/account":
    pass
'''
    changed=patch_csrf_server(source)
    full_response=changed[changed.rfind('_json(self,200,{'):changed.index('if clean=="/account":')]
    assert '"csrf_token":_security_csrf_token(sid)' in full_response
    assert patch_csrf_server(changed)==changed


def test_draft_delete_reports_missing_resource():
    source='''def _draft_delete(sid,draft_id):
    sid=_safe_id(sid); draft_id=_safe_id(draft_id)
    if not sid or not draft_id:
        return False
    root=_draft_dir(sid)
    return True

def _short_index_path(sid):
    pass
'''
    changed=patch_draft_delete_semantics(source)
    assert 'if not _draft_load(sid,draft_id):' in changed
    assert patch_draft_delete_semantics(changed)==changed


def test_project_state_survives_durable_save_restore(tmp_path,monkeypatch):
    from web import project_state_v157 as persistence
    monkeypatch.setattr(persistence,'_s3',lambda:None)
    session={'gsf_active_project_id':'one','gsf_source_path':'/one.mp4'}
    sync_project(session)
    persistence.save_project(session,tmp_path/'sessions'/'browser')
    restored={}
    persistence.restore_project(restored,tmp_path/'sessions'/'browser')
    assert restored[PROJECT_SESSION_KEY]['source_ref']=='/one.mp4'

