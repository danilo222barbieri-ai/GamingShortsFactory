"""V443 Home behaviour in a real browser (GSF_BROWSER=webkit in the Production Gate)."""
import json
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = (ROOT / "web/home_v154_component/index.html").read_text(encoding="utf-8")
PARENT = """<!doctype html><html><body><iframe id=home src="/home" style="width:390px;height:844px"></iframe><script>
window.READY=0;window.TOASTS=[];window.GSFNotify={show:(t,b,k)=>TOASTS.push([t,b,k])};window.RESPOND=null;
addEventListener('message',e=>{if(e.data&&e.data.type==='streamlit:componentReady'){READY++;
 if(RESPOND!==null&&READY>=RESPOND)document.getElementById('home').contentWindow.postMessage({type:'streamlit:render',args:window.ARGS||{}},'*')}});
</script></body></html>"""

try:
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover
    sync_playwright = None


@unittest.skipUnless(sync_playwright, "requires playwright")
class HomeBrowser(unittest.TestCase):
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

    def open(self, respond_at=1, args=None, routes=None):
        context = self.browser.new_context(viewport={"width": 390, "height": 844})
        self.addCleanup(context.close)
        page = context.new_page()
        self.calls = []
        routes = routes or {}

        def handle(route):
            url = route.request.url
            path = url.split("://", 1)[1].split("/", 1)[1].split("?", 1)[0]
            path = "/" + path
            if path == "/":
                return route.fulfill(status=200, content_type="text/html", body=PARENT)
            if path == "/home":
                return route.fulfill(status=200, content_type="text/html", body=HOME)
            self.calls.append((path, route.request.post_data))
            status, body = routes.get(path, (404, {}))
            return route.fulfill(status=status, content_type="application/json", body=json.dumps(body))

        page.route("**/*", handle)
        page.add_init_script(f"window.RESPOND={json.dumps(respond_at)};window.ARGS={json.dumps(args or {})};")
        page.goto("http://gsf.test/")
        page.evaluate(f"window.RESPOND={json.dumps(respond_at)};window.ARGS={json.dumps(args or {})};")
        return page, page.frame_locator("#home")

    def test_ready_handshake_repeats_until_render_then_stops(self):
        page, _ = self.open(respond_at=3)
        page.wait_for_function("READY>=3", timeout=8000)
        page.wait_for_timeout(1500)
        settled = page.evaluate("READY")
        page.wait_for_timeout(1500)
        self.assertEqual(page.evaluate("READY"), settled)

    def pick(self, frame):
        frame.locator("#pick").set_input_files({"name": "due.mp4", "mimeType": "video/mp4", "buffer": b"x"})

    def test_failed_draft_gives_one_readable_notification(self):
        routes = {"/creator-hub/state": (200, {"csrf_token": "t"}),
                  "/drafts/save-current": (503, {"ok": False, "verified": False, "error": "No module named 'web.mobile_editor_recipe'"})}
        page, frame = self.open(args={"loaded": True}, routes=routes)
        page.wait_for_timeout(300)
        self.pick(frame)
        page.wait_for_function("TOASTS.length>0", timeout=5000)
        page.wait_for_timeout(300)
        toasts = page.evaluate("TOASTS")
        self.assertEqual(len(toasts), 1, toasts)
        self.assertNotIn("module", " ".join(toasts[0]).lower())
        self.assertEqual(frame.locator("#statusText").inner_text(), "")
        self.assertNotIn("Video caricato", frame.locator("#uploadLabel").inner_text())
        self.assertFalse(any(path.startswith("/direct-upload/") or path == "/workflow/prepare-new-upload" for path, _ in self.calls))

    def test_replacement_is_decided_by_the_server_not_by_loaded(self):
        routes = {"/creator-hub/state": (200, {"csrf_token": "t"}),
                  "/drafts/save-current": (409, {"ok": False, "verified": False, "error": "Bozza non verificata."})}
        page, frame = self.open(args={"loaded": False}, routes=routes)
        page.wait_for_timeout(300)
        self.pick(frame)
        page.wait_for_function("TOASTS.length>0", timeout=5000)
        body = next(data for path, data in self.calls if path == "/drafts/save-current")
        self.assertEqual(json.loads(body), {"for_replacement": True})
        self.assertFalse(any(path.startswith("/direct-upload/") for path, _ in self.calls))


if __name__ == "__main__":
    unittest.main()
