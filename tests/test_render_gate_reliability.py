"""Nested rendering stages share one slot; independent jobs stay serialized."""
import importlib.util
from pathlib import Path
import threading
import unittest
from unittest.mock import patch


class RenderGateReliability(unittest.TestCase):
    def gate(self):
        spec = importlib.util.spec_from_file_location('isolated_render_gate', Path(__file__).resolve().parents[1]/'web/render_gate_v293.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_nested_postprocessing_does_not_deadlock(self):
        gate=self.gate()
        completed=threading.Event()
        def render():
            with gate.render_slot('final'):
                with gate.render_slot('cinematic'):
                    self.assertEqual(gate._ACTIVE, 1)
            completed.set()
        worker=threading.Thread(target=render,daemon=True)
        worker.start()
        self.assertTrue(completed.wait(.5), 'nested pipeline deadlocked on its own render slot')
        self.assertEqual(gate._ACTIVE,0)

    def test_busy_queue_fails_within_deadline(self):
        gate=self.gate()
        gate._RENDER_GATE.acquire()
        try:
            with patch.dict('os.environ', {'GSF_RENDER_QUEUE_TIMEOUT': '.05'}):
                with self.assertRaisesRegex(TimeoutError, 'Render occupato'):
                    with gate.render_slot():
                        self.fail('unavailable slot acquired')
            self.assertEqual(gate._ACTIVE,0)
        finally:
            gate._RENDER_GATE.release()

    def test_exception_releases_slot_and_other_threads_wait(self):
        gate=self.gate()
        entered=threading.Event()
        def competing():
            with gate.render_slot('other'):
                entered.set()
        try:
            with gate.render_slot('final'):
                worker=threading.Thread(target=competing,daemon=True)
                worker.start()
                self.assertFalse(entered.wait(.05))
                with gate.render_slot('audio'):
                    raise ValueError('failed effect')
        except ValueError:
            pass
        self.assertTrue(entered.wait(.5))
        worker.join(.5)
        self.assertEqual(gate._ACTIVE,0)
