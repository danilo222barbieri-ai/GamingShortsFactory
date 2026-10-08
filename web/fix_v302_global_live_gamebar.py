#!/usr/bin/env python3
from pathlib import Path
import re

HOME = Path('/app/web/home_v154_component/index.html')
APP = Path('/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')

LIVE_SVG = '<svg viewBox="0 0 32 32"><g transform="rotate(-8 16 16)"><circle cx="16" cy="14" r="3"/><path d="M16 17v10M11 27h10"/><path d="M9.5 8.5a8 8 0 0 0 0 11M22.5 8.5a8 8 0 0 1 0 11"/><path d="M6 5a13 13 0 0 0 0 18M26 5a13 13 0 0 1 0 18"/></g></svg>'


def _normalise_button(button: str, *, target: str, section: str = '', active: str = '', label: str = '') -> str:
    open_end = button.find('>')
    if open_end < 0:
        return button
    body = button[open_end+1:]
    attrs = ['class="gsf-page-nav-item"', f'data-target="{target}"']
    if section:
        attrs.append(f'data-section="{section}"')
    if active:
        attrs.append(f'data-active="{active}"')
    attrs.append('type="button"')
    if label:
        body = re.sub(r'<span>[^<]*</span>', f'<span>{label}</span>', body, count=1)
    return '<button ' + ' '.join(attrs) + '>' + body


def _four_column_gamebar(text: str, selector: str) -> str:
    pat = re.compile(
        r'('+re.escape(selector)+r'\s*\{[^{}]*?grid-template-columns\s*:)\s*repeat\(5\s*,\s*1fr\)',
        re.DOTALL,
    )
    return pat.sub(r'\1repeat(4,1fr)', text)


def patch_home() -> None:
    text = HOME.read_text(encoding='utf-8')
    before = text

    # The Home Game Bar is canonical too: Home / Hub / Progetti / Live.
    text = re.sub(
        r'\s*<button class="navItem" data-nav="shorts">.*?</button>',
        '', text, count=1, flags=re.DOTALL,
    )

    def home_button(match: re.Match) -> str:
        button = match.group(0)
        nav = match.group('nav')
        if nav in ('home', 'hub', 'projects'):
            return button
        if nav in ('social', 'live'):
            button = re.sub(r'data-nav="(?:social|live)"', 'data-nav="live"', button, count=1)
            button = re.sub(r'<svg viewBox="0 0 32 32">.*?</svg>', LIVE_SVG, button, count=1, flags=re.DOTALL)
            button = re.sub(r'<span>[^<]*</span>', '<span>Live</span>', button, count=1)
            return button
        return button

    text = re.sub(
        r'<button class="navItem(?: active)?" data-nav="(?P<nav>[^"]+)">.*?</button>',
        home_button, text, flags=re.DOTALL,
    )

    # Explicit routes. No route derives its destination from previous state.
    text = text.replace('if(nav==="hub")shellNav("hub",{section:"profile"});', 'if(nav==="hub")shellNav("hub",{section:"dashboard"});')
    text = text.replace('if(nav==="projects"){shellNav("hub",{section:"project"});value({event:"open_projects",section:"project"});}', 'if(nav==="projects"){shellNav("hub",{section:"projects"});value({event:"open_projects",section:"projects"});}')
    text = text.replace('if(nav==="social")shellNav("hub",{section:"social"});', 'if(nav==="live")shellNav("hub",{section:"live"});')

    # Defensive cleanup for already partially-patched source.
    text = text.replace('if(nav==="hub")shellNav("hub");', 'if(nav==="hub")shellNav("hub",{section:"dashboard"});')
    text = text.replace('if(nav==="projects")shellNav("hub",{section:"project"});', 'if(nav==="projects")shellNav("hub",{section:"projects"});')

    text = _four_column_gamebar(text, '.bottomNav')
    text = _four_column_gamebar(text, '#home154 .bottomNav')

    required = [
        'data-nav="home"',
        'data-nav="hub"',
        'data-nav="projects"',
        'data-nav="live"',
        'if(nav==="hub")shellNav("hub",{section:"dashboard"});',
        'if(nav==="projects"){shellNav("hub",{section:"projects"});',
        'if(nav==="live")shellNav("hub",{section:"live"});',
    ]
    missing = [m for m in required if m not in text]
    if missing:
        raise RuntimeError('V302 Home Game Bar canonical routes missing: ' + ', '.join(missing))
    nav_match = re.search(r'<nav class="bottomNav".*?</nav>', text, flags=re.DOTALL)
    nav_markup = nav_match.group(0) if nav_match else ''
    if not nav_markup or 'data-nav="shorts"' in nav_markup or 'data-nav="social"' in nav_markup:
        raise RuntimeError('V302 visible Home Game Bar still contains legacy destinations')

    HOME.write_text(text, encoding='utf-8')
    print('V302 Home Game Bar canonical: Home / Hub dashboard / Projects / Live; changed=', text != before, flush=True)


