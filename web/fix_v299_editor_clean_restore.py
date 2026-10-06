#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path('/app')
EDITOR = ROOT / 'web' / 'editor_2027_component' / 'index.html'
EMBED = ROOT / 'web' / 'editor_2027_embed.py'


def main() -> None:
    if not EDITOR.is_file() or not EMBED.is_file():
        raise RuntimeError('V299 required Editor files missing')

    editor = EDITOR.read_text(encoding='utf-8')
    # The restored file must be the pre-V297 Editor, not a second desktop shell.
    forbidden = (
        'V297 DESK REBUILD — EDITOR',
        'v297EditorRuntime',
        'V298 EDITOR GRAPHIC ONLY',
        'v298EditorGraphicOnly',
        'v298EditorWorkspace',
    )
    leftovers = [marker for marker in forbidden if marker in editor]
    if leftovers:
        raise RuntimeError('V299 restore still contains overlay layers: ' + ', '.join(leftovers))

    required = ('.cockpit', '.stage.r916', '.timeline', 'data-panel="frame"', 'data-panel="caption"')
    missing = [marker for marker in required if marker not in editor]
    if missing:
        raise RuntimeError('V299 restored Editor missing legacy controls: ' + ', '.join(missing))

    embed = EMBED.read_text(encoding='utf-8')
    patched, count = re.subn(r'"gsf_editor_2027_v\d+"', '"gsf_editor_2027_v299"', embed, count=1)
    if count != 1:
        raise RuntimeError('V299 editor cache key anchor missing')
    EMBED.write_text(patched, encoding='utf-8')

    print('V299 clean legacy Editor restored: PASS', flush=True)
    print('V299 Editor cache key: v299', flush=True)


if __name__ == '__main__':
    main()
