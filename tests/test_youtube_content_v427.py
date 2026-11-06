import unittest
import sys
import types
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
sys.path.insert(0, str(ROOT))

botocore = types.ModuleType("botocore")
botocore_config = types.ModuleType("botocore.config")
botocore_config.Config = MagicMock()
botocore_exceptions = types.ModuleType("botocore.exceptions")
botocore_exceptions.ClientError = Exception
sys.modules["botocore"] = botocore
sys.modules["botocore.config"] = botocore_config
sys.modules["botocore.exceptions"] = botocore_exceptions

boto3 = types.ModuleType("boto3")
boto3_s3 = types.ModuleType("boto3.s3")
boto3_s3_transfer = types.ModuleType("boto3.s3.transfer")
boto3_s3_transfer.TransferConfig = MagicMock()
sys.modules["boto3"] = boto3
sys.modules["boto3.s3"] = boto3_s3
sys.modules["boto3.s3.transfer"] = boto3_s3_transfer

from web.direct_upload_server import _parse_yt_duration, _youtube_content, _YouTubeContentError


class TestYouTubeContent(unittest.TestCase):
    def test_parse_yt_duration(self):
        self.assertEqual(_parse_yt_duration("PT15M33S"), 933)
        self.assertEqual(_parse_yt_duration("PT1H2M3S"), 3723)
        self.assertEqual(_parse_yt_duration("PT45S"), 45)
        self.assertEqual(_parse_yt_duration("PT1H"), 3600)
        self.assertEqual(_parse_yt_duration(""), 0)
        self.assertEqual(_parse_yt_duration(None), 0)

    @patch("web.direct_upload_server._youtube_analytics_token")
    def test_youtube_content_disconnected(self, mock_token):
        # V442: a missing/expired authorization is an explicit 401, so the Hub
        # can tell "not connected" apart from "no content" or "API down".
        mock_token.return_value = {}
        with self.assertRaises(_YouTubeContentError) as ctx:
            _youtube_content("test-sid")
        self.assertEqual(ctx.exception.status, 401)

    @patch("web.direct_upload_server.urllib.request.urlopen")
    @patch("web.direct_upload_server._youtube_analytics_token")
    def test_youtube_content_connected_mock(self, mock_token, mock_urlopen):
        mock_token.return_value = {"access_token": "mock-token-xyz"}

        # Response 1: channels.list
        ch_resp = MagicMock()
        ch_resp.__enter__.return_value = ch_resp
        ch_resp.read.return_value = json.dumps({
            "items": [{
                "id": "UC123456",
                "snippet": {"title": "Danilo Gaming", "customUrl": "@DaniloGaming", "thumbnails": {"default": {"url": "https://thumb/ch.jpg"}}},
                "statistics": {"subscriberCount": "1500", "videoCount": "42", "viewCount": "120000"},
                "contentDetails": {"relatedPlaylists": {"uploads": "UU123456"}}
            }]
        }).encode("utf-8")

        # Response 2: playlistItems.list
        pl_resp = MagicMock()
        pl_resp.__enter__.return_value = pl_resp
        pl_resp.read.return_value = json.dumps({
            "items": [{
                "snippet": {"title": "FC25 Pro Highlights #1", "publishedAt": "2026-10-15T12:00:00Z", "thumbnails": {"medium": {"url": "https://thumb/v1.jpg"}}},
                "contentDetails": {"videoId": "vid_abc123"}
            }],
            "nextPageToken": "cursor_page_2"
        }).encode("utf-8")

        # Response 3: videos.list
        v_resp = MagicMock()
        v_resp.__enter__.return_value = v_resp
        v_resp.read.return_value = json.dumps({
            "items": [{
                "id": "vid_abc123",
                "contentDetails": {"duration": "PT12M45S"},
                "statistics": {"viewCount": "3500", "likeCount": "210"}
            }]
        }).encode("utf-8")

        mock_urlopen.side_effect = [ch_resp, pl_resp, v_resp]

        res = _youtube_content("test-sid")
        self.assertTrue(res["connected"])
        self.assertEqual(res["cursor"], "cursor_page_2")
        self.assertEqual(res["channel"]["title"], "Danilo Gaming")
        self.assertEqual(res["channel"]["subscribers"], 1500)
        self.assertEqual(len(res["data"]), 1)
        video = res["data"][0]
        self.assertEqual(video["id"], "vid_abc123")
        self.assertEqual(video["title"], "FC25 Pro Highlights #1")
        self.assertEqual(video["duration"], 765)
        self.assertEqual(video["views"], 3500)
        self.assertEqual(video["likes"], 210)
        self.assertFalse(video["can_import"])
        self.assertIn("API ufficiali", video["import_reason"])


if __name__ == "__main__":
    unittest.main()
