from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app_flow_v403 import (
    EDITOR_COMPONENT_ID, ROUTE_CREATE_SHORT, ROUTE_EDITOR, ROUTE_MOMENTS,
    ROUTE_MOTORI, analysis_request_token, create_short_handoff,
    editor_handoff, new_snapshot, reconcile_snapshot, render_request_token,
    resolve_route, transition,
)
from apply_v403_flow import (
    patch_ai_text as patch_flow_ai_text, patch_app_text, patch_nginx_text,
    patch_server_text, patch_share_text as patch_flow_share_text,
)
from fix_v403_surface_collisions import (
    patch_ai_text as patch_surface_ai_text,
    patch_share_text as patch_surface_share_text,
)


def candidate(i=0, start=10.0, end=40.0, event="KILL"):
    return {"id": f"m{i}", "rank": i + 1, "start_seconds": start,
            "end_seconds": end, "event": event, "confidence": .8,
            "fusion_reason": f"{event} · High Action",
            "preview_ref": f"/media/sid/media/candidate_{i+1}.mp4"}


def base():
    return transition(new_snapshot(project_id="p_v403", source_video_ref="gsf://source/p.mp4"),
                      "source_ready", {"source_video_ref": "gsf://source/p.mp4"})


def runtime_ai():
    raw=(ROOT/"ai_v221_component"/"index.html").read_text(encoding="utf-8")
    return patch_surface_ai_text(patch_flow_ai_text(raw))


def runtime_share():
    raw=(ROOT/"share_v156_component"/"index.html").read_text(encoding="utf-8")
    return patch_surface_share_text(patch_flow_share_text(raw))


def test_project_source_survive_navigation():
    s=base(); pid=s["project_id"]; src=s["source_video_ref"]
    for route in (ROUTE_MOTORI,"home","hub",ROUTE_MOTORI):
        s=transition(s,"route",{"route":route})
        assert s["project_id"]==pid and s["source_video_ref"]==src


def test_analysis_job_is_idempotent_on_resume():
    s=transition(base(),"analysis_started",{"job_id":"a1","engine":"auto","duration":30})
    token=analysis_request_token(s)
    s=transition(s,"analysis_started",{"job_id":"a1","engine":"auto","duration":30})
    s=reconcile_snapshot(copy.deepcopy(s),copy.deepcopy(s))
    assert analysis_request_token(s)==token and s["analysis"]["issue_count"]==1


def test_render_job_is_idempotent_on_resume():
    s=transition(base(),"analysis_completed",{"job_id":"a1","candidates":[candidate()]})
    s=transition(s,"candidate_selected",{"index":0}); s=transition(s,"render_started",{"job_id":"r1"})
    token=render_request_token(s); s=transition(s,"render_started",{"job_id":"r1"})
    s=reconcile_snapshot(copy.deepcopy(s),copy.deepcopy(s))
    assert render_request_token(s)==token and s["render"]["issue_count"]==1


def test_profile_retains_last_valid_on_refresh_failure():
    valid={"name":"Creator","avatar":"avatar://1","plan":"Pro","version":7}
    s=transition(base(),"profile_valid",valid); s=transition(s,"profile_refreshing",{})
    assert s["profile"]["data"]==valid
    s=transition(s,"profile_refresh_failed",{"error":"temporary"})
    assert s["profile"]["data"]==valid and s["profile"]["status"]=="stale"


def test_analysis_routes_to_moments_and_selection_survives_resume():
    rows=[candidate(0,10,40),candidate(1,50,80,"CLUTCH"),candidate(2,90,120,"VICTORY")]
    s=transition(base(),"analysis_completed",{"job_id":"a1","candidates":rows})
    assert s["route"]==ROUTE_MOMENTS and len(s["candidates"])==3
    s=transition(s,"candidate_selected",{"index":1}); selected=s["selected_candidate_id"]
    moved=transition(s,"route",{"route":"hub"}); restored=reconcile_snapshot(moved,s)
    assert moved["selected_candidate_id"]==selected
    assert restored["selected_candidate_id"]==selected and restored["selected_candidate_index"]==1


def test_invalid_create_short_resolves_safely():
    s=base(); assert resolve_route(s,ROUTE_CREATE_SHORT)==ROUTE_MOTORI
    s=transition(s,"analysis_completed",{"job_id":"a1","candidates":[candidate()]})
    assert resolve_route(s,ROUTE_CREATE_SHORT)==ROUTE_MOMENTS


def test_editor_and_short_handoff_use_selected_candidate():
    s=transition(base(),"analysis_completed",{"job_id":"a1","candidates":[candidate(),candidate(1,51.5,81.5,"CLUTCH")]})
    s=transition(s,"candidate_selected",{"index":1}); e=editor_handoff(s); c=create_short_handoff(s)
    assert e["component_id"]=="gsf_editor_2027_v1086" and e["candidate_id"]=="m1"
    assert e["start_seconds"]==51.5 and e["end_seconds"]==81.5
    assert c["candidate_id"]=="m1" and c["source_video_ref"]==s["source_video_ref"]


