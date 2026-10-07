#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path('/app')
WEB = ROOT / 'web'

MEDIA_START_RE = re.compile(r'@media\s*([^\{]+)\{', re.IGNORECASE)
MOBILE_MAX_RE = re.compile(r'max-width\s*:\s*(\d+(?:\.\d+)?)px', re.IGNORECASE)
LEGACY_SCRIPT_RE = re.compile(
    r'<script\b[^>]*\bid=["\'](?:v297[^"\']*|v298[^"\']*)["\'][^>]*>.*?</script\s*>',
    re.IGNORECASE | re.DOTALL,
)
LEGACY_STYLE_RE = re.compile(
    r'<style\b[^>]*\bid=["\']v305[^"\']*["\'][^>]*>.*?</style\s*>',
    re.IGNORECASE | re.DOTALL,
)
DESK_LAYOUT_ATTR_RE = re.compile(r'\sdata-v29[78]-layout=(?:"[^"]*"|\'[^\']*\')', re.IGNORECASE)


FLUID_CSS = {
    'home': r'''
#home154{
  width:min(100%,1600px)!important;max-width:1600px!important;height:100dvh!important;max-height:none!important;
  margin:0 auto!important;padding:clamp(8px,1.2vh,20px) clamp(10px,2.8vw,48px) clamp(8px,1.2vh,16px)!important;
  border-radius:clamp(20px,2.4vw,34px)!important;
}
#home154 .stage{min-height:clamp(280px,48dvh,620px)!important;display:flex!important;align-items:center!important;justify-content:center!important}
#home154 .rings{width:clamp(235px,min(38vw,44dvh),430px)!important;height:clamp(235px,min(38vw,44dvh),430px)!important}
#home154 .icon{width:clamp(56px,4.8vw,76px)!important;height:clamp(56px,4.8vw,76px)!important;margin-bottom:clamp(12px,1.5vh,20px)!important}
#home154 .circle strong{font-size:clamp(18px,1.45vw,24px)!important;max-width:clamp(205px,18vw,285px)!important}
#home154 .scribble{font-size:clamp(18px,1.6vw,28px)!important;width:clamp(165px,18vw,255px)!important}
#home154 .scribble.left{left:clamp(8px,6.8vw,150px)!important;top:clamp(112px,17dvh,188px)!important}
#home154 .scribble.right{right:clamp(8px,6.8vw,150px)!important;top:clamp(112px,17dvh,188px)!important}
#home154 .features{width:min(100%,1180px)!important;margin:clamp(-2px,-.2vh,0px) auto clamp(7px,1vh,13px)!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:clamp(7px,1.2vw,22px)!important}
#home154 .feature{min-height:clamp(88px,11dvh,138px)!important;padding:clamp(8px,1.1vh,14px) clamp(8px,1.4vw,20px)!important;border-radius:clamp(17px,1.6vw,24px)!important}
#home154 .featureIcon{width:clamp(40px,3.5vw,54px)!important;height:clamp(40px,3.5vw,54px)!important}
#home154 .feature b{font-size:clamp(13px,1.05vw,17px)!important}
#home154 .feature small{font-size:clamp(8px,.72vw,11px)!important}
#home154 .bottomNav,#home154 .siteFooter{width:min(100%,1180px)!important;margin-left:auto!important;margin-right:auto!important}
''',
    'ai': r'''
#ai221{width:min(100%,1400px)!important;max-width:1400px!important;height:100dvh!important;margin:0 auto!important;overflow:hidden!important;padding:clamp(9px,1.35vw,22px)!important}
#ai221 .top{gap:clamp(8px,1.2vw,18px)!important;margin-bottom:clamp(8px,1.2vh,14px)!important}
#ai221 h1{font-size:clamp(20px,2.2vw,34px)!important}
#ai221 .titleIcon{width:clamp(40px,4vw,52px)!important;height:clamp(40px,4vw,52px)!important}
#ai221 .panel{padding:clamp(9px,1.15vw,15px)!important;border-radius:clamp(20px,1.8vw,27px)!important}
#ai221 .engines{grid-template-columns:repeat(auto-fit,minmax(clamp(145px,18vw,260px),1fr))!important;gap:clamp(6px,.85vw,12px)!important}
#ai221 .engine{min-height:clamp(137px,18dvh,190px)!important;padding:clamp(9px,1vw,13px)!important;border-radius:clamp(16px,1.5vw,21px)!important}
#ai221 .engineIcon{width:clamp(34px,3.2vw,44px)!important;height:clamp(34px,3.2vw,44px)!important}
#ai221 .engine h3{font-size:clamp(11px,1.1vw,15px)!important}
#ai221 .engine p{font-size:clamp(8.5px,.75vw,10px)!important}
#ai221 .moments{grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:clamp(6px,.85vw,12px)!important}
#ai221 .moment{min-height:clamp(90px,12dvh,116px)!important}
''',
    'hub': r'''
#hub{width:min(100%,1180px)!important;max-width:1180px!important;height:100dvh!important;margin:0 auto!important;padding:clamp(7px,1.2vw,18px)!important;gap:clamp(6px,.8vw,12px)!important}
#hub h1{font-size:clamp(19px,2.1vw,31px)!important}
#hub .titleIcon{width:clamp(38px,3.6vw,48px)!important;height:clamp(38px,3.6vw,48px)!important}
#hub .profileCard{min-height:clamp(86px,11dvh,112px)!important;padding:clamp(8px,1vw,14px)!important}
#hub .folders{grid-template-columns:repeat(auto-fit,minmax(clamp(145px,28vw,360px),1fr))!important;grid-auto-rows:minmax(0,1fr)!important;gap:clamp(6px,.8vw,12px)!important}
#hub .folder{padding:clamp(8px,1vw,14px)!important;border-radius:clamp(17px,1.5vw,23px)!important}
#hub .folderIcon{width:clamp(30px,3vw,38px)!important;height:clamp(30px,3vw,38px)!important}
#hub .folder h2{font-size:clamp(12.7px,1.1vw,15px)!important}
#hub .folder p{font-size:clamp(8.4px,.72vw,10px)!important}
#hub .detailCard{padding:clamp(7px,1vw,13px)!important;border-radius:clamp(18px,1.5vw,23px)!important}
''',
    'share': r'''
#share{width:min(100%,1320px)!important;max-width:1320px!important;height:100dvh!important;margin:0 auto!important;overflow:auto!important;padding:clamp(10px,1.45vw,22px)!important}
#share h1{font-size:clamp(21px,2.2vw,34px)!important}
#share .titleIcon{width:clamp(42px,4vw,52px)!important;height:clamp(42px,4vw,52px)!important}
#share .section{padding:clamp(10px,1.15vw,15px)!important;border-radius:clamp(20px,1.8vw,27px)!important}
#share .socials{grid-template-columns:repeat(auto-fit,minmax(clamp(145px,19vw,280px),1fr))!important;gap:clamp(7px,.9vw,12px)!important}
#share .card{min-height:clamp(150px,18dvh,195px)!important;padding:clamp(10px,1vw,14px)!important;border-radius:clamp(17px,1.5vw,22px)!important}
#share .logo{width:clamp(36px,3.2vw,44px)!important;height:clamp(36px,3.2vw,44px)!important}
#share .downloadRow{grid-template-columns:minmax(0,1fr) auto!important;gap:clamp(8px,1vw,16px)!important}
#share .downloadBtn{padding:clamp(11px,1vw,14px) clamp(14px,1.6vw,22px)!important;font-size:clamp(9px,.9vw,12px)!important}
''',
    'editor': r'''
#ng27 .shell{width:100%!important;max-width:min(96vw,980px)!important;margin:0 auto!important;padding:clamp(3px,.7vw,10px)!important;border-radius:clamp(18px,1.8vw,26px)!important}
#ng27 .cockpit{grid-template-columns:clamp(48px,6vw,84px) minmax(0,1fr) clamp(48px,6vw,84px)!important;gap:clamp(6px,.8vw,12px)!important}
#ng27 .rail{gap:clamp(5px,.65vw,9px)!important}
#ng27 .railBtn{width:clamp(46px,5.5vw,76px)!important;height:clamp(46px,5.5vw,76px)!important;border-radius:clamp(14px,1.4vw,20px)!important}
#ng27 .railBtn .ico{width:clamp(20px,2vw,27px)!important;height:clamp(20px,2vw,27px)!important}
#ng27 .railBtn span{font-size:clamp(7px,.68vw,9px)!important}
#ng27 .stage.r916{width:min(100%,clamp(220px,28vw,360px))!important;aspect-ratio:9/16!important;border-radius:clamp(18px,1.8vw,24px)!important}
#ng27 .timeline{width:min(96%,780px)!important;margin-left:auto!important;margin-right:auto!important}
#ng27 .zoomEditorBtn{height:clamp(24px,2.5vw,32px)!important}
''',
}


