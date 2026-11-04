import unittest
import tempfile
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from web.workflow_engine_v4 import (
    WorkflowState,
    WorkflowPath,
    ProjectWorkflow,
    load_workflow,
    save_workflow,
)


class TestWorkflowServerIntegration(unittest.TestCase):

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.session_root = Path(self.td.name)

    def tearDown(self):
        self.td.cleanup()

    def test_01_upload_sets_percorso_a_or_b(self):
        # Case A: duration >= 15s -> UPLOADED
        wf = load_workflow(self.session_root)
        wf.duration = 25.0
        self.assertTrue(wf.transition_to(WorkflowState.UPLOADED, source_path="/tmp/game.mp4"))
        self.assertEqual(wf.state, WorkflowState.UPLOADED)
        self.assertEqual(wf.path, WorkflowPath.PERCORSO_A)
        self.assertTrue(wf.allowed_actions()["find_moments"])
        self.assertFalse(wf.allowed_actions()["open_editor"])

        # Case B: duration < 15s -> EDITOR_READY
        wf_b = ProjectWorkflow(state=WorkflowState.EMPTY, duration=12.0)
        self.assertTrue(wf_b.transition_to(WorkflowState.UPLOADED, source_path="/tmp/short.mp4"))
        self.assertEqual(wf_b.state, WorkflowState.EDITOR_READY)
        self.assertEqual(wf_b.path, WorkflowPath.PERCORSO_B)
        self.assertFalse(wf_b.allowed_actions()["find_moments"])
        self.assertTrue(wf_b.allowed_actions()["open_editor"])

    def test_02_editor_save_confirms_edit(self):
        wf = ProjectWorkflow(state=WorkflowState.EDITOR_READY, duration=10.0)
        self.assertTrue(wf.transition_to(WorkflowState.EDIT_CONFIRMED))
        self.assertEqual(wf.state, WorkflowState.EDIT_CONFIRMED)
        self.assertTrue(wf.allowed_actions()["create_short"])
        self.assertFalse(wf.allowed_actions()["publish"])

    def test_03_publish_guard_blocks_unready_shorts(self):
        # In EDIT_CONFIRMED, publishing is blocked
        wf = ProjectWorkflow(state=WorkflowState.EDIT_CONFIRMED, duration=20.0)
        self.assertFalse(wf.allowed_actions()["publish"])

        # Only in SHORT_READY does publishing unlock
        wf.transition_to(WorkflowState.SHORT_READY)
        self.assertTrue(wf.allowed_actions()["publish"])


if __name__ == "__main__":
    unittest.main()
