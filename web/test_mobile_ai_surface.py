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


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    v288 = (root / 'web' / 'fix_v288_ai_journey.py').read_text(encoding='utf-8')
    ai = (root / 'web' / 'ai_v221_component' / 'index.html').read_text(encoding='utf-8')
    v308 = (root / 'web' / 'fix_v308_mobile_ai_flow.py').read_text(encoding='utf-8')

    forbidden = (
        'AI_STEPS',
        'journeySteps',
        '1 Motore',
        '2 Momento',
        '3 Editor',
        '4 Crea Short',
        '5 Pronto',
    )
    for marker in forbidden:
        require(f"line-up removed from V288: {marker}", marker not in v288)

    for marker in (
        'TROVA I 3 MOMENTI MIGLIORI',
        'momentNextActions',
        'select_moment',
        'open_editor',
        'create_short',
        'selectedMoment',
    ):
        require(f"V288 flow preserved: {marker}", marker in v288)

    for engine in ('auto', 'best', 'action', 'reaction'):
        require(f"real AI engine preserved: {engine}", f'data-engine="{engine}"' in ai)

    require("AI mobile root scrolls internally", 'overflow-y:auto!important' in v308)
    require("AI mobile overscroll is contained", 'overscroll-behavior-y:contain!important' in v308)
    require("three moments remain readable below engines", 'grid-template-columns:1fr!important' in v308)

    for marker in (
        'function openMomentPreview',
        'function closeMomentPreview',
        'requestFullscreen',
        'webkitEnterFullscreen',
        'webkitendfullscreen',
        'fullscreenchange',
        'momentPreviewScroll',
        'scrollIntoView',
    ):
        require(f"fullscreen state contract: {marker}", marker in v308)

    close_start = v308.find('function closeMomentPreview')
    open_start = v308.find('function openMomentPreview')
    close_body = v308[close_start:open_start]
    require("fullscreen exit does not clear selected moment", 'selectedMoment=-1' not in close_body and 'selectedMoment = -1' not in close_body)

    print("\nGSF MOBILE AI SURFACE CONTRACT: PASS")


if __name__ == '__main__':
    main()
