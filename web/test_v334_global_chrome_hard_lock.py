#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
home=(root/'web/home_v154_component/index.html').read_text(encoding='utf-8')
shell=(root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py').read_text(encoding='utf-8')
start=(root/'web/start_web.sh').read_text(encoding='utf-8')
fix=(root/'web/fix_v334_global_chrome_hard_lock.py').read_text(encoding='utf-8')

checks={
  'Home reserves but hides duplicate header':'V334_GLOBAL_CHROME_HOME_SLOT' in home and '#home154 .topbar,' in home and 'visibility:hidden!important' in home,
  'Home reserves but hides duplicate Game Bar':'#home154 .bottomNav,' in home and 'height:62px!important' in home,
  'Home reserves but hides duplicate footer':'#home154 .siteFooter{' in home and 'height:30px!important' in home,
  'Parent header exists':'gsf-v334-header' in shell and 'GAMING SHORTS FACTORY' in shell,
  'Exact GSF alpha mark is used':'v334Mark' in shell and '-webkit-mask-image:url("${LOGO}")' in shell,
  'Parent Game Bar exists':'gsf-v334-gamebar' in shell and 'data-page="home"' in shell and 'data-page="projects"' in shell and 'data-page="live"' in shell,
  'Parent footer exists':'gsf-v334-footer' in shell and 'v334Socials' in shell and 'Segnala bug' in shell,
  'Chrome is fixed':'position:fixed' in shell and '--gsf-v334-head:44px' in shell and '--gsf-v334-foot:30px' in shell and '--gsf-v334-bar:62px' in shell,
  'Old parent chrome is suppressed':'#gsf-v330-global-brand,#gsf-v330-global-footer,#gsf-page-nav-v249' in shell,
  'Internal content reserves chrome':'gsf-short-overlay-v331' in shell and 'bottom:calc(var(--gsf-v334-foot) + var(--gsf-v334-bar)' in shell,
  'Canonical nav messages remain':'GSF_SHELL_NAV' in shell and "section:p==='hub'?'dashboard':p" in shell,
  'V334 patch is idempotent':'if MARK not in shell' in fix and 'V334_GLOBAL_CHROME_HOME_SLOT' in fix,
  'V334 runs after V333':start.find('fix_v334_global_chrome_hard_lock.py')>start.find('fix_v333_home_cta_touch_fix.py')>=0,
  'V334 validates before final app generation':start.find('test_v334_global_chrome_hard_lock.py')<start.find('apply_v293_render_memory_guard.py'),
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if failed: raise SystemExit('V334 global chrome hard lock contract failed: '+', '.join(failed))
print('V334 GLOBAL CHROME HARD LOCK CONTRACT: PASS')
