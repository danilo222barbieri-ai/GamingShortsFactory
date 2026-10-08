#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PATCH = ROOT / 'web' / 'fix_v314_hub_context_fill.py'
V315 = ROOT / 'web' / 'fix_v315_mobile_home_lower_flow.py'
START = ROOT / 'web' / 'start_web.sh'


def fail(msg: str) -> None:
    print('[FAIL]', msg)
    raise SystemExit(1)


def ok(msg: str) -> None:
    print('[ OK ]', msg)


if not PATCH.is_file():
    fail('V314 Hub context/fill patch missing')
if not V315.is_file():
    fail('V315 mobile Home lower-flow patch missing')

spec = importlib.util.spec_from_file_location('v314_hub_context_fill', PATCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

sample = '''
<html><head></head><body>
<div id="hub">
  <section class="view" data-view="projects">
    <div class="folderScroller"><div id="projectHubCards"></div></div>
  </section>
  <section class="view" data-view="live">
    <div class="detailCard"><div class="folderScroller">
      <div class="livePane active livePlatformCard livePlatformTwitch" data-live-pane="twitch"></div>
      <div class="livePane livePlatformCard livePlatformYoutube" data-live-pane="youtube"></div>
    </div></div>
  </section>
</div>
<!-- V311 APPROVED CREATOR REFERENCE -->
</body></html>
'''

patched = mod.patch_text(sample)

checks = {
    'projects guide': 'Qui trovi i tuoi progetti: Shorts completati e bozze da riprendere quando vuoi.',
    'live guide': 'Qui trovi e gestisci live, VOD e Highlights da Twitch e YouTube.',
    'style marker': 'id="v314HubContextFill"',
    'live full-height grid': 'grid-template-rows:auto repeat(2,minmax(0,1fr))!important',
    'live cards stretch': 'height:100%!important',
    'three live rows stretch': 'grid-template-rows:repeat(3,minmax(0,1fr))!important',
}
for name, marker in checks.items():
    if marker not in patched:
        fail(name + ' missing')
    ok(name)

if patched.count('hubProjectsGuide') != 1:
    fail('projects guide duplicated')
if patched.count('hubLiveGuide') != 1:
    fail('live guide duplicated')
if mod.patch_text(patched) != patched:
    fail('V314 patch is not idempotent')
ok('V314 patch is idempotent')

source = PATCH.read_text(encoding='utf-8')
for marker in ('fix_v315_mobile_home_lower_flow.py', '_apply_v315_mobile_home_lower_flow()', '/app/web/home_v154_component/index.html'):
    if marker not in source:
        fail('V315 final runtime delegation missing: ' + marker)
ok('V315 mobile Home lower-flow is delegated from V314 final pass')

v315_spec = importlib.util.spec_from_file_location('v315_mobile_home_lower_flow', V315)
v315_mod = importlib.util.module_from_spec(v315_spec)
v315_spec.loader.exec_module(v315_mod)
home_sample = '''<html><head></head><body><div id="home154"><div class="stage"><div class="muralAmbient muralGuide">x</div><div class="rings"></div></div><div class="features"></div><nav class="bottomNav"></nav><footer class="siteFooter"></footer></div></body></html>'''
home_patched = v315_mod.patch_text(home_sample)
for marker in ('--gsf-home-lower-shift:clamp(14px,2.5vh,22px)!important', 'bottom:calc(1px - var(--gsf-home-lower-shift))!important', 'margin-bottom:12px!important'):
    if marker not in home_patched:
        fail('V315 mobile Home contract missing: ' + marker)
if v315_mod.patch_text(home_patched) != home_patched:
    fail('V315 patch is not idempotent')
ok('V315 mobile Home lower-flow contract')

if START.is_file():
    start = START.read_text(encoding='utf-8')
    patch_marker = 'python /app/web/fix_v314_hub_context_fill.py /app/web/creator_hub_v156_component/index.html'
    test_marker = 'python /app/web/test_v314_hub_context_fill.py /app'
    if patch_marker not in start or test_marker not in start:
        fail('V314 startup registration missing')
    if start.index(patch_marker) < start.index('python /app/web/fix_v313_mobile_profile_fit.py'):
        fail('V314 must run after V313')
    if start.index(test_marker) < start.index(patch_marker):
        fail('V314 test must run after patch')
    ok('V314/V315 startup order')

print('\nV314 HUB CONTEXT + LIVE FILL + V315 HOME FLOW CONTRACT: PASS')
