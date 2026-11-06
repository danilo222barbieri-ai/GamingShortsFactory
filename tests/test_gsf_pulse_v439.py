"""GSF Pulse V439: one quiet, accessible notifications surface on mobile and desktop."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_gsf_notify_is_the_one_visible_pulse_surface():
    client = _read("web/direct_upload_server.py")
    assert "GSF_PULSE_V439" in client
    assert 'font-family:"Nunito Sans"' in client
    assert "'Caveat'" not in client
    assert "max(10px,env(safe-area-inset-top,0px))" in client
    assert "const top=Math.max(10," in client
    assert 'gsf-site-toast-stack' in client
    assert "length<1" in client, "Only one toast may occupy the screen"
    assert "kind==='error'?8500" in client
    assert 'if(event===\'upload.completed\'||event===\'ai.found\'' in client
    assert "if(!status.ready)upsert('alive:upload'" in client


def test_alive_breathes_but_never_creates_a_second_handwritten_popup():
    runtime = _read("web/gsf_alive_v418.js")
    assert '#gsf-alive-whisper{display:none!important' in runtime
    assert 'whisperEl.classList.add("on")' not in runtime
    assert 'if (liveEl) liveEl.textContent = text;' in runtime
    assert 'notify.alive(state)' in runtime
    assert '"Caveat"' not in runtime
    for page in (
        "web/home_v154_component/index.html",
        "web/ai_v221_component/index.html",
        "web/share_v156_component/index.html",
        "web/creator_hub_v156_component/index.html",
    ):
        html = _read(page)
        assert html.count("/* GSF_ALIVE:BEGIN */") == 1
        assert '#gsf-alive-whisper{display:none!important' in html


def test_web_has_no_legacy_streamlit_duplicate_success_toasts():
    app = _read("app.py")
    assert 'if not GSF_WEB_MODE: st.toast(' in app
    assert 'if st.session_state.pop("gsf_v107_draft_resumed",False) and not GSF_WEB_MODE:' in app
    assert 'if st.session_state.pop("gsf_v107_render_done_toast",False) and not GSF_WEB_MODE:' in app
    assert 'showToast("Short completato"' in _read("web/direct_upload_server.py")
