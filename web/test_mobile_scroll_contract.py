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
    final_visual = (web / 'fix_v307_mobile_visual_source.py').read_text(encoding='utf-8')

    h = compact(home)
    require('Home browser surface is fixed', 'html,body{' in h and 'overflow:hidden' in h)
    require('Home root is fixed', '#home154{' in h and 'overflow:hidden' in h.split('#home154{',1)[1].split('}',1)[0])

    a = compact(ai_patch)
    require('AI is its own scroll owner', '#ai221{' in a and 'overflow-y:auto!important' in a)
    require('AI contains overscroll', 'overscroll-behavior-y:contain!important' in a)
    require('AI enables iOS momentum scrolling', '-webkit-overflow-scrolling:touch!important' in a)

    v = compact(final_visual)
    require('final visual pass owns mobile scroll contract', 'gsfmobile-onlyscrollcontract' in v)
    require('Hub active view owns vertical scroll', '#hub.view.active' in v and 'overflow-y:auto!important' in v)
    require('Hub active view contains overscroll', '#hub.view.active' in v and 'overscroll-behavior-y:contain!important' in v)
    require('Hub active view enables iOS momentum scrolling', '#hub.view.active' in v and '-webkit-overflow-scrolling:touch!important' in v)
    require('Hub profile nested primary scroll is disabled', '.profileonlyscroller' in v and 'overflow:visible!important' in v)

    require('Editor browser body remains locked', 'html,body{overflow:hidden!important' in v)
    require('Editor root owns vertical page scroll', '#ng27{height:100dvh!important' in v and 'overflow-y:auto!important' in v)
    require('Editor contains overscroll', '#ng27{height:100dvh!important' in v and 'overscroll-behavior-y:contain!important' in v)
    require('Editor enables iOS momentum scrolling', '#ng27{height:100dvh!important' in v and '-webkit-overflow-scrolling:touch!important' in v)

    require('Share root owns vertical page scroll', '#share{height:100dvh!important' in v and 'overflow-y:auto!important' in v)
    require('Share contains overscroll', '#share{height:100dvh!important' in v and 'overscroll-behavior-y:contain!important' in v)
    require('Share enables iOS momentum scrolling', '#share{height:100dvh!important' in v and '-webkit-overflow-scrolling:touch!important' in v)

    print('\nGSF MOBILE SCROLL CONTRACT: PASS')


if __name__ == '__main__':
    main()
