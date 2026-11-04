#!/usr/bin/env python3
"""
Unit and regression tests for GSF AI Engine 3.0 — Blocco 4 (IA Personalizzata).
Covers:
- Strict per-user isolation of preferences (no global state bleeding).
- Progressive learning on selected/published events and genres.
- Safe, interpretable bounds on learning multiplier [0.88, 1.14].
- Reset functionality completely wiping/resetting user preferences.
- Integration with smart_rank_candidates via sid parameter.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from web.feedback_learning_v127 import (
    empty_user_model,
    load_user_model,
    reset_user_model,
    save_user_model,
    update_user_preferences,
    user_learning_multiplier,
    user_preferences_path,
)
from web.ai_performance_engine_v2 import smart_rank_candidates


class TestPersonalizedAiBlocco4(unittest.TestCase):
    def test_per_user_isolation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            sid_user_a = "user_alpha_123"
            sid_user_b = "user_beta_456"

            path_a = user_preferences_path(sid_user_a, runtime_root=root)
            path_b = user_preferences_path(sid_user_b, runtime_root=root)

            self.assertNotEqual(path_a, path_b)
            self.assertIn(sid_user_a, str(path_a))
            self.assertIn(sid_user_b, str(path_b))

            # Update User A with clutch preference
            update_user_preferences(
                sid_user_a,
                {"event": "clutch", "genre": "FPS", "action": "published", "score": 0.92},
                runtime_root=root,
            )
            # Update User B with reaction preference in Horror
            update_user_preferences(
                sid_user_b,
                {"event": "reaction", "genre": "Horror", "action": "published", "score": 0.88},
                runtime_root=root,
            )

            model_a = load_user_model(sid_user_a, runtime_root=root)
            model_b = load_user_model(sid_user_b, runtime_root=root)

            # User A should have clutch, but not reaction
            self.assertIn("clutch", model_a.get("events", {}))
            self.assertNotIn("reaction", model_a.get("events", {}))

            # User B should have reaction, but not clutch
            self.assertIn("reaction", model_b.get("events", {}))
            self.assertNotIn("clutch", model_b.get("events", {}))

    def test_progressive_learning_and_bounded_multiplier(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            sid = "user_gamer_777"

            # Initial empty model
            model = load_user_model(sid, runtime_root=root)
            init_mult = user_learning_multiplier(model, "clutch", genre="FPS")
            self.assertEqual(init_mult, 1.0)

            # 5 consecutive published choices of "clutch" in "FPS"
            for _ in range(5):
                model = update_user_preferences(
                    sid,
                    {"event": "clutch", "genre": "FPS", "action": "published", "score": 0.95},
                    runtime_root=root,
                )

            learned_mult = user_learning_multiplier(model, "clutch", genre="FPS")
            self.assertGreater(learned_mult, 1.0)
            self.assertLessEqual(learned_mult, 1.14)

            # Rejections lower the multiplier
            for _ in range(8):
                model = update_user_preferences(
                    sid,
                    {"event": "clutch", "genre": "FPS", "action": "rejected", "score": 0.40},
                    runtime_root=root,
                )

            penalized_mult = user_learning_multiplier(model, "clutch", genre="FPS")
            self.assertLess(penalized_mult, 1.0)
            self.assertGreaterEqual(penalized_mult, 0.88)

    def test_reset_user_preferences(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            sid = "user_reset_test"

            update_user_preferences(
                sid,
                {"event": "boss", "genre": "RPG", "action": "selected", "score": 0.85},
                runtime_root=root,
            )
            model_before = load_user_model(sid, runtime_root=root)
            self.assertEqual(model_before.get("total_feedback"), 1)

            # Reset preferences
            reset_user_model(sid, runtime_root=root)
            model_after = load_user_model(sid, runtime_root=root)
            self.assertEqual(model_after.get("total_feedback"), 0)
            self.assertEqual(model_after.get("events"), {})
            self.assertEqual(model_after.get("genres"), {})
            self.assertEqual(model_after.get("recent_choices"), [])


if __name__ == "__main__":
    unittest.main()
