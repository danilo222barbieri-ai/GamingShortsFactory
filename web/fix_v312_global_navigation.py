#!/usr/bin/env python3
from pathlib import Path
import re
import sys

DEFAULT_ROOT = Path('/app')
HUB_CACHE_KEY = '3663'
HUB_CACHE_URL = f'/creator-hub-v156/?v={HUB_CACHE_KEY}&ui=profile-ref-2'


def _button_pattern(active: str) -> re.Pattern:
    return re.compile(
        r'<button\b(?=[^>]*\bdata-active="' + re.escape(active) + r'")[^>]*>.*?</button>',
        re.DOTALL,
    )


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
    # Do this while V154 is still ordinary source, before V343 serializes the
    # global shell into a large Python/JavaScript string. Late replacement can
    # invalidate quoting; source-time replacement cannot.
    if HUB_CACHE_URL in text:
        return text
    candidates = (
        '/creator-hub-v156/?v=3115&ui=profile-ref-2',
        '/creator-hub-v156/?v=3115',
    )
    for old in candidates:
        if old in text:
            return text.replace(old, HUB_CACHE_URL)
    raise RuntimeError('V312: Creator Hub cache-key anchor missing')


def patch_shell_text(text: str) -> str:
    # Final shared-page Game Bar source of truth. Do not preserve inherited route values.
    text = _normalize_button(text, 'home', 'home', None)
    text = _normalize_button(text, 'hub', 'hub', 'dashboard')
    text = _normalize_button(text, 'projects', 'hub', 'projects')
    text = _normalize_button(text, 'live', 'hub', 'live')

    # Hub means dashboard only, never the page previously visited.
    text = re.sub(
        r"else if\(target==='hub'\) active=\([^;]*\);",
        "else if(target==='hub') active=(lastTarget==='hub'&&(lastSection==='dashboard'||!lastSection));",
        text,
        count=1,
    )
    text = _bump_hub_cache(text)
    return text


def main() -> None:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
    app = root / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
    home = root / 'web' / 'home_v154_component' / 'index.html'
    if not app.is_file():
        raise SystemExit(f'V312 shell missing: {app}')
    if not home.is_file():
        raise SystemExit(f'V312 Home missing: {home}')

    # IMPORTANT: Home navigation is owned by V302. V312.0 attempted to rewrite
    # its JS with a generic regex and could split the Projects handler, aborting
    # the entire Home navigation script. Never rewrite Home routes here.
    app_before = app.read_text(encoding='utf-8')
    app_after = patch_shell_text(app_before)

    compile(app_after, str(app), 'exec')
    app.write_text(app_after, encoding='utf-8')
    print('V312.2 shared-page navigation + safe Hub cache bump normalized; Home routes preserved from V302:',
          'shell_changed=', app_before != app_after,
          'hub_cache=', HUB_CACHE_KEY,
          flush=True)


if __name__ == '__main__':
    main()
