#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
MODULE = WEB / "ui_release.py"

if not MODULE.is_file():
    raise SystemExit("V308 FAIL: ui_release.py missing")

spec = importlib.util.spec_from_file_location("gsf_ui_release", MODULE)
if spec is None or spec.loader is None:
    raise SystemExit("V308 FAIL: ui_release.py not loadable")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

checks = {
    "release id": getattr(mod, "GSF_UI_RELEASE", None) == "308",
    "fresh path": mod.versioned_path("/ai-v221/") == "/ai-v221/?v=308",
    "replaces old version": mod.versioned_path("/ai-v221/?v=287") == "/ai-v221/?v=308",
}

home = (WEB / "home_v154_embed.py").read_text(encoding="utf-8")
editor = (WEB / "editor_2027_embed.py").read_text(encoding="utf-8")
checks.update({
    "Home uses central release": "GSF_UI_RELEASE" in home and "gsf_home_v154_live_{GSF_UI_RELEASE}" in home,
    "Editor uses central release": "GSF_UI_RELEASE" in editor and "gsf_editor_2027_v{GSF_UI_RELEASE}" in editor,
})

failed = []
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)
    if not ok:
        failed.append(name)
if failed:
    raise SystemExit("V308 UI release contract failed: " + ", ".join(failed))
print("V308 UI release contract: PASS")
