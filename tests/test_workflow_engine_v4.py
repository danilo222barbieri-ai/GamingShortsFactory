import unittest
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from web.workflow_engine_v4 import (
    WorkflowState,
    WorkflowPath,
    ProjectWorkflow,
    determine_path,
    load_workflow,
    save_workflow,
)


class TestWorkflowEngineV4(unittest.TestCase):

    def test_01_determine_path_threshold(self):
        self.assertEqual(determine_path(None), WorkflowPath.PERCORSO_A)
        self.assertEqual(determine_path(15.0), WorkflowPath.PERCORSO_A)
        self.assertEqual(determine_path(30.0), WorkflowPath.PERCORSO_A)
        self.assertEqual(determine_path(14.9), WorkflowPath.PERCORSO_B)
        self.assertEqual(determine_path(10.0), WorkflowPath.PERCORSO_B)
        self.assertEqual(determine_path(5.0), WorkflowPath.PERCORSO_B)

    def test_02_empty_state_allowed_and_blocked(self):
        wf = ProjectWorkflow(state=WorkflowState.EMPTY)
        allowed = wf.allowed_actions()
        self.assertTrue(allowed["upload"])
        self.assertTrue(allowed["creator_hub"])
        self.assertFalse(allowed["find_moments"])
        self.assertFalse(allowed["select_moment"])
        self.assertFalse(allowed["open_editor"])
        self.assertFalse(allowed["create_short"])
        self.assertFalse(allowed["publish"])

    def test_03_percorso_a_full_progression(self):
        wf = ProjectWorkflow(state=WorkflowState.EMPTY, duration=30.0)
        self.assertEqual(wf.path, WorkflowPath.PERCORSO_A)

        # Upload step
        self.assertTrue(wf.transition_to(WorkflowState.UPLOADING))
        self.assertTrue(wf.transition_to(WorkflowState.UPLOADED, source_path="/path/test.mp4"))
        self.assertEqual(wf.state, WorkflowState.UPLOADED)

        # Trying to skip directly to editor must fail
        ok, reason = wf.validate_transition(WorkflowState.EDITOR_READY)
        self.assertFalse(ok)
        self.assertIn("Completa l'analisi IA", reason)

        # AI analysis
        self.assertTrue(wf.transition_to(WorkflowState.ANALYZING))
        self.assertTrue(wf.transition_to(WorkflowState.MOMENTS_READY))

        # Trying to open editor without selecting a moment must fail
        ok, reason = wf.validate_transition(WorkflowState.EDITOR_READY)
        self.assertFalse(ok)
        self.assertIn("Seleziona uno dei tre momenti", reason)

        # Moment selection
        self.assertTrue(wf.transition_to(WorkflowState.MOMENT_SELECTED, moment_selected=1, clip_start=8.5, clip_duration=15.0))
        allowed = wf.allowed_actions()
        self.assertTrue(allowed["open_editor"])
        self.assertFalse(allowed["create_short"])

        # Editor flow
        self.assertTrue(wf.transition_to(WorkflowState.EDITOR_READY))
        self.assertTrue(wf.transition_to(WorkflowState.EDITING))

        # Trying to jump to create short without confirming edit must fail
        ok, reason = wf.validate_transition(WorkflowState.SHORT_READY)
        self.assertFalse(ok)
        self.assertIn("Conferma il montaggio", reason)

        # Confirm edit
        self.assertTrue(wf.transition_to(WorkflowState.EDIT_CONFIRMED))
        allowed = wf.allowed_actions()
        self.assertTrue(allowed["create_short"])
        self.assertFalse(allowed["publish"])

        # Short creation & ready
        self.assertTrue(wf.transition_to(WorkflowState.SHORT_CREATING))
        self.assertTrue(wf.transition_to(WorkflowState.SHORT_READY, final_video_path="/path/short.mp4"))
        allowed = wf.allowed_actions()
        self.assertTrue(allowed["publish"])
        self.assertTrue(allowed["export"])

        # Export & publish
        self.assertTrue(wf.transition_to(WorkflowState.PUBLISHED))

    def test_04_percorso_b_video_under_15s_direct_to_editor(self):
        wf = ProjectWorkflow(state=WorkflowState.EMPTY, duration=10.0)
        self.assertEqual(wf.path, WorkflowPath.PERCORSO_B)

        self.assertTrue(wf.transition_to(WorkflowState.UPLOADING))
        self.assertTrue(wf.transition_to(WorkflowState.UPLOADED, source_path="/path/quick.mp4"))
        # In Percorso B, UPLOADED auto-routes to EDITOR_READY
        self.assertEqual(wf.state, WorkflowState.EDITOR_READY)

        # AI analysis must be forbidden in Percorso B
        ok, reason = wf.validate_transition(WorkflowState.ANALYZING)
        self.assertFalse(ok)
        self.assertIn("inferiori a 15 secondi", reason)

        allowed = wf.allowed_actions()
        self.assertTrue(allowed["open_editor"])
        self.assertFalse(allowed["find_moments"])
        self.assertFalse(allowed["create_short"])

        # Confirm edit and finish
        self.assertTrue(wf.transition_to(WorkflowState.EDIT_CONFIRMED))
        self.assertTrue(wf.transition_to(WorkflowState.SHORT_READY, final_video_path="/path/short_b.mp4"))
        self.assertTrue(wf.allowed_actions()["publish"])

    def test_05_creator_hub_always_accessible(self):
        for state in WorkflowState:
            wf = ProjectWorkflow(state=state, duration=20.0)
            self.assertTrue(wf.allowed_actions()["creator_hub"], f"Creator Hub must be accessible in state {state}")

    def test_06_workflow_persistence(self):
        with tempfile.TemporaryDirectory() as td:
            session_dir = Path(td)
            wf1 = ProjectWorkflow(
                project_id="prj_123",
                state=WorkflowState.MOMENT_SELECTED,
                duration=30.0,
                source_path="/videos/game.mp4",
                moment_selected=0,
                clip_start=12.0,
                clip_duration=15.0,
            )
            saved_file = save_workflow(session_dir, wf1)
            self.assertTrue(saved_file.is_file())

            wf2 = load_workflow(session_dir)
            self.assertEqual(wf2.project_id, "prj_123")
            self.assertEqual(wf2.state, WorkflowState.MOMENT_SELECTED)
            self.assertEqual(wf2.duration, 30.0)
            self.assertEqual(wf2.moment_selected, 0)
            self.assertEqual(wf2.clip_start, 12.0)
            self.assertTrue(wf2.allowed_actions()["open_editor"])


if __name__ == "__main__":
    unittest.main()
