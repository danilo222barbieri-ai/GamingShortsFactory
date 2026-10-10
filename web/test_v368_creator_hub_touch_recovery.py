#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
HUB = ROOT / 'web' / 'creator_hub_v156_component' / 'index.html'
FIX = ROOT / 'web' / 'fix_v368_creator_hub_touch_recovery.py'
STARTUP = ROOT / 'web' / 'fix_v362_project_pages_cleanup.py'


def ok(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError('FAIL: ' + label)
    print('[ OK ] ' + label, flush=True)


ok(HUB.is_file(), 'Creator Hub source exists')
ok(FIX.is_file(), 'V368 touch recovery patch exists')
ok(STARTUP.is_file(), 'Creator Hub startup patch exists')

spec = importlib.util.spec_from_file_location('fix_v368_creator_hub_touch_recovery', FIX)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

source = HUB.read_text(encoding='utf-8')
patched = mod.patch_text(source)
runtime = patched[patched.index('V368_CREATOR_HUB_TOUCH_RECOVERY'):]

ok('V368_CREATOR_HUB_TOUCH_RECOVERY' in patched, 'V368 marker injected')
ok('function v368RepairActiveView()' in runtime, 'active Hub view repair exists')
ok("view.style.pointerEvents=on?'auto':'none'" in runtime, 'active view pointer events are explicit')
ok("view.style.visibility=on?'visible':'hidden'" in runtime, 'active view visibility is explicit')
ok('const frame=window.frameElement;' in runtime, 'Hub repairs its own parent iframe')
ok("frame.style.pointerEvents='auto'" in runtime, 'Hub iframe pointer events are restored')
ok("frame.closest('#gsf-creator-hub-live-v160')" in runtime, 'Hub targets only its own parent overlay')
ok("overlay.style.pointerEvents='auto'" in runtime, 'open Hub overlay pointer events are restored')

# V368 is a visibility/pointer repair only. Navigation/actions stay exclusively
# in the base Hub handlers so Safari never sees two competing input routers.
ok('function v368HubAction(' not in runtime, 'no duplicate Hub action router')
ok("document.addEventListener('pointerup'" not in runtime, 'no capture pointerup router')
ok("document.addEventListener('click'" not in runtime, 'no capture click router')
ok('stopPropagation()' not in runtime, 'V368 never blocks native event propagation')
ok('preventDefault()' not in runtime, 'V368 never cancels native input')
ok("window.addEventListener('pageshow',v368RepairActiveView)" in runtime, 'bfcache/pageshow repairs active view')
ok("window.addEventListener('focus',v368RepairActiveView)" in runtime, 'focus repairs active view')
ok("window.addEventListener('message',v368RepairFromFocusMessage)" in runtime, 'shell focus message repairs active view')

startup = STARTUP.read_text(encoding='utf-8')
ok("fix_v368_creator_hub_touch_recovery.py" in startup, 'V368 patch is called from Hub startup')
ok("test_v368_creator_hub_touch_recovery.py" in startup, 'V368 contract is enforced at startup')
ok("subprocess.run([sys.executable, str(touch_fix), str(path)], check=True)" in startup, 'V368 patch runs against runtime Hub file')

# Idempotence: a second pass must not duplicate the runtime.
patched2 = mod.patch_text(patched)
ok(patched2 == patched, 'V368 patch is idempotent')
ok(patched.count('V368_CREATOR_HUB_TOUCH_RECOVERY') == 1, 'single V368 runtime marker')

print('V368 CREATOR HUB TOUCH RECOVERY CONTRACT: PASS', flush=True)
