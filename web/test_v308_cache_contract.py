#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import py_compile
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
FIX = WEB / "fix_v308_runtime_shell.py"
if not FIX.is_file():
    raise SystemExit("V308 FAIL: runtime shell normalizer missing")
spec = importlib.util.spec_from_file_location("v308_runtime_shell", FIX)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

shell_path = ROOT / "GamingShortsFactory_V154_STRUCTURAL_HOME.py"
nginx_path = WEB / "nginx.conf.template"
shell = mod.normalize_shell(shell_path.read_text(encoding="utf-8"))
nginx = mod.normalize_nginx(nginx_path.read_text(encoding="utf-8"))
home = (WEB / "home_v154_embed.py").read_text(encoding="utf-8")
editor = (WEB / "editor_2027_embed.py").read_text(encoding="utf-8")

old_versions = tuple(f"?v={v}" for v in (285,287,300,305,306,307))
checks = {
    "no old active UI versions": not any(v in shell for v in old_versions),
    "Hub release 308": "/creator-hub-v156/?v=308" in shell,
    "Share release 308": "/share-v156/?v=308" in shell,
    "AI release 308": "/ai-v221/?v=308" in shell,
    "Home central component release": "gsf_home_v154_live_{GSF_UI_RELEASE}" in home,
    "Editor central component release": "gsf_editor_2027_v{GSF_UI_RELEASE}" in editor,
    "UI static cache no-store": 'no-store, max-age=0' in nginx and 'always' in nginx,
    "desktop preview redirects Home": "V308 DESKTOP PREVIEW REDIRECT" in nginx,
    "desktop home redirects Home": "V308 DESKTOP HOME REDIRECT" in nginx,
}
failed=[]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)
    if not ok: failed.append(name)
if failed:
    raise SystemExit("V308 cache contract failed: " + ", ".join(failed))
py_compile.compile(str(shell_path), doraise=True)
print("V308 cache contract: PASS")
