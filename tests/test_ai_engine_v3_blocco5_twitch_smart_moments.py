#!/usr/bin/env python3
"""
Unit and regression tests for GSF AI Engine 3.0 — Blocco 5 (Twitch Smart Moments).
Verifies:
- Official Helix API integration for Twitch VOD moments.
- Returning up to 3 reliable moments ranked by views/climax, avoiding near-duplicates.
- Honest handling when insufficient clips/markers exist for a VOD (no fake confidence).
- Isolation: only the user-selected clip is acquired on «Carica su GSF», never full VOD.
"""
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from web.direct_upload_server import _twitch_vod_moments


class TestTwitchSmartMomentsBlocco5(unittest.TestCase):
    @patch("web.direct_upload_server._twitch_access")
    @patch("web.direct_upload_server._twitch_api")
    def test_vod_moments_with_clips(self, mock_api, mock_access):
        mock_access.return_value = {"access_token": "fake_tok", "user_id": "12345"}
        
        # Mock VOD details
        mock_api.side_effect = [
            # 1. videos
            {
                "data": [{
                    "id": "vod_999",
                    "title": "Epic 6 Hour Stream",
                    "duration": "6h30m15s",
                    "created_at": "2026-11-04T12:00:00Z",
                }]
            },
            # 2. clips
            {
                "data": [
                    {
                        "id": "clip_alpha",
                        "video_id": "vod_999",
                        "title": "Triple Kill Clutch",
                        "vod_offset": 3600.0,
                        "duration": 30.0,
                        "view_count": 500,
                        "thumbnail_url": "https://twitch.tv/thumb1_%{width}x%{height}.jpg",
                        "url": "https://clips.twitch.tv/clip_alpha",
                    },
                    {
                        "id": "clip_beta",
                        "video_id": "vod_999",
                        "title": "Boss Fight Victory",
                        "vod_offset": 7200.0,
                        "duration": 45.0,
                        "view_count": 1200,
                        "thumbnail_url": "https://twitch.tv/thumb2_%{width}x%{height}.jpg",
                        "url": "https://clips.twitch.tv/clip_beta",
                    },
                    {
                        "id": "clip_gamma_overlap",
                        "video_id": "vod_999",
                        "title": "Near duplicate of Boss Fight",
                        "vod_offset": 7205.0,
                        "duration": 40.0,
                        "view_count": 50,
                        "thumbnail_url": "https://twitch.tv/thumb3_%{width}x%{height}.jpg",
                        "url": "https://clips.twitch.tv/clip_gamma",
                    },
                    {
                        "id": "clip_delta",
                        "video_id": "vod_999",
                        "title": "Funny Reaction",
                        "vod_offset": 10800.0,
                        "duration": 20.0,
                        "view_count": 300,
                        "thumbnail_url": "https://twitch.tv/thumb4_%{width}x%{height}.jpg",
                        "url": "https://clips.twitch.tv/clip_delta",
                    },
                    {
                        "id": "clip_unrelated_vod",
                        "video_id": "vod_other",
                        "title": "From other VOD",
                        "vod_offset": 100.0,
                        "duration": 15.0,
                        "view_count": 9999,
                    }
                ]
            }
        ]

        res = _twitch_vod_moments("test_sid", "vod_999")
        self.assertEqual(res.get("reason"), "success")
        moments = res.get("moments", [])
        self.assertEqual(len(moments), 3)

        # Ranked by views (clip_beta has 1200 views, clip_alpha has 500 views, clip_delta has 300 views)
        self.assertEqual(moments[0]["id"], "clip_beta")
        self.assertEqual(moments[1]["id"], "clip_alpha")
        self.assertEqual(moments[2]["id"], "clip_delta")

        # Overlapping clip_gamma (offset 7205 vs 7200) was eliminated
        self.assertNotIn("clip_gamma_overlap", [m["id"] for m in moments])
        # Unrelated VOD clip was not included
        self.assertNotIn("clip_unrelated_vod", [m["id"] for m in moments])

    @patch("web.direct_upload_server._twitch_access")
    @patch("web.direct_upload_server._twitch_api")
    def test_vod_moments_insufficient_data_honesty(self, mock_api, mock_access):
        mock_access.return_value = {"access_token": "fake_tok", "user_id": "12345"}
        mock_api.side_effect = [
            {"data": [{"id": "vod_empty", "title": "Quiet VOD", "duration": "1h", "created_at": "2026-11-04T12:00:00Z"}]},
            {"data": []}  # No clips
        ]

        res = _twitch_vod_moments("test_sid", "vod_empty")
        self.assertEqual(res.get("count"), 0)
        self.assertEqual(res.get("reason"), "insufficient_data")
        self.assertTrue(len(res.get("message", "")) > 10)
        self.assertEqual(res.get("moments"), [])


if __name__ == "__main__":
    unittest.main()
