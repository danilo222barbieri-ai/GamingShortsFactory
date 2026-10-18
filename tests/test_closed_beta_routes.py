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


if __name__ == '__main__':
    unittest.main()
