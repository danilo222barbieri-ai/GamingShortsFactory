#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
WEB = ROOT/'web'
PATCH = WEB/'fix_v311_mobile_hub_clean_pass.py'
HUB = WEB/'creator_hub_v156_component'/'index.html'
START = WEB/'start_web.sh'


def fail(msg):
    print('[FAIL]',msg)
    raise SystemExit(1)


def ok(msg):
    print('[ OK ]',msg)

for path,label in ((PATCH,'patch'),(HUB,'hub'),(START,'start_web')):
    if not path.is_file(): fail(label+' missing')

spec=importlib.util.spec_from_file_location('v311',PATCH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
source=HUB.read_text(encoding='utf-8')
patched=mod.patch_hub_text(source)

required=(
    'V311 MOBILE HUB CLEAN PASS',
    'id="v311HubForce"',
    '#hub .view[data-view="profile"] .profileMobilePlan',
    '#hub .view[data-view="profile"] .profilePlanGroup',
    '#hub .view[data-view="profile"] .profileOverviewActions',
    '#hub .view[data-view="projects"] #projectRows .stats',
    '#hub .view[data-view="drafts"] #projectRows .stats',
    '#hub .view[data-view="live"] .liveRootFolders',
    'data-live-pane="youtube"',
    'youtubeLiveFolders',
    '<b>Le tue live</b><small>Dirette YouTube salvate nel Creator Hub</small>',
    '<b>VOD</b><small>Replay completi delle live YouTube</small>',
    '<b>Highlights</b><small>Short e momenti estratti da YouTube</small>',
    'grid-template-rows:repeat(4,minmax(0,1fr))!important',
    '.folder[data-folder="subscription"]{display:none!important}',
    'id="v311HubRuntime"',
    "gsfHubVersion='3112'",
    'MutationObserver',
)
for marker in required:
    if marker not in patched: fail('missing marker: '+marker)
    ok('found '+marker)

style_block=patched.split('<style id="v311HubForce">',1)[1].split('</style>',1)[0]
if '@media(' in style_block:
    fail('V311 final rules must not depend on iframe viewport width')
if 'data-v300-layout' in style_block:
    fail('V311 final rules must not depend on historical layout attributes')
ok('V311 final rules are independent from historical CSS/layout markers')

# The force style must be appended as the last head style, not inserted before
# historical CSS where the cascade can override it.
head=patched.split('</head>',1)[0]
if head.rfind('id="v311HubForce"') < head.rfind('</style>') - 20000:
    fail('V311 force style is not at the end of the head cascade')
if head.rfind('id="v311HubForce"') <= head.find('<style>'):
    fail('V311 force style must come after the base stylesheet')
ok('V311 force style is appended after historical styles')

if mod.patch_hub_text(patched)!=patched:
    fail('V311 Hub patch is not idempotent')
ok('Hub patch is idempotent')

shell_sample='x="/creator-hub-v156/?v=307"\ny="/share-v156/?v=307"\n'
shell_patched=mod.patch_shell_text(shell_sample)
if '/creator-hub-v156/?v=3112' not in shell_patched:
    fail('Creator Hub cache key not bumped to v3112')
if '/share-v156/?v=307' not in shell_patched:
    fail('V311 must not alter unrelated routes')
if mod.patch_shell_text(shell_patched)!=shell_patched:
    fail('V311 shell patch is not idempotent')
ok('Creator Hub cache key v3112')

start=START.read_text(encoding='utf-8')
needle='python /app/web/fix_v311_mobile_hub_clean_pass.py /app/web/creator_hub_v156_component/index.html'
if needle not in start: fail('V311 startup patch not registered')
if start.index(needle)<start.index('python /app/web/test_v310_creator_hub_mobile_cleanup.py /app'):
    fail('V311 must run after V310')
if start.index(needle)>start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V311 must run before production app generation')
ok('startup order correct')

print('\nV311 MOBILE HUB CLEAN PASS: PASS')
