#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path('/app')
WEB = ROOT / 'web'

COMPONENTS = (
    WEB / 'home_v154_component' / 'index.html',
    WEB / 'ai_v221_component' / 'index.html',
    WEB / 'creator_hub_v156_component' / 'index.html',
    WEB / 'editor_2027_component' / 'index.html',
    WEB / 'share_v156_component' / 'index.html',
)
SHELL = ROOT / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
HOME_EMBED = WEB / 'home_v154_embed.py'
EDITOR_EMBED = WEB / 'editor_2027_embed.py'

LEGACY_SCRIPT_RE = re.compile(
    r'<script\b[^>]*\bid=["\'](?:v297[^"\']*|v298[^"\']*)["\'][^>]*>.*?</script\s*>',
    re.IGNORECASE | re.DOTALL,
)
LEGACY_STYLE_RE = re.compile(
    r'<style\b[^>]*\bid=["\']v305[^"\']*["\'][^>]*>.*?</style\s*>',
    re.IGNORECASE | re.DOTALL,
)
DESK_LAYOUT_ATTR_RE = re.compile(r'\sdata-v29[78]-layout=(?:"[^"]*"|\'[^\']*\')', re.IGNORECASE)
MEDIA_START_RE = re.compile(r'@media\s*([^\{]+)\{', re.IGNORECASE)
MOBILE_MAX_RE = re.compile(r'max-width\s*:\s*(\d+(?:\.\d+)?)px', re.IGNORECASE)


def _find_matching_brace(text: str, open_index: int) -> int:
    depth = 0
    quote = None
    escaped = False
    i = open_index
    n = len(text)
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ''
        if quote:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch in ('"', "'"):
            quote = ch
            i += 1
            continue
        if ch == '/' and nxt == '*':
            end = text.find('*/', i + 2)
            if end < 0:
                return -1
            i = end + 2
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _is_mobile_viewport_condition(condition: str) -> bool:
    lower = condition.lower()
    if 'min-width' in lower:
        return False
    widths = [float(x) for x in MOBILE_MAX_RE.findall(lower)]
    return bool(widths) and max(widths) <= 1024


def transform_media(text: str) -> str:
    out = []
    pos = 0
    while True:
        match = MEDIA_START_RE.search(text, pos)
        if not match:
            out.append(text[pos:])
            break
        open_index = match.end() - 1
        close_index = _find_matching_brace(text, open_index)
        if close_index < 0:
            out.append(text[pos:])
            break
        out.append(text[pos:match.start()])
        condition = match.group(1).strip()
        inner = transform_media(text[open_index + 1:close_index])
        lower = condition.lower()
        if 'min-width' in lower:
            replacement = ''
        elif _is_mobile_viewport_condition(condition):
            replacement = inner
        else:
            replacement = text[match.start():open_index + 1] + inner + '}'
        out.append(replacement)
        pos = close_index + 1
    return ''.join(out)


