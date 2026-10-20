import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "web" / "direct_upload_server.py"
HUB = ROOT / "web" / "creator_hub_v156_component" / "index.html"


class OAuthReturnRegressionContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = SERVER.read_text(encoding="utf-8")
        cls.hub = HUB.read_text(encoding="utf-8")

    def test_tiktok_publish_connection_does_not_require_video_list(self):
        match = re.search(r'^TIKTOK_SCOPE="([^"]+)"', self.server, re.MULTILINE)
        self.assertIsNotNone(match, "TikTok OAuth scope declaration is missing")
        scopes = {item.strip() for item in match.group(1).split(",") if item.strip()}
        self.assertIn("user.info.basic", scopes)
        self.assertIn("video.publish", scopes)
        self.assertNotIn(
            "video.list",
            scopes,
            "video.list is an analytics permission and must not block the Direct Post connection",
        )

        callback = self.server[
            self.server.index("def _tiktok_oauth_callback") : self.server.index("def _tiktok_disconnect")
        ]
        self.assertNotIn(
            '"video.list"}<=granted',
            callback,
            "TikTok callback must accept a valid Direct Post grant without video.list",
        )

    def test_creator_hub_state_uses_authoritative_twitch_connection(self):
        state_route = self.server[
            self.server.index('if clean=="/creator-hub/state"') : self.server.index('if clean=="/account"')
        ]
        self.assertNotIn(
            '"twitch":bool(providers.get("twitch"))',
            state_route,
            "Twitch is a source OAuth connection, not a Creator login provider",
        )
        self.assertRegex(
            state_route,
            r'"twitch":\s*(?:bool\()?social_snapshot(?:\.get\("twitch"[^)]*\)|\["twitch"\])',
        )

    def test_oauth_navigation_failure_does_not_poison_restored_hub(self):
        self.assertIn("oauthNavigating", self.hub)
        connect_start = self.hub.index("function connectSocial")
        connect_end = self.hub.index("async function disconnectSocial", connect_start)
        self.assertIn("oauthNavigating=true", self.hub[connect_start:connect_end].replace(" ", ""))

        load_start = self.hub.index("async function loadState")
        load_end = self.hub.index("function openSection", load_start)
        load_block = self.hub[load_start:load_end]
        self.assertRegex(load_block, r'catch\s*\([^)]*\)\s*\{[^}]*oauthNavigating')

        pageshow = re.search(r'addEventListener\(["\']pageshow["\'][^;]+;', self.hub)
        self.assertIsNotNone(pageshow, "Creator Hub must repair BFCache restores after OAuth")
        self.assertIn("loadState", pageshow.group(0))

    def test_render_strips_restores_layout_after_transient_load_failure(self):
        start = self.hub.index("function renderStrips")
        end = self.hub.index("function renderShorts", start)
        block = self.hub[start:end]
        self.assertIn('classList.add("strip")', block)


if __name__ == "__main__":
    unittest.main()
