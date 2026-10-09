#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import re
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PATCH = ROOT / 'web' / 'fix_v313_mobile_profile_fit.py'
START = ROOT / 'web' / 'start_web.sh'
HUB = ROOT / 'web' / 'creator_hub_v156_component' / 'index.html'


def fail(msg: str) -> None:
    print('[FAIL]', msg)
    raise SystemExit(1)


def ok(msg: str) -> None:
    print('[ OK ]', msg)


def css_rule_has(style: str, selector: str, *declarations: str) -> bool:
    """Check declarations inside a selector block without depending on property order."""
    match = re.search(re.escape(selector) + r'\{([^}]*)\}', style, flags=re.DOTALL)
    if not match:
        return False
    body = re.sub(r'\s+', '', match.group(1))
    return all(re.sub(r'\s+', '', declaration) in body for declaration in declarations)


if not PATCH.is_file():
    fail('V313 mobile profile fit patch missing')

spec = importlib.util.spec_from_file_location('v313_mobile_profile_fit', PATCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

platforms = ('youtube', 'tiktok', 'instagram', 'facebook', 'twitch')
social_rows = ''.join(
    f'<button class="profileSocialRefRow" data-platform="{platform}"><span>{platform}</span></button>'
    for platform in platforms
)
sample = f'''<!doctype html><html><head><style id="v311HubForce">/* V311 APPROVED CREATOR REFERENCE */
#hub .profileReferenceEdit{{min-height:248px!important}}
#hub .profilePlanRef{{padding:20px!important}}
</style></head><body><div id="hub"><div class="profileReferenceScroll">
<div class="profileReferenceCard profileReferenceEdit"></div>
<div class="profileReferenceCard profilePlanRef"></div>
<div class="profileReferenceCard profileSocialRef"><div class="profileSocialRows">{social_rows}</div></div>
</div></div></body></html>'''

patched = mod.patch_text(sample)
if patched.count('id="v313MobileProfileFit"') != 1:
    fail('V313 style was not installed exactly once')
ok('V313 style is installed exactly once')

style_match = re.search(r'<style id="v313MobileProfileFit">(.*?)</style>', patched, flags=re.DOTALL)
if not style_match:
    fail('V313 style block missing')
style = style_match.group(1)

if '@media(max-width:767px)' not in style:
    fail('mobile breakpoint missing')

rule_checks = (
    ('#hub .profileReferenceEdit', ('min-height:0!important', 'height:136px!important')),
    ('#hub .profilePlanRef', ('min-height:0!important', 'height:124px!important')),
    ('#hub .profileReferenceBrand', ('min-height:34px!important', 'height:34px!important')),
    ('#hub .profileRefAvatar', ('width:68px!important', 'height:68px!important')),
    ('#hub .profileRefInputWrap', ('height:34px!important',)),
    ('#hub .profileRefSave', ('height:30px!important',)),
    ('#hub .profilePlanCta', ('height:28px!important',)),
)
for selector, declarations in rule_checks:
    if not css_rule_has(style, selector, *declarations):
        fail('missing compact mobile rule: ' + selector + ' -> ' + ', '.join(declarations))
ok('Profile and subscription boxes are compact on mobile')

for platform in platforms:
    before = sample.count(f'data-platform="{platform}"')
    after = patched.count(f'data-platform="{platform}"')
    if before != 1 or after != 1:
        fail(f'social connection {platform} was removed or duplicated')
ok('all five social connection rows are preserved')

if re.search(r'profileSocial(?:Ref|Rows|RefRow)[^{]*\{[^}]*display\s*:\s*none', style, flags=re.I|re.S):
    fail('V313 hides social connection content')
ok('V313 does not hide social rows')

if mod.patch_text(patched) != patched:
    fail('V313 patch is not idempotent')
ok('V313 patch is idempotent')

if START.is_file():
    start = START.read_text(encoding='utf-8')
    patch_marker = 'python /app/web/fix_v313_mobile_profile_fit.py /app/web/creator_hub_v156_component/index.html'
    test_marker = 'python /app/web/test_v313_mobile_profile_fit.py /app'
    after_v312 = 'python /app/web/test_v312_navigation_contract.py /app'
    production_generation = 'python /app/web/apply_v343_v293_compat.py'
    for anchor, label in (
        (patch_marker, 'V313 patch'),
        (test_marker, 'V313 test'),
        (after_v312, 'V312 navigation test'),
        (production_generation, 'V343/V293 production generation'),
    ):
        if anchor not in start:
            fail(label + ' anchor is not registered')
    if start.index(patch_marker) < start.index(after_v312):
        fail('V313 must run after V312 navigation restoration')
    if start.index(test_marker) < start.index(patch_marker):
        fail('V313 test must run after its patch')
    if start.index(test_marker) > start.index(production_generation):
        fail('V313 must run before production app generation')
    ok('V313 startup order is correct')

if HUB.is_file() and 'V311 APPROVED CREATOR REFERENCE' in HUB.read_text(encoding='utf-8'):
    html = HUB.read_text(encoding='utf-8')
    for platform in platforms:
        if f'data-platform="{platform}"' not in html:
            fail(f'runtime Hub is missing social platform {platform}')
    ok('runtime Hub still contains every social platform')

print('\nV313 MOBILE PROFILE FIT CONTRACT: PASS')
