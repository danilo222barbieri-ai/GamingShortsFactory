"""V416 event-driven web push: one notification per real event, right page on tap."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))

import gsf_push_v416 as push  # noqa: E402

NOW = 1_800_000_000.0


def _session(root: Path, sid: str = "s1", subscribed: bool = True) -> Path:
    d = root / sid
    (d / "media").mkdir(parents=True, exist_ok=True)
    if subscribed:
        (d / push.SUBSCRIPTION_FILE).write_text('{"endpoint":"https://x","keys":{}}', encoding="utf-8")
    return d


def _write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def _watcher(root: Path):
    sent: list[tuple[str, push.PushEvent]] = []
    w = push.PushWatcher(root, lambda sid, ev: sent.append((sid, ev)) or True, log=lambda *a: None)
    return w, sent


def test_short_ready_notifies_once_and_opens_crea_short():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = _session(root)
        _write(d / push.RENDER_JOB_FILE, {"status": "ready", "completed_at": NOW - 5})
        w, sent = _watcher(root)
        assert w.scan_once(NOW) == 1
        assert w.scan_once(NOW + 4) == 0  # every later scan sees the same file
        sid, ev = sent[0]
        assert sid == "s1" and ev.kind == "short_ready" and ev.title == "Short pronto"
        assert ev.url == "/#gsf-open=short"


def test_legacy_ready_call_and_watcher_share_the_ledger():
    """app.py's /push/notify and the watcher must not produce two pushes."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = _session(root)
        _write(d / push.RENDER_JOB_FILE, {"status": "ready", "completed_at": NOW - 1})
        w, sent = _watcher(root)
        assert push.is_short_ready_tag("gsf-short-ready")
        assert push.is_short_ready_tag("gsf-short-ready-abc123")
        assert not push.is_short_ready_tag("gsf-short-published-x")
        w.scan_session(d, NOW)      # what the /push/notify hook does
        w.scan_once(NOW + 2)        # the background loop right after
        assert len(sent) == 1


