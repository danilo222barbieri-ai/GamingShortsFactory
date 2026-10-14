#!/usr/bin/env python3
"""Production-path contract for V407 desktop-as-mobile shell."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
if str(WEB) not in sys.path:
    sys.path.insert(0, str(WEB))

from gsf_desktop_shell_v407 import DesktopShellConfig, build_desktop_shell_html

INSTALLER = WEB / "install_adsense_bridge.py"
DOCKERFILE = ROOT / "Dockerfile"
LEGACY_V267_GATE = WEB / "test_v267_global_desktop_polish.py"


class V407ProductionPathTests(unittest.TestCase):
    def setUp(self):
        self.cfg = DesktopShellConfig()
        self.html = build_desktop_shell_html(self.cfg)
        self.installer = INSTALLER.read_text(encoding="utf-8")
        self.dockerfile = DOCKERFILE.read_text(encoding="utf-8")
        self.legacy_v267_gate = LEGACY_V267_GATE.read_text(encoding="utf-8")

    def test_desktop_is_one_phone_canvas_not_a_second_app(self):
        self.assertEqual(self.cfg.center_width_px, 480)
        self.assertIn("@media (min-width:1100px)", self.html)
        self.assertIn("max-width:var(--gsf-mobile-canvas)!important", self.html)
        self.assertIn("width:var(--gsf-mobile-canvas)!important", self.html)
        self.assertNotIn("<iframe", self.html.lower())
        self.assertNotIn("desktop_app", self.html.lower())

    def test_native_streamlit_rows_stack_like_mobile_on_desktop(self):
        self.assertIn('[data-testid="stHorizontalBlock"]', self.html)
        self.assertIn("flex-direction:column!important", self.html)
        self.assertIn('[data-testid="column"]', self.html)
        self.assertIn("flex:1 1 100%!important", self.html)

    def test_two_giant_ad_rails_use_available_desktop_space(self):
        self.assertEqual(self.cfg.rail_max_px, 460)
        self.assertIn("--gsf-rail-max:460px", self.html)
        self.assertIn("height:calc(100vh - 40px)", self.html)
        self.assertIn('id="gsf-desktop-ad-left"', self.html)
        self.assertIn('id="gsf-desktop-ad-right"', self.html)

    def test_mobile_and_tablet_are_not_reformatted(self):
        before_desktop = self.html.split("@media (min-width:1100px)", 1)[0]
        self.assertIn(".gsf-desktop-ad-rail{display:none}", before_desktop)
        self.assertNotIn("max-width:var(--gsf-mobile-canvas)", before_desktop)
        self.assertNotIn("flex-direction:column!important", before_desktop)

    def test_existing_adsense_bridge_creates_v407_rails_from_live_slots(self):
        self.assertIn("V407", self.installer)
        self.assertIn("build_desktop_shell_html", self.installer)
        self.assertIn('createRail("gsf-desktop-ad-left"', self.installer)
        self.assertIn('createRail("gsf-desktop-ad-right"', self.installer)
        self.assertIn("gsf-v1057-live", self.installer)
        self.assertIn("gsf-v1057-ad-mount", self.installer)
        self.assertIn("gsf-v407-rail-ad", self.installer)

    def test_desktop_shell_keeps_mobile_inline_ad_slots_intact(self):
        self.assertNotIn("gsf-v407-desktop-ad-policy", self.installer)
        self.assertNotIn(".gsf-v1057-live:not(.gsf-v407-rail-ad){display:none!important}", self.installer)

    def test_preview_mode_gets_giant_rails_but_off_mode_does_not_fake_ads(self):
        self.assertIn("function createPreviewRail", self.installer)
        self.assertIn('.gsf-v1057-ad:not(.gsf-v1057-live)', self.installer)
        self.assertIn("getComputedStyle(node).display!==\"none\"", self.installer)
        self.assertIn('createPreviewRail("gsf-desktop-ad-left"', self.installer)
        self.assertIn('createPreviewRail("gsf-desktop-ad-right"', self.installer)
        self.assertIn("removeDesktopRails", self.installer)

    def test_global_chrome_and_overlays_share_the_mobile_canvas(self):
        self.assertIn("#gsf-global-header,#gsf-global-gamebar,#gsf-global-footer", self.html)
        self.assertIn("#gsf-creator-hub-live-v160", self.html)
        self.assertIn("#gsf-editor-overlay-v220", self.html)
        self.assertIn("left:calc(50% - 240px)!important", self.html)
        self.assertIn('html body [data-testid="stMainBlockContainer"]', self.html)

    def test_docker_build_already_installs_the_browser_bridge(self):
        self.assertIn("python /app/web/install_adsense_bridge.py", self.dockerfile)
        self.assertIn("COPY web /app/web", self.dockerfile)

    def test_bridge_installer_is_valid_python(self):
        compile(self.installer, str(INSTALLER), "exec")


if __name__ == "__main__":
    unittest.main()

