#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

WEB = Path("/app/web")
APP = Path("/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py")
HOME = WEB / "home_v154_component/index.html"
HUB = WEB / "creator_hub_v156_component/index.html"
AI = WEB / "ai_v221_component/index.html"
EDITOR = WEB / "editor_2027_component/index.html"
SHARE = WEB / "share_v156_component/index.html"
SERVER = WEB / "direct_upload_server.py"
NGINX = WEB / "nginx.conf.template"


def run(label: str, *args: str, timeout: int = 180) -> None:
    cmd = [sys.executable, *args]
    print(f"\n=== {label} ===", flush=True)
    proc = subprocess.run(cmd, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise SystemExit(f"V292 audit failed at {label}: rc={proc.returncode}")


def need(label: str, ok: bool) -> None:
    print(("PASS: " if ok else "FAIL: ") + label, flush=True)
    if not ok:
        raise SystemExit("V292 audit failed: " + label)


for path in (APP, HOME, HUB, AI, EDITOR, SHARE, SERVER, NGINX):
    need(f"required production artifact exists: {path.name}", path.is_file())

# Parse the actual generated Streamlit application first. This catches broken
# patch chains before individual feature contracts can hide the syntax error.
app_text = APP.read_text(encoding="utf-8")
compile(app_text, str(APP), "exec")
print("PASS: generated production app compiles", flush=True)

run("Creator Hub click safety", str(WEB / "test_v285_creator_hub_clicks.py"), str(HUB))
run("Global Game Bar", str(WEB / "test_v286_global_gamebar.py"), str(HUB), str(APP))
run("Profile overview", str(WEB / "test_v287_profile_overview.py"), str(HUB), str(APP))
run(
    "AI journey/editor handoff",
    str(WEB / "test_v288_ai_journey.py"),
    str(AI), str(HOME), str(EDITOR), str(APP),
)
run("Final share surface", str(WEB / "test_v289_share_final.py"), str(SHARE), str(APP))
run("AI engine bridge", str(WEB / "test_v291_ai_engine_bridge.py"), str(HOME), str(APP))
run("Semantic provider resilience", str(WEB / "test_v292_semantic_circuit.py"))
run("AI profile differentiation", str(WEB / "test_v292_ai_profiles.py"))

run("No-audio final master", str(WEB / "test_v105_no_audio_master.py"), str(APP))
run("Render contract", str(WEB / "test_v105_render_contract.py"))
run("Upload policy", str(WEB / "test_v105_upload_policy.py"))
run("Worker image contract", str(WEB / "test_v105_worker_image.py"))
run("FFmpeg smoke", str(WEB / "test_v107_ffmpeg_smoke.py"), timeout=240)
run("Mobile codec smoke", str(WEB / "test_v107_mobile_codec_smoke.py"), timeout=300)
run("Editor 2027 component", str(WEB / "test_editor_2027_component.py"), str(APP))
run("Persistent content memory", str(WEB / "test_v145_content_memory.py"), str(SERVER), str(APP))

run(
    "Full publish/share flow",
    str(WEB / "audit_v290_full_flow.py"),
    str(APP), str(SHARE), str(SERVER), str(NGINX),
)

# Current production invariants that span several older feature tests.
need("three AI candidates remain the production target", "numero_clip=3" in app_text)
need("15-second path remains supported", "15" in app_text)
need("30-second path remains supported", "30" in app_text)
need("V291 authoritative engine state is present", "gsf_v291_engine_profile" in app_text)
need("final app keeps content-memory integration", "GSF_V145_MEMORY_FINAL" in app_text)
need("final app keeps no-audio fallback", "anullsrc=channel_layout=stereo:sample_rate=48000" in app_text)

# Keep memory/concurrency safety explicit: Railway currently has 1 GB per
# service and the worker is intentionally serialized. Do not let a future
# optimization silently multiply concurrent whole-video scans.
worker_docker = (WEB / "Dockerfile.worker").read_text(encoding="utf-8")
need("worker scan slots stay at one", "GSF_WORKER_SCAN_SLOTS=1" in worker_docker)
need("semantic hard timeout is explicit", "GSF_SEMANTIC_TIMEOUT_SECONDS=45" in worker_docker)
need("429 provider cooldown is explicit", "GSF_SEMANTIC_COOLDOWN_429_SECONDS=900" in worker_docker)
need("503 provider cooldown is explicit", "GSF_SEMANTIC_COOLDOWN_503_SECONDS=120" in worker_docker)

print("\nV292 FULL PRODUCTION AUDIT: PASS", flush=True)