def test_final_render_stays_on_create_short_and_is_ready():
    s=transition(base(),"analysis_completed",{"job_id":"a1","candidates":[candidate()]})
    s=transition(s,"candidate_selected",{"index":0}); s=transition(s,"route",{"route":ROUTE_CREATE_SHORT})
    s=transition(s,"render_started",{"job_id":"r1"}); s=transition(s,"render_completed",{"job_id":"r1","asset_ref":"gsf://final/p.mp4"})
    assert s["route"]==ROUTE_CREATE_SHORT and s["render"]["status"]=="ready" and s["final_asset_ref"]


def test_gamebar_routes_are_stateless():
    s=base(); assert resolve_route(s,"hub")=="hub"
    s=transition(s,"route",{"route":ROUTE_EDITOR})
    assert resolve_route(s,"hub")=="hub" and resolve_route(s,"home")=="home"


def test_editor_identity_locked():
    assert EDITOR_COMPONENT_ID=="gsf_editor_2027_v1086"
    assert "gsf_editor_2027_v1086" in (ROOT/"editor_2027_embed.py").read_text(encoding="utf-8")


def test_runtime_patch_chain_is_idempotent():
    raw_ai=(ROOT/"ai_v221_component"/"index.html").read_text(encoding="utf-8")
    raw_share=(ROOT/"share_v156_component"/"index.html").read_text(encoding="utf-8")
    raw_server=(ROOT/"direct_upload_server.py").read_text(encoding="utf-8")
    raw_nginx=(ROOT/"nginx.conf.template").read_text(encoding="utf-8")
    ai=patch_surface_ai_text(patch_flow_ai_text(raw_ai)); share=patch_surface_share_text(patch_flow_share_text(raw_share))
    server=patch_server_text(raw_server); nginx=patch_nginx_text(raw_nginx)
    assert patch_surface_ai_text(ai)==ai and patch_surface_share_text(share)==share
    assert patch_server_text(server)==server and patch_nginx_text(nginx)==nginx
    compile(server,"server_v403.py","exec")


def test_motori_is_config_progress_only_after_final_runtime_patch():
    html=runtime_ai().lower()
    for token in ('id="v403motorionly"','#ai221>.panel:has(.moments)','v403legacymomentsretired','display:none!important','/project/flow','gsf_v403_open_moments','v403_motori_results_retired'):
        assert token in html,token


def test_dedicated_moments_surface_contract():
    html=(ROOT/"moments_v403_component"/"index.html").read_text(encoding="utf-8").lower()
    for token in ("i tuoi 3 momenti","data-candidate-id","crea short","modifica nel game editor","fullscreen","overflow-y:auto","fusion_reason","/project/flow"):
        assert token in html,token


def test_server_nginx_authoritative_flow_contract():
    server=patch_server_text((ROOT/"direct_upload_server.py").read_text(encoding="utf-8"))
    nginx=patch_nginx_text((ROOT/"nginx.conf.template").read_text(encoding="utf-8"))
    for token in ('if clean=="/project/flow":','_v403_transition(','_v403_reconcile_snapshot(','project_flow_v403.json','V403_PROJECT_FLOW'):
        assert token in server,token
    for token in ('location = /project/flow','location /moments-v403/','moments_v403_component'):
        assert token in nginx,token
    block=nginx.split('location /moments-v403/',1)[1].split('location = /project/flow',1)[0]
    assert 'gsf_mobile_client' not in block


def test_parent_reconciliation_never_starts_jobs():
    patched=patch_app_text("import streamlit as st\nGSF_WEB_MODE=True\n").lower()
    for token in ("visibilitychange","pageshow","/project/flow","gsf_v403_open_moments","gsf_v403_open_editor","gsf_v403_open_short"):
        assert token in patched,token
    assert "analysis_started" not in patched and "render_started" not in patched


def test_create_short_has_pre_render_ready_and_mobile_v396_override():
    html=runtime_share().lower()
    for token in ("pre-render","setattribute('data-v403-state','pre-render')",'data-v403-state="ready"','crea short','modifica nel game editor','salva bozza','scegli un altro momento','download','/project/flow','v396mobilepublishsurface','v403_share_v396_override'):
        assert token in html,token
    assert '#share.v403prerender.v396mobilemode>#v396mobilepublishsurface' in html
    refresh=html.split('async function refresh()',1)[1].split('function poll()',1)[0]
    assert 'render_started' not in refresh


def test_snapshot_is_metadata_only_and_bounded():
    s=transition(base(),"analysis_completed",{"job_id":"a1","candidates":[candidate()]})
    s=transition(s,"candidate_selected",{"index":0}); raw=json.dumps(s,sort_keys=True)
    assert "bytes" not in raw.lower() and len(raw)<200_000


def main():
    tests=[v for k,v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for test in tests:test()
    print(f"V403 APP STABILITY FLOW: PASS ({len(tests)} tests)")


if __name__=="__main__":main()