def patch_app() -> None:
    text = APP.read_text(encoding='utf-8')
    before = text

    # Normalize the shared page Game Bar to exactly four destinations.
    button_pat = re.compile(r'<button\b[^>]*class="gsf-page-nav-item"[^>]*>.*?</button>', re.DOTALL)
    buttons = list(button_pat.finditer(text))
    for match in reversed(buttons):
        button = match.group(0)
        label_match = re.search(r'<span>([^<]*)</span>', button)
        label = (label_match.group(1).strip() if label_match else '')
        low = label.lower()
        updated = button
        if low == 'home':
            updated = _normalise_button(button, target='home', active='home', label='Home')
        elif low == 'hub':
            updated = _normalise_button(button, target='hub', section='dashboard', active='hub', label='Hub')
        elif low in ('bozze', 'progetti'):
            updated = _normalise_button(button, target='hub', section='projects', active='projects', label='Progetti')
        elif low in ('social', 'live'):
            updated = _normalise_button(button, target='hub', section='live', active='live', label='Live')
            updated = re.sub(r'<svg viewBox="0 0 32 32">.*?</svg>', LIVE_SVG, updated, count=1, flags=re.DOTALL)
        elif low in ('i miei shorts', 'shorts'):
            updated = ''
        if updated != button:
            text = text[:match.start()] + updated + text[match.end():]

    text = _four_column_gamebar(text, '#gsf-page-nav-v249')

    old_active = '''          if(activeKey==='drafts') active=(lastTarget==='hub'&&lastSection==='drafts');
          else if(activeKey==='shorts') active=(lastTarget==='hub'&&lastSection==='shorts');
          else if(activeKey==='social') active=(lastTarget==='hub'&&lastSection==='social');
          else if(target==='hub') active=(lastTarget==='hub'&&lastSection!=='drafts'&&lastSection!=='shorts'&&lastSection!=='social');
          else active=(lastTarget===target);'''
    new_active = '''          if(activeKey==='home') active=(lastTarget==='home');
          else if(activeKey==='hub') active=(lastTarget==='hub'&&(lastSection==='dashboard'||!lastSection));
          else if(activeKey==='projects') active=(lastTarget==='hub'&&lastSection==='projects');
          else if(activeKey==='live') active=(lastTarget==='hub'&&lastSection==='live');
          else active=false;'''
    if old_active in text:
        text = text.replace(old_active, new_active, 1)
    else:
        text = re.sub(
            r"\s*if\(activeKey==='drafts'\).*?else active=\(lastTarget===target\);",
            '\n'+new_active,
            text, count=1, flags=re.DOTALL,
        )

    # Repeated Hub presses must always mean dashboard, never a remembered section.
    text = text.replace("lastTarget='hub';lastSection=String(e.data.section||'profile');", "lastTarget='hub';lastSection=String(e.data.section||'dashboard');")
    text = text.replace("const section=String(e.data.section||(t==='profile'?'profile':'profile'));", "const section=String(e.data.section||(t==='profile'?'profile':'dashboard'));")

    required = [
        'data-target="home" data-active="home"',
        'data-target="hub" data-section="dashboard" data-active="hub"',
        'data-section="projects" data-active="projects"',
        'data-section="live" data-active="live"',
        "activeKey==='projects'",
        "activeKey==='live'",
        "lastSection=String(e.data.section||'dashboard')",
        "t==='profile'?'profile':'dashboard'",
    ]
    missing = [m for m in required if m not in text]
    if missing:
        raise RuntimeError('V302 global Game Bar canonical routes missing: ' + ', '.join(missing))

    APP.write_text(text, encoding='utf-8')
    print('V302 global Game Bar canonical: Home / Hub dashboard / Projects / Live; changed=', text != before, flush=True)


if __name__ == '__main__':
    if not HOME.is_file() or not APP.is_file():
        raise RuntimeError('V302 required files missing')
    patch_home()
    patch_app()