def _remove_marked_desktop_blocks(text: str) -> str:
    # V296 was entirely a desktop visual pass even though its marker omitted the word desktop.
    text = re.sub(
        r'/\*\s*V296 VISIBLE INTERNAL PAGES\b.*?/\*\s*END V296 VISIBLE INTERNAL PAGES\b.*?\*/',
        '',
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    # Remove any historical version block explicitly named DESKTOP/DESK in its opening marker.
    start_re = re.compile(r'/\*\s*(V\d+[^*]*(?:DESKTOP|\bDESK\b|EDITOR GRAPHIC ONLY)[^*]*)\*/', re.IGNORECASE)
    scan = 0
    while True:
        match = start_re.search(text, scan)
        if not match:
            break
        version_match = re.search(r'V(\d+)', match.group(1), re.IGNORECASE)
        if not version_match:
            scan = match.end()
            continue
        version = version_match.group(1)
        end_re = re.compile(r'/\*\s*END\s+V' + re.escape(version) + r'[^*]*\*/', re.IGNORECASE)
        end = end_re.search(text, match.end())
        if end:
            text = text[:match.start()] + text[end.end():]
            scan = match.start()
        else:
            text = text[:match.start()] + text[match.end():]
            scan = match.start()
    return text


def sanitize_text(text: str) -> str:
    """Sanitize HTML/CSS component source only. Never pass Python source here."""
    text = LEGACY_STYLE_RE.sub('', text)
    text = LEGACY_SCRIPT_RE.sub('', text)
    text = DESK_LAYOUT_ATTR_RE.sub('', text)
    text = _remove_marked_desktop_blocks(text)
    text = transform_media(text)
    # Remove orphaned comments that only label old desktop passes.
    text = re.sub(r'/\*[^*]*(?:DESKTOP|\bDESK\b)[^*]*\*/', '', text, flags=re.IGNORECASE)
    return text


def has_viewport_min_width_media(text: str) -> bool:
    for match in MEDIA_START_RE.finditer(text):
        if 'min-width' in match.group(1).lower():
            return True
    return False


def _rewrite_component(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError('V307 required component missing: ' + str(path))
    original = path.read_text(encoding='utf-8')
    cleaned = sanitize_text(original)
    if cleaned != original:
        path.write_text(cleaned, encoding='utf-8')
        print('V307 visual purge:', path, flush=True)
    else:
        print('V307 already clean:', path, flush=True)


def _bump_cache_keys() -> None:
    if HOME_EMBED.is_file():
        text = HOME_EMBED.read_text(encoding='utf-8')
        text, count = re.subn(r'"gsf_home_v154_live_[^"]+"', '"gsf_home_v154_live_307"', text, count=1)
        if count == 0 and '"gsf_home_v154_live_307"' not in text:
            raise RuntimeError('V307 Home cache key anchor missing')
        HOME_EMBED.write_text(text, encoding='utf-8')
    if EDITOR_EMBED.is_file():
        text = EDITOR_EMBED.read_text(encoding='utf-8')
        text, count = re.subn(r'"gsf_editor_2027_v[^"]+"', '"gsf_editor_2027_v307"', text, count=1)
        if count == 0 and '"gsf_editor_2027_v307"' not in text:
            raise RuntimeError('V307 Editor cache key anchor missing')
        EDITOR_EMBED.write_text(text, encoding='utf-8')
    if SHELL.is_file():
        # The shell is Python and can contain f-strings with doubled CSS braces.
        # Only update route cache keys; never run the raw CSS/media sanitizer on it.
        text = SHELL.read_text(encoding='utf-8')
        for route in ('creator-hub-v156', 'share-v156', 'ai-v221'):
            text = re.sub(rf'/{route}/\?v=[^"\'&\s]+', f'/{route}/?v=307', text)
        compile(text, str(SHELL), 'exec')
        SHELL.write_text(text, encoding='utf-8')


def main(root: Path = ROOT) -> None:
    global ROOT, WEB, COMPONENTS, SHELL, HOME_EMBED, EDITOR_EMBED
    if root != ROOT:
        ROOT = root
        WEB = ROOT / 'web'
        COMPONENTS = (
            WEB / 'home_v154_component' / 'index.html',
            WEB / 'ai_v221_component' / 'index.html',
            WEB / 'creator_hub_v156_component' / 'index.html',
            WEB / 'editor_2027_component' / 'index.html',
            WEB / 'share_v156_component' / 'index.html',
        )
        SHELL = ROOT / 'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
        HOME_EMBED = WEB / 'home_v154_embed.py'
        EDITOR_EMBED = WEB / 'editor_2027_embed.py'
    for path in COMPONENTS:
        _rewrite_component(path)
    _bump_cache_keys()
    print('V307 mobile visual source applied: HTML visual history purged; Python shell preserved', flush=True)


if __name__ == '__main__':
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
    main(root)
