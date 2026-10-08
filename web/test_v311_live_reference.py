#!/usr/bin/env python3
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "web" / "fix_v311_mobile_hub_clean_pass.py"

spec = importlib.util.spec_from_file_location("v311_live", PATCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

sample = '''
<section class="view" data-view="live">
 <div class="profileCard">PROFILE MUST NOT BE HERE</div>
 <div class="detail">
  <div class="detailHead"><div class="detailHeadText"><h2>Live</h2></div></div>
  <div class="detailCard"><div class="folderScroller">
   <div class="liveRootFolders"><button>Twitch</button><button>YouTube</button></div>
   <div class="livePane active" data-live-pane="twitch">
    <div class="livePaneTitle">Twitch</div>
    <div class="liveMiniFolders">
     <button class="liveMiniFolder"><span>▣</span><div><b>Le tue live</b><small>old</small></div><i>›</i></button>
     <button class="liveMiniFolder"><span>▶</span><div><b>VOD</b><small>old</small></div><i>›</i></button>
     <button class="liveMiniFolder"><span>✦</span><div><b>Highlights</b><small>old</small></div><i>›</i></button>
    </div>
   </div>
   <div class="livePane" data-live-pane="youtube"><div class="livePaneTitle">YouTube Live</div></div>
   <div class="livePane" data-live-pane="highlights"><div>legacy</div></div>
  </div></div>
 </div>
</section>
'''

out = mod.normalize_live_reference(sample)

assert 'PROFILE MUST NOT BE HERE' not in out, 'Live page still contains the profile card'
assert 'liveRootFolders' not in out, 'Legacy Live launchers still present'
assert 'data-live-pane="highlights"' not in out, 'Legacy highlights pane still present'
assert 'livePlatformCard livePlatformTwitch' in out, 'Twitch reference card missing'
assert 'livePlatformCard livePlatformYoutube' in out, 'YouTube reference card missing'
assert 'Gestisci e riutilizza i contenuti delle tue live su Twitch.' in out
assert 'Gestisci e riutilizza i contenuti delle tue live su YouTube.' in out
assert out.count('<b>Le tue live</b>') == 2
assert out.count('<b>VOD</b>') == 2
assert out.count('<b>Highlights</b>') == 2

style = mod.STYLE
for marker in (
    'V311 LIVE REFERENCE LAYOUT',
    '.livePlatformCard',
    '.livePlatformHead',
    '.livePlatformIcon',
    '.livePlatformTwitch',
    '.livePlatformYoutube',
):
    assert marker in style, f'missing Live visual marker: {marker}'

print('V311 LIVE REFERENCE: PASS')
