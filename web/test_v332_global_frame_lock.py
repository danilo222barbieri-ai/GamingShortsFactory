#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
home=(root/'web/home_v154_component/index.html').read_text(encoding='utf-8')
shell=(root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py').read_text(encoding='utf-8')
start=(root/'web/start_web.sh').read_text(encoding='utf-8')
fix=(root/'web/fix_v332_global_frame_lock.py').read_text(encoding='utf-8')

checks={
  'Home frame lock style present':'v332HomeFrameLock' in home,
  'Home header forced visible':'.topbar{display:flex!important' in home,
  'Home Game Bar forced visible':'.bottomNav{display:grid!important' in home,
  'Home footer forced visible':'.siteFooter{display:grid!important' in home,
  'Home footer brand stays removed':'.footerBrand{display:none!important' in home,
  'Global frame lock present':'V332_GLOBAL_FRAME_LOCK' in shell,
  'Known internal pages drive chrome':'gsf-short-overlay-v331' in shell and 'gsf-editor-overlay-v220' in shell and 'gsf-ai-overlay-v221' in shell,
  'Global header is shown on internal pages':"brand.classList.toggle('show',internal)" in shell,
  'Global footer is shown on internal pages':"footer.classList.toggle('show',internal)" in shell,
  'Global Game Bar is fixed above footer':"bottom:'calc(var(--gsf-v330-footer-h,30px) + env(safe-area-inset-bottom))'" in shell,
  'Global Game Bar visibility is deterministic':'nav.style.visibility=internal' in shell,
  'V332 runs after V331':start.find('fix_v332_global_frame_lock.py')>start.find('fix_v331_primary_actions_routing.py')>=0,
  'V332 test runs before final app generation':start.find('test_v332_global_frame_lock.py')<start.find('apply_v293_render_memory_guard.py'),
  'V332 is idempotent':'if MARK not in shell' in fix,
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if failed: raise SystemExit('V332 global frame lock contract failed: '+', '.join(failed))
print('V332 GLOBAL FRAME LOCK CONTRACT: PASS')
