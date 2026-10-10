#!/usr/bin/env python3
from pathlib import Path
import importlib.util
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
    for forbidden in (
        "view.classList.remove('v362ProjectClean','v362CollectionEmpty')",
        "view.classList.toggle('v362ProjectClean',direct)",
        "view.classList.remove('v362CollectionEmpty')",
        "rows.classList.toggle('v362EmptyCollection',removableEmpty)",
        "view.classList.toggle('v362CollectionEmpty',removableEmpty)",
    ):
        assert forbidden not in runtime, f'{label}: unstable observer mutation remains: {forbidden}'


assert FIX.is_file(), 'V362 cleanup patch missing'
spec = importlib.util.spec_from_file_location('v362_stability', FIX)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

# Unit-level fixture represents the real point in the Docker patch chain where
# V359 already exists and V362 is applied. Raw repository HTML is intentionally
# earlier than that stage, so applying V362 directly to it would be an invalid test.
fixture = '''<!doctype html><html><body>
<div id="hub">
  <section class="view active" data-view="projects" style="visibility:visible;pointer-events:auto">
    <div class="detail"><div class="detailHead"><h2 id="projectsViewTitle">I miei Shorts</h2></div>
      <div class="detailCard"><div class="folderScroller">
        <div class="hubProjectsGuide">Guida</div>
        <div class="projectSection" data-project-pane="shorts" style="display:block">
          <div class="projectHero">Shorts</div><div id="shortRows"><div class="empty">Nessuno Short archiviato.</div></div>
        </div>
        <div class="projectSection" data-project-pane="drafts" style="display:none">
          <div class="projectHero">Bozze</div><div id="draftRows"><div class="empty">Nessun progetto in lavorazione salvato.</div></div>
        </div>
      </div></div>
    </div>
  </section>
</div>
<!-- V359_CREATOR_HUB_GAMEBAR_FIT -->
</body></html>'''
patched_fixture = mod.patch_text(fixture)
check_runtime('Patched V362 fixture', patched_fixture)
check_runtime('V362 generator', mod.PATCH)
assert mod.patch_text(patched_fixture) == patched_fixture, 'V371 upgrade must be idempotent'

# The repository Hub may still be pre-V359; Docker upgrades it later. We only
# use it here to preserve the independent V368 safety contract.
hub = HUB.read_text(encoding='utf-8')
assert 'V368_CREATOR_HUB_TOUCH_RECOVERY' in hub, 'V368 recovery unexpectedly missing'
assert 'new MutationObserver(v368RepairActiveView)' in hub, 'V368 active-view repair unexpectedly missing'
v368 = hub.split('V368_CREATOR_HUB_TOUCH_RECOVERY', 1)[1]
assert 'stopPropagation(' not in v368, 'V368 must not block native input'
assert 'preventDefault(' not in v368, 'V368 must not cancel native input'

print('V371 CREATOR HUB OBSERVER STABILITY CONTRACT: PASS')
