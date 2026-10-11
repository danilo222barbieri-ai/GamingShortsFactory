#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
FIX = ROOT / 'fix_v374_creator_hub_spacing_live.py'
assert FIX.is_file(), 'V374 Creator Hub spacing/live patch is missing'

spec = importlib.util.spec_from_file_location('v374', FIX)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

fixture = '''<!doctype html><html><body>
<div id="hub"><div class="stage">
<section class="view" data-view="projects"><div class="detail"><div class="detailHead"><h2 id="projectsViewTitle">Bozze</h2></div></div></section>
<section class="view" data-view="live">
  <div class="v357LiveRoot">
    <button data-v357-live="twitch">Twitch</button>
    <button data-v357-live="youtube">YouTube</button>
  </div>
  <div class="v357LiveDetailBody">
    <div class="livePlatformCard livePlatformTwitch"><div class="liveMiniFolders"><div class="liveMiniFolder">Twitch categoria</div></div></div>
    <div class="livePlatformCard livePlatformYoutube"><div class="liveMiniFolders"><div class="liveMiniFolder">YouTube categoria</div></div></div>
  </div>
</section>
</div></div>
</body></html>'''

patched = mod.patch_text(fixture)
for token in (
    'V374_CREATOR_HUB_SPACING_LIVE_ISOLATION',
    '#hub>.stage>.view[data-view="projects"]{top:46px!important}',
    '#hub>.stage>.view[data-view="live"]{top:46px!important}',
    'data-v374-platform="twitch"',
    'data-v374-platform="youtube"',
    '.livePlatformYoutube{display:none!important}',
    '.livePlatformTwitch{display:none!important}',
    "name==='twitch'",
    "name==='youtube'",
):
    assert token in patched, f'missing V374 contract token: {token}'

assert mod.patch_text(patched) == patched, 'V374 patch must be idempotent'
print('V374 CREATOR HUB SPACING + LIVE PLATFORM ISOLATION CONTRACT: PASS')
