"""Real post-upload state delivery; no request/result mocking."""
import os
import unittest
import time
import uuid
from urllib.parse import urlsplit
from visual.gsf_navigation_stress import MEDIA_FIXTURE


@unittest.skipUnless(os.environ.get('GSF_BASE_URL'), 'requires running GSF_BASE_URL')
class UploadHandoff(unittest.TestCase):
    def check_viewport(self, width, height):
        from playwright.sync_api import sync_playwright, expect
        base = os.environ['GSF_BASE_URL'].rstrip('/')
        with sync_playwright() as p:
            engine = getattr(p, os.environ.get('GSF_BROWSER', 'webkit'))
            options = {'executable_path': os.environ.get('GSF_CHROMIUM', '/usr/bin/chromium'),
                       'args': ['--no-sandbox']} if engine.name == 'chromium' else {}
            if os.environ.get('GSF_BROWSER_PROXY'):
                options['proxy'] = {'server': os.environ['GSF_BROWSER_PROXY']}
            browser = engine.launch(**options)
            try:
                context = browser.new_context(**{**p.devices['iPhone 13'],
                                                 'viewport': {'width': width, 'height': height}})
                if base.startswith('http://'):
                    context.add_cookies([{'name': 'gsf_sid', 'value': 'handoff'+uuid.uuid4().hex[:24], 'url': base+'/'}])
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.on('response', lambda r: errors.append(f'HTTP {r.status} {urlsplit(r.url).path}') if r.status >= 500 else None)
                page.goto(base, wait_until='domcontentloaded', timeout=60000)
                page.wait_for_function("()=>[...document.querySelectorAll('iframe')].some(f=>{try{return f.contentWindow.__GSF_V333_CTA_TOUCH===true}catch(_){return false}})", timeout=60000)
                home = page.frame_locator('iframe[title*="gsf_home_v154"]')
                home.locator('#pick').set_input_files(files=[{'name': 'handoff.mp4', 'mimeType': 'video/mp4', 'buffer': MEDIA_FIXTURE}])
                # The approved uploader returns to idle after success. Its old
                # transient .rings.uploaded class is deliberately not the contract.
                home.locator('#circle[data-gsf-uploader-idle="true"]').wait_for(timeout=60000)
                home.locator('.feature[data-action="ai"]').click()
                ai = page.frame_locator('#gsf-ai-overlay-v221 iframe')
                expect(ai.locator('#createAi')).to_be_enabled(timeout=20000)
                # Readiness alone missed a stale Streamlit window registry: it
                # could paint an enabled CTA while silently dropping create_ai.
                page.evaluate("""()=>window.addEventListener('message',e=>{if(e.origin===location.origin&&e.data?.type==='GSF_AI_UI'&&e.data.action==='create')window.__gsfTestRequest=e.data.request_id})""")
                ai.locator('#createAi').click()
                page.wait_for_function("""()=>{const d=document.querySelector('#gsf-ai-overlay-v221 iframe')?.contentDocument;return !!d&&(d.querySelector('[data-view="moments"]')?.classList.contains('is-active')||d.querySelector('[data-view="engines"]')?.classList.contains('failed'))}""", polling=100, timeout=120000)
                request_id = page.evaluate('()=>window.__gsfTestRequest')
                # A whole-source moment is intentionally usable while the scan
                # continues. Wait for this request's actual backend terminal state.
                deadline = time.monotonic()+120
                while True:
                    result = page.evaluate("()=>fetch('/ai/results',{cache:'no-store',credentials:'same-origin'}).then(r=>r.json())")
                    if result.get('request_id')==request_id and result.get('status') in ('success','failed'):
                        break
                    if time.monotonic()>=deadline:
                        self.fail('Backend did not terminate the current AI request')
                    page.wait_for_timeout(100)
                self.assertTrue(request_id)
                self.assertEqual(result.get('request_id'), request_id)
                self.assertIn(result.get('status'), ('success', 'failed'))
                self.assertFalse(errors, errors)
            finally:
                browser.close()

    def test_375_667(self):
        self.check_viewport(375, 667)

    def test_390_844(self):
        self.check_viewport(390, 844)

    def test_393_852(self):
        self.check_viewport(393, 852)

    def test_430_932(self):
        self.check_viewport(430, 932)


def test_mobile_webkit_remains_a_blocking_release_gate():
    from pathlib import Path
    import re
    root = Path(__file__).resolve().parents[1]
    workflow = (root / '.github/workflows/v397-production-gate.yml').read_text()
    block = re.search(r"      - name: (?:Extended Mobile WebKit diagnostics|Mobile WebKit interaction gate)\n([\s\S]*?)(?=      - name:)", workflow)
    assert block, 'Mobile WebKit coverage must remain in Production Gate'
    assert 'continue-on-error' not in block.group(1), 'Mobile regressions must prevent promotion'
    assert 'python tests/visual/gsf_visual_check.py' in block.group(1)
