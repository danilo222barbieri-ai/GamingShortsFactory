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

source=HUB.read_text(encoding='utf-8')
if "gsfHubVersion='3115'" in source and 'V311 APPROVED CREATOR REFERENCE' in source:
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
    'V311 LIVE REFERENCE LAYOUT',
    'id="v311HubForce"',
    'id="v311HubRuntime"',
    "gsfHubVersion='3115'",
    'id="projectHubCards"',
    'data-project-dest="shorts"',
    'data-project-dest="drafts"',
    'grid-template-rows:repeat(3,minmax(0,1fr))!important',
    'livePlatformCard livePlatformTwitch',
    'livePlatformCard livePlatformYoutube',
    'youtubeLiveFolders',
)
for marker in required:
    if marker not in patched: fail('missing marker: '+marker)
    ok('found '+marker)

# Dashboard remains Profile / Projects / Live only.
dashboard=patched.split('<section class="view active" data-view="dashboard">',1)[1].split('<section class="view" data-view="projects">',1)[0]
folders=re.findall(r'data-folder="([^"]+)"',dashboard)
if folders != ['profile','projects','live']:
    fail('dashboard destinations are not exactly profile/projects/live: '+repr(folders))
for forbidden in ('data-folder="social"','data-folder="subscription"','hubMural'):
    if forbidden in dashboard: fail('dashboard legacy node remains: '+forbidden)
if '<h2>Live</h2>' not in dashboard: fail('dashboard Live title missing')
ok('dashboard matches approved three-card structure')

# Profile stays account-only: plan + social.
profile=patched.split('<section class="view" data-view="profile">',1)[1].split('<section class="view" data-view="social">',1)[0]
if 'data-profile-overview="shorts"' in profile or 'data-profile-overview="drafts"' in profile:
    fail('Profile still contains Shorts/Bozze overview cards')
if profile.count('class="profileOverviewCard"') != 2:
    fail('Profile must contain exactly two overview cards')
if 'data-profile-overview="subscription"' not in profile or 'data-profile-overview="social"' not in profile:
    fail('Profile plan/social portals missing')
ok('Profile contains only plan and social overview destinations')

# Projects starts from My Shorts + Drafts.
projects=patched.split('<section class="view" data-view="projects">',1)[1].split('<section class="view" data-view="profile">',1)[0]
if projects.count('data-project-dest=') != 2:
    fail('Projects landing must expose exactly two destinations')
if 'data-project-dest="shorts"' not in projects or 'data-project-dest="drafts"' not in projects:
    fail('Projects landing missing Shorts or Bozze')
ok('Projects landing contains I miei Shorts + Bozze')

# Live matches the approved reference: no profile, no launchers, Twitch then YouTube.
live=patched.split('<section class="view" data-view="live">',1)[1].split('</main>',1)[0]
for forbidden in ('class="profileCard"','liveRootFolders','data-live-pane="highlights"'):
    if forbidden in live: fail('Live legacy element remains: '+forbidden)
for marker in (
    'livePlatformCard livePlatformTwitch',
    'Gestisci e riutilizza i contenuti delle tue live su Twitch.',
    'livePlatformCard livePlatformYoutube',
    'Gestisci e riutilizza i contenuti delle tue live su YouTube.',
):
    if marker not in live: fail('Live reference marker missing: '+marker)
if live.count('<b>Le tue live</b>') != 2 or live.count('<b>VOD</b>') != 2 or live.count('<b>Highlights</b>') != 2:
    fail('Live must expose three rows for both Twitch and YouTube')
if live.index('livePlatformTwitch') > live.index('livePlatformYoutube'):
    fail('Twitch must appear before YouTube')
ok('Live is profile-free Twitch + YouTube reference layout')

# Drafts old current-project/four-stat strip stays gone.
if '$("#projectRows").innerHTML=' in patched and '$("#projectRows").innerHTML="";' not in patched:
    fail('Bozze still renders current-project/stats source')
if '<div class="stats">' in patched: fail('Bozze four-stat strip is still generated')
ok('Bozze old project/stats source removed')

style_block=patched.split('<style id="v311HubForce">',1)[1].split('</style>',1)[0]
if 'data-v300-layout' in style_block: fail('final Hub rules depend on historical layout attributes')
for visual in ('width:76px!important','border-radius:26px!important','font-size:22px!important','.livePlatformCard','.livePlatformHead','.livePlatformIcon'):
    if visual not in style_block: fail('approved visual marker missing: '+visual)
ok('approved dashboard and Live sizing is locked')

if mod.patch_hub_text(patched)!=patched: fail('Hub patch is not idempotent')
ok('Hub patch is idempotent')

