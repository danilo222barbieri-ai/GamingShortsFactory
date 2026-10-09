#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
HOME=ROOT/'web/home_v154_component/index.html'
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
START=ROOT/'web/start_web.sh'

home=HOME.read_text(encoding='utf-8')
app=APP.read_text(encoding='utf-8')
start=START.read_text(encoding='utf-8')

checks=[
    ('home V330 marker','id="v330HomeChrome"' in home),
    ('home logo mask is V330 transparent asset','--gsf-v330-logo' in home and 'v330HomeChrome' in home),
    ('home broken V328 logo overridden','#home154 .brandOnly:before' in home and 'var(--gsf-v330-logo)' in home),
    ('home footer remains visible','.siteFooter' in home and '--gsf-v330-footer-h' in home),
    ('home footer brand stays removed','.footerBrand{display:none!important}' in home),
    ('home fixed viewport restored','height:100dvh!important' in home and 'overflow:hidden!important' in home),
    ('global V330 shell marker','V330_GLOBAL_CHROME' in app),
    ('broken V328 inline mark disabled','.gsf-v328-brand-mark{display:none!important}' in app),
    ('correct inline brand mark exists','.gsf-v330-inline-mark' in app),
    ('global fallback brand exists','gsf-v330-global-brand' in app),
    ('global footer exists','gsf-v330-global-footer' in app),
    ('footer has no GSF brand','Gaming Shorts Factory</span>' not in app.split('V330_GLOBAL_CHROME',1)[-1]),
    ('footer has five social destinations',all(x in app.split('V330_GLOBAL_CHROME',1)[-1] for x in ('Facebook','Instagram','YouTube','TikTok','Twitch'))),
    ('footer includes bug action','Segnala bug' in app.split('V330_GLOBAL_CHROME',1)[-1]),
    ('global chrome tracks overlays','overlayOpen' in app and 'syncChrome' in app),
    ('game bar pinned above footer','--gsf-v330-footer-h' in app and 'bottom:calc(var(--gsf-v330-footer-h)' in app),
    ('V330 startup apply','fix_v330_global_chrome.py /app' in start),
    ('V330 startup verify','test_v330_global_chrome.py /app' in start),
]

for label,ok in checks:
    if not ok:
        raise AssertionError('V330 failed: '+label)
    print('PASS:',label)

order=(
    start.index('fix_v329_worker_cost_guard.py'),
    start.index('fix_v330_global_chrome.py'),
    start.index('apply_v293_render_memory_guard.py'),
)
assert order[0] < order[1] < order[2], 'V330 startup order wrong'
print('PASS: V330 startup order')
print('V330 GLOBAL HEADER + FOOTER CONTRACT: PASS')
