"""The public save-current action must reach its actual companion handler."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ClosedBetaRoutes(unittest.TestCase):
    def test_save_current_has_a_companion_route(self):
        nginx=(ROOT/'web/nginx.conf.template').read_text()
        match=re.search(r'location = /drafts/save-current\s*\{(.*?)(?=\n    location|\Z)',nginx,re.S)
        self.assertIsNotNone(match, 'Save draft currently falls through to Streamlit and returns HTTP 405')
        self.assertIn('proxy_pass http://127.0.0.1:8502',match.group(1))
        self.assertIn('X-GSF-Session-ID $gsf_session_cookie',match.group(1))
        self.assertIn('limit_except POST',match.group(1))


class PublicComponentDeepLinks(unittest.TestCase):
    def test_top_level_routes_keep_the_global_shell_and_iframes_keep_canonical_bytes(self):
        import os
        import urllib.request
        import urllib.error
        base=os.environ.get('GSF_BASE_URL')
        if not base:
            self.skipTest('requires running image GSF_BASE_URL')
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args):
                return None
        client=urllib.request.build_opener(NoRedirect)
        headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile Safari/604.1'}
        for path,target,component in (
            ('/game-editor-mobile/','editor','game_editor_mobile_component'),
            ('/editor-live/','editor','editor_2027_component'),
            ('/creator-hub-v156/','hub','creator_hub_v156_component'),
            ('/ai-v221/','ai','ai_v221_component'),
            ('/share-v156/','short','share_v156_component')):
            with self.subTest(path=path):
                request=urllib.request.Request(base+path,headers={**headers,'Sec-Fetch-Dest':'document'})
                try:
                    response=client.open(request,timeout=5)
                except urllib.error.HTTPError as exc:
                    response=exc
                with response:
                    self.assertEqual(response.status,302)
                    from urllib.parse import urlsplit
                    location=urlsplit(response.headers['Location'])
                    self.assertEqual(location.path+'?'+location.query,'/?gsf_page='+target)
                request=urllib.request.Request(base+path,headers={**headers,'Sec-Fetch-Dest':'iframe'})
                with client.open(request,timeout=5) as response:
                    self.assertEqual(response.read(),(ROOT/'web'/component/'index.html').read_bytes())


if __name__ == '__main__':
    unittest.main()
