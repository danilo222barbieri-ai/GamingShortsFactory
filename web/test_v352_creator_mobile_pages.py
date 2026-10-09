#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FIX = HERE / 'fix_v352_creator_mobile_pages.py'

BASE = '''<html><head><style id="v322MobileHubLiveFill"></style></head><body><main id="hub"><section class="view" data-view="projects"><div class="detail"><div class="detailHead"><div class="detailHeadText"><h2 id="projectsViewTitle">I miei progetti</h2><p id="projectsViewSubtitle">I miei Shorts e Bozze, nello stesso posto.</p></div></div><div class="detailCard"><div class="folderScroller"><div class="hubContextGuide hubProjectsGuide">Qui trovi i tuoi progetti</div><div id="projectHubCards"></div></div></div></div></section><section class="view" data-view="live"><div class="detail"><div class="detailHead"><div class="detailHeadText"><h2>Live</h2><p>Le tue dirette diventano una libreria di momenti.</p></div></div><div class="detailCard"><div class="folderScroller"><div class="hubContextGuide hubLiveGuide">Qui trovi e gestisci live</div><div class="livePane active livePlatformCard livePlatformTwitch"></div><div class="livePane livePlatformCard livePlatformYoutube"></div></div></div></div></section></main></body></html>'''

with tempfile.TemporaryDirectory() as td:
    hub = Path(td) / 'index.html'
    hub.write_text(BASE, encoding='utf-8')
    subprocess.run([sys.executable, str(FIX), str(hub)], check=True)
    out = hub.read_text(encoding='utf-8')

    required = [
        'v352CreatorMobilePages',
        'overflow-y:auto!important',
        'font-size:24px!important',
        'display:flex!important',
        'grid-template-rows:auto minmax(0,1fr)!important',
        'livePlatformCard',
        'min-height:68px!important',
        'padding:2px 2px 100px!important',
    ]
    for token in required:
        assert token in out, f'missing V352 token: {token}'

    once = out
    subprocess.run([sys.executable, str(FIX), str(hub)], check=True)
    assert hub.read_text(encoding='utf-8') == once, 'V352 must be restart-safe'

print('V352 CREATOR MOBILE PAGES: PASS', flush=True)
