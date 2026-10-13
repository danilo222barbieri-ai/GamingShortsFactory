from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs/runbooks/gsf-one-command-workflow.md"
AGENTS = ROOT / "AGENTS.md"


class OneCommandContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not RUNBOOK.exists():
            raise AssertionError("one-command runbook is missing")
        cls.runbook = RUNBOOK.read_text(encoding="utf-8")
        cls.agents = AGENTS.read_text(encoding="utf-8")

    def test_state_machine_is_complete(self):
        required = (
            "INTAKE", "CLAIMED", "IMPLEMENTING", "TESTED", "INTEGRATING",
            "GATE", "DEPLOYING", "VERIFYING", "LIVE", "BLOCKED",
            "ROLLED_BACK", "HANDOFF",
        )
        for state in required:
            with self.subTest(state=state):
                self.assertIn(state, self.runbook)

    def test_terminal_statuses_are_exact(self):
        for status in ("LIVE", "BLOCKED", "ROLLED_BACK", "HANDOFF_REQUIRED"):
            self.assertIn(f"`{status}`", self.runbook)

    def test_safe_close_boundary_is_explicit(self):
        self.assertIn("GitHub handoff", self.runbook)
        self.assertIn("before GitHub handoff", self.runbook)
        self.assertIn("no guarantee", self.runbook.lower())

    def test_agents_make_protocol_default_for_coding_requests(self):
        self.assertIn("one-command", self.agents.lower())
        self.assertIn("coding request", self.agents.lower())


if __name__ == "__main__":
    unittest.main()
