"""Runs the Production Gate promotion step against throw-away git repos.

Regression: a runtime merge whose own gate run was skipped, followed by a
docs-only push, left Railway on the old build because the step only diffed
the last push. The step must diff each service against its current marker.
"""
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "v397-production-gate.yml"


def promotion_script() -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    block = text.split("- name: Promote tested commit to Railway", 1)[1]
    block = block.split("\n      - name:", 1)[0]
    body = block.split("run: |\n", 1)[1]
    return "\n".join(line[10:] if line.startswith(" " * 10) else line.strip() for line in body.splitlines())


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class PromotionDiffTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.origin = base / "origin.git"
        self.work = base / "work"
        git(base, "init", "-q", "--bare", "-b", "main", str(self.origin))
        git(base, "clone", "-q", str(self.origin), str(self.work))
        for key, value in (("user.name", "t"), ("user.email", "t@example.com")):
            git(self.work, "config", key, value)
        (self.work / "README.md").write_text("x\n")
        self.commit("init")
        self.promoted = git(self.work, "rev-parse", "HEAD")
        (self.work / ".railway").mkdir()
        for name in ("frontend-deploy.txt", "worker-deploy.txt"):
            (self.work / ".railway" / name).write_text(self.promoted + "\n")
        self.commit("deploy: markers")

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, message):
        git(self.work, "add", "-A")
        git(self.work, "commit", "-q", "-m", message)
        git(self.work, "push", "-q", "origin", "HEAD:main")
        return git(self.work, "rev-parse", "HEAD")

    def run_step(self, before, tested):
        env = dict(os.environ, BEFORE_SHA=before, TESTED_SHA=tested)
        out = subprocess.run(["bash", "-c", promotion_script()], cwd=self.work, env=env,
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        return out.stdout

    def marker(self, name):
        git(self.work, "fetch", "-q", "origin")
        return git(self.work, "show", f"origin/main:.railway/{name}")

    def test_docs_push_after_unpromoted_runtime_merge_promotes_frontend(self):
        (self.work / "web").mkdir()
        (self.work / "web" / "page.html").write_text("new\n")
        self.commit("feat: runtime change whose gate was skipped")
        before = git(self.work, "rev-parse", "HEAD")
        (self.work / "CLAUDE.md").write_text("note\n")
        tested = self.commit("docs: note")
        self.run_step(before, tested)
        self.assertEqual(self.marker("frontend-deploy.txt"), tested)
        self.assertEqual(self.marker("worker-deploy.txt"), self.promoted, "worker files did not change")

    def test_docs_only_since_promotion_writes_no_marker(self):
        (self.work / "CLAUDE.md").write_text("note\n")
        before = git(self.work, "rev-parse", "HEAD~0")
        tested = self.commit("docs: note")
        out = self.run_step(before, tested)
        self.assertIn("No Railway runtime files changed", out)
        self.assertEqual(self.marker("frontend-deploy.txt"), self.promoted)

    def test_invalid_marker_falls_back_to_previous_push(self):
        (self.work / ".railway" / "frontend-deploy.txt").write_text("not-a-sha\n")
        self.commit("break marker")
        before = git(self.work, "rev-parse", "HEAD")
        (self.work / "gsf_core").mkdir()
        (self.work / "gsf_core" / "x.py").write_text("x = 1\n")
        tested = self.commit("feat: core")
        self.run_step(before, tested)
        self.assertEqual(self.marker("frontend-deploy.txt"), tested)

    def test_workflow_uses_marker_bases(self):
        script = promotion_script()
        self.assertIn("base_for .railway/frontend-deploy.txt", script)
        self.assertIn("base_for .railway/worker-deploy.txt", script)
        self.assertTrue(re.search(r"merge-base --is-ancestor", script))


if __name__ == "__main__":
    unittest.main()
