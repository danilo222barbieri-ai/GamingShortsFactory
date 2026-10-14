import unittest

from gsf_editor_v403 import (
    apply_director_suggestion,
    default_editor_state,
    game_director_suggestions,
    normalize_editor_state,
    normalize_timeline_markers,
    push_history,
    redo_state,
    undo_state,
)


class GameEditorV403StateTests(unittest.TestCase):
    def test_default_state_is_vertical_non_destructive_and_short_friendly(self):
        state = default_editor_state(42.0, preferred_duration=15.0)
        self.assertEqual(state["format"], "9:16 Short")
        self.assertEqual(state["start"], 0.0)
        self.assertEqual(state["end"], 15.0)
        self.assertEqual(state["active_tool"], "FRAME")
        self.assertTrue(state["safe_zones"])
        self.assertFalse(state["focus_mode"])
        self.assertEqual(state["compare_mode"], "EDITED")
        self.assertEqual(state["source_duration"], 42.0)

    def test_normalize_clamps_edit_decisions_without_mutating_input(self):
        raw = {
            "start": -10,
            "end": 90,
            "zoom": 9,
            "x": -400,
            "y": 300,
            "volume": 500,
            "speed": 9,
            "brightness": 2,
            "contrast": -2,
            "active_tool": "NOPE",
        }
        normalized = normalize_editor_state(raw, 30.0)
        self.assertEqual(raw["start"], -10)
        self.assertEqual(normalized["start"], 0.0)
        self.assertEqual(normalized["end"], 30.0)
        self.assertEqual(normalized["zoom"], 2.0)
        self.assertEqual(normalized["x"], -100)
        self.assertEqual(normalized["y"], 100)
        self.assertEqual(normalized["volume"], 200)
        self.assertEqual(normalized["speed"], 2.0)
        self.assertEqual(normalized["brightness"], 0.3)
        self.assertEqual(normalized["contrast"], 0.7)
        self.assertEqual(normalized["active_tool"], "FRAME")

    def test_history_deduplicates_and_undo_redo_round_trip(self):
        a = default_editor_state(30.0)
        b = dict(a, zoom=1.25)
        past = push_history([], a)
        past = push_history(past, a)
        self.assertEqual(len(past), 1)
        restored, past_after, future = undo_state(past, b, [])
        self.assertEqual(restored["zoom"], 1.0)
        self.assertEqual(past_after, [])
        redone, past_final, future_final = redo_state(past_after, restored, future)
        self.assertEqual(redone["zoom"], 1.25)
        self.assertEqual(len(past_final), 1)
        self.assertEqual(future_final, [])


class GameEditorV403TimelineTests(unittest.TestCase):
    def test_markers_are_filtered_sorted_and_positioned_inside_selected_scene(self):
        markers = normalize_timeline_markers(
            [
                {"time": 13.0, "type": "kill", "score": 0.9},
                {"time": 11.0, "type": "action_peak", "label": "Peak", "score": 1.0},
                {"time": 50.0, "type": "speech"},
                {"time": "bad", "type": "aim"},
            ],
            clip_start=10.0,
            clip_end=20.0,
        )
        self.assertEqual([m["type"] for m in markers], ["ACTION_PEAK", "KILL"])
        self.assertAlmostEqual(markers[0]["position_pct"], 10.0)
        self.assertAlmostEqual(markers[1]["position_pct"], 30.0)
        self.assertEqual(markers[0]["label"], "Peak")


class GameEditorV403DirectorTests(unittest.TestCase):
    def test_director_returns_specific_actionable_patches(self):
        state = default_editor_state(30.0)
        state.update({"start": 0.0, "end": 15.0, "subtitle_y": 91, "volume": 70, "zoom": 1.0})
        markers = normalize_timeline_markers(
            [{"time": 2.2, "type": "action_peak", "score": 1.0}],
            0.0,
            15.0,
        )
        suggestions = game_director_suggestions(state, markers)
        ids = {item["id"] for item in suggestions}
        self.assertIn("tighten_hook", ids)
        self.assertIn("caption_safe_zone", ids)
        self.assertIn("lift_game_audio", ids)
        self.assertIn("action_reframe", ids)
        for suggestion in suggestions:
            self.assertTrue(suggestion["patch"])
            self.assertIn(suggestion["category"], {"FRAME", "CAPTION", "AUDIO", "AI"})

    def test_apply_suggestion_is_non_destructive_and_normalized(self):
        state = default_editor_state(30.0)
        suggestion = {"patch": {"zoom": 1.15, "x": 12, "safe_zones": True}}
        changed = apply_director_suggestion(state, suggestion, 30.0)
        self.assertEqual(state["zoom"], 1.0)
        self.assertEqual(changed["zoom"], 1.15)
        self.assertEqual(changed["x"], 12)
        self.assertTrue(changed["safe_zones"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
