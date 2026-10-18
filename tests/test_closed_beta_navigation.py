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

    def test_real_home_editor_cta_prepares_backend_as_well_as_navigation(self):
        self.page.set_viewport_size({'width':390,'height':844})
        self.page.goto('http://gsf.test/')
        self.page.set_content((ROOT/'web/home_v154_component/index.html').read_text())
        self.page.evaluate("window.backendEvents=[];window.addEventListener('message',e=>{if(e.data?.type==='streamlit:setComponentValue')backendEvents.push(e.data.value)})")
        self.page.evaluate("window.postMessage({type:'streamlit:render',args:{loaded:true,duration:15}},location.origin)")
        self.page.locator('.feature[data-action="editor"]').click()
        self.page.wait_for_function("backendEvents.some(e=>e.event==='open_editor'&&e.engine==='manual')",timeout=1500)

    def test_create_short_waits_for_the_prepared_render_button(self):
        self.load()
        self.page.route('**/share/state',lambda r:r.fulfill(content_type='application/json',body='{"ok":true,"ready":false}'))
        self.page.evaluate("GSFNavigation.navigate({target:'short'});window.renderClicks=0;window.notices=[]")
        app=(ROOT/'app.py').read_text()
        start=app.index('      const startShortIfNeeded=async requestedAt=>{')
        end=app.index("      P.GSFNavigation.registerSurface('social'",start)
        function=app[start:end]
        self.page.evaluate("const P=window,bridge={signal:{aborted:false}};let lastShortRequest=0;const notice=t=>window.notices.push(t);"+function+"window.startShortIfNeeded=startShortIfNeeded")
        self.page.evaluate("setTimeout(()=>{const box=document.createElement('div');box.className='st-key-gsf-major-create-short';const button=document.createElement('button');button.textContent='CREA SHORT FINALE';button.onclick=()=>window.renderClicks++;box.append(button);document.body.append(box)},100)")
        self.page.evaluate('startShortIfNeeded(Date.now())')
        self.page.wait_for_function('renderClicks===1',timeout=1200)

    def test_internal_ai_state_message_does_not_navigate_away(self):
        self.load()
        self.page.evaluate("GSFNavigation.navigate({target:'editor'});window.postMessage({type:'GSF_SHELL_NAV',target:'ai-state',loaded:true},location.origin)")
        self.page.wait_for_timeout(100)
        self.assertEqual(self.page.evaluate('GSFNavigation.snapshot().target'),'editor')
        self.assertFalse(self.page.evaluate("GSFNavigation.navigate({target:'unknown-command'})"))

    def test_receiving_home_state_does_not_click_backend_widgets(self):
        self.page.goto('http://gsf.test/')
        source=(ROOT/'web/home_v154_component/index.html').read_text()
        self.page.route('**/home-component',lambda r:r.fulfill(content_type='text/html',body=source))
        self.page.evaluate("document.body.innerHTML='<button id=duration>15s</button><button id=engine>Manuale</button><iframe src=/home-component></iframe>';window.widgetClicks=0;document.querySelectorAll('button').forEach(b=>b.onclick=()=>widgetClicks++)")
        self.page.wait_for_function("document.querySelector('iframe').contentWindow.__GSF_V333_CTA_TOUCH===true")
        self.page.evaluate("document.querySelector('iframe').contentWindow.postMessage({type:'streamlit:render',args:{loaded:true,duration:15,engine:'manual'}},location.origin)")
        self.page.wait_for_timeout(100)
        self.assertEqual(self.page.evaluate('widgetClicks'),0,'receiving state must not trigger another backend rerun')

    def test_profile_link_and_unknown_route_are_normalized(self):
        self.load('/?gsf_page=hub&gsf_section=profile')
        self.assertEqual(self.page.evaluate('GSFNavigation.snapshot().section'),'profile')
        self.load('/?gsf_page=not-a-page')
        self.assertEqual(self.page.evaluate('GSFNavigation.snapshot().target'),'home')


if __name__ == '__main__':
    unittest.main()