# The isolated Live normalizer must also remove an accidentally injected profile.
live_sample='''<section class="view" data-view="live"><div class="profileCard">BAD PROFILE</div><div class="detail"><div class="detailCard"><div class="folderScroller"><div class="liveRootFolders">old</div><div class="livePane active" data-live-pane="twitch"><div class="livePaneTitle">Twitch</div></div><div class="livePane" data-live-pane="youtube"><div class="livePaneTitle">YouTube Live</div></div><div class="livePane" data-live-pane="highlights"><div>x</div><div>y</div></div></div></div></div></section>'''
normalized=mod.normalize_live_reference(live_sample)
if 'BAD PROFILE' in normalized or 'liveRootFolders' in normalized or 'data-live-pane="highlights"' in normalized:
    fail('isolated Live normalizer left legacy/profile content')
if 'livePlatformTwitch' not in normalized or 'livePlatformYoutube' not in normalized:
    fail('isolated Live normalizer did not build both platform cards')
ok('isolated Live normalizer is structural and profile-free')

# V287 must no-op on an already-normalized V311 Hub.
with TemporaryDirectory() as tmp:
    tmp=Path(tmp)
    restart_hub=tmp/'hub.html'; restart_app=tmp/'app.py'
    restart_hub.write_text(patched,encoding='utf-8')
    restart_app.write_text('HUB_URL="/creator-hub-v156/?v=3115"\n',encoding='utf-8')
    old_hub,old_app=mod287.HUB,mod287.APP
    mod287.HUB,mod287.APP=restart_hub,restart_app
    try:
        before_hub=restart_hub.read_text(encoding='utf-8'); before_app=restart_app.read_text(encoding='utf-8')
        mod287.patch_hub(); mod287.patch_shell()
        if restart_hub.read_text(encoding='utf-8')!=before_hub: fail('V287 changed normalized V311 Hub')
        if restart_app.read_text(encoding='utf-8')!=before_app: fail('V287 changed newer V311 shell cache')
    finally:
        mod287.HUB,mod287.APP=old_hub,old_app
ok('V287 is restart-safe after V311 normalization')

shell_sample='''
<style>.mobile-gamebar-inner{grid-template-columns:repeat(5,minmax(0,1fr))}</style>
<div class="mobile-gamebar">
<button class="mobile-gamebar-item home-slot" data-target="home" type="button"><span>Home</span></button>
<button class="mobile-gamebar-item" data-target="hub" data-section="dashboard" data-active="hub" type="button"><span>Hub</span></button>
<button class="mobile-gamebar-item" data-target="hub" data-section="shorts" data-active="shorts" type="button"><span>I miei Shorts</span></button>
<button class="mobile-gamebar-item" data-target="hub" data-section="drafts" data-active="drafts" type="button"><span>Bozze</span></button>
<button class="mobile-gamebar-item" data-target="hub" data-section="live" data-active="live" type="button"><span>Live</span></button>
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
if len(re.findall(r'<button\b',shell_patched)) != 4: fail('global Game Bar is not exactly four buttons')
if '<span>I miei Shorts</span>' in shell_patched or '<span>Bozze</span>' in shell_patched: fail('legacy Game Bar slots remain')
for marker in ('data-section="dashboard"','data-active="home"','data-section="projects"','data-active="projects"','<span>Progetti</span>','data-section="live"',"activeKey==='projects'",'grid-template-columns:repeat(4,minmax(0,1fr))','/creator-hub-v156/?v=3115'):
    if marker not in shell_patched: fail('Game Bar marker missing: '+marker)
ok('Game Bar rewrite and v3115 cache key correct')
if mod.patch_shell_text(shell_patched)!=shell_patched: fail('Shell patch is not idempotent')
ok('Shell patch is idempotent')

start=START.read_text(encoding='utf-8')
needle='python /app/web/fix_v311_mobile_hub_clean_pass.py /app/web/creator_hub_v156_component/index.html'
after_v310='python /app/web/test_v310_creator_hub_mobile_cleanup.py /app'
production_generation='python /app/web/apply_v343_v293_compat.py'
for anchor,label in ((needle,'V311 startup patch'),(after_v310,'V310 cleanup test'),(production_generation,'V343/V293 production generation')):
    if anchor not in start: fail(label+' anchor is not registered')
if start.index(needle)<start.index(after_v310): fail('V311 must run after V310')
if start.index(needle)>start.index(production_generation): fail('V311 must run before production app generation')
if 'V311_RESTART_SAFE' not in start or 'GSF_HISTORY_READY' not in start or 'touch "$GSF_V311_READY"' not in start: fail('startup restart-safe migration guard missing')
ok('startup order and restart-safe guard correct')

print('\nV311.5 APPROVED CREATOR HUB + LIVE REFERENCE: PASS')
