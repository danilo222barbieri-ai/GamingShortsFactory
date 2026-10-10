#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARK = 'V370_SINGLE_NAVIGATION_OWNER'

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

V160_IFRAME_RE = re.compile(
    r'<iframe\s+src="/creator-hub-v156/\?v=[^"]+"\s+data-src="/creator-hub-v156/[^"]*"\s+data-loaded="1"\s+title="Creator Hub"></iframe>'
)
V160_IFRAME_LAZY = '<iframe src="about:blank" data-src="/creator-hub-v156/?v=3663&ui=profile-ref-2" data-loaded="0" title="Creator Hub"></iframe>'


def patch_home_text(text: str) -> str:
    if MARK in text and 'function shellNav(target,data={})' in text:
        return text
    new, n = HOME_NAV_RE.subn(HOME_NAV, text, count=1)
    if n != 1:
        raise RuntimeError(f'V370 Home shellNav anchor count={n}')
    return new


def _patch_v158(text: str) -> str:
    # Disable V158's automatic hidden Hub preload even if it initializes before V343.
    if V158_AUTO_PRELOAD in text:
        text = text.replace(V158_AUTO_PRELOAD, V158_NO_PRELOAD, 1)
    elif V158_NO_PRELOAD not in text:
        raise RuntimeError('V370 V158 preload anchor missing')

    # Listener may be installed before V343; therefore check ownership per message.
    if V158_LISTENER_OLD in text:
        text = text.replace(V158_LISTENER_OLD, V158_LISTENER_NEW, 1)
    elif V158_LISTENER_NEW not in text:
        raise RuntimeError('V370 V158 listener anchor missing')
    return text


def _patch_v160(text: str) -> str:
    if V160_IFRAME_LAZY not in text:
        text, n = V160_IFRAME_RE.subn(V160_IFRAME_LAZY, text, count=1)
        if n != 1:
            raise RuntimeError(f'V370 V160 iframe anchor count={n}')

    # Scope replacement to the V160 listener signature so V159/V220 keep their own internals.
    if V160_LISTENER_OLD in text:
        text = text.replace(V160_LISTENER_OLD, V160_LISTENER_NEW, 1)
    elif V160_LISTENER_NEW not in text:
        raise RuntimeError('V370 V160 listener anchor missing')
    return text


def patch_shell_text(text: str) -> str:
    text = _patch_v158(text)
    text = _patch_v160(text)
    return text


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
    if not home.is_file() or not generator.is_file():
        raise SystemExit('V370 required Home/generator files missing')

    home_changed = _write_if_changed(home, patch_home_text)
    generator_changed = _write_if_changed(generator, patch_shell_text)

    runtime_changed = []
    for name in ('GamingShortsFactory_V154_STRUCTURAL_HOME.py','GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'):
        path = root/name
        if not path.is_file():
            continue
        changed = _write_if_changed(path, patch_shell_text)
        # Runtime Home source is external, so only shell blocks are patched here.
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')
        runtime_changed.append((name, changed))

    print(
        'V370 single navigation owner applied',
        'home_changed=', home_changed,
        'generator_changed=', generator_changed,
        'runtime_changed=', runtime_changed,
        flush=True,
    )


if __name__ == '__main__':
    main()
