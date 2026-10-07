#!/usr/bin/env python3
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import re
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
WEB = ROOT/'web'
PATCH = WEB/'fix_v311_mobile_hub_clean_pass.py'
V287 = WEB/'fix_v287_profile_overview.py'
HUB = WEB/'creator_hub_v156_component'/'index.html'
START = WEB/'start_web.sh'


def fail(msg):
    print('[FAIL]',msg)
    raise SystemExit(1)


def ok(msg):
    print('[ OK ]',msg)

for path,label in ((PATCH,'patch'),(V287,'V287 profile patch'),(HUB,'hub'),(START,'start_web')):
    if not path.is_file(): fail(label+' missing')

spec=importlib.util.spec_from_file_location('v311',PATCH)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
spec287=importlib.util.spec_from_file_location('v287',V287)
mod287=importlib.util.module_from_spec(spec287); spec287.loader.exec_module(mod287)

# The contract can run in two valid states:
# 1) CI/source state, before V311 has rewritten the Hub; reproduce V287 first.
# 2) production startup state, immediately after fix_v311 has already normalized
#    the same file; validate it directly instead of trying to recreate deleted
#    legacy anchors. This makes the test itself idempotent across restarts.
source=HUB.read_text(encoding='utf-8')
if 'V311 APPROVED CREATOR REFERENCE' in source:
    patched=source
else:
    if 'id="profileOverviewShorts"' not in source:
        pattern=re.compile(r'\s*<div class="profileMural profileOnlyMural" aria-hidden="true">Questo è il tuo spazio,<br>fallo tuo</div>\s*<button class="logoutProfile" id="logoutProfile" type="button">Disconnetti dal Creator Hub</button>')
        source,count=pattern.subn('\n'+mod287.OVERVIEW_HTML,source,count=1)
        if count!=1: fail('could not simulate V287 Profile overview injection')
    patched=mod.patch_hub_text(source)

required=(
    'V311 MOBILE HUB CLEAN PASS',
    'V311 APPROVED CREATOR REFERENCE',
    'id="v311HubForce"',
    'data-live-pane="youtube"',
    'youtubeLiveFolders',
    'id="projectHubCards"',
    'data-project-dest="shorts"',
    'data-project-dest="drafts"',
    'grid-template-rows:repeat(3,minmax(0,1fr))!important',
    'id="v311HubRuntime"',
    "gsfHubVersion='3114'",
)
for marker in required:
    if marker not in patched: fail('missing marker: '+marker)
    ok('found '+marker)

# Dashboard is the approved reference: creator card + exactly Profile, Projects, Live.
dashboard=patched.split('<section class="view active" data-view="dashboard">',1)[1].split('<section class="view" data-view="projects">',1)[0]
folders=re.findall(r'data-folder="([^"]+)"', dashboard)
if folders != ['profile','projects','live']:
    fail('dashboard destinations are not exactly profile/projects/live: '+repr(folders))
for forbidden in ('data-folder="social"','data-folder="subscription"','hubMural'):
    if forbidden in dashboard: fail('dashboard legacy node remains: '+forbidden)
if '<h2>Live</h2>' not in dashboard:
    fail('dashboard Live title missing')
ok('dashboard matches approved three-card structure')

# Profile keeps only plan + social portals; Shorts/Bozze belong in Projects.
profile=patched.split('<section class="view" data-view="profile">',1)[1].split('<section class="view" data-view="social">',1)[0]
if 'data-profile-overview="shorts"' in profile or 'data-profile-overview="drafts"' in profile:
    fail('Profile still contains Shorts/Bozze overview cards')
if profile.count('class="profileOverviewCard"') != 2:
    fail('Profile must contain exactly two overview cards')
if 'data-profile-overview="subscription"' not in profile or 'data-profile-overview="social"' not in profile:
    fail('Profile plan/social portals missing')
ok('Profile contains only plan and social overview destinations')

# Projects opens as a folder landing with My Shorts + Drafts.
projects=patched.split('<section class="view" data-view="projects">',1)[1].split('<section class="view" data-view="profile">',1)[0]
if projects.count('data-project-dest=') != 2:
    fail('Projects landing must expose exactly two destinations')
if 'data-project-dest="shorts"' not in projects or 'data-project-dest="drafts"' not in projects:
    fail('Projects landing missing Shorts or Bozze')
ok('Projects landing contains I miei Shorts + Bozze')

# Live is structurally Twitch + YouTube only.
live=patched.split('<section class="view" data-view="live">',1)[1].split('</main>',1)[0]
if 'liveRootFolders' in live or 'data-live-pane="highlights"' in live:
    fail('legacy Live launcher/highlights pane remains')
if 'youtubeLiveFolders' not in live:
    fail('dedicated YouTube section missing')
ok('Live is Twitch + YouTube')

# Drafts no longer generates the old current-project/four-stat strip.
if '$("#projectRows").innerHTML=' in patched and '$("#projectRows").innerHTML="";' not in patched:
    fail('Bozze still renders current-project/stats source')
if '<div class="stats">' in patched:
    fail('Bozze four-stat strip is still generated')
ok('Bozze old project/stats source removed')

style_block=patched.split('<style id="v311HubForce">',1)[1].split('</style>',1)[0]
if '@media(' in style_block:
    fail('final Hub rules must not depend on iframe viewport width')
if 'data-v300-layout' in style_block:
    fail('final Hub rules must not depend on historical layout attributes')
for visual in ('width:76px!important','border-radius:26px!important','font-size:22px!important'):
    if visual not in style_block:
        fail('approved reference visual marker missing: '+visual)
ok('approved reference sizing is locked')

if mod.patch_hub_text(patched)!=patched:
    fail('Hub patch is not idempotent')
