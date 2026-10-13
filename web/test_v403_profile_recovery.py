from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from fix_v403_profile_recovery import patch_text
from fix_v403_resume_handoff import patch_hub_text


def test_profile_patch_keeps_last_valid_state_on_transient_failure():
    raw=(ROOT/'creator_hub_v156_component'/'index.html').read_text(encoding='utf-8')
    patched=patch_text(raw)
    assert 'V403_PROFILE_RECOVERY' in patched
    assert 'gsf_creator_hub_last_valid_v403' in patched
    assert 'v403HubHasIdentity(state)' in patched
    assert 'v403HubMarkStale()' in patched
    block=patched.split('async function loadState()',1)[1].split('async function deleteShort',1)[0]
    assert 'if(v403HubHasIdentity(state)){v403HubMarkStale();return}' in block
    assert 'state=cached;render();v403HubMarkStale();return' in block
    assert patch_text(patched)==patched


def test_profile_recovery_and_single_flight_resume_compose():
    raw=(ROOT/'creator_hub_v156_component'/'index.html').read_text(encoding='utf-8')
    patched=patch_hub_text(patch_text(raw))
    assert 'V403_PROFILE_RECOVERY' in patched
    assert 'V403_PROFILE_RESUME' in patched
    assert 'v403StateLoadPromise' in patched
    assert 'visibilitychange' in patched and 'pageshow' in patched
    assert patch_hub_text(patched)==patched


def main():
    tests=[v for k,v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    for test in tests:test()
    print(f'V403 PROFILE RECOVERY: PASS ({len(tests)} tests)')

if __name__=='__main__':main()
