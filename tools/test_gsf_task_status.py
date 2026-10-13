from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.gsf_claims import Claim
from tools.gsf_task import task_status_payload


class TaskStatusTests(unittest.TestCase):
    def test_machine_readable_status_shape(self):
        claim = Claim(
            id="editor-a1b2c3",
            branch="chat/editor-a1b2c3",
            scope="Game Editor mobile",
            paths=["web/editor.py"],
            owner="chat/editor-a1b2c3",
            created_at="2026-10-13T22:00:00Z",
            state="active",
            evidence={
                "commit": "abc123",
                "pr": 42,
                "tests": {"unit": "PASS"},
                "gate": "pending",
                "railway": None,
                "terminal_status": None,
                "updated_at": "2026-10-13T22:05:00Z",
            },
        )
        payload = task_status_payload(claim)
        self.assertEqual(
            set(payload),
            {"claim_id", "branch", "scope", "state", "paths", "commit", "pr", "tests", "gate", "railway", "terminal_status", "updated_at"},
        )
        self.assertEqual(payload["claim_id"], "editor-a1b2c3")
        self.assertEqual(payload["pr"], 42)
        self.assertEqual(payload["tests"]["unit"], "PASS")

    def test_defaults_do_not_invent_success(self):
        claim = Claim("x", "chat/x", "x", ["web/x.py"], "chat/x", "2026-10-13T22:00:00Z", "active")
        payload = task_status_payload(claim)
        self.assertIsNone(payload["terminal_status"])
        self.assertIsNone(payload["gate"])
        self.assertIsNone(payload["railway"])
        self.assertEqual(payload["tests"], {})


if __name__ == "__main__":
    unittest.main()
