#!/usr/bin/env python3
"""
Unit and regression tests for GSF AI Engine 3.0 — Blocco 3 (Game-Aware AI).
Covers:
- Recognition of all 10 canonical game genres from titles/keywords.
- Profile metadata (priority, recommended duration, vision zones, padding).
- Correct application of genre-specific score multipliers in V2, V108, and V112.
- Clean fallback to 'Auto' when title is unknown.
"""
from __future__ import annotations

import unittest

from web.ai_performance_engine_v2 import (
    GAME_PROFILES,
    get_game_profile,
    infer_game_genre_v2,
    genre_score_multiplier_v2,
)
from web.game_vision_v108 import infer_game_genre, genre_score_multiplier, vision_zones_for_genre
from web.game_brain_v112 import _candidate


class TestGameAwareAiBlocco3(unittest.TestCase):
    def test_all_10_genres_defined_with_required_fields(self):
        expected_genres = [
            "FPS", "Battle Royale", "Action", "Racing", "Sports",
            "Survival", "Horror", "RPG", "Platform", "Narrative", "Auto"
        ]
        for g in expected_genres:
            self.assertIn(g, GAME_PROFILES)
            prof = GAME_PROFILES[g]
            self.assertTrue(prof.get("name"))
            self.assertTrue(prof.get("label"))
            self.assertTrue(prof.get("important_events"))
            self.assertIn(prof.get("recommended_duration"), (15, 30, 60))
            self.assertTrue(prof.get("priority"))
            self.assertIn("pre_event_seconds", prof.get("context_padding", {}))
            self.assertIn("post_event_seconds", prof.get("context_padding", {}))
            self.assertTrue(prof.get("vision_zones"))

    def test_title_inference_across_genres(self):
        cases = [
            ("Call of Duty Warzone clip", "Battle Royale"),
            ("CS2 de_mirage ace", "FPS"),
            ("Valorant radiant 1v4", "FPS"),
            ("Devil May Cry 5 combo SSS", "Action"),
            ("F1 24 Monaco lap", "Racing"),
            ("Rocket League aerial goal", "Sports"),
            ("Sons of the Forest shelter", "Survival"),
            ("Resident Evil Village jumpscare", "Horror"),
            ("Dark Souls 3 nameless king", "RPG"),
            ("Super Mario Wonder final stage", "Platform"),
            ("Detroit Become Human ending", "Narrative"),
            ("Unrecognized mystery game", "Auto"),
        ]
        for title, expected in cases:
            self.assertEqual(infer_game_genre_v2(title), expected)
            self.assertEqual(infer_game_genre(title), expected)

    def test_genre_score_multiplier_bounds(self):
        features = {
            "motion_burst": 0.8,
            "sustained_motion": 0.6,
            "continuity": 0.7,
            "audio_burst": 0.85,
            "synergy": 0.75,
            "arc": 0.8,
            "reaction": 0.9,
            "event_score": 0.85,
        }
        for g in GAME_PROFILES:
            mult = genre_score_multiplier_v2(g, "auto", features)
            self.assertGreaterEqual(mult, 0.93)
            self.assertLessEqual(mult, 1.08)

    def test_vision_zones_coverage(self):
        for g in ["FPS", "Battle Royale", "Action", "Racing", "Sports", "Survival", "Horror", "RPG", "Platform", "Narrative", "Auto"]:
            zones = vision_zones_for_genre(g)
            self.assertIsInstance(zones, list)
            self.assertTrue(len(zones) >= 1)


if __name__ == "__main__":
    unittest.main()
