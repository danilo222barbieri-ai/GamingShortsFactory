import re
import sys
from pathlib import Path

hub = Path(sys.argv[1] if len(sys.argv) > 1 else "/app/web/creator_hub_v156_component/index.html")
app = Path(sys.argv[2] if len(sys.argv) > 2 else "/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py")

hub_text = hub.read_text(encoding="utf-8")
app_text = app.read_text(encoding="utf-8") if app.is_file() else ""

broken_collection_calls = re.findall(r'(?<!\$)\$\([^\n]{0,120}?\)\.forEach', hub_text)
legacy_routes = (
    'data-target="hub" data-section="shorts"' in app_text
    and 'data-target="hub" data-section="drafts"' in app_text
)
canonical_routes = (
    'data-section="projects"' in app_text
    and 'data-section="live"' in app_text
)

# The canonical singleton owns explicit destinations; the removed V249 DOM
# is no longer a routing source and must not be required by this legacy guard.
parent_routes = (
    all('data-page="'+target+'"' in app_text for target in ('home','hub','projects','live'))
    and "P.GSFNavigation.navigate(data)" in app_text
    and "section:b.dataset.page==='hub'?'dashboard':''" in app_text
)

checks = {
    "Creator Hub has no querySelector().forEach collection crash": not broken_collection_calls,
    "social dots use querySelectorAll": '$$(".socialDot").forEach' in hub_text,
    "Creator Hub listens for Game Bar focus": 'e.data.type!=="GSF_HUB_FOCUS"' in hub_text,
    "Creator Hub opens requested Game Bar section": 'openView(raw);' in hub_text,
    "global Game Bar routes Hub": 'data-target="hub" data-section="dashboard"' in app_text or parent_routes,
    "global Game Bar has a supported route set": legacy_routes or canonical_routes or parent_routes,
    "global shell forwards section to Creator Hub": "type:'GSF_HUB_FOCUS',section" in app_text,
    "Creator Hub route is present": '/creator-hub-v156/' in app_text,
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
