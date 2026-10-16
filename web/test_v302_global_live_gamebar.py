#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/app')
home = (root / 'web/home_v154_component/index.html').read_text(encoding='utf-8')
app = (root / 'app.py').read_text(encoding='utf-8')
lifecycle = (root / 'web/gsf_navigation_lifecycle.js').read_text(encoding='utf-8') if (root / 'web/gsf_navigation_lifecycle.js').exists() else ''
nav_match = re.search(r'<nav class="bottomNav".*?</nav>', home, flags=re.DOTALL)
home_nav = nav_match.group(0) if nav_match else ''
page_match = re.search(r'<nav id="gsf-global-gamebar".*?</nav>',app,flags=re.DOTALL)
page_nav = page_match.group(0) if page_match else ''

checks = [
    ('Home Game Bar has exactly four canonical destinations', bool(home_nav) and all(x in home_nav for x in ('data-nav="home"','data-nav="hub"','data-nav="projects"','data-nav="live"')) and 'data-nav="shorts"' not in home_nav and 'data-nav="social"' not in home_nav and home_nav.count('class="navItem') == 4),
    ('Home Hub always routes to Creator Hub dashboard', 'if(nav==="hub")shellNav("hub",{section:"dashboard"});' in home and 'if(nav==="hub")shellNav("hub",{section:"profile"});' not in home),
    ('Home Projects routes to project landing', 'if(nav==="projects"){shellNav("hub",{section:"projects"});' in home),
    ('Home Live routes to Hub live', 'if(nav==="live")shellNav("hub",{section:"live"});' in home),
    ('Page Game Bar has canonical Hub', 'data-page="hub"' in page_nav and "section:b.dataset.page==='hub'?'dashboard':''" in app),
    ('Page Game Bar has canonical Projects', 'data-page="projects"' in page_nav and "target==='projects'||target==='live'" in lifecycle and '<span>Progetti</span>' in app),
    ('Page Game Bar has canonical Live', 'data-page="live"' in page_nav and "target==='projects'||target==='live'" in lifecycle and '<span>Live</span>' in app),
    ('Hub active state is dashboard-only', ("activeKey==='hub'" in app and "lastSection==='dashboard'" in app) or ("const selected=current.target==='hub'?" in lifecycle and "current.section" in lifecycle)),
    ('Hub focus fallback is dashboard, not profile', ("t==='profile'?'profile':'dashboard'" in app or ("if (target==='profile'||target==='account') {target='hub';section='profile';}" in lifecycle and "section='dashboard'" in lifecycle)) and "t==='profile'?'profile':'profile'" not in app),
    ('Repeated Hub messages cannot inherit profile fallback', ("lastSection=String(e.data.section||'dashboard')" in app or ("let target=String(data.target||'home'), section=String(data.section||'');" in lifecycle and "section='dashboard'" in lifecycle)) and "lastSection=String(e.data.section||'profile')" not in app),
    ('Live icons retained in Home and parent shell', 'transform="rotate(-8 16 16)"' in home_nav and '<span class="v343Icon">◉</span><span>Live</span>' in page_nav),
]
failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(('PASS' if ok else 'FAIL') + ': ' + name)
if failed:
    raise SystemExit('V302 failed: ' + ', '.join(failed))
print('V302 canonical global Game Bar: PASS')
