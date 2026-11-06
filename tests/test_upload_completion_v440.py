"""V440: successful uploads must not be erased by stale Home state echoes."""
from pathlib import Path

HOME = Path(__file__).resolve().parents[1] / "web/home_v154_component/index.html"


def _home():
    return HOME.read_text(encoding="utf-8")


def test_false_parent_snapshot_cannot_erase_active_or_completed_upload():
    src = _home()
    receive = src.split("function receive(args){", 1)[1].split('window.addEventListener("message"', 1)[0]
    assert "const committed=currentUploadState===UPLOAD_ST.COMPLETED;" in receive
    assert "const inFlight=uploadBusy||currentUploadState===UPLOAD_ST.RECOVERABLE_ERROR;" in receive
    assert "else if(uploadAcknowledgement)" in receive
    assert "setLoaded(true);" in receive
    assert "setLoaded(false);" in receive
    assert "setLoaded(!!args.loaded)" not in receive


def test_server_save_precedes_completion_and_success_is_not_rolled_back():
    src = _home()
    finalization = src.split("async function executeProjectFinalization(", 1)[1].split("// Tapping circle", 1)[0]
    assert finalization.index('"/direct-upload/projects/save-uploaded-source"') < finalization.index("setUploadState(UPLOAD_ST.COMPLETED)")
    assert "Promise.race([" in finalization
    assert "setTimeout(()=>resolve(null),3000)" in finalization
    assert "GSF_UPLOAD_DIAG] post_commit_handoff_failed" in src
    assert "if(currentUploadState===UPLOAD_ST.COMPLETED)" in src


def test_confirmation_is_short_lived_and_cleared_for_new_upload():
    src = _home()
    assert "Date.now()-stamped<45000" in src
    assert "sessionStorage.setItem(UPLOAD_ACK_KEY,String(Date.now()))" in src
    assert "setUploadAcknowledgement(false);" in src
    assert 'setUploadState(UPLOAD_ST.UPLOADING, {pct: 1});' in src
