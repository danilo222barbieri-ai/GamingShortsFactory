from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.gsf_claims import Claim, find_conflicts, normalize_paths, patterns_overlap, validate_claim_dict


class ClaimModelTests(unittest.TestCase):
    def test_normalize_paths_deduplicates_and_sorts(self):
        self.assertEqual(normalize_paths(["web/b.py", "web/a.py", "web/b.py"]), ["web/a.py", "web/b.py"])

    def test_exact_overlap(self):
        self.assertTrue(patterns_overlap("web/editor.py", "web/editor.py"))

    def test_glob_exact_overlap(self):
        self.assertTrue(patterns_overlap("web/fix_v*_mobile_editor_*.py", "web/fix_v403_mobile_editor_x.py"))
        self.assertTrue(patterns_overlap("web/fix_v403_mobile_editor_x.py", "web/fix_v*_mobile_editor_*.py"))

    def test_glob_glob_overlap(self):
        self.assertTrue(patterns_overlap("web/editor_*.py", "web/*_2027.py"))

    def test_non_overlap(self):
        self.assertFalse(patterns_overlap("web/editor_*.py", "web/ai_worker_server.py"))

    def test_validate_rejects_unknown_state(self):
        with self.assertRaises(ValueError):
            validate_claim_dict({
                "id": "x",
                "branch": "chat/x-abcd",
                "scope": "x",
                "paths": ["web/x.py"],
                "owner": "chat/x-abcd",
                "created_at": "2026-10-13T23:50:00+02:00",
                "state": "mystery",
            })

    def test_only_active_and_handoff_block(self):
        requested = ["web/editor.py"]
        active = Claim("a", "chat/a", "editor", ["web/editor.py"], "chat/a", "2026-10-13T23:50:00+02:00", "active")
        handoff = Claim("b", "chat/b", "editor", ["web/editor.py"], "chat/b", "2026-10-13T23:50:00+02:00", "handoff")
        completed = Claim("c", "chat/c", "editor", ["web/editor.py"], "chat/c", "2026-10-13T23:50:00+02:00", "completed")
        conflicts = find_conflicts(requested, [active, handoff, completed])
        self.assertEqual([c.id for c in conflicts], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
