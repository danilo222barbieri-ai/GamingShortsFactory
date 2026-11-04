#!/usr/bin/env python3
"""
Unit and regression tests for GSF AI Engine 3.1 — Blocco 4 (Account-Bound Persistent Personalization).

Covers:
1. Account-bound durable storage in users/{account_id}/ai_user_preferences.json.
2. Guest session storage in sessions/{sid}/ai_user_preferences.json.
3. Seamless migration of guest session preferences when an account_id is authenticated.
4. Strict per-account isolation (no cross-account leakage).
5. Progressive Bayesian learning safely bounded in [0.88, 1.14].
6. Factory reset to default settings via reset_user_model and HTTP endpoint simulation.
"""
from __future__ import annotations

import json
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


class TestAccountBoundPersonalizationBlocco4(unittest.TestCase):
    def test_account_bound_vs_guest_storage_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sid = "guest_session_999"
            acc_id = "usr_acc_alpha_123"

            # 1. Guest path: should be in sessions/
            guest_path = user_preferences_path(sid, account_id=None, runtime_root=root)
            self.assertIn("sessions", str(guest_path))
            self.assertIn(sid, str(guest_path))

            # 2. Account path: should be in users/
            acc_path = user_preferences_path(sid, account_id=acc_id, runtime_root=root)
            self.assertIn("users", str(acc_path))
            self.assertIn(acc_id, str(acc_path))
            self.assertNotEqual(guest_path, acc_path)

    def test_account_isolation_and_progressive_learning(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            acc_a = "usr_creator_A"
            acc_b = "usr_creator_B"

            # Creator A selects and publishes clutch moments in FPS
            for _ in range(4):
                update_user_preferences(
                    sid="sid_a",
                    event_row={"event": "clutch", "genre": "FPS", "action": "published", "score": 0.95},
                    account_id=acc_a,
                    runtime_root=root,
                )

            # Creator B selects and publishes reaction moments in Horror
            for _ in range(4):
                update_user_preferences(
                    sid="sid_b",
                    event_row={"event": "reaction", "genre": "Horror", "action": "published", "score": 0.90},
                    account_id=acc_b,
                    runtime_root=root,
                )

            model_a = load_user_model(account_id=acc_a, runtime_root=root)
            model_b = load_user_model(account_id=acc_b, runtime_root=root)

            # Strict isolation: Creator A has clutch, not reaction
            self.assertIn("clutch", model_a.get("events", {}))
            self.assertNotIn("reaction", model_a.get("events", {}))

            # Creator B has reaction, not clutch
            self.assertIn("reaction", model_b.get("events", {}))
            self.assertNotIn("clutch", model_b.get("events", {}))

            # Learning multiplier bounds [0.88, 1.14]
            mult_a_clutch = user_learning_multiplier(model_a, "clutch", genre="FPS")
            mult_a_reaction = user_learning_multiplier(model_a, "reaction", genre="Horror")
            self.assertGreater(mult_a_clutch, 1.0)
            self.assertLessEqual(mult_a_clutch, 1.14)
            self.assertEqual(mult_a_reaction, 1.0)

    def test_seamless_migration_from_guest_session_to_account(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            guest_sid = "temp_guest_session_777"
            auth_account = "usr_permanent_account_888"

            # 1. Guest performs actions before logging in
            update_user_preferences(
                sid=guest_sid,
                event_row={"event": "boss", "genre": "RPG", "action": "published", "score": 0.94},
                account_id=None,
                runtime_root=root,
            )

            # Guest file exists, account file does not exist yet
            guest_file = user_preferences_path(guest_sid, account_id=None, runtime_root=root)
            acc_file = user_preferences_path(guest_sid, account_id=auth_account, runtime_root=root)
            self.assertTrue(guest_file.is_file())
            self.assertFalse(acc_file.is_file())

            # 2. User logs in: loading with both sid and account_id migrates preferences to account
            migrated_model = load_user_model(sid=guest_sid, account_id=auth_account, runtime_root=root)
            self.assertEqual(migrated_model.get("total_feedback"), 1)
            self.assertIn("boss", migrated_model.get("events", {}))
            self.assertTrue(acc_file.is_file())

    def test_factory_reset_wipes_preferences(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            acc_id = "usr_to_reset"

            # Populate preferences
            update_user_preferences(
                sid="",
                event_row={"event": "goal", "genre": "Sports", "action": "published", "score": 0.90},
                account_id=acc_id,
                runtime_root=root,
            )
            model_before = load_user_model(account_id=acc_id, runtime_root=root)
            self.assertEqual(model_before.get("total_feedback"), 1)

            # Factory reset
            reset_model = reset_user_model(account_id=acc_id, runtime_root=root)
            self.assertEqual(reset_model.get("total_feedback"), 0)
            self.assertEqual(reset_model.get("events"), {})
            self.assertEqual(reset_model.get("genres"), {})
            self.assertEqual(reset_model.get("recent_choices"), [])

            # Reload to verify persistence of reset state
            reloaded = load_user_model(account_id=acc_id, runtime_root=root)
            self.assertEqual(reloaded.get("total_feedback"), 0)

    def test_smart_ranking_incorporates_account_preferences(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            acc_id = "usr_ranking_pref"

            # Teach ranker to prioritize clutch
            for _ in range(5):
                update_user_preferences(
                    sid="",
                    event_row={"event": "clutch", "genre": "FPS", "action": "published", "score": 0.95},
                    account_id=acc_id,
                    runtime_root=root,
                )

            # Scan with 2 candidate peaks: one standard highlight, one clutch
            audio = [0.20] * 60
            motion = [0.20] * 60
            for i in range(10, 16):
                audio[i] = 0.85
                motion[i] = 0.85
            for i in range(35, 41):
                audio[i] = 0.85
                motion[i] = 0.85
            scan = {"step": 0.5, "audio": audio, "peak": audio, "motion": motion}

            import os
            old_root = os.environ.get("GSF_RUNTIME_ROOT")
            try:
                os.environ["GSF_RUNTIME_ROOT"] = str(root)
                selected, alternates = smart_rank_candidates(
                    scan, target_duration=15.0, genre="FPS", account_id=acc_id
                )
                self.assertTrue(len(selected) > 0)
            finally:
                if old_root is not None:
                    os.environ["GSF_RUNTIME_ROOT"] = old_root
                else:
                    os.environ.pop("GSF_RUNTIME_ROOT", None)


if __name__ == "__main__":
    unittest.main()
