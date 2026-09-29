from pathlib import Path
import sys

path=Path(sys.argv[1] if len(sys.argv)>1 else "/app/GamingShortsFactory_V107_PRODUCTION_UI.py")
s=path.read_text(encoding="utf-8")

required=[
    "PERSONALIZZA IL TUO GAMEPLAY",
    "editor_2027_embed",
    "v1055_ad_manual_before_editor",
    "v1055_ad_manual_after_editor",
    "gsf-major-create-ai",
    "gsf-major-create-short",
    "Scegli il tuo motore IA o crea il tuo gameplay",
]
for marker in required:
    if marker not in s:
        raise SystemExit(f"FAIL missing V107 marker: {marker}")

for forbidden in [
    "_GSF_REAL_DEMO",
    "/app/demo_assets/",
    "DEMO FUNZIONALE",
    "demo_gameplay.mp4",
]:
    if forbidden in s:
        raise SystemExit(f"FAIL demo-only runtime leaked into production: {forbidden}")

compile(s,str(path),"exec")
print("V107 production UI smoke test: PASS")