def _find_matching_brace(text: str, open_index: int) -> int:
    depth = 0
    quote = None
    escaped = False
    i = open_index
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ''
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
    text = re.sub(
        r'/\*\s*V296 VISIBLE INTERNAL PAGES\b.*?/\*\s*END V296 VISIBLE INTERNAL PAGES\b.*?\*/',
        '', text, flags=re.IGNORECASE | re.DOTALL,
    )
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


def _inject_master_style(surface: str, text: str) -> str:
    style_id = f'gsf-v308-{surface}-fluid-master'
    text = re.sub(
        rf'<style\b[^>]*\bid=["\']{re.escape(style_id)}["\'][^>]*>.*?</style\s*>',
        '', text, flags=re.IGNORECASE | re.DOTALL,
    )
    style = f'\n<style id="{style_id}">\n{FLUID_CSS[surface].strip()}\n</style>\n'
    pos = text.lower().find('</head>')
    if pos >= 0:
        return text[:pos] + style + text[pos:]
    return style + text


def canonicalize_text(surface: str, text: str) -> str:
    if surface not in FLUID_CSS:
        raise ValueError('unknown V308 surface: ' + str(surface))
    text = LEGACY_STYLE_RE.sub('', text)
    text = LEGACY_SCRIPT_RE.sub('', text)
    text = DESK_LAYOUT_ATTR_RE.sub('', text)
    text = _remove_marked_desktop_blocks(text)
    text = transform_media(text)
    text = re.sub(r'/\*[^*]*(?:DESKTOP|\bDESK\b)[^*]*\*/', '', text, flags=re.IGNORECASE)
    return _inject_master_style(surface, text)


def main(root: Path = ROOT) -> None:
    web = root / 'web'
    targets = {
        'home': web / 'home_v154_component' / 'index.html',
        'ai': web / 'ai_v221_component' / 'index.html',
        'hub': web / 'creator_hub_v156_component' / 'index.html',
        'share': web / 'share_v156_component' / 'index.html',
        'editor': web / 'editor_2027_component' / 'index.html',
    }
    for surface, path in targets.items():
        if not path.is_file():
            raise RuntimeError('V308 required surface missing: ' + str(path))
        original = path.read_text(encoding='utf-8')
        canonical = canonicalize_text(surface, original)
        path.write_text(canonical, encoding='utf-8')
        print(f'V308 canonical {surface}:', path, flush=True)
    print('V308 mobile-master canonicalization: PASS', flush=True)


if __name__ == '__main__':
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
    main(root)
