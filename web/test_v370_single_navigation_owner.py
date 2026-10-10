#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, importlib.util, re, sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
HOME=ROOT/'web'/'home_v154_component'/'index.html'
APPLY=ROOT/'web'/'apply_v154_structural_home.py'
V343=ROOT/'web'/'fix_v343_single_global_shell.py'
FIX=ROOT/'web'/'fix_v370_single_navigation_owner.py'

def ok(cond,label):
    if not cond:
        raise AssertionError('FAIL: '+label)
    print('[ OK ] '+label,flush=True)

home=HOME.read_text(encoding='utf-8')
apply=APPLY.read_text(encoding='utf-8')

start=home.find('function shellNav(target,data={}){')
end=home.find('function parentClick',start)
ok(start>=0 and end>start,'Home shellNav exists')
nav=home[start:end]
ok('window.parent.postMessage({type:"GSF_SHELL_NAV"' in nav,'Home delegates navigation to canonical shell')
ok('window.parent.document' not in nav,'Home does not mutate parent overlays directly')
ok('classList.add("is-open")' not in nav and 'style.pointerEvents' not in nav,'Home has no parallel overlay router')

account_start=home.find('async function syncAccountEntry()')
account_end=home.find('const hub=document.getElementById("hubBtn")',account_start)
ok(account_start>=0 and account_end>account_start,'Home account sync block exists')
account=home[account_start:account_end]
ok('window.parent.__GSF_GLOBAL_SHELL_V343' in account,'Home account sync stands down when V343 owns header')
ok('/creator-hub/state?scope=header' in account,'Home fallback uses lightweight header state')
ok('fetch("/creator-hub/state",' not in account,'Home no longer requests heavy Creator Hub state')
ok('setTimeout(syncAccountEntry,120);' in account,'Home delays first account sync so V343 can mount first')

v158=re.search(r"_shell_v158 = r'''(.*?)'''\ns = s\.rstrip\(\) \+",apply,re.S)
ok(bool(v158),'V158 source block exists')
v158=v158.group(1)
ok("if(window.__GSF_GLOBAL_SHELL_V343)return;" in v158,'V158 legacy router stands down when V343 is active')
ok('new MutationObserver(sync)' not in v158,'V158 no longer preloads/rewrites hidden Hub portal')

v160=re.search(r"_hub_surface_v160 = r'''(.*?)'''\ns = s\.rstrip\(\) \+",apply,re.S)
ok(bool(v160),'V160 source block exists')
v160=v160.group(1)
ok("if(window.__GSF_GLOBAL_SHELL_V343)return;" in v160,'V160 legacy router stands down when V343 is active')
ok('src="about:blank"' in v160 and 'data-loaded="0"' in v160,'V160 Hub iframe is lazy until canonical navigation opens it')

# Regression: the production runtime may reorder/add iframe attributes before V370 runs.
fix_spec=importlib.util.spec_from_file_location('v370fix',FIX)
fix_mod=importlib.util.module_from_spec(fix_spec); assert fix_spec and fix_spec.loader; fix_spec.loader.exec_module(fix_mod)
transformed_v160='''# GSF_GLOBAL_SHELL_V343\n<iframe class="gsf-hub-frame-v160" data-loaded="1" title="Creator Hub" data-src="/creator-hub-v156/" src="/creator-hub-v156/?v=3663&ui=profile-ref-2"></iframe>\n        if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;\n        const t=String(e.data.target||'');\n        if(t==='hub'||t==='profile'){\n'''
patched_transformed=fix_mod._patch_v160(transformed_v160)
ok('src="about:blank"' in patched_transformed and 'data-loaded="0"' in patched_transformed,'V370 handles transformed V160 iframe attribute order')
ok("if(window.__GSF_GLOBAL_SHELL_V343)return;" in patched_transformed,'V370 mutes transformed V160 listener')

# Regression: V343 may already have retired V160 completely in a generated runtime.
canonical_only='# GSF_GLOBAL_SHELL_V343\nconst canonicalShell=true;\n'
ok(fix_mod._patch_v160(canonical_only)==canonical_only,'V370 accepts runtime where V343 already retired V160')
missing_owner_failed=False
try:
    fix_mod._patch_v160('const noCanonicalOwner=true;\n')
except RuntimeError:
    missing_owner_failed=True
ok(missing_owner_failed,'V370 still rejects missing V160 when V343 is absent')

spec=importlib.util.spec_from_file_location('v343',V343)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)
bridge=gzip.decompress(base64.b64decode(mod.JS_GZIP_B64)).decode('utf-8')
ok("const f=o.querySelector('iframe');" in bridge,'V343 owns Hub iframe')
ok("if(f&&f.dataset.loaded!=='1')" in bridge and "f.dataset.loaded='1'" in bridge,'V343 lazy-loads Hub exactly on navigation')
ok("P.addEventListener('message',e=>{if(e.origin!==P.location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;route(e.data)},true)" in bridge,'V343 is canonical GSF_SHELL_NAV listener')
ok("P.fetch('/creator-hub/state?scope=header'" in bridge,'V343 header uses lightweight state')
ok("P.fetch('/creator-hub/state',{cache:'no-store'" not in bridge,'V343 header does not trigger full Hub state')

for runtime_name in ('GamingShortsFactory_V154_STRUCTURAL_HOME.py','GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'):
    runtime=ROOT/runtime_name
    if runtime.is_file():
        text=runtime.read_text(encoding='utf-8')
        ok("P.fetch('/creator-hub/state?scope=header'" in text,f'{runtime_name} carries lightweight V343 header fetch')

print('V370.1 SINGLE NAVIGATION OWNER + LIGHT HEADER STATE CONTRACT: PASS',flush=True)
