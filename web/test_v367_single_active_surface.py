#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
FIX = ROOT / 'web' / 'fix_v343_single_global_shell.py'


def need(text: str, token: str, label: str) -> None:
    if token not in text:
        raise AssertionError(f'V367 missing {label}: {token}')


def main() -> None:
    if not FIX.is_file():
        raise SystemExit(f'V367 shell source missing: {FIX}')
    spec = importlib.util.spec_from_file_location('gsf_v343_for_v367', FIX)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    block = mod.build_shell_block()

    need(block, 'GSF_SINGLE_ACTIVE_SURFACE_V367', 'arbiter marker')
    need(block, '__GSF_SINGLE_ACTIVE_SURFACE_V367', 'single-install guard')
    for surface_id in (
        'gsf-editor-overlay-v220',
        'gsf-short-overlay-v343',
        'gsf-creator-hub-live-v160',
        'gsf-ai-overlay-v221',
        'gsf-social-overlay-v159',
        'gsf-account-overlay-v223',
    ):
        need(block, surface_id, f'surface {surface_id}')

    need(block, "el.style.pointerEvents=on?'auto':'none'", 'exclusive pointer-event gate')
    need(block, "el.toggleAttribute('inert',!on)", 'inactive inert gate')
    need(block, "el.setAttribute('aria-hidden',on?'false':'true')", 'accessibility visibility gate')
    need(block, "target==='home'||target==='close'", 'home/close release')
    need(block, "target==='hub'", 'Hub route mapping')
    need(block, "target==='editor'", 'Editor route mapping')
    need(block, "target==='short'", 'Short route mapping')
    need(block, "e.data.type!=='GSF_SHELL_NAV'", 'canonical navigation listener')
    need(block, 'requestAnimationFrame', 'post-navigation reconciliation')
    need(block, 'pageshow', 'Safari back-forward recovery')
    need(block, 'visibilitychange', 'Safari foreground recovery')

    # V367 deliberately reuses route events and bounded retries instead of
    # adding another MutationObserver on top of the V343 watchdog.
    marker_pos = block.index('GSF_SINGLE_ACTIVE_SURFACE_V367')
    v367 = block[marker_pos:]
    if 'MutationObserver' in v367:
        raise AssertionError('V367 must not add another MutationObserver')

    print('V367 SINGLE ACTIVE SURFACE CONTRACT: PASS', flush=True)


if __name__ == '__main__':
    main()
