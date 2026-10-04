import sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else "/app/web/creator_hub_v156_component/index.html")
text = path.read_text(encoding="utf-8")

checks = {
    "data-view uses querySelectorAll": '$$("[data-view]").forEach' in text,
    "project panes use querySelectorAll": '$$("[data-project-pane]").forEach' in text,
    "broken data-view selector removed": '$("[data-view]").forEach' not in text.replace('$$("[data-view]").forEach', ''),
    "broken project-pane selector removed": '$("[data-project-pane]").forEach' not in text.replace('$$("[data-project-pane]").forEach', ''),
    "folder click handler preserved": '$$(".folder").forEach' in text,
    "Hub still boots": 'openView("dashboard");loadState();' in text,
}

for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)

bad = [name for name, ok in checks.items() if not ok]
if bad:
    raise SystemExit("V285 Creator Hub clicks failed: " + ", ".join(bad))

print("V285 Creator Hub clicks: PASS")
