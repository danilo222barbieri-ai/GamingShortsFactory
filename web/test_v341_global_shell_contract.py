#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
HOME=ROOT/'web/home_v154_component/index.html'


def need(text, token, label):
    if token not in text:
        raise AssertionError(f'V341 missing {label}: {token}')


def forbid(text, token, label):
    if token in text:
        raise AssertionError(f'V341 forbidden {label}: {token}')


def main():
    if not APP.is_file() or not HOME.is_file():
        raise SystemExit('V341 runtime files missing')
    app=APP.read_text(encoding='utf-8')
    home=HOME.read_text(encoding='utf-8')

    need(app,'V341_GLOBAL_SHELL_CONTRACT','contract marker')
    need(app,'V342_GLOBAL_CHROME_SAFEAREA','safe-area shell marker')
    need(app,'#gsf-v334-header{position:fixed','fixed global header')
    need(app,'#gsf-v334-gamebar{position:fixed','fixed global game bar')
    need(app,'#gsf-v334-footer{position:fixed','fixed global footer')
    need(app,'V341_DESKTOP_GLOBAL_CHROME','desktop global shell rule')
    need(app,'suppressLocalChrome','local chrome suppressor')
    need(app,'gsf-global-shell-active','child shell state')
    need(app,'data-gsf-v341-duplicate-chrome','duplicate brand marker')
    need(app,'keepGlobalChromeMounted','global chrome watchdog')
    need(app,'<span class="v334AccountName">Accedi</span>','signed-out header label')
    need(app,"a.display_name||a.nickname||a.name||a.username||String(a.email||'').split('@')[0]",'account display-name fallback')
    need(app,'--gsf-v334-safe-bottom:max(8px,env(safe-area-inset-bottom))','mobile safe bottom variable')
    need(app,'bottom:calc(var(--gsf-v334-foot) + var(--gsf-v334-safe-bottom) + 6px)','gamebar above footer')
    need(app,'height:calc(var(--gsf-v334-foot) + var(--gsf-v334-safe-bottom))','footer includes safe area')
    need(app,'background-image:url("${LOGO}")','visible logo image')

    need(home,'html.gsf-v334-parent-ready #home154 .topbar','home fallback handoff')
    need(home,'V342_EDITOR_CANONICAL_ROUTE','canonical editor route marker')
    need(home,"P.postMessage({type:'GSF_SHELL_NAV',target:'editor'},P.location.origin);",'editor route to parent shell')
    forbid(home,"const o=D.getElementById('gsf-editor-overlay-v220');\n      if(!o)return false;",'legacy editor dead-end')

    # Home must keep invisible local chrome space reserved so the global bar/footer
    # do not cover the CTA cards. V340 controls that handoff via visibility, not display:none.
    forbid(app,'html.gsf-global-shell-active #home154 .bottomNav,','home nav removed from layout')
    forbid(app,'html.gsf-global-shell-active #home154 .siteFooter,','home footer removed from layout')

    forbidden='@media(min-width:761px){#gsf-v334-header,#gsf-v334-gamebar,#gsf-v334-footer{display:none!important}}'
    forbid(app,forbidden,'desktop global chrome disabled')

    compile(app,str(APP),'exec')
    print('V341/V342 global shell + editor route: PASS',flush=True)

if __name__=='__main__':
    main()
