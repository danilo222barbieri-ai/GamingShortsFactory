#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
HOME=ROOT/'web/home_v154_component/index.html'


def need(text, token, label):
    if token not in text:
        raise AssertionError(f'V341 missing {label}: {token}')


def main():
    if not APP.is_file() or not HOME.is_file():
        raise SystemExit('V341 runtime files missing')
    app=APP.read_text(encoding='utf-8')
    home=HOME.read_text(encoding='utf-8')

    need(app,'V341_GLOBAL_SHELL_CONTRACT','contract marker')
    need(app,'#gsf-v334-header{position:fixed','fixed global header')
    need(app,'#gsf-v334-gamebar{position:fixed','fixed global game bar')
    need(app,'#gsf-v334-footer{position:fixed','fixed global footer')
    need(app,'V341_DESKTOP_GLOBAL_CHROME','desktop global shell rule')
    need(app,'suppressLocalChrome','local chrome suppressor')
    need(app,'gsf-global-shell-active','child shell state')
    need(app,'data-gsf-v341-duplicate-chrome','duplicate brand marker')
    need(app,'.bottomNav,.siteFooter','local nav/footer suppression')
    need(app,'keepGlobalChromeMounted','global chrome watchdog')
    need(app,'<span class="v334AccountName">Accedi</span>','signed-out header label')
    need(home,'html.gsf-v334-parent-ready #home154 .topbar','home fallback handoff')

    forbidden='@media(min-width:761px){#gsf-v334-header,#gsf-v334-gamebar,#gsf-v334-footer{display:none!important}}'
    if forbidden in app:
        raise AssertionError('V341 global chrome still disabled on desktop')

    compile(app,str(APP),'exec')
    print('V341 global shell contract: PASS',flush=True)

if __name__=='__main__':
    main()
