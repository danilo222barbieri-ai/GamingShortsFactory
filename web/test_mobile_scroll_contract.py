#!/usr/bin/env python3
from pathlib import Path
import sys


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[ OK ] {message}")


def require(name: str, condition: bool) -> None:
    if not condition:
        fail(name)
    ok(name)


def compact(text: str) -> str:
    return ''.join(text.split()).lower()


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    web = root / 'web'

    home = (web / 'home_v154_component' / 'index.html').read_text(encoding='utf-8')
    ai_patch = (web / 'fix_v308_mobile_ai_flow.py').read_text(encoding='utf-8')
    hub_patch = (web / 'fix_v300_creator_hub_clean.py').read_text(encoding='utf-8')
    hub_compact = (web / 'fix_v303_mobile_hub_compact.py').read_text(encoding='utf-8')
    editor = (web / 'editor_2027_component' / 'index.html').read_text(encoding='utf-8')
    share = (web / 'share_v156_component' / 'index.html').read_text(encoding='utf-8')

    h = compact(home)
    require('Home browser surface is fixed', 'html,body{' in h and 'overflow:hidden' in h)
    require('Home root is fixed', '#home154{' in h and '#home154{' + h.split('#home154{',1)[1].split('}',1)[0] and 'overflow:hidden' in h.split('#home154{',1)[1].split('}',1)[0])

    a = compact(ai_patch)
    require('AI is its own scroll owner', '#ai221{' in a and 'overflow-y:auto!important' in a)
    require('AI contains overscroll', 'overscroll-behavior-y:contain!important' in a)
    require('AI enables iOS momentum scrolling', '-webkit-overflow-scrolling:touch!important' in a)

    hub = compact(hub_patch)
    require('Hub root keeps browser scroll locked', '#hub[data-v300-layout="hub"]{' in hub and 'overflow:hidden!important' in hub)
    require('Hub active view owns vertical scroll', '.view.active' in hub and 'overflow-y:auto!important' in hub)
    require('Hub active view contains overscroll', '.view.active' in hub and 'overscroll-behavior-y:contain!important' in hub)
    require('Hub active view enables iOS momentum scrolling', '.view.active' in hub and '-webkit-overflow-scrolling:touch!important' in hub)

    hc = compact(hub_compact)
    profile_scroller = hc.split('.profileonlyscroller{',1)[1].split('}',1)[0] if '.profileonlyscroller{' in hc else ''
    require('Hub profile does not create a nested primary scroller', 'overflow:auto' not in profile_scroller and 'overflow-y:auto' not in profile_scroller)

    e = compact(editor)
    require('Editor browser body is locked', 'html,body{' in e and 'overflow:hidden' in e.split('html,body{',1)[1].split('}',1)[0])
    require('Editor root owns vertical page scroll', '#ng27{' in e and 'overflow-y:auto' in e.split('#ng27{',1)[1].split('}',1)[0])
    require('Editor contains overscroll', 'overscroll-behavior-y:contain' in e.split('#ng27{',1)[1].split('}',1)[0])
    require('Editor enables iOS momentum scrolling', '-webkit-overflow-scrolling:touch' in e.split('#ng27{',1)[1].split('}',1)[0])

    s = compact(share)
    require('Share browser body is locked', 'html,body{' in s and 'overflow:hidden' in s.split('html,body{',1)[1].split('}',1)[0])
    share_root = s.split('#share{',1)[1].split('}',1)[0]
    require('Share root owns vertical page scroll', 'overflow-y:auto' in share_root)
    require('Share contains overscroll', 'overscroll-behavior-y:contain' in share_root)
    require('Share enables iOS momentum scrolling', '-webkit-overflow-scrolling:touch' in share_root)

    print('\nGSF MOBILE SCROLL CONTRACT: PASS')


if __name__ == '__main__':
    main()
