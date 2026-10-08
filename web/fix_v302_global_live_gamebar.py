#!/usr/bin/env python3
from pathlib import Path
import re

HOME = Path('/app/web/home_v154_component/index.html')
APP = Path('/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')

OLD_HOME = '''<button class="navItem" data-nav="social"><svg viewBox="0 0 32 32"><circle cx="24" cy="7" r="3"/><circle cx="8" cy="16" r="3"/><circle cx="24" cy="25" r="3"/><path d="m11 14.5 10-5.7M11 17.5l10 5.7"/></svg><span>Social</span></button>'''
NEW_HOME = '''<button class="navItem" data-nav="live"><svg viewBox="0 0 32 32"><g transform="rotate(-8 16 16)"><circle cx="16" cy="14" r="3"/><path d="M16 17v10M11 27h10"/><path d="M9.5 8.5a8 8 0 0 0 0 11M22.5 8.5a8 8 0 0 1 0 11"/><path d="M6 5a13 13 0 0 0 0 18M26 5a13 13 0 0 1 0 18"/></g></svg><span>Live</span></button>'''

OLD_PAGE = '''<button class="gsf-page-nav-item" data-target="hub" data-section="social" data-active="social" type="button">
        <svg viewBox="0 0 32 32"><circle cx="24" cy="7" r="3"/><circle cx="8" cy="16" r="3"/><circle cx="24" cy="25" r="3"/><path d="m11 14.5 10-5.7M11 17.5l10 5.7"/></svg><span>Social</span>
      </button>'''
NEW_PAGE = '''<button class="gsf-page-nav-item" data-target="hub" data-section="live" data-active="live" type="button">
        <svg viewBox="0 0 32 32"><g transform="rotate(-8 16 16)"><circle cx="16" cy="14" r="3"/><path d="M16 17v10M11 27h10"/><path d="M9.5 8.5a8 8 0 0 0 0 11M22.5 8.5a8 8 0 0 1 0 11"/><path d="M6 5a13 13 0 0 0 0 18M26 5a13 13 0 0 1 0 18"/></g></svg><span>Live</span>
      </button>'''


def once(text, old, new, label):
    if new in text:
        return text
    if text.count(old) != 1:
        raise RuntimeError(f'V302 {label}: expected one anchor, found {text.count(old)}')
    return text.replace(old, new, 1)


def force_hub_dashboard(text: str) -> str:
    """The Hub tab must always reopen the Creator Hub landing/dashboard."""
    pattern = re.compile(r'<button\b(?=[^>]*\bdata-active="hub")[^>]*>', re.DOTALL)
    match = pattern.search(text)
    if not match:
        return text
    tag = match.group(0)
    if re.search(r'\bdata-target="[^"]*"', tag):
        tag = re.sub(r'\bdata-target="[^"]*"', 'data-target="hub"', tag, count=1)
    else:
        tag = tag[:-1] + ' data-target="hub">'
    if re.search(r'\bdata-section="[^"]*"', tag):
        tag = re.sub(r'\bdata-section="[^"]*"', 'data-section="dashboard"', tag, count=1)
    else:
        tag = tag[:-1] + ' data-section="dashboard">'
    return text[:match.start()] + tag + text[match.end():]


def patch_home():
    text = HOME.read_text(encoding='utf-8')
    text = once(text, OLD_HOME, NEW_HOME, 'Home nav')
    text = once(text,
        'if(nav==="social")shellNav("hub",{section:"social"});',
        'if(nav==="live")shellNav("hub",{section:"live"});',
        'Home Live route')
    HOME.write_text(text, encoding='utf-8')
    print('V302 Home Game Bar: Social -> Live', flush=True)


def patch_app():
    text = APP.read_text(encoding='utf-8')
    text = once(text, OLD_PAGE, NEW_PAGE, 'page Game Bar')
    text = once(text,
        "else if(activeKey==='social') active=(lastTarget==='hub'&&lastSection==='social');",
        "else if(activeKey==='live') active=(lastTarget==='hub'&&lastSection==='live');",
        'Live active state')
    text = once(text,
        "else if(target==='hub') active=(lastTarget==='hub'&&lastSection!=='drafts'&&lastSection!=='shorts'&&lastSection!=='social');",
        "else if(target==='hub') active=(lastTarget==='hub'&&lastSection!=='drafts'&&lastSection!=='shorts'&&lastSection!=='live');",
        'Hub active state')
    text = force_hub_dashboard(text)
    APP.write_text(text, encoding='utf-8')
    print('V302 global page Game Bar: Hub -> Creator Hub dashboard; Social -> Live', flush=True)


if __name__ == '__main__':
    if not HOME.is_file() or not APP.is_file():
        raise RuntimeError('V302 required files missing')
    patch_home()
    patch_app()
