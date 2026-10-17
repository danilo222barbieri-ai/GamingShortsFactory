"""Exercise the real parent shell CSS/runtime without starting video/AI services.

Run directly with Python or pytest; requires Playwright + Chromium (GSF_CHROMIUM_EXECUTABLE may
select the system browser). Reintroducing V394's footer restoration must fail
on the actual computed display, not merely on a source-string assertion.
"""
import ast
import os
import re
import shutil
from pathlib import Path

import unittest

ROOT = Path(__file__).resolve().parents[1]


def _fixture():
    tree = ast.parse((ROOT / 'app.py').read_text())
    constants = {}
    css = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    constants[target.id] = node.value.value
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == 'markdown' and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            css.extend(re.findall(r'<style[^>]*>(.*?)</style>', node.args[0].value, re.S))
    surfaces = ''.join(constants[name] for name in
                       ('_GSF_SURFACE_EDITOR', '_GSF_SURFACE_HUB', '_GSF_SURFACE_SOCIAL'))
    shell = constants['_GSF_PARENT_SHELL']
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', shell, re.S)
    # Include the later footer owners: their inline styles previously revived
    # the white footer only on the Editor route.
    for name in ('_GSF_PARENT_FOOTER348', '_GSF_PARENT_FOOTER351'):
        scripts.extend(re.findall(r'<script[^>]*>(.*?)</script>', constants.get(name, ''), re.S))
    html = '<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">'
    html += '<style>' + '\n'.join(css) + '</style></head><body>'
    html += '<div class="stApp"><div data-testid="stAppViewContainer"></div></div>' + surfaces
    html += '</body></html>'
    return html, [(ROOT / 'web/gsf_navigation_lifecycle.js').read_text(), *scripts]


def check_editor_uses_shared_header_and_dark_canvas_to_bottom(size):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise unittest.SkipTest('Install Playwright to run shell geometry checks')

    html, scripts = _fixture()
    with sync_playwright() as p:
        engine = getattr(p, os.environ.get('GSF_BROWSER', 'chromium'))
        executable = os.environ.get('GSF_CHROMIUM_EXECUTABLE') or shutil.which('chromium')
        options = {'executable_path': executable, 'args': ['--no-sandbox']} if engine.name == 'chromium' and executable else {}
        if not executable and not Path(engine.executable_path).exists():
            raise unittest.SkipTest('Install Playwright browser to run shell geometry checks')
        browser = engine.launch(**options)
        page = browser.new_page(viewport=dict(zip(('width', 'height'), size)),
                                is_mobile=size[0] < 760, has_touch=size[0] < 760)
        page.route('**/*', lambda route: route.fulfill(content_type='text/html', body=html)
                   if route.request.url == 'http://gsf.test/' else route.fulfill(
                       content_type='application/json', body='{"account":{"display_name":"Creator"}}'))
        page.goto('http://gsf.test/')
        for script in scripts:
            page.evaluate(script)
        page.evaluate('window.sharedHeader=document.getElementById("gsf-global-header"); window.sharedBar=document.getElementById("gsf-global-gamebar")')
        header = page.locator('#gsf-global-header').evaluate('(e)=>({html:e.innerHTML, height:e.offsetHeight, background:getComputedStyle(e).background, padding:getComputedStyle(e).padding, filter:getComputedStyle(e).backdropFilter})')
        for route in ('hub', 'editor', 'home', 'editor'):
            page.evaluate('(target)=>GSFNavigation.navigate({target})', route)
            assert page.locator('#gsf-global-header').evaluate('(e)=>e===window.sharedHeader')
            assert page.locator('#gsf-global-gamebar').evaluate('(e)=>e===window.sharedBar')
            assert page.locator('#gsf-global-header').evaluate('(e)=>({html:e.innerHTML, height:e.offsetHeight, background:getComputedStyle(e).background, padding:getComputedStyle(e).padding, filter:getComputedStyle(e).backdropFilter})') == header
            assert page.locator('#gsf-global-footer').evaluate('(e)=>getComputedStyle(e).display') == 'none'
            # A nonzero safe area is injected through the shell's actual token;
            # desktop emulation reports env(safe-area-inset-bottom) as zero.
            for safe in (8, 34):
                page.evaluate('(v)=>document.documentElement.style.setProperty("--gsf-shell-safe-bottom",v+"px")', safe)
                bar = page.locator('#gsf-global-gamebar').bounding_box()
                assert abs(size[1] - bar['y'] - bar['height'] - safe - 10) < 1
                for scroll in (0, 1000, -1000):
                    page.evaluate('(y)=>window.scrollTo(0,y)', scroll)
                    assert page.evaluate('getComputedStyle(document.documentElement).backgroundColor') == 'rgb(5, 13, 22)'
                    assert page.evaluate('getComputedStyle(document.body).backgroundColor') == 'rgb(5, 13, 22)'
                    assert page.evaluate('''() => {
                      const e=document.elementFromPoint(innerWidth/2,innerHeight-1);
                      return !e.closest('#gsf-global-footer') && getComputedStyle(e).backgroundColor;
                    }''') in ('rgb(5, 13, 22)', 'rgba(0, 0, 0, 0)')
        if os.environ.get('GSF_SHELL_SCREENSHOTS'):
            page.screenshot(path=f'/tmp/gsf-editor-shell-{size[0]}.png')
        assert 'viewport-fit=cover' in page.locator('meta[name="viewport"]').get_attribute('content')
        browser.close()


class EditorShellIntegrationTests(unittest.TestCase):
    def test_iphone_and_desktop(self):
        for size in [(390, 844), (375, 667), (1440, 900)]:
            with self.subTest(size=size):
                check_editor_uses_shared_header_and_dark_canvas_to_bottom(size)


if __name__ == '__main__':
    unittest.main()
