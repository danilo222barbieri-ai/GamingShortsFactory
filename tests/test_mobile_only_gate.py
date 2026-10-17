"""GSF_MOBILE_ONLY_V419 — GSF is a phone app; desktop and tablets get the mobile-only page.

Static contracts always run. The behavioural check renders the real nginx
template against a stub Streamlit backend and runs when an nginx binary exists
(GitHub ubuntu runners ship one).
"""

from __future__ import annotations

import http.server
import os
import re
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
NGINX = (WEB / "nginx.conf.template").read_text(encoding="utf-8")
GATE = (WEB / "mobile_only_gate.html").read_text(encoding="utf-8")
BRIDGE = (WEB / "install_adsense_bridge.py").read_text(encoding="utf-8")

IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/19.0 Mobile/15E148 Safari/604.1"
ANDROID_PHONE = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Mobile Safari/537.36"
DESKTOP_CHROME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
DESKTOP_SAFARI = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/19.0 Safari/605.1.15"
IPAD_LEGACY = "Mozilla/5.0 (iPad; CPU OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/19.0 Mobile/15E148 Safari/604.1"
ANDROID_TABLET = "Mozilla/5.0 (Linux; Android 15; SM-X910) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"


def _location_block(name: str) -> str:
    start = NGINX.index(name)
    depth, i = 0, NGINX.index("{", start)
    while True:
        if NGINX[i] == "{":
            depth += 1
        elif NGINX[i] == "}":
            depth -= 1
            if depth == 0:
                return NGINX[start : i + 1]
        i += 1


class StaticContracts(unittest.TestCase):
    def test_root_and_catch_all_gate_non_phones_after_oauth(self):
        for name in ("    location = / {", "    location / {"):
            block = _location_block(name)
            self.assertIn("error_page 424 = /__gsf_mobile_gate;", block, name)
            self.assertRegex(block, r"if \(\$gsf_mobile_client = 0\) \{\s*return 424;\s*\}", name)
            self.assertNotIn("V407_DESKTOP_ACCESS", block, name)
        root = _location_block("    location = / {")
        gate_at = root.index("return 424;")
        for prefix in ("gsfsc_", "gsfyt_", "gsfig_", "gsfacg_", "gsfacf_", "gsfact_"):
            self.assertLess(root.index(prefix), gate_at, f"OAuth {prefix} must be routed before the gate")

    def test_gate_location_is_internal_and_uncached(self):
        block = _location_block("    location = /__gsf_mobile_gate {")
        self.assertIn("internal;", block)
        self.assertIn("alias /app/web/mobile_only_gate.html;", block)
        self.assertIn('Cache-Control "no-store, max-age=0" always', block)

    def test_phone_detection_excludes_tablets(self):
        self.assertIn('"~*(ipad|tablet|kindle|silk/|playbook)" 0;', NGINX)
        self.assertLess(NGINX.index('"~*(ipad|tablet'), NGINX.index('"~*(iphone|ipod|android.+mobile'))

    def test_gate_page_contract(self):
        self.assertIn("GSF_MOBILE_ONLY_GATE_V419", GATE)
        self.assertIn("solo su smartphone", GATE)
        self.assertIn('href="/privacy"', GATE)
        self.assertIn('href="/terms"', GATE)
        self.assertIn('id="copy"', GATE)
        self.assertIn("Kazuhiko Arase", GATE)  # MIT notice for the inlined QR encoder
        self.assertNotRegex(GATE, r"<script[^>]+src=", "the gate page must be self-contained")
        self.assertNotIn("Streamlit", GATE)

    def test_desktop_frame_is_gone(self):
        self.assertFalse((WEB / "gsf_desktop_shell_v407.py").exists())
        self.assertNotIn("gsf_desktop_shell_v407", BRIDGE)
        self.assertNotIn("gsf-desktop-ad", BRIDGE)
        self.assertIn('id="gsf-adsense-bridge"', BRIDGE)


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class _Stub(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        body = b"<!doctype html><title>Streamlit</title>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@unittest.skipUnless(shutil.which("nginx"), "nginx binary not available")
class BehaviourWithRealNginx(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="gsf-gate-"))
        cls.port, cls.backend = _free_port(), _free_port()
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", cls.backend), _Stub)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        server = (
            NGINX.replace("${PORT}", str(cls.port))
            .replace("127.0.0.1:8501", f"127.0.0.1:{cls.backend}")
            .replace("/app/web/", str(WEB) + "/")
        )
        (cls.tmp / "nginx.conf").write_text(
            "worker_processes 1; daemon off; pid %s/nginx.pid; error_log %s/error.log;\n"
            "events {}\nhttp { include /etc/nginx/mime.types; access_log off;\n"
            "client_body_temp_path %s; proxy_temp_path %s; fastcgi_temp_path %s; uwsgi_temp_path %s; scgi_temp_path %s;\n%s\n}\n"
            % ((cls.tmp,) * 7 + (server,)),
            encoding="utf-8",
        )
        cls.proc = subprocess.Popen(["nginx", "-c", str(cls.tmp / "nginx.conf"), "-p", str(cls.tmp)], stderr=subprocess.PIPE)
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", cls.port), 0.2).close()
                break
            except OSError:
                if cls.proc.poll() is not None:
                    raise RuntimeError(cls.proc.stderr.read().decode())
                time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait(5)
        cls.server.shutdown()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def get(self, path, ua, extra=None):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", headers={"User-Agent": ua, **(extra or {})})
        opener = urllib.request.build_opener(_NoRedirect)
        try:
            r = opener.open(req, timeout=5)
        except urllib.error.HTTPError as e:
            r = e
        with r:
            return r.status, r.headers, r.read()

    def test_phones_get_the_app(self):
        for ua in (IPHONE, ANDROID_PHONE):
            status, _, body = self.get("/", ua)
            self.assertEqual(status, 200, ua)
            self.assertIn(b"Streamlit", body, ua)
        status, _, body = self.get("/", DESKTOP_CHROME, {"Sec-CH-UA-Mobile": "?1"})
        self.assertIn(b"Streamlit", body)

    def test_desktop_and_tablets_get_the_gate(self):
        for ua in (DESKTOP_CHROME, DESKTOP_SAFARI, IPAD_LEGACY, ANDROID_TABLET, "curl/8.5"):
            for path in ("/", "/?gsf_hub=social", "/some/streamlit/page"):
                status, headers, body = self.get(path, ua)
                self.assertEqual(status, 200, (ua, path))
                self.assertIn(b"GSF_MOBILE_ONLY_GATE_V419", body, (ua, path))
                self.assertIn("no-store", headers.get("Cache-Control", ""), (ua, path))

    def test_legal_pages_stay_public_on_desktop(self):
        for path in ("/privacy", "/terms"):
            status, _, body = self.get(path, DESKTOP_CHROME)
            self.assertEqual(status, 200, path)
            self.assertNotIn(b"GSF_MOBILE_ONLY_GATE_V419", body, path)

    def test_gate_is_not_directly_addressable(self):
        status, _, _ = self.get("/__gsf_mobile_gate", IPHONE)
        self.assertEqual(status, 404)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


if __name__ == "__main__":
    unittest.main()
