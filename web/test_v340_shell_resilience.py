#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
HOME=ROOT/'web/home_v154_component/index.html'
APP=ROOT/'GamingShortsFactory_V154_STRUCTURAL_HOME.py'

if not HOME.is_file():
    raise SystemExit('V340 test: Home missing')
if not APP.is_file():
    raise SystemExit('V340 test: shell app missing')

home=HOME.read_text(encoding='utf-8')
app=APP.read_text(encoding='utf-8')

checks=[
    ('V340 marker', 'V340_SHELL_RESILIENCE' in app),
    ('editor fallback builder', 'ensureEditorSurface' in app),
    ('editor fallback creates canonical overlay', "o.id='gsf-editor-overlay-v220'" in app),
    ('editor fallback iframe', "f.dataset.src='/editor-live/'" in app and "f.src='/editor-live/?v=340'" in app),
    ('editor no longer depends on retry-only legacy overlay', 'if(!o){if(attempt<20)' not in app),
    ('global chrome completeness guard', 'v340ChromeComplete' in app),
    ('global chrome can rebuild after DOM loss', 'P.__GSF_V334_GLOBAL_CHROME_HARD_LOCK&&v340ChromeComplete()' in app),
    ('Home keeps fallback chrome until parent ready', 'html.gsf-v334-parent-ready #home154 .topbar' in home),
    ('Home chrome readiness watcher', 'V340_HOME_CHROME_FALLBACK' in home and 'gsf-v334-parent-ready' in home),
]

failed=[]
for label,ok in checks:
    if ok:
        print('PASS:',label)
    else:
        print('FAIL:',label)
        failed.append(label)

try:
    compile(app,str(APP),'exec')
    print('PASS: V340 shell compiles')
except Exception as exc:
    print('FAIL: V340 shell compile:',exc)
    failed.append('shell compile')

if failed:
    raise SystemExit('V340 shell resilience contract failed: '+', '.join(failed))
print('V340 shell resilience contract: PASS')
