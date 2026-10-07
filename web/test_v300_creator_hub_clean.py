#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/app')
hub = (root / 'web/creator_hub_v156_component/index.html').read_text(encoding='utf-8')
app = (root / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py').read_text(encoding='utf-8')

checks = [
    ('V300 marker exists', 'V300 CREATOR HUB CLEAN REBUILD' in hub),
    ('V300 root marker exists', 'data-v300-layout="hub"' in hub),
    ('V297 Hub sidebar removed', 'v297HubSidebar' not in hub),
    ('V297 Hub CSS removed', 'V297 DESK REBUILD — HUB' not in hub),
    ('internal top nav hidden', '#hub[data-v300-layout="hub"]>.top{display:none!important}' in hub),
    ('real V287 profile overview preserved', 'profileOverviewGrid' in hub),
    ('profile routes Shorts directly', 'data-profile-overview="shorts"' in hub),
    ('profile routes Drafts directly', 'data-profile-overview="drafts"' in hub),
    ('profile routes Social directly', 'data-profile-overview="social"' in hub),
    ('profile routes Subscription directly', 'data-profile-overview="subscription"' in hub),
    ('Creator Hub cache is V300', '/creator-hub-v156/?v=300' in app),
]
folders = re.findall(r'<button class="folder" data-folder="([^"]+)"', hub)
checks.append(('dashboard has exactly five folders', folders == ['profile','projects','live','social','subscription']))
for view in ('dashboard','projects','profile','live','social','subscription'):
    checks.append((f'{view} view preserved', f'data-view="{view}"' in hub))

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(('PASS' if ok else 'FAIL') + ': ' + name)
if failed:
    raise SystemExit('V300 Creator Hub contract failed: ' + ', '.join(failed))
print('V300 Creator Hub clean rebuild: PASS')
