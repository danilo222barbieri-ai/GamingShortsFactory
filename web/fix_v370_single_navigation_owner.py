#!/usr/bin/env python3
from pathlib import Path
import base64
import gzip
import re
import sys

MARK = 'V370_SINGLE_NAVIGATION_OWNER'
HEADER_STATE_OLD = "P.fetch('/creator-hub/state',{cache:'no-store',credentials:'same-origin'})"
HEADER_STATE_NEW = "P.fetch('/creator-hub/state?scope=header',{cache:'no-store',credentials:'same-origin'})"

HOME_NAV_RE = re.compile(
    r'function shellNav\(target,data=\{\}\)\{.*?\n\s*return handled;\n\s*\}',
    re.DOTALL,
)

HOME_NAV = r'''function shellNav(target,data={}){
    // V370_SINGLE_NAVIGATION_OWNER: Home emits intent only. V343 owns parent surfaces.
    try{
      window.parent.postMessage({type:"GSF_SHELL_NAV",target,...data},location.origin);
      return true;
    }catch(_e){return false}
  }'''

HOME_ACCOUNT_RE = re.compile(
    r'(async function syncAccountEntry\(\)\{\n\s*if\(!accountEntry\)return;\n)'
)
HOME_ACCOUNT_GUARD = '   try{if(window.parent&&window.parent.__GSF_GLOBAL_SHELL_V343)return}catch(_e){}\n'
HOME_ACCOUNT_FETCH_OLD = 'fetch("/creator-hub/state",{cache:"no-store",credentials:"same-origin"})'
HOME_ACCOUNT_FETCH_NEW = 'fetch("/creator-hub/state?scope=header",{cache:"no-store",credentials:"same-origin"})'
HOME_ACCOUNT_BOOT_OLD = ''' window.addEventListener("focus",syncAccountEntry);
 document.addEventListener("visibilitychange",()=>{if(!document.hidden)syncAccountEntry()});
 syncAccountEntry();'''
HOME_ACCOUNT_BOOT_NEW = ''' window.addEventListener("focus",syncAccountEntry);
 document.addEventListener("visibilitychange",()=>{if(!document.hidden)syncAccountEntry()});
 setTimeout(syncAccountEntry,120);'''

V158_AUTO_PRELOAD = """      sync();
      new MutationObserver(sync).observe(document.body,{childList:true,subtree:true});
"""
V158_NO_PRELOAD = """      // V370_SINGLE_NAVIGATION_OWNER: never preload the legacy Hub portal.
      // V343 owns the live Hub iframe; V158 remains only as a fallback router.
"""

V158_LISTENER_OLD = """        if(ev.origin!==location.origin || !ev.data || ev.data.type!=='GSF_SHELL_NAV')return;
        const t=String(ev.data.target||'');
"""
V158_LISTENER_NEW = """        if(ev.origin!==location.origin || !ev.data || ev.data.type!=='GSF_SHELL_NAV')return;
        if(window.__GSF_GLOBAL_SHELL_V343)return;
        const t=String(ev.data.target||'');
"""

V160_LISTENER_OLD = """        if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        const t=String(e.data.target||'');
        if(t==='hub'||t==='profile'){
"""
V160_LISTENER_NEW = """        if(e.origin!==location.origin||!e.data||e.data.type!=='GSF_SHELL_NAV')return;
        if(window.__GSF_GLOBAL_SHELL_V343)return;
        const t=String(e.data.target||'');
        if(t==='hub'||t==='profile'){
"""

# Runtime migrations can add/reorder iframe attributes before V370 runs. Match
# the semantic V160 Hub frame rather than one exact serialized attribute order.
V160_IFRAME_RE = re.compile(
    r'<iframe\b(?=[^>]*\btitle="Creator Hub")(?=[^>]*\bdata-loaded="1")(?=[^>]*\b(?:src|data-src)="[^"]*/creator-hub-v156/[^"]*")[^>]*></iframe>'
)
V160_IFRAME_LAZY = '<iframe src="about:blank" data-src="/creator-hub-v156/?v=3663&ui=profile-ref-2" data-loaded="0" title="Creator Hub"></iframe>'


def patch_home_text(text: str) -> str:
    if MARK not in text:
        new, n = HOME_NAV_RE.subn(HOME_NAV, text, count=1)
        if n != 1:
            raise RuntimeError(f'V370 Home shellNav anchor count={n}')
        text = new

    if 'window.parent.__GSF_GLOBAL_SHELL_V343' not in text:
        match = HOME_ACCOUNT_RE.search(text)
        if not match:
            raise RuntimeError('V370 Home account sync anchor missing')
        text = text[:match.end()] + HOME_ACCOUNT_GUARD + text[match.end():]

    if HOME_ACCOUNT_FETCH_OLD in text:
        text = text.replace(HOME_ACCOUNT_FETCH_OLD, HOME_ACCOUNT_FETCH_NEW, 1)
    elif HOME_ACCOUNT_FETCH_NEW not in text:
        raise RuntimeError('V370 Home header-state endpoint anchor missing')

    if HOME_ACCOUNT_BOOT_OLD in text:
        text = text.replace(HOME_ACCOUNT_BOOT_OLD, HOME_ACCOUNT_BOOT_NEW, 1)
    elif HOME_ACCOUNT_BOOT_NEW not in text:
        raise RuntimeError('V370 Home account boot anchor missing')
    return text


