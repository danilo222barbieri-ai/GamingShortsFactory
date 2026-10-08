#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import re
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PATCH = ROOT / 'web' / 'fix_v311_mobile_hub_clean_pass.py'
START = ROOT / 'web' / 'start_web.sh'


def fail(msg: str) -> None:
    print('[FAIL]', msg)
    raise SystemExit(1)


def ok(msg: str) -> None:
    print('[ OK ]', msg)


if not PATCH.is_file():
    fail('V311 canonical patch missing')

spec = importlib.util.spec_from_file_location('v311_nav_contract', PATCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Reproduce the real regression: historical patches can leave canonical labels
# attached to stale targets/sections. The final V311 pass must ignore inherited
# route state and normalize every visible destination explicitly.
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
    match = re.search(
        r'<button\b(?=[^>]*\bdata-active="' + re.escape(active) + r'")[^>]*>.*?</button>',
        patched,
        flags=re.DOTALL,
    )
    if not match:
        fail(f'missing canonical {active} button')
    button = match.group(0)
    if f'data-target="{target}"' not in button:
        fail(f'{active} target not normalized to {target}: {button}')
    if section is None:
        if 'data-section=' in button:
            fail(f'{active} must not inherit a section: {button}')
    elif f'data-section="{section}"' not in button:
        fail(f'{active} section not normalized to {section}: {button}')
    ok(f'{active} destination is canonical')

if 'data-target="editor"' in patched:
    fail('stale editor destination remains in Game Bar')
if 'data-section="editor"' in patched or 'data-section="social"' in patched:
    fail('stale inherited Game Bar section remains')
ok('stale inherited routes are removed')

if mod.patch_shell_text(patched) != patched:
    fail('canonical navigation normalization is not idempotent')
ok('navigation normalization is idempotent')

if START.is_file():
    start = START.read_text(encoding='utf-8')
    marker = 'python /app/web/test_v312_navigation_contract.py /app'
    if marker not in start:
        fail('V312 navigation contract is not registered at startup')
    if start.index(marker) < start.index('python /app/web/fix_v311_mobile_hub_clean_pass.py'):
        fail('V312 navigation contract must run after final V311 normalization')
    ok('startup validates navigation after V311')

print('\nV312 GLOBAL NAVIGATION CONTRACT: PASS')
