#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
START = ROOT / "web" / "start_web.sh"
text = START.read_text(encoding="utf-8")

forbidden = (
    "fix_v295_internal_pages_responsive.py",
    "fix_v303_mobile_hub_compact.py",
    "fix_v306_home_visual_lock.py",
    "fix_v307_mobile_visual_source.py",
)
checks = {
    "no obsolete visual mutators": not any(name in text for name in forbidden),
    "V308 canonicalizer runs": "fix_v308_mobile_master.py" in text,
    "V308 runtime shell normalizer runs": "fix_v308_runtime_shell.py" in text,
    "V308 UI release test runs": "test_v308_ui_release.py" in text,
    "V308 Home test runs": "test_v308_home_mobile_master.py" in text,
    "V308 surfaces test runs": "test_v308_surfaces_mobile_master.py" in text,
    "V308 Editor test runs": "test_v308_editor_mobile_master.py" in text,
    "V308 cache test runs": "test_v308_cache_contract.py" in text,
    "render guard runs after V308": text.find("apply_v293_render_memory_guard.py") > text.find("test_v308_cache_contract.py") >= 0,
}
failed=[]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)
    if not ok: failed.append(name)
if failed:
    raise SystemExit("V308 startup contract failed: " + ", ".join(failed))
subprocess.run(["sh", "-n", str(START)], check=True)
print("V308 startup contract: PASS")
