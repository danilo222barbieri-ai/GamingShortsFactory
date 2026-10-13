#!/usr/bin/env python3
"""V403 public runtime migrator.

The historical/core flow patch stays frozen in apply_v403_flow_core. This
wrapper re-exports its pure patch helpers for tests and, when executed by
start_web.sh, applies the final V403 refinements in production order.
"""
from __future__ import annotations

from pathlib import Path
import py_compile
import sys

from apply_v403_flow_core import *  # noqa: F401,F403
from apply_v403_flow_core import main as _core_main
from fix_v403_profile_recovery import patch_text as _patch_profile_text
from fix_v403_resume_handoff import patch_hub_text as _patch_hub_resume_text, patch_app_text as _patch_editor_handoff_text
from fix_v403_surface_collisions import patch_ai_text as _patch_surface_ai_text, patch_share_text as _patch_surface_share_text

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path("/app")
HUB = ROOT / "web/creator_hub_v156_component/index.html"
APP = ROOT / "GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py"
AI = ROOT / "web/ai_v221_component/index.html"
SHARE = ROOT / "web/share_v156_component/index.html"


def _rewrite(path: Path, fn, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"V403 missing {label}: {path}")
    before = path.read_text(encoding="utf-8")
    after = fn(before)
    path.write_text(after, encoding="utf-8")
    print(f"V403 final {label} changed={before != after}", flush=True)


def main() -> None:
    _core_main()
    # Creator Hub: preserve last valid payload first, then replace foreground
    # startup with the single-flight resume owner.
    _rewrite(HUB, _patch_profile_text, "profile recovery")
    _rewrite(HUB, _patch_hub_resume_text, "Creator Hub resume")
    # Editor handoff must see the core V403 browser bridge before patching it.
    _rewrite(APP, _patch_editor_handoff_text, "selected-moment Editor handoff")
    # Historical V319/V320/V396 DOM remains for boot compatibility, but V403
    # becomes the final visible owner after those gates have passed.
    _rewrite(AI, _patch_surface_ai_text, "Motori result retirement")
    _rewrite(SHARE, _patch_surface_share_text, "Crea Short mobile ownership")
    py_compile.compile(str(APP), doraise=True)
    print("V403 FINAL RUNTIME: PASS", flush=True)


if __name__ == "__main__":
    main()
