#!/usr/bin/env python3
from pathlib import Path
import re
import sys

DEFAULT_ROOT = Path('/app')


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


def patch_shell_text(text: str) -> str:
    # Final navigation source of truth. Do not preserve inherited route values.
    text = _normalize_button(text, 'home', 'home', None)
    text = _normalize_button(text, 'hub', 'hub', 'dashboard')
    text = _normalize_button(text, 'projects', 'hub', 'projects')
    text = _normalize_button(text, 'live', 'hub', 'live')

    # Active state is also explicit: Hub means dashboard only, never the page
    # previously visited (Editor/Profile/Projects/Live).
    text = re.sub(
        r"else if\(target==='hub'\) active=\([^;]*\);",
        "else if(target==='hub') active=(lastTarget==='hub'&&(lastSection==='dashboard'||!lastSection));",
        text,
        count=1,
    )
    return text


def patch_home_text(text: str) -> str:
    # Home component already uses data-nav. Reassert the four routes explicitly
    # so a historical replacement cannot redirect Hub through Editor state.
    replacements = {
        'home': 'if(nav==="home")shellNav("home");',
        'hub': 'if(nav==="hub")shellNav("hub",{section:"dashboard"});',
        'projects': 'if(nav==="projects")shellNav("hub",{section:"projects"});',
        'live': 'if(nav==="live")shellNav("hub",{section:"live"});',
    }
    for key, canonical in replacements.items():
        # Replace any one-line conditional for this nav key, regardless of stale target.
        pattern = re.compile(r'if\(nav==="' + re.escape(key) + r'"\)(?:\{)?[^\n;]*;(?:\})?')
        if pattern.search(text):
            text = pattern.sub(canonical, text, count=1)
        elif canonical not in text:
            raise RuntimeError(f'V312: Home route anchor missing for {key}')
    return text


def main() -> None:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
    app = root / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
    home = root / 'web' / 'home_v154_component' / 'index.html'
    if not app.is_file():
        raise SystemExit(f'V312 shell missing: {app}')
    if not home.is_file():
        raise SystemExit(f'V312 Home missing: {home}')

    app_before = app.read_text(encoding='utf-8')
    home_before = home.read_text(encoding='utf-8')
    app_after = patch_shell_text(app_before)
    home_after = patch_home_text(home_before)

    compile(app_after, str(app), 'exec')
    app.write_text(app_after, encoding='utf-8')
    home.write_text(home_after, encoding='utf-8')
    print('V312 canonical global navigation applied:',
          'shell_changed=', app_before != app_after,
          'home_changed=', home_before != home_after,
          flush=True)


if __name__ == '__main__':
    main()