ok('Hub patch is idempotent')

# A restart runs V287 again against the already-normalized V311 source. That
# older migration must no-op instead of looking for legacy profile anchors.
with TemporaryDirectory() as tmp:
    tmp=Path(tmp)
    restart_hub=tmp/'hub.html'
    restart_app=tmp/'app.py'
    restart_hub.write_text(patched,encoding='utf-8')
    restart_app.write_text('HUB_URL="/creator-hub-v156/?v=3114"\n',encoding='utf-8')
    old_hub,old_app=mod287.HUB,mod287.APP
    mod287.HUB,mod287.APP=restart_hub,restart_app
    try:
        before_hub=restart_hub.read_text(encoding='utf-8')
        before_app=restart_app.read_text(encoding='utf-8')
        mod287.patch_hub()
        mod287.patch_shell()
        if restart_hub.read_text(encoding='utf-8')!=before_hub:
            fail('V287 changed an already-normalized V311 Hub on restart')
        if restart_app.read_text(encoding='utf-8')!=before_app:
            fail('V287 changed a newer V311 shell cache on restart')
    finally:
        mod287.HUB,mod287.APP=old_hub,old_app
ok('V287 is restart-safe after V311 normalization')

# Synthetic shell mirrors the semantic attributes generated before V311 but
# intentionally uses a different CSS class. V311 must not depend on one class.
shell_sample='''
<style>.mobile-gamebar-inner{grid-template-columns:repeat(5,minmax(0,1fr))}</style>
<div class="mobile-gamebar">
<button class="mobile-gamebar-item home-slot" data-target="home" type="button"><svg></svg><span>Home</span></button>
<button class="mobile-gamebar-item" data-target="hub" data-section="dashboard" data-active="hub" type="button"><svg></svg><span>Hub</span></button>
<button class="mobile-gamebar-item" data-target="hub" data-section="shorts" data-active="shorts" type="button"><svg></svg><span>I miei Shorts</span></button>
<button class="mobile-gamebar-item" data-target="hub" data-section="drafts" data-active="drafts" type="button"><svg></svg><span>Bozze</span></button>
<button class="mobile-gamebar-item" data-target="hub" data-section="live" data-active="live" type="button"><svg></svg><span>Live</span></button>
</div>
<script>
if(activeKey==='home') active=lastTarget==='home';
else if(activeKey==='shorts') active=(lastTarget==='hub'&&lastSection==='shorts');
else if(activeKey==='drafts') active=(lastTarget==='hub'&&lastSection==='drafts');
else if(activeKey==='live') active=(lastTarget==='hub'&&lastSection==='live');
else if(target==='hub') active=(lastTarget==='hub'&&lastSection!=='drafts'&&lastSection!=='shorts'&&lastSection!=='live');
const hubUrl="/creator-hub-v156/?v=307";
</script>
'''
shell_patched=mod.patch_shell_text(shell_sample)
if len(re.findall(r'<button\b',shell_patched)) != 4:
    fail('global Game Bar is not exactly four buttons')
if '<span>I miei Shorts</span>' in shell_patched or '<span>Bozze</span>' in shell_patched:
    fail('legacy Shorts/Bozze Game Bar buttons remain')
for marker in (
    'data-target="hub"',
    'data-section="dashboard"',
    'data-active="home"',
    'data-section="projects"',
    'data-active="projects"',
    '<span>Progetti</span>',
    'data-section="live"',
    "activeKey==='projects'",
    'grid-template-columns:repeat(4,minmax(0,1fr))',
    '/creator-hub-v156/?v=3114',
):
    if marker not in shell_patched: fail('Game Bar marker missing: '+marker)
ok('Game Bar rewrite follows semantic attributes, not historical CSS classes')
if mod.patch_shell_text(shell_patched)!=shell_patched:
    fail('Shell patch is not idempotent')
ok('Shell patch is idempotent')

# Production safety: if one optional Home button is absent, the Hub cache and
# remaining navigation must still patch without taking the whole service down.
no_home_shell='''
<div class="different-gamebar">
<button class="x" data-target="hub" data-section="dashboard" data-active="hub"><span>Hub</span></button>
<button class="x" data-target="hub" data-section="drafts" data-active="drafts"><span>Bozze</span></button>
<button class="x" data-target="hub" data-section="live" data-active="live"><span>Live</span></button>
</div>
const hubUrl="/creator-hub-v156/?v=307";
'''
try:
    no_home_patched=mod.patch_shell_text(no_home_shell)
except Exception as exc:
    fail('missing optional Home slot still crashes startup: '+repr(exc))
if '/creator-hub-v156/?v=3114' not in no_home_patched or '<span>Progetti</span>' not in no_home_patched:
    fail('safe fallback did not preserve cache/project rewrite')
ok('missing historical Home button can no longer crash production startup')

start=START.read_text(encoding='utf-8')
needle='python /app/web/fix_v311_mobile_hub_clean_pass.py /app/web/creator_hub_v156_component/index.html'
if needle not in start: fail('V311 startup patch not registered')
if start.index(needle)<start.index('python /app/web/test_v310_creator_hub_mobile_cleanup.py /app'):
    fail('V311 must run after V310')
if start.index(needle)>start.index('python /app/web/apply_v293_render_memory_guard.py'):
    fail('V311 must run before production app generation')
if 'V311_RESTART_SAFE' not in start or 'GSF_HISTORY_READY' not in start or 'touch "$GSF_V311_READY"' not in start:
    fail('startup restart-safe migration guard missing')
ok('startup order and restart-safe guard correct')

print('\nV311 APPROVED CREATOR HUB REFERENCE: PASS')
