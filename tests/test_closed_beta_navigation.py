"""History and deep links exercise the actual top-owned navigation runtime."""
import os
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class ClosedBetaNavigation(unittest.TestCase):
    def setUp(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.skipTest('Playwright required for browser history checks')
        self.p=sync_playwright().start()
        self.addCleanup(self.p.stop)
        engine=os.environ.get('GSF_BROWSER','chromium')
        options={'executable_path':os.environ.get('GSF_CHROMIUM','/usr/bin/chromium'),'args':['--no-sandbox']} if engine=='chromium' else {}
        self.browser=getattr(self.p,engine).launch(**options)
        self.addCleanup(self.browser.close)
        self.page=self.browser.new_page()
        self.page.route('**/*',lambda route:route.fulfill(content_type='text/html',body='<!doctype html><html><body></body></html>'))

    def load(self, path='/'):
        self.page.goto('http://gsf.test'+path)
        self.page.evaluate((ROOT/'web/gsf_navigation_lifecycle.js').read_text())

    def test_direct_editor_link_survives_refresh(self):
        self.load('/?gsf_page=editor')
        self.assertEqual(self.page.evaluate('GSFNavigation.snapshot().target'),'editor')
        self.page.reload()
        self.page.evaluate((ROOT/'web/gsf_navigation_lifecycle.js').read_text())
        self.assertEqual(self.page.evaluate('GSFNavigation.snapshot().target'),'editor')

    def test_native_back_returns_to_previous_app_surface(self):
        self.load()
        self.page.evaluate("GSFNavigation.navigate({target:'hub'})")
        self.page.evaluate("GSFNavigation.navigate({target:'editor'})")
        self.page.go_back()
        self.page.wait_for_function("GSFNavigation.snapshot().target==='hub'")
        self.page.go_forward()
        self.page.wait_for_function("GSFNavigation.snapshot().target==='editor'")

    def test_forward_to_create_short_preserves_render_action(self):
        self.load()
        self.page.evaluate("GSFNavigation.navigate({target:'short'})")
        self.page.evaluate("GSFNavigation.navigate({target:'home'})")
        self.page.go_back()
        self.page.wait_for_function("GSFNavigation.snapshot().target==='social'")
        self.assertTrue(self.page.evaluate('GSFNavigation.snapshot().createShort'))

    def test_profile_link_and_unknown_route_are_normalized(self):
        self.load('/?gsf_page=hub&gsf_section=profile')
        self.assertEqual(self.page.evaluate('GSFNavigation.snapshot().section'),'profile')
        self.load('/?gsf_page=not-a-page')
        self.assertEqual(self.page.evaluate('GSFNavigation.snapshot().target'),'home')


if __name__ == '__main__':
    unittest.main()
