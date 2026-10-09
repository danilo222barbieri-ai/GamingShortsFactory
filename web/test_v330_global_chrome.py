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
v330=app.split('V330_GLOBAL_CHROME',1)[-1] if 'V330_GLOBAL_CHROME' in app else ''

checks=[
    ('home V330 marker','id="v330HomeChrome"' in home),
    ('home logo mask is V330 transparent asset','--gsf-v330-logo' in home and 'v330HomeChrome' in home),
    ('home broken V328 logo overridden','#home154 .brandOnly:before' in home and 'var(--gsf-v330-logo)' in home),
    ('home footer remains visible','.siteFooter' in home and '--gsf-v330-footer-h' in home),
    ('home footer brand stays removed','.footerBrand{display:none!important}' in home),
    ('home fixed viewport restored','height:100dvh!important' in home and 'overflow:hidden!important' in home),
    ('home still owns all social links',home.count('class="footerSocialLink"') >= 5),
    ('global V330 shell marker','V330_GLOBAL_CHROME' in app),
    ('broken V328 inline mark disabled','.gsf-v328-brand-mark{display:none!important}' in v330),
    ('correct inline brand mark exists','.gsf-v330-inline-mark' in v330),
    ('global fallback brand exists','gsf-v330-global-brand' in v330),
    ('global footer exists','gsf-v330-global-footer' in v330),
    ('global footer has no footer brand','footerBrand' not in v330),
    ('global footer clones Home socials',"querySelectorAll('#home154 .footerSocialLink')" in v330),
    ('footer includes bug action','Segnala bug' in v330),
    ('global chrome tracks overlays','overlayOpen' in v330 and 'syncChrome' in v330),
    ('game bar pinned above footer','--gsf-v330-footer-h' in v330 and 'bottom:calc(var(--gsf-v330-footer-h)' in v330),
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
