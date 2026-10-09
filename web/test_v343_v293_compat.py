#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
V293=ROOT/'web/apply_v293_render_memory_guard.py'
START=ROOT/'web/start_web.sh'

if not V293.is_file() or not START.is_file():
    raise SystemExit('V343/V293 compatibility files missing')

v293=V293.read_text(encoding='utf-8')
start=START.read_text(encoding='utf-8')

checks={
    'project-reference shell mutation skips V343': (
        'if "GSF_GLOBAL_SHELL_V343" in shell:' in v293
        and 'V343 owns shell route' in v293
    ),
    'legacy gamebar normalizer skips V343': (
        'V343 canonical shell owns routing' in v293
    ),
    'V293 still runs': 'python /app/web/apply_v293_render_memory_guard.py' in start,
    'V343 is retested after V293': (
        start.rfind('python /app/web/test_v343_single_global_shell.py /app')
        > start.find('python /app/web/apply_v293_render_memory_guard.py')
    ),
    'final shell compile runs after V293': (
        start.rfind('python -m py_compile /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')
        > start.find('python /app/web/apply_v293_render_memory_guard.py')
    ),
}

failed=[name for name,ok in checks.items() if not ok]
for name,ok in checks.items():
    print(('PASS: ' if ok else 'FAIL: ')+name)
if failed:
    raise SystemExit('V343/V293 compatibility contract failed: '+', '.join(failed))
print('V343/V293 COMPATIBILITY CONTRACT: PASS',flush=True)
