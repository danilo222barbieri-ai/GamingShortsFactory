from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.gsf_rollback_policy import (
    incident_key,
    should_rollback,
    validate_incident_index,
    validate_known_good,
)


def snapshot(status="SUCCESS", *, deployment="B", health="healthy", current=True, kind="frontend"):
    return {
        "service_id": "svc",
        "deployment_id": deployment,
        "status": status,
        "health": health,
        "is_current": current,
        "service_kind": kind,
    }


def known_good(deployment="A"):
    return {
        "version": 1,
        "services": {
            "svc": {
                "service_id": "svc",
                "environment_id": "prod",
                "deployment_id": deployment,
                "promotion_commit": "abc",
                "verified_at": "2026-10-13T22:00:00Z",
                "health_endpoint": "/healthz",
                "state": "verified",
            }
        },
    }


def incidents(records=None):
    return {"version": 1, "incidents": records or {}}


class RollbackPolicyTests(unittest.TestCase):
    def test_success_does_nothing(self):
        self.assertEqual(should_rollback(snapshot(), incidents(), known_good()).action, "none")

    def test_failed_rolls_back_to_known_good(self):
        decision = should_rollback(snapshot("FAILED"), incidents(), known_good("A"))
        self.assertEqual(decision.action, "rollback")
        self.assertEqual(decision.target_deployment_id, "A")

    def test_crashed_rolls_back(self):
        self.assertEqual(should_rollback(snapshot("CRASHED"), incidents(), known_good()).action, "rollback")

    def test_oom_rolls_back(self):
        self.assertEqual(should_rollback(snapshot("OOM_KILLED"), incidents(), known_good()).action, "rollback")

    def test_sustained_unhealthy_frontend_rolls_back(self):
        self.assertEqual(
            should_rollback(snapshot("SUCCESS", health="unhealthy_sustained"), incidents(), known_good()).action,
            "rollback",
        )

    def test_sleeping_worker_is_healthy_when_sleep_enabled(self):
        current = snapshot("SLEEPING", kind="worker")
        current["sleep_enabled"] = True
        self.assertEqual(should_rollback(current, incidents(), known_good()).action, "none")

    def test_isolated_5xx_is_notify_only(self):
        self.assertEqual(
            should_rollback(snapshot("SUCCESS", health="isolated_5xx"), incidents(), known_good()).action,
            "notify",
        )

    def test_superseded_failure_does_not_rollback(self):
        self.assertEqual(should_rollback(snapshot("FAILED", current=False), incidents(), known_good()).action, "none")

    def test_missing_known_good_fails_closed(self):
        decision = should_rollback(snapshot("FAILED"), incidents(), {"version": 1, "services": {}})
        self.assertEqual(decision.action, "notify")
        self.assertIsNone(decision.target_deployment_id)

    def test_duplicate_incident_never_redeploys_twice(self):
        key = incident_key("svc", "B")
        index = incidents({key: {"attempt_count": 1, "status": "rollback_attempted"}})
        self.assertNotEqual(should_rollback(snapshot("FAILED"), index, known_good()).action, "rollback")

    def test_failed_recovery_escalates(self):
        current = snapshot("FAILED")
        current["recovery_failed"] = True
        self.assertEqual(should_rollback(current, incidents(), known_good()).action, "escalate")

    def test_schema_rejects_secret_like_keys(self):
        bad = known_good()
        bad["services"]["svc"]["token"] = "nope"
        with self.assertRaises(ValueError):
            validate_known_good(bad)
        bad_incident = incidents({"svc:B": {"attempt_count": 1, "secret": "nope"}})
        with self.assertRaises(ValueError):
            validate_incident_index(bad_incident)

    def test_end_to_end_failed_release_allows_exactly_one_rollback(self):
        current = snapshot("FAILED", deployment="B")
        first = should_rollback(current, incidents(), known_good("A"))
        self.assertEqual(first.action, "rollback")
        self.assertEqual(first.target_deployment_id, "A")

        key = incident_key("svc", "B")
        after_attempt = incidents({
            key: {
                "attempt_count": 1,
                "status": "rollback_attempted",
                "target_deployment_id": "A",
            }
        })
        second = should_rollback(current, after_attempt, known_good("A"))
        self.assertNotEqual(second.action, "rollback")
        self.assertIn(second.action, {"notify", "none"})

    def test_end_to_end_failed_recovery_escalates_without_recursive_rollback(self):
        recovery = snapshot("FAILED", deployment="C")
        recovery["recovery_failed"] = True
        decision = should_rollback(recovery, incidents(), known_good("A"))
        self.assertEqual(decision.action, "escalate")
        self.assertIsNone(decision.target_deployment_id)


if __name__ == "__main__":
    unittest.main()
