#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'
PATCH = WEB / 'fix_v312_creator_hub_design_sync.py'
HUB = WEB / 'creator_hub_v156_component' / 'index.html'
START = WEB / 'start_web.sh'


def fail(msg):
    print('[FAIL]', msg)
    raise SystemExit(1)


def ok(msg):
    print('[ OK ]', msg)


if not PATCH.exists():
    fail('V312 patch file missing')
if not HUB.exists():
    fail('Creator Hub source missing')
if not START.exists():
    fail('start_web.sh missing')

spec = importlib.util.spec_from_file_location('v312', PATCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if not hasattr(mod, 'patch_hub_text'):
    fail('patch_hub_text() missing')

source = HUB.read_text(encoding='utf-8')
patched = mod.patch_hub_text(source)

checks = {
    'V312 marker': 'V312 CREATOR HUB DESIGN SYNC' in patched,
    'dashboard has only three master cards': 'data-folder="profile"' in patched and 'data-folder="projects"' in patched and 'data-folder="live"' in patched,
    'dashboard Social card removed': '<button class="folder" data-folder="social">' not in patched,
    'dashboard subscription card removed': '<button class="folder" data-folder="subscription">' not in patched,
    'dashboard live label normalized': '<h2>Live</h2>' in patched,
    'profile keeps plan card': 'class="profilePortalCard profilePortalPlan"' in patched,
    'profile keeps social card': 'class="profilePortalCard profilePortalSocial"' in patched,
    'profile removes shorts summary': 'SHORTS CREATI' not in patched,
    'profile removes drafts summary': 'BOZZE</div><div class="profileOverviewValue"' not in patched,
    'projects landing exists': 'id="projectHubCards"' in patched,
    'projects landing has Shorts': 'data-project-dest="shorts"' in patched,
    'projects landing has Bozze': 'data-project-dest="drafts"' in patched,
    'projects landing toggles in openView': 'projectHub.hidden=!!projectMode' in patched,
    'Shorts list renders design cards': 'shortDesignCard' in patched,
    'draft list renders design cards': 'draftDesignCard' in patched,
    'live has Twitch section': 'liveDesignSection twitchDesignSection' in patched,
    'live has YouTube section': 'liveDesignSection youtubeDesignSection' in patched,
    'social summary exists': 'id="socialSummaryCount"' in patched,
    'subscription plan cards exist': 'subscriptionPlanCard creatorPlan' in patched and 'subscriptionPlanCard proPlan' in patched,
    'mobile fixed gamebar clearance': 'padding-bottom:calc(96px + env(safe-area-inset-bottom))!important' in patched,
}
for name, passed in checks.items():
    if not passed:
        fail(name)
    ok(name)

patched_twice = mod.patch_hub_text(patched)
if patched_twice != patched:
    fail('patch is not idempotent')
ok('patch is idempotent')

start = START.read_text(encoding='utf-8')
needle = 'python /app/web/fix_v312_creator_hub_design_sync.py /app/web/creator_hub_v156_component/index.html'
if needle not in start:
    fail('V312 startup patch is not registered')
if start.index(needle) < start.index('python /app/web/fix_v311_mobile_hub_clean_pass.py'):
    fail('V312 must run after V311')
if start.index(needle) > start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V312 must run before production app generation')
ok('startup order is correct')

print('\nV312 CREATOR HUB DESIGN SYNC: PASS')