def test_restored_old_result_does_not_notify():
    """A bucket restore after a redeploy rewrites render_job.json with the old time."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = _session(root)
        _write(d / push.RENDER_JOB_FILE, {"status": "ready", "completed_at": NOW - 3 * 3600})
        w, sent = _watcher(root)
        assert w.scan_once(NOW) == 0 and sent == []


def test_new_render_after_a_previous_one_notifies_again():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = _session(root)
        w, sent = _watcher(root)
        _write(d / push.RENDER_JOB_FILE, {"status": "ready", "completed_at": NOW - 10})
        w.scan_once(NOW)
        _write(d / push.RENDER_JOB_FILE, {"status": "running", "started_at": NOW + 20})
        w.scan_once(NOW + 30)
        _write(d / push.RENDER_JOB_FILE, {"status": "ready", "completed_at": NOW + 200})
        w.scan_once(NOW + 205)
        assert [e.kind for _, e in sent] == ["short_ready", "short_ready"]


def test_render_failure_notifies_cancel_does_not():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = _session(root)
        w, sent = _watcher(root)
        _write(d / push.RENDER_JOB_FILE, {"status": "cancelled", "started_at": NOW - 5})
        w.scan_once(NOW)
        assert sent == []
        _write(d / push.RENDER_JOB_FILE, {"status": "failed", "failed_at": NOW - 2})
        w.scan_once(NOW)
        assert [e.kind for _, e in sent] == ["render_failed"]
        assert sent[0][1].url == "/#gsf-open=home"


def test_ai_results_one_push_per_search_not_per_swap():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = _session(root)
        w, sent = _watcher(root)
        meta = d / "media" / push.AI_RESULTS_FILE
        items = [{"start": 1}, {"start": 9}, {"start": 30}]
        _write(meta, {"request_id": "req-1", "updated_at": NOW - 3, "items": items})
        w.scan_once(NOW)
        _write(meta, {"request_id": "req-1", "updated_at": NOW + 40, "items": items[::-1]})  # "Cambia short"
        w.scan_once(NOW + 45)
        _write(meta, {"request_id": "req-2", "updated_at": NOW + 400, "items": items})        # new search
        w.scan_once(NOW + 405)
        kinds = [e for _, e in sent]
        assert [e.kind for e in kinds] == ["ai_ready", "ai_ready"]
        assert kinds[0].url == "/#gsf-open=ai" and "3 momenti" in kinds[0].body


def test_ai_results_without_items_are_quiet():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = _session(root)
        _write(d / "media" / push.AI_RESULTS_FILE, {"request_id": "r", "updated_at": NOW, "items": []})
        w, sent = _watcher(root)
        assert w.scan_once(NOW) == 0


def test_publish_finished_success_partial_and_failure():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = _session(root)
        w, sent = _watcher(root)
        job = d / push.PUBLISH_FILE
        _write(job, {"id": "p1", "state": "running", "updated_at": NOW,
                     "results": {"youtube": {"label": "YouTube", "status": "running"}}})
        w.scan_once(NOW)
        assert sent == []
        _write(job, {"id": "p1", "state": "finished", "updated_at": NOW + 30,
                     "results": {"youtube": {"label": "YouTube", "status": "done"},
                                 "tiktok": {"label": "TikTok", "status": "error"}}})
        w.scan_once(NOW + 31)
        ev = sent[-1][1]
        assert ev.kind == "published" and "YouTube" in ev.body and "TikTok" in ev.body
        assert ev.url == "/#gsf-open=short"
        _write(job, {"id": "p2", "state": "finished", "updated_at": NOW + 90,
                     "results": {"youtube": {"label": "YouTube", "status": "error"}}})
        w.scan_once(NOW + 91)
        assert sent[-1][1].kind == "publish_failed"
        _write(job, {"id": "p3", "state": "finished", "updated_at": NOW + 150,
                     "results": {"instagram": {"label": "Instagram", "status": "manual"}}})
        w.scan_once(NOW + 151)
        assert len(sent) == 2  # manual-only: the page already guides the user


def test_sessions_without_subscription_are_ignored():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = _session(root, subscribed=False)
        _write(d / push.RENDER_JOB_FILE, {"status": "ready", "completed_at": NOW})
        w, sent = _watcher(root)
        assert w.scan_once(NOW) == 0 and not (d / push.LEDGER_FILE).exists()


def test_failing_sender_does_not_retry_into_a_second_push():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = _session(root)
        _write(d / push.RENDER_JOB_FILE, {"status": "ready", "completed_at": NOW})
        calls = []

        def boom(sid, ev):
            calls.append(ev)
            raise RuntimeError("push service down")

        w = push.PushWatcher(root, boom, log=lambda *a: None)
        w.scan_once(NOW)
        w.scan_once(NOW + 5)
        assert len(calls) == 1


def test_corrupt_files_never_break_the_scan():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = _session(root)
        (d / push.RENDER_JOB_FILE).write_text("{not json", encoding="utf-8")
        (d / push.PUBLISH_FILE).write_text("[]", encoding="utf-8")
        (d / "media" / push.AI_RESULTS_FILE).write_text('{"items":"x"}', encoding="utf-8")
        (d / push.LEDGER_FILE).write_text("garbage", encoding="utf-8")
        w, sent = _watcher(root)
        assert w.scan_once(NOW) == 0


def test_ledger_stays_small():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        ledger = push.Ledger(d)
        for i in range(push.LEDGER_MAX_ENTRIES + 50):
            ledger.mark("k%d" % i, NOW + i)
        assert len(ledger.load()) == push.LEDGER_MAX_ENTRIES
        ledger.mark("fresh", NOW + push.LEDGER_TTL_SECONDS + 10_000)
        assert ledger.load() == {"fresh": NOW + push.LEDGER_TTL_SECONDS + 10_000}


def test_browser_scripts_parse_and_keep_contracts():
    client = push.client_js().decode("utf-8")
    worker = push.service_worker_js().decode("utf-8")
    # Font names inside the double-quoted CSS string must not use double quotes (PR #153).
    assert 'font-family:"Avenir' not in client
    # Public API used by Home, Creator Hub and the shell.
    for token in ("window.GSFNotify", "window.GSFPush", "confirm:confirmToast", "ensure:subscribe",
                  "Upload completato", "__GSF_GLOBAL_NOTIFICATIONS_V2__", "gsf_final_ready_sync_v111"):
        assert token in client, token
    # Taps open the right page through the shell, not a dead legacy button.
    assert "GSF_SHELL_NAV" in client and "GSF_PUSH_OPEN" in client and "gsf-open=" in client
    assert "CONDIVIDI O SCARICA" not in client
    # requestPermission runs before any await inside enable() (Safari on iPhone).
    enable = client[client.index("const enable=()=>{"):client.index("const openTarget")]
    assert enable.index("Notification.requestPermission()") < enable.index(".then(")
    assert "await" not in enable
    assert "GSF_PUSH_OPEN" in worker and "openWindow" in worker and "showNotification" in worker
    node = shutil.which("node")
    if node:
        with tempfile.TemporaryDirectory() as tmp:
            for name, src in (("client.js", client), ("sw.js", worker)):
                f = Path(tmp) / name
                f.write_text(src, encoding="utf-8")
                r = subprocess.run([node, "--check", str(f)], capture_output=True, text=True)
                assert r.returncode == 0, name + ": " + r.stderr[-400:]
