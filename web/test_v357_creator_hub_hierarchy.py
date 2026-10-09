#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FIX = HERE / 'fix_v357_creator_hub_hierarchy.py'
START = HERE / 'start_web.sh'

FIXTURE = r'''<!doctype html><html><head>
<!-- V311 APPROVED CREATOR REFERENCE -->
<style id="v352CreatorMobilePages"></style>
</head><body>
<div id="hub">
  <div class="top"><h1>Creator Hub</h1><p class="subtitle">legacy</p></div>
  <div class="stage">
    <section class="view" data-view="projects"><div class="detail"><div class="detailHead"><div class="detailHeadText"><h2 id="projectsViewTitle">I miei progetti</h2><p id="projectsViewSubtitle">I miei Shorts e Bozze</p></div></div><div class="detailCard"><div class="folderScroller"><div id="projectHubCards"></div></div></div></div></section>
    <section class="view" data-view="live"><div class="detail"><div class="detailHead"><div class="detailHeadText"><h2>Live</h2></div></div><div class="detailCard"><div class="folderScroller"><div class="hubLiveGuide">guide</div><div class="livePlatforms">
      <div class="livePane livePlatformCard livePlatformTwitch" data-live-pane="twitch"><div class="livePlatformHead"><span class="livePlatformIcon">T</span><div><div class="livePaneTitle">Twitch</div></div></div><div class="liveMiniFolders"><button class="liveMiniFolder" data-live-mini="sessions">live</button><button class="liveMiniFolder" data-live-mini="vod">vod</button><button class="liveMiniFolder" data-live-mini="twitch-highlights">highlights</button></div></div>
      <div class="livePane livePlatformCard livePlatformYoutube" data-live-pane="youtube"><div class="livePlatformHead"><span class="livePlatformIcon">Y</span><div><div class="livePaneTitle">YouTube</div></div></div><div class="liveMiniFolders youtubeLiveFolders"><div class="liveMiniFolder">live</div><div class="liveMiniFolder">vod</div><div class="liveMiniFolder">highlights</div></div></div>
    </div></div></div></div></section>
    <section class="view" data-view="profile"><div class="profileReferenceScroll"><div class="profileReferenceBrand">brand</div><div class="profileReferenceCard profileReferenceEdit">profile</div><div class="profileReferenceCard profilePlanRef">plan</div><div class="profileReferenceCard profileSocialRef"><div class="profileSocialRefHead"><div class="profileRefSectionIcon">S</div><div class="profileRefSectionText"><h2>Social collegati</h2></div></div><div class="profileSocialRows"><div class="profileSocialRefRow" data-platform="youtube">youtube</div><div class="profileSocialRefRow" data-platform="tiktok">tiktok</div><div class="profileSocialRefRow" data-platform="instagram">instagram</div><div class="profileSocialRefRow" data-platform="facebook">facebook</div><div class="profileSocialRefRow" data-platform="twitch">twitch</div></div></div></div></section>
  </div>
</div>
</body></html>'''


def main() -> None:
    assert FIX.is_file(), 'V357 fix script missing'
    with tempfile.TemporaryDirectory() as td:
        hub = Path(td) / 'index.html'
        hub.write_text(FIXTURE, encoding='utf-8')
        subprocess.run([sys.executable, str(FIX), str(hub)], check=True)
        out = hub.read_text(encoding='utf-8')

        required = [
            'V357_CREATOR_HUB_HIERARCHY',
            'id="v357CreatorHubHierarchy"',
            '@media(max-width:767px)',
            'v357NoLegacyTop',
            'data-view="projects"',
            'data-view="live"',
            'v357LiveRoot',
            'data-v357-live="twitch"',
            'data-v357-live="youtube"',
            'v357LiveBack',
            'v357LiveDetail',
            'openLivePlatform',
            'closeLivePlatform',
            'v357SocialBack',
            'v357SocialOpen',
            'openSocialDetail',
            'closeSocialDetail',
            'profileSocialRows',
            'profileSocialRefRow',
            "f.dataset.v357Bound='1'",
        ]
        for token in required:
            assert token in out, f'missing V357 contract token: {token}'

        assert 'cloneNode(' not in out, 'V357 must reuse original Live/social nodes, not clone functional rows'
        assert '#hub.v357NoLegacyTop>.top{display:none!important}' in out, 'Projects/Live legacy header must be suppressed'
        assert '#hub .view[data-view="profile"] .profileReferenceScroll' in out, 'Profile mobile spacing override missing'
        assert '#hub .view[data-view="live"] .folderScroller' in out and 'overflow:hidden!important' in out, 'Live root must not vertically scroll'

        once = out
        subprocess.run([sys.executable, str(FIX), str(hub)], check=True)
        assert hub.read_text(encoding='utf-8') == once, 'V357 patch must be restart-safe'

    assert START.is_file(), 'start_web.sh missing'
    start = START.read_text(encoding='utf-8')
    v352 = start.index('fix_v352_creator_mobile_pages.py')
    v357 = start.index('fix_v357_creator_hub_hierarchy.py')
    assert v357 > v352, 'V357 must run after V352'
    assert 'test_v357_creator_hub_hierarchy.py' in start, 'V357 startup test missing'
    assert "grep -q 'V357_CREATOR_HUB_HIERARCHY'" in start, 'V357 startup marker guard missing'

    print('V357 CREATOR HUB HIERARCHY: PASS', flush=True)


if __name__ == '__main__':
    main()
