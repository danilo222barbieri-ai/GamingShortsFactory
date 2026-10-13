from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/v397-production-gate.yml"


class CoordinationGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_coordination_paths_are_ignored_by_heavy_gate(self):
        required = (
            "- '.gsf/**'",
            "- 'PROJECT_STATUS.md'",
            "- 'AGENTS.md'",
            "- 'docs/superpowers/**'",
            "- 'docs/runbooks/**'",
        )
        for item in required:
            with self.subTest(item=item):
                self.assertIn(item, self.text)

    def test_coordination_paths_are_not_runtime_promotion_patterns(self):
        promotion = self.text.split("frontend=0", 1)[1].split("if [ \"$frontend\" -eq 0 ]", 1)[0]
        for forbidden in (".gsf/", "PROJECT_STATUS.md", "AGENTS.md", "docs/superpowers", "docs/runbooks"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, promotion)

    def test_runtime_paths_remain_covered(self):
        for runtime_path in ("Dockerfile|app.py", "web/*", "web/Dockerfile.worker", "web/ai_worker_server.py"):
            with self.subTest(runtime_path=runtime_path):
                self.assertIn(runtime_path, self.text)


if __name__ == "__main__":
    unittest.main()
