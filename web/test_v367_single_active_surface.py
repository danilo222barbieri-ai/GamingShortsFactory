#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
FIX = ROOT / 'web' / 'fix_v367_single_active_surface.py'


def need(text: str, token: str, label: str) -> None:
    if token not in text:
        raise AssertionError(f'V367 missing {label}: {token}')


def main() -> None:
    if not FIX.is_file():
        raise SystemExit(f'V367 shell arbiter source missing: {FIX}')
    spec = importlib.util.spec_from_file_location('gsf_v367', FIX)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    arbiter = mod.ARBITER

    need(arbiter, 'GSF_SINGLE_ACTIVE_SURFACE_V367', 'arbiter marker')
    need(arbiter, '__GSF_SINGLE_ACTIVE_SURFACE_V367', 'single-install guard')
    for surface_id in (
        'gsf-editor-overlay-v220',
        'gsf-short-overlay-v343',
        'gsf-creator-hub-live-v160',
        'gsf-ai-overlay-v221',
        'gsf-social-overlay-v159',
        'gsf-account-overlay-v223',
    ):
        need(arbiter, surface_id, f'surface {surface_id}')

    need(arbiter, "el.style.pointerEvents=on?'auto':'none'", 'exclusive pointer-event gate')
    need(arbiter, "el.toggleAttribute('inert',!on)", 'inactive inert gate')
    need(arbiter, "el.setAttribute('aria-hidden',on?'false':'true')", 'accessibility visibility gate')
    need(arbiter, "target==='home'||target==='close'", 'home/close release')
    need(arbiter, "target==='hub'", 'Hub route mapping')
    need(arbiter, "target==='editor'", 'Editor route mapping')
    need(arbiter, "target==='short'", 'Short route mapping')
    need(arbiter, "e.data.type!=='GSF_SHELL_NAV'", 'canonical navigation listener')
    need(arbiter, 'requestAnimationFrame', 'post-navigation reconciliation')
    need(arbiter, 'pageshow', 'Safari back-forward recovery')
    need(arbiter, 'visibilitychange', 'Safari foreground recovery')

    # V367 deliberately reuses route events and bounded retries instead of
    # instantiating another observer on top of the V343 watchdog.
    if 'new MutationObserver' in arbiter:
        raise AssertionError('V367 must not instantiate another MutationObserver')

    fixture = (
        "import streamlit.components.v1 as _gsf_components_v343\n"
        "_gsf_components_v343.html('<script>window.__GSF_GLOBAL_SHELL_V343=1</script>', height=0)\n"
    )
    patched, changed = mod.patch_app(fixture, Path('fixture.py'))
    assert changed, 'V367 first application must modify the V343 bridge'
    need(patched, 'GSF_SINGLE_ACTIVE_SURFACE_V367', 'injected arbiter in V343 bridge')
    compile(patched, 'fixture.py', 'exec')

    patched_again, changed_again = mod.patch_app(patched, Path('fixture.py'))
    assert not changed_again, 'V367 must be restart-safe/idempotent'
    assert patched_again == patched, 'V367 second application must be byte-stable'

    print('V367 SINGLE ACTIVE SURFACE CONTRACT: PASS', flush=True)


if __name__ == '__main__':
    main()
