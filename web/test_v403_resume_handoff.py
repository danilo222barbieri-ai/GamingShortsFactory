from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from fix_v403_resume_handoff import patch_hub_text, patch_app_text
from apply_v403_flow import patch_app_text as patch_flow_app


def test_creator_hub_resume_is_single_flight_and_last_valid_safe():
    raw=(ROOT/'creator_hub_v156_component'/'index.html').read_text(encoding='utf-8')
    patched=patch_hub_text(raw)
    assert 'V403_PROFILE_RESUME' in patched
    assert 'v403StateLoadPromise' in patched
    assert 'visibilitychange' in patched
    assert 'pageshow' in patched
    # Existing loadState catch must not replace state/account or blank profile identity.
    catch=patched.split('async function loadState()',1)[1].split('async function deleteShort',1)[0]
    assert 'state={account:' not in catch
    assert '#profileName' not in catch
    assert patch_hub_text(patched)==patched


def test_editor_handoff_comes_from_authoritative_selected_candidate():
    fixture='''import streamlit as st\nGSF_WEB_MODE=True\n'''
    flow_patched=patch_flow_app(fixture)
    patched=patch_app_text(flow_patched)
    assert 'V403_EDITOR_HANDOFF' in patched
    assert 'selected_candidate_id' in patched
    assert 'start_seconds' in patched
    assert 'end_seconds' in patched
    assert 'candidate_id' in patched
    assert 'gsf_editor_2027_v1086' in patched
    assert patch_app_text(patched)==patched


def main():
    tests=[v for k,v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    for test in tests:test()
    print(f'V403 RESUME HANDOFF: PASS ({len(tests)} tests)')

if __name__=='__main__':main()
