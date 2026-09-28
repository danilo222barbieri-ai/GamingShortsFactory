from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
req = (root / "requirements-web.txt").read_text(encoding="utf-8")
start = (root / "web" / "start_web.sh").read_text(encoding="utf-8")
docker = (root / "Dockerfile").read_text(encoding="utf-8")

checks = {
    "Streamlit compatibility pin": "streamlit==1.49.1" in req,
    "V95 remains production entrypoint": "GamingShortsFactory_V95_RENDER_TEXT_POLISH.py" in start,
    "V95 regression remains in Docker build": "test_v95_render_text_polish.py" in docker,
    "V94 quality regression remains in Docker build": "test_v94_short_quality.py" in docker,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)
if failed:
    raise SystemExit("V96 compatibility regression failed: " + ", ".join(failed))
print("V96 Streamlit compatibility regression: PASS")
