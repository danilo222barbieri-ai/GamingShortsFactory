import re
import sys
from pathlib import Path

hub = Path(sys.argv[1] if len(sys.argv) > 1 else "/app/web/creator_hub_v156_component/index.html")
app = Path(sys.argv[2] if len(sys.argv) > 2 else "/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py")

hub_text = hub.read_text(encoding="utf-8")
app_text = app.read_text(encoding="utf-8") if app.is_file() else ""

broken_collection_calls = re.findall(r'(?<!\$)\$\([^\n]{0,120}?\)\.forEach', hub_text)

checks = {
    "Creator Hub has no querySelector().forEach collection crash": not broken_collection_calls,
    "social dots use querySelectorAll": '$$(".socialDot").forEach' in hub_text,
    "Creator Hub listens for Game Bar focus": 'e.data.type!=="GSF_HUB_FOCUS"' in hub_text,
    "Creator Hub opens requested Game Bar section": 'openView(raw);' in hub_text,
    "global Game Bar routes Hub": 'data-target="hub" data-section="dashboard"' in app_text,
    "global Game Bar routes My Shorts": 'data-target="hub" data-section="shorts"' in app_text,
    "global Game Bar routes Drafts": 'data-target="hub" data-section="drafts"' in app_text,
    "global shell forwards section to Creator Hub": "type:'GSF_HUB_FOCUS',section" in app_text,
    "Creator Hub iframe cache is V286": '/creator-hub-v156/?v=286' in app_text,
}

for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)

if broken_collection_calls:
    print("Broken collection calls:")
    for item in broken_collection_calls:
        print(" -", item)

bad = [name for name, ok in checks.items() if not ok]
if bad:
    raise SystemExit("V286 global Game Bar regression failed: " + ", ".join(bad))

print("V286 global Game Bar: PASS")
