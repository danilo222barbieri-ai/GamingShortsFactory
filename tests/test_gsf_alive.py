import unittest
from dataclasses import replace

from gsf_alive import (
    AliveEvent,
    AliveEventType,
    AliveMode,
    AliveState,
    SystemHealth,
    alive_motion_profile,
    build_alive_css,
    reduce_alive,
    suggest_next_action,
    sync_alive_from_session,
    emit_alive,
    SESSION_KEY,
)


class AliveCoreTests(unittest.TestCase):
    def test_initial_state_is_calm_and_points_to_upload(self):
        state = AliveState()
        self.assertEqual(state.mode, AliveMode.IDLE)
        self.assertEqual(suggest_next_action(state), "upload")
        self.assertEqual(state.message, "Pronto quando vuoi.")

    def test_upload_moves_from_working_to_active(self):
        state = reduce_alive(AliveState(), AliveEvent(AliveEventType.UPLOAD_STARTED))
        self.assertEqual(state.mode, AliveMode.WORKING)
        self.assertEqual(state.active_job, "upload")
        self.assertEqual(state.message, "Carico il gameplay.")

        state = reduce_alive(state, AliveEvent(AliveEventType.UPLOAD_PROGRESS, {"progress": 0.42}))
        self.assertAlmostEqual(state.progress, 0.42)

        state = reduce_alive(state, AliveEvent(AliveEventType.UPLOAD_COMPLETED))
        self.assertEqual(state.mode, AliveMode.ACTIVE)
        self.assertTrue(state.video_ready)
        self.assertIsNone(state.active_job)
        self.assertEqual(suggest_next_action(state), "create_with_ai")

    def test_ai_moments_and_selection_drive_next_action(self):
        state = replace(AliveState(), video_ready=True, mode=AliveMode.ACTIVE)
        state = reduce_alive(state, AliveEvent(AliveEventType.AI_STARTED))
        self.assertEqual(state.mode, AliveMode.WORKING)
        self.assertEqual(state.message, "Vediamo cosa c’è dentro.")

        state = reduce_alive(state, AliveEvent(AliveEventType.AI_MOMENTS_FOUND, {"count": 3}))
        self.assertEqual(state.mode, AliveMode.ACTIVE)
        self.assertEqual(state.moments_count, 3)
        self.assertEqual(state.message, "Ho trovato 3 momenti forti.")
        self.assertEqual(suggest_next_action(state), "choose_moment")

        state = reduce_alive(state, AliveEvent(AliveEventType.MOMENT_SELECTED, {"index": 1}))
        self.assertTrue(state.moment_selected)
        self.assertEqual(state.message, "Questa merita attenzione.")
        self.assertEqual(suggest_next_action(state), "create_short")

    def test_render_completion_celebrates_and_prioritizes_publish(self):
        state = replace(AliveState(), video_ready=True, moment_selected=True, mode=AliveMode.ACTIVE)
        state = reduce_alive(state, AliveEvent(AliveEventType.RENDER_STARTED))
        self.assertEqual(state.mode, AliveMode.WORKING)
        self.assertEqual(state.active_job, "render")
        self.assertEqual(state.message, "Ci sto lavorando.")

        state = reduce_alive(state, AliveEvent(AliveEventType.RENDER_COMPLETED))
        self.assertEqual(state.mode, AliveMode.CELEBRATE)
        self.assertTrue(state.short_ready)
        self.assertEqual(state.message, "È pronto.")
        self.assertEqual(suggest_next_action(state), "publish")

    def test_error_and_recovery_are_explicit(self):
        state = reduce_alive(AliveState(), AliveEvent(AliveEventType.FAILURE, {"message": "Render fermo."}))
        self.assertEqual(state.mode, AliveMode.ERROR)
        self.assertEqual(state.message, "Render fermo.")
        self.assertEqual(suggest_next_action(state), "retry")

        state = reduce_alive(state, AliveEvent(AliveEventType.RECOVERED))
        self.assertNotEqual(state.mode, AliveMode.ERROR)
        self.assertIsNone(state.error)

    def test_degraded_health_is_calm_not_alarmist(self):
        state = reduce_alive(
            AliveState(),
            AliveEvent(AliveEventType.SYSTEM_HEALTH_CHANGED, {"health": "degraded"}),
        )
        self.assertEqual(state.system_health, SystemHealth.DEGRADED)
        self.assertEqual(state.message, "Coda un po’ più lunga del solito.")
        self.assertNotEqual(state.mode, AliveMode.ERROR)

    def test_motion_profile_changes_with_mode(self):
        idle = alive_motion_profile(AliveState())
        working = alive_motion_profile(replace(AliveState(), mode=AliveMode.WORKING, progress=0.5))
        celebrate = alive_motion_profile(replace(AliveState(), mode=AliveMode.CELEBRATE))
        self.assertGreater(idle["duration_s"], working["duration_s"])
        self.assertGreater(celebrate["scale"], idle["scale"])

    def test_css_exposes_alive_variables_and_respects_reduced_motion(self):
        css = build_alive_css(replace(AliveState(), mode=AliveMode.WORKING, progress=0.5))
        self.assertIn("--gsf-alive-duration", css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)
        self.assertIn("[data-gsf-alive-orb]", css)

    def test_session_bridge_observes_existing_app_state_without_overwriting_it(self):
        session = {
            "current_page": "home",
            "video_path": "/tmp/input.mp4",
            "rendering": True,
            "render_progress": 35,
        }
        state = sync_alive_from_session(session)
        self.assertTrue(state.video_ready)
        self.assertEqual(state.active_job, "render")
        self.assertAlmostEqual(state.progress, 0.35)
        self.assertEqual(session["video_path"], "/tmp/input.mp4")
        self.assertIn(SESSION_KEY, session)

    def test_explicit_events_round_trip_through_session_state(self):
        session = {}
        state = emit_alive(session, AliveEventType.UPLOAD_STARTED)
        self.assertEqual(state.active_job, "upload")
        state = emit_alive(session, AliveEventType.UPLOAD_COMPLETED)
        self.assertTrue(state.video_ready)
        self.assertEqual(session[SESSION_KEY]["mode"], "active")


if __name__ == "__main__":
    unittest.main()
