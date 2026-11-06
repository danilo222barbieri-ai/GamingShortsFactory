"""V444 full mandatory flow against a running GSF stack (the Production Gate image).

Requires GSF_BASE_URL (e.g. http://127.0.0.1:18080) and GSF_V444_MEDIA, a folder
with five_min.mp4 (300 s), second60.mp4 (60 s) and short8.mp4 (8 s).
GSF_BROWSER selects the engine (webkit in the Gate) with an iPhone profile.
"""
import json
import os
import time
import unittest
from pathlib import Path

BASE = os.environ.get("GSF_BASE_URL", "").rstrip("/")
MEDIA = Path(os.environ.get("GSF_V444_MEDIA", "/nonexistent"))

try:
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover
    sync_playwright = None

SURFACES = ("gsf-ai-overlay-v221", "gsf-editor-overlay-v220", "gsf-social-overlay-v159", "gsf-creator-hub-live-v160")


READY = bool(sync_playwright and BASE and all((MEDIA / n).is_file() for n in ("five_min.mp4", "second60.mp4", "short8.mp4")))


@unittest.skipUnless(READY or os.environ.get("GSF_V444_REQUIRED"), "requires a running stack and media")
class MandatoryFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # In the Production Gate a missing prerequisite is a failure, never a skip.
        if not READY:
            raise AssertionError("V444 flow prerequisites missing (browser, GSF_BASE_URL or media)")

    def setUp(self):
        self.pw = sync_playwright().start()
        engine = getattr(self.pw, os.environ.get("GSF_BROWSER", "chromium"))
        self.browser = engine.launch()
        self.context = self.browser.new_context(**self.pw.devices["iPhone 13"])
        # Production serves HTTPS, where the Secure session cookie sticks. The gate
        # image is plain http on 127.0.0.1 and WebKit drops Secure cookies there,
        # so each request would get a new session. Seed the same id a real
        # browser keeps (nginx reuses an existing gsf_sid).
        import uuid
        self.context.add_cookies([{"name": "gsf_sid", "value": "v444" + uuid.uuid4().hex,
                                   "url": BASE + "/", "httpOnly": True, "sameSite": "Lax"}])
        self.page = self.context.new_page()
        self.page.on("console", lambda m: print("CONSOLE", m.text[:200]) if "GSF" in m.text else None)
        self.page.goto(BASE + "/", wait_until="domcontentloaded")
        self.home()
        self.page.wait_for_timeout(6000)

    def tearDown(self):
        try:
            self.page.screenshot(path=f"/tmp/gsf-v444-{self._testMethodName}.png")
        except Exception:
            pass
        self.context.close()
        self.browser.close()
        self.pw.stop()

    def frame(self, needle):
        return next((f for f in self.page.frames if needle in f.url), None)

    def home(self):
        return self.wait(lambda: (f := self.frame("home_v154")) and f.query_selector("#pick") and f, 60, "Home")

    def wait(self, fn, seconds, label):
        end = time.time() + seconds
        while time.time() < end:
            try:
                value = fn()
                if value:
                    return value
            except Exception:
                pass
            self.page.wait_for_timeout(400)
        self.fail("timeout: " + label)

    def drafts(self):
        return self.page.evaluate("fetch('/creator-hub/state',{credentials:'same-origin',cache:'no-store'}).then(r=>r.json()).then(j=>(j.drafts||[]).map(d=>d.source_name||d.title))")

    def check(self):
        return self.home().evaluate("({label:document.getElementById('uploadLabel').innerText.trim(),on:document.getElementById('uploadIcon').classList.contains('loadedCheck')})")

    def surfaces(self):
        return self.page.evaluate("ids=>ids.filter(id=>document.getElementById(id)?.classList.contains('is-open'))", list(SURFACES))

    def upload(self, name):
        self.home().set_input_files("#pick", str(MEDIA / name))

    def tap_feature(self, action):
        self.home().locator(f'.feature[data-action="{action}"]').tap()

    def go_home(self):
        self.page.locator('#gsf-global-gamebar button[data-page="home"]').tap()
        self.page.wait_for_timeout(1500)

    def moments(self):
        ai = self.frame("ai-v221")
        return ai.evaluate("document.querySelectorAll('#previews .short:not(.skel)').length") if ai else -1

    def scanning(self):
        ai = self.frame("ai-v221")
        return bool(ai) and ai.evaluate("document.querySelector('[data-view=\"engines\"]').classList.contains('scanning')")

    def test_upload_moments_editor_short_and_replacement(self):
        self.assertEqual(self.drafts(), [], "1 no project")
        self.assertFalse(self.check()["on"], "1 empty uploader")
        self.upload("five_min.mp4")
        self.wait(lambda: self.check()["on"], 120, "3 green check")
        self.page.wait_for_timeout(4000)
        self.assertTrue(self.check()["on"], "3 check survives reruns")
        self.assertEqual(self.surfaces(), [], "≥15s stays on Home until Trova i momenti")
        self.assertEqual(self.drafts(), [], "4 not in Bozze")

        self.tap_feature("ai")
        self.wait(self.scanning, 15, "6 analysis starts on the press")
        self.wait(lambda: self.moments() == 3, 420, "7 three moments without leaving the page")
        ai = self.frame("ai-v221")
        self.assertEqual(ai.evaluate("document.querySelector('.view.is-active').dataset.view"), "moments")
        self.assertEqual(self.drafts(), [], "AI results do not create a draft")

        ai.locator('#previews .short[data-index="1"]').tap()
        self.assertTrue(ai.evaluate("document.querySelector('#previews .short[data-index=\"1\"]').classList.contains('is-selected')"), "8 selection")
        ai.locator("#editMoment").tap()
        self.wait(lambda: "gsf-editor-overlay-v220" in self.surfaces(), 20, "9 Game Editor")
        self.go_home()
        self.tap_feature("short")
        self.wait(lambda: "gsf-social-overlay-v159" in self.surfaces(), 20, "9 Crea Short")

        self.go_home()
        self.assertTrue(self.check()["on"], "10 project still active on Home")
        self.page.reload(wait_until="domcontentloaded")
        self.wait(lambda: self.check()["on"], 60, "10 project active after refresh")

        self.page.wait_for_timeout(4000)
        self.upload("second60.mp4")
        self.wait(lambda: len(self.drafts()) == 1, 120, "12 previous project in Bozze")
        self.wait(lambda: self.check()["on"], 120, "13 new upload confirmed")
        self.tap_feature("ai")
        self.wait(self.scanning, 15, "13 new analysis")
        self.assertEqual(self.moments(), 0, "14 previous moments are gone")
        self.wait(lambda: self.moments() == 3, 420, "14 new moments")

        self.go_home()
        self.page.wait_for_timeout(3000)
        self.upload("short8.mp4")
        self.wait(lambda: "gsf-editor-overlay-v220" in self.surfaces(), 120, "15 <15s opens the Game Editor")
        self.assertNotIn("gsf-ai-overlay-v221", self.surfaces(), "15 no analysis for <15s")
        self.wait(lambda: len(self.drafts()) == 2, 60, "15 second project in Bozze")
        print("V444 drafts", json.dumps(self.drafts()))


if __name__ == "__main__":
    unittest.main()
