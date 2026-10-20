import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SERVER=(ROOT/"web/direct_upload_server.py").read_text(encoding="utf-8")
HUB=(ROOT/"web/creator_hub_v156_component/index.html").read_text(encoding="utf-8")
class OAuthReturnRegressionContracts(unittest.TestCase):
    def test_tiktok_direct_post_scope_is_minimal(self):
        m=re.search(r'^TIKTOK_SCOPE="([^"]+)"',SERVER,re.M); self.assertIsNotNone(m); scopes=set(m.group(1).split(',')); self.assertIn('user.info.basic',scopes); self.assertIn('video.publish',scopes); self.assertNotIn('video.list',scopes)
        cb=SERVER[SERVER.index('def _tiktok_oauth_callback'):SERVER.index('def _tiktok_disconnect')]; self.assertNotIn('"video.list"}<=granted',cb)
    def test_twitch_state_uses_authoritative_social_snapshot(self):
        block=SERVER[SERVER.index('if clean=="/creator-hub/state":'):SERVER.index('if clean=="/account":')]; self.assertIn('"twitch":bool(social_snapshot.get("twitch"))',block); self.assertNotIn('"twitch":bool(providers.get("twitch"))',block)
    def test_oauth_return_is_fresh_and_no_store(self):
        self.assertIn('oauth_return=',SERVER); self.assertIn('no-store, max-age=0',SERVER); self.assertIn('handler.send_header("Pragma","no-cache")',SERVER)
    def test_hub_suppresses_transient_navigation_failure(self):
        self.assertIn('oauthNavigating=true',HUB.replace(' ','')); self.assertIn('oauthNavigating||document.visibilityState==="hidden"',HUB); self.assertIn('pageshow",()=>{oauthNavigating=false;repairFrame();loadState()}',HUB)
if __name__=='__main__':unittest.main()
