import importlib.util
import unittest

import gsf_project_state as ps


class ProjectStateContractTests(unittest.TestCase):
    def test_project_state_module_exists(self):
        self.assertIsNotNone(
            importlib.util.find_spec("gsf_project_state"),
            "gsf_project_state must exist as the durable project-state boundary",
        )

    def test_new_project_has_one_stable_durable_identity(self):
        self.assertTrue(hasattr(ps, "new_project"))
        self.assertTrue(hasattr(ps, "ProjectStage"))
        state = ps.new_project("project-42")
        self.assertEqual(state.project_id, "project-42")
        self.assertEqual(state.stage, ps.ProjectStage.EMPTY)
        self.assertIsNone(state.source_ref)
        self.assertIsNone(state.final_ref)

    def test_source_attachment_keeps_only_lightweight_reference(self):
        self.assertTrue(hasattr(ps, "ProjectEvent"))
        self.assertTrue(hasattr(ps, "ProjectEventType"))
        self.assertTrue(hasattr(ps, "reduce_project"))
        state = ps.new_project("project-42")
        state = ps.reduce_project(
            state,
            ps.ProjectEvent(ps.ProjectEventType.SOURCE_ATTACHED, {"source_ref": "asset://source-1"}),
        )
        self.assertEqual(state.source_ref, "asset://source-1")
        self.assertEqual(state.stage, ps.ProjectStage.SOURCE_READY)
        with self.assertRaises(TypeError):
            ps.reduce_project(
                state,
                ps.ProjectEvent(ps.ProjectEventType.SOURCE_ATTACHED, {"source_ref": b"video-bytes"}),
            )

    def test_ai_selection_editor_and_render_share_the_same_project(self):
        state = ps.new_project("project-42")
        state = ps.reduce_project(
            state,
            ps.ProjectEvent(ps.ProjectEventType.SOURCE_ATTACHED, {"source_ref": "asset://source-1"}),
        )
        state = ps.reduce_project(
            state,
            ps.ProjectEvent(
                ps.ProjectEventType.MOMENTS_FOUND,
                {"candidate_refs": ["moment://a", "moment://b", "moment://c"]},
            ),
        )
        self.assertEqual(state.stage, ps.ProjectStage.MOMENTS_READY)
        self.assertEqual(state.candidate_refs, ("moment://a", "moment://b", "moment://c"))

        state = ps.reduce_project(
            state,
            ps.ProjectEvent(ps.ProjectEventType.MOMENT_SELECTED, {"candidate_ref": "moment://b"}),
        )
        self.assertEqual(state.selected_candidate_ref, "moment://b")

        state = ps.reduce_project(state, ps.ProjectEvent(ps.ProjectEventType.EDIT_SAVED))
        self.assertEqual(state.stage, ps.ProjectStage.EDITING)
        self.assertEqual(state.edit_revision, 1)
        self.assertEqual(state.source_ref, "asset://source-1")

        state = ps.reduce_project(
            state,
            ps.ProjectEvent(ps.ProjectEventType.RENDER_STARTED, {"job_id": "render-9"}),
        )
        self.assertEqual(state.stage, ps.ProjectStage.RENDERING)
        self.assertEqual(state.render_job_id, "render-9")

        state = ps.reduce_project(
            state,
            ps.ProjectEvent(ps.ProjectEventType.RENDER_COMPLETED, {"final_ref": "asset://short-9"}),
        )
        self.assertEqual(state.stage, ps.ProjectStage.READY)
        self.assertEqual(state.final_ref, "asset://short-9")
        self.assertIsNone(state.render_job_id)

    def test_publish_is_additive_and_does_not_destroy_edit_state(self):
        state = ps.new_project("project-42")
        for event in (
            ps.ProjectEvent(ps.ProjectEventType.SOURCE_ATTACHED, {"source_ref": "asset://source-1"}),
            ps.ProjectEvent(ps.ProjectEventType.MOMENTS_FOUND, {"candidate_refs": ["moment://a"]}),
            ps.ProjectEvent(ps.ProjectEventType.MOMENT_SELECTED, {"candidate_ref": "moment://a"}),
            ps.ProjectEvent(ps.ProjectEventType.EDIT_SAVED),
            ps.ProjectEvent(ps.ProjectEventType.RENDER_COMPLETED, {"final_ref": "asset://short-9"}),
            ps.ProjectEvent(ps.ProjectEventType.PUBLISHED, {"target": "youtube"}),
            ps.ProjectEvent(ps.ProjectEventType.PUBLISHED, {"target": "tiktok"}),
        ):
            state = ps.reduce_project(state, event)
        self.assertEqual(state.stage, ps.ProjectStage.PUBLISHED)
        self.assertEqual(state.published_targets, ("youtube", "tiktok"))
        self.assertEqual(state.edit_revision, 1)
        self.assertEqual(state.final_ref, "asset://short-9")

    def test_state_round_trips_as_json_safe_data(self):
        self.assertTrue(hasattr(ps, "ProjectState"))
        state = ps.new_project("project-42")
        state = ps.reduce_project(
            state,
            ps.ProjectEvent(ps.ProjectEventType.SOURCE_ATTACHED, {"source_ref": "asset://source-1"}),
        )
        raw = state.to_dict()
        self.assertEqual(raw["stage"], "source_ready")
        restored = ps.ProjectState.from_dict({**raw, "future_field": "ignored"})
        self.assertEqual(restored, state)

    def test_session_bridge_preserves_unrelated_app_state(self):
        self.assertTrue(hasattr(ps, "PROJECT_SESSION_KEY"))
        self.assertTrue(hasattr(ps, "load_project_session"))
        self.assertTrue(hasattr(ps, "save_project_session"))
        session = {"current_page": "editor", "video_path": "/tmp/legacy.mp4"}
        state = ps.load_project_session(session, project_id="project-42")
        state = ps.reduce_project(
            state,
            ps.ProjectEvent(ps.ProjectEventType.SOURCE_ATTACHED, {"source_ref": "asset://source-1"}),
        )
        ps.save_project_session(session, state)
        self.assertEqual(session["current_page"], "editor")
        self.assertEqual(session["video_path"], "/tmp/legacy.mp4")
        self.assertEqual(session[ps.PROJECT_SESSION_KEY]["project_id"], "project-42")
        self.assertEqual(session[ps.PROJECT_SESSION_KEY]["source_ref"], "asset://source-1")


if __name__ == "__main__":
    unittest.main()
