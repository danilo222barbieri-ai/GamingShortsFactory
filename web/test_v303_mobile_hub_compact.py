#!/usr/bin/env python3
from pathlib import Path

p = Path('/app/web/creator_hub_v156_component/index.html')
s = p.read_text(encoding='utf-8')
checks = {
    'v303 marker': 'V303 MOBILE HUB COMPACT' in s,
    'dashboard mural hidden mobile': '.view[data-view="dashboard"] .hubMural' in s and 'display:none!important' in s,
    'subscription tile hidden mobile': '.folder[data-folder="subscription"]' in s,
    'four mobile rows': 'grid-template-rows:repeat(4,minmax(0,1fr))!important' in s,
    'profile mural hidden mobile': '.view[data-view="profile"] .profileOnlyMural' in s,
    'mobile plan inside profile': 'mobileProfilePlanName' in s and 'mobileProfilePlanText' in s,
}
for name, ok in checks.items():
    if not ok:
        raise SystemExit(f'FAIL: {name}')
    print(f'PASS: {name}')
print('V303 mobile Creator Hub compact: PASS')
