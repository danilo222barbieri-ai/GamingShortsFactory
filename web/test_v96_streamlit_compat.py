from pathlib import Path

root = Path(__file__).resolve().parents[1]
req = (root / "requirements-web.txt").read_text(encoding="utf-8")
start = (root / "web" / "start_web.sh").read_text(encoding="utf-8")
v95_path = root / "GamingShortsFactory_V95_RENDER_TEXT_POLISH.py"
v95 = v95_path.read_text(encoding="utf-8") if v95_path.exists() else ""

checks = {
    "Streamlit compatibility pin": "streamlit==1.49.1" in req,
    "V95/V98 production lineage entrypoint": ("GamingShortsFactory_V95_RENDER_TEXT_POLISH.py" in start or "GamingShortsFactory_V98_EDITOR_POLISH.py" in start or "GamingShortsFactory_V98_1_EDITOR_HOTFIX.py" in start or "GamingShortsFactory_V98_2_UPLOAD_RECOVERY.py" in start or "GamingShortsFactory_V98_3_HOME_COMPACT.py" in start),
    "V95 generated artifact exists": bool(v95),
    "V95 render-text marker present": "V95 Render Text Polish" in v95,
    "approved player code remains present": "components" in v95 and "html" in v95,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)
if failed:
    raise SystemExit("V96 compatibility regression failed: " + ", ".join(failed))
print("V96 Streamlit compatibility regression: PASS")
