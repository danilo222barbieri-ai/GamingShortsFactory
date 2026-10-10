#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
HUB = ROOT / 'web' / 'creator_hub_v156_component' / 'index.html'
FIX = ROOT / 'web' / 'fix_v362_project_pages_cleanup.py'


def extract_v362_runtime(text: str) -> str:
    m = re.search(r'<script id="v362ProjectPagesCleanupRuntime">(.*?)</script>', text, re.S)
    if not m:
        raise AssertionError('V362 runtime block missing')
    return m.group(1)


def check_runtime(label: str, text: str) -> None:
    runtime = extract_v362_runtime(text)
    assert 'V371_OBSERVER_STABILITY' in runtime, f'{label}: V371 stability marker missing'
    assert 'function v362SetClass' in runtime, f'{label}: idempotent class helper missing'
    assert "attributeFilter:['class','style']" in runtime, f'{label}: required project visibility observer changed unexpectedly'
    assert "v362SetClass(view,'v362ProjectClean',direct)" in runtime, f'{label}: project clean class is not idempotent'
    assert "v362SetClass(view,'v362CollectionEmpty',removableEmpty)" in runtime, f'{label}: empty collection class is not idempotent'
    assert "v362SetClass(el,'v362EmptyCollection',removableEmpty)" in runtime, f'{label}: empty rows class is not idempotent'
    # The observer watches class/style, therefore its callback must never blindly
    # rewrite classes on every callback. That creates a MutationObserver feedback
    # loop when V368 writes inline pointer/visibility styles on startup.
    for forbidden in (
        "view.classList.remove('v362ProjectClean','v362CollectionEmpty')",
        "view.classList.toggle('v362ProjectClean',direct)",
        "view.classList.remove('v362CollectionEmpty')",
        "rows.classList.toggle('v362EmptyCollection',removableEmpty)",
        "view.classList.toggle('v362CollectionEmpty',removableEmpty)",
    ):
        assert forbidden not in runtime, f'{label}: unstable observer mutation remains: {forbidden}'


hub = HUB.read_text(encoding='utf-8')
fix = FIX.read_text(encoding='utf-8')
check_runtime('Hub source', hub)
check_runtime('V362 generator', fix)

assert 'V368_CREATOR_HUB_TOUCH_RECOVERY' in hub, 'V368 recovery unexpectedly missing'
assert 'new MutationObserver(v368RepairActiveView)' in hub, 'V368 active-view repair unexpectedly missing'
assert 'stopPropagation(' not in hub.split('V368_CREATOR_HUB_TOUCH_RECOVERY', 1)[1], 'V368 must not block native input'
assert 'preventDefault(' not in hub.split('V368_CREATOR_HUB_TOUCH_RECOVERY', 1)[1], 'V368 must not cancel native input'

print('V371 CREATOR HUB OBSERVER STABILITY CONTRACT: PASS')
