#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
HUB = ROOT / 'web' / 'creator_hub_v156_component' / 'index.html'
BOOT = ROOT / 'web' / 'fix_v365_creator_hub_bootstrap.py'
TOUCH = ROOT / 'web' / 'fix_v368_creator_hub_touch_recovery.py'


def ok(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError('FAIL: ' + label)
    print('[ OK ] ' + label, flush=True)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


ok(HUB.is_file(), 'Creator Hub source exists')
ok(BOOT.is_file(), 'V365 bootstrap fix exists')
ok(TOUCH.is_file(), 'V368 touch fix exists')

boot = load_module('fix_v365_creator_hub_bootstrap_v369', BOOT)
touch = load_module('fix_v368_creator_hub_touch_recovery_v369', TOUCH)

source = HUB.read_text(encoding='utf-8')
patched = touch.patch_text(boot.patch_text(source))

# The base Hub must own navigation through one native handler path.
ok('$$("[data-view]").forEach' in patched, 'view collection uses querySelectorAll helper')
ok('$$("[data-project-pane]").forEach' in patched, 'project panes use querySelectorAll helper')
ok('$$(".socialDot").forEach' in patched, 'social dots use querySelectorAll helper')
ok('$$(".folder").forEach(b=>b.onclick=()=>openView(b.dataset.folder));' in patched, 'native folder navigation remains installed')
ok('$$(".backBtn").forEach(b=>b.onclick=()=>openView("dashboard"));' in patched, 'native back navigation remains installed')

marker = patched.index('V368_CREATOR_HUB_TOUCH_RECOVERY')
runtime = patched[marker:]

# Regression: the Safari recovery layer must never become a second action router.
ok('function v368RepairActiveView()' in runtime, 'V368 still repairs Hub visibility and pointer state')
ok('function v368HubAction(' not in runtime, 'V368 does not duplicate Hub actions')
ok("document.addEventListener('pointerup'" not in runtime, 'no capture pointerup router')
ok("document.addEventListener('click'" not in runtime, 'no document capture click router')
ok('stopPropagation()' not in runtime, 'recovery layer never blocks native propagation')
ok('preventDefault()' not in runtime, 'recovery layer never cancels native input')
ok("window.addEventListener('pageshow',v368RepairActiveView)" in runtime, 'pageshow still repairs active Hub view')
ok("window.addEventListener('focus',v368RepairActiveView)" in runtime, 'focus still repairs active Hub view')
ok("window.addEventListener('message',v368RepairFromFocusMessage)" in runtime, 'shell focus still repairs active Hub view')

print('V369 CREATOR HUB NATIVE INPUT REGRESSION: PASS', flush=True)
