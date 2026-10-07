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
    'V311 SOURCE NORMALIZED',
    'id="v311HubForce"',
    'data-live-pane="youtube"',
    'youtubeLiveFolders',
    '<b>Le tue live</b><small>Dirette YouTube salvate nel Creator Hub</small>',
    '<b>VOD</b><small>Replay completi delle live YouTube</small>',
    '<b>Highlights</b><small>Short e momenti estratti da YouTube</small>',
    'grid-template-rows:repeat(4,minmax(0,1fr))!important',
    'id="v311HubRuntime"',
    "gsfHubVersion='3113'",
)
for marker in required:
    if marker not in patched: fail('missing marker: '+marker)
    ok('found '+marker)

# V311.3 must change the actual DOM/JS source, not merely hide the old UI with CSS.
dashboard=patched.split('<section class="view active" data-view="dashboard">',1)[1].split('<section class="view" data-view="projects">',1)[0]
if 'data-folder="subscription"' in dashboard:
    fail('subscription dashboard tile still exists in DOM')
if 'hubMural' in dashboard:
    fail('dashboard mural still exists in DOM')
ok('dashboard old nodes removed structurally')

live=patched.split('<section class="view" data-view="live">',1)[1].split('</main>',1)[0]
if 'liveRootFolders' in live:
    fail('Live launcher tiles still exist in DOM')
if 'data-live-pane="highlights"' in live:
    fail('old Auto Highlights pane still exists in DOM')
if 'youtubeLiveFolders' not in live:
    fail('dedicated YouTube section missing')
ok('Live is structurally Twitch + YouTube')

if '$("#projectRows").innerHTML=' in patched and '$("#projectRows").innerHTML="";' not in patched:
    fail('Bozze still renders current-project/stats source')
if '<div class="stats">' in patched:
    fail('Bozze four-stat strip is still generated')
ok('Bozze old project/stats source removed')

# Simulate the runtime state after V287 + V303 with the same multiline shape as
# the production component. Keep the four cards; delete only duplicate strips.
profile_fixture='''<html><head></head><body>
<main id="hub">
<section class="view" data-view="profile">
 <div class="profileGroup profilePlanGroup profileMobilePlan" aria-label="Abbonamento"><div class="profileGroupTitle">ABBONAMENTO</div><div class="planRow">old plan</div></div>
 <div class="profileOverviewGrid"><button class="profileOverviewCard">Shorts creati</button><button class="profileOverviewCard">Bozze</button><button class="profileOverviewCard">Il tuo piano</button><button class="profileOverviewCard">Social collegati</button></div>
 <div class="profileOverviewActions"><button>Gestisci il tuo abbonamento</button><button>Account collegati</button></div>
 <button class="logoutProfile" type="button">Disconnetti</button>
</section>
<section class="view" data-view="live">
 <div class="liveRootFolders"><button>old</button></div>
 <div class="livePane" data-live-pane="twitch"></div>
 <div class="livePane" data-live-pane="youtube"><div class="livePaneTitle">YouTube Live</div><div class="empty">Quando collegheremo YouTube Live, dirette e replay compariranno qui con la stessa struttura a cartelle.</div></div>
 <div class="livePane" data-live-pane="highlights"><div class="livePaneTitle">Auto Highlights</div><div class="empty">old</div></div>
</section>
<section class="view active" data-view="dashboard">
 <div class="dashboard"><div class="hubMural">old</div><div class="folders">
  <button class="folder" data-folder="subscription"><div>old</div></button>
 </div></div>
</section>
<section class="view" data-view="projects"><div id="projectRows"></div></section>
</main>
<script>
   $("#projectRows").innerHTML=p.id?'<div class="projectBox">old</div><div class="stats"><div class="stat">old</div></div>':'<div class="empty">old</div>';
</script>
</body></html>'''
fixture=mod.patch_hub_text(profile_fixture)
profile=fixture.split('<section class="view" data-view="profile">',1)[1].split('<section class="view" data-view="live">',1)[0]
if 'profileMobilePlan' in profile or 'profileOverviewActions' in profile:
    fail('Profile duplicate plan/action strips were not removed structurally')
if 'profileOverviewGrid' not in profile or profile.count('profileOverviewCard') != 4:
    fail('Profile four overview cards were not preserved')
ok('Profile keeps four cards and removes duplicate strips')

style_block=patched.split('<style id="v311HubForce">',1)[1].split('</style>',1)[0]
if '@media(' in style_block:
    fail('V311 final rules must not depend on iframe viewport width')
if 'data-v300-layout' in style_block:
    fail('V311 final rules must not depend on historical layout attributes')
ok('V311 final rules are independent from historical CSS/layout markers')

if mod.patch_hub_text(patched)!=patched:
    fail('V311 Hub patch is not idempotent')
ok('Hub patch is idempotent')

shell_sample='x="/creator-hub-v156/?v=307"\ny="/share-v156/?v=307"\n'
shell_patched=mod.patch_shell_text(shell_sample)
if '/creator-hub-v156/?v=3113' not in shell_patched:
    fail('Creator Hub cache key not bumped to v3113')
if '/share-v156/?v=307' not in shell_patched:
    fail('V311 must not alter unrelated routes')
if mod.patch_shell_text(shell_patched)!=shell_patched:
    fail('V311 shell patch is not idempotent')
ok('Creator Hub cache key v3113')

start=START.read_text(encoding='utf-8')
needle='python /app/web/fix_v311_mobile_hub_clean_pass.py /app/web/creator_hub_v156_component/index.html'
if needle not in start: fail('V311 startup patch not registered')
if start.index(needle)<start.index('python /app/web/test_v310_creator_hub_mobile_cleanup.py /app'):
    fail('V311 must run after V310')
if start.index(needle)>start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V311 must run before production app generation')
ok('startup order correct')

print('\nV311 MOBILE HUB CLEAN PASS: PASS')
