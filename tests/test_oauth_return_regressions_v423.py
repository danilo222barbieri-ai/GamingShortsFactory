import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "web" / "direct_upload_server_v423.py"
START = ROOT / "web" / "start_web.sh"


class OAuthReturnRegressionContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patch = PATCH.read_text(encoding="utf-8")
        cls.start = START.read_text(encoding="utf-8")

    def test_tiktok_publish_connection_does_not_require_video_list(self):
        self.assertIn('base.TIKTOK_SCOPE = "user.info.basic,video.publish"', self.patch)
        callback = self.patch[
            self.patch.index("def _tiktok_oauth_callback") : self.patch.index("base._tiktok_oauth_callback =")
        ]
        self.assertIn('{"user.info.basic", "video.publish"}', callback)
        self.assertNotIn(
            "video.list",
            callback,
            "video.list is analytics-only and must not block Direct Post OAuth",
        )

    def test_creator_hub_state_uses_authoritative_twitch_connection(self):
        route = self.patch[
            self.patch.index("def _creator_hub_state") : self.patch.index("class Handler")
        ]
        self.assertIn("social_snapshot = base._creator_social_snapshot", route)
        self.assertIn('"twitch": bool(social_snapshot.get("twitch"))', route)
        self.assertNotIn('bool(providers.get("twitch"))', route)

    def test_social_oauth_return_forces_fresh_mobile_page(self):
        redirect = self.patch[
            self.patch.index("def _fresh_social_redirect") : self.patch.index("base._redirect =")
        ]
        self.assertIn("oauth_return=", redirect)
        self.assertIn('"Cache-Control", "no-store, max-age=0"', redirect)
        self.assertIn('"Pragma", "no-cache"', redirect)

    def test_canonical_startup_uses_v423_entrypoint(self):
        self.assertIn("python /app/web/direct_upload_server_v423.py &", self.start)
        self.assertNotIn("python /app/web/direct_upload_server.py &", self.start)


if __name__ == "__main__":
    unittest.main()
