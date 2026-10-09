#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
home=(root/'web/home_v154_component/index.html').read_text(encoding='utf-8')
start=(root/'web/start_web.sh').read_text(encoding='utf-8')
fix=(root/'web/fix_v333_home_cta_touch_fix.py').read_text(encoding='utf-8')
checks={
 'V333 style present':'v333HomeCtaTouchFix' in home,
 'murals never capture taps':'#home154 .muralGuide,#home154 .muralGuide *,#home154 .muralAmbient,#home154 .muralAmbient *{pointer-events:none!important}' in home,
 'feature row above murals':'#home154 .features{position:relative!important;z-index:60!important' in home,
 'features accept touch':'#home154 .feature{pointer-events:auto!important;touch-action:manipulation!important' in home,
 'direct editor opener':'GSF_V333_OPEN_EDITOR' in home and "/editor-live/?v=333" in home,
 'direct short opener':'GSF_V333_OPEN_SHORT' in home and "target:'short'" in home,
 'touchend binding':'touchend' in home,
 'click fallback binding':"addEventListener('click'" in home,
 'startup runs V333 after V332':start.find('fix_v333_home_cta_touch_fix.py')>start.find('fix_v332_global_frame_lock.py')>=0,
 'startup validates before final generation':start.find('test_v333_home_cta_touch_fix.py')<start.find('apply_v293_render_memory_guard.py'),
 'idempotent':'v333HomeCtaTouchFix' in fix,
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if failed: raise SystemExit('V333 home CTA touch contract failed: '+', '.join(failed))
print('V333 HOME CTA TOUCH CONTRACT: PASS')
