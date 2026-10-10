#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import re
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PATCH = ROOT / 'web' / 'fix_v312_global_navigation.py'
HOME = ROOT / 'web' / 'home_v154_component' / 'index.html'
START = ROOT / 'web' / 'start_web.sh'


def fail(msg: str) -> None:
    print('[FAIL]', msg)
    raise SystemExit(1)


def ok(msg: str) -> None:
    print('[ OK ]', msg)


if not PATCH.is_file():
    fail('V312 canonical navigation patch missing')

spec = importlib.util.spec_from_file_location('v312_nav_contract', PATCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

shell_sample = '''
<style>.mobile-gamebar-inner{grid-template-columns:repeat(4,minmax(0,1fr))}</style>
<div class="mobile-gamebar">
  <button class="mobile-gamebar-item home-slot" data-target="hub" data-section="editor" data-active="home" type="button"><span>Home</span></button>
  <button class="mobile-gamebar-item" data-target="editor" data-section="editor" data-active="hub" type="button"><span>Hub</span></button>
  <button class="mobile-gamebar-item" data-target="editor" data-section="drafts" data-active="projects" type="button"><span>Progetti</span></button>
  <button class="mobile-gamebar-item" data-target="editor" data-section="social" data-active="live" type="button"><span>Live</span></button>
</div>
<script>
if(activeKey==='home') active=lastTarget==='home';
else if(activeKey==='projects') active=(lastTarget==='hub'&&lastSection==='projects');
else if(activeKey==='live') active=(lastTarget==='hub'&&lastSection==='live');
else if(target==='hub') active=(lastTarget==='hub'&&(lastSection==='dashboard'||!lastSection));
const hubUrl="/creator-hub-v156/?v=3115&ui=profile-ref-2";
</script>
'''

patched = mod.patch_shell_text(shell_sample)
expected = {
    'home': ('home', None),
    'hub': ('hub', 'dashboard'),
    'projects': ('hub', 'projects'),
    'live': ('hub', 'live'),
}
for active, (target, section) in expected.items():
    match = re.search(r'<button\b(?=[^>]*\bdata-active="' + re.escape(active) + r'")[^>]*>.*?</button>', patched, flags=re.DOTALL)
    if not match:
        fail(f'missing canonical {active} button')
    button = match.group(0)
    if f'data-target="{target}"' not in button:
        fail(f'{active} target not normalized to {target}')
    if section is None:
        if 'data-section=' in button:
            fail(f'{active} inherited a section')
    elif f'data-section="{section}"' not in button:
        fail(f'{active} section not normalized to {section}')
    ok(f'{active} destination is canonical')

if 'data-target="editor"' in patched or 'data-section="editor"' in patched or 'data-section="social"' in patched:
    fail('stale inherited route remains')
ok('stale inherited routes are removed')

if mod.HUB_CACHE_URL not in patched:
    fail('Creator Hub cache key was not safely bumped before shell serialization')
if '/creator-hub-v156/?v=3115&ui=profile-ref-2' in patched:
    fail('stale V3115 Creator Hub cache key remains after V312')
ok('Creator Hub cache key is refreshed before V343 serialization')

if mod.patch_shell_text(patched) != patched:
    fail('shell normalization is not idempotent')
ok('shell normalization is idempotent')

# Regression guard for V312.0: V312 must never rewrite the Home JS again.
source = PATCH.read_text(encoding='utf-8')
if 'patch_home_text' in source or 'home_after = patch_home_text' in source:
    fail('V312 still rewrites Home navigation')
ok('V312 leaves Home navigation owned by V302')

if HOME.is_file():
    home = HOME.read_text(encoding='utf-8')
    required = (
        'if(nav==="hub")shellNav("hub",{section:"dashboard"});',
        'if(nav==="projects"){shellNav("hub",{section:"projects"});',
        'if(nav==="live")shellNav("hub",{section:"live"});',
    )
    for marker in required:
        if marker not in home:
            fail('V302 Home route missing: ' + marker)
    ok('V302 Home routes remain intact')

if START.is_file():
    start = START.read_text(encoding='utf-8')
    patch_marker = 'python /app/web/fix_v312_global_navigation.py /app'
    test_marker = 'python /app/web/test_v312_navigation_contract.py /app'
    if patch_marker not in start or test_marker not in start:
        fail('V312 patch/test missing from startup')
    if start.index(patch_marker) < start.index('python /app/web/fix_v311_mobile_hub_clean_pass.py'):
        fail('V312 must run after V311')
    if start.index(test_marker) < start.index(patch_marker):
        fail('V312 contract must run after V312 patch')
    if start.index(patch_marker) > start.index('python /app/web/fix_v343_single_global_shell.py'):
        fail('V312 Hub cache bump must happen before V343 shell serialization')
    ok('startup order is correct and cache bump precedes V343')

print('\nV312.2 NAVIGATION + SAFE HUB CACHE CONTRACT: PASS')
