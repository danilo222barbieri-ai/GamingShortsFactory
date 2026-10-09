#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
home=(root/'web/home_v154_component/index.html').read_text(encoding='utf-8')
hub=(root/'web/creator_hub_v156_component/index.html').read_text(encoding='utf-8')
shell=(root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py').read_text(encoding='utf-8')
start=(root/'web/start_web.sh').read_text(encoding='utf-8')

legacy_short='if(!opened)shellNav("short")' in home
canonical_v331_short='if(action==="short"){shellNav("short")' in home
checks={
    'home footer brand removed':'<span class="footerBrand">Gaming Shorts Factory</span>' not in home,
    'home footer compact marker':'v328HomeBalance' in home and 'height:28px!important' in home,
    'home logo follows text color':'#home154 .brandOnly:before' in home and 'background:currentColor' in home,
    'home short routing is preserved':legacy_short or canonical_v331_short,
    'live page compact mobile marker':'v328LiveCompact' in hub,
    'live cards are compact':'grid-template-rows:repeat(3,74px)!important' in hub,
    'global balance bridge installed':'V328_GLOBAL_BALANCE' in shell,
    'global footer exists':'gsf-v328-global-footer' in shell,
    'global game bar is pinned above footer':'--gsf-v328-footer-h:28px' in shell and 'bottom:calc(var(--gsf-v328-footer-h) + env(safe-area-inset-bottom))' in shell,
    'global logo uses current color':'gsf-v328-brand-mark' in shell and 'background:currentColor' in shell,
    'create short shell bridge exists':"target==='short'" in shell and 'v328TriggerShort' in shell,
    'V327 editor bridge preserved':'V327_EDITOR_OPEN_BRIDGE' in shell,
    'V328 startup is explicit':'python /app/web/fix_v328_global_balance.py /app' in start and 'python /app/web/test_v328_global_balance.py /app' in start,
    'V311 restart guard recognizes V328':"grep -q 'V328_GLOBAL_BALANCE' \"$GSF_SHELL_APP\"" in start and 'V328 shell already finalized' in start,
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS: ' if v else 'FAIL: ')+k)
if failed: raise SystemExit('V328 global balance contract failed: '+', '.join(failed))
compile(shell,str(root/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'),'exec')
print('V328 GLOBAL BALANCE CONTRACT: PASS')
