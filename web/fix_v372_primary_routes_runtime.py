#!/usr/bin/env python3
from pathlib import Path
import re
import sys

MARK = 'V372_PRIMARY_ROUTES_HOME_HANDOFF'
NAV_RE = re.compile(
    r'function shellNav\(target,data=\{\}\)\{.*?\n\s*return handled;\n\s*\}',
    re.DOTALL,
)
NAV = r'''function shellNav(target,data={}){
    // V372_PRIMARY_ROUTES_HOME_HANDOFF: Home emits intent only; V343 owns surfaces.
    try{
      window.parent.postMessage({type:"GSF_SHELL_NAV",target,...data},location.origin);
      return true;
    }catch(_e){return false}
  }'''


def patch_home(text: str) -> str:
    if MARK in text and 'window.parent.postMessage({type:"GSF_SHELL_NAV",target,...data},location.origin);' in text:
        return text
    patched, count = NAV_RE.subn(NAV, text, count=1)
    if count != 1:
        raise RuntimeError(f'V372 Home shellNav anchor count={count}')
    return patched


def main() -> None:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('/app')
    home = root / 'web' / 'home_v154_component' / 'index.html'
    if not home.is_file():
        raise SystemExit(f'V372 Home missing: {home}')
    before = home.read_text(encoding='utf-8')
    after = patch_home(before)
    changed = after != before
    if changed:
        home.write_text(after, encoding='utf-8')
    print(f'V372 primary Home handoff applied changed={changed}', flush=True)


if __name__ == '__main__':
    main()
