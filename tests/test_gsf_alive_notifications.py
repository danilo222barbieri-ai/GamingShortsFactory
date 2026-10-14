import unittest

from gsf_alive import AliveEvent, AliveEventType, AliveState, reduce_alive
from gsf_alive_notifications import (
    build_alive_notification_css,
    build_alive_notification_markup,
    pop_alive_notification,
    sync_alive_notification,
)


class AliveNotificationTests(unittest.TestCase):
    def test_upload_completed_emits_video_caricato_once(self):
        session = {}
        state = reduce_alive(AliveState(), AliveEvent(AliveEventType.UPLOAD_COMPLETED))

        sync_alive_notification(session, state)
        note = pop_alive_notification(session)

        self.assertIsNotNone(note)
        self.assertEqual(note.message, "Video caricato")
        self.assertEqual(note.kind, "success")
        self.assertIsNone(note.action)

        sync_alive_notification(session, state)
        self.assertIsNone(pop_alive_notification(session))

    def test_same_completion_can_notify_again_after_a_different_event(self):
        session = {}
        completed = reduce_alive(AliveState(), AliveEvent(AliveEventType.UPLOAD_COMPLETED))
        started = reduce_alive(completed, AliveEvent(AliveEventType.UPLOAD_STARTED))

        sync_alive_notification(session, completed)
        self.assertIsNotNone(pop_alive_notification(session))

        sync_alive_notification(session, started)
        self.assertIsNone(pop_alive_notification(session))

        completed_again = reduce_alive(started, AliveEvent(AliveEventType.UPLOAD_COMPLETED))
        sync_alive_notification(session, completed_again)
        self.assertEqual(pop_alive_notification(session).message, "Video caricato")

    def test_short_completed_points_to_publish_without_embedding_file_details(self):
        session = {}
        state = reduce_alive(AliveState(), AliveEvent(AliveEventType.RENDER_COMPLETED))

        sync_alive_notification(session, state)
        note = pop_alive_notification(session)

        self.assertEqual(note.message, "Short completato")
        self.assertEqual(note.action, "publish")
        self.assertNotIn(".mp4", note.message)

    def test_published_emits_short_pubblicato(self):
        session = {}
        state = reduce_alive(AliveState(), AliveEvent(AliveEventType.PUBLISHED))

        sync_alive_notification(session, state)
        note = pop_alive_notification(session)

        self.assertEqual(note.message, "Short pubblicato")
        self.assertEqual(note.kind, "success")

    def test_failure_uses_safe_alive_message(self):
        session = {}
        state = reduce_alive(
            AliveState(),
            AliveEvent(AliveEventType.FAILURE, {"message": "Il render si è fermato."}),
        )

        sync_alive_notification(session, state)
        note = pop_alive_notification(session)

        self.assertEqual(note.message, "Il render si è fermato.")
        self.assertEqual(note.kind, "error")
        self.assertEqual(note.action, "retry")

    def test_recovered_emits_calm_recovery_message(self):
        session = {}
        failed = reduce_alive(
            AliveState(),
            AliveEvent(AliveEventType.FAILURE, {"message": "Errore."}),
        )
        recovered = reduce_alive(failed, AliveEvent(AliveEventType.RECOVERED))

        sync_alive_notification(session, failed)
        pop_alive_notification(session)
        sync_alive_notification(session, recovered)
        note = pop_alive_notification(session)

        self.assertEqual(note.message, "Ci siamo.")
        self.assertEqual(note.kind, "info")

    def test_notification_css_is_fixed_above_game_bar_and_does_not_reflow(self):
        css = build_alive_notification_css()
        self.assertIn("position:fixed", css)
        self.assertIn("bottom:84px", css)
        self.assertIn("pointer-events:none", css)
        self.assertIn("@keyframes gsfAliveToast", css)

    def test_markup_is_compact_and_carries_action_metadata(self):
        session = {}
        state = reduce_alive(AliveState(), AliveEvent(AliveEventType.RENDER_COMPLETED))
        sync_alive_notification(session, state)
        note = pop_alive_notification(session)

        markup = build_alive_notification_markup(note)

        self.assertIn("gsf-alive-notification", markup)
        self.assertIn("data-alive-action='publish'", markup)
        self.assertIn("Short completato", markup)


if __name__ == "__main__":
    unittest.main()
