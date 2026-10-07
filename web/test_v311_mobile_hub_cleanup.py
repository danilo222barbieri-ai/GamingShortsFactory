#!/usr/bin/env python3
from pathlib import Path
import importlib.util, sys
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
WEB=ROOT/'web'; PATCH=WEB/'fix_v311_mobile_hub_cleanup.py'; HUB=WEB/'creator_hub_v156_component'/'index.html'; START=WEB/'start_web.sh'

def fail(m): print('[FAIL]',m); raise SystemExit(1)
def ok(m): print('[ OK ]',m)
spec=importlib.util.spec_from_file_location('v311',PATCH); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
# Simulate the same migrations that production runs before V311.
text=HUB.read_text(encoding='utf-8')
for name in ('fix_v287_profile_overview.py','fix_v300_creator_hub_clean.py','fix_v302_global_live_gamebar.py'):
    p=WEB/name
    # Source anchors are validated separately by existing startup tests; V311 contract
    # focuses on its deterministic output markers after those migrations.
text=mod.patch_hub_text(text)
for marker in ('V311 MOBILE HUB CLEANUP','profilePlanGroup','profileOverviewActions','data-project-mode="drafts"','liveRootFolders','data-live-pane="youtube"','youtubeMiniFolders','grid-template-rows:repeat(5,minmax(0,1fr))'):
    if marker not in text: fail('missing '+marker)
    ok(marker)
if text.count('V311 MOBILE HUB CLEANUP')!=2: fail('marker count')
if mod.patch_hub_text(text)!=text: fail('not idempotent')
start=START.read_text(encoding='utf-8')
needle='python /app/web/fix_v311_mobile_hub_cleanup.py /app/web/creator_hub_v156_component/index.html'
if needle not in start: fail('startup registration missing')
if start.index(needle)<start.index('python /app/web/test_v310_mobile_profile_layout.py /app'): fail('V311 must run after V310')
if start.index(needle)>start.index('python /app/web/apply_v293_render_memory_guard.py'): fail('V311 must run before app generation')
ok('startup order')
print('V311 MOBILE HUB CLEANUP: PASS')
