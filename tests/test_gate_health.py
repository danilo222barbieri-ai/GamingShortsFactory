"""Real HTTP responses, including a socket that never sends a response."""
import importlib.util
import json
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class GateHealth(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'tools/gsf_gate_health.py'
        self.assertTrue(path.exists(), 'bounded composite-health checker must exist')
        spec = importlib.util.spec_from_file_location('gate_health', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.responses = []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                response = owner.responses.pop(0) if len(owner.responses) > 1 else owner.responses[0]
                if response == 'hang':
                    time.sleep(1)
                    return
                if response == 'drip':
                    self.send_response(200)
                    self.end_headers()
                    for _ in range(40):
                        try:
                            self.wfile.write(b' ')
                            self.wfile.flush()
                        except OSError:
                            break
                        time.sleep(.03)
                    return
                status, payload = response
                self.send_response(status)
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode())

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}/healthz'

    def tearDown(self):
        if hasattr(self, 'server'):
            self.server.shutdown()
            self.server.server_close()

    def wait(self, **kwargs):
        return self.module.wait_for_health(self.url, deadline_seconds=.35,
                                          request_timeout=.1, interval=.01, **kwargs)

    def test_waits_for_real_composite_readiness(self):
        self.responses = [(503, {'ok':False}), (200, {'ok':True,'companion':True,'streamlit':True})]
        self.assertTrue(self.wait()['ok'])

    def test_http_200_with_unhealthy_component_never_passes(self):
        self.responses = [(200, {'ok':True,'companion':True,'streamlit':False})]
        with self.assertRaises(TimeoutError):
            self.wait()

    def test_slow_body_is_bounded_by_total_deadline(self):
        self.responses = ['drip']
        started = time.monotonic()
        with self.assertRaises(TimeoutError):
            self.wait()
        self.assertLess(time.monotonic()-started, .8)

    def test_stalled_response_is_bounded_by_total_deadline(self):
        self.responses = ['hang']
        started = time.monotonic()
        with self.assertRaises(TimeoutError):
            self.wait()
        self.assertLess(time.monotonic() - started, .8)


if __name__ == '__main__':
    unittest.main()
