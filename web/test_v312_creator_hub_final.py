#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'
PATCH = WEB / 'fix_v312_creator_hub_final.py'
HUB = WEB / 'creator_hub_v156_component' / 'index.html'
START = WEB / 'start_web.sh'
V310 = WEB / 'fix_v310_creator_hub_mobile_cleanup.py'


def fail(msg):
    print('[FAIL]', msg)
    raise SystemExit(1)


def ok(msg):
    print('[ OK ]', msg)


for path, label in [(PATCH, 'V312 final patch'), (HUB, 'Creator Hub source'), (START, 'start_web.sh'), (V310, 'V310 patch')]:
    if not path.exists():
        fail(f'{label} missing')

spec = importlib.util.spec_from_file_location('v312final', PATCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if not hasattr(mod, 'patch_hub_text') or not hasattr(mod, 'patch_shell_text'):
    fail('V312 final patch functions missing')

spec310 = importlib.util.spec_from_file_location('v310', V310)
mod310 = importlib.util.module_from_spec(spec310)
spec310.loader.exec_module(mod310)

source = HUB.read_text(encoding='utf-8')
source_after_v310 = mod310.patch_hub_text(source)
patched = mod.patch_hub_text(source_after_v310)

checks = {
    'final marker': 'V312 CREATOR HUB FINAL' in patched,
    'layout is iframe-width independent': '@media(max-width:760px)' not in mod.FINAL_CSS,
    'dashboard social folder removed': '<button class="folder" data-folder="social">' not in patched,
    'dashboard subscription folder removed': '<button class="folder" data-folder="subscription">' not in patched,
    'dashboard keeps profile': 'data-folder="profile"' in patched,
    'dashboard keeps projects': 'data-folder="projects"' in patched,
    'dashboard keeps live': 'data-folder="live"' in patched,
    'profile only approved portals': 'profilePortalPlan' in patched and 'profilePortalSocial' in patched,
    'profile shorts card gone': 'SHORTS CREATI' not in patched,
    'profile drafts card gone': 'profileOverviewDrafts' not in patched,
    'projects landing': 'id="projectHubCards"' in patched,
    'projects shorts destination': 'data-project-dest="shorts"' in patched,
    'projects drafts destination': 'data-project-dest="drafts"' in patched,
    'short design cards': 'shortDesignCard' in patched,
    'draft design cards': 'draftDesignCard' in patched,
    'live Twitch section': 'twitchDesignSection' in patched,
    'live YouTube section': 'youtubeDesignSection' in patched,
    'social page summary': 'id="socialSummaryCount"' in patched,
    'subscription plans': 'subscriptionPlanCard creatorPlan' in patched and 'subscriptionPlanCard proPlan' in patched,
    'internal page scroll clearance': 'padding-bottom:calc(96px + env(safe-area-inset-bottom))!important' in patched,
}
for name, passed in checks.items():
    if not passed:
        fail(name)
    ok(name)

if mod.patch_hub_text(patched) != patched:
    fail('Hub patch not idempotent')
ok('Hub patch idempotent')

# The V154 shell is generated inside Docker by apply_v154_structural_home.py,
# so it does not exist in the repository checkout. Test the cache transformer
# against the exact route shape; the production-image gate below exercises the
# real generated V154 file at startup.
shell_fixture = 'HUB_URL = "/creator-hub-v156/?v=3112"\n'
shell_patched = mod.patch_shell_text(shell_fixture)
if '/creator-hub-v156/?v=312' not in shell_patched:
    fail('Creator Hub cache key not bumped to v312')
ok('Creator Hub cache key bumped')
if mod.patch_shell_text(shell_patched) != shell_patched:
    fail('Shell patch not idempotent')
ok('Shell patch idempotent')

start = START.read_text(encoding='utf-8')
new_call = 'python /app/web/fix_v312_creator_hub_final.py /app/web/creator_hub_v156_component/index.html /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py'
old_call = 'python /app/web/fix_v311_mobile_hub_clean_pass.py /app/web/creator_hub_v156_component/index.html'
if new_call not in start:
    fail('V312 final startup call missing')
if old_call in start:
    fail('legacy V311 runtime call still active')
if start.index(new_call) > start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V312 must run before production app generation')
ok('startup uses one authoritative Creator Hub finalizer')

print('\nV312 CREATOR HUB FINAL: PASS')
