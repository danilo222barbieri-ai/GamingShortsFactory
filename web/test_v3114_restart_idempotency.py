#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import re
import sys
import tempfile

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'
HUB = WEB / 'creator_hub_v156_component' / 'index.html'
V287 = WEB / 'fix_v287_profile_overview.py'
V311 = WEB / 'fix_v311_mobile_hub_clean_pass.py'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


v287 = load('v287_restart', V287)
v311 = load('v311_restart', V311)
source = HUB.read_text(encoding='utf-8')

# Reproduce the first successful V287 -> V311 startup pass.
if 'id="profileOverviewShorts"' not in source:
    pattern = re.compile(
        r'\s*<div class="profileMural profileOnlyMural" aria-hidden="true">Questo è il tuo spazio,<br>fallo tuo</div>\s*'
        r'<button class="logoutProfile" id="logoutProfile" type="button">Disconnetti dal Creator Hub</button>'
    )
    source, count = pattern.subn('\n' + v287.OVERVIEW_HTML, source, count=1)
    if count != 1:
        raise SystemExit('RED fixture failed: could not simulate first V287 pass')
normalized = v311.patch_hub_text(source)

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    hub = tmp / 'hub.html'
    app = tmp / 'app.py'
    hub.write_text(normalized, encoding='utf-8')
    app.write_text('HUB_URL="/creator-hub-v156/?v=287"\n', encoding='utf-8')

    old_hub, old_app = v287.HUB, v287.APP
    v287.HUB, v287.APP = hub, app
    try:
        # This is exactly what a Railway container restart does: V287 executes
        # again against the already-normalized V311 Hub file.
        v287.patch_hub()
        v287.patch_shell()
    except Exception as exc:
        raise SystemExit(f'V311.4 restart regression: V287 is not restart-safe: {exc}') from exc
    finally:
        v287.HUB, v287.APP = old_hub, old_app

    restarted = hub.read_text(encoding='utf-8')
    profile = restarted.split('<section class="view" data-view="profile">', 1)[1].split('<section class="view" data-view="social">', 1)[0]
    if 'data-profile-overview="shorts"' in profile or 'data-profile-overview="drafts"' in profile:
        raise SystemExit('V311.4 restart regression: V287 reintroduced Shorts/Bozze into Profile')
    if 'data-profile-overview="subscription"' not in profile or 'data-profile-overview="social"' not in profile:
        raise SystemExit('V311.4 restart regression: plan/social portals were lost')

print('V311.4 restart idempotency: PASS')
