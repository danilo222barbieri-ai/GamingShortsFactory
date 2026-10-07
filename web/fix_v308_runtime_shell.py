#!/usr/bin/env python3
from pathlib import Path
import re
import sys

from web.ui_release import GSF_UI_RELEASE, versioned_path

ROOT = Path('/app')
SHELL = ROOT / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
NGINX = ROOT / 'web' / 'nginx.conf.template'

UI_ROUTES = ('creator-hub-v156', 'share-v156', 'ai-v221')


def normalize_shell(text: str) -> str:
    out = text
    for route in UI_ROUTES:
        target = versioned_path(f'/{route}/')
        out = re.sub(
            rf'/{re.escape(route)}/(?:\?v=[0-9A-Za-z._-]+)?',
            lambda _m, target=target: target,
            out,
        )
    return out


def _replace_location(text: str, header_pattern: str, replacement: str) -> str:
    pattern = re.compile(
        rf'(?ms)^\s*location\s+{header_pattern}\s*\{{.*?^\s*\}}\s*',
    )
    return pattern.sub(replacement.rstrip() + '\n\n', text, count=1)


def normalize_nginx(text: str) -> str:
    out = text
    out = _replace_location(
        out,
        r'=\s*/desktop-preview',
        '''    # V308 DESKTOP PREVIEW REDIRECT — one UI only.
    location = /desktop-preview {
        return 302 /;
    }''',
    )
    out = _replace_location(
        out,
        r'/desktop-preview/',
        '''    location /desktop-preview/ {
        return 302 /;
    }''',
    )
    out = _replace_location(
        out,
        r'=\s*/desktop-home',
        '''    # V308 DESKTOP HOME REDIRECT — one UI only.
    location = /desktop-home {
        return 302 /;
    }''',
    )
    out = _replace_location(
        out,
        r'/desktop-home/',
        '''    location /desktop-home/ {
        return 302 /;
    }''',
    )
    out = out.replace('add_header Cache-Control "no-store";', 'add_header Cache-Control "no-store, max-age=0" always;')
    out = out.replace('add_header Cache-Control "no-store" always;', 'add_header Cache-Control "no-store, max-age=0" always;')
    return out


def main(root: Path = ROOT) -> None:
    shell = root / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
    nginx = root / 'web' / 'nginx.conf.template'
    shell_text = normalize_shell(shell.read_text(encoding='utf-8'))
    nginx_text = normalize_nginx(nginx.read_text(encoding='utf-8'))
    shell.write_text(shell_text, encoding='utf-8')
    nginx.write_text(nginx_text, encoding='utf-8')
    print(f'V308 runtime shell normalized: release={GSF_UI_RELEASE}', flush=True)


if __name__ == '__main__':
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
    main(root)
