#!/usr/bin/env python3
"""Compatibility bridge for build-time replay of legacy runtime migrations.

The V404 Crea con IA rewrite replaced the old ai221 DOM. Historical migrations
still contain useful Home, Editor, Hub, nginx and server work, so this helper
runs only those safe portions while preserving the new ai404 component.
"""
from pathlib import Path
import importlib.util
import py_compile
import subprocess
import sys

ROOT = Path('/app')
WEB = ROOT / 'web'
AI = WEB / 'ai_v221_component' / 'index.html'
HOME = WEB / 'home_v154_component' / 'index.html'
EDITOR = WEB / 'editor_2027_component' / 'index.html'
APP = ROOT / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
HUB = WEB / 'creator_hub_v156_component' / 'index.html'
SERVER = WEB / 'direct_upload_server.py'
NGINX = WEB / 'nginx.conf.template'


def fail(message):
    raise SystemExit('V404 legacy compatibility: ' + message)


def load(filename, name):
    path = WEB / filename
    if not path.is_file():
        fail('missing helper: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_ai404():
    if not AI.is_file() or 'id="ai404"' not in AI.read_text(encoding='utf-8'):
        fail('ai404 component not detected')


def run_v404_contract():
    subprocess.run([sys.executable, str(WEB / 'test_v404_crea_con_ia_simple.py')], check=True)


def migrate_v288():
    require_ai404()
    mod = load('fix_v288_ai_journey.py', 'v288_compat')
    # Preserve V404 AI. The Home/Editor/shell bridge remains useful.
    mod.patch_home()
    mod.patch_editor()
    mod.patch_app()
    print('V404 compat V288: preserved ai404; Home/Editor/shell migrated', flush=True)


def test_v288():
    require_ai404()
    run_v404_contract()
    home = HOME.read_text(encoding='utf-8')
    editor = EDITOR.read_text(encoding='utf-8')
    app = APP.read_text(encoding='utf-8')
    checks = {
        'Home V288 bridge': 'V288 AI JOURNEY BRIDGE' in home,
        'Editor V288 bridge': 'V288 EDITOR TO SHORT' in editor,
        'Shell V288 bridge': 'V288 EDITOR JOURNEY BRIDGE' in app,
    }
    bad = [name for name, ok in checks.items() if not ok]
    if bad:
        fail('V288 safe bridge missing: ' + ', '.join(bad))
    print('V404 compat V288 contract: PASS', flush=True)


def migrate_v308():
    require_ai404()
    # V308 was exclusively an ai221 mobile-preview migration. V404 owns its
    # own responsive layout and preview bridge, so no mutation is valid here.
    print('V404 compat V308: obsolete ai221 mutation skipped', flush=True)


def test_v308():
    require_ai404()
    # V307 intentionally purges historical viewport media blocks immediately
    # before this step. The authoritative replacement is therefore the V404
    # functional contract plus the component's responsive viewport declaration,
    # not the presence of a specific legacy @media rule.
    run_v404_contract()
    ai = AI.read_text(encoding='utf-8')
    if '<meta name="viewport"' not in ai or 'width=device-width' not in ai:
        fail('V404 viewport contract missing after V307 normalization')
    print('V404 compat V308 replacement contract: PASS', flush=True)


def migrate_v316():
    require_ai404()
    mod = load('fix_v316_creator_hub_dashboard_ad.py', 'v316_compat')
    if not HUB.is_file():
        fail('Creator Hub missing')

    before = HUB.read_text(encoding='utf-8')
    after = mod.patch_text(before)
    HUB.write_text(after, encoding='utf-8')
    print('V404 compat V316 Hub dashboard ad changed=', before != after, flush=True)

    # Keep Hub/Live migrations, but skip V317 and V320 because they target the
    # retired ai221 DOM.
    mod._apply_v318(HUB)

    # V319 also carries the live /ai/results backend + nginx route and an
    # optional Home nonce. Apply those portions only; preserve ai404 itself.
    v319 = load('fix_v319_ai_results_bridge.py', 'v319_compat')
    v319.ROOT = ROOT
    v319.SERVER = SERVER
    v319.NGINX = NGINX
    v319.HOME = HOME
    v319._write(SERVER, v319.patch_server_text, 'AI results endpoint')
    v319._write(NGINX, v319.patch_nginx_text, 'nginx AI results route')
    v319._write(HOME, v319.patch_home_text, 'Home create nonce bridge')
    py_compile.compile(str(SERVER), doraise=True)

    mod._apply_v321(HUB)
    mod._apply_v322(HUB)
    print('V404 compat V316: Hub/Live + V319 backend migrated; ai404 preserved', flush=True)


def test_v316():
    require_ai404()
    run_v404_contract()
    hub = HUB.read_text(encoding='utf-8')
    server = SERVER.read_text(encoding='utf-8')
    nginx = NGINX.read_text(encoding='utf-8')
    checks = {
        'V316 dashboard ad': 'id="hubDashboardAd"' in hub and 'id="v316HubDashboardAd"' in hub,
        'V318 Hub/Live fit': 'id="v318HubFillLiveFit"' in hub,
        'V321 Live balance': 'id="v321LiveMobileBalance"' in hub,
        'V319 results backend': '# V319 AI RESULTS BRIDGE' in server and '# V319 AI RESULTS ROUTE' in server,
        'V319 nginx route': '# V319 AI RESULTS NGINX' in nginx and 'location = /ai/results' in nginx,
    }
    bad = [name for name, ok in checks.items() if not ok]
    if bad:
        fail('V316 replacement contract missing: ' + ', '.join(bad))
    print('V404 compat V316 replacement contract: PASS', flush=True)


def main():
    if len(sys.argv) != 2:
        fail('usage: v404_legacy_runtime_compat.py v288|test-v288|v308|test-v308|v316|test-v316')
    command = sys.argv[1]
    actions = {
        'v288': migrate_v288,
        'test-v288': test_v288,
        'v308': migrate_v308,
        'test-v308': test_v308,
        'v316': migrate_v316,
        'test-v316': test_v316,
    }
    action = actions.get(command)
    if action is None:
        fail('unknown command: ' + command)
    action()


if __name__ == '__main__':
    main()
