#!/usr/bin/env python3
from pathlib import Path
import re
import sys

DEFAULT_ROOT = Path('/app')
HUB_CACHE_KEY = '3663'
HUB_CACHE_URL = f'/creator-hub-v156/?v={HUB_CACHE_KEY}&ui=profile-ref-2'


def _button_pattern(active: str) -> re.Pattern:
    return re.compile(r'<button\b(?=[^>]*\bdata-active="' + re.escape(active) + r'")[^>]*>.*?</button>', re.DOTALL)


def _set_attr(button: str, name: str, value: str) -> str:
    attr = f'{name}="{value}"'
    pattern = r'\b' + re.escape(name) + r'="[^"]*"'
    if re.search(pattern, button):
        return re.sub(pattern, attr, button, count=1)
    return button.replace('>', ' ' + attr + '>', 1)


def _remove_attr(button: str, name: str) -> str:
    return re.sub(r'\s+\b' + re.escape(name) + r'="[^"]*"', '', button, count=1)


def _normalize_button(text: str, active: str, target: str, section: str | None) -> str:
    pattern = _button_pattern(active)
    match = pattern.search(text)
    if not match:
        # Restart-safe: V343 owns the canonical shell after the historical V312
        # migration has already been consumed. Do not make a later restart fatal.
        if 'GSF_SHELL_NAV' in text or 'V343' in text:
            return text
        raise RuntimeError(f'V312: missing Game Bar button data-active={active}')
    button = match.group(0)
    button = _set_attr(button, 'data-target', target)
    button = _set_attr(button, 'data-active', active)
    if section is None:
        button = _remove_attr(button, 'data-section')
    else:
        button = _set_attr(button, 'data-section', section)
    return pattern.sub(lambda _m: button, text, count=1)


def _bump_hub_cache(text: str) -> str:
    if HUB_CACHE_URL in text:
        return text
    pattern = re.compile(r'/creator-hub-v156/\?v=\d+(?:&ui=profile-ref-2)?')
    if pattern.search(text):
        return pattern.sub(HUB_CACHE_URL, text)
    # The cache URL is historical migration state. Once V343 has serialized the
    # canonical shell it may legitimately be absent; absence must be a no-op.
    if 'GSF_SHELL_NAV' in text or 'V343' in text:
        return text
    raise RuntimeError('V312: Creator Hub cache-key anchor missing')


def patch_shell_text(text: str) -> str:
    text = _normalize_button(text, 'home', 'home', None)
    text = _normalize_button(text, 'hub', 'hub', 'dashboard')
    text = _normalize_button(text, 'projects', 'hub', 'projects')
    text = _normalize_button(text, 'live', 'hub', 'live')
    text = re.sub(r"else if\(target==='hub'\) active=\([^;]*\);", "else if(target==='hub') active=(lastTarget==='hub'&&(lastSection==='dashboard'||!lastSection));", text, count=1)
    return _bump_hub_cache(text)


def main() -> None:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
    app = root / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
    home = root / 'web' / 'home_v154_component' / 'index.html'
    if not app.is_file(): raise SystemExit(f'V312 shell missing: {app}')
    if not home.is_file(): raise SystemExit(f'V312 Home missing: {home}')
    app_before = app.read_text(encoding='utf-8')
    app_after = patch_shell_text(app_before)
    compile(app_after, str(app), 'exec')
    app.write_text(app_after, encoding='utf-8')
    print('V312.3 shared-page navigation restart-safe; Home routes preserved:', 'shell_changed=', app_before != app_after, 'hub_cache=', HUB_CACHE_KEY, flush=True)


if __name__ == '__main__': main()
