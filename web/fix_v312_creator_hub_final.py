#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import re
import sys

DEFAULT_HUB = Path('/app/web/creator_hub_v156_component/index.html')
DEFAULT_APP = Path('/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')
CACHE_KEY = '312'
BASE_PATCH = Path(__file__).with_name('fix_v312_creator_hub_design_sync.py')


def _load_base():
    spec = importlib.util.spec_from_file_location('v312_design_sync', BASE_PATCH)
    if spec is None or spec.loader is None:
        raise RuntimeError('V312 final: cannot load approved design module')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_width_independent(css: str) -> str:
    media = '@media(max-width:760px){'
    if media not in css:
        raise RuntimeError('V312 final: mobile media wrapper missing')
    body = css.replace(media, '', 1)
    end = '\n}\n/* END V312 CREATOR HUB DESIGN SYNC */'
    if end not in body:
        raise RuntimeError('V312 final: mobile media closing anchor missing')
    body = body.replace(end, '\n/* END V312 CREATOR HUB DESIGN SYNC */', 1)
    return '/* V312 CREATOR HUB FINAL */\n' + body


_base = _load_base()
FINAL_CSS = _make_width_independent(_base.CSS)


def patch_hub_text(text: str) -> str:
    # The public Creator Hub route is already mobile-gated. Do not depend on the
    # iframe width: this finalizer owns the whole Creator Hub visual contract.
    if 'V312 CREATOR HUB FINAL' in text:
        return text
    _base.CSS = FINAL_CSS
    return _base.patch_hub_text(text)


def patch_shell_text(text: str) -> str:
    target = f'/creator-hub-v156/?v={CACHE_KEY}'
    if target in text:
        return text
    updated, count = re.subn(
        r'/creator-hub-v156/\?v=[^"\'&\s]+',
        target,
        text,
    )
    if count < 1:
        raise RuntimeError('V312 final: Creator Hub shell cache anchor missing')
    return updated


def main() -> None:
    hub = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HUB
    app = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_APP
    if not hub.is_file():
        raise SystemExit(f'V312 final Hub target missing: {hub}')
    if not app.is_file():
        raise SystemExit(f'V312 final shell target missing: {app}')

    before = hub.read_text(encoding='utf-8')
    after = patch_hub_text(before)
    hub.write_text(after, encoding='utf-8')

    shell_before = app.read_text(encoding='utf-8')
    shell_after = patch_shell_text(shell_before)
    compile(shell_after, str(app), 'exec')
    app.write_text(shell_after, encoding='utf-8')

    print('V312 final Creator Hub applied:', hub, 'changed=', before != after, flush=True)
    print('V312 Creator Hub cache key:', 'v=' + CACHE_KEY, 'changed=', shell_before != shell_after, flush=True)


if __name__ == '__main__':
    main()
