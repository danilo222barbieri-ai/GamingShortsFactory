#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
HUB = ROOT / 'web' / 'creator_hub_v156_component' / 'index.html'
FIX = ROOT / 'web' / 'fix_v368_creator_hub_touch_recovery.py'


def ok(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError('FAIL: ' + label)
    print('[ OK ] ' + label, flush=True)


ok(HUB.is_file(), 'Creator Hub source exists')
ok(FIX.is_file(), 'V368 touch recovery patch exists')

spec = importlib.util.spec_from_file_location('fix_v368_creator_hub_touch_recovery', FIX)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

source = HUB.read_text(encoding='utf-8')
patched = mod.patch_text(source)

ok('V368_CREATOR_HUB_TOUCH_RECOVERY' in patched, 'V368 marker injected')
ok('function v368RepairActiveView()' in patched, 'active Hub view repair exists')
ok("view.style.pointerEvents=on?'auto':'none'" in patched, 'active view pointer events are explicit')
ok("view.style.visibility=on?'visible':'hidden'" in patched, 'active view visibility is explicit')
ok('function v368HubAction(target)' in patched, 'delegated Hub action router exists')
ok("target.closest('.folder')" in patched, 'folder taps are delegated')
ok("target.closest('[data-open-folder]')" in patched, 'dashboard shortcut taps are delegated')
ok("target.closest('.backBtn')" in patched, 'back taps are delegated')
ok("target.closest('.closeTop')" in patched, 'close taps are delegated')
ok("target.closest('.socialDot')" in patched, 'social shortcut taps are delegated')
ok("document.addEventListener('pointerup',v368PointerUp,true)" in patched, 'Safari pointerup capture exists')
ok("document.addEventListener('click',v368Click,true)" in patched, 'click capture fallback exists')
ok("window.addEventListener('pageshow',v368RepairActiveView)" in patched, 'bfcache/pageshow repairs active view')
ok("window.addEventListener('focus',v368RepairActiveView)" in patched, 'focus repairs active view')
ok("window.addEventListener('message',v368RepairFromFocusMessage)" in patched, 'shell focus message repairs active view')
ok('V368_HUB_TAP' in patched, 'tap telemetry is emitted')
ok('preventDefault()' not in patched[patched.index('V368_CREATOR_HUB_TOUCH_RECOVERY'):], 'V368 never globally cancels native taps')

# Idempotence: a second pass must not duplicate the runtime.
patched2 = mod.patch_text(patched)
ok(patched2 == patched, 'V368 patch is idempotent')
ok(patched.count('V368_CREATOR_HUB_TOUCH_RECOVERY') == 1, 'single V368 runtime marker')

print('V368 CREATOR HUB TOUCH RECOVERY CONTRACT: PASS', flush=True)