def _patch_v158(text: str) -> str:
    if V158_AUTO_PRELOAD in text:
        text = text.replace(V158_AUTO_PRELOAD, V158_NO_PRELOAD, 1)
    elif V158_NO_PRELOAD not in text:
        raise RuntimeError('V370 V158 preload anchor missing')

    if V158_LISTENER_OLD in text:
        text = text.replace(V158_LISTENER_OLD, V158_LISTENER_NEW, 1)
    elif V158_LISTENER_NEW not in text:
        raise RuntimeError('V370 V158 listener anchor missing')
    return text


def _patch_v160(text: str) -> str:
    canonical_v343 = 'GSF_GLOBAL_SHELL_V343' in text or '__GSF_GLOBAL_SHELL_V343' in text

    if V160_IFRAME_LAZY not in text:
        text, n = V160_IFRAME_RE.subn(V160_IFRAME_LAZY, text, count=1)
        if n == 0 and not canonical_v343:
            raise RuntimeError('V370 V160 iframe anchor count=0 without canonical V343 owner')

    if V160_LISTENER_OLD in text:
        text = text.replace(V160_LISTENER_OLD, V160_LISTENER_NEW, 1)
    elif V160_LISTENER_NEW not in text and not canonical_v343:
        raise RuntimeError('V370 V160 listener anchor missing without canonical V343 owner')
    return text


def _patch_v343_runtime_endpoint(text: str) -> str:
    # Generator/source form: the JS may exist directly in text.
    if HEADER_STATE_NEW in text:
        return text
    if HEADER_STATE_OLD in text:
        return text.replace(HEADER_STATE_OLD, HEADER_STATE_NEW, 1)

    # Generated V154/V293 form: V343 is embedded via repr(bridge), so the
    # JavaScript single quotes are escaped inside the Python string literal.
    # Patch the serialized spelling without reserializing the whole app source.
    escaped_old = HEADER_STATE_OLD.replace("'", "\\'")
    escaped_new = HEADER_STATE_NEW.replace("'", "\\'")
    if escaped_new in text:
        return text
    if escaped_old in text:
        return text.replace(escaped_old, escaped_new, 1)
    return text


def patch_shell_text(text: str) -> str:
    text = _patch_v158(text)
    text = _patch_v160(text)
    text = _patch_v343_runtime_endpoint(text)
    return text


def patch_v343_source(text: str) -> str:
    match = re.search(r"JS_GZIP_B64='([^']+)'", text)
    if not match:
        raise RuntimeError('V370 V343 compressed bridge anchor missing')
    bridge = gzip.decompress(base64.b64decode(match.group(1))).decode('utf-8')
    if HEADER_STATE_NEW in bridge:
        return text
    if HEADER_STATE_OLD not in bridge:
        raise RuntimeError('V370 V343 header-state fetch anchor missing')
    bridge = bridge.replace(HEADER_STATE_OLD, HEADER_STATE_NEW, 1)
    encoded = base64.b64encode(gzip.compress(bridge.encode('utf-8'), mtime=0)).decode('ascii')
    replacement = "JS_GZIP_B64='" + encoded + "'"
    return text[:match.start()] + replacement + text[match.end():]


def _write_if_changed(path: Path, patcher) -> bool:
    before = path.read_text(encoding='utf-8')
    after = patcher(before)
    if after != before:
        path.write_text(after, encoding='utf-8')
        return True
    return False


def main() -> None:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
    home = root/'web'/'home_v154_component'/'index.html'
    generator = root/'web'/'apply_v154_structural_home.py'
    v343 = root/'web'/'fix_v343_single_global_shell.py'
    if not home.is_file() or not generator.is_file() or not v343.is_file():
        raise SystemExit('V370 required Home/generator/V343 files missing')

    home_changed = _write_if_changed(home, patch_home_text)
    generator_changed = _write_if_changed(generator, patch_shell_text)
    v343_changed = _write_if_changed(v343, patch_v343_source)

    runtime_changed = []
    for name in ('GamingShortsFactory_V154_STRUCTURAL_HOME.py','GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'):
        path = root/name
        if not path.is_file():
            continue
        changed = _write_if_changed(path, patch_shell_text)
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')
        runtime_changed.append((name, changed))

    print(
        'V370.1 single navigation owner + lightweight header state applied',
        'home_changed=', home_changed,
        'generator_changed=', generator_changed,
        'v343_changed=', v343_changed,
        'runtime_changed=', runtime_changed,
        flush=True,
    )


if __name__ == '__main__':
    main()
