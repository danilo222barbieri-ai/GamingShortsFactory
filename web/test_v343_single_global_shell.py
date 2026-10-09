#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'
START=ROOT/'web/start_web.sh'
HOME=ROOT/'web/home_v154_component/index.html'


def need(text, token, label):
    if token not in text:
        raise AssertionError(f'V343 missing {label}: {token}')


def main():
    for p in (APP,START,HOME):
        if not p.is_file():
            raise SystemExit(f'V343 runtime file missing: {p}')
    shell=APP.read_text(encoding='utf-8')
    start=START.read_text(encoding='utf-8')
    home=HOME.read_text(encoding='utf-8')

    need(shell,'GSF_GLOBAL_SHELL_V343','V343 marker')
    assert shell.count('id="gsf-global-header"') == 1, 'V343 must create exactly one global header'
    assert shell.count('id="gsf-global-gamebar"') == 1, 'V343 must create exactly one global Game Bar'
    assert shell.count('id="gsf-global-footer"') == 1, 'V343 must create exactly one global footer'
    for token,label in (
        ('GAMING SHORTS FACTORY','brand copy'),
        ('>Accedi<','signed-out fallback'),
        ("target:'editor'",'Editor route'),
        ('/editor-live/','Editor lazy source'),
        ("target:'short'",'Short route'),
        ('--gsf-shell-safe-bottom','safe bottom variable'),
        ('keepGlobalShellMounted','single watchdog'),
    ):
        need(shell,token,label)

    for old in (
        'fix_v330_global_chrome.py',
        'fix_v332_global_frame_lock.py',
        'fix_v334_global_chrome_hard_lock.py',
        'fix_v340_shell_resilience.py',
    ):
        if old in start:
            raise AssertionError(f'legacy chrome authority still active in startup: {old}')

    need(start,'fix_v343_single_global_shell.py','V343 startup apply')
    need(start,'test_v343_single_global_shell.py','V343 startup test')
    if 'fix_v341_global_shell_contract.py' in start:
        raise AssertionError('V341 must not run directly from startup')

    for old_id in ('gsf-v328-global-footer','gsf-v330-global-footer','gsf-v334-header','gsf-v334-gamebar','gsf-v334-footer'):
        if old_id in shell:
            raise AssertionError(f'legacy global chrome remains in runtime shell: {old_id}')

    need(home,'V343_HOME_SHELL_RESERVE','Home shell reserve marker')
    compile(shell,str(APP),'exec')
    print('V343 SINGLE GLOBAL SHELL CONTRACT: PASS',flush=True)

if __name__=='__main__':
    main()
