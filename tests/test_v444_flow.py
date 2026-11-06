"""V444 mandatory sequence: units, contracts and the AI page in a real browser."""
import json
import os
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from web import ai_engines_v412 as v412  # noqa: E402

URL = lambda name: "/media/" + name


def meta(**extra):
    return {"request_id": "rq1", "updated_at": time.time(), **extra}


ITEMS = [{"index": i, "start_time": float(10 * i), "end_time": float(10 * i + 15)} for i in range(3)]
FILES = [(i + 1, float(10 * i), time.time(), f"v71_mini_{i + 1}_{10 * i:.2f}.mp4") for i in range(3)]


class ResultsState(unittest.TestCase):
    def test_running_analysis_has_no_verdict(self):
        out = v412.merge_results(meta(status="analyzing", items=[]), [], URL)
        self.assertEqual((out["status"], out["result_state"]), ("analyzing", "analyzing"))

    def test_moments_waiting_for_their_previews_are_not_no_highlights(self):
        out = v412.merge_results(meta(items=ITEMS), FILES[:1], URL)
        self.assertEqual(out["result_state"], "rendering_previews")

    def test_complete_results(self):
        out = v412.merge_results(meta(items=ITEMS), FILES, URL)
        self.assertEqual((out["result_state"], out["count"]), ("completed_with_results", 3))

    def test_finished_without_moments(self):
        out = v412.merge_results(meta(items=[]), [], URL)
        self.assertEqual(out["result_state"], "completed_no_highlights")

    def test_long_analysis_is_not_failed_at_two_minutes(self):
        out = v412.merge_results(meta(status="analyzing", items=[], updated_at=time.time() - 180), [], URL)
        self.assertEqual(out["status"], "analyzing")
        out = v412.merge_results(meta(status="analyzing", items=[], updated_at=time.time() - 500), [], URL)
        self.assertEqual(out["status"], "failed")


class SequenceContracts(unittest.TestCase):
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    home = (ROOT / "web/home_v154_component/index.html").read_text(encoding="utf-8")

    def test_ai_results_never_create_a_draft(self):
        self.assertNotIn('"draft_ai_"+', self.app)
        self.assertIn("GSF_V444_ACTIVE_PROJECT", self.app)

    def test_home_position_is_stable_across_reruns(self):
        source = (ROOT / "web/queue_runtime_v411.py").read_text(encoding="utf-8")
        self.assertIn("with st_module.container():", source)

    def test_upload_check_is_not_reset_after_handoff(self):
        embed = (ROOT / "web/home_v154_embed.py").read_text(encoding="utf-8")
        self.assertNotIn("    _render_v428_uploader_handoff_reset_bridge()\n", embed)
        self.assertIn("GSF_V444_PERSISTENT_ACK", self.home)

    def test_long_video_waits_for_the_press(self):
        block = self.home[self.home.index("if (isUnder15) {"):self.home.index("// Tapping circle in recoverable")]
        self.assertNotIn("auto_search: true", block)
        self.assertIn('shellNav("editor"', block)
        self.assertIn('shellNav("ai",{duration,engine:engine||"auto",auto_search:true})', self.home)
        self.assertIn("window.GSFHomeFeature(action)", self.home)

    def test_ai_results_route_returns(self):
        server = (ROOT / "web/direct_upload_server.py").read_text(encoding="utf-8")
        self.assertIn('_json(self,200,_ai_results_payload(sid))\n            return', server)


try:
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover
    sync_playwright = None

AI_PAGE = (ROOT / "web/ai_v221_component/index.html").read_text(encoding="utf-8")
PARENT = """<!doctype html><html><body><iframe id=ai src="/ai-v221/" style="width:390px;height:844px"></iframe><script>
window.CREATES=[];
addEventListener('message',e=>{const d=e.data||{};if(d.type!=='GSF_AI_UI')return;
 if(d.action==='ready'){document.getElementById('ai').contentWindow.postMessage({type:'GSF_AI_STATE',state:{loaded:true,duration:15,engine:'auto',previews:[]}},'*');}
 if(d.action==='create'){CREATES.push(d.request_id);}
});
</script></body></html>"""


@unittest.skipUnless(sync_playwright, "requires playwright")
class AiPageBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        name = os.environ.get("GSF_BROWSER", "chromium")
        try:
            cls.browser = getattr(cls.pw, name).launch()
        except Exception as exc:
            cls.pw.stop()
            raise unittest.SkipTest(f"{name} unavailable: {exc}")

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def run_search(self, running_payload):
        context = self.browser.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
        self.addCleanup(context.close)
        page = context.new_page()
        polls = {"n": 0}

        def handle(route):
            path = "/" + route.request.url.split("://", 1)[1].split("/", 1)[1].split("?", 1)[0]
            if path == "/":
                return route.fulfill(status=200, content_type="text/html", body=PARENT)
            if path.startswith("/ai-v221"):
                return route.fulfill(status=200, content_type="text/html", body=AI_PAGE)
            if path == "/ai/results":
                creates = page.evaluate("CREATES")
                if not creates:
                    return route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True, "previews": []}))
                polls["n"] += 1
                rid = creates[-1]
                if polls["n"] < 6:
                    body = {**running_payload, "request_id": rid}
                else:
                    body = {"ok": True, "status": "success", "result_state": "completed_with_results", "request_id": rid,
                            "previews": [{"index": i, "start_time": i * 10, "end_time": i * 10 + 15, "video": f"/media/m{i}.mp4", "label": f"M{i}"} for i in range(3)],
                            "count": 3}
                return route.fulfill(status=200, content_type="application/json", body=json.dumps(body))
            return route.fulfill(status=404, body="")

        page.route("**/*", handle)
        page.goto("http://gsf.test/")
        frame = page.frame_locator("#ai")
        page.wait_for_timeout(600)
        orb = frame.locator("#createAi")
        page.wait_for_function("()=>!document.getElementById('ai').contentDocument.getElementById('createAi').disabled", timeout=8000)
        orb.dispatch_event("click")
        page.wait_for_function("CREATES.length===1", timeout=5000)
        frame.locator('#previews .short:not(.skel)').nth(2).wait_for(timeout=20000)
        page.wait_for_timeout(1500)
        return page, frame

    def test_moments_appear_on_the_same_page(self):
        page, frame = self.run_search({"ok": True, "status": "analyzing", "result_state": "analyzing", "previews": []})
        self.assertEqual(frame.locator("#previews .short:not(.skel)").count(), 3)
        self.assertEqual(page.evaluate("CREATES.length"), 1, "one press, one analysis")

    def test_legacy_running_verdict_does_not_stop_polling(self):
        # Before V444 the server labelled a running analysis "completed_no_highlights".
        page, frame = self.run_search({"ok": True, "status": "analyzing", "result_state": "completed_no_highlights", "previews": []})
        self.assertEqual(frame.locator("#previews .short:not(.skel)").count(), 3)

    def test_selected_moment_opens_the_next_steps(self):
        page, frame = self.run_search({"ok": True, "status": "analyzing", "result_state": "analyzing", "previews": []})
        frame.locator('#previews .short[data-index="1"]').dispatch_event("click")
        self.assertTrue(frame.locator('#previews .short[data-index="1"]').evaluate("e=>e.classList.contains('is-selected')"))
        self.assertFalse(frame.locator("#editMoment").is_disabled())
        self.assertFalse(frame.locator("#createShort").is_disabled())


if __name__ == "__main__":
    unittest.main()
